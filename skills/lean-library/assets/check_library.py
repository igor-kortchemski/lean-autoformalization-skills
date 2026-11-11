#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Adapted, with modifications, from the repository check and lint report scripts
# of one of the author's Lean libraries (Apache-2.0).
"""Build every library module, compile the examples, and audit axioms and docstrings.

Copy this file to `scripts/check.py` in the library's repository, set the constants
below once, and run it from anywhere: `python3 scripts/check.py`. CI runs the same
command. It

1. discovers every `.lean` file of the library (and of the vendored packages) from
   the checkout, never from a hand-maintained list, and builds each one explicitly
   with `lake build --wfail`, so a module that nothing imports is still checked and
   any warning fails the check;
2. compiles each example file with `autoImplicit` off and warnings as errors (an
   example imports only library modules and dependencies, not another example);
3. generates a temporary, non-module Lean file importing every module, which loads
   private declarations and proofs under the module system too, and checks that
   every constant depends only on the allowed axioms (its axiom closure);
4. runs `#lint only docBlame` (needs Batteries, which Mathlib brings).

`--allow-sorry` is for a campaign branch whose frozen statements still have
registered `sorry` holes: the build runs without `--wfail`, and the audit lists the
declarations that depend on `sorryAx` instead of failing on them. Every other axiom
still fails, and a release needs an empty list. This mode accepts any `sorry`;
`freeze_check.py` (lean-orchestrator) is what checks that only registered holes
remain.

`--names FILE` checks a coverage index: FILE lists one fully qualified declaration
name per line (blank lines and `#` comments ignored). The check fails if a name does
not resolve, and reports the names whose axiom closure contains `sorryAx`.

With `--lint-report` it runs the environment linters (`#lint`) over every built
module instead, Mathlib's own ones included when Mathlib is a dependency, and prints
the findings by linter. It exits 0 unless `--strict` is given and a linter reports
something: a non-blocking CI job uses it without `--strict`, a blocking one with it.

The axiom closure does not replay declarations in the kernel; use `lake check` or
Comparator for that, and search the sources for `debug.skipKernelTC`.

Adapted from the repository check of one of the author's Lean libraries.
Tested with Lean 4.35.0; older toolchains may need changes.
"""

import argparse
import json
from collections import Counter
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]

# --- Project settings: edit once. -------------------------------------------------
LIBRARY = "MyLib"  # name of the `lean_lib` and of its root folder and root file
VENDORED = []  # e.g. [("vendor/some-package", "SomePackage")]
EXAMPLES = ["MyLibTest"]  # files or folders of self-contained example files
ALLOWED_AXIOMS = ["propext", "Classical.choice", "Quot.sound"]
EXAMPLE_OPTIONS = ["-DautoImplicit=false", "-DwarningAsError=true"]
# -----------------------------------------------------------------------------------

IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_']*")


def lean_name(module: str) -> str:
    """Write a module name for Lean source, quoting components that need `«…»`."""
    return ".".join(c if IDENT.fullmatch(c) else f"«{c}»" for c in module.split("."))


def modules(package: Path, root: str) -> list[str]:
    """Return the module names of `root`, its root file first when it exists."""
    sources = sorted(p for p in (package / root).rglob("*.lean") if ".lake" not in p.parts)
    if (package / f"{root}.lean").is_file():
        sources.insert(0, package / f"{root}.lean")
    if not sources:
        raise SystemExit(f"No Lean sources found for {root} in {package}")
    return [".".join(p.relative_to(package).with_suffix("").parts) for p in sources]


def run(*args: str) -> None:
    shown = " ".join(args)
    print("+ " + (shown if len(shown) < 300 else shown[:300] + f" … ({len(args)} arguments)"),
          flush=True)
    done = subprocess.run(args, cwd=ROOT)
    if done.returncode != 0:
        raise SystemExit(done.returncode)


