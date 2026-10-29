# Package validation

Validation date: **29 October 2026**.

## Scope

This directory is a skill package, not a completed Lean formalization. No Lean
build, theorem proof, Comparator run, hosted Palomar preflight, submission, or
registration was performed. The checks below concern package structure,
internal consistency, and the instructions introduced by this revision.

## Packaging cleanup

On 29 October 2026, addressed F2 and F3 from [AUDIT_CURRENT.md](AUDIT_CURRENT.md):

- The README and architecture skill now identify `lean-publication` as the
  companion supplying policy references for Palomar-sensitive design. Ordinary
  project design remains usable with `lean-project-architecture` alone.
- Converted 23 internal evidence links in the historical audit to package-relative
  paths, retaining historical line numbers in prose. The older-package citation
  explicitly identifies an external source that is not bundled.
- Marked the later audit's findings as addressed while preserving its original
  assessment, measurements, and snapshot fingerprint.
- Removed Finder metadata and added a `.DS_Store` rule to `.gitignore`.

F1's destination-specific badge condition and the optional initial-prompt
destination clause were implemented before this cleanup and remain intact.

All six skills passed `skill-creator/scripts/quick_validate.py`; all six UI
metadata files parsed and passed basic field checks. Package-local Markdown file
links resolved inside an isolated relocated copy, with no absolute or escaping
file targets. Code fences are balanced; no CRLF files, symlinks, or Finder
metadata remain. License files and attribution are unchanged. These checks do
not constitute a new Lean, Comparator, or publication run. Installed skills and
external repositories were not modified.

The following sections preserve earlier implementation and validation records.

## Comparator publication default

On 29 October 2026, made Comparator the default for published mathematical
results, including small and single-theorem GitHub-only projects. Publication,
architecture, statement review, README guidance, and publication prompts now
agree on that scope. Ordinary proof work retains focused checks; comparison
belongs at meaningful integration and publication checkpoints.

The GitHub guide requires both CI and Comparator badges near the README title,
linked to actual checks for the intended branch. Where one workflow backs both,
the README must disclose the shared aggregate status without inventing separate
job results or duplicating check runs. Unrun, skipped, incompatible, and failed
checks must not be presented as successful comparison.

The default preserves source review of the Challenge, project trust policy,
frozen interfaces, proof-hole rules, pinned versions, and existing publication
authorization. Palomar-specific policy and full preflight remain conditional
on that destination. Applicable comparison evidence can be reused, including
from full Palomar preflight; changes require reassessing the affected evidence.
Concrete incompatibility or a lack of advertised mathematical target results
must be explained rather than using project size as an exemption.

Validation completed:

- All six skills passed `skill-creator/scripts/quick_validate.py` with the
  user-installed PyYAML 6.0.3. This supersedes the earlier environment limitation;
  the historical records below retain the results of their original runs.
- All six UI metadata files parsed and passed basic field and length checks.
- Local Markdown targets resolve and code fences are balanced. The collection
  still has six skills; no scripts, dependencies, or badge service were added.
- Three parallel reviewers contributed or checked the scoped edits, including
  consistency of project trust policy, public-result coverage, and badge status.
