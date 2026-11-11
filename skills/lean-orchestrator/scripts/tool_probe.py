#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""List the local tools a formalization campaign can use.

Checks a fixed list of tools on PATH and in the usual install directories
(MacPorts, Homebrew, TeX Live, elan), reads their versions, checks a few Python
modules, and lists the MacPorts ports requested explicitly. It only reads: it
installs nothing, runs no package manager command that changes anything, sends
nothing over the network itself, and runs version commands in an empty
directory under /tmp, outside any project, so that no project's `lean-toolchain`
selects a toolchain to download; elan may still install its default toolchain
when none is installed at all. Prints JSON, or a Markdown
table with --markdown for the operational plan. Exits 1 if git, lean or lake is
missing.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HOME = os.path.expanduser("~")
EXTRA_DIRS = ["/opt/local/bin", "/opt/homebrew/bin", "/usr/local/bin",
              "/Library/TeX/texbin", f"{HOME}/.elan/bin", f"{HOME}/.local/bin",
              f"{HOME}/.cargo/bin"]

# (name, executables tried in order, version arguments or None, use)
TOOLS = [
    ("git", ["git"], ["--version"], "version control"),
    ("lean", ["lean"], ["--version"], "Lean (default toolchain)"),
    ("lake", ["lake"], ["--version"], "Lean builds"),
    ("elan", ["elan"], ["--version"], "Lean toolchains"),
    ("codex", ["codex"], ["--version"], "Codex workers"),
    ("lean-beam", ["lean-beam"], ["--version"], "Lean Beam: warm Lean probes at the source position"),
    ("lean-beam-mcp", ["lean-beam-mcp"], ["--version"], "Lean Beam MCP server"),
    ("gh", ["gh"], ["--version"], "GitHub publication"),
    ("python3", ["python3"], ["--version"], "scripts of the skills"),
    ("uv", ["uv"], ["--version"], "isolated Python environments"),
    ("rg", ["rg"], ["--version"], "fast search in Mathlib and logs"),
    ("fd", ["fd"], ["--version"], "fast file search"),
    ("jq", ["jq"], ["--version"], "JSON logs and handoffs"),
    ("timeout", ["timeout", "gtimeout"], ["--version"], "time limits on commands"),
    ("parallel", ["parallel"], ["--version"], "parallel shell jobs"),
    ("latexmk", ["latexmk"], ["-v"], "erratum PDF"),
    ("pdflatex", ["pdflatex"], ["--version"], "LaTeX"),
    ("pandoc", ["pandoc"], ["--version"], "document conversion"),
    ("hyperfine", ["hyperfine"], ["--version"], "elaboration benchmarks"),
    ("gp", ["gp"], ["--version-short"], "PARI/GP: numerical and arithmetic checks"),
    ("sage", ["sage"], ["--version"], "SageMath: computer algebra"),
    ("maxima", ["maxima"], ["--version"], "Maxima: computer algebra"),
    ("wolframscript", ["wolframscript"], ["-version"], "Mathematica"),
    ("geng", ["geng", "nauty-geng"], None, "nauty: enumerate graphs for counterexamples"),
    ("dot", ["dot"], ["-V"], "Graphviz: draw the dependency graph"),
]
CORE = ("git", "lean", "lake")
PY_MODULES = ["numpy", "scipy", "sympy", "mpmath", "networkx"]


def locate(executables):
    for exe in executables:
        found = shutil.which(exe)
        if found:
            return exe, found, True
    for exe in executables:
        for directory in EXTRA_DIRS:
            candidate = os.path.join(directory, exe)
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                return exe, candidate, False
    return None, None, False


