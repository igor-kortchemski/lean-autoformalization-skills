---
name: lean-statement-audit
description: Check that Lean declarations faithfully cover claimed paper results and that their proof evidence supports the claim. Use for early statement checks, source coverage, interface approval, semantic changes, main-result completion, publication review, or auditing claimed errors in the paper or in cited works before an erratum; not for every helper lemma.
license: CC-BY-4.0
---

# Review statements, coverage, and evidence

Identify the exact exports, source version and locations, declared scope,
relevant author rulings, and code revision. If a frozen manifest exists, verify
its identity using the project's checker before reviewing. Do not create a
manifest merely to conduct an audit. Keep the review read-only unless fixes were
requested.

Resolve routine choices and uncertainties from the source, project context, and
prior decisions, reusing existing authorization. Ask only for essential missing
information, decisions, or permission that block faithful completion; identify
the exact blocker and continue independent authorized checks. If the user
requests no questions, record and report the blocker, leave dependent work
pending, and do not guess the mathematics or authorization.

Review main results and their required dependencies first, while retaining all
other in-scope claims in the audit.

## Early statement checkpoint

Before moving from exploration to substantial proof work on a main source result,
or using a source-facing mathematical interface for substantial dependent work,
obtain a passing statement-fidelity review from a reviewer who did not author
the declaration. This applies to a sustained single-worker proof as well as
delegated work. Ordinary internal helpers need no separate checkpoint.

Use one independent reviewer by default. Give them the source version and exact
locations, the proposed Lean declaration, its relevant definitions, and any
existing applicable review. They should reconstruct the source meaning first,
then inspect the elaborated statement and its semantic dependencies using
“Compare the mathematics” below. Reuse current elaboration evidence or perform a
focused check, respecting the project's proof-hole rules. A passing review
establishes statement fidelity, not completion of the target's proof.

An unresolved source mismatch, ambiguity, or required characterization bridge
prevents a pass for claims relying on it. Work to establish that bridge may
proceed: independently review its own statement against the explicit source
obligation, without assuming its conclusion, then prove it. This also applies
when the bridge is itself a main result. Keep claims relying on the missing
identification pending until the bridge is proved. Resolve actionable findings
within existing authorization and return only affected parts for review.

Scope this early review to statement fidelity; leave target-proof, paper-coverage,
full-build, and Comparator checks at their existing milestones. Exploration
resolves uncertainty about the statement, encoding, or feasible proof route;
sustained implementation of the chosen route requires a pass. Searches and
independent work can continue while review is pending. If independent review is
unavailable, report that blocker once and keep affected work exploratory;
self-review does not pass this checkpoint. Use the existing clarification policy
for essential missing input.

Batch closely related statements and review shared definitions once. Reuse a
passing independent review when the source, elaborated statement, and semantic
dependencies are unchanged. Recheck affected parts after a change to those
inputs; proof-body-only changes follow the existing proof-correspondence rules.
Record the source and declaration reviewed, reviewer, verdict, and any findings
briefly in an existing project record or handoff. No new manifest, ledger, or
per-helper form is required. Proceed after a pass without another user approval,
unless the project already requires one.

## Compare the mathematics

Read the source statement independently of the implementation. Reconstruct its
premises, quantifiers, conclusion, and definitions. Then inspect the Lean
declaration and the project definitions that determine its meaning, including
notation, coercions, structures, and instance arguments.

Check especially:

- **Premises:** every logical assumption comes from the source, genuine standing
  assumptions, necessary typing, or an explicit author ruling. Expand bundles
  far enough to expose hidden estimates or existence assumptions.
- **Scope:** quantifier order preserves uniform constants and shared witnesses;
  a theorem split does not silently replace one witness with independent ones.
- **Meaning:** carriers, finite/infinite cases, normalization, signs, scaling,
  endpoint conditions, and coercions match the claim.
- **Definitions:** the exported object has the required characterization where
  the theorem uses it. A totalized library convention or non-unique choice is
  acceptable only when its side conditions and required invariance are justified.
- **Strength:** a specialization, conditional helper, or changed conclusion is
  described honestly and is not counted as the original source result.
- **Hidden content:** the conclusion is not carried by a hypothesis, a structure
  or class field, or a class with no genuine instance. Project definitions are
  not hollow: none ignores a parameter, replaces a condition by `True`, or is a
  `def` returning `Prop` that stands in for a theorem. An abstract proxy for a
  source quantity is connected to it by a proved theorem. A comment that
  justifies a deviation is not evidence that the deviation is acceptable.

When there is a concrete reason to suspect a mistranslation, check whether the
premises have become jointly contradictory. A witness must satisfy all premises;
a counterexample must also refute the exact conclusion. A short proof or proof
by contradiction alone is not evidence of vacuity. Compare any finding with the
source and report source contradictions without arbitrarily changing the target.
Failure to find a counterexample does not certify fidelity; no per-helper check
is required.

A theorem proved from an extra estimate is useful as a helper. To certify the
source result, find the proof that supplies that estimate and exports the exact
source type. If an encoding differs from the source, inspect its equivalence or
characterization theorem. Record unresolved ambiguities instead of certifying
them.

## Audit coverage and proof correspondence

Keep an isolated theorem review scoped to that theorem and its relevant
dependencies. For a broader paper review, initially inventory every theorem,
proposition, lemma, corollary, and substantive claim in the declared scope,
including claims in remarks, independently of the implementation; reuse an
already checked inventory when its source and scope are unchanged. Use the
existing coverage record or `FORMALIZATION_REPORT.md` and check entries against
exact proved declarations or verified specializations of more general ones.
Do not count conditional helpers, unproved bridges, or similar-looking theorems
as complete.

