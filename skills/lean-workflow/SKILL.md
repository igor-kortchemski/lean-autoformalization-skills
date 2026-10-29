---
name: lean-workflow
description: Write, repair, or refactor Lean 4 proofs in Mathlib projects. Use for ordinary formalization work, including paper-result coverage, lemma search, and focused validation; use specialized skills only for design, source audits, measured performance, coordination, or publication.
license: CC-BY-4.0
---

# Lean proof development

The output is useful Lean mathematics with evidence for the claim being made.
Read the project's instructions, pinned environment, nearby code, and declared
source scope first. Existing author approvals, frozen interfaces, quarantine
rules, and build limits remain binding. This skill does not authorize changing
them.

Work autonomously within scope and existing authorization, resolving uncertainties
from the source, project context, and prior decisions first. Ask only for essential
missing input, decisions, or authorization needed for faithful completion;
explain the blocker and continue independent work. If questions are prohibited,
record the blocker and leave dependent work pending without guessing mathematics
or permission.

## Work at the smallest useful scale

1. Identify the exact goal and its mathematical source, if any. Inspect the
   definitions that determine its meaning and distinguish source assumptions
   from facts that the proof must establish.
2. Search the installed Mathlib revision and the project before inventing an
   object or lemma. Search by mathematical concept, namespace, conclusion shape,
   and nearby APIs. Inspect the actual declaration, hypotheses, and imports.
   Use [proof-tools.md](references/proof-tools.md) when search or tactics stall.
3. Before substantial proof work on a main source result or substantial work
   depending on a source-facing interface, obtain a passing independent
   statement-fidelity review; reuse an applicable passing review. Use
   `lean-statement-audit` when available; otherwise have one reviewer who did not
   author the declaration compare the exact source, elaborated statement, and
   relevant definitions using this skill's fidelity rules. Claims relying on
   unresolved source ambiguity or missing semantic justification cannot pass;
   work to establish a missing bridge can proceed after review of its own target.
   No additional installation or user approval is required beyond existing
   project rules.
4. Write a proof or a genuinely reusable helper. Conditional helpers are useful;
   their hypotheses must be discharged when proving the advertised result.
   A helper assuming an unfinished estimate is not a proof of that estimate.
5. During iteration, compile the narrowest useful target with the project's build
   wrapper if provided. Once edits to exported types, definitions, imports,
   instances, attributes, or visibility stabilize, validate affected consumers
   before integration or completion. Select the smallest existing target covering
   the advertised result and those consumers; broaden if coverage is uncertain
   and retain repository-mandated checks. Use the approved scratch area for
   probes and remove temporary files after recording useful evidence.
6. Inspect the diff, resolve relevant warnings, and report the proved export,
   validation, and remaining mathematical obligations. In a paper-companion
   project, update coverage at a coherent milestone, not after every helper edit.

Reuse search results and diagnostics. If repeated attempts reach the same
obstruction without new evidence, change route or isolate the missing lemma.
If still blocked after investigating viable alternatives, record the exact goal,
attempted approaches, and missing input or mathematics without weakening the target.
No fixed retry count is needed. Finish when the scope is verified, an applicable
resource limit is reached, or no useful authorized work remains; report results,
evidence, and unresolved obligations.

Prefer nearby Mathlib naming and proof style. Use explicit intermediate facts
where they clarify the argument; keep successful concise automation when it is
readable and affordable. Replace exploratory search tactics with their found
proofs before landing. Do not mechanically rewrite every `simp` or `nlinarith`.

## Cover the paper while allowing better proofs

Prioritize proving every main result and the dependencies needed to establish
it, while retaining all other in-scope claims as completion obligations.

Within the declared scope, aim to formalize every theorem, proposition, lemma,
corollary, and substantive mathematical claim. Each needs a proved Lean
statement with the same mathematical content, or a checked specialization of a
proved, more general statement. Track this in the project's existing equivalent
coverage record or `FORMALIZATION_REPORT.md`, updated at coherent milestones.
An isolated lemma task does not require a new paper-wide inventory; update an
existing applicable record and report substantive source departures as needed.

