#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Record approved Lean files and check that only their proof holes changed.

`record` saves each `--file` by its SHA-256 (the file is frozen whole) and each
`--holes` file in full (its `sorry` tokens in code, outside comments, strings,
raw strings and `«…»` names, are the registered holes), with the Git commit. It
also freezes the Lake configuration (`lakefile.lean`, `lakefile.toml`,
`lean-toolchain`, `lake-manifest.json`: contents, and which of them exist) and
the source state of every dependency of the manifest: for a Git dependency its
commit and a fingerprint of any local change or untracked file, outside `.lake`;
for a path dependency a hash of its files outside `.lake` and `.git`. With
`--decl` (and the `--module` files that declare them), it builds those modules
(`lake -R build`), then saves, printed by Lean with `pp.all` and no size limit,
then hashed under the declaration's full name, the type of each named
declaration and of every declaration of the project that these types use, and
the value of each such definition, transitively. The project's declarations are
those of every module that comes neither from the Lean toolchain nor from
`.lake/packages`, whatever its library. It also hashes the `.olean` file of
every dependency module that holds a declaration these reach (through types,
definition values and constructors), so a dependency's compiled definitions
cannot change unseen. The proofs of theorems are not recorded. Run it right
after the approval; it prints the record's SHA-256, which the coordinator keeps
in its report to the user, and `check` prints it again.

`check` first compares the Lake configuration and the dependencies' source
state, without running Lake, and stops at the first difference: a legitimate
update needs a new approval and a new record. It passes a `--holes` file when
the current text is the approved text with each hole replaced by proof text,
and a `--file` file when its hash is unchanged. A filled hole must contain
proof text only: no Lean command such as `local instance`, `notation`,
`attribute`, `seal`, `open` or `set_option` without `in`, or `#exit`, anywhere
in it, and no comment, string or `«…»` name left open, because Lean accepts a
command after a tactic block and it would change the meaning of the frozen text
that follows. This is a lexical filter, not a parser; the printed declarations
are the guarantee, so pass every statement of a frozen file with `--decl`.
Put helpers in an owned helper module instead. When the record has
declarations, `check` rebuilds the modules with `lake -R build`, prints the
declarations again and requires the same hashes, with nothing elided (`⋯`), and
the same dependency `.olean` hashes. Records of an older format (before
version 2.0.0) are refused: record again from the recorded commit, in a worktree
at that commit. It also lists, as warnings, the
commands with a global effect (instances, notations, macros, attribute
changes) in the helper modules: the project modules that a file with holes
imports directly and that are not frozen themselves; the printed values already
catch any change of meaning they cause. It reads files under `--root` (default:
the current directory), so it works in a worktree, and exits with 0 when all
pass, 1 otherwise (2 when `record` cannot record).
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

FORMAT = 4

# Lean identifier characters around a keyword: a keyword inside a name is not a keyword.
BEFORE, AFTER = r"(?<![\w.'!?])", r"(?![\w'!?])"
# A hole is a `sorry` token in code with the blanks before it, so `by sorry` may become
# `by\n  ...`.
SORRY = re.compile(BEFORE + r"sorry" + AFTER)
COMMAND_WORDS = (
    "theorem lemma def abbrev instance example axiom opaque structure class inductive "
    "coinductive mutual notation notation3 infix infixl infixr prefix postfix macro "
    "macro_rules syntax elab elab_rules declare_syntax_cat local scoped attribute namespace "
    "section end variable universe export noncomputable private protected partial unsafe "
    "nonrec initialize builtin_initialize irreducible_def alias deriving omit include simproc "
    "dsimproc unif_hint binder_predicate run_cmd run_elab run_meta add_decl_doc register_option "
    "register_simp_attr library_note assert_not_exists seal unseal grind_pattern simproc_decl "
    "dsimproc_decl declare_simp_like_tactic declare_config_elab").split()
