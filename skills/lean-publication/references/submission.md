# Full preflight and submission

Read the current [verifier documentation](https://github.com/PalomarRegistry/PalomarSubmission/blob/main/README.md),
[reusable workflow](https://github.com/PalomarRegistry/PalomarSubmission/blob/main/.github/workflows/submission.yml),
and [agent intake protocol](https://submit.palomar-registry.org/llms.txt) at use
time. The following summarizes the route observed on 28 October 2026.

## Complete mechanical preflight

Prepare the official reusable `submission.yml` call for the exact public
repository, source commit, project path, metadata path, and Comparator path.
Resolve a real full pipeline commit; use that same SHA for both the workflow
reference and `pipeline_commit`. Never invent a pin or leave a branch reference.

Set `mode: full`, not the preparation-only `preflight` mode. External callers
use `execution_profile: palomar-standard-v1`. Supply a 12-character lowercase
alphanumeric `request_id` and the required options, including a truthful
authorization relationship. Use the workflow's current schema; do not copy an
example's personal relationship as a default. Prepare a workflow locally if
publication or execution is not yet authorized.

Inspect `mechanical-report.json`, its status, source and pipeline identities,
paths, declarations, and completed checks. A green job label alone is not
evidence. Lean and NanoDa acceptance are mandatory; interpret any advisory
con-ron result according to the current report policy. Local builds and
standalone Comparator checks are useful earlier diagnostics, not substitutes
for this full preflight. This is a predictive check, not registry intake.

Fix diagnostic causes before retrying. Resource or environment failures are
not mathematical refutations and are not passes. Keep the passing report with
the candidate revision; a changed source snapshot needs fresh verification.

## Intake and registration

Before intake, follow live `llms.txt`. Complete authorized preparation before
requesting missing authorization. Present the concrete repository, commit,
Comparator path, claimed relationship, and proposed action, with the protocol
requirement that makes a decision necessary. Leave intake pending until any
required authorization is available. Reuse existing permission when it covers
the action. If the user requested no questions, report missing authorization
without requesting a response and continue useful authorized work.
The agent route uses `gh` and temporary tag/secret-gist proof artifacts; do not
automate the person's browser sign-in. Follow cleanup and retry instructions,
protect bearer tokens, and stop on an unknown submission outcome.

Show the returned review and what registration publishes. Register only on the
user's decision about that review, using its exact `review_sha256`. Submission
authorization does not authorize that later decision. Do not publish private
review contents before registration. These boundaries come from the
[service protocol](https://submit.palomar-registry.org/llms.txt).
If the required decision is missing, request it after presenting the review and
publication effects, unless the user requested no questions. Leave registration
pending until that decision is available.

Verification already exposes source/run information; registration also
publishes the review and preserves the source, as described by the
[publication contract](https://github.com/PalomarRegistry/PalomarPolicy/blob/main/docs/specification.md).
Record actual returned submission and registration identifiers, never infer
completion from a request being sent. Follow service retry delays and limits;
fix a known failure before another attempt.