def has_mathlib() -> bool:
    """Whether Mathlib is among the dependencies recorded in the Lake manifest."""
    try:
        manifest = json.loads((ROOT / "lake-manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return any(p.get("name") == "mathlib" for p in manifest.get("packages", []))


def read_names(path: str) -> list[str]:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [ln.strip() for ln in lines if ln.strip() and not ln.lstrip().startswith("#")]


def audit_source(names: list[str], library: str, doc_lint: bool, allow_sorry: bool,
                 catalog: list[str]) -> str:
    imports = "\n".join(f"import {lean_name(name)}" for name in names)
    tools = ["Lean.Elab.Command", "Lean.Util.CollectAxioms"]
    tools += ["Batteries.Tactic.Lint"] if doc_lint else []
    tool_imports = "\n".join(f"import {name}" for name in tools)
    expected = ", ".join(f"`{lean_name(name)}" for name in names)
    allowed = ", ".join(f"`{name}" for name in ALLOWED_AXIOMS)
    lint_cmd = f"\n#lint only docBlame in {library}\n" if doc_lint else ""
    allow = "true" if allow_sorry else "false"
    listed = ", ".join(f"`{lean_name(name)}" for name in catalog)
    return f"""{imports}
{tool_imports}

/-! Generated axiom audit of every project constant, private and generated ones included. -/

open Lean in
set_option maxHeartbeats 0 in
-- One pass over every constant of the audited modules.
run_cmd do
  let env ← getEnv
  let expected : Array Name := #[{expected}]
  let allowed : Array Name := #[{allowed}]
  let allowSorry : Bool := {allow}
  let mut checked : Nat := 0
  let mut holes : Array Name := #[]
  let catalog : Array Name := #[{listed}]
  let mut unresolved : Array Name := #[]
  let mut catalogHoles : Array Name := #[]
  for name in catalog do
    if env.contains name then
      if (← collectAxioms name).contains ``sorryAx then
        catalogHoles := catalogHoles.push name
    else
      unresolved := unresolved.push name
  unless unresolved.isEmpty do
    throwError "{{unresolved.size}} listed names do not resolve: {{unresolved.toList}}"
  unless catalogHoles.isEmpty do
    logWarning m!"{{catalogHoles.size}} listed names depend on sorryAx: {{catalogHoles.toList}}"
  unless catalog.isEmpty do
    logInfo m!"Coverage index: {{catalog.size}} names resolve, {{catalogHoles.size}} depend on sorryAx."
  for modName in expected do
    unless env.header.moduleNames.contains modName do
      throwError "Missing audited module {{modName}}"
  for idx in [:env.header.moduleNames.size] do
    if expected.contains env.header.moduleNames[idx]! then
      for name in env.header.moduleData[idx]!.constNames do
        for ax in (← collectAxioms name) do
          if allowSorry && ax == ``sorryAx then
            holes := holes.push name
          else unless allowed.contains ax do
            throwError "Forbidden axiom {{ax}} in {{name}}"
        checked := checked + 1
  if checked == 0 then throwError "Audit selected no project constants"
  logInfo m!"Axiom audit passed: {{checked}} constants from {{expected.size}} modules."
  unless holes.isEmpty do
    logWarning m!"{{holes.size}} declarations depend on sorryAx (registered holes?): {{holes.toList.take 50}}"
{lint_cmd}"""


def example_files(entries: list[str]) -> list[Path]:
    files = []
    for entry in entries:
        path = ROOT / entry
        if path.is_dir():
            files.extend(sorted(p for p in path.rglob("*.lean") if ".lake" not in p.parts))
        elif path.is_file():
            files.append(path)
        else:
            raise SystemExit(f"Example path not found: {entry}")
    return files


def lint_report(names: list[str], library: str, strict: bool) -> int:
    probe = "\n".join(f"import {lean_name(name)}" for name in names)
    probe += "\nimport Batteries.Tactic.Lint"
    probe += "\nimport Mathlib.Tactic.Linter.Lint" if has_mathlib() else ""
    probe += f"\n\n#lint in {library}\n"
    with tempfile.TemporaryDirectory(prefix="lint-report-") as temporary:
        path = Path(temporary) / "Lint.lean"
        path.write_text(probe, encoding="utf-8")
        done = subprocess.run(["lake", "env", "lean", str(path)], cwd=ROOT,
                              capture_output=True, text=True)
    output = done.stdout + done.stderr
    counts: Counter[str] = Counter()
    linter = None
    for line in output.splitlines():
        found = re.match(r"/- The `(\w+)` linter reports", line)
        if found:
            linter = found.group(1)
        elif line.startswith("#check") and linter:
            counts[linter] += 1
    if done.returncode != 0 and not counts:
        print(output)
        print("lint probe failed: build the library first", file=sys.stderr)
        return 2
    summary = [ln for ln in output.splitlines() if "errors in" in ln or "linting checks" in ln]
    print(output if counts else "\n".join(summary))
    for name, count in sorted(counts.items()):
        print(f"{name}: {count}")
    return 1 if strict and counts else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--library", default=LIBRARY, help="override LIBRARY")
    parser.add_argument("--examples", nargs="*", help="override EXAMPLES")
    parser.add_argument("--no-doc-lint", action="store_true",
                        help="skip #lint only docBlame (for a project without Batteries)")
    parser.add_argument("--allow-sorry", action="store_true",
                        help="list declarations depending on sorryAx instead of failing")
    parser.add_argument("--lint-report", action="store_true",
                        help="run Mathlib's environment linters instead of the check")
    parser.add_argument("--strict", action="store_true",
                        help="with --lint-report, exit 1 if any linter reports a finding")
    parser.add_argument("--names", metavar="FILE",
                        help="check that the declarations listed in FILE resolve")
    args = parser.parse_args()
    library = args.library
    names = modules(ROOT, library)
    vendored = [m for path, root in VENDORED for m in modules(ROOT / path, root)]
    if args.lint_report:
        return lint_report(names, library, args.strict)
    strict = [] if args.allow_sorry else ["--wfail"]
    run("lake", "build", *strict, library,
        *(f"+{lean_name(name)}" for name in names + vendored))
    lean = ("lake", "env", "lean", *EXAMPLE_OPTIONS)
    examples = example_files(EXAMPLES if args.examples is None else args.examples)
    for path in examples:
        run(*lean, str(path))
    with tempfile.TemporaryDirectory(prefix="library-check-") as temporary:
        audit = Path(temporary) / "Audit.lean"
        catalog = read_names(args.names) if args.names else []
        audit.write_text(audit_source(names + vendored, library, not args.no_doc_lint,
                                      args.allow_sorry, catalog), encoding="utf-8")
        run("lake", "env", "lean", str(audit))
    print(f"Check passed: {len(names)} library and {len(vendored)} vendored modules, "
          f"{len(examples)} example files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