COMMAND = re.compile(BEFORE + r"(?:" + "|".join(COMMAND_WORDS) + r")" + AFTER
                     + r"|@\[|" + BEFORE + r"#[a-z_]{2,}")
# `open` and `set_option` are tactics and terms too, when followed by `in` and the rest.
SCOPED = re.compile(BEFORE + r"(?:open|set_option)" + AFTER)
NAME = r"[^\W\d][\w.'!?]*"
# What may follow `open` before `in`: namespaces, `scoped`, `(names)`, `hiding` and `renaming`.
OPEN_IN = re.compile(r"open(?:\s+(?:scoped|hiding|renaming|→|->|\([^()]*\)|(?!(?:in|open|set_option)" + AFTER + r")"
                     + NAME + r"))+\s+in" + AFTER)
SET_OPTION_IN = re.compile(r"set_option\s+" + NAME + r"\s+(?:(?!in" + AFTER + r")\S+\s+)?in" + AFTER)
GLOBAL_WORDS = (
    "instance notation notation3 infix infixl infixr prefix postfix macro macro_rules syntax "
    "elab elab_rules declare_syntax_cat unif_hint binder_predicate axiom initialize "
    "builtin_initialize export default_instance implemented_by extern").split()
GLOBAL = re.compile(BEFORE + r"(?:" + "|".join(GLOBAL_WORDS) + r")" + AFTER
                    + r"|" + BEFORE + r"attribute\s*\[\s*-")
# What `strip_code` matches at a position: the character before a raw string or character
# literal (which must not continue a name), the opening of a raw string, a character literal.
NAME_CHAR = re.compile(r"[\w'!?.]")
RAW_OPEN = re.compile(r'r(#*)"')
CHAR = re.compile(r"'(?:\\.[^']*|[^\\'])'")
IMPORT = re.compile(r"^[ \t]*(?:public[ \t]+)?(?:meta[ \t]+)?import[ \t]+(?:all[ \t]+)?([^\s]+)",
                    re.M)


def blank(text):
    """Spaces in place of `text`, keeping its line breaks, so offsets and lines stay valid."""
    return re.sub(r"[^\n]", " ", text)


def strip_code(text):
    """Text with comments, string, raw string and character literals and «names» blanked,
    and the problems found.

    The result has the length and the line breaks of `text`."""
    out, problems, i, n = [], [], 0, len(text)
    while i < n:
        if text.startswith("/-", i):
            depth, j = 1, i + 2
            while j < n and depth:
                if text.startswith("/-", j):
                    depth, j = depth + 1, j + 2
                elif text.startswith("-/", j):
                    depth, j = depth - 1, j + 2
                else:
                    j += 1
            if depth:
                problems.append("a comment is opened and not closed")
            out.append(blank(text[i:j]))
            i = j
        elif text.startswith("-/", i):
            problems.append("a comment is closed that was not opened")
            out.append("  ")
            i += 2
        elif text.startswith("--", i):
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append(blank(text[i:j]))
            i = j
        elif text[i] == "r" and (i == 0 or not NAME_CHAR.match(text, i - 1)) and (
                m := RAW_OPEN.match(text, i)):
            close = '"' + m.group(1)
            j = text.find(close, m.end())
            if j < 0:
                problems.append("a raw string is opened and not closed")
                j = n
            else:
                j += len(close)
            out.append(blank(text[i:j]))
            i = j
        elif text[i] == "«":
            j = text.find("»", i + 1)
            if j < 0:
                problems.append("a «name» is opened and not closed")
                j = n
            else:
                j += 1
            out.append(blank(text[i:j]))
            i = j
        elif text[i] == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            if j >= n:
                problems.append("a string is opened and not closed")
            j = min(j + 1, n)
            out.append(blank(text[i:j]))
            i = j
        elif text[i] == "'" and (i == 0 or not NAME_CHAR.match(text, i - 1)) and (
                m := CHAR.match(text, i)):
            out.append(blank(m.group(0)))
            i = m.end()
        else:
            out.append(text[i])
            i += 1
    return "".join(out), problems


