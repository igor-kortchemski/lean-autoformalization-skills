---
name: lean-book
description: Set up and steer the formalization of a textbook, monograph, or lecture notes, usually by other authors, as a reusable Lean library with an explicit book-to-code correspondence. Covers the project rules to settle first (source handling, rights, provider authorization, scope, precedence over the paper defaults), the item inventory and stable IDs, correspondence records, the book's errata register, chapter campaigns, coverage claims, and the reading companion. Use when starting or scoping a book project, maintaining its inventory or records, reporting its coverage, or building its companion; individual proofs use lean-workflow.
license: CC-BY-4.0
---

# Formalize a book as a library

The book supplies the roadmap, Mathlib shapes the reusable API, and a companion
exposes the correspondence. The output is a library organized by mathematical
concepts and dependencies, not by book numbering, together with a stable,
honest map from the book's items to Lean declarations. A theorem already in
Mathlib is a successful reuse, not something to reprove. The target is a
reusable library, not a pedagogical companion that follows the text and leaves
exercises as `sorry`, as Tao's *Analysis I* companion does; such a project needs
different coverage settings.

Use this skill with `lean-library` for the library's design and checks,
`lean-workflow` for proofs, `lean-statement-audit` for fidelity reviews,
`lean-orchestrator` for campaigns, and `lean-publication` for releases. Read the
project's instructions and existing decisions first; record a consequential
unresolved choice and continue independent work. Never decide publication
rights, trust-policy exceptions, or changes to the mathematical target alone.

## Settle the project rules before Lean work

Write these rules into the project's `AGENTS.md`, starting from
[assets/AGENTS-book.md](assets/AGENTS-book.md), with a `CLAUDE.md` that imports
it (`@AGENTS.md`). Keep the core short: Codex reads only `AGENTS.md`, and the
coordinator repeats its rules in every worker brief. Move long material into
topic files that the core links to.

1. **Source.** The edition, the PDF that is the authority, and any converted
   text, which is working material only. Machine transcription silently "fixes"
   printed typos and moves inline material; check uncertain formulas,
   quantifiers, and labels against the page image. A locator gives the printed
   page and the physical PDF page as separate fields.
