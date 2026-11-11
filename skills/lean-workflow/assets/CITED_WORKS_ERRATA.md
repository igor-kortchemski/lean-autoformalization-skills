# Errata to cited works

Register of errors that formalization found in the works the paper cites or
relies on: articles, preprints and books by other authors or by the user. Use
it in every paper formalization, whatever the publication status of the paper
formalized, creating the file at the first entry. It is written for the user,
not published: the skills never send it to the authors of a cited work, a
journal, an archive or a coauthor. Copy this
template to the project root to use it.

- **Paper formalized:** [title, version]
- **Formalization:** [repository and revision]

Record here only errors in the cited work itself: a false or overstated
statement, a missing hypothesis without which it fails, a proof step that does
not follow, a wrong constant, sign, exponent or case, or a wrong reference
inside that work. Elsewhere:

- a wrong citation by the paper formalized (wrong number, omitted hypothesis,
  wrong attribution) is an error in the paper and goes to its corrections
  deliverable;
- a difference of convention (sign, orientation, normalization) is a note for
  the formalizer in the report, not an error;
- when the paper formalized relies on a cited claim that is false as stated,
  record the error here and the affected step of the paper in its corrections
  deliverable (in the report for a paper not distributed), each entry pointing
  to the other.

An entry starts as **suspected**. It becomes **confirmed** only after an
independent reviewer has tried to refute it (see `lean-statement-audit`), on
evidence of one of these kinds: a counterexample or a corrected version proved
in Lean, or a refutation checked by that reviewer against the version read.
Paraphrase the printed claim; quote at most a short phrase. If formalization
found no error in a cited work, create no file: say so in the formalization
report.

## E1 — [Authors, short title: result, short description]

- **Work:** [authors, title, journal or book, year, DOI; arXiv identifier]
- **Version read:** [published version or arXiv version, as actually read]
- **Location:** [result number, section, page, equation in the version read]
- **Printed claim:** [what the work states, paraphrased]
- **Problem:** [what is wrong, in one sentence]
- **Correction:** [the smallest corrected statement or step]
- **Reason:** [a counterexample, or the step that fails and why]
- **Already known:** [published erratum or later version that corrects it /
  none found in: sources searched / not searched]
- **Effect on the paper formalized:** [none / the paper uses it in [result]:
  see corrections entry C…]
- **Evidence:** [report entry D… and Lean declaration]
- **Authors:** [include the user or a coauthor: an erratum to that work may be
  drafted at the user's request / other authors: note for the user]
- **Status:** [suspected / confirmed / reclassified / withdrawn, with the
  audit's date and reason]

Write formulas with `$...$` inline, and with each `$$` of a displayed formula on
its own line, preceded and followed by a blank line.
