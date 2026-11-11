# Delegate a bounded task to a Codex worker

Read this when the coordinator assigns work to a Codex worker (Open Math OS,
Luna, Sol or Astra) or needs to inspect subscription quotas. Use the assigned role's model
and effort and the shared limits in [the Claude profile](claude-profile.md).
A Codex worker occupies one Codex slot until it
finishes or its interruption is confirmed. Do not start it when a cap is full.

This route needs a logged-in Codex CLI. Check `codex exec --help` for the
installed options before the first launch; the bundled scripts were written
against Codex CLI 0.165.0. The examples below set `SKILL_DIR` to this skill's
installed directory: `.claude/skills/lean-orchestrator` for a project
installation, `~/.claude/skills/lean-orchestrator` for a personal one. Use an
absolute path when the command runs from another directory.

## Authorization for external work

Codex runs locally but sends its inputs to OpenAI, or, with
`--provider openmathos`, to Open Math OS and the model vendors it routes to.
Authorization for one provider does not cover the other; apply the rule of the
[main skill](../SKILL.md#coordinate-mathematical-work). A public paper does not
establish permission to send private local revisions. Supply only the material
the task needs, never credentials, unrelated private files or other projects'
material. After a denial, do not bypass it: report it and keep the work with
Claude or pending.

## Check the project once

Before the first launch in a project:

- Codex refuses to run outside a Git repository it does not trust, before any
  model call. Prefer a Git project. Pass `--skip-git-repo-check` to the
  launcher only for a non-Git project the user has explicitly approved.
- Workers load the user's `~/.codex/config.toml`, including its MCP servers,
  and the global `~/.codex/AGENTS.md`. Check that nothing there conflicts with
  the brief; the launcher's `--ignore-user-config` skips the configuration file
  when needed.
- If Claude Code's own command sandbox is active, a `codex exec` launched from
  it nests Codex's macOS sandbox inside Claude's and may fail. Run one short
  read-only launch first and report a failure rather than weakening either
  sandbox without the user's decision.

## Prepare one short brief

Keep one directory per task, for example `.orchestration/<task>/` at the Lean
project root, ignored by Git, holding `brief.md`. The launcher creates a fresh
`attempt-<n>/` subdirectory for every attempt, so an earlier attempt's result or
exit status can never be mistaken for the current one. Use an existing task
note when the project has one.

Include the exact Lean target and graph node, source passages or paths, usable
inputs, owned files, the frozen statements and their files, relevant project
rules verbatim, verified progress, failed approaches, the validation command,
the stop condition and the expected handoff. Codex reads the project's
`AGENTS.md` but not `CLAUDE.md`: repeat in the brief every project rule and
frozen statement the task depends on. Frozen statements are read only, byte for
byte; the brief states where the proof is written, following the project's
sealing protocol, and which proof bodies the task owns. A registered hole is
filled with proof text only: no command such as `local instance`,
`notation`, `attribute`, or `open` and `set_option` without `in`, anywhere in
the fill, and no comment or string left open. Helpers go in an owned helper
module, where instances and notations are declared `local`. Instruct the worker not
to spawn agents, launch another model process, change a frozen or protected
statement, or edit outside its owned files. Name the skill to use, such as
`lean-workflow`, rather than pasting the collection. Request a compact final
message: changed files, progress, failed approaches, remaining obstacles, and
checks actually run with their results, pointing to long outputs by path. End it
with a one-line comment on the model or effort only if they visibly hindered
the task; do not ask which model and effort it ran with, since it cannot tell
and the launcher records them. The worker does not run `freeze_check.py`: the
coordinator runs `check` at integration. The worker never changes the Lake configuration or anything under
`.lake/packages`.

List the local tools the task may use, taken from the setup's
[tool list](claude-profile.md#campaign-phases), with absolute paths for those
off the worker's `PATH`: for example `rg` for searching Mathlib, or PARI/GP to
test a candidate counterexample numerically before proving it. Name only the
tools relevant to the task, never the whole list.

**Compilation slots.** Before the launch, the coordinator reserves the
compilation the task may need, within the profile's caps and any stricter
project rule, and writes it in the brief as a bounded sequence of pre-granted
checks: for example, one targeted `lake build <Module>` at a time on the owned
modules, at most a stated number of times. Do not ask Codex workers for `nice`:
Codex's `workspace-write` sandbox refuses to change process priority
(`setpriority: Operation not permitted`); the compilation caps bound the load
instead. The worker runs no other
build, in particular no whole-project build, and returns any further check it
needs for the coordinator to run. The reservation lasts until the attempt has
finished or its cancellation is confirmed. A build waiting on a project compile
gate is expected, not a hang.

For an audit by the Sol reviewer, as second auditor of a main result or as
fallback, state that it is read-only, provide
paths to current Lean-produced elaborated types and relevant definitions with
the commands that produced them, and request findings with source and Lean
references. Missing or stale required evidence makes the review incomplete;
the reviewer returns a request for it.

For an upgrade to Sol or an exceptional mission, include the effort,
deliverable, return conditions, and the prior attempts and diagnosis from the
[escalation rules](claude-profile.md#bounded-escalation-checkpoint). The worker
must not wait for a human reply: at a return condition, it preserves useful
progress and returns its diagnosis.

## Launch with the bundled launcher

From the Lean project root, with `brief.md` written, run the launcher in the
foreground of one background command of the coordinator's shell tool, so the
coordinator is notified when it exits instead of polling:

```sh
SKILL_DIR=.claude/skills/lean-orchestrator
python3 -I "$SKILL_DIR/scripts/codex_worker.py" launch \
  --task-dir .orchestration/luna-node12 --model gpt-6-luna --effort xhigh
```

In Claude Code, this means the Bash tool with `run_in_background: true` and the
launcher as the command itself. Do not add `&`, `nohup` or `setsid`: a detached
launcher returns at once and sends no notification. If a worker was detached
anyway, wait for its `exit-status` file with one background `until` loop rather
than checking by hand.

The launcher creates `attempt-<n>/` and runs `codex exec` in its own process
session, in the current directory or the one given by `--cd`, with `--json`, `--disable multi_agent` and `--disable multi_agent_v2`
(no subagents), and `--sandbox workspace-write` by default. In the attempt
directory it writes:

| File | Content |
| --- | --- |
| `brief.md` | Copy of the brief used |
| `process.json` | Command, working directory, PID, process group and start time, for identity checks |
| `events.jsonl` | Codex's JSONL event stream (stdout only) |
| `stderr.log` | Codex's standard error, kept out of the event stream |
| `result.md` | The worker's final message |
| `exit-status` | The worker's exit code, written atomically when it ends |
| `settings.json` | Requested and observed model and effort, and token usage, from the Codex session log |

The launcher exits with the worker's own code (128 plus the signal number after
a signal), so the notification is faithful. Its own codes are 124 at the time
limit, 75 at a quota floor (Open Math OS, or every Codex account), 2 when a check before the start
fails, and 126 or 127 when the Codex executable cannot run.

For a Sol upgrade, use `--model gpt-6.1-sol --effort medium`; for an Astra
research task, `--model gpt-6-astra --effort high`. For a read-only audit, add
`--sandbox read-only`. Some setups instead run Codex in "yolo" mode;
the launcher's `--dangerously-bypass-approvals-and-sandbox` removes the sandbox
and all approvals and is used only on the user's explicit choice, on a
dedicated machine or checkout. If the sandbox blocks a needed Lean or Lake
operation, report the limitation rather than bypassing it silently.

Give workers disjoint owned files. When more than one worker compiles at the
same time and the project has no compile gate, give each compiling worker its
own worktree, so that concurrent builds never share `.lake` outputs.
Worktrees remain subject to any project rule limiting compilations, such as
one compilation at a time for the whole project. Workers that do not compile
can share the main checkout.

**Worktree recipe.** A new Git worktree has no `.lake`, and a copy that changes
file dates makes Lake rebuild everything, Mathlib included. Tested on macOS
with APFS:

```sh
git worktree add -b wt-node12 ../wt-node12 HEAD
cp -c -R -p .lake ../wt-node12/.lake
(cd ../wt-node12 && lake build --no-build Project.Module)
```

`cp -c` clones the files without copying their data and `-p` keeps their
dates; the last command exits with 0 when nothing needs rebuilding. Elsewhere,
use the file system's equivalent, such as `cp -a --reflink=auto` on Linux, and
check the same way. A lighter variant links `.lake/packages` to the main
checkout's and rebuilds only the project's own modules; count that rebuild
against the compilation caps. Launch the worker in its worktree with
`--cd ../wt-node12`; the task directory stays in the coordinator's checkout.

By convention in this setup, the coordinator makes the integration commits:
it reviews the diff, commits it on the worktree's branch, merges it with
`git merge --no-ff`, recompiles, and removes the worktree and its branch once
the node is sealed. Briefs tell workers not to commit; in the default
`workspace-write` sandbox they could not anyway, since a worktree's Git data
lies outside their writable directory.

Workers are child processes of the coordinator's session: closing or losing
that session can stop them. Keep the machine awake for the whole campaign with
`caffeinate`, as described in the [profile](claude-profile.md#apply-the-settings).

## Choose the Codex account

With several Codex accounts of your own, used within each provider's terms
(the choice spreads work over each account's own limits and bypasses none),
log each in under its own `CODEX_HOME`
(`CODEX_HOME=~/.codex-work codex login`) and list them in
`~/.config/lean-orchestrator/codex-accounts.json`, with each account's
allowance relative to the others as `weight`:

```json
{"accounts": [{"name": "personal", "codex_home": "~/.codex-personal", "weight": 1},
              {"name": "work", "codex_home": "~/.codex-work", "weight": 2}],
 "floor_percent": {"five-hour": 5, "weekly": 10}}
```

Then every launch without `--provider` reads all accounts first and runs the
worker under the chosen account's `CODEX_HOME`. With `--account auto`, the
default, it chooses, among the accounts with no server block and every window
at or above its floor, the largest weight × (smallest headroom above a floor,
in percentage points), ties going to the earlier weekly reset; `--account
NAME` uses that account if it qualifies. When none qualifies the launcher
exits with 75 and launches nothing. A `--resume` runs under the account whose
`sessions/` folder holds the session, since a session cannot move between
accounts, and exits with 75 if that account is below a floor. `settings.json`
records the account and its reading under `codex_account`. Without the file,
the launcher uses the default `CODEX_HOME`, as before.

The accounts' folders keep their own `config.toml`, MCP servers and
`AGENTS.md`; keeping them without either makes the accounts behave alike.
`codex_quota.py --all` reads every account; `--choose` also prints the one a
launch would use.

## Use Open Math OS models

`--provider openmathos` routes the worker's model calls to Open Math OS
(`https://os.openmathmodel.org/v1`, Responses API) instead of the logged-in
OpenAI account. The launcher defines the provider on the command line, so the
user's `config.toml` is unchanged and `--ignore-user-config` still applies.
Everything else is identical: attempt directory, sandbox, notification,
cancellation and the confirmed model and effort in `settings.json`, which also
records the requested provider.

- The user creates a **Model API** key (`nuc_ak_…`) in their Open Math OS
  account and stores it in the macOS Keychain under the service name
  `OPENMATHOS_API_KEY` (`security add-generic-password -a "$USER" -s
  OPENMATHOS_API_KEY -w`, which prompts for it), or exports it under that name.
  The launcher uses the environment variable when set, otherwise the Keychain
  item, and passes the key only to the worker's environment; it refuses to
  start when neither exists. Never ask for the key in chat, write it to a file
  or pass it on a command line.
- Model identifiers have the form `vendor/model`, such as
  `moonshotai/kimi-k3.1-pro`, the profile's routine default; the current list
  is at `https://os.openmathmodel.org/v1/models` with the key. Efforts are
  model-specific: Kimi accepts `low`, `high` and `max` only. Request
  an effort the model supports, and report a mismatch in `settings.json`.
- Model calls count against the user's Open Math OS team quota, not the Codex
  or Claude subscriptions. `codex_quota.py` does not read it.
- **Quota floor.** The launcher reads that quota with the bundled
  `openmathos_quota.py` before starting, and every `--quota-poll` minutes (5)
  while the worker runs. It launches nothing, or stops the worker and its
  builds as `cancel` does, when less than 5% of the team's weekly quota remains,
  or when the quota cannot be read (at launch, or three readings in a row
  while running; `--quota-poll` must be positive). It then exits with 75 and records the readings and the
  reason under `openmathos_quota` in `settings.json`. The reading needs the
  Platform key `OPENMATHOS_PLATFORM_KEY`, in the environment or the Keychain:
  without it no Open Math OS worker starts. Lower the floor with
  `--floor-percent` only on the user's instruction. A worker stopped at the
  floor keeps its worktree; resume its session once the quota is back above
  the floor, or move the task to Luna as the profile's
  [quota reserves](claude-profile.md#quota-reserves) say.
- Claude Code's auto mode may refuse the first launch, since it sends project
  material to a new provider. Do not work around a refusal: ask the user to
  allow the launch, for instance with a project rule in
  `.claude/settings.local.json` such as
  `Bash(python3 -I .claude/skills/lean-orchestrator/scripts/codex_worker.py launch * --provider openmathos *)`.

```sh
python3 -I "$SKILL_DIR/scripts/codex_worker.py" launch \
  --task-dir .orchestration/omm-node12 --provider openmathos \
  --model moonshotai/kimi-k3.1-pro --effort high --max-minutes 45
```

`--max-minutes` stops the worker and its builds when the limit is reached, as
`cancel` does, and the launcher then exits with 124 and records
`time_limit_reached` in `settings.json`. The profile requires it for every Kimi
attempt, since Kimi can loop on a no-op; it is available for any worker.

A 401 response naming `nuc_ak_` means the key is missing, invalid or not a
Model API key, and a 429 or other refusal means the quota or service is
unavailable; report it and route the task to Luna within the Codex reserves or
keep it pending.

## Wait and follow up

The launcher's exit is the completion signal. After a resume or compaction,
inspect an attempt instead of trusting memory:

```sh
SKILL_DIR=.claude/skills/lean-orchestrator
python3 -I "$SKILL_DIR/scripts/codex_worker.py" status --task-dir .orchestration/luna-node12
```

It reports `finished` with the exit code, `running` when the recorded process is
still the same one (same command and start time), `interrupted` when there is
no `exit-status` and the process is gone or its PID was reused, or `unverified`
when the attempt cannot be tied to a live process, which calls for a check by
hand. An interrupted
attempt is unfinished: continue from a handoff brief in a new attempt.
`tail` on `events.jsonl` shows live progress when needed.

The session id is the `thread_id` of the first event in `events.jsonl`. To give
the same worker a follow-up, such as the output of a coordinator-run check or a
revised brief, write it to a file and launch a new attempt with
`--resume <SESSION_ID> --brief <file>` and the same model, at the effort the
profile sets for that follow-up (`low` for a well-located repair by an Open
Math OS worker, the original effort otherwise). The
launcher then runs `codex exec resume`, which accepts no `--sandbox` option: it
passes the sandbox as `-c sandbox_mode=...` instead. For a mid-task message to
a running session, `codex queue --thread <SESSION_ID> --message '...'` may be
available; verify it with the installed client before relying on it.

## Collect and hand off

Check the exit code, the final message in `result.md`, and whether the
requested result was actually produced. A zero exit code or a success message
does not replace review of the diff and Lean checks: review every diff and run
the target checks before integration. A worker usually cannot tell which
model and effort it ran with, and `events.jsonl` does not record them: the
launcher reads them from the Codex session log (under the account's
`CODEX_HOME`, by default `~/.codex/sessions/`) when the attempt ends, writes them to `settings.json` in the
attempt directory with the token usage, and flags a mismatch with the
requested model or effort. For a resumed session it reads only the part of the
log this attempt wrote, so a resume at another effort is not a mismatch. The usage is the Codex session's total when the
attempt ended, also after a cancellation; a resumed session keeps counting, so
an attempt's own usage is the difference with the attempt it resumed. Missing values remain
unknown. Add these confirmed settings to the coordinator's
[one-line record](claude-profile.md#settings-report) of the attempt, noting any
mismatch with the launch, for the coordinator's next report to the user. Then release the task's
slots and file ownership.

To cancel, always use the launcher, not a signal to a remembered PID:

```sh
SKILL_DIR=.claude/skills/lean-orchestrator
python3 -I "$SKILL_DIR/scripts/codex_worker.py" cancel --task-dir .orchestration/luna-node12
```

It checks the process identity first, then sends `TERM` to the worker's
process group and to every descendant, including builds that a tool started in
their own session, then `KILL` after a grace period. It exits with 0 only when
none of those processes remain, with 2 and the list of survivors otherwise, and
with 3, signalling nothing, when the attempt is `unverified`: no process
record, or a live process that is not provably the recorded one. Release compilation slots and files only after exit 0;
after 2 or 3, inspect the reported processes and ask the user before stopping
anything not provably part of the attempt. If the launcher and
the worker were both killed abruptly, descendants that left the worker's group
can no longer be traced: check for remaining `lake` or `lean` processes in the
project before reusing the slot. Stopping the background command through the
coordinator's tool also stops the worker, but use `cancel` when the launcher
may already be gone. Preserve outputs and edits; never terminate unrelated
processes.

## Read subscription quotas

Use this at the quota checkpoints in the
[Claude profile](claude-profile.md#quota-reserves). Neither reading calls a
model or consumes quota.

**Codex.** Run the bundled script, with an absolute `SKILL_DIR` when the
command runs outside the project:

```sh
SKILL_DIR=.claude/skills/lean-orchestrator
python3 -I "$SKILL_DIR/scripts/codex_quota.py" --json
```

With an accounts file, use `--all` (or `--choose`) to read every account.

The script starts `codex app-server`, sends only `initialize`, `initialized`
and `account/rateLimits/read` over JSON-RPC, and prints each limit's windows
with used and remaining percentages, window duration, reset time in local time,
and the observation time. It also reports `server_block`, true when the server
refuses ordinary usage (`ordinaryUsageAllowed` false), a spend control is
reached, or a rate limit is reported as reached on any limit of the account;
the coordinator then launches no Codex work, even if the reached limit does
not obviously pay for the task. It never starts a thread or
turn, prints no authentication data, and never uses a rate-limit reset credit.
It needs a Codex CLI logged in with ChatGPT; an API-key login has no
subscription windows. `app-server` is marked experimental in the CLI: if the
script fails, read the latest `rate_limits` event in the newest file under
`~/.codex/sessions/`, whose event timestamp is the observation time and which
is only as fresh as the last Codex session, or ask the user for `/status`.

**Claude.** In the Claude desktop app, use its usage tool, which reports the
plan's five-hour, weekly and model-specific windows with percent used and reset
times. In a terminal session, the reading depends on the user's `/usage`: ask
for it at check-ins, and report that the Claude reserves cannot be checked
before each wave of launches in that setting.

| Reported allowance | Meaning |
| --- | --- |
| Claude five-hour limit (`Current session`) | Shared five-hour subscription window |
| Claude weekly, all models | Shared weekly subscription window |
| Claude model-specific weekly windows | Further limits when they apply to Opus or Sonnet |
| Codex window of 10080 minutes | Weekly window of the Codex account paying for Luna, Sol and Astra |
| Codex window of 300 minutes, if reported | Five-hour window of that account |

Per-session cost, duration and token counters are not subscription-window
readings. Record the observation time, window labels, percentages used, reset
times and timezone in the existing campaign notes when needed for a scheduling
decision, and convert used percentage to remaining allowance. Resolve relative
reset labels against the observation time; an ambiguous reset remains unknown.
Keep missing or stale readings unknown and apply the profile's fallback rules.
A reading establishes observability, not automatic enforcement of the reserves.
