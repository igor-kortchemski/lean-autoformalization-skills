---
name: lean-project-architecture
description: Design a Lean formalization and its public-result comparison interface. Use when choosing mathematical encodings, module boundaries, target statements, or a proof plan; not for routine edits within an established API.
license: CC-BY-4.0
---

# Design for proof and publication

Start from the source result, the existing repository, and the intended
declarations. Preserve already approved interfaces. For a new project, establish
the current supported environment before building substantial infrastructure;
for an existing project, report incompatibilities without silently upgrading it.

## Settle the mathematical interface

Write down the target's premises, conclusion, carrier, boundary cases, and
constant dependence. Work autonomously within scope and existing authorization,
resolving ambiguities from the source, project context, and prior decisions first.
Ask only for essential missing input, decisions, or authorization needed for
faithful completion; explain the blocker and continue independent work. If
questions are prohibited, record the blocker and leave dependent work pending
without guessing mathematics or permission.

Preserve the claimed mathematics. An equivalent encoding needs a clear
mathematical justification, not necessarily identical notation.

Prefer existing Mathlib objects and APIs. Choose an ambient carrier that fits
the mathematics and downstream theorems. Build the access and characterization
lemmas that make an encoding usable before expanding the proof campaign.

Exploration is allowed: prototype alternative statements and constructions in
the repository-approved scratch area without unauthorized axioms or holes.
Distinguish candidates from accepted source statements. Proof attempts can inform
API design; there is no requirement to finalize every helper before starting.

For an object specified by a property, establish existence and the properties
needed by its clients. Establish uniqueness or choice independence when the
source or later claims require it. A constructive definition may precede its
characterization proof; do not claim source fidelity until that bridge is proved.
Honor stricter project rules, including any requirement to land them together.

## Keep a small public-result comparison interface

Use Comparator by default when publishing named mathematical results, including
small or one-theorem GitHub-only projects. Design a small Challenge/Solution pair
for the selected public exports and their semantic dependencies; no per-helper
comparison interface is needed.

Reconstruct and review the Challenge against the mathematical source independently
of the proof implementation, so a mathematician can read it on its own. Plan the
exact compared declarations, Challenge/Solution and Comparator configuration paths,
and candidate revision. The compared fully qualified names and elaborated types
must match, together with their semantic definition closure; matching interfaces
does not itself establish source fidelity.

Keep statement definitions public and their needed bodies exposed under the
pinned toolchain's visibility conventions. Definitions copied into the Challenge
must retain their mathematical content and the identities required by Comparator. Avoid
private generated names or helper dependencies that cannot travel with them.
Plan and audit the transitive statement closure, not just the top-level imports.

Separate statement and proof modules so proof code never imports the Challenge
or a quarantined draft. If the project has frozen declarations, retain its
manifest, provider, and sealing protocol exactly. A new project does not need
an additional internal freezing system merely because it uses Comparator.

Respect existing proof-hole rules: a comparison interface does not authorize new
Challenge holes or exceptions to frozen declarations. Publication targets use
Palomar's permitted axioms and any stricter project policy. Report conflicts with
established toolchains, dependencies, or proof policy before changing them.

For work intended for publication, target Palomar-compatible artifacts by default.
Use `lean-publication` for current policy references when available, or consult
the [official submission standard](https://github.com/PalomarRegistry/PalomarPolicy/blob/main/CONTRIBUTING.md)
directly. Apply the Challenge import allowlist, module conventions, size limits,
and axiom restrictions during design. Full preflight and registry actions remain
separate requested work. Prefer Mathlib-only statement dependencies when adequate;
additional Challenge libraries must satisfy
that allowlist, separately from Solution dependencies. Leave margin under Challenge
and repository-wide Lean-file limits, and plan any required module-system port early.

## Plan only enough to unblock proofs

Prioritize proving every main result and its required dependencies, while
retaining all other in-scope claims as completion obligations.

For a small result, a short list of target, next lemmas, and unresolved decisions
is sufficient. Expand a dependency graph only when task size or an explicit
request warrants it. Record substantive obligations, external inputs, and
alternative proof routes; an edge never licenses adding a premise to the target.

When extracting a source proof graph, give steps stable names and source
locators, distinguish conjunctions from alternative routes, and mark missing
arguments. Review the routes that carry the main result. A complete proof
database and per-node metadata are optional deliverables, not prerequisites for
useful Lean work. Topology is not proof status.

End with concrete declarations or design choices, a feasible next proof task,
and any unresolved obstruction. Before substantial proof work, obtain a passing
independent statement-fidelity review of the main interface; reuse valid review
and revisit affected findings after semantic changes. Ordinary internal helpers
need no separate approval cycle.

Use `lean-statement-audit` when available; otherwise have one reviewer who did
not author the declaration compare the exact source, elaborated statement, and
relevant definitions using this skill's fidelity rules. Claims relying on
unresolved source ambiguity or missing semantic justification cannot pass;
work to establish a missing bridge can proceed after review of its own target.
No additional installation or user approval is required beyond existing project
rules.