def hole_spans(text):
    """(start, end) of each hole of `text`: a `sorry` token in code with the blanks before it."""
    spans = []
    for m in SORRY.finditer(strip_code(text)[0]):
        start = m.start()
        while start and text[start - 1] in " \t":
            start -= 1
        spans.append((start, m.end()))
    return spans


def fill_problems(fill):
    """Why a filled hole is not proof text only, or an empty list."""
    code, problems = strip_code(fill)
    # `scoped`, `hiding` and `renaming` after `open` are part of a scoped `open … in`.
    scan = code
    for m in SCOPED.finditer(code):
        if m.group(0) == "open" and (scoped := OPEN_IN.match(code, m.start())):
            scan = scan[:m.start()] + blank(scan[m.start():scoped.end()]) + scan[scoped.end():]
    for m in COMMAND.finditer(scan):
        problems.append(f"command {m.group(0)!r}")
    for m in SCOPED.finditer(code):
        scoped = (OPEN_IN if m.group(0) == "open" else SET_OPTION_IN).match(code, m.start())
        if not scoped or not code[scoped.end():].strip():
            problems.append(f"{m.group(0)!r} without `in` and the rest of the proof")
    return problems


def git(root, *args):
    try:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def match_holes(approved, current):
    """(None, fills) if `current` is `approved` with each hole filled; else (approved line, None)."""
    spans = hole_spans(approved)
    cuts = [0] + [offset for span in spans for offset in span] + [len(approved)]
    segments = [approved[cuts[k]:cuts[k + 1]] for k in range(0, len(cuts), 2)]
    starts = [0] + [end for _, end in spans]

    def line(offset):
        return approved[:offset].count("\n") + 1

    def common_prefix(a, b):
        n = 0
        while n < min(len(a), len(b)) and a[n] == b[n]:
            n += 1
        return n

    if not current.startswith(segments[0]):
        return line(common_prefix(approved, current)), None
    if len(segments) == 1:
        return (None, []) if current == approved else (line(len(approved)), None)
    # Leftmost matching of the fixed segments decides a pattern s0 * s1 * ... * sN.
    pos, fills = len(segments[0]), []
    for i in range(1, len(segments) - 1):
        at = current.find(segments[i], pos)
        if at < 0:
            return line(starts[i]), None  # somewhere in this segment, up to the next hole
        fills.append((line(starts[i]), current[pos:at]))
        pos = at + len(segments[i])
    last = segments[-1]
    if current.endswith(last) and len(current) - len(last) >= pos:
        fills.append((line(starts[-1]), current[pos:len(current) - len(last)]))
        return None, fills
    return line(len(approved) - common_prefix(last[::-1], current[::-1])), None


def module_path(root, module):
    return root / (module.replace(".", "/") + ".lean")


def lean_name(name):
    return "`" + ".".join(part if re.fullmatch(r"[^\W\d][\w'!?]*", part) else f"«{part}»"
                          for part in name.split("."))


# Without a step limit, Lean elides parts of a large term as `⋯`, which can hide a change.
ELIDED = "⋯"

