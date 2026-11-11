#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check local package links, Markdown math/fences, YAML, agents, scripts, shell syntax.

Covers every Markdown file: local links and heading anchors, code fences,
display math (`$$` alone on its own line, with a blank line around each pair),
no `\\(` or `\\[` delimiters, and dollar amounts that would read as math; the
YAML frontmatter of the skills and Claude agents; the syntax of every Python
script of the package; `zsh -n` on every `sh` code block; and, in a Git
checkout, `git diff --check HEAD`, which finds nothing on a clean tree. Standard
library only. Does not execute a model, install skills, or build Lean.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]


def yaml_scalar(text):
    if text.startswith('"'):
        return json.loads(text)
    if text.startswith("'"):
        assert text.endswith("'") and len(text) > 1, f"Unclosed quote: {text!r}"
        return text[1:-1].replace("''", "'")
    # A plain scalar cannot hold these sequences in YAML; quote the value instead.
    assert ": " not in text and " #" not in text, f"Plain YAML scalar needs quotes: {text!r}"
    return text


def load_yaml(text):
    """Parse the YAML subset of this package: top-level scalars, string lists, one nested mapping."""
    data, key = {}, None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if not raw[0].isspace():
            key, sep, value = raw.partition(":")
            assert sep and key.strip(), f"Unsupported YAML line: {raw!r}"
            key = key.strip()
            data[key] = yaml_scalar(value.strip()) if value.strip() else None
            continue
        item = raw.strip()
        assert key is not None, f"Indented YAML line without a key: {raw!r}"
        if item.startswith("- "):
            data[key] = (data[key] or []) + [yaml_scalar(item[2:].strip())]
        else:
            sub, sep, value = item.partition(":")
            assert sep and sub.strip(), f"Unsupported YAML line: {raw!r}"
            data[key] = {**(data[key] or {}), sub.strip(): yaml_scalar(value.strip())}
    return data


def markdown_body(text):
    body, fence = [], None
    for line in text.splitlines():
        match = re.match(r"\s*(`{3,}|~{3,})(.*)$", line)
        if match:
            marker, rest = match.groups()
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence) and not rest.strip():
                fence = None
            continue
        if fence is None:
            body.append(line)
    assert fence is None, "Unclosed code fence"
    return "\n".join(body)


def main():
    if not __debug__:
        raise SystemExit("run without -O: the checks are assertions")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    files = []
    for parent, dirs, names in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in {".git", ".lake", "__pycache__"}]
        files.extend(Path(parent) / n for n in names if n.endswith(".md"))
    link_count = 0
    for path in sorted(files):
        body = markdown_body(path.read_text())
        assert not re.search(r"\\[\[(]", body), f"Non-MacDown math delimiter: {path}"
        assert not re.search(r"^\s*\$\$.+\$\$\s*$", body, re.M), f"Single-line display math: {path}"
        # A dollar amount such as $3.24 can pair with another dollar sign as inline math.
        # Inline math, such as $2 + 2 = 4$ or $1/2$, opens and closes next to a non-blank
        # character, and its closing dollar is not followed by a digit, as in Pandoc.
        prose = re.sub(r"\$(?=[^\s$])[^$\n]*?(?<=[^\s$])\$(?!\d)", "", body)
        money = re.search(r"\$\d[\d,]*(?:\.\d+)?(?=[\s,;:)|/]|\.(?!\d)|$)", prose, re.M)
        assert not money, f"Dollar amount read as math (write USD): {path}: {money and money.group(0)}"
        lines = body.splitlines()
        for line in lines:
            prose_line = re.sub(r"`[^`]*`", "", line)  # `$$` in inline code is not a delimiter
            assert "$$" not in prose_line or line == "$$", \
                f"Display math delimiter not alone on its line: {path}: {line[:60]!r}"
        delimiters = [i for i, line in enumerate(lines) if line == "$$"]
        assert len(delimiters) % 2 == 0, f"Unbalanced display math: {path}"
        for opening, closing in zip(delimiters[::2], delimiters[1::2]):
            assert opening == 0 or not lines[opening - 1].strip(), path
            assert closing + 1 == len(lines) or not lines[closing + 1].strip(), path
        for target in re.findall(r"\]\(([^)]+)\)", body):
            if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue
            name, _, anchor = unquote(target).partition("#")
            dest = (path.parent / name).resolve() if name else path
            assert dest.exists(), f"Missing local link: {path.relative_to(ROOT)} -> {target}"
            if anchor:
                heads = re.findall(r"^#+\s+(.+)$", markdown_body(dest.read_text()), re.M)
                slugs = [re.sub(r"[^\w\- ]", "", h.lower()).replace(" ", "-") for h in heads]
                assert anchor in slugs, f"Missing heading: {path.relative_to(ROOT)} -> {target}"
            link_count += 1
    metadata = []
    for skill in sorted((ROOT / "skills").iterdir()):
        if not skill.is_dir():
            continue
        front = load_yaml((skill / "SKILL.md").read_text().split("---", 2)[1])
        assert front["name"] == skill.name
        assert isinstance(front["description"], str) and front["description"]
        ui = load_yaml((skill / "agents/openai.yaml").read_text())
        assert isinstance(ui["interface"], dict)
        metadata.append(skill.name)
    agents = []
    skill_names = {d.name for d in (ROOT / "skills").iterdir() if d.is_dir()}
    for agent in sorted((ROOT / "skills/lean-orchestrator/assets/agents").glob("*.md")):
        front = load_yaml(agent.read_text().split("---", 2)[1])
        assert front["name"] == agent.stem, agent
        assert isinstance(front["description"], str) and front["description"], agent
        assert isinstance(front["tools"], str) and front["tools"], agent
        assert front["model"] in {"sonnet", "opus", "haiku", "inherit"}, agent
        assert set(front.get("skills", [])) <= skill_names, agent
        agents.append(agent.stem)
    scripts = []
    for script in sorted(p for p in ROOT.rglob("*.py") if not {".git", ".lake"} & set(p.parts)):
        compile(script.read_text(), str(script), "exec")
        scripts.append(script.name)
    shell_examples = [example for path in sorted(files)
                      for example in re.findall(r"```sh\n(.*?)\n```", path.read_text(), re.S)]
    assert shell_examples, "No Codex shell examples found"
    for example in shell_examples:
        syntax = subprocess.run(["zsh", "-n"], input=example, capture_output=True, text=True)
        assert syntax.returncode == 0, syntax.stderr
    whitespace_exit = None
    if (ROOT / ".git").exists():
        whitespace = subprocess.run(["git", "diff", "--check", "HEAD"], cwd=ROOT,
                                    capture_output=True, text=True)
        assert whitespace.returncode == 0, whitespace.stdout + whitespace.stderr
        whitespace_exit = whitespace.returncode
    report = {"markdown_files": len(files), "local_links": link_count,
              "yaml_skills": metadata, "claude_agents": agents, "python_scripts": scripts,
              "shell_examples": len(shell_examples),
              "shell_syntax_exit": syntax.returncode,
              "git_diff_check_exit": whitespace_exit,
              "result": "PASS", "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
