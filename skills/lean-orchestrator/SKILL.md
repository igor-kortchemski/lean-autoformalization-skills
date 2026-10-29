---
name: lean-orchestrator
description: Coordinate parallel or long-running Lean paper formalization without losing result coverage, statement fidelity, or control of shared builds. Use when multiple proof tasks, agents, or integration branches need coordination; not for a single local proof.
license: CC-BY-4.0
---

# Coordinate mathematical work

Read the active project plan and rules, declared paper scope, and
the existing coverage record or `FORMALIZATION_REPORT.md` if used. Reuse the
existing workflow. Keep the main mathematical interface and integration
decisions with one owner. Preserve approved frozen statements and their
dependency definitions; this skill creates
no new exception to the project's axiom or draft policy.

When publication is intended, resolve interface and dependency choices against
current artifact requirements before assigning dependent proof work. Use
`lean-project-architecture` and `lean-publication` as needed, or consult the
[official submission standard](https://github.com/PalomarRegistry/PalomarPolicy/blob/main/CONTRIBUTING.md)
directly. Reuse settled project decisions; full Palomar preflight remains separate
requested work.

## Split by actual independence

Prioritize proving every main result and its required dependencies, while
retaining all other in-scope claims as completion obligations.

Use one proof worker by default for ordinary work. Identify the next paper
results whose inputs are available. Delegate substantial independent proofs,
Mathlib searches, alternative-route explorations, or source reviews when their
benefit justifies duplicated context and coordination. Lower elapsed time need
not mean lower total compute. Avoid assigning dependent implementation tasks
before their shared API is settled.

Before assigning substantial proof tasks, check that the relevant main statements
and shared source-facing interfaces have passed independent statement-fidelity
review; batch related reviews and continue independent work while they are pending.
Use `lean-statement-audit` when available; otherwise have one reviewer who did
not author the declaration compare the exact source, elaborated statement, and
relevant definitions. Check explicit and bundled premises, quantifier and witness
scope, carriers, normalization, boundary cases, coercions, and required
characterizations or equivalences.
Claims relying on unresolved source ambiguity or missing semantic justification
cannot pass; work to establish a missing bridge can proceed after review of its
own target.
No additional installation or user approval is required beyond existing project
rules.

Give each worker the exact target, source location, owned files, usable inputs,
validation command, and relevant project constraints. Include the obstruction
that should cause a handoff. Do not copy an entire policy collection into every
brief.

Use disjoint file ownership or isolated worktrees when available. A small task
does not need a branch per lemma. Never overwrite unrelated edits or assume a
worker's summary proves its code is correct.

Workers explore and adopt proof routes autonomously, preserving the requested
mathematics, complete declared coverage, and established project requirements.
Record substantive departures and accurately state which paper arguments were
checked; workers report unresolved blockers to the coordinator.

The coordinator resolves uncertainties from the source, project context, and
prior decisions and consolidates only questions about essential missing
information, decisions, or authorization that block faithful completion. Reuse
existing authorization, identify the exact blocker, and continue independent
authorized work. If the user requests no questions, record and report blockers,
leave dependent work pending, and do not guess the mathematics or authorization.

## Keep builds coordinated

Respect the repository's build limit across workers. Under a one-build rule,
have a single coordinator schedule compilation while other workers search,
write, or review. A live build is not permission to delete caches, kill jobs, or
start another conflicting build. Use an existing compile gate when provided; do
not install a new machine-wide scheduling framework for a small campaign.

Coordinate invocations that share build outputs while preserving Lake's internal
parallelism. Isolated work need not be serialized unless project rules or shared
resource limits require it.

At handoff, include changed files, the validation command and target, its result,
and a reference to the actual output. Review each diff and run target checks
before integration, reusing outputs only while their source, proof bodies,
dependencies, toolchain, configuration, and targets remain unchanged. Rebuild
affected consumers when interfaces or imports change. Batch independent edits
only when their joint validation remains understandable, and batch related axiom queries
after a coherent integration group. Preserve dependency artifacts and other
sessions' staged changes.

## Track mathematics rather than ceremony

Use the project's existing equivalent coverage and difference record or
`FORMALIZATION_REPORT.md`, updated at coherent milestones rather than per helper.
Put advisory exposition observations in `MANUSCRIPT_RECOMMENDATIONS.md`, which
may remain empty. Do not
create a second status system unless the repository already requires one.

Distinguish proved results, conditional helpers, explored alternatives, and open
obligations. Investigate viable proof alternatives; never add an obstruction as
a new hypothesis of the advertised theorem.

For a paper campaign, initially inventory its declared scope independently of
the implementation, or reuse an inventory checked against the same source and
scope. Keep isolated theorem reviews scoped to the theorem and its relevant
dependencies. At coverage milestones, review changed exports and affected dependencies and consumers,
verify current axiom evidence, and preserve individually valid coverage entries.
Reuse statement-fidelity findings when source, elaborated statements, and semantic
dependencies are unchanged; after proof changes, check the proof route and relevant
implementation dependencies and refresh affected correspondence findings.
Preserve findings, review status, and required fresh review: reused independent
components may satisfy the corresponding obligations, while self-review does not replace
an available or required independent review. No such review is required per helper.

When the source or declared scope changes and before claiming whole-paper
completion, scan that scope for omitted results and reconcile the report.
For GitHub publication, Palomar, or both, hand the final tree and evidence to
`lean-publication` if installed. Do not imply that coordination, agent consensus,
or a complete-looking table substitutes for kernel
verification.

Finish when the scope is verified, an applicable resource limit is reached, or
no useful authorized work remains. Report changed results, checks, route
decisions, and remaining work. Avoid per-helper manifests, repetitive forms,
and invented progress percentages.
