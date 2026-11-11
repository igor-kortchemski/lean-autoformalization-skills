# Correspondence records and coverage claims

A book project keeps one small record per inventoried item. This page gives a
proposed schema, its vocabularies, and the rules for aggregate claims. Reuse
suitable existing metadata rather than imposing this exact layout.

## A record

```yaml
id: author-3e-4.22
kind: lemma
source:
  reference: author2021
  edition: 3
  item: "4.22"
  printed_page: null      # fill from the source; never guess
  pdf_page: null
parts: []                 # e.g. ["(i)", "(ii)"]; empty for one claim
formalizations:
  - variant: printed
    decls:
      - MyLib.Book.lemma_4_22
    relation: unassessed # or {"(i)": equivalent, "(ii)": partial}
human_review: {by: null, commit: null}
note: >
  Candidate from a module docstring that cites this lemma. Check
  the statement, assumptions, and conventions against the source and the
  pinned declaration. No resolution, build, or approval is asserted here.
```

This example is illustrative, not a completed audit.

`decls` is a list of fully qualified names, including required bridges. Give a
relation per part where needed, using the recorded part identifiers. A
corrected formalization uses `variant: corrected` with `errata: C4-05` beside
that variant, never `errata:` on the item. Keep a short explanation in `note`,
including who set or confirmed each relation; campaign state belongs to the
orchestrator.

`human_review` remains null until a named human approves the correspondence at
`commit`. The user's freeze of a statement is its human statement review, not
approval of a bridge or relation proved afterwards. Agents never supply human
approval, and agreement between agents is never human approval. A human may
review a batch at section close, recording the items and commit covered.

Name resolution, validation (sorry-free and allowed axioms), origin (dependency
or project), and displayed counts are generated, never hand-edited. Run
`python3 scripts/check.py --names FILE` at a recorded commit, where `FILE`
contains one fully qualified declaration name per line extracted from the
catalog. The check reports names that do not resolve and names whose axiom
closure contains `sorryAx`; the repository check enforces the allowed-axiom
policy. Never copy a passing status from an older commit.

## Relations

| Relation | Meaning |
| --- | --- |
| `equivalent` | The full scope is preserved under an explained translation of objects and conventions; both directions and the definitions are checked |
| `generalization` | The formal result recovers the whole book claim by a proved specialization or bridge |
| `special_case` | Extra restrictions or a narrower domain remain |
| `partial` | A direction, conclusion, case, or other required part is missing |
| `refuted` | The printed statement is false: its errata entry is confirmed and a counterexample is proved in Lean |
| `unassessed` | The correspondence has not been established |

When `special_case` and `partial` both apply, record `partial` and list the
restriction of each part. Similar wording, a theorem name, or a citation is
not a correspondence. For a generalization, give the recovery of the book
claim.

## Coverage claims

- A **formally checked full-coverage candidate** has an `equivalent` or
  `generalization` relation for the printed variant and every required part,
  every listed declaration resolves with no `sorryAx` in its axiom closure
  according to `check.py --names` at a recorded commit, and the relation was
  confirmed by an agent that did not write the declarations, as the note
  records.
- A **human-approved full correspondence** adds the named human review. It is
  the meaning of an unqualified "fully covered".
- Every percentage names its category, its denominator (from a
  `source_checked` inventory of the claimed region), its review threshold, and
  its commit. Partial items, corrected-source coverage, and refuted items are
  each reported on their own line, never as fractions of theorems or as
  covered.

For public milestones, generate a machine-readable export of the records,
generated facts, and check commit through documented interfaces; do not make
unstable internal formats a permanent contract.