# Each entry starts with a marker line holding the full name, quoted by Lean, then the text
# printed. The nonce makes the marker impossible to forge from printed text.
PROBE = """open Lean Elab Command in
set_option pp.all true in
set_option pp.maxSteps 1000000000 in
set_option pp.deepTerms true in
#eval show CommandElabM Unit from do
  let env ← getEnv
  let lib := (← getLibDir (← findSysroot)).toString
  let names := env.allImportedModuleNames
  let mut kind : Std.HashMap ModuleIdx Bool := {{}}  -- true: project, false: dependency
  let mut oleans : Std.HashMap ModuleIdx String := {{}}
  for m in names do
    let olean := (← findOLean m).toString
    if let some i := env.getModuleIdx? m then
      if !olean.startsWith lib then
        kind := kind.insert i ((olean.splitOn "/.lake/packages/").length == 1)
        oleans := oleans.insert i olean
  let mut todo : Array Name := #[{decls}]
  let mut seen : NameSet := {{}}
  let mut depMods : Std.HashSet ModuleIdx := {{}}
  let mut out : Array (String × MessageData) := #[]
  while h : todo.size > 0 do
    let c := todo.back
    todo := todo.pop
    if seen.contains c then continue
    seen := seen.insert c
    let some info := env.find? c | throwError m!"unknown declaration {{c}}"
    let place := (env.getModuleIdxFor? c).bind kind.get?
    if place == some false then
      if let some i := env.getModuleIdxFor? c then depMods := depMods.insert i
    if place != some true then
      -- A dependency's declaration: follow it to find the modules to hash, print nothing.
      if place == none then continue
    else
      out := out.push (c.toString ++ " :", m!"[freeze {nonce}] {{c.toString.quote}} :\\n[freeze] {{c}} : {{info.type}}")
    let mut used := info.type.getUsedConstants
    match info with
    | .defnInfo d =>
      if place == some true then
        out := out.push (c.toString ++ " :=", m!"[freeze {nonce}] {{c.toString.quote}} :=\\n[freeze] {{c}} := {{d.value}}")
      used := used ++ d.value.getUsedConstants
    | .opaqueInfo d =>
      if place == some true then
        out := out.push (c.toString ++ " :=", m!"[freeze {nonce}] {{c.toString.quote}} :=\\n[freeze] {{c}} := {{d.value}}")
      used := used ++ d.value.getUsedConstants
    | .inductInfo d => used := used ++ d.ctors.toArray
    | .ctorInfo d => used := used.push d.induct
    | _ => pure ()
    for u in used do
      if !seen.contains u then todo := todo.push u
  let sorted := out.qsort (fun a b => a.1 < b.1)
  let mods : Array MessageData := depMods.toArray.map (fun i => m!"[olean {nonce}] {{names[i]!}} {{oleans.getD i ""}}")
  logInfo (MessageData.joinSep ((sorted.map (·.2)).toList ++ mods.toList) "\\n")
"""


def lake_command(lake, *args):
    # `-R` elaborates the (verified) configuration files instead of a cached build of them.
    return [lake, "-R", *args]


def run_lean(root, probe, lake):
    with tempfile.NamedTemporaryFile("w", suffix=".lean", delete=False, encoding="utf-8") as f:
        f.write(probe)
    try:
        done = subprocess.run(lake_command(lake, "env", "lean", f.name), cwd=root,
                              capture_output=True, text=True, encoding="utf-8", errors="replace")
    except OSError as error:
        raise RuntimeError(str(error))
    finally:
        Path(f.name).unlink()
    if done.returncode != 0:
        raise RuntimeError((done.stdout + done.stderr).strip()[-2000:])
    return done.stdout


def build(root, modules, lake):
    """Build the modules with Lake, so the check never reads stale `.olean` files; or raise."""
    try:
        done = subprocess.run(lake_command(lake, "build", *modules), cwd=root, capture_output=True,
                              text=True, encoding="utf-8", errors="replace")
    except OSError as error:
        raise RuntimeError(str(error))
    if done.returncode != 0:
        raise RuntimeError((done.stdout + done.stderr).strip()[-2000:])


def unquote(text):
    """The Lean string literal at the start of `text`, decoded, and the rest; or raise."""
    if not text.startswith('"'):
        raise ValueError("no quoted name")
    out, i = [], 1
    simple = {"n": "\n", "t": "\t", "\\": "\\", '"': '"', "'": "'", "r": "\r", "0": "\0"}
    while i < len(text):
        c = text[i]
        if c == '"':
            return "".join(out), text[i + 1:]
        if c == "\\":
            e = text[i + 1]
            if e in simple:
                out.append(simple[e]); i += 2
            elif e == "x":
                out.append(chr(int(text[i + 2:i + 4], 16))); i += 4
            elif e == "u":
                close = text.index("}", i)
                out.append(chr(int(text[i + 3:close], 16))); i = close + 1
            else:
                raise ValueError(f"unknown escape \\{e}")
        else:
            out.append(c); i += 1
    raise ValueError("unterminated quoted name")


