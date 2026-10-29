# Proposal: an early independent statement check

Status: implemented in this checkout on 29 October 2026 after user approval.
The proposed wording and its audit below are retained as the design record;
the active instructions are in the four skill files linked below. No installation
or synchronization command was run.
Implementation checks and the standalone-orchestrator clarification are recorded
in [VALIDATION.md](VALIDATION.md#early-statement-checkpoint-implementation).

The aim is to catch a wrong mathematical target before substantial proof effort
depends on it, with one focused review and no new approval workflow. This extends
the existing statement audit rather than introducing another skill or tool.

## Proposed instruction

Add this subsection to `lean-statement-audit`, before “Compare the mathematics”:

### Early statement checkpoint

Before moving from exploration to substantial proof work on a main source result,
or using a source-facing mathematical interface for substantial dependent work,
obtain a passing statement-fidelity review from a reviewer who did not author
the declaration. This applies to a sustained single-worker proof as well as
delegated work. Ordinary internal helpers need no separate checkpoint.

Use one independent reviewer by default. Give them the source version and exact
locations, the proposed Lean declaration, its relevant definitions, and any
existing applicable review. They should reconstruct the source meaning first,
then inspect the elaborated statement and its semantic dependencies using
“Compare the mathematics” below. Reuse current elaboration evidence or perform a
focused check, respecting the project's proof-hole rules. A passing review
establishes statement fidelity, not completion of the target's proof.

An unresolved source mismatch, ambiguity, or required characterization bridge
prevents a pass for claims relying on it. Work to establish that bridge may
proceed: independently review its own statement against the explicit source
obligation, without assuming its conclusion, then prove it. This also applies
when the bridge is itself a main result. Keep claims relying on the missing
identification pending until the bridge is proved. Resolve actionable findings
within existing authorization and return only affected parts for review.

Scope this early review to statement fidelity; leave target-proof, paper-coverage,
full-build, and Comparator checks at their existing milestones. Exploration
resolves uncertainty about the statement, encoding, or feasible proof route;
sustained implementation of the chosen route requires a pass. Searches and
independent work can continue while review is pending. If independent review is
unavailable, report that blocker once and keep affected work exploratory;
self-review does not pass this checkpoint. Use the existing clarification policy
for essential missing input.

Batch closely related statements and review shared definitions once. Reuse a
passing independent review when the source, elaborated statement, and semantic
dependencies are unchanged. Recheck affected parts after a change to those
inputs; proof-body-only changes follow the existing proof-correspondence rules.
Record the source and declaration reviewed, reviewer, verdict, and any findings
briefly in an existing project record or handoff. No new manifest, ledger, or
per-helper form is required. Proceed after a pass without another user approval,
unless the project already requires one.

## Minimal integration

Keep the instruction above in one place. The following small routing edits would
make it reachable through normal entry points and remove contradictory defaults:

| Existing location | Proposed edit |
| --- | --- |
| [lean-workflow](skills/lean-workflow/SKILL.md), “Work at the smallest useful scale,” after step 2 | Add: “Before substantial proof work on a main source result or substantial work depending on a source-facing interface, obtain a passing independent statement-fidelity review; reuse an applicable passing review.” |
| [lean-workflow](skills/lean-workflow/SKILL.md), final paragraph | Replace the blanket statement that this skill introduces no independent reviewer with: “Independent review is required at the early statement checkpoint; ordinary helpers do not acquire a separate review requirement. No manifest, dependency database, or status ledger is introduced.” |
| [lean-project-architecture](skills/lean-project-architecture/SKILL.md), final paragraph | Replace “Obtain available independent source review…” with: “Before substantial proof work, obtain a passing independent statement-fidelity review of the main interface; reuse valid review and revisit affected findings after semantic changes. Ordinary internal helpers need no separate approval cycle.” |
| [lean-orchestrator](skills/lean-orchestrator/SKILL.md), “Split by actual independence” | Add: “Before assigning substantial proof tasks, check that the relevant main statements and shared source-facing interfaces have passed independent statement-fidelity review; batch related reviews and continue independent work while they are pending.” |
| [lean-statement-audit](skills/lean-statement-audit/SKILL.md), final paragraph | Add after the self-review fallback: “Labelled self-review does not satisfy the early statement checkpoint.” |

Keep the three entry points usable with partial installations. Accompany their
new trigger with this routing sentence:

> Use `lean-statement-audit` when available; otherwise have one reviewer who did
> not author the declaration compare the exact source, elaborated statement, and
> relevant definitions using this skill's fidelity rules. Claims relying on
> unresolved source ambiguity or missing semantic justification cannot pass;
> work to establish a missing bridge can proceed after review of its own target.
> No additional installation or user approval is required.

Existing frozen-statement rules and final proof, coverage, and publication checks
continue to apply. Existing projects can reuse qualifying independent reviews;
this proposal does not require restarting their campaigns.

## Expected behavior

| Situation | Expected action |
| --- | --- |
| New main theorem ready for sustained proof work | Run one focused independent statement review, then proceed on a pass. |
| Several targets use the same definitions | Review the related targets together and inspect their common semantics once. |
| Routine helper or tactic repair under a reviewed interface | Use ordinary focused validation; no new statement checkpoint. |
| A changed definition alters an unchanged theorem's meaning | Recheck affected statement-fidelity findings before dependent work resumes. |
| The main statement is unchanged but the proof route changes | Preserve valid statement review; refresh affected proof-correspondence findings. |
| Characterization is unfinished | Review and prove the bridge's own target; keep claims relying on the missing identification pending. |
| The source is ambiguous or a review fails | Resolve supported fixes autonomously, ask only for essential missing input, and re-review affected parts. |
| No independent reviewer is available | Report the blocker once; continue exploration and independent tasks without claiming a pass. |
| An entry-point skill is installed without the audit companion | Give an independent reviewer the focused comparison directly; no installation prerequisite. |

## Audit of this proposal

Three agents independently reviewed the initial proposal with separate remits:

| Review | Finding and revision |
| --- | --- |
| Mathematical safeguards | An unfinished characterization could block its own proof. Clarified that its independently reviewed target can be proved while dependent claims remain pending. |
| Compute cost | No necessary cost fix found. Tightened the early audit's scope to “Compare the mathematics” so later proof-evidence instructions do not trigger premature builds or axiom probes. |
| User experience | Mandatory routing could break partial installations. Added a direct-review fallback, a concrete meaning of exploration, and autonomous repair of findings. |

Focused rechecks cleared the mathematical and compute findings. The UX reviewer's
final clarification, explicitly withholding a pass for unresolved semantics in
the standalone fallback, was incorporated verbatim. All actionable findings have
been addressed. The audits assess instructions and scenario behavior, not
executed Lean proofs or measured performance. Three reviewers for this proposal
do not imply three reviewers for each future statement.
