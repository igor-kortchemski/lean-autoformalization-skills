# Prompt suggestions for autonomous Lean formalization

Choose one prompt and replace its bracketed placeholders. The named skills supply
the shared proof, review, autonomy, and authorization rules; add only task-specific
scope, preferences, or resource limits. These are practical defaults, not a
measured optimum.

## Claude campaign starters

Start Claude Code from the Lean project directory, with Opus 5.5 at `xhigh`,
keeping the Mac awake (`caffeinate -is claude --model claude-opus-5-5 --effort
xhigh`). The
[Claude profile](skills/lean-orchestrator/references/claude-profile.md) is the
single source for models, efforts and resource limits; the prompts below refer
to it instead of repeating its numbers, so a later edit of the profile is not
overridden by an old instruction. Ordinary single-target work can use the
shorter `lean-workflow` starters below.

### Research and blueprint (optional)

```text
Use /lean-orchestrator to prepare a formalization of [theorem] from the sources
in [sources/]. Launch one background Codex worker on gpt-6-astra (high effort) to
find the most formalization-friendly proof, have an Opus subagent (high effort)
audit its findings, then have a Sonnet subagent write [blueprint.md] with the
proof outline. Ask me your questions before starting.
```

### Start a campaign

```text
Use /lean-orchestrator with its Claude profile to formalize [paper/version and
declared scope], following [blueprint or paper]. Apply the profile's caps
[or: the server caps it describes]: Sonnet subagents, routine
workers launched as background Codex processes (Kimi K3.1 Pro at high through
Open Math OS by default, GPT 6 Luna at xhigh as the fallback), and Sol
upgrades. Audits should be done by Sonnet, and if there is a particularly
difficult part of the code to write you can move it to GPT 6.1 Sol (medium)
within the Sol cap. Build the dependency graph, have the
key statements audited and present them to me for approval before freezing
them, then prove node by node with sealing and re-audit. Make a detailed plan
first and report completed results, actual checks and remaining obligations.
```

### Resume a campaign

```text
Use /lean-orchestrator with its Claude profile to resume [campaign and scope].
Read the existing plan, dependency graph, handoff notes and verification
outputs. Check the Codex workers and builds still running, reuse valid work,
then continue the next dependency-ready nodes within the profile's limits.
Preserve the frozen statements and report unresolved blockers.
```

### Clean up before release

```text
Use /lean-orchestrator to run the cleanup phase of its Claude profile on
[project]. Have one Sonnet worker do the dead-code sweep: check the paper's
result inventory, public uses and Comparator identities first, remove only
private fragments whose abandonment is established, report unused public
declarations for my decision, and recompile every consumer after each removal.
Then measure elaboration, apply supported improvements with /lean-elaboration,
and measure again. Have a different Sonnet agent audit the result. Preserve
every frozen and advertised statement, and report the before and after
measurements and the removed declarations.
```

## Publication clause

If publication is part of the final deliverable, add this clause to the initial
formalization prompt:

```text
Prepare the final deliverable for GitHub with a Palomar-compatible artifact.
Account for compatibility during formalization and report completed checks and
remaining gaps. Full Palomar preflight and registry actions are not requested.
```

Use current artifact requirements to inform design; keep expensive
verification at relevant integration and publication milestones. “Ready for
publication” requests preparation. Specify publication or submission actions
separately when they are also requested, reusing any authorization already given.
The artifact default does not require choosing a registry action before proof work.

## Five short starters

### Complete a target

```text
Use /lean-workflow to complete [target] from [source/locator, if applicable]
through integration and verification. Preserve the mathematical scope, project
rules, and frozen exports. Report the proved declarations, actual checks,
substantive source departures, and remaining obligations.
```

### Formalize a paper

```text
Use /lean-workflow to formalize every theorem, proposition, lemma, corollary,
and substantive mathematical claim in [paper/version and declared scope].
Prioritize main results and their dependencies while retaining every in-scope
obligation. Maintain the existing coverage record or FORMALIZATION_REPORT.md,
including substantive proof departures and which paper arguments were checked.
Use /lean-statement-audit initially to check the inventory, then review changed
results and affected dependencies at milestones. Reconcile the full inventory
and scan for omissions when source or scope changes and before claiming complete
coverage. Finish with current proof evidence and explicit unresolved obligations.
The paper is [published in a journal: reference and DOI, published PDF at
[path] / on arXiv only or submitted / not distributed]; draft the corrections
deliverable for it from the audited errors found.
```

### Audit without repairs

```text
Use /lean-statement-audit to compare [exports or declared scope] with
[source/version and locators], without changing maintained project files.
Use permitted builds and temporary probes. Report precise findings on statement
fidelity, coverage, proof correspondence, completion, and missing evidence.
Preserve the status of reused reviews and identify self-review accurately.
```

### Resume work

```text
Use /lean-workflow to resume [target and declared scope] from the code, coverage
record, notes, and actual check outputs. Continue through integration and
verification. Reuse valid work and review components: preserve applicable
statement review, refresh correspondence after proof-route changes, and recheck
mechanical evidence whose inputs changed or are uncertain. Report remaining
obligations without weakening the target.
```