def probe_output(root, modules, decls, lake):
    """(entries, dependency .olean paths) printed by the probe; or raise RuntimeError.

    entries maps 'name :' and 'name :=' (full names) to the printed text."""
    nonce = os.urandom(8).hex()
    probe = "import Lean\n" + "".join(f"import {m}\n" for m in modules) + PROBE.format(
        nonce=nonce, decls=", ".join(lean_name(d) for d in decls))
    output = run_lean(root, probe, lake)
    found, oleans, key = {}, {}, None
    marker, olean = f"[freeze {nonce}] ", f"[olean {nonce}] "
    for line in output.splitlines():
        if line.startswith(marker):
            try:
                name, rest = unquote(line[len(marker):])
            except (ValueError, IndexError):
                raise RuntimeError(f"unreadable probe line: {line[:200]}")
            key = name + (" :=" if rest == " :=" else " :")
            if key in found:
                raise RuntimeError(f"two printed entries for {key!r}")
            found[key] = None
        elif line.startswith(olean):
            module, _, path = line[len(olean):].partition(" ")
            oleans[module] = path
            key = None
        elif key:
            found[key] = line if found[key] is None else found[key] + "\n" + line
    return found, oleans


def elided(text):
    """Whether Lean elided a subterm: a `⋯` outside string literals and «names»."""
    return ELIDED in re.sub(r'"(?:\\.|[^"\\])*"|«[^»]*»', "", text)


def sha(data):
    return hashlib.sha256(data).hexdigest()


CONFIG_FILES = ("lakefile.lean", "lakefile.toml", "lean-toolchain", "lake-manifest.json")


def config_state(root):
    """SHA-256 of each Lake configuration file, or None when it does not exist."""
    return {name: sha((root / name).read_bytes()) if (root / name).is_file() else None
            for name in CONFIG_FILES}


def tree_hash(directory):
    """SHA-256 of the files under `directory`, outside `.lake` and `.git`, by path and content."""
    digest = hashlib.sha256()
    for parent, dirs, names in os.walk(directory):
        dirs[:] = sorted(d for d in dirs if d not in (".lake", ".git"))
        for name in sorted(names):
            path = Path(parent) / name
            digest.update(str(path.relative_to(directory)).encode() + b"\0")
            digest.update(path.read_bytes() if path.is_file() and not path.is_symlink()
                          else os.readlink(path).encode() if path.is_symlink() else b"")
    return digest.hexdigest()


