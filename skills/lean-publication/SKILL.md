---
name: lean-publication
description: Prepare, verify, and publish Lean formalizations on GitHub, in Palomar, or both. Use for public repositories, releases, GitHub deposits, and Palomar submissions; not routine proof development.
license: CC-BY-4.0
---

# Publish a Lean formalization

Read the project instructions and inspect the existing artifact. Infer the
destination and action from the request and prior decisions; do not require a
questionnaire. A preparation request ends with a reviewable local candidate.
Carry out publication or submission only within the user's authorization.

Prepare GitHub publication artifacts for mathematical results to meet current
Palomar requirements by default. Apply relevant constraints during design, reuse
validation evidence, and report unresolved or unverified compatibility issues.
Preserve established toolchains, dependencies, and proof policy; report
incompatibilities before changing them. Full Palomar preflight, intake, and
registration are separate requested actions; GitHub publication alone does not
request them. A request to submit includes its required verification, while
registration still requires the decision described in the submission protocol.

| Work | Read when applicable |
| --- | --- |
| Artifact preparation | [requirements.md](references/requirements.md) and [palomar.md](references/palomar.md): current constraints, statement interface, and metadata |
| GitHub publication | [github.md](references/github.md): public repository, Comparator, CI and badges, and requested GitHub Release |
| Requested Palomar verification or submission | [submission.md](references/submission.md): full preflight, intake, and registration protocol |

Palomar needs a public GitHub commit, not necessarily a GitHub Release. For an
existing public commit, reuse its presentation and CI; do not redesign the
repository just to submit it. If private work must become public, prepare the
candidate and establish any missing publication authorization. Never infer
permission to expose private material from a Palomar-only request.

## Prepare the shared candidate

Identify the source paper/version, declared scope, target repository and
revision, chosen license, and actual proof status from available evidence.
Preserve useful layout and history. For a curated export, record the source
revision and whether it becomes the maintained repository or is synchronized
from another development. Use an isolated export when useful; do not rewrite
history or change repository visibility merely to prepare it.

Reuse the project's correspondence record or `FORMALIZATION_REPORT.md` when
present. Otherwise write a proportionate source-to-Lean map in the README or a
linked report; no particular template is required. Reconcile advertised results
with proved declarations or checked specializations. A whole-paper claim must
cover every in-scope theorem, proposition, lemma, corollary, and substantive
claim, with a whole-scope omission scan when source or scope changes and before
claiming whole-paper completion. Reuse an independently checked inventory and
individually valid entries; establish the inventory if absent, and keep reviews
of selected results scoped to those results and relevant dependencies.
Distinguish proving a result from checking the paper's argument; explain
substantive departures, extra assumptions, and remaining gaps.

Include the required proof modules or public dependencies pinned to reproducible
revisions. Keep `lean-toolchain`, the Lake configuration, and the manifest in the
candidate. Review all content that would become public, including history if
published, for credentials, private paths, unpublished material, and unwanted
generated artifacts. Preserve authorship, provenance, and third-party notices.
Never invent a license choice, endorsement, DOI, review, or missing proof count.

Publication cleanup must preserve theorem statements and their defining
dependencies. Respect frozen declarations and the project's proof policy.
Prepare documentation, Challenge/Solution, Comparator configuration, and
formalization metadata before final checks, so they describe one candidate.

## Verify once where the evidence applies

Verify the candidate using the documented commands in a clean checkout with
public dependencies. Ensure every advertised result is built; a default Lake
target may omit modules. Inspect the relevant proof/axiom closure and existing
project checks. A proved result must not depend on `sorryAx`. Label unfinished
work and deliberate Challenge holes separately; report other axioms honestly
and apply the project's policy. Check Palomar artifact requirements for the
published mathematical exports and the entire candidate tree, including unused
files; a compatible statement interface alone is insufficient.

Use Comparator by default for published mathematical results, including small
and single-theorem projects. Reuse or prepare a small Challenge/Solution interface
for the advertised public results; review the Challenge and its definitions
against the mathematical source independently of the proof implementation.
Verify the exact candidate, configuration, declarations, and permitted axioms.
Use Palomar's permitted axioms together with any stricter project policy; never
widen a policy to pass. Report concrete toolchain or policy blockers without
silently upgrading versions, bypassing checks, or claiming comparison succeeded. Project size alone
is not an exception; a utility library without such target results may use a
suitable kernel/axiom check instead, labeled accurately.

Review source correspondence, metadata, and release contents. Use
`lean-statement-audit` if available when mathematical review is needed; prefer an
independent reviewer for the final mathematical interface and label self-review.
Reuse statement-fidelity findings when source, elaborated statements, and semantic
dependencies remain unchanged. Proof-correspondence findings also depend on the
proof route and relevant implementation dependencies: after proof changes,
check and refresh affected correspondence findings while preserving the rest.
Preserve findings, including unresolved issues, and review status, and honor any
required fresh review; tactic-only changes need not cause a full source audit.

A clean CI build or full official preflight can satisfy checks it demonstrably
covers for this candidate. Inspect its report and identity; a green label alone
is insufficient. Reuse a full preflight's Comparator evidence when it covers
the same candidate and configuration. Run comparison at relevant integration
and publication checkpoints, not after every helper edit. Do not repeat an
equivalent build because two destinations were selected, or substitute ordinary
CI for mandatory Palomar verification. Report the checks actually completed and
any remaining gaps; build or Comparator success alone is not full Palomar
verification. Do not add a full-preflight CI job merely to prepare a GitHub artifact.
Changes to sources, dependencies, toolchain, targets, or configuration require
reassessing affected evidence. Reuse does not turn self-review into independent
review. Check links, citation metadata, and generated documentation as applicable.

## Finish within the requested scope

Resolve routine choices from available evidence and reuse existing authorization.
Ask only for essential missing facts, decisions, or permission that block
completion; explain the exact blocker and its source, and continue independent
authorized work. If the user requests no questions, record and report the
blocker, leave dependent actions pending, and do not guess facts or authorization.

Follow the selected reference for authorized external actions. For both, bind
the GitHub artifact and Palomar submission to the same final commit. If later
review requires changes, identify a new candidate and release version as needed;
never silently move a published release. Palomar's review-dependent registration
decision remains distinct from authorization to submit.

Return usable paths or URLs, the candidate/release commit when available, the
checks actually completed, and any unresolved limitations. State separately
what is prepared, verified, published, submitted, and registered. A failed or
pending destination must not obscure a completed one. No extra status database
or approval ledger is needed.
