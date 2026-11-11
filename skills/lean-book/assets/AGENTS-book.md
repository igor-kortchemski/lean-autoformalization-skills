# <Short book title> in Lean: project rules

These rules are shared by Claude Code, through `CLAUDE.md` (`@AGENTS.md`), and
by Codex workers, which read only this file. Worker briefs repeat the rules a
task depends on. Replace every `<…>` and delete what does not apply.

## Skills and precedence

Skills: `lean-autoformalization-skills`, tag `<vX.Y.Z>`,
installed in `.agents/skills/` (Claude Code reads them through
`.claude/skills/`). Do not patch the installed copies; update only to a later
tag, then re-read this section. Start book work with `lean-book`, proofs with
`lean-workflow`, and library design with `lean-library`.

For this project, these rules override the skills' paper defaults:

- The book is by `<authors>`, not by the user: no publication-status question.
- Errors in the book go to `<errata register path>`, kept git-ignored and
  private `<unless publishing it was decided on …>`. No `ERRATUM.tex` or
  `MANUSCRIPT_CORRECTIONS.md`; nothing is sent to the authors or the publisher.
- The coverage record is `<catalog path>`; no `FORMALIZATION_REPORT.md`.
- A campaign covers one declared chapter or section.

When publication approaches, settle its target, Palomar compatibility,
Challenge/Solution pairs and Comparator, Mathlib bump frequency, the license of
original prose, and the human reviewers.

## Source

- Book: `<authors, title, edition, year>`.
- Authority: `<absolute path of the PDF>` (git-ignored); SHA-256: `<hash>`.
- Working text: `<absolute path of the converted text>` (git-ignored; it may
  differ silently from the print).
- Locators give the printed page and the PDF page as separate fields.
- Read the item's errata entry before specifying its statement.

## Provider authorization

`<What book material may be sent to which provider (OpenAI through Codex
workers, Open Math OS, the Open Math OS VM), and for what purpose; or: none
without asking the user.>` Workers and any audit routed to them receive source
passages; where this section forbids it, `<the fallback: Claude reviewers only,
or briefs without the book's text>`.

## Scope

| Category | Counted toward coverage |
| --- | --- |
| Numbered theorems, lemmas, propositions, corollaries | `<yes>` |
| Unnumbered definitions and conventions | `<recorded when a target needs them>` |
| Exercises | `<on demand, outside the headline denominator>` |
| Appendices | `<when a chapter target depends on them>` |
| Remarks and footnotes | `<when they carry a claim used later>` |

## Rules

1. Search the pinned Mathlib and this repository before defining anything.
2. Library modules have no `sorry`, no added axiom, and no native evaluation,
   except the registered holes of frozen statements during a campaign (checked
   with `scripts/check.py --allow-sorry` on the campaign branch only). Drafts
   live in `<draft library>`, outside the library's folder.
3. Before substantial proof work on a book item, obtain the user's freeze of
   the statement, or an independent agent review recorded in `note` when the
   user delegates it. Agents never supply human approval; the later human
   correspondence review remains separate.
4. Never count a corrected, special-case, or partial statement as the printed
   item.
5. Update the item's record; never hand-edit generated fields.
6. Never commit or publish the book's PDF, converted text, or page images.
7. No pull request, post, or publication without the user's request.

## Environment

- Lean `<version>`, Mathlib `<full commit>`.
- Namespaces: `<rule, for example topic namespaces for reusable results and
  a book namespace for book-facing corollaries>`.
- Repository check: `python3 scripts/check.py`.
- Code license: `<Apache-2.0>`.
