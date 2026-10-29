# Formalization report

## Purpose and scope

This report records coverage of the mathematical results in the accompanying
paper and substantive differences between the written and formal arguments. It
is a completion artifact for a paper-companion formalization, not a log of every
Lean edit.

- **Paper and version:** [title, version, date or commit]
- **Declared formalization scope:** [whole paper or explicit exclusions]
- **Lean repository and revision:** [repository and commit/tag]
- **Lean/Mathlib versions:** [versions]

Within the declared scope, aim to cover every theorem, proposition, lemma,
corollary, and other substantive mathematical claim. Conjectures, questions,
and purely expository remarks should be identified rather than presented as
proved results.

Prioritize proving every main result and its required dependencies, while
retaining all other in-scope claims as completion obligations. Clearly identify
any main result that remains unproved.

A paper result is covered only by a proved Lean declaration with the same
mathematical content, or by a checked specialization of a proved, more general
declaration. A conditional helper, nearby theorem, or matching name is not by
itself coverage.

## Result correspondence

Replace the placeholder row with actual results and checked status.

| ID | Paper result | Source location | Lean declaration | Coverage | Proof correspondence | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| [ID] | [Result] | [Section/page] | [Declaration, if present] | [Actual status] | [Checked correspondence] | [Notes] |

Suggested **Coverage** values: `Complete`, `Partial`, `Blocked`, `Out of scope`,
`Conjecture/question`. Suggested **Proof correspondence** values: `Same main
strategy`, `Local adaptation`, `Alternative proof`, `Generalized in Lean`, or a
short precise description.

Update this table at coherent milestones, not after every helper lemma. If one
Lean theorem covers several paper results, list each paper result separately and
state the specialization or implication that was checked.

## Substantive differences

Record differences that change what part of the paper's mathematics is being
checked or how a reader should understand the correspondence. Do not record
routine formal implementation details.

### D1 — [Short title]

- **Paper:** [statement, construction, or proof route]
- **Formalization:** [what Lean proves or how it proves it]
- **Reason:** [library reuse, simpler route, correction, stronger result, etc.]
- **Mathematical effect:** [none / stronger result / changed hypothesis /
  different proof route / correction]
- **Paper argument checked:** [yes / partly / no, with explanation]
- **Manuscript action:** [none / explanatory note / revision required /
  recommendation recorded]
- **Unresolved obstruction, if any:** [issue and supporting evidence]

Record, in particular:

- a genuinely different argument;
- replacement of a central construction by an equivalent one;
- a theorem strengthened, generalized, specialized, or given different
  hypotheses in Lean;
- a paper lemma bypassed by a stronger library theorem;
- a missing assumption, boundary case, or dependence of constants discovered
  during formalization;
- a written proof step that required correction.

Do not record tactic choices, added helper lemmas, routine algebraic reordering,
namespace or file organization, standard automation, or the splitting of one
written calculation into several Lean statements.

A different Lean proof can verify the result without verifying the written
argument it bypasses. In particular, an alternative proof does not silently
repair a gap in the manuscript; record the gap and the required manuscript
action explicitly.

## Unresolved coverage or correspondence obligations

Record precise obstructions that remain after investigating available evidence
and viable alternatives, including unresolved source ambiguities or unavailable
authorization. Include the supporting evidence and the next step needed to
resolve each obligation, preserving the claimed mathematics and scope.