At intermediate milestones, review changed results and affected dependencies,
preserving individually valid entries. Repeat the whole-scope omission scan
when the source or declared scope changes and before claiming whole-paper
completion.

Check that substantive differences are recorded but routine Lean details are
not. An alternative proof may verify the result without checking the paper's
argument; a bypassed novel method, central construction, or manuscript gap must
be stated. Check that adopted routes preserve the requested mathematics,
complete declared coverage, and established project requirements; a different
route alone requires no approval. `MANUSCRIPT_RECOMMENDATIONS.md` is advisory,
but correctness issues that affect coverage also belong in the report.

## Audit corrections to the paper and errata to cited works

Before an error in the paper enters an erratum or `MANUSCRIPT_CORRECTIONS.md`,
have a reviewer who did not record it try to refute it. Claiming an error that
is not one does more harm than missing one. Read the source location in the
version the deliverable cites, and check:

- the notation, conventions and standing assumptions of the paper, including
  those stated in another section, a footnote or an earlier paper it relies on;
- whether the claimed counterexample satisfies every hypothesis of the paper's
  statement, as the paper means it, and violates its conclusion;
- whether the failing step is really used, or another argument in the paper
  covers it;
- that the Lean evidence formalizes the paper's statement and not a
  mistranslation, and is proved without `sorry` or unexpected axioms;
- that the correction is the smallest one that makes the claim true, and that
  its stated effect on the main results is right;
- that an imprecision or a formalization choice has not been recorded as an
  error.

Give a verdict per entry: confirmed, reclassified, or withdrawn, with the
reason. Only confirmed entries go into the deliverable.

For an entry of `CITED_WORKS_ERRATA.md`, an error in a work the paper cites, the
bar is higher: it says that other authors are wrong. Apply the checks above to
that work, read in the version the entry names, and also check:

- the cited work's own conventions, normalizations and standing assumptions,
  which may differ from the paper's (a sign, an orientation, a parametrization);
- that the work states the claim in the form recorded, and that a misreading or
  a wrong citation by the paper is not being attributed to the work;
- whether a published erratum, a later version or the later literature already
  corrects it, and that the entry says what was searched;
- that the evidence is a counterexample or a corrected version proved in Lean,
  or a refutation that you checked yourself against the version read.

Without such evidence the entry stays suspected; give the same verdicts
otherwise, and check the entry's stated effect on the paper formalized.

## Check the proof evidence

Compile the exact targets and inspect `#print axioms` through a temporary probe
with current imports, batching related queries after coherent edits. An earlier
verification claim still needs current evidence.

A successful Lean Beam probe, an empty goal list (a probe running `sorry`
leaves none either) or a "save ready" status (which tolerates `sorry`) is
development feedback, not proof evidence: base the verdict on the compiled
targets and the axiom check.

Reuse mechanical outputs only when source, proof bodies, dependencies,
toolchain, configuration, and targets are clearly unchanged. Do not treat a
summary as a source audit. Reuse statement-fidelity findings when the source,
elaborated statement, and semantic dependencies are unchanged; proof-correspondence
findings also depend on the proof route and relevant implementation dependencies.
After proof changes, check whether that correspondence changed and refresh the
affected findings, preserving the rest. A tactic-only refactoring need not cause
a full source audit. Preserve findings, including unresolved issues, and review
status; honor required fresh review, and never turn self-review into independent
review through reuse. Rerun focused checks or review when uncertain.

An independently reconstructed exact-type `example` can catch binder or
elaboration surprises; use it when useful or required, without a proof hole. For
publication targets, including GitHub-only artifacts, only `propext`,
`Classical.choice`, and `Quot.sound` may appear in the axiom closure, subject to
any stricter project policy. Report incompatibilities with established policy
before changing it; never widen it merely to pass a check. Inspect
relevant definitions as well as headline theorems. A text search alone cannot
establish this closure.

Trace the advertised proof through its project-local dependencies. A
substantial-looking lemma it does not use proves nothing for it; a `sorry`,
`admit` or axiom moved or renamed into a helper still counts; `exfalso`,
`False.elim` or `Subsingleton.elim` producing the main result calls for the
vacuity check above.

Respect frozen-file and Challenge exceptions precisely. An allowed draft hole
can coexist with a faithful statement, but its export is still unproved. Never
use a draft to certify a dependency or weaken a frozen statement to close it.

For publication of named mathematical results, inspect the Challenge/Solution
pair and Comparator evidence by default, including small or one-theorem GitHub-only
projects. Check that the exact candidate revision, comparison paths and configuration,
and compared declarations cover the advertised exports and their transitive semantic
definitions. Review the Challenge against the mathematical source independently of
the proof; two matching interfaces can share the same source error. Preserve the
scoped review and evidence-reuse criteria above, without per-helper comparison work.

For a requested full Palomar verification or submission, also inspect the current
full mechanical report, checking its repository, commit, paths, compared
declarations, and mandatory kernel results. Artifact preparation alone may leave
this check unrun and must report that limitation.
A local build, axiom list, or standalone Comparator success is not the complete
deposit check.

## Give a proportionate verdict

Separate statement fidelity, scope coverage, proof-route correspondence, proof
completion, Lean checks, Comparator evidence, and Palomar verification. Never let one compensate
another: a sorry-free proof of an unfaithful statement fails. Give
concrete findings with source/code locations and missing evidence. Do not
manufacture a passing verdict from a completed table.

For main-result completion and final deposit, prefer a reviewer who did not write
the declaration. Qualifying reused independent review components may satisfy
the corresponding review obligations under the criteria above. Self-review does
not replace an available or required independent review. If none is available,
label the review as self-review. Labelled self-review does not satisfy the early
statement checkpoint. Do not demand independent reviewers for every helper.
