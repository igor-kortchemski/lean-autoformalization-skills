# Claude coordinator profile

The editable configuration of the Claude Code coordinator: roles, models,
efforts, caps, campaign phases, escalation and quota rules. Read it when
setting up or resuming a campaign. It is the single source of these defaults;
the evidence behind them is summarized in the package's `TESTING.md` (not
installed with the skills). Explicit user choices and stricter project, client
or machine limits take precedence. Give workers only the settings their brief
needs.

## Editable settings

| Role | Route | Model | Effort |
| --- | --- | --- | --- |
| Coordinator | Claude Code session | `claude-opus-5-5` | `xhigh`; `high` allowed in phase 5 (see [Coordinator effort](#coordinator-effort)) |
| Audits, read-backs, coverage, documentation drafts; cleanup, repair and blueprint (one editor at a time) | Native subagent | `sonnet` | agent default |
| Long Claude task (a batch of audits, cleanup, blueprint, documentation), where the user authorized it | A background Claude worker launcher, not included (see [Claude workers](#claude-workers)) | `sonnet` | agent default |
| Routine Lean, local (default where Open Math OS is authorized) | `codex_worker.py --provider openmathos --max-minutes 45` | `moonshotai/kimi-k3.1-pro` | `high`; `low` for a resumed repair |
| Routine Lean, local (fallback) | `codex_worker.py` | `gpt-6-luna` | `xhigh` |
| Hard node or shared blocker; second audit of main results; audit fallback | `codex_worker.py` (read-only sandbox for audits) | `gpt-6.1-sol` | `medium` |
| Lean on the Open Math OS VM, where the user authorized that channel | `vm_worker.py` ([unofficial](openmathos-vm.md)) | `moonshotai/kimi-k3.1-pro` | `high`; `low` for a repair |
| Optional research before the campaign | `codex_worker.py`, then an Opus subagent audits it | `gpt-6-astra`, then `opus` | `high` |

| Cap (four-core machine, 24 GB) | Default |
| --- | ---: |
| Processes compiling or elaborating Lean at once, any agent, including auditors' probes, an open editor's Lean server and each document open in Lean Beam | 4, of which 1 heavy (a full build or a build of unknown cost) |
| Codex workers (Kimi through Codex, Luna, Sol, Astra) | 3, of which at most 2 Sol |
| Native Sonnet or Opus subagents | 4, at most 1 editing project files |
| Open Math OS VM workers, across all of the user's campaigns | 4 (`vm_worker.py` refuses a fifth, exit 9) |

These are ceilings, not targets: launch only useful independent work; a small
task stays with the coordinator. Claude workers obey their launcher's own
ceilings and count toward the compilation cap when they compile. On a
many-core server, start from about a third of the cores for heavy builds and up
to 8 Codex workers, then adjust after observation. State the effective
settings at setup.

## Apply the settings

Start the coordinator from the Lean project directory with
`caffeinate -is claude --model claude-opus-5-5 --effort xhigh`; in the desktop
app, use its model and effort controls and run `caffeinate -is` in a terminal
for the whole campaign. Workers are child processes of the coordinator's
session: keep it open while they run. Reading this file does not change a
running session.

Before using this profile on an existing project, read its instructions. If
they designate another coordinator or limit Claude to bounded reviews, full
coordination by Claude needs the user's explicit agreement and an aligned
project rule.

Apply the model and effort explicitly at every launch:

- **Native subagents:** the Agent tool with `model: "sonnet"` (or `"opus"`),
  or the definitions in [`../assets/agents/`](../assets/agents/) copied to the
  project's `.claude/agents/`. They do not launch further agents.
- **Codex workers** (Kimi, Luna, Sol, Astra): the [Codex worker guide](codex-worker.md),
  one background launch of `scripts/codex_worker.py` per attempt, never
  detached with `&` or `nohup`.
- **VM workers:** the [VM worker guide](openmathos-vm.md).

Report an unavailable model or setting rather than substituting it silently.
Kimi accepts only `low`, `high` and `max`. Never run a second coordinator.

### Coordinator effort

The coordinator runs at `xhigh` for phases 1 to 4 (blueprint, dependency
graph, key statements, freeze): it interprets the source and writes the
statements and interfaces, where a mistake costs a versioned successor and the
work built on it. Once the key statements are frozen, phase 5 may run at
`high`: dispatching dependency-ready nodes, reviewing diffs and sealing are
short turns, and every seal is still checked by recompilation, axioms,
`freeze_check.py` and an independent re-audit. Return to `xhigh` to arbitrate a
blocker, diagnose a node after the escalation checkpoint, write or revise a
statement (a new key statement or a versioned successor), and for phase 8.

The coordinator cannot change its own effort: it proposes the switch in its
settings report, and the user applies it with the client's effort control or by
resuming the session with `--effort high` or `--effort xhigh`. Record the
effort of each stretch in the plan, so that the token ledger, which counts
tokens per effort, shows what `high` saved.

## Assign the roles

**Routine nodes** (bounded proofs of dependency-ready nodes, Mathlib searches,
repairs, mechanical preparation) go to Kimi at `high` through Codex where the
user's Open Math OS authorization covers the project and the material.
Launch every Kimi attempt with `--max-minutes 45`: it can loop on a no-op, and
exit 124 is a failed attempt. Fall back to Luna at `xhigh` when Open Math OS is
not authorized, refuses requests or is below its floor, and for a node on which
two Kimi attempts failed.

**The VM** takes a self-contained node when local compilation is saturated,
when a node needs many builds, or for a hard node when the Codex quota is
short. Packaging has a cost: use it for nodes worth packaging. Keep audits,
small repairs and nodes whose dependencies are not yet sealed on the local
machine.

**Upgrade to Sol** within the Sol cap: from the start for a node marked hard,
after the [escalation checkpoint](#bounded-escalation-checkpoint), when a
shared lemma blocks several tasks, or when a routine attempt shows a real
mathematical obstruction. Relaunch the task on Sol from a handoff brief; the
Sol attempt takes the routine worker's slot and returns it when done. Kimi on
the VM at `high` is an alternative for a hard node; do not raise Kimi to `max`,
which is not an escalation.

**Repair** of a routine worker's output goes first to the same worker: resume
its session once with the compiler output (`--resume`, see
[Wait and follow up](codex-worker.md#wait-and-follow-up)), at `low` for a Kimi
worker with a well-located error. If that fails and the fix is local and well
specified, a Sonnet cleans it up. A Sonnet that repaired a proof does not audit
it.

**Audits.** Every audit is done by a reviewer that authored neither the
declaration nor its proof: a Sonnet subagent or Claude worker. The main
results also get one read-only Sol audit at the key-statement phase, so that
another model family checks what the Claude coordinator wrote. Audits are
read-only for maintained files; they may elaborate statements and query axioms
through temporary probes or, when the brief grants them, the Lean Beam tools. A change of provider or account does not make an
author's review independent. If no Claude reviewer is available, use the Sol
audit fallback within the user's authorization; if no independent reviewer is
available, dependent work stays pending.

**The coordinator** keeps source interpretation, the dependency graph, shared
interfaces, integration decisions and the user dialogue. It does not routinely
solve a worker's task again.

Whatever the model, review every diff and compile it before integration.

### Claude workers

This package includes no launcher for background Claude Code workers. Where
one is installed (for example a `claude-workers` skill) and `~/.claude/CLAUDE.md`
or the project authorizes it, use it for long Claude tasks that would otherwise
draw on the coordinator's quota: a batch of audits, the cleanup of phase 7, a
blueprint, documentation. Run such workers only on Claude accounts you hold,
within their terms. Read-only tasks get read-only tools; editing tasks get a
worktree, their own files and only the build commands the brief pre-grants.
Short tasks stay native subagents: they are cheaper to brief and report
directly. Worker usage is not counted by the [token ledger](#token-ledger);
note their attempts in the plan. Without such a launcher, these tasks go to
native subagents.

## Campaign phases

Reuse the project's existing equivalent records instead of creating parallel
ones.

**At setup:**

- Ask the author once whether the paper is published in a journal, on arXiv
  only or submitted, or not distributed, and record it in the plan and the
  formalization report; for a published paper, also ask for the reference,
  DOI and PDF of the published version. If the user asked for no questions,
  record the status as unknown and use `MANUSCRIPT_CORRECTIONS.md` at phase 8.
- List the local tools once with
  `python3 -I <SKILL_DIR>/scripts/tool_probe.py --markdown`, from the project
  directory, and record the table in the plan. Call tools that are installed
  but not on `PATH` by absolute path, in commands and briefs. A quick
  numerical check (PARI/GP, Mathematica, Python, nauty's `geng`) before a Lean
  attempt at a suspected counterexample is triage, not evidence. Never install
  a tool or change the user's shell configuration; suggest an install with the
  reason.
- If the tool list shows `lean-beam` and this session has its MCP tools
  (`mcp__lean-beam__…`), the coordinator may use them and grant them in the
  briefs of native subagents, which share its Beam server; background workers
  do not use Beam. Record this in the plan and add `.beam/` to the project's
  `.gitignore`. Before a heavy build or `freeze_check.py` on that checkout,
  call `lean_drop_workspace`, which also ends the subagents' probes, and
  confirm that its Lean processes have exited.
- Register the session for the [token ledger](#token-ledger).

**Phases:**

1. **Research and blueprint**, by default when a first reading suggests a
   hard node: an Astra worker looks for the most formalization-friendly proof,
   an Opus subagent at `high` audits the findings, and a Sonnet writes a
   blueprint. Raise questions about the sources before starting.
2. **Dependency graph.** The coordinator builds the source dependency graph:
   statements are nodes, implications are edges. Mark each node routine or
   hard (a long or delicate argument, missing Mathlib API, or a route known to
   fail). Hard nodes go to Sol from the start.
3. **Key statements.** Write the main theorems and important propositions and
   lemmas as exact final declarations. Have them audited by Sonnet reviewers
   who did not write them, plus one Sol audit for the main results. For each
   main result, obtain a **blind read-back**: a fresh
   [`lean-readback`](../assets/agents/lean-readback.md) subagent states in
   mathematical English what the Lean literally asserts, from the
   `#check @Name` and `#print` of each project definition it rests on, taken
   from a temporary probe or from Beam's `lean_run_at` at the end of a module
   that only imports (an `open` shortens names),
   transitively, without comments or docstrings and with the declaration's name
   replaced by a neutral label; never the source, blueprint or audit. It helps
   the user compare; it is not an audit. Present the declarations with their
   read-backs for approval, record each approval in the project's manifest or
   plan, and check that record before assigning dependent proofs. This is the
   explicit exception to the skills' "no additional user approval" default.
4. **Freeze.** Follow the project's existing freezing protocol if it has one.
   Otherwise:
   - Freeze only approved declarations that are still unproved, with a
     registered `sorry` body; never replace an existing proof by `sorry`. Every
     other `sorry`, axiom or placeholder stays forbidden. Frozen text is read
     only, byte for byte.
   - Right after approval and before any launch, run `freeze_check.py record
     --out <record.json>` with `--holes <file>` for a file whose only permitted
     changes are its registered holes, `--file <file>` for a file frozen whole,
     `--decl <name>` for **every** statement of a frozen file, and
     `--module <module>` for the modules declaring them. It records the
     declarations' types and the definitions they rely on by value (`pp.all`),
     the compiled dependency modules they reach, the Lake configuration and the
     dependencies' sources.
   - Keep the record outside every worktree and the project. Give the user the
     SHA-256 that `record` prints.
   - A hole is filled with proof text only: no command (`local instance`,
     `notation`, `attribute`, `open` or `set_option` without `in`), and no
     comment, string, raw string or `«…»` name left open. Helpers go in an
     owned helper module, with `local` instances and notations. When several
     nodes of one file are proved at once, give each its own helper module
     already imported by that file.
   - A Mathlib bump or any edit under `.lake/packages` makes `check` stop
     before running Lake: it needs the user's approval and a new record.
   - Put shared definitions in their own module; scaffold with targeted
     Mathlib imports, not `import Mathlib`.
5. **Prove node by node.** A node is dependency-ready when all its
   predecessors are `PROVED`. A proved node is **sealed** and marked `PROVED`
   only when: existing proofs are preserved; the export is recompiled;
   `#print axioms` shows no `sorryAx` and no unauthorized axiom;
   `freeze_check.py check <record> --root <tree>` passes and prints the
   recorded SHA-256 (it rebuilds the frozen modules first, so count it as one
   build); and an independent re-audit against the source passes. A result
   resting on a frozen hole or an undischarged hypothesis is never `PROVED` and
   unblocks nothing. When the re-audit finds a hypothesis of a frozen statement
   that the proof does not use, leave the statement unchanged and report it with
   its likely cause (the statement assumes what the source derives; the source
   states a hypothesis Lean does not need; or the result holds without it).
   Record a decisive failed route in the node's note in the plan when it
   happens, not at the next milestone: the route, the exact target, the reason,
   the path of retained evidence, and what would justify trying it again. Keep
   it after the node is proved by another route, and give it to any later
   worker on that node. A failed tactic does not show that a mathematical route
   is impossible.
6. **Check-ins.** The user answers questions, re-approves a rewritten
   statement, or assigns a stronger model to a blocking lemma.
7. **Cleanup**, by one Sonnet or Claude worker, then an independent audit:
   - dead code: before removing a declaration, check the result inventory, its
     public uses and the identities Comparator needs; remove automatically only
     private fragments whose abandonment is established; report unused public
     declarations; recompile consumers after each removal;
   - elaboration: measure, apply `lean-elaboration`'s supported improvements,
     measure again (delete the measured modules' outputs under `.lake/build`
     first: Lake compares hashes, so `touch` does not force a rebuild);
   - frozen and advertised statements stay unchanged.
8. **Corrections to the paper.** Once coverage is reconciled, have each
   difference classified as an error in the paper audited by a Sonnet that did
   not record it (`lean-statement-audit`'s correction audit), keep the confirmed
   ones, and draft: an erratum from
   [`ERRATUM.tex`](../../lean-workflow/assets/ERRATUM.tex) for a journal
   paper (locations in the published version, `latexmk -pdf`);
   [`MANUSCRIPT_CORRECTIONS.md`](../../lean-workflow/assets/MANUSCRIPT_CORRECTIONS.md)
   for a paper on arXiv only or submitted; nothing beyond
   `MANUSCRIPT_RECOMMENDATIONS.md` for a paper not distributed. Close
   `CITED_WORKS_ERRATA.md` the same way under the stricter checks for cited
   works. With no error found, say so and create no file. These are drafts for
   the user: never send them to a journal, an archive, a coauthor or a cited
   work's authors.
9. **Publication.** Hand the final tree and evidence to `lean-publication`.

If a frozen declaration turns out to be wrong, stop the affected branch, obtain
the user's ruling, create a versioned successor, re-anchor the graph and
invalidate dependent proof and audit status. Never repair a frozen statement in
place. When the source itself is wrong, record it as an error in the paper for
phase 8.

## Bounded escalation checkpoint

After two materially different unsuccessful approaches to the same obligation
(minor tactic variations do not count), the worker stops and returns a
diagnosis: mathematical obstruction, unsuitable shared interface, or
elaboration problem, with the target, approaches tried, reusable progress and
compiler evidence. The coordinator chooses: revise the strategy or interface,
upgrade to Sol, assign a Sonnet, request a performance diagnosis, or run one
exceptional mission. Workers never launch their own replacements.

### Exceptional effort

Diagnose before raising effort: missing dependencies, unfamiliar APIs, suspect
statements and saturated compilation need investigation, not effort.

| Situation | Next step |
| --- | --- |
| Difficult code with an identifiable strategy | Sol, `medium` |
| Kimi at `high` stops on a mathematical obstruction | A focused coordinator analysis as a follow-up in the same session, then Sol |
| Sol `medium` makes no progress on a central lemma with a plausible strategy | Sol `high` or `xhigh`, one bounded mission |
| Representation or architecture blocking several tasks | The coordinator itself |
| Identified reasoning limitation with a plausible gain | Sol `max`, after [human arbitration](#human-arbitration) |

At most one exceptional mission runs at a time. Its brief defines the
obligation, the deliverable and the return conditions (deliverable ready,
prerequisite missing, avenues exhausted). Renew expensive work only for a
materially new approach; useful progress is a validated lemma, a reproduced
obstruction, a usable representation or a route ruled out for a precise
reason.

### Human arbitration

Ask the user for a concrete decision when:

- a source ambiguity or missing assumption persists after examination, or a
  choice would change the mathematical content or declared scope;
- a key statement needs approval, or a frozen statement a versioned successor;
- an `xhigh` mission finds no usable avenue (before trying `max`), or a `max`
  attempt makes no progress (before another expensive attempt).

Keep the request short: blocker and why it matters, approaches tried, reusable
results, one question with a recommendation. Suspend only the affected branch.
Silence is not approval. If the user prohibited questions, record the blocker
and keep dependent work pending. Keep one note per blocked obligation and read
it after a resume or compaction.

## Settings report

Keep one line per attempt in the plan: role, model and effort requested and
confirmed (from `settings.json` for a Codex worker, from the launch otherwise),
wall time, outcome, and whether it needed repair. Workers comment on their
model or effort only when it visibly hindered the task.

At setup, resumption and milestones, tell the user in a few lines: the active
agents per role with confirmed settings, any discrepancy with this profile,
the compilation load, and the latest quota readings or their absence. Apply
adjustments this profile allows (a Sol upgrade, fewer workers under load) and
say so; changes to its defaults are proposals for the user.

## Token ledger

At setup and at each resumption in a new Claude Code session, register the
session:

```sh
SKILL_DIR=.claude/skills/lean-orchestrator
python3 -I "$SKILL_DIR/scripts/token_ledger.py" register --project .
```

It reads the session id from `CLAUDE_CODE_SESSION_ID`; elsewhere pass
`--session <id>`. Add `--end` when a session leaves the campaign. At milestones
and at the close, `token_ledger.py report --project .` prints one row per agent,
model and effort, in tokens (it reads the registered transcripts, the Codex
workers' `settings.json` and the VM runs' `usage.json`; it calls no model).
Tokens of different models are not comparable in cost.

## Campaign retrospective

At the close, or when handing over at a resource limit, write one short
retrospective in the plan or report: models and efforts used, verified
results, share of output needing repair per model, Sol upgrades and their
outcome, compilation bottlenecks, the ledger table, and at most three
recommendations for comparable work (observation, suggested adjustment,
scope). Keep missing values unknown; do not infer a general model ranking from
one campaign or launch anything just to write it. Recommendations never edit
this profile by themselves.

Give each recommendation what is needed to act on it later: the installed
skill tag and any local override, the incident and the path of its retained
evidence, the proposed change, and its disposition (proposed, adopted,
deferred with its next evaluation step, or rejected). One reproducible
correctness defect can justify a fix; routing or performance advice needs
observations from comparable work. When a recommendation leads to a change of
the installed skills, link that change here.

A repair rate, if reported, counts each initial candidate with a known first
review once: a repair is a correction needed to meet the original brief, not
optional cleanup or a changed brief; repair rounds, attempts that produced no
candidate, and candidates awaiting review are reported apart.

## Local resources

The local defaults target a four-core Mac with 24 GB of memory. Model
inference is remote, so the limit is Lean compilation: a file importing
Mathlib uses one core and often 1.5 to 3 GB. Get the Mathlib cache
(`lake exe cache get`) before the campaign. Observe one representative build
(`top -l 1 -s 0 | head -12`, `memory_pressure`, `sysctl vm.swapusage`) and
adjust: propose four Codex workers if memory pressure stays normal while
workers often wait for builds; drop to two if pressure turns to warning or
swap keeps growing. Idle workers waiting for a build slot cost quota and add
nothing. Use an existing compile gate when the project has one; never add a
scheduling service.

## Quota reserves

Three pools pay: the Claude subscription (coordinator and native subagents;
Claude workers use their own accounts), the Codex subscriptions (Luna, Sol,
Astra), and the Open Math OS team quota (Kimi through Codex and on the VM).
Check readings at setup, before each wave of launches and at milestones.

| Pool | Reading | Floor: stop new work against the pool below |
| --- | --- | --- |
| Codex, per account | `scripts/codex_quota.py --all` | 5% of a five-hour window, 10% of the weekly window, enforced by `codex_worker.py` when an accounts file exists |
| Claude | the desktop app's usage tool, or the user's `/usage` | 5% of the five-hour window, 10% of a weekly window |
| Open Math OS | `scripts/openmathos_quota.py` (needs `OPENMATHOS_PLATFORM_KEY`) | 5% of the weekly window, enforced by the launchers |

- **Several Codex accounts.** With the accounts file of the
  [Codex worker guide](codex-worker.md#choose-the-codex-account), the launcher
  picks, at each launch, the account with the most headroom above its floors
  weighted by its size, skips accounts that are blocked or below a floor, and
  exits with 75 when none qualifies. A resumed session stays on its account.
  Codex is short only when every account is.
- An account reporting `server_block`: launch nothing on it, whatever the
  percentages. Apply only the windows an account actually reports.
- Unknown reading: let in-flight work finish; launch a new wave against that
  pool only after a reading (for Claude in a terminal, ask the user for
  `/usage` and say the reserve was not checked). Open Math OS workers never
  start without a reading.
- Open Math OS launchers exit with 75 (`codex_worker.py`) or 7 and 4
  (`vm_worker.py`) at the floor or on an unreadable quota: launch nothing more
  on that pool until a reading is back above the floor. Lower the floor only
  on the user's instruction. Without the Platform key, ask the user to store it
  in the Keychain or the environment themselves, never in the chat.
- Never use a rate-limit reset credit without the user's explicit instruction.
  A quota window is not a deadline; respect explicit user budgets.

When one pool is short:

- **Codex** (every account below a floor or blocked): stop Luna and Sol; routine work continues on Open Math OS where
  authorized; hard nodes go to Kimi on the VM, or to a Claude worker or Sonnet,
  or wait.
- **Open Math OS:** stop its workers; route routine work to Luna or leave it
  pending.
- **Claude:** move non-coordinator Claude work to Claude workers where
  authorized, otherwise stop non-audit Sonnet work and use the Sol audit
  fallback; write a resumable handoff and stop before the floor rather than
  losing the coordinator mid-integration.

Read quotas following [the quota procedure](codex-worker.md#read-subscription-quotas).
Token counts and API spending are not subscription-window readings.