Proof details may differ: suitable library results, equivalent representations,
extra helpers, local arguments, and routine reordering are allowed. Prefer the
paper's main strategy and novel ideas. Record only substantive departures,
corrections, or changed coverage in the report; put useful exposition advice in
`MANUSCRIPT_RECOMMENDATIONS.md`, which may remain empty. A different proof does
not silently validate or repair a manuscript argument that it bypasses.

## Preserve the mathematical target

Keep the source carriers, boundary cases, normalization, and quantifier order.
In particular, a uniform constant must not acquire dependence on a parameter
through reordered binders. Audit bundled assumptions as carefully as explicit
hypotheses. Proving a convenient specialization is progress toward a target,
not completion of the original target.

Definitions must have their claimed meaning on the domain actually used. An
existing totalized Mathlib definition or a classical choice can be legitimate;
check its side conditions and characterization instead of banning its syntax.
Do not invent a default value or opaque assumption bundle to bypass missing
mathematics. Keep experimental encodings visibly provisional until justified.

Never introduce a custom axiom or an unapproved proof hole. A Comparator Challenge
hole is a separate, explicitly governed statement artifact, not a development
shortcut. Do not import a Challenge or quarantined draft into proof code.

## Build and kernel discipline

Work intended for publication targets Palomar-compatible artifacts by default,
including GitHub-only publication. Preserve established versions and proof policy;
report conflicts before changing them. This does not require publication checks
for an ordinary local proof task or full Palomar preflight without a request.
Before publication-sensitive interface or dependency choices, consult current
artifact requirements through `lean-publication` or the
[official submission standard](https://github.com/PalomarRegistry/PalomarPolicy/blob/main/CONTRIBUTING.md).
Use `lean-project-architecture` when design work is needed.

- Preserve the pinned Lean/Mathlib versions. Do not run `lake clean`, remove
  dependency artifacts, or update pins as a debugging shortcut.
- Respect shared build limits; do not kill another session's processes or
  overwrite its work. A focused target may rebuild upstream project modules;
  preserve installed dependency artifacts according to repository policy.
- Use `module` and the pinned toolchain's visibility conventions for publication
  source files. Keep proof implementations out of the Challenge import closure.
- Follow the project's trust policy for computational proof methods and inspect
  their actual transitive axiom closures in the pinned toolchain. For publication
  targets, reject native-evaluation axioms, including any introduced by
  `native_decide` or `bv_decide`. Keep generated kernel terms reasonably small.
- After a coherent group of edits, compile the relevant module and batch related
  `#print axioms Namespace.theorem` queries in one temporary probe. An earlier
  verification claim still requires current evidence. Ensure imports are current
  through the project wrapper or a supported dependency-aware Lake command.
  Palomar solutions allow only `propext`, `Classical.choice`, and `Quot.sound`.

Reuse actual check outputs only when the checked source, including proof bodies,
dependencies, toolchain, configuration, and targets are clearly unchanged. A
matching commit, unchanged signature, or worker summary is insufficient. If
unsure, rerun the focused incremental check; do not add a separate evidence
cache. Required fresh checks and independent source review still apply.

An axiom report checks dependencies, not source fidelity or independent kernel
replay. For a main theorem, changed mathematical interface, or paper-coverage
milestone, use `lean-statement-audit` if available, scoped to changed results and
affected dependencies. Reuse the checked paper inventory between milestones;
scan the whole declared scope for omissions when the source or scope changes and
before whole-paper completion. An isolated theorem review stays local. For routine
helpers, a focused check is enough unless the repository requires more.
Independent review is required at the early statement checkpoint; ordinary
helpers do not acquire a separate review requirement. No manifest, dependency
database, or status ledger is introduced.