def first_line(cmd, cwd, timeout):
    try:
        out = subprocess.run(cmd, cwd=cwd, stdin=subprocess.DEVNULL,
                             capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return None
    for line in (out.stdout + "\n" + out.stderr).splitlines():
        if line.strip():
            return line.strip()[:120]
    return None


def python_modules(python, cwd, timeout):
    code = ("import importlib.util, json, sys; "
            "print(json.dumps({m: importlib.util.find_spec(m) is not None "
            "for m in sys.argv[1:]}))")
    try:
        out = subprocess.run([python, "-I", "-c", code, *PY_MODULES], cwd=cwd,
                             stdin=subprocess.DEVNULL, capture_output=True,
                             text=True, timeout=timeout)
        return json.loads(out.stdout)
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return None


def python_interpreters():
    """python3 on PATH, then versioned python3.N in the install directories."""
    found, seen = [], set()
    candidates = [shutil.which("python3")]
    for directory in EXTRA_DIRS:
        if os.path.isdir(directory):
            candidates += [os.path.join(directory, name) for name in sorted(os.listdir(directory))
                           if re.fullmatch(r"python3\.\d+", name)]
    for path in candidates:
        if path and os.access(path, os.X_OK) and os.path.realpath(path) not in seen:
            seen.add(os.path.realpath(path))
            found.append(path)
    return found


def requested_ports(port, timeout):
    try:
        out = subprocess.run([port, "-q", "echo", "requested"], stdin=subprocess.DEVNULL,
                             capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return None
    names = sorted({line.split()[0] for line in out.stdout.splitlines() if line.strip()})
    return names or None


def probe(timeout, ports):
    report = {"tools": {}, "missing": [], "off_path": [], "hints": []}
    with tempfile.TemporaryDirectory(dir="/tmp" if os.path.isdir("/tmp") else None) as empty:
        for name, executables, version_args, use in TOOLS:
            exe, path, on_path = locate(executables)
            if path is None:
                report["missing"].append(name)
                continue
            version = first_line([path, *version_args], empty, timeout) if version_args else None
            report["tools"][name] = {"executable": exe, "path": path, "on_path": on_path,
                                     "version": version, "use": use}
            if not on_path:
                report["off_path"].append(name)
        report["python_modules"] = {}
        for python in python_interpreters():
            report["python_modules"][python] = {
                "version": first_line([python, "--version"], empty, timeout),
                "on_path": shutil.which(os.path.basename(python)) == python,
                "modules": python_modules(python, empty, timeout)}
    managers = {}
    for manager, candidates in (("macports", ["/opt/local/bin/port"]),
                                ("homebrew", ["/opt/homebrew/bin/brew", "/usr/local/bin/brew"])):
        path = shutil.which("port" if manager == "macports" else "brew") or next(
            (c for c in candidates if os.path.isfile(c)), None)
        managers[manager] = {"path": path}
        if manager == "macports" and path and ports:
            managers[manager]["requested"] = requested_ports(path, timeout * 4)
    report["package_managers"] = managers
    if report["off_path"]:
        dirs = sorted({os.path.dirname(report["tools"][n]["path"]) for n in report["off_path"]})
        report["hints"].append(
            "Installed but not on this PATH: " + ", ".join(report["off_path"])
            + ". Worker processes inherit this PATH: call these by absolute path, or add "
            + ":".join(dirs) + " to PATH in the worker's command. Changing the user's shell "
            "configuration is the user's decision.")
    default = shutil.which("python3")
    for python, info in report["python_modules"].items():
        present = [m for m, ok in (info["modules"] or {}).items() if ok]
        if python != default and present:
            report["hints"].append(
                f"{', '.join(present)} available with {python}, not with the default python3: "
                "run numerical checks with that interpreter by absolute path.")
    if "timeout" in report["missing"]:
        report["hints"].append("No timeout or gtimeout: bound long commands another way "
                               "(the worker scripts' own limits, or Python's subprocess timeout).")
    if "latexmk" in report["missing"]:
        report["hints"].append("No latexmk: a PDF erratum cannot be compiled here; draft the "
                               ".tex and give it to the user to compile.")
    report["core_missing"] = [n for n in CORE if n in report["missing"]]
    return report


def markdown(report):
    lines = ["| Tool | Use | Path | On PATH | Version |", "| --- | --- | --- | --- | --- |"]
    for name, info in report["tools"].items():
        lines.append(f"| {name} | {info['use']} | `{info['path']}` | "
                     f"{'yes' if info['on_path'] else 'no'} | {(info['version'] or '').replace('|', '/')} |")
    lines.append("")
    lines.append("Missing: " + (", ".join(report["missing"]) or "none") + ".")
    for python, info in report.get("python_modules", {}).items():
        modules = info["modules"] or {}
        present = [m for m, ok in modules.items() if ok]
        lines.append(f"Python modules with `{python}` ({info['version'] or 'version unknown'}): "
                     + (", ".join(present) or "none of " + ", ".join(PY_MODULES)) + ".")
    requested = report["package_managers"].get("macports", {}).get("requested")
    if requested:
        lines.append("MacPorts ports requested: " + ", ".join(requested) + ".")
    for hint in report["hints"]:
        lines.append("")
        lines.append(hint)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--markdown", action="store_true", help="print a Markdown table")
    parser.add_argument("--no-ports", action="store_true",
                        help="do not list the requested MacPorts ports")
    parser.add_argument("--timeout", type=float, default=10.0,
                        help="seconds allowed for each version command")
    args = parser.parse_args()
    report = probe(args.timeout, not args.no_ports)
    print(markdown(report) if args.markdown else json.dumps(report, indent=2))
    return 1 if report["core_missing"] else 0


if __name__ == "__main__":
    sys.exit(main())
