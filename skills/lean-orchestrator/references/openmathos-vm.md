# Open Math OS VM worker

> **Unofficial and unsupported.** `vm_worker.py` drives the VM through the
> Open Math OS web app's own protocol, which is not documented, and reads
> quotas through the Platform API, which is not publicly documented either.
> Open Math OS does not endorse or support this route; it may break or be
> refused at any time. Use it only where the user accepts that risk, within
> Open Math OS's terms, and fall back to the browser or to local workers when
> it fails.

An Open Math OS team has a cloud VM (in November 2026: 4 CPUs, 16 GB of
memory, Lean 4 and Mathlib preinstalled) and a hosted agent that works on it with a shell. A VM
worker is one chat of that agent in an Open Math OS project: it writes and
compiles Lean on the VM, so it uses no Codex quota, no Claude slot and no local
compilation. The coordinator prepares a package, follows the run and
re-verifies the result locally before integration. This differs from the
[Codex worker on Open Math OS](codex-worker.md#use-open-math-os-models), which
only routes a local worker's model calls to Open Math OS and compiles locally.

## When to use it

- A dependency-ready node whose frozen statements and dependencies can be
  shipped as a self-contained subset of the project.
- When local compilation is the bottleneck, or the Codex quota is short: the
  VM run consumes only the Open Math OS team quota.
- For a hard node, Kimi K3.1 Pro at `high` is an alternative to a Sol upgrade.

Not for audits: an audit needs a reviewer that did not author the proof, and a
change of provider does not make a review independent.

## Authorization

Sending project material to the VM, as an uploaded archive, is a separate
channel from Codex workers. An authorization for "Open Math OS through Codex
workers" does not cover it. The VM channel is authorized by a section of the
project's `CLAUDE.md` or `AGENTS.md`, next to the authorization for Codex
workers, with the same material and exclusions, or by a standing authorization
of the user that names this channel. Without either, ask the user before the
first VM run of the project and record the answer in such a section. Never
send unpublished coauthor material without explicit permission. Create each VM
project with **Model training off**; the setting is per project, and
`vm_worker.py` sets and checks it before sending anything.

A section such as the following works; name the project's actual material, and
add any source to ask about first:

```markdown
## Authorization for the Open Math OS VM

At the user's explicit request on <date>, the Claude coordinator is authorized
to run VM workers on the user's Open Math OS team VM, launched with
`vm_worker.py` through the Platform API or, as a fallback, in the browser. It
may upload to that VM, in projects created with model training off, a package
of the material a node needs (<Lean source, compiler and axiom output, project
notes, and the relevant passages of the paper's sources>) and send the worker's
brief; the hosted agent writes and compiles Lean there, and Open Math OS routes
its model calls to the model vendors it uses. Unpublished coauthor material is
excluded unless the user says otherwise. This excludes credentials, unrelated
private files and other projects' material, and does not authorize publication
or unrelated external actions. A run may download, inside its own work
directory on the VM, the Lean toolchain and Mathlib cache the project pins when
the VM's preinstalled ones differ. Each run deletes its work directory on the VM
after its handoff. Reuse this authorization within its scope without asking
again; later user instructions remain binding.
```

Claude Code's auto mode may refuse the first launch of `vm_worker.py` in a
project, since it sends project material to a new provider. Do not work around
a refusal: ask the user to allow the launcher, for instance with a project rule
in `.claude/settings.local.json` such as
`Bash(python3 -I .claude/skills/lean-orchestrator/scripts/vm_worker.py *)`,
written with the path the coordinator actually uses.

## Prepare the package

Build the package from the state a worker would find, never from a later one.
Steps 2 and 3 matter for a replay of a node already solved, where a later
state holds the solution; for a node never solved, the current sealed state is
that state, and they reduce to shipping the frozen statements with their holes
and the owned files as their current stubs:

1. Take the import closure of everything the worker may use (the sealed
   modules, the frozen `Defs` and statements file, finished providers), plus
   the Lake files (`lakefile.toml`, `lean-toolchain`, `lake-manifest.json`) of
   the project and of every local path dependency, without `.lake` or `.git`.
   Include all sealed modules the worker could use, not only those the known
   solution imports.
2. Restore the frozen statements file with its registered holes from the freeze
   record, and the owned provider files as the stubs they were. Every module
   that imports an owned file and was proved later becomes a stub too.
3. Remove every trace of the solution. Check that no shipped file contains a
   proof of the targets, and that no shipped source changed after the
   reference attempt started. Ship guidance without status paragraphs added
   after the fact.
4. Ship the rules file with paths relative to the project root, the
   `lean-workflow` skill, `freeze_check.py` and the freeze record.
5. Precheck locally on a copy, with clones of the local `.lake` caches
   (`cp -cR` on APFS). The stub state must build with exactly the registered
   holes, and `freeze_check` must pass. On the VM, `check` stops before
   running Lake if the dependencies there are not the recorded ones, for
   instance when the preinstalled Mathlib is not a Git checkout at the
   manifest's commit; tell the agent to report that and rely on its build, since
   the coordinator's local check decides.

## Brief

Keep the project's provider brief and add:

- **Setup:** extract the archive under the home directory, then compare the
  preinstalled versions with the project's pins: `lean --version` with
  `lean-toolchain`, and the Mathlib commit with the `rev` in
  `lake-manifest.json`. `/opt` belongs to `root`, so Git needs a
  command-local exception:
  `git -c safe.directory='*' -C /opt/mathlib rev-parse HEAD`. A matching
  version number is not enough; the commit must be identical.
  - **Identical:** reuse the preinstalled toolchain and Mathlib.
    `/opt/mathlib` is a symbolic link to a versioned directory, so copy that
    directory, never the link: in the project, `mkdir -p .lake/packages`, then
    `cp -a "$(readlink -f /opt/mathlib)" .lake/packages/mathlib` (`cp -a` keeps
    file dates), and check that `.lake/packages/mathlib` is not a link
    (`test ! -L`) before anything else. Then `chmod -R u+w
    .lake/packages/mathlib/.lake/packages`, move its packages up with `mv
    .lake/packages/mathlib/.lake/packages/* .lake/packages/`, set each Git
    package's `origin` to the manifest's `url`, check that each `HEAD` equals
    the manifest's `rev`, and check with `lake build --no-build Mathlib`,
    which exits with 0 when nothing needs rebuilding. A command that would
    write through `/opt` is a recipe error: stop and fall back.
  - **Different, or the check fails:** install `elan` in an isolated
    `HOME`/`ELAN_HOME` inside the run's directory and run `lake exe cache get`.

  Then build the statements file to confirm the hole count, and record in the
  log which route was taken.
- **A timing log:** `date -u` at the start, at `setup_done`, at each build (start, end,
  PASS/FAIL) and at each statement proved.
- **Handoff:** copy the owned files and the log into `handoff/` inside the
  project's own folder, the one shown in the app's Files panel. The panel does
  not show the home directory.
- **Cleanup:** after the handoff copy, delete the work directory with
  `rm -rf "$HOME/<dir>"`. A run with the preinstalled route leaves about 7.5 GB
  there and one with the isolated install about 11 GB, on a disk shared by
  every run of the team. The agent's shell tool can cut a command that runs silently
  for about 25 s (`sleep 600` and a loop deleting twelve directories were
  cut, while builds of several minutes were not), so delete one directory per
  tool call.
- **Print and stop:** as the very last step, print each handoff file (`sha256sum`,
  then `cat`, in chunks of 400 lines with `sed -n` above 30,000 bytes), then end
  the turn with no further tool call, not even `true`. The coordinator rebuilds
  the files from `session_history` and checks the SHA-256, so the user downloads
  nothing.
- **Isolation:** the VM is shared by every project of the team and keeps earlier
  runs' files, including solutions. Name one fresh directory under the home
  directory as the only workspace and forbid reading anything else, with two
  exceptions: reading the platform's preinstalled toolchain and `/opt/mathlib`,
  where writing is forbidden, and the project's own `handoff/` folder, which
  the agent creates, writes, and reads back for the final print. Never reuse a
  toolchain or package directory from an earlier run's workspace.

## Launch and follow

Run at most the profile's number of VM workers at once, across all campaigns:
`vm_worker.py launch` refuses a run beyond `--max-vm-workers` (4) while the
runs it launched, from any campaign, are still going (exit code 9, nothing
launched). Each run holds a slot file in `~/.cache/lean-orchestrator/vm-slots`
until `wait` sees it end or `stop` interrupts it; a launch removes the slots of
runs that have ended. Runs started in the browser hold no slot: count them by
hand.
Four concurrent chats were tried on the 4-CPU VM: they ran side by side, and
their builds shared the CPUs, so a build took about as many times longer as
runs were compiling at once. Launch with the bundled
[`vm_worker.py`](../scripts/vm_worker.py), which drives the runtime the way the
web app does, with the Platform key `OPENMATHOS_PLATFORM_KEY` (a personal
`nuc_oc_` key, read from the environment or the Keychain, never printed). Keep
the browser procedure below as the fallback. The commands below assume
`SKILL_DIR=.claude/skills/lean-orchestrator`, or the path of a personal
installation.

1. **Archive.** Pass the package with `--upload`: the launcher uploads it to
   the new project's folder in 256 KiB chunks, downloads it back and compares
   SHA-256 before sending anything. In the brief, write the folder as
   `{PROJECT_REPO}` (for example `{PROJECT_REPO}/node12.tar.gz`), which the
   launcher replaces with the path the agent sees, and name that archive as the
   only file the agent may read outside its directory, besides the exceptions
   of the isolation rule above (the preinstalled toolchain and `/opt/mathlib`,
   and its own `handoff/` folder).
2. **Launch.** One command creates a new project, turns model training off and
   checks it, uploads the archive, then sends the brief and starts the chat;
   nothing is sent if training is not off or the upload does not round-trip. Choose the model and effort as for any VM worker (Kimi
   K3.1 Pro: `high` for routine and hard nodes, `low` for a well-specified
   repair; after a stop, escalate as the profile's
   [Exceptional effort](claude-profile.md#exceptional-effort) says, not by
   switching to `max`). Set the run's own input-token cap at launch with
   `--max-input-tokens` (default 20 million; see step 3): `wait` takes it from
   the run record. The launch is refused, with nothing sent, when less than 5%
   of the team's weekly quota remains (the floor, exit code 7), when the quota
   cannot be read (exit code 4), or at the cap on running VM workers (exit
   code 9). If the launch fails after the brief was sent, it says so: the agent
   may be running, so follow it with `wait` or interrupt it with `stop`. Use a
   new run directory, project name and chat name per run:

   ```sh
   python3 -I "$SKILL_DIR/scripts/vm_worker.py" launch --run-dir .orchestration/vm-node12 \
     --display-name vm-node12 --session node12-high --brief .orchestration/vm-node12/brief.md \
     --upload .orchestration/vm-node12/node12.tar.gz \
     --model moonshotai/kimi-k3.1-pro --effort high
   ```
3. **Follow.** Run `vm_worker.py wait --run-dir …` as one background command.
   It reads `session_history` every minute and interrupts the run itself
   (`sessions.interrupt`) on a cap: `--max-minutes` (default 40) and the run's
   own input tokens (the launch's cap; `wait --max-input-tokens` overrides
   it), which other work on the team quota, such as local Kimi workers, does
   not affect. The 20-million default suits a routine node (median 5.2
   million in the trials); for a hard node launch with
   `--max-input-tokens 60000000` and wait with `--max-minutes 60`. Exit codes: 0 done; 2 time limit; 3 token or
   loop cap (15 identical tool calls in a row); 4 the quota or the session
   history unreadable three times in a row; 7 less than 5% of the team's
   weekly quota left (launch nothing more on Open Math OS, on the VM or
   through Codex, until it is back above the floor; lower the floor with
   `--floor-percent`, at launch, only on the user's instruction); 8 any
   unexpected error. In each case the run is interrupted, except that a run
   whose latest turn has already finished is left as it is. Exit code 6 means a
   cap was reached but the interruption failed: stop the run with `stop` or in
   the web app at once. Kimi can loop on a no-op after a trivial follow-up.
   `vm_worker.py stop`
   interrupts by hand; `status` prints one line.
   `wait` and `status` keep the run's own token counts, by effort, in
   `usage.json` in the run directory for the
   [token ledger](claude-profile.md#token-ledger).
4. **Retrieve.** `vm_worker.py fetch --run-dir … --out …` downloads the
   project's `handoff/` folder and compares each file with the SHA-256 the
   agent printed, when it printed one; it exits with 1 on a mismatch or an
   empty folder. The brief's final print stays useful as that check and as a
   record in the transcript.
5. **Follow-up.** When the first turn stops with a mathematical obstruction,
   send the follow-up in the same chat, which keeps the agent's context; this
   is the analogue of `--resume`. The launcher does not send follow-ups yet: use
   the browser for them. `wait` ends with the first turn, so a follow-up turn
   is not watched until you run `vm_worker.py wait --follow-up --run-dir …`
   right after sending it, once per follow-up, with the same caps as step 3.
   It waits for the new message, then follows its turn, and counts the token
   cap from the moment you run it. If that `wait` is itself stopped,
   run `wait` again, with or without `--follow-up`: it resumes, still waiting
   for the follow-up message if it had not arrived, with the same starting
   point.

`vm_worker.py` pins the web app's runtime version (0.52.0, IPC 6). When the
platform answers with another version, it exits with 5 and sends nothing: use
the browser until the script is updated.

**Browser fallback.** In the built-in browser, create the project, check that
Model training is off, choose the model and effort, and fill the brief into the
message box. A value set programmatically needs one keystroke, such as a space
then Backspace, before the app registers it; check the length of the text before
sending. The chat's session id is the last segment of its URL. Follow and
retrieve with `session_history` as above; the chat's Stop control ends a run.
The built-in browser cannot attach a local file, so the user drags the archive
into the project's Files panel; the Files panel's Download button opens a macOS
save dialog it cannot answer.

Read the Open Math OS quota before and after each run with the bundled
[`openmathos_quota.py`](../scripts/openmathos_quota.py). The difference between
the two readings bounds the run's cost; other activity in the same window also
counts, so compare the run's own model tokens when the team is busy.

## Re-verify before integration

The agent's report is not evidence. On a local copy of the package with the
returned files:

- no `sorry`, `admit`, `native_decide`, `unsafe` or custom axiom;
- the owned targets build, together with the statements file;
- each target's type is `Expr`-equal to its frozen declaration;
- `#print axioms` (or `collectAxioms`) gives only `propext`,
  `Classical.choice`, `Quot.sound`;
- `freeze_check` passes locally, against the record kept outside the project,
  with the record SHA-256 given to the user.

Then integrate as for any worker output: review the diff, seal, and have the
seal re-audited by a Sonnet that did not author the proof. Compare the
returned proof with the package sources to see what it copied.

## Platform API

The Platform API is not publicly documented. Every operation is
`POST /v1/<operation>` with a JSON object body, and bodies are validated
strictly. The web app drives the VM through a runtime reached with `open` and a
WebSocket (`agent-vm-runtime-v1`) that must match the client's version.
`vm_worker.py` uses only what the web app does for one chat: `project_create`,
`project_training`, `open`, `files.upload`, `files.download`, `files.list`,
`conversation.history`, `conversation.say`, `conversation.ensure`,
`sessions.create`, `sessions.interrupt`, and the read operations. Like the web
app, it sends each request line in WebSocket messages of at most 64 KiB; the
runtime closes the connection on a larger one. Do not script other operations,
exceed the profile's VM worker count, or work around a refusal or a version
change: report it and use the browser.
