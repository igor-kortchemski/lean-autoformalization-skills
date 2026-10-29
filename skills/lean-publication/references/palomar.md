# Palomar preparation and publication

Read this only for Palomar or both destinations. Read
[requirements.md](requirements.md), then refresh its official policy, metadata,
allowlists, and pipeline sources before deposit-sensitive changes. Record the
policy and pipeline revisions actually used; a retrieval date or moving URL is
not an immutable revision. Resolve material conflicts before claiming compliance.

## Prepare the mathematical interface

Identify the exact exports, repository snapshot, project/configuration paths,
and substantive development behind any wrapper. Use the official starter as a
reference, preserving the existing project. Required toolchain changes or new
Challenge holes remain subject to the project's rules and existing authorization.

Keep Challenge small, readable, and independent of proof modules. Its statement
imports must satisfy the current allowlist. Challenge and Solution declarations
must have the same fully qualified names and types, with matching mathematical
dependencies. Comparator must validate this correspondence; similar-looking
source text is insufficient. Inspect the actual Solution and its axiom closure.

Compare every advertised declaration and its semantic definition closure with
the paper. Keep conditional results visibly conditional, explain encoding
differences, and check any specialization from a more general Lean theorem.
Reconcile the selected exports with the shared correspondence record; Palomar
may cover a narrower, accurately described selection than the whole repository.
Do not claim the written proof was formalized when the Lean proof bypasses it.
Preserve established requirements concerning the paper's main strategy and novel
arguments; routine implementation differences need no note or approval.

Write factual `formalization.yaml` metadata using the current schema. Explain
sources, scope, authorship, license, automation, proof correspondence, review,
and known limitations. Include a readable mathematical account of every selected
result. Do not infer human review, endorsement, novelty, or the submitter's
relationship from code ownership alone. Preserve third-party notices and
distinguish paper authors from formalization contributors.

Review the entire submitted tree, including unused files and local dependencies,
against current policy. On a Palomar-only request for an existing public commit,
modify only what submission requires; identify any necessary new candidate.
GitHub presentation improvements and a GitHub Release are not prerequisites.

## Verify and submit

Run focused project checks and local comparison as useful, then follow
[submission.md](submission.md) for the complete official mechanical preflight
and live intake/registration protocol. Preparation without external execution
may leave a ready workflow and clearly unrun preflight; never claim it passed.

Share applicable builds and reviews with GitHub preparation. A successful full
preflight can satisfy the isolated mechanical checks it covers for the same
candidate; it does not replace source review or uncovered project checks.
Treat incomplete runs, resource failures, and missing reports as unverified.
Correct the cause before retrying; never weaken the theorem or bypass a
mandatory checker to obtain a green result.

Public release, preflight, intake, and registration can have different effects
and authorization scopes. Follow the live protocol, reuse permission that
covers the concrete action, and present any missing required decision with its
source. Registration requires the user's decision about the returned review,
as detailed in [submission.md](submission.md). Report actual returned status:
passing preflight does not register a result or guarantee the editorial outcome.