### Prepare publication

```text
Use /lean-publication to prepare [project, source/version, and declared scope]
for [GitHub, Palomar, or both]. Reuse adequate documentation and applicable
verification evidence. Prepare Palomar-compatible artifacts by default. Use
Comparator for the advertised mathematical results,
including small projects. For GitHub or both destinations, include CI and
Comparator badges in the GitHub README.
Deliver a reviewable candidate, its identity, actual
checks, blockers, and proposed external actions. This request authorizes local
preparation only; do not publish, submit, or register it.
```

## Optional variants

Use these when a more specific task or publication action is intended.

### Formalize one theorem from a source

```text
Use /lean-workflow to formalize [theorem and locator] from [source/version].
Preserve its assumptions and conclusion, justify equivalent encodings, and
respect frozen interfaces. Use /lean-statement-audit for source fidelity and
proof evidence. Report substantive proof departures, the proved export, checks,
and open obligations. Update an applicable coverage record; this task does not
require a new paper-wide inventory.
```

### Review and repair

```text
Use /lean-statement-audit to compare [exports or declared scope] with
[source/version and locators], then use /lean-workflow to repair implementation
defects within that scope. Preserve the mathematical target and frozen exports;
check affected consumers. Refresh affected review components, including proof
correspondence when a route changes. Report fixes, current evidence, and
unresolved findings, identifying self-review accurately.
```

### Investigate an observed performance problem

```text
Use /lean-elaboration to investigate [slow declaration, timeout, or measured
regression]. Establish a comparable baseline and implement the smallest
supported improvement while preserving the mathematical statement, pinned
environment, and project build rules. Report before/after measurements,
validation, and limitations, or state that no improvement was established.
```

Syntax, type, and import errors normally belong to `lean-workflow`.

### Audit a library for public reuse

```text
Use /lean-library to audit [repository and branch] for public reuse, Mathlib,
and Tau Ceti, read-only. Record the exact baseline, run the mechanical checks
exhaustively and sample the semantic ones deliberately, test an outside
consumer, and write LEAN_LIBRARY_AUDIT.md with prioritized findings and an
ordered remediation plan. Do not change sources, statements, pins, or the
license, and do not commit or publish.
```

### Start a book formalization

```text
Use /lean-book to set up the formalization of [authors, title, edition] from
[PDF path; converted text path, if any]. Draft AGENTS.md from the skill's
template, leaving open what I must decide (provider authorization, scope,
publication target, reviewers), set up the repository with the source material
ignored, seed the inventory of [pilot section] from [existing extraction or
ledger, if any], and propose the pilot. Do not send book material to any
provider before AGENTS.md records my decision.
```

### Prepare GitHub only

```text
Use /lean-publication to prepare [project and declared paper scope] for GitHub
only. Reuse adequate layout, README, CI, licensing, and citation metadata; fill
gaps needed for readers to find and verify the results. Prepare Comparator
verification for the advertised results and include CI and Comparator badges
linked to actual checks. Verify the exact
candidate and report its location, checks, and blockers. This is preparation
only: do not publish or upload. Keep optional sites and archival within the
requested scope. Meet current Palomar artifact requirements, but do not run full
Palomar preflight, submit, or register without a separate request.
```

### Prepare Palomar from a public commit

```text
Use /lean-publication to prepare Palomar submission of [public repository,
full commit SHA, and results]. Apply current requirements, reuse adequate
presentation and evidence, and prepare the required full preflight. Run it only
if already requested and authorized; identify any unrun checks. If changes
are needed, identify the new candidate and refresh affected evidence. Report
completed checks and blockers. This authorizes preparation only; keep publication
of changes, submission, and registration pending.
```

### Prepare GitHub and Palomar together

```text
Use /lean-publication to prepare [project and declared paper scope] for GitHub
and Palomar as one candidate. Prepare both destinations' files before final
verification, share the coverage record and applicable evidence, and identify
the same intended commit. Include CI and Comparator badges in the GitHub README.
Complete requested, authorized checks; prepare the full Palomar verification
workflow but run it only if requested. Report unrun checks precisely.
Return the candidate, actual results, blockers, and proposed actions. This is
preparation only; do not publish, submit, or register.
```

### Carry out selected external actions

Specify the actions and destinations you authorize, such as publishing a named
repository, creating a release, or submitting a public commit. Palomar registration
requires a decision about the returned review.

```text
Use /lean-publication to [specific external actions and destinations] for
[candidate path or exact public commit]. Reuse existing authorization and
confirm that verification still applies before acting. Preserve existing release
identities. For Palomar registration, present the returned review and register
only after my decision about it. Report the exact commit, checks, resulting URLs,
and pending work; distinguish published, submitted, and registered outcomes.
```

Keep reporting proportional to the scope. Treat the selected profile's agent
counts as ceilings, not staffing targets. Avoid per-helper reviews and prescribed
planning forms. Measure real tasks before claiming lower compute cost.
