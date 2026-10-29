# Lean Autoformalization Skills

Six focused skills for developing faithful Lean proofs, accompanying a research
paper with a complete formalization, and preparing publication on GitHub,
Palomar, or both. Updated on 29 October 2026. This is a streamlined adaptation of
Scott Armstrong's collection, with one publication workflow; see
[attribution and licensing](ATTRIBUTION.md).

The design keeps everyday proof work small and puts source review, independent
verification, paper-coverage checks, and publication controls at the milestones
where they matter. It does not relax an existing project's frozen-statement or
proof-integrity rules.

## Choose the skill that matches the task

| Skill | When it helps |
| --- | --- |
| [lean-workflow](skills/lean-workflow/SKILL.md) | Prove or repair a result; search Mathlib; maintain paper coverage; compile and check |
| [lean-project-architecture](skills/lean-project-architecture/SKILL.md) | Choose encodings, module boundaries, main statements, and a small Comparator interface for publication |
| [lean-statement-audit](skills/lean-statement-audit/SKILL.md) | Review statement fidelity, paper coverage, proof correspondence, or final evidence |
| [lean-elaboration](skills/lean-elaboration/SKILL.md) | Diagnose actual slowness or run a requested benchmark |
| [lean-orchestrator](skills/lean-orchestrator/SKILL.md) | Coordinate independent proof tasks, route exploration, reviews, and shared compilation |
| [lean-publication](skills/lean-publication/SKILL.md) | Prepare and verify GitHub publication, Palomar submission, or both; carry out authorised external actions |

Ordinary work usually needs only `lean-workflow`. Load the other skills when
their task arises, rather than reading the entire collection at every turn.

## Paper-companion workflow

When publication is part of the intended outcome, state GitHub, Palomar, or both
in the initial formalization request; use the destination clause in
[Prompt suggestions](PROMPT_SUGGESTIONS.md). Apply the relevant requirements
during design and keep expensive verification at integration and publication
milestones. An undecided destination need not block independent proof work.

For a research paper published with its formalization, use the root templates
as needed:

- [FORMALIZATION_REPORT.md](FORMALIZATION_REPORT.md), or the project's existing
  equivalent record, provides the required coverage and correspondence record.
  Update it at coherent milestones. It maps every theorem, proposition, lemma,
  corollary, and substantive mathematical claim in the declared scope to proved Lean code,
  and records mathematically substantive departures from the paper.
- [MANUSCRIPT_RECOMMENDATIONS.md](MANUSCRIPT_RECOMMENDATIONS.md) is an optional,
  advisory list of correctness, clarity, and exposition observations. It may
  remain empty and does not authorize manuscript edits.

An isolated lemma task does not require a new paper-wide inventory; update an
existing applicable record and report substantive source departures as needed.
At intermediate milestones, review changed results and affected dependencies,
preserving valid inventory entries and review findings. A proof-route change
requires revisiting correspondence even when statement review remains valid.

The formal proof may use different helpers, library results, equivalent
representations, and local arguments. The default is to preserve the paper's
main strategy and novel ideas. Routine differences need no report. Prioritize
proving every main result and its required dependencies, while retaining all
other in-scope claims as completion obligations.

Work autonomously within the established scope and authorization. Resolve
uncertainties from available evidence first. Ask only for essential missing
input, decisions, or authorization that block faithful completion; continue
useful independent work. Routine proof choices, difficult proofs, and permission
to continue are not reasons to ask. If the user explicitly requests no questions,
record blockers and leave dependent work pending without guessing or inferring
authorization. Finish when the scope is verified, an applicable resource limit
is reached, or no useful authorized work remains; report results and open
obligations accurately.

## Publication workflow

Use `lean-publication` for an existing public repository, a first publication,
or a curated export from private development. Choose the destination and the
requested action independently: preparing a candidate does not itself publish,
submit, or register it. Reuse authorisation already given for those actions.

Comparator verification is the default for published mathematical results,
including small and single-theorem projects. Keep the comparison interface
focused on advertised results and review it against the source; project size
alone is not a reason to omit it. Reuse applicable evidence at integration and
publication checkpoints. Document actual compatibility or policy blockers.

- **GitHub:** prepare a readable README, links from paper results to Lean code,
  reproducible build and Comparator instructions, suitable CI, licensing, and
  citation metadata. Include CI and Comparator badges near the README title,
  linked to real checks with accurate status and scope.
  Create a versioned GitHub Release when requested. Blueprint, API documentation,
  and Zenodo archival are optional. Palomar-specific submission requirements
  apply only when Palomar is selected.
