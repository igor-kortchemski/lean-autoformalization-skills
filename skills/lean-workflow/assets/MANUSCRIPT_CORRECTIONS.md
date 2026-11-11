# Corrections to the manuscript

Draft list of errors that formalization found in a paper on arXiv only or
submitted, for the next version or the revision. It is written for the authors,
not published: it takes effect only once they approve it. For a paper published
in a journal, write the erratum from the `ERRATUM.tex` template next to this
one instead. Copy this template to the project root to use it.

- **Paper:** [title, authors]
- **Version formalized:** [arXiv identifier and version, or submitted version]
- **Formalization:** [repository and revision]
- **Status:** [draft / audited / approved by the authors]

Keep each entry brief. List only errors in the paper, as classified in the
formalization report: a false or overstated claim, a missing hypothesis, a
proof step that does not follow, a wrong constant, exponent or case. Leave
imprecisions and exposition to `MANUSCRIPT_RECOMMENDATIONS.md`, and do not
list differences that only reflect the formal proof. A wrong citation by the
paper belongs here; an error in the cited work itself goes to
`CITED_WORKS_ERRATA.md`. If formalization found no error, create no file: say so
in the formalization report.

## C1 — [Result or section, short title]

- **Location:** [result number, section, page and line in the version formalized]
- **Problem:** [what is wrong, in one sentence]
- **Correction:** [the corrected statement or step, as the paper should read]
- **Reason:** [a counterexample, or the step that fails and why]
- **Effect:** [none on the main results / the main results stand as corrected /
  [result] is weakened to ...]
- **Evidence:** [report entry D… and Lean declaration]
- **Audit:** [independent audit result and date]

Write formulas with `$...$` inline, and with each `$$` of a displayed formula on
its own line, preceded and followed by a blank line.
