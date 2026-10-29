---
name: lean-elaboration
description: Diagnose slow Lean elaboration, heartbeat failures, or build regressions, and run requested performance benchmarks. Use when measured performance needs attention, not as a prerequisite for ordinary proof work.
license: CC-BY-4.0
---

# Lean performance

Measure the suspected cost, change one cause, and compare. Preserve theorem
statements, mathematical definitions, pinned versions, and the project's build
and concurrency rules. Performance work grants no exception to frozen files.

Work autonomously within scope and existing authorization, resolving uncertainties
from available evidence, project context, and prior decisions first. Ask only for
essential missing input, decisions, or authorization needed for faithful completion;
explain the blocker and continue independent work. If questions are prohibited,
record the blocker and leave dependent work pending without guessing mathematics
or permission.

## Establish a useful baseline

Read the build wrapper, toolchain, and relevant prior timings. Use the narrowest
target covering the problem. Record the commit and local changes, exact command,
cache state, result, and observed machine load. Follow any single-build rule;
do not interrupt another person's build to obtain cleaner measurements.

Check the pinned executable's help or local documentation for profiling flags.
Profile a warm file after its dependencies are available. Distinguish time spent
loading imports, elaborating statements, executing tactics, and checking terms.
A Lake job duration is not CPU time; summing job durations does not measure CPU.
Profiler categories can overlap and remain sensitive to contention.

Use source locations and targeted traces to locate expensive declarations.
Inspect whether the cost comes from a signature or its proof before editing
tactics. Do not insert `sorry`, new axioms, or weakened statements as probes.

## Match the intervention to the evidence

| Observed cost | Candidate change |
| --- | --- |
| Import loading | Narrow a consumer's imports; compile to catch implicit instance and tactic dependencies. Splitting helps only if consumers load less or useful parallelism becomes available. |
| Typeclass search with unresolved types | Add type ascriptions or explicit arguments where inference first loses the intended type. More instances usually worsen this search. |
| Repeated search for a fully determined instance | Try a narrowly scoped, explicit instance or local cache; check overlap and downstream effects. Do not apply caches by analogy. |
| Expensive simplification | Use a small `simp only` set, a named rewrite, or `exact`/`rfl` for the particular hot call. Avoid blanket simplifier rewrites. |
| Arithmetic automation | Limit hypotheses with `linarith only`; use named inequalities and `calc`. Isolate a polynomial argument over abstract reals before feeding transcendental expressions to nonlinear automation. |
| Dependent unification | Supply explicit intermediate types; use the abstraction expected by the consumer inside implementation code. Keep frozen binders unchanged unless existing authorization permits the change. |
| Congruence search | When the function is known, try `congrArg f` with that function explicit. |
| Large proof terms or kernel checking | Extract useful lemmas and reduce repeated computation; include replay cost when assessing the result. |

Choose the smallest plausible change. A short helper with a clean context can
help; splitting files or adding caches without evidence can make builds slower.
Raising a heartbeat limit changes a budget, not the underlying cost. Respect
local limits and do not present a budget increase as a performance improvement.

## Compare and finish

Run baseline and candidate with the same versions, target, cache conditions,
and comparable machine load. Repeat measurements when the difference is near
run-to-run variation. Check the relevant profile and end-to-end elapsed time;
neither is immune to noise. Rebuild affected consumers after structural changes.
Keep improvements supported by the evidence; revert only your own unsuccessful
edits. Stop tuning a technique when repeated trials show no useful gain.

For publication targets, including GitHub-only artifacts intended to be
Palomar-compatible, a faster elaborator is insufficient if the resulting term is
costly for the independent kernel. Reject native-evaluation axioms, including any
introduced by `native_decide` or `bv_decide` in the pinned toolchain.
Recheck affected exports' transitive axiom closures against
`propext`, `Classical.choice`, and `Quot.sound`. Run the project's independent
replay when term size or kernel computation is the issue. Full Palomar preflight
belongs to requested verification or submission, not ordinary performance tuning.

## Requested repository benchmark

Use this mode only for a requested benchmark or a diagnosed project-wide issue.
Confirm the target actually covers the intended modules. Report elapsed time,
CPU and peak memory when available, slow modules, and the main sources of cost.
Use the platform's timing tool correctly; GNU and BSD `time` differ.

A cold project rebuild with warm dependency caches needs the project's approved
invalidation procedure or an isolated checkout with those caches prepared.
Do not run `lake clean`,
delete dependency artifacts, update pins, or trigger dependency compilation to
collect a timing. If required caches are missing, report the setup issue before
measuring. Label a warm or partial build accurately rather than calling it clean.

Record the decisive commands, before/after measurements, validation results, and
limitations in the existing project notes. A compact table is usually enough.