- **Palomar:** reuse an existing public GitHub commit and its adequate
  documentation, or prepare a public candidate if one is needed. Apply the
  current Challenge/Solution, metadata, Comparator, and preflight requirements.
  A GitHub Release is not required. Publishing private material, submission for
  review, and final registration have their own authorisation scopes.
- **Both:** prepare one candidate with the GitHub and Palomar files before final
  verification, and identify the same commit for both destinations. Share the
  coverage record, source review, and applicable build evidence; repeat affected
  checks when their inputs change.

The [GitHub guide](skills/lean-publication/references/github.md) and
[Palomar guide](skills/lean-publication/references/palomar.md) hold the destination
details. Routine proof development and mathematical review stay in their
existing skills. The unified entry replaces `palomar-deposit`; there is no
second release skill or alias to install from this collection.

## Use and installation

Each directory under `skills/` is a skill entry with YAML
frontmatter and UI metadata. Copy the desired directories into the skill
location used by your agent, such as a project's `.agents/skills/`. Keep
referenced files with their skill. Install all six for the complete route. For
the paper-companion workflow, reuse an existing equivalent coverage record or
copy the formalization report template to the project root; use the
recommendations template as needed.

For Palomar-sensitive project design, install `lean-publication` alongside
`lean-project-architecture` to supply the policy references. Ordinary project
design can use `lean-project-architecture` alone.

When copied skills will be shared, preserve the accompanying attribution,
adaptation notices, and applicable license files alongside them, without
replacing the destination project's license. Exclude `.DS_Store` files from
distribution archives.

Review existing directories and symlinks before copying: five skill names are
shared with the original collection. Do not merge two versions blindly or
install duplicate names in competing discovery locations.

When upgrading from the earlier package, inspect the installed `palomar-deposit`
directory or symlink and preserve any local customizations. After installing
`lean-publication`, retire the old entry, update explicit references to its name,
and check that only the intended publication entry remains discoverable. Copying
the new directories over an existing installation does not remove the old name.

This package does not install anything. It contains no installation script, Lean
project, proof holes, credentials, or preconfigured submission workflow. Local
project instructions continue to govern versions, permitted actions, frozen
declarations, draft quarantine, build concurrency, and public release.

Example requests:

- “Use $lean-workflow to prove this lemma and check its axioms.”
- “Formalize every result in this paper and maintain the formalization report.”
- “Choose a suitable proof route and record substantive departures from the paper.”
- “Use $lean-statement-audit to compare these exports and coverage table with the paper.”
- “Use $lean-publication to prepare this paper companion for GitHub only.”
- “Use $lean-publication to prepare a Palomar submission from this public commit.”
- “Use $lean-publication to prepare GitHub publication and Palomar submission from one candidate, without publishing or submitting.”

For short copy-ready starters and optional task-specific detail, see
[Prompt suggestions](PROMPT_SUGGESTIONS.md).

## What was simplified

Search, proof patterns, naming, and recurring API advice are folded into the
daily workflow. Project planning includes an optional lightweight dependency
graph. Performance diagnosis and requested build measurement share one skill.
Publication shares one preparation workflow and loads destination details only
when needed.

The collection still has six skills. There is no mandatory manifest system,
per-helper approval, exhaustive graph database, machine-readable correspondence
schema, or status form. Existing versions of those controls remain binding where a project has
deliberately adopted them. The formalization report is one lightweight human
readable table; the recommendations file is advisory.

The retained safeguards are complete declared result coverage, precise
mathematical statements, honest proof-route correspondence, axiom checks,
dependency/build hygiene, source review at major boundaries, and the applicable
publication checks. Consider a small Comparator Challenge early when publication
is planned; load the current Palomar submission procedure only when applicable.

## Palomar and existing projects

The [dated requirements guide](skills/lean-publication/references/requirements.md)
links the official sources checked for this edition. Re-read them at deposit
time; requirements can change and this archive does not certify a project. Do
not use a Palomar-compatible default to override stricter repository rules.

For an existing project with approved frozen results, keep its manifests,
checkers, provider quarantine, and author approval process. These skills do not
authorize new Challenge holes, toolchain changes, license changes, publication,
submission, or registration. The user's actual instruction and existing
authorization determine which work is permitted.

## Validation

Package validation results are recorded in [VALIDATION.md](VALIDATION.md). They
cover skill structure, links, archive integrity, and instruction-level scenario
review, not an end-to-end formalization or a real Palomar submission. The design
is a practical starting point, not a claim of universally optimal performance.
Refine it using observed failures rather than adding universal rules for
hypothetical cases.