2. **Rights and providers.** The book's text is the publisher's. Keep the PDF,
   converted text, and page images out of version history and out of every
   published output (HTML, search indexes, exports, logs). Write the
   `.gitignore` before `git init`, and confirm with `git status --ignored`
   before the first commit: ignoring a file later does not remove a committed
   copy. Git worktrees lack ignored files, so local worker briefs give the
   source by absolute path; a VM worker receives only the passages packaged for
   it. Record in `AGENTS.md` exactly what book material may be sent to which
   model provider, for what purpose. Codex and VM workers, and any audit the
   orchestration profile routes to them, receive source passages; if the rule
   forbids that, name the fallback (Claude reviewers only, or briefs without
   the book's text). Installing the skills authorizes nothing, and without the
   rule the coordinator asks.
3. **Scope.** Which categories count toward coverage. A usual default:
   numbered theorems, lemmas, propositions, and corollaries of the chapters are
   in scope; unnumbered definitions and conventions are recorded when a target
   needs them; exercises are recorded on demand, outside the headline
   denominator; appendices count when a chapter target depends on them; remarks
   and footnotes count when they carry a claim used later.
4. **Precedence over the paper defaults.** The other skills assume a paper by
   the user. State that, for this project: there is no publication-status
   question; errors in the book go to the book's errata register (below), not
   to `ERRATUM.tex` or `MANUSCRIPT_CORRECTIONS.md`; the correspondence catalog
   is the coverage record, so no `FORMALIZATION_REPORT.md` is created; and
   campaigns cover one chapter or section.
5. **Toolchain and library.** Lean and Mathlib pins, the namespace rule, the
   license of original code (Apache-2.0, as Mathlib), the installed skill tag,
   and the repository check `python3 scripts/check.py`.

When publication approaches, settle its target, Palomar compatibility,
Challenge/Solution pairs and Comparator, Mathlib bump frequency, the license of
original prose, and the human reviewers.

Initialize the repository with the source material ignored before any Lean
work; the rules above rely on revisions, worktrees, and clean-checkout CI.

## Inventory the book without a setup bottleneck

Use stable, edition-qualified IDs that do not depend on file names or line
numbers. Check the book's numbering first: when theorems, lemmas, and
corollaries share one counter per chapter, `book-3e-4.22` with a separate
`kind` field is safer than an ID that repeats the kind. Fix the forms for
exercises (`book-3e-ex-4.16`), numbered equations, appendix items, and
unnumbered definitions (`book-3e-ch4-def-independence`); parts are listed
inside the record. Never invent a printed number.

Seed the inventory from any existing extraction or review ledger, and mark each
region's enumeration `extracted` until it has been compared with the source,
then `source_checked`. Reconcile counts from different extractions before using
one as a denominator. Inventory the pilot section first and expand
progressively: a complete catalogue is not a prerequisite for useful
formalization, but a partial inventory never supplies a whole-book percentage.

Split multipart results into recorded parts; the parent counts once, and as
fully covered only when every required part is. One general theorem may cover
several items, and one item may need several declarations.

## Keep correspondence records small and authoritative

Keep one record per inventoried item: identity, source locator, parts,
formalizations with a list of fully qualified `decls` and relations, a note,
and one human review. Generate resolution, validation, and origin; campaign
state stays in the orchestrator. The user's freeze is the statement review; an
independent agent review delegated by the user goes in the note. See
[references/correspondence.md](references/correspondence.md) for the schema and
coverage standards.

## Read the book's errors before specifying a statement

Keep one errata register for the book: an existing review ledger, or a file
built from `lean-workflow`'s
[cited-works template](../lean-workflow/assets/CITED_WORKS_ERRATA.md). Like
that template, it is written for the user: keep it in a git-ignored location
unless `AGENTS.md` records a decision to publish it. Before writing a
statement, read the item's entry.

- An entry stays suspected until an independent audit confirms it, at the bar
  `lean-statement-audit` sets for cited works: the book's own conventions and
  standing assumptions, a search for a published erratum or later edition, and
  a counterexample or corrected statement checked in Lean or by hand.
- A corrected statement is a separate formalization of the item, marked
  `variant: corrected` and citing the entry. Never describe it as a proof of
  the printed statement, and count corrected-source coverage separately.
- A printed statement whose entry is confirmed and whose counterexample is
  proved in Lean has the relation `refuted`, a deliverable in its own right.
- The register is for the user. Nothing is sent to the author or the
  publisher. If the user is an author of the book, draft an erratum from
  `lean-workflow`'s `ERRATUM.tex` only at the user's request.

## Specify statements with the book's conventions

Read the complete claim and the conventions inherited from its section and
chapter, not only the theorem environment. Inspect the elaborated statement and
the definitions behind its notation, using
[references/source-checks.md](references/source-checks.md). Do not add a
hypothesis that supplies the conclusion, make a theorem vacuous with
incompatible assumptions, or weaken a conclusion to get a proof. A necessary
restriction becomes a recorded `special_case` or `partial`. Give a consequential
new definition or translation a small sanity example; it catches mistakes but
does not replace a fidelity review.

Keep a short terminology guide from the book's terms to Mathlib's names, each
entry checked against the pinned declaration (for example, a book's "Borel
space" against the typeclass assumptions of the Mathlib result used).

## Organize the code as a library

Follow `lean-library`. Reusable modules follow mathematical dependencies; the
book order never forces the import graph. Book-facing bridges live in their own
layer inside the library's folder, for example `Lib/Book/`, so the build, the
axiom audit, and the documentation linter cover them; they may import the rest
of the library, never the reverse. Public names are mathematical names. Give
the book an entry in `docs/references.bib` and cite it in docstrings as Mathlib
does, in one greppable form such as `[Author2021], Lemma 4.22`; doc-gen4
links these citations to the bibliography. Do not create a custom attribute.
When a general result differs from the book's presentation, add a thin
book-facing corollary instead of duplicating definitions or proofs to follow
the book's order. Prove nontrivial bridges; a definitional identification can
be documented without a redundant theorem.

## Run the book chapter by chapter

Start with one pilot section, preferably one with an existing Mathlib result
and a small bridge. Deliver its source-checked inventory, declarations or
mappings, and a catalog validated by `python3 scripts/check.py --names FILE`.
The companion page and outside-consumer example come at the first public
milestone. The pilot needs no whole-book inventory, custom website, or live
Lean server, and human review may remain pending if it says so. Avoid a pilot
that another project is already formalizing from the same book.

Then run campaigns with `lean-orchestrator`, each limited to one declared
chapter or section: its inventory, dependency graph, frozen statements, and
close cover that region only. While frozen statements still have registered
holes, the repository check runs with `--allow-sorry` on the campaign branch
(`lean-library`). Prioritize infrastructure that unlocks several in-scope
items, without replacing the assigned target by an easier one. One integrator
owns the catalog, root imports, manifests, and shared documentation. Reviewers
receive the source claim and the actual declarations, not only the
implementer's summary.

## Claim coverage honestly

Report formally checked full-coverage candidates separately from
human-approved full correspondences, as defined in
[references/correspondence.md](references/correspondence.md#coverage-claims);
an unqualified "fully covered" means the second. Every percentage names its
category, denominator, review threshold, and commit. Definitions are
not proved theorems. Covering a statement is distinct from reproducing the
book's argument: an alternative proof or a Mathlib specialization is acceptable
and is identified. A theorem count measures neither difficulty nor effort.

In the README's status words (`lean-library`), *available* means a formally
checked full-coverage candidate, *in progress* means active or partial work,
and *planned* means recorded but not started; *fully covered* is reserved for
human-approved correspondences.

## Publish the reading companion

Follow [references/companion.md](references/companion.md): version 1 is
doc-gen4 API documentation in a nested project plus a table generated from the
catalog, in book order, linking to doc-gen4 anchors. The library builds without
the companion's toolchain. Never publish the book's text.

## Maintain through Mathlib bumps and upstreaming

A Mathlib bump is an owner decision, and during a campaign it needs the user's
approval and a new freeze record. At each bump, re-resolve every mapped
declaration, handle renames and deprecations in the records, and rerun the
affected checks. Keep IDs through refactors and upstreaming: a result moved
into Mathlib keeps its record with the new target and origin. Reassess
correspondence after a change to a statement, a translation, or a definition it
depends on; unchanged pretty-printed text does not guarantee unchanged meaning.
A proof-only refactor keeps fidelity approval but needs its formal checks.

## Definition of done and handoff

An item may be *implementation done, review pending*; reserve *fully covered*
for the human-approved standard. Before claiming a status:

- source scope, inherited assumptions, parts, and errata entries identified;
- existing Mathlib results considered and credited;
- reusable API and required bridges in place;
- build, allowed-axiom, and `check.py --names` checks passed at the commit;
- relations and human review accurate, no missing part counted as complete;
- catalog record, documentation, and generated evidence updated;
- outside use, publication, and license checks complete or explicitly pending.

Hand off in this form, not as a second database:

```text
Scope: book IDs, modules, and assigned objective.
Delivered: declarations, bridges, record and documentation changes.
Coverage: relations, covered and missing parts, human review, errata entries.
Validation: commands, target scope, outcomes, revision and pins, reused evidence.
Reuse: required imports, a useful example, upstream considerations.
Remaining: precise mathematical gaps, review needs, infrastructure blockers.
```
