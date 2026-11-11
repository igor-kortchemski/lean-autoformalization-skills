# Testing

What was actually checked, between 4 and 10 November 2026, on one machine: a
four-core Mac with 24 GB of memory, Lean 4.35.0 and Mathlib v4.35.0,
Claude Code with Opus 5.5 as coordinator, Codex CLI 0.165.0. The full dated log
is unpublished; this page summarizes it.
Nothing here certifies a project: every result a campaign produces must still
pass its own build, axiom check and audits.

Model names, prices and quotas below are those of November 2026 and will age.

## Automatic checks

- [`validation/check_package.py`](validation/README.md) checks the package
  itself: local links and heading anchors, display math, code fences, skill
  and agent frontmatter, the syntax of the bundled scripts and of the shell
  examples. It runs in CI.
- [`validation/check_library_test.py`](validation/check_library_test.py) runs
  `lean-library`'s `check_library.py` on throwaway Lake projects (Lean only, no
  Mathlib): a clean library passes, a `sorry` fails unless allowed, an added
  axiom always fails, an unimported module is still built.

## Scripts, tested without a model

- **`codex_worker.py`**, with stub workers in place of Codex: exit codes are
  propagated; each launch gets a fresh attempt directory; `cancel` stops the
  worker's process group, including a real Lean process started from a shell;
  a process it cannot attribute to the attempt is never signalled; the time
  limit (`--max-minutes`) stops the worker and its builds with exit 124. With a
  fake `codex`, sixteen cases of the choice between several accounts passed
  (weights, quota floors, a server block, no eligible account, a resumed
  session kept on its account).
- **`freeze_check.py`**, on small Lean projects. An early version compared
  only the text outside the proof holes, and Lean accepted this file, which
  proves a false statement from a filled hole:

  ```lean
  theorem first (x : Nat) (h : 0 < x) : 0 < x := by
    exact h
    local instance (priority := high) instLENatTriv : LE Nat := ⟨fun _ _ => True⟩

  theorem second (n : Nat) : n ≤ 0 := by
    trivial
  ```

  The check now rejects commands inside a hole and compares the elaborated
  type of each frozen declaration, and the value of every project definition
  it uses, printed with `pp.all`. Tested: legitimate multi-line proofs pass;
  injected instances, notations, `#exit`, changed hypotheses, appended
  declarations, an instance added in a helper module, and names differing only
  after a space are all reported.
- **Quota readers and floors**: `codex_quota.py` against the live Codex
  `app-server` and a simulated server block; the Open Math OS floors of both
  launchers against simulated Platform API readings (launches refused below
  the floor or on an unreadable quota).
- **Refactoring of 10 November 2026**: old and new hole matching agree on
  hand-written Lean snippets and 20,000 random inputs.

## Campaign trials

On a published research paper, in copies of its Lean project:

- **One node, one Luna worker** (4 November): statement audited, approved and
  frozen; the worker proved it in 16 minutes under Codex's `workspace-write`
  sandbox; seal passed (frozen text unchanged, build, standard axioms only,
  independent Sonnet re-audit).
- **Five nodes with real dependencies** (4 November): four proved by Luna at
  `xhigh` (18 to 23 minutes each, first attempt), one by a Sonnet worker, all
  sealed. Two workers ran at once in separate worktrees with cloned `.lake`
  directories (`cp -c -R -p`; without `-p` Lake rebuilds everything). A worker
  cancelled during a build was resumed and finished. The cleanup phase replaced
  `import Mathlib` by targeted imports and roughly halved the library build.
- **Open Math OS through Codex** (5 November): three routine nodes, two by
  Kimi K3.1 Pro at `high` (about 11 minutes each) and one by DeepSeek V4.1
  Flash, all compiled at the first handoff with the frozen types and standard
  axioms.
- **Open Math OS VM** (5 and 6 November): replays of nodes already solved, from
  packages with no trace of the solution, re-verified locally. Kimi at `high`
  was the cheapest effort that succeeded on both a routine node (about
  6 minutes) and a hard node (7 holes, 16 minutes); `max` brought no gain, `low`
  sufficed for repairs. One run per cell: suggestive, not a ranking. Four VM
  workers at once fit in memory; each build took about three times as long.
  One failure mode was seen once (Kimi repeating a no-op tool call), hence the
  cost caps and the stop on repeated identical calls.

## Library and book skills

`check_library.py` was run on small module-system and non-module projects:
every module built, including an unimported one; a public theorem resting on a
`private` lemma closed by `sorry` failed the axiom audit, as did an unused
`axiom`. `lean-library` and `lean-book` were audited twice, read-only, but have
not run on a real project.

## Lean Beam (optional)

A pilot of Lean Beam 0.2.0 on a built project of 83 modules: after a first
call of 23 to 42 seconds per file, probes took 0.04 to 0.27 seconds, against
15 to 45 seconds for a temporary file; about 1 GB per open document plus
1.2 GB for the server; compiled files unchanged after Beam stopped. Read-back
text matches a temporary probe only from a module that opens nothing, which is
why the profile asks for one.

## Audits

The package went through several independent read-only audits (Claude
reviewers, Codex, and one review on Open Math OS), among them an audit for
over-engineering that shortened the coordinator's instructions from about
9,300 to about 4,200 words without removing a safeguard. Every finding of high
or medium severity was checked before being fixed.

## Not yet tested

- A full research-paper formalization, and a Palomar submission.
- `lean-library` and `lean-book` on a real project.
- The quota floors and the token ledger in a live campaign (simulated only).
- The caps at their limits: at most two Codex workers and two Sonnet subagents
  ran at once, so the local defaults remain estimates for a four-core machine.
- Open Math OS models on hard nodes through Codex workers, and VM workers on
  nodes not solved before.
- The loss of the coordinator's session while workers run.
- The read-back step, the hidden-content checks of an audit, and the
  corrections deliverable in a campaign.
- Background Claude workers, which need a launcher not included here.

Refine the skills from observed failures, not hypothetical cases.