- Comparator command and platform guidance was checked against the current
  [Lake reference](https://lean-lang.org/doc/reference/latest/Build-Tools-and-Distribution/Lake/),
  and badge guidance against [GitHub's documentation](https://docs.github.com/en/actions/how-tos/monitor-workflows/add-a-status-badge).

A fresh reviewer read the revised skills and fictional project states without
the audit or expected answers. These were instruction-level walkthroughs:

| Scenario | Observed interpretation |
| --- | --- |
| One theorem, passing build CI, no comparison, supported toolchain, GitHub preparation only | Prepare a small source-reviewed comparison interface and actual checks; project size does not waive Comparator. No publication. |
| Both checks already run unconditionally in one workflow | Keep two visibly labelled badges, disclose shared aggregate status, and reuse the workflow without duplicate runs or badge infrastructure. |
| Frozen incompatible toolchain, GitHub-only project with an allowed native axiom | Preserve pins and trust policy, report comparison unverified and the concrete blocker, and never invent a passing badge. |
| Both destinations requested for an exact unchanged public commit; README badges missing | Reuse applicable preflight evidence for that commit and prepare the README patch separately. A successor commit must be identified explicitly and receive the required verification; the old report does not certify it. |

This change updates the skill package's publication instructions. No Lean
project, GitHub workflow, badge endpoint, or Palomar submission was executed or
published. The sections below are historical records of earlier revisions.

## Audit implementation

Implemented the recommendations from [AUDIT.md](AUDIT.md) on 29 October 2026.
The audit remains a historical assessment of its recorded snapshot; the sections
below this implementation record also describe earlier revisions.

- **F1:** statement-fidelity review and proof-correspondence review now have
  separate reuse criteria. Proof changes require checking the affected route and
  implementation dependencies; valid review components and their status remain
  reusable. Mechanical evidence still depends on the actual proof bodies.
- **F2:** initial inventories can be reused per result. Intermediate reviews
  cover changed results and affected dependencies; isolated theorem reviews stay
  local. Source/scope changes and whole-paper completion retain full omission scans.
- **F3:** the README explicitly explains retirement of the differently named
  `palomar-deposit` entry during an upgrade, including local customizations and
  explicit references. No installed skills were changed.
- **F4:** ordinary computational proof methods follow the project's trust policy;
  Palomar's axiom restrictions apply to Palomar targets. Actual closures in the
  pinned toolchain determine admissibility; no custom axioms or unapproved holes
  were authorized.
- **F5:** prompts now begin with five short starters and retain seven focused
  optional variants. Each skill retains concise standalone autonomy guidance.

The report template now uses a neutral placeholder row, worker handoffs include
references to actual validation evidence, and the README excludes Finder metadata
from future archives. Both local `.DS_Store` files were removed. Six skill entry
points remain; no installer, script, runtime dependency, evidence database, or
additional approval process was added. No archive was rebuilt.

Validation completed for this implementation:

- Ruby YAML parsed all six skill frontmatters and six UI metadata files. Names,
  supported fields, descriptions, licenses, and basic UI field lengths passed.
- Skill frontmatter, UI metadata, and all destination/proof-tool reference files
  remain byte-identical to the pre-implementation snapshot.
- Local Markdown link targets resolve. Code fences are balanced; no CRLF files,
  symlinks, or Finder metadata remain in the package.
- The skill-creator Python validator was attempted but could not start because
  PyYAML is unavailable. No pass from that validator is claimed; the Ruby checks
  above provide the available structural validation without installing dependencies.
- The coordinator reviewed the changed instructions and prompts for consistent
  scope, review reuse, project trust policy, and publication authorization.

A fresh reviewer, given the revised skills and fictional project states but not
the audit or expected answers, walked through these requests:

| Request and state | Observed interpretation |
| --- | --- |
| Review one rewritten proof whose statement is unchanged | Reuse applicable statement review and current mechanical evidence; refresh its changed proof correspondence and preserve other entries. |
| Review one newly proved result in an unchanged 80-claim paper | Reuse the checked inventory; inspect the new proof and obtain focused evidence. A milestone alone does not trigger a full omission scan or establish whole-paper completion. |
| Complete a GitHub-only computation proof allowed by project policy | Retain the permitted method, check the final proof, and disclose its actual axiom closure without imposing Palomar policy. |
| Prepare both destinations from one already-verified public commit | Check evidence identity and coverage, reuse applicable checks, and return the candidate without new publication, submission, or registration. |
| Finish without questions while one ambiguity blocks the target | Leave the dependent theorem pending, record the ambiguity, and continue the two actionable independent proof tasks. |

These were instruction-level walkthroughs, not executed proofs or publication
workflows. The reviewer also distinguished existing mechanical evidence from a
claim of compliance with current external policy: any required live-policy
refresh remains applicable and was not performed in this implementation check.

Whitespace-delimited text counts, including frontmatter where applicable:

| Text | Before | After |
| --- | --- | --- |
| Six skill entry points | 5,057 words | 5,202 words |
| Prompt library | 1,951 words | 894 words |
| Default target prompt | 196 words | 34 words |

The prompt library is 54% shorter. Added review criteria account for the small
net increase in skill text despite compressed autonomy guidance. These are text
measurements, not demonstrated token, CPU, latency, or completion improvements.
Representative real-task measurements remain future work; this revision does
not claim a Lean or publication benchmark.

## Unified publication implementation

Implemented `lean-publication` on 29 October 2026, replacing the collection's
`palomar-deposit` entry point. The package still has six skills. The new entry
coordinates GitHub, Palomar, or both with shared preparation and conditional
references; no scripts, runtime dependencies, installer, or extra approval
system were added. Existing installed skills and ZIP archives were not changed.

Validation completed:

- All six skill frontmatters and UI metadata files parsed with Ruby YAML.
  Names match directories; descriptions, allowed frontmatter fields, licences,
  UI names, and UI description lengths passed the checks.
- All package-relative Markdown links and referenced headings resolve. No
  overlapping publication entry point or stale link to the old directory remains.
- The migrated Palomar `requirements.md` and `submission.md` are byte-identical
  to the pre-change snapshot. Their dated facts still require live refresh when
  used; preservation is not a fresh policy certification.
- Three independent agents reviewed community practice/UX, correctness and
  authorization, and simplicity. Each found no material issue in the implemented
  skill or its integration.

Each reviewer also walked through one instruction-level scenario:

| Scenario | Observed interpretation |
| --- | --- |
| Small completed project, GitHub preparation only, adequate README/CI and `CITATION.bib` | Reuse existing files and covered build evidence; no forced CFF, website, Palomar files, or publication. |
| Palomar preparation from a public commit, standalone Comparator pass but no official full report | Keep adequate presentation/CI, prepare full preflight, and report it unverified if execution is outside scope; no intake or registration. |
| Both destinations, evidence for A, then a needed statement change producing B | Do not silently change mathematics; after an authorized change, refresh affected review and build evidence for B while sharing applicable checks across destinations. |

These were reviews and scenario walkthroughs, not executed release workflows or
Lean builds. No remote repository, CI job, archive, or Palomar entry was created.
The skill-creator Python validator was attempted but could not run because
PyYAML is absent from the available Python environments. The Ruby metadata
checks above passed; no pass from the Python validator is claimed and no
dependencies were installed.

## Paper-companion revision

The sections from here onward record the earlier paper-companion revision and
its validation; the current publication implementation is recorded above.

This revision keeps the six-skill architecture and adds no runtime dependency,
installer, workflow daemon, or new approval ledger. It adds two root templates:

- `FORMALIZATION_REPORT.md` for complete result coverage and substantive
  paper–formalization differences;
- `MANUSCRIPT_RECOMMENDATIONS.md` for optional human-facing correctness,
  clarity, and exposition observations.

The skills require faithful coverage of the declared paper scope, prioritizing
proofs of every main result and their required dependencies. Work proceeds
autonomously within existing authorization and project requirements. Essential
questions are allowed after checking available evidence; explicit no-questions
runs leave unresolved decisions pending. Substantive departures and obstructions
are recorded while useful unaffected work continues. Existing equivalent coverage
records may replace `FORMALIZATION_REPORT.md`, with milestone updates.

The revision also incorporates the earlier efficiency clarifications: related
axiom queries are normally batched after coherent edits; an earlier verification
claim still needs evidence; and a substantive source audit may be reused only
when its source, elaborated statement, and semantic dependencies are unchanged.
Reuse preserves findings and review status, so self-review does not become an
independent review.

## Static checks

Before the audit cleanup, earlier packaging checks covered:

- six skill entrypoints with parseable YAML frontmatter, matching directory
  names, nonempty descriptions, and the expected license;
- six parseable UI metadata files with display names and short descriptions;
- existing targets for all package-relative Markdown links;
- the two new templates and their references from the README and prompts;
- absence of symlinks, macOS metadata, stale references to a missing audit file, absolute
  local workstation paths, and CRLF line endings;
- presence of the then-current coverage, route-adoption, audit-reuse, and
  review-status rules in the relevant skill entrypoints;
- ZIP integrity and extraction round-trip against the source tree.

Those archive checks passed. YAML was parsed with PyYAML 6.0.3. The distributed
archive contains only the intended top-level `lean-palomar-skills/` directory.

For this audit cleanup, agent cross-reviews and local Markdown link/heading checks
passed. All six skill frontmatters and six UI metadata files were parsed with
Ruby's YAML parser and remain byte-identical to the pre-edit snapshot. File-path
and SHA-256 comparisons confirm `lean-palomar-skills` is unchanged.
The skill-creator validator was attempted but could not run because PyYAML is
unavailable in the checked Python environments; no pass from that validator is
claimed. No archive was rebuilt and no dependencies were installed.

## Instruction-level scenarios reviewed

The edited instructions were checked against these cases:

| Scenario | Required behavior |
| --- | --- |
| Routine tactic or helper change | Proceed without requesting human input or a difference entry |
| Main results and other claims remain | Prioritize main results and their dependencies; retain every in-scope obligation |
| Difficult proof or missing helper | Investigate viable routes; record any remaining obstruction and continue useful work without asking permission to continue |
| Essential source interpretation remains unresolved | Ask a focused question after checking available evidence; continue independent work |
| Essential factual submission metadata is unavailable | Ask for the missing facts after checking available sources; do not invent authorship, provenance, or review |
| Necessary action lacks authorization | Finish authorized preparation, present the concrete candidate/action and governing requirement, and keep the action pending |
| User explicitly requests no questions | Record the unresolved decision or authorization and continue unaffected authorized work |
| Isolated lemma task | Update an existing applicable coverage record; do not create a new paper-wide inventory |
| Shorter alternative route discovered | Explore and adopt autonomously within established requirements |
| Alternative bypasses the paper's novel argument | Record the departure and preserve all required claims and argument-verification requirements |
| Existing equivalent coverage record | Reuse it and update at coherent milestones; no duplicate report |
| General Lean theorem covers a paper lemma | Check the specialization and list the paper lemma separately |
| Alternative Lean proof bypasses a manuscript gap | Verify the result if possible, but record rather than silently repair the gap |
| Completion claim for the whole paper | Scan the declared source scope for omitted substantive results |
| Earlier audit was a self-review | Preserve that status; do not use it as independent review |
| Several results finish together | Batch checks and update the report at the coherent milestone |

No additional per-helper review, manifest, machine-readable correspondence
schema, or mandatory manuscript rewrite was introduced.

## Limits of this validation

These are package and instruction checks, not a runtime benchmark. The cleanup
consolidates repeated policy where practical while keeping each skill and prompt
self-contained. Improved completion or lower cost remains to be established on
representative real tasks, using existing project notes rather than a new suite.
