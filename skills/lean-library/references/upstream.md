# Upstream routes: Mathlib and Tau Ceti

These policies were read on 8 November 2026. Re-read the current pages before
preparing a contribution or declaring compliance; they change. Compiling
against an upstream library or passing an audit does not guarantee acceptance.

## Mathlib

Policy: [contribution and AI use](https://mathlib.org/contribute/index.html),
[values](https://mathlib.org/contribute/values.html),
[naming](https://mathlib.org/contribute/naming.html),
[style](https://mathlib.org/contribute/style.html),
[documentation](https://mathlib.org/contribute/doc.html), and the
[PR review guide](https://mathlib.org/contribute/pr-review.html).

- A named human contributor must understand the definitions, proofs, and design
  choices, and takes responsibility for the contribution.
- The PR description says which AI tools were used and how. A PR with
  substantial LLM-generated code carries the `LLM-generated` label.
- Comments on GitHub and Zulip must be the contributor's own words: an agent
  never drafts them.
- A new theory starts with a Zulip discussion. Then send small, coherent PRs,
  generic lemmas first, each checked against current Mathlib `master`, which
  may already contain it.
- The candidate's import closure contains only Mathlib. Vendored packages, Tau
  Ceti, and application layers must be removed or replaced first.
- Mathlib's linters must be clean, with its naming and documentation
  conventions; no native evaluation.

## Tau Ceti

Sources: [overview](https://github.com/TauCetiProject/TauCeti),
[repository rules](https://github.com/TauCetiProject/TauCeti/blob/main/AGENTS.md),
[roadmap contribution guide](https://github.com/TauCetiProject/TauCetiRoadmap/blob/main/CONTRIBUTING.md),
and [review rubrics](https://github.com/TauCetiProject/TauCetiReview/tree/main/rubrics).

- New mathematics enters through human-curated roadmaps, which specify the
  desired mathematics independently of any existing implementation. An existing
  library can be cited as a source for a roadmap; a port follows the roadmap's
  specification, not the library's.
- Tau Ceti tracks Mathlib `master`, allows no `set_option`, keeps no backward
  compatibility layer, and takes one topic per pull request.
- It does not automatically move its material into Mathlib, and a Mathlib
  candidate cannot depend on Tau Ceti.

## Preparing a contribution

1. Search the pinned dependencies and current upstream for the result.
2. Design the reusable statement, prove it locally, and audit its API.
3. Obtain the owner's review and choose the route.
4. Prepare the code and an internal factual handoff for the human contributor.
   External actions (pull requests, issues, posts) need the user's explicit
   authorization each time.
5. After a merge, wait until the result is available at the project's pin, then
   migrate users, remove the duplicate, and keep the source mapping and its
   stable identifiers.
