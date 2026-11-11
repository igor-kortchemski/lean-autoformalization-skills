#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Regression cases for lean-library's `check_library.py` on a throwaway Lake project.

Needs Elan and the toolchain below (no Mathlib, no network). Each case writes a small
project in a temporary directory, with the Lake options that `lean-library` prescribes,
and runs the copied check:

1. a clean library with a module that nothing imports and an example passes;
2. a `sorry` fails the check and passes with `--allow-sorry`, which lists it;
3. an added axiom fails, even with `--allow-sorry`;
4. `--names` passes on resolving names, fails on a missing one, and reports a name
   that depends on `sorryAx`.

    python3 validation/check_library_test.py [--toolchain leanprover/lean4:v4.35.0]
"""

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

SCRIPT = Path(__file__).resolve().parents[1] / "skills/lean-library/assets/check_library.py"

LAKEFILE = """name = "toy"
defaultTargets = ["Toy"]

[leanOptions]
autoImplicit = false

[[lean_lib]]
name = "Toy"
globs = ["Toy.*"]
"""


def make_project(root: Path, toolchain: str, extra: str) -> None:
    (root / "Toy").mkdir(parents=True)
    (root / "ToyTest").mkdir()
    (root / "scripts").mkdir()
    (root / "lean-toolchain").write_text(toolchain + "\n")
    (root / "lakefile.toml").write_text(LAKEFILE)
    (root / "Toy.lean").write_text("import Toy.Basic\n")
    (root / "Toy/Basic.lean").write_text("theorem Toy.one : 1 = 1 := rfl\n")
    (root / "Toy/Orphan.lean").write_text("theorem Toy.two : 2 = 2 := rfl\n" + extra)
    (root / "ToyTest/Use.lean").write_text("import Toy.Basic\nexample : 1 = 1 := Toy.one\n")
    script = SCRIPT.read_text(encoding="utf-8")
    script = script.replace('LIBRARY = "MyLib"', 'LIBRARY = "Toy"', 1)
    script = script.replace('EXAMPLES = ["MyLibTest"]', 'EXAMPLES = ["ToyTest"]', 1)
    (root / "scripts/check.py").write_text(script)


def check(root: Path, *args: str) -> tuple[int, str]:
    done = subprocess.run([sys.executable, "scripts/check.py", "--no-doc-lint", *args],
                          cwd=root, capture_output=True, text=True)
    return done.returncode, done.stdout + done.stderr


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--toolchain", default="leanprover/lean4:v4.35.0")
    args = parser.parse_args()
    if shutil.which("lake") is None:
        print("lake not found: install Elan first", file=sys.stderr)
        return 2
    failures = []

    def expect(name: str, ok: bool, output: str) -> None:
        print(("PASS " if ok else "FAIL ") + name, flush=True)
        if not ok:
            failures.append(name)
            print(output[-2000:])

    cases = {
        "clean": "",
        "sorry": "theorem Toy.hole : 3 = 3 := sorry\n",
        "axiom": "axiom Toy.bad : False\ntheorem Toy.worse : 1 = 2 := Toy.bad.elim\n",
    }
    with tempfile.TemporaryDirectory(prefix="check-library-test-") as temporary:
        roots = {}
        for case, extra in cases.items():
            roots[case] = Path(temporary) / case
            make_project(roots[case], args.toolchain, extra)

        code, out = check(roots["clean"])
        expect("clean library with an unimported module passes",
               code == 0 and "Check passed: 3 library" in out, out)

        code, out = check(roots["sorry"])
        expect("sorry fails without --allow-sorry", code != 0, out)
        code, out = check(roots["sorry"], "--allow-sorry")
        expect("sorry passes with --allow-sorry and is listed",
               code == 0 and "Toy.hole" in out and "sorryAx" in out, out)

        code, out = check(roots["axiom"], "--allow-sorry")
        expect("added axiom fails even with --allow-sorry",
               code != 0 and "Forbidden axiom Toy.bad" in out, out)

        names = roots["sorry"] / "names.txt"
        names.write_text("# coverage index\nToy.one\nToy.two\nNat.add_comm\n")
        code, out = check(roots["sorry"], "--allow-sorry", "--names", str(names))
        expect("--names passes on resolving names",
               code == 0 and "Coverage index: 3 names resolve" in out, out)
        names.write_text("Toy.one\nToy.missing\n")
        code, out = check(roots["sorry"], "--allow-sorry", "--names", str(names))
        expect("--names fails on a missing name", code != 0 and "Toy.missing" in out, out)
        names.write_text("Toy.hole\n")
        code, out = check(roots["sorry"], "--allow-sorry", "--names", str(names))
        expect("--names reports a name that depends on sorryAx",
               code == 0 and "1 listed names depend on sorryAx" in out, out)

    print(f"{len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
