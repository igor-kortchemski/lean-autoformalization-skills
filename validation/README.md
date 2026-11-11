# Package check

[`check_package.py`](check_package.py) checks local links and heading anchors,
MacDown-compatible display math, code fences, skill YAML metadata, the
frontmatter of the Claude agent definitions, the syntax of the bundled Python
scripts, and the shell syntax of every `sh` example in the Markdown files.
It uses only the Python standard library and runs `git diff --check` when the
package is a Git repository:

```sh
python3 validation/check_package.py
```

It does not execute a model, launch a worker, install skills, or build Lean.

## Regression cases of the library check

[`check_library_test.py`](check_library_test.py) copies `lean-library`'s
`check_library.py` into throwaway Lake projects (Lean only, no Mathlib, no
network) configured as the skill prescribes, and checks that a clean library
with an unimported module passes, that a `sorry` fails unless `--allow-sorry`
is given, that an added axiom always fails, and that `--names` passes on
resolving names, fails on a missing one, and reports one that depends on
`sorryAx`. It needs Elan and the Lean toolchain it names (default 4.35.0):

```sh
python3 validation/check_library_test.py
```
