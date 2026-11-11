---
name: lean-orchestrator
description: Coordinate parallel or long-running Lean paper formalization from Claude Code, with Sonnet subagents, optional Claude workers and background Codex or Open Math OS workers, without losing result coverage, statement fidelity, or control of shared builds. Use when multiple proof tasks, agents, or integration branches need coordination; not for a single local proof.
license: CC-BY-4.0
---

# Coordinate mathematical work

Read the project's plan and rules, the declared paper scope, and its coverage
record or `FORMALIZATION_REPORT.md`. Throughout, reuse the project's existing
records, protocols, gates and authorizations instead of creating parallel
ones. Keep the main mathematical interface and integration decisions with one
owner. This skill creates no exception to the project's axiom, draft or
frozen-statement policy.

As the coordinator, read the [Claude profile](references/claude-profile.md) at
setup and at each resumption: roles, models, efforts, caps, campaign phases,
escalation and quota rules. Read [the Codex worker guide](references/codex-worker.md)
before delegating to Kimi, Luna, Sol or Astra, and
[the VM worker guide](references/openmathos-vm.md) before running a node on
the Open Math OS VM. Workers follow their brief and do not load these
references.

Each external route needs the user's authorization for that provider, project
and material: reuse one given in the conversation, in the project's
`CLAUDE.md` or `AGENTS.md`, or as a standing authorization in
`~/.claude/CLAUDE.md`; do not ask again within its scope, and state at setup
which one you rely on. Installing the skills authorizes nothing.

When publication is intended, settle interface and dependency choices against
the current artifact requirements before assigning dependent proof work
(`lean-project-architecture`, `lean-publication`, or the
[official submission standard](https://github.com/PalomarRegistry/PalomarPolicy/blob/main/CONTRIBUTING.md)).

## Split by actual independence

Prioritize every main result and its dependencies; keep the other in-scope
claims as completion obligations. Delegate substantial independent proofs,
searches, explorations or reviews when the benefit justifies the duplicated
context; aim for fewer tokens per verified result, not lower elapsed time
alone. Do not assign dependent tasks before their shared API is settled.

Before substantial proof work, the relevant main statements and shared
interfaces must pass an independent statement-fidelity review
(`lean-statement-audit`, or one reviewer who did not author the declaration
comparing source, elaborated statement and definitions). A campaign following
the profile's [phases](references/claude-profile.md#campaign-phases) also
needs the user's recorded approval of key statements.

Give each worker the exact target, source location, owned files, usable
inputs, pre-granted checks, relevant project rules verbatim, verified progress,
failed approaches and the condition for handing back. Delegate a coherent
batch, not one call per micro-step. Point to artifacts instead of copying
histories; ask for a compact result with long logs in files. Only the
coordinator starts agents. Use disjoint owned files or worktrees; never trust a
worker's summary as proof that its code is correct.

Workers choose proof routes autonomously within the requested mathematics and
report substantive departures and blockers. The coordinator resolves
uncertainties from the source and prior decisions, asks only what blocks
faithful completion, and continues independent work meanwhile. If the user
requests no questions, record blockers and leave dependent work pending
without guessing.

## Keep builds coordinated

Respect the profile's compilation caps and any stricter project rule; use the
project's compile gate when it has one. Native subagents and background
workers have no reliable mid-task channel, so their compilation is pre-granted
in the brief as a bounded sequence of targeted checks; anything more they
return for the coordinator to run. A live build is not permission to delete
caches, kill jobs or start a conflicting build. Keep the inputs of a running
compilation stable. `lake env lean` does not refresh imported artifacts: use
the project wrapper or `lake build`.

At handoff, require changed files, the validation command, its result and the
path of its output. Review each diff and run target checks before integration,
reusing outputs only while their sources, dependencies, toolchain and targets
are unchanged; rebuild consumers when interfaces change. Batch related axiom
queries after a coherent integration group.

When a confirmed counterexample refutes a shared assumption, record the
witness, the refuted statement and the evidence, and notify only affected
workers; keep conjectures and numerical indications apart from confirmed
refutations.

## Track mathematics rather than ceremony

Update the coverage record at coherent milestones, not per helper; put
exposition remarks in `MANUSCRIPT_RECOMMENDATIONS.md`. Distinguish proved
results, conditional helpers, explored alternatives and open obligations.
Never add an obstruction as a new hypothesis of an advertised theorem.

For a paper campaign, inventory the declared scope independently of the
implementation, or reuse an inventory checked against the same source. Reuse
statement-fidelity findings while source, elaborated statements and semantic
dependencies are unchanged; after a proof-route change, refresh the affected
correspondence. Self-review never replaces a required independent review; none
is required per helper. Before claiming whole-paper completion, scan the scope
for omitted results. Agent consensus or a complete-looking table never
substitutes for kernel verification.

Finish when the scope is verified, the user stops, a global limit is reached,
or no useful authorized work remains. A provider-specific limit blocks only
that pool. On a budget limit, stop or interrupt delegated work, keep its
useful state, and launch no replacement. Report changed results, checks, route
decisions and remaining work, with the profile's
[settings report](references/claude-profile.md#settings-report) at setup,
resumption and milestones, and the
[retrospective](references/claude-profile.md#campaign-retrospective) at the
close. Unknown external usage is unknown, not zero.