def git_state(directory):
    """(commit, fingerprint of local changes and untracked files outside `.lake`), or None."""
    head = git(directory, "rev-parse", "HEAD")
    if not head or not (directory / ".git").exists():
        return None
    try:
        status = subprocess.run(["git", "-C", str(directory), "status", "--porcelain=v1", "-z",
                                 "--untracked-files=all", "--ignored=no"], capture_output=True,
                                check=True).stdout
        diff = subprocess.run(["git", "-C", str(directory), "diff", "HEAD", "--binary", "--",
                               ".", ":(exclude).lake"], capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    digest = hashlib.sha256(diff)
    for item in status.split(b"\0"):
        path = item[3:].decode(errors="replace")
        if not item or path == ".lake" or path.startswith(".lake/"):
            continue
        digest.update(item + b"\0")
        if item.startswith(b"??") and (directory / path).is_file():
            digest.update((directory / path).read_bytes())
    return head, digest.hexdigest()


def dependency_state(root):
    """Source state of each dependency of `lake-manifest.json`, by name."""
    manifest_path = root / "lake-manifest.json"
    if not manifest_path.is_file():
        return {}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    packages_dir = root / manifest.get("packagesDir", ".lake/packages")
    state = {}
    for package in manifest.get("packages", []):
        name = package.get("name")
        if package.get("type") == "path":
            directory = (root / package.get("dir", "")).resolve()
            state[name] = {"type": "path", "dir": package.get("dir"),
                           "files_sha256": tree_hash(directory) if directory.is_dir() else None}
            continue
        directory = packages_dir / name
        found = git_state(directory) if directory.is_dir() else None
        if found:
            state[name] = {"type": "git", "manifest_rev": package.get("rev"), "commit": found[0],
                           "changes_sha256": found[1]}
        else:
            state[name] = {"type": package.get("type"), "manifest_rev": package.get("rev"),
                           "commit": None,
                           "files_sha256": tree_hash(directory) if directory.is_dir() else None}
    return state


def olean_digests(root, oleans):
    """{module: SHA-256 of its .olean} for the dependency modules found by the probe."""
    return {module: sha(Path(path).read_bytes()) if Path(path).is_file() else None
            for module, path in sorted(oleans.items())}


def statement_names(root, paths):
    """Names declared in the frozen files, found lexically, for the `--decl` warning."""
    found = set()
    pattern = re.compile(BEFORE + r"(?:theorem|lemma|def|abbrev|instance|opaque|structure|class|"
                         r"inductive)\s+(" + NAME + r")")
    for path in paths:
        try:
            code = strip_code((root / path).read_text(encoding="utf-8"))[0]
        except (OSError, UnicodeDecodeError):
            continue
        found.update(m.group(1) for m in pattern.finditer(code))
    return found


def record(args):
    root = Path(args.root).resolve()
    head = git(root, "rev-parse", "HEAD")
    data = {"format": FORMAT,
            "recorded_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
            "commit": head, "clean_tree": (git(root, "status", "--porcelain") == "") if head else None,
            "files": [], "holes": [], "types": None}
    try:
        for path in args.file:
            data["files"].append({"path": path, "sha256": sha((root / path).read_bytes())})
        for path in args.holes:
            text = (root / path).read_text(encoding="utf-8")
            data["holes"].append({"path": path, "holes": len(hole_spans(text)), "text": text})
        data["config"] = config_state(root)
        data["dependencies"] = dependency_state(root)
    except OSError as error:
        print(f"cannot read {error.filename}", file=sys.stderr)
        return 2
    except (UnicodeDecodeError, ValueError) as error:
        print(f"cannot read a frozen file or the manifest: {error}", file=sys.stderr)
        return 2
    warnings = [f"dependency {name}: commit {d['commit']} is not the manifest's {d['manifest_rev']}"
                for name, d in data["dependencies"].items()
                if d.get("commit") and d.get("manifest_rev") and d["commit"] != d["manifest_rev"]]
    if args.decl:
        if not args.module:
            print("--decl needs the --module files that declare it", file=sys.stderr)
            return 2
        try:
            build(root, args.module, args.lake)
            found, oleans = probe_output(root, args.module, args.decl, args.lake)
        except RuntimeError as error:
            print(f"cannot build or elaborate the declarations:\n{error}", file=sys.stderr)
            return 2
        if any(text is None or elided(text) for text in found.values()):
            print(f"Lean elided part of the printed declarations ({ELIDED}): not recorded",
                  file=sys.stderr)
            return 2
        data["types"] = {"modules": args.module, "decls": args.decl,
                         "printed_characters": sum(len(t) for t in found.values()),
                         "sha256": {k: sha(t.encode()) for k, t in found.items()},
                         "dependency_oleans": olean_digests(root, oleans)}
        missing = [m for m, d in data["types"]["dependency_oleans"].items() if d is None]
        if missing:
            print(f"dependency .olean files not found: {missing[:5]}", file=sys.stderr)
            return 2
    frozen_names = {d.split(".")[-1] for d in args.decl}
    unfrozen = sorted(n for n in statement_names(root, args.holes + args.file)
                      if n.split(".")[-1] not in frozen_names)
    if unfrozen:
        warnings.append("declared in a frozen file but not passed with --decl, so frozen by text "
                        f"only: {', '.join(unfrozen[:20])}")
    text = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    Path(args.out).write_text(text, encoding="utf-8")
    print(json.dumps({"recorded": args.out, "record_sha256": sha(text.encode()), "commit": head,
                      "clean_tree": data["clean_tree"], "files": args.file,
                      "holes": {h["path"]: h["holes"] for h in data["holes"]}, "decls": args.decl,
                      "declarations_frozen": len({k.rsplit(" ", 1)[0] for k in data["types"]["sha256"]})
                      if data["types"] else 0,
                      "dependency_oleans": len(data["types"]["dependency_oleans"]) if data["types"] else 0,
                      "dependencies": len(data["dependencies"]), "warnings": warnings}, ensure_ascii=False))
    return 0


def global_commands(root, data):
    """Commands with a global effect in the helper modules: the project modules that a
    file with holes imports directly and that are not frozen themselves."""
    frozen = {f["path"] for f in data["files"]} | {h["path"] for h in data["holes"]}
    helpers = set()
    for frozen_holes in data["holes"]:
        try:
            helpers.update(IMPORT.findall(strip_code((root / frozen_holes["path"]).read_text(
                encoding="utf-8"))[0]))
        except (OSError, UnicodeDecodeError):
            pass
    warnings = []
    for module in sorted(helpers):
        path = module_path(root, module)
        if not path.is_file() or str(path.relative_to(root)) in frozen:
            continue
        try:
            code = strip_code(path.read_text(encoding="utf-8"))[0]
        except (OSError, UnicodeDecodeError):
            warnings.append(f"{path.relative_to(root)}: not readable as UTF-8")
            continue
        for m in GLOBAL.finditer(code):
            before = code[:m.start()].split()
            if before and before[-1] in ("local", "[local"):
                continue
            line = code[:m.start()].count("\n") + 1
            warnings.append(f"{path.relative_to(root)}:{line}: {m.group(0)!r}")
    return warnings


def configuration_problems(root, data):
    """Differences in the Lake configuration and the dependencies' sources, without running Lake."""
    problems = []
    try:
        now = config_state(root)
    except OSError as error:
        return [f"cannot read {error.filename}"]
    for name in CONFIG_FILES:
        if now[name] != data["config"].get(name):
            what = ("added" if data["config"].get(name) is None else
                    "removed" if now[name] is None else "changed")
            problems.append(f"{name} {what}")
    if problems:
        return problems  # the manifest may differ: do not read the dependencies from it
    try:
        deps = dependency_state(root)
    except (OSError, ValueError, UnicodeDecodeError) as error:
        return [f"cannot read the dependencies: {error}"]
    for name in sorted(deps.keys() | data["dependencies"].keys()):
        old, new = data["dependencies"].get(name), deps.get(name)
        if old != new:
            if old is None or new is None:
                problems.append(f"dependency {name} {'added' if old is None else 'removed'}")
            else:
                fields = [k for k in old.keys() | new.keys() if old.get(k) != new.get(k)]
                problems.append(f"dependency {name}: {', '.join(sorted(fields))} changed")
    return problems


def check(args):
    root = Path(args.root).resolve()
    try:
        raw = Path(args.record).read_bytes()
        data = json.loads(raw.decode("utf-8"))
    except (OSError, ValueError) as error:
        print(f"cannot read the record: {error}")
        print("FAIL")
        return 1
    print(f"record sha256: {sha(raw)}")
    version = data.get("format", 1)
    if version < FORMAT:
        print(f"record format {version} (before version 2.0.0) is no longer accepted: record again "
              "from its recorded commit, in a worktree at that commit")
        print("FAIL")
        return 1
    problems = configuration_problems(root, data)
    if problems:
        # Stop before running Lake: the configuration or a dependency is not the frozen one.
        for problem in problems:
            print(f"Lake configuration or dependency: CHANGED ({problem})")
        print("stopped before running Lake: a legitimate update needs a new approval and a new record")
        print("FAIL")
        return 1
    print("Lake configuration and dependency sources: OK")
    results = []
    for frozen in data["files"]:
        try:
            same = sha((root / frozen["path"]).read_bytes()) == frozen["sha256"]
            results.append((frozen["path"], "OK" if same else "CHANGED"))
        except OSError:
            results.append((frozen["path"], "NO FILE"))
    for frozen in data["holes"]:
        try:
            line, fills = match_holes(frozen["text"], (root / frozen["path"]).read_text(encoding="utf-8"))
        except OSError:
            results.append((frozen["path"], "NO FILE"))
            continue
        except UnicodeDecodeError:
            results.append((frozen["path"], "CHANGED (not UTF-8)"))
            continue
        if line is not None:
            results.append((frozen["path"], f"CHANGED (outside the holes, from approved line {line} on)"))
            continue
        bad = [(at, problems) for at, fill in fills if (problems := fill_problems(fill))]
        results.append((frozen["path"], "OK" if not bad else "NOT PROOF TEXT IN A HOLE ("
                        + "; ".join(f"hole of approved line {at}: {', '.join(p[:3])}"
                                    for at, p in bad) + ")"))
    types = data.get("types")
    if types:
        try:
            build(root, types["modules"], args.lake)
            found, oleans = probe_output(root, types["modules"], types["decls"], args.lake)
            new, old = {k: sha(t.encode()) for k, t in found.items()}, types["sha256"]
            changed = sorted(k for k in old.keys() | new.keys() if old.get(k) != new.get(k))
            old_o, new_o = types.get("dependency_oleans", {}), olean_digests(root, oleans)
            changed += sorted(f"{m} (.olean)" for m in old_o.keys() | new_o.keys()
                              if old_o.get(m) != new_o.get(m))
            if any(t is None or elided(t) for t in found.values()):
                state = f"NOT EXHAUSTIVE (Lean elided part of the output: {ELIDED})"
            elif changed or not new:
                state = f"CHANGED ({', '.join(changed[:10]) or 'nothing printed'})"
            else:
                state = "OK"
        except RuntimeError as error:
            state = f"NOT BUILT OR NOT ELABORATED ({(str(error).splitlines() or ['no output'])[-1]})"
        results.append(("frozen declarations (types, definition values and dependency .olean files)",
                         state))
    passed = all(state == "OK" for _, state in results)
    for path, state in results:
        print(f"{path}: {state}")
    for warning in global_commands(root, data):
        print(f"warning: global command in a helper module: {warning}")
    print("PASS" if passed else "FAIL")
    return 0 if passed else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="action", required=True)
    rec = sub.add_parser("record", help="record the approved files")
    rec.add_argument("--out", required=True, help="JSON record to write")
    rec.add_argument("--root", default=".", help="project root (default: current directory)")
    rec.add_argument("--file", action="append", default=[], metavar="PATH", help="frozen whole")
    rec.add_argument("--holes", action="append", default=[], metavar="PATH",
                     help="frozen except its `sorry` holes")
    rec.add_argument("--decl", action="append", default=[], metavar="NAME",
                     help="frozen declaration, recorded with the project declarations it uses")
    rec.add_argument("--module", action="append", default=[], metavar="MODULE",
                     help="module imported to elaborate the declarations, e.g. Project.Statements")
    rec.add_argument("--lake", default="lake", help="Lake executable")
    chk = sub.add_parser("check", help="check a tree against the record")
    chk.add_argument("record", help="JSON record written by `record`")
    chk.add_argument("--root", default=".", help="project root or worktree (default: current directory)")
    chk.add_argument("--lake", default="lake", help="Lake executable")
    args = parser.parse_args()
    return {"record": record, "check": check}[args.action](args)


if __name__ == "__main__":
    sys.exit(main())
