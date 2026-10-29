# Prompt suggestions for autonomous Lean formalization

Choose one prompt and replace its bracketed placeholders. The named skills supply
the shared proof, review, autonomy, and authorization rules; add only task-specific
scope, preferences, or resource limits. These are practical defaults, not a
measured optimum.

If publication is part of the final deliverable, add this clause to the initial
formalization prompt:

```text
The final deliverable should be ready for publication on [GitHub, Palomar, or both].
Account for that destination during formalization and prepare a verified
publication candidate.
```

Use applicable destination requirements to inform design; keep expensive
verification at relevant integration and publication milestones. “Ready for
publication” requests preparation. Specify publication or submission actions
separately when they are also requested, reusing any authorization already given.
If the destination is undecided, continue work that does not depend on it and
resolve the choice when a concrete design or delivery decision requires it.

## Five short starters

### Complete a target

```text
Use $lean-workflow to complete [target] from [source/locator, if applicable]
through integration and verification. Preserve the mathematical scope, project
rules, and frozen exports. Report the proved declarations, actual checks,
substantive source departures, and remaining obligations.
```

### Formalize a paper

```text
Use $lean-workflow to formalize every theorem, proposition, lemma, corollary,
and substantive mathematical claim in [paper/version and declared scope].
Prioritize main results and their dependencies while retaining every in-scope
obligation. Maintain the existing coverage record or FORMALIZATION_REPORT.md,
including substantive proof departures and which paper arguments were checked.
Use $lean-statement-audit initially to check the inventory, then review changed
results and affected dependencies at milestones. Reconcile the full inventory
and scan for omissions when source or scope changes and before claiming complete
coverage. Finish with current proof evidence and explicit unresolved obligations.
```

### Audit without repairs

```text
Use $lean-statement-audit to compare [exports or declared scope] with
[source/version and locators], without changing maintained project files.
Use permitted builds and temporary probes. Report precise findings on statement
fidelity, coverage, proof correspondence, completion, and missing evidence.
Preserve the status of reused reviews and identify self-review accurately.
```

### Resume work

```text
Use $lean-workflow to resume [target and declared scope] from the code, coverage
record, notes, and actual check outputs. Continue through integration and
verification. Reuse valid work and review components: preserve applicable
statement review, refresh correspondence after proof-route changes, and recheck
mechanical evidence whose inputs changed or are uncertain. Report remaining
obligations without weakening the target.
```

### Prepare publication

```text
Use $lean-publication to prepare [project, source/version, and declared scope]
for [GitHub, Palomar, or both]. Reuse adequate documentation and applicable
verification evidence. Use Comparator for the advertised mathematical results,
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
Use $lean-workflow to formalize [theorem and locator] from [source/version].
Preserve its assumptions and conclusion, justify equivalent encodings, and
respect frozen interfaces. Use $lean-statement-audit for source fidelity and
proof evidence. Report substantive proof departures, the proved export, checks,
and open obligations. Update an applicable coverage record; this task does not
require a new paper-wide inventory.
```

### Review and repair

```text
Use $lean-statement-audit to compare [exports or declared scope] with
[source/version and locators], then use $lean-workflow to repair implementation
defects within that scope. Preserve the mathematical target and frozen exports;
check affected consumers. Refresh affected review components, including proof
correspondence when a route changes. Report fixes, current evidence, and
unresolved findings, identifying self-review accurately.
```

### Investigate an observed performance problem

```text
Use $lean-elaboration to investigate [slow declaration, timeout, or measured
regression]. Establish a comparable baseline and implement the smallest
supported improvement while preserving the mathematical statement, pinned
environment, and project build rules. Report before/after measurements,
validation, and limitations, or state that no improvement was established.
```

Syntax, type, and import errors normally belong to `lean-workflow`.

### Prepare GitHub only

```text
Use $lean-publication to prepare [project and declared paper scope] for GitHub
only. Reuse adequate layout, README, CI, licensing, and citation metadata; fill
gaps needed for readers to find and verify the results. Prepare Comparator
verification for the advertised results and include CI and Comparator badges
linked to actual checks. Verify the exact
candidate and report its location, checks, and blockers. This is preparation
only: do not publish or upload. Keep optional sites and archival within the
requested scope; do not add Palomar requirements.
```

### Prepare Palomar from a public commit

```text
Use $lean-publication to prepare Palomar submission of [public repository,
full commit SHA, and results]. Apply current requirements, reuse adequate
presentation and evidence, and prepare the required full preflight. Execute
external checks only if already authorized; identify any unrun checks. If changes
are needed, identify the new candidate and refresh affected evidence. Report
completed checks and blockers. This authorizes preparation only; keep publication
of changes, submission, and registration pending.
```

### Prepare GitHub and Palomar together

```text
Use $lean-publication to prepare [project and declared paper scope] for GitHub
and Palomar as one candidate. Prepare both destinations' files before final
verification, share the coverage record and applicable evidence, and identify
the same intended commit. Include CI and Comparator badges in the GitHub README.
Complete authorized checks, including mandatory
Palomar verification when execution is authorized; report unrun checks precisely.
Return the candidate, actual results, blockers, and proposed actions. This is
preparation only; do not publish, submit, or register.
```

### Carry out selected external actions

Specify the actions and destinations you authorize, such as publishing a named
repository, creating a release, or submitting a public commit. Palomar registration
requires a decision about the returned review.

```text
Use $lean-publication to [specific external actions and destinations] for
[candidate path or exact public commit]. Reuse existing authorization and
confirm that verification still applies before acting. Preserve existing release
identities. For Palomar registration, present the returned review and register
only after my decision about it. Report the exact commit, checks, resulting URLs,
and pending work; distinguish published, submitted, and registered outcomes.
```

Keep reporting proportional to the scope. Avoid fixed agent counts, per-helper
reviews, and prescribed planning forms. Measure real tasks before claiming lower
compute cost.
