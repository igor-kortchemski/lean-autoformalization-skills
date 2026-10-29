---
name: lean-statement-audit
description: Check that Lean declarations faithfully cover claimed paper results and that their proof evidence supports the claim. Use for source coverage, interface approval, semantic changes, main-result completion, or publication review; not for every helper lemma.
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

## Check the proof evidence

Compile the exact targets and inspect `#print axioms` through a temporary probe
with current imports, batching related queries after coherent edits. An earlier
verification claim still needs current evidence.

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
Palomar solutions, only `propext`, `Classical.choice`, and `Quot.sound` may
appear in the axiom closure; GitHub-only publication follows the project's
permitted-axiom policy. Never widen that policy merely to pass a check. Inspect
relevant definitions as well as headline theorems. A text search alone cannot
establish this closure.

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

For Palomar, also inspect the current full mechanical report, checking its
repository, commit, paths, compared declarations, and mandatory kernel results.
A local build, axiom list, or standalone Comparator success is not the complete
deposit check.

## Give a proportionate verdict

Separate statement fidelity, scope coverage, proof-route correspondence, proof
completion, Lean checks, Comparator evidence, and Palomar verification. Give
concrete findings with source/code locations and missing evidence. Do not
manufacture a passing verdict from a completed table.

For main-result completion and final deposit, prefer a reviewer who did not write
the declaration. Qualifying reused independent review components may satisfy
the corresponding review obligations under the criteria above. Self-review does
not replace an available or required independent review. If none is available,
label the review as self-review. Do not demand independent reviewers for every helper.
