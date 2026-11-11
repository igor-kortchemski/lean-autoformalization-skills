# Formalization report

## Purpose and scope

This report records coverage of the mathematical results in the accompanying
paper and substantive differences between the written and formal arguments. It
is a completion artifact for a paper-companion formalization, not a log of every
Lean edit.

- **Paper and version:** [title, version, date or commit; SHA-256 of the
  exact PDF or source files read, and how they correspond when both are used]
- **Publication status:** [published in a journal: reference, DOI, and the
  published version used for locations / arXiv only or submitted: version /
  not distributed], as answered by the author at the start
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
- **Classification:** [error in the paper / imprecision / formalization choice]
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

Classify each difference when you record it:

- **Error in the paper:** a statement that is false or stronger than what is
  proved, a missing hypothesis without which a claim fails, a proof step that
  does not follow, or a wrong constant, exponent or case. Each needs a reason a
  reader can check: a counterexample, or the step that fails and why.
- **Imprecision:** the intended mathematics is right, but a convention,
  quantifier, domain or boundary case is left unclear or inconsistent.
- **Formalization choice:** a different route, representation or library
  result, or a change made only for Lean's convenience.

Only errors in the paper go into the corrections deliverable chosen by the
publication status: an erratum in PDF for a published paper, or
`MANUSCRIPT_CORRECTIONS.md` for a paper on arXiv only or submitted, from the
templates in `lean-workflow/assets/`.
Imprecisions go to `MANUSCRIPT_RECOMMENDATIONS.md`.

An error found in a work the paper cites or relies on is not a difference of
the paper: record it, whatever the publication status, in
`CITED_WORKS_ERRATA.md` (template in `lean-workflow/assets/`), as suspected until
an independent audit confirms it. When the paper relies on the false claim,
also record the affected step here as an error in the paper. At the close, give
the register's outcome here: the confirmed and suspected entries, or that no
error was confirmed in a cited work within the reviewed scope.

## Corrections to the paper

State the outcome with its scope: "no confirmed mathematical error was found
within the reviewed scope at this revision", or the confirmed errors (by their
difference IDs) and, if one exists, a link to the published erratum. Drafts and
correspondence with authors stay private, and whether to mention them is the
author's choice; it never removes a difference that a reader needs to
understand an advertised result.

## Verification and assumptions

Give this once per checked scope, not per theorem. Mark each item `passed`,
`failed`, `not run`, `not applicable` or `superseded`, with the date and the
path or link of its retained output; a branch badge does not verify a release
commit.

- **Checked revision:** [commit or release tag; toolchain; dependencies as
  pinned]
- **Build:** [command, targets, outcome]
- **Axioms:** [the `#print axioms` output of the advertised exports]
- **Semantic dependencies:** [the definitions the main statements rest on,
  with any convention that differs from the paper]
- **Statement preservation:** [approval of the main statements (date, who
  approved, by delegation if so), the frozen declarations, the outcome of the
  freeze check on this revision, and whether outsiders can replay it]
- **Source-fidelity review:** [scope, reviewer, outcome]
- **Comparator:** [configuration, compared declarations, outcome]
- **Kernel replay and full deposit verification:** [where applicable]

Building and kernel checking show that the Lean statements are proved from the
listed axioms; they do not show that the statements say what the paper says,
and a Challenge and a Solution can share a misreading of the paper.

## How the formalization was produced

A short paragraph: the human decisions (statement approvals, rulings on
ambiguities, decisions on corrections), the roles of the models (proof,
research, audit, read-back) with their confirmed settings where known, and
material repair or integration work. Keep it consistent with the credits and
any registry metadata; no transcripts.

A different Lean proof can verify the result without verifying the written
argument it bypasses. In particular, an alternative proof does not silently
repair a gap in the manuscript; record the gap and the required manuscript
action explicitly.

## Unresolved coverage or correspondence obligations

Record precise obstructions that remain after investigating available evidence
and viable alternatives, including unresolved source ambiguities or unavailable
authorization. Include the supporting evidence and the next step needed to
resolve each obligation, preserving the claimed mathematics and scope.
