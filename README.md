# Lean Autoformalization Skills — Claude Orchestrator

Eight [Claude Code](https://claude.com/claude-code) skills for faithful Lean 4
formalization: proving and repairing results, accompanying a research paper
with a complete formalization, building reusable libraries, formalizing books,
and publishing on GitHub, Palomar, or both. For large projects, Claude Code
coordinates a campaign: it freezes approved statements, hands proofs to
parallel workers, and seals each result only after a build, an axiom check and
an independent audit.

Version 2.0.0, 11 November 2026; see the [changelog](CHANGELOG.md). Adapted
from [Scott Armstrong's collection](https://github.com/scottnarmstrong/LeanAutoformalizationSkills),
via an earlier, unpublished adaptation for Codex orchestration; see
[attribution and licensing](ATTRIBUTION.md).
This is not an official release of that collection.

## Skills

| Skill | When it helps |
| --- | --- |
| [lean-workflow](skills/lean-workflow/SKILL.md) | Prove or repair a result; search Mathlib; maintain paper coverage; compile and check |
| [lean-project-architecture](skills/lean-project-architecture/SKILL.md) | Choose encodings, module boundaries, main statements, and a small Comparator interface |
| [lean-statement-audit](skills/lean-statement-audit/SKILL.md) | Review statement fidelity, paper coverage, proof correspondence, or final evidence |
| [lean-elaboration](skills/lean-elaboration/SKILL.md) | Diagnose actual slowness or run a requested benchmark |
| [lean-orchestrator](skills/lean-orchestrator/SKILL.md) | Coordinate a campaign from Claude Code with Sonnet subagents and background Codex or Open Math OS workers |
| [lean-publication](skills/lean-publication/SKILL.md) | Prepare and verify GitHub publication, Palomar submission, or both |
| [lean-library](skills/lean-library/SKILL.md) | Layer, check, document and audit a reusable library |
| [lean-book](skills/lean-book/SKILL.md) | Formalize a book by other authors as a library, with honest coverage claims |

Ordinary work needs only `lean-workflow`; load the others when their task
arises. Everything except `lean-orchestrator` works with Claude Code alone.

## Requirements

- A Lean 4 project with Mathlib, and its Mathlib cache (`lake exe cache get`).
- Claude Code, logged in.
- For campaigns with background workers (`lean-orchestrator`), one or more of:
  - the Codex CLI, logged in with a ChatGPT plan, for GPT workers;
  - an [Open Math OS](https://os.openmathmodel.org) team account, for Kimi and
    other models through the Codex CLI, and optionally on the team's hosted VM.
    It needs the keys `OPENMATHOS_API_KEY` and, for quota readings and the VM,
    `OPENMATHOS_PLATFORM_KEY`, in the macOS Keychain or the environment.
- Python 3 for the bundled scripts (standard library only; tested with 3.14
  and 3.15). They also call `curl` (the VM launcher) and macOS `security`
  (keys in the Keychain).
- Optional: [Lean Beam](https://github.com/leanprover/lean-beam) for fast
  probes on the Claude side (see below).

**Unofficial Open Math OS tools.** The VM launcher (`vm_worker.py`) drives the
Open Math OS VM through the web app's own protocol, which is not documented,
and the Open Math OS quota reader (`openmathos_quota.py`, also used by the
Codex launcher for its quota floor) calls the Platform API, which is not
publicly documented either. They are unofficial: not endorsed or supported by
Open Math OS, and they may break or be refused at any time. Use them at your
own risk and within Open Math OS's terms, or leave the VM route out of your
campaigns. The models themselves are called through the documented model API.

Developed and tested on macOS (a four-core Mac with 24 GB); the
scripts use macOS tools such as `caffeinate` and APFS clones (`cp -c`). Other
systems are untested.

## Installation

Each directory under `skills/` is a skill. Install them where Claude Code reads
skills (`.claude/skills/` in a project, or `~/.claude/skills/`) and, for Codex
workers, where Codex reads them (`.agents/skills/` or `~/.agents/skills/`); a
symlink keeps one copy. Keep each skill's `references/`, `scripts/` and
`assets/` with its `SKILL.md`. Optionally copy the subagent definitions from
`skills/lean-orchestrator/assets/agents/` to the project's `.claude/agents/`.

```sh
git clone https://github.com/igor-kortchemski/lean-autoformalization-skills.git lean-skills
cd lean-skills && git checkout v2.0.0
mkdir -p /path/to/project/.claude/skills
rsync -a --exclude='.DS_Store' --exclude='._*' --exclude='.git/' --exclude='.lake/' --exclude='__pycache__/' skills/ /path/to/project/.claude/skills/
```

Install from a tagged version and record the tag in the project, so an
installed copy can be compared with it by `diff -r`. Before replacing an
existing installation, check for local customizations and for skills of the
same name from another edition; keep one edition per discovery location.
Codex reads `AGENTS.md` but not `CLAUDE.md`, so worker briefs repeat the
project rules they depend on.

Lean Beam is optional and used only on the Claude side: install it with its
own installer (`./scripts/install-beam.sh --claude --claude-mcp --toolchain
<the project's toolchain>`), without its Codex options, which also installs
its `lean-beam` skill; this package does not include it.

## Authorizing external workers

Installing the skills authorizes nothing. A campaign sends project material
(Lean code, compiler output, the relevant parts of the sources) to a provider
only where your instructions allow it, in `~/.claude/CLAUDE.md` or the
project's `CLAUDE.md`. For example:

```markdown
## Authorization for Codex workers

I authorize Claude Code to send the material of my Lean projects under
`~/Lean` (sources, Lean code, compiler output) to OpenAI through Codex workers,
for formalization work. Unpublished coauthor material is excluded unless the
project says otherwise.
```

Write one such paragraph per provider (Codex, Open Math OS, the Open Math OS
VM), and narrow it in a project's own instructions when needed. The
coordinator asks before any publication, submission or other outside action.

Where the skills support several accounts (Codex accounts chosen by remaining
quota, or a separate launcher for background Claude workers, which this
package does not include), use only accounts you hold, within each provider's
terms. Choosing among accounts spreads work over the limits each account
already has; it does not raise or bypass any of them.

## First steps

Start Claude Code from the Lean project directory, then ask, for example:

- “Use /lean-workflow to prove this lemma and check its axioms.”
- “Use /lean-orchestrator to coordinate this paper formalization.”
- “Use /lean-statement-audit to compare these exports and the coverage table with the paper.”
- “Use /lean-publication to prepare this paper companion for GitHub only.”
- “Use /lean-library to audit this library for public reuse, without changing it.”
- “Use /lean-book to set up the formalization of this book.”

For a campaign, start the coordinator as the profile recommends, keeping the
Mac awake (`caffeinate -is claude --model claude-opus-5-5 --effort xhigh`).
More starters are in [Prompt suggestions](PROMPT_SUGGESTIONS.md).

## How a campaign runs

Opus at `xhigh` (`high` allowed while proving frozen nodes) coordinates from
the Lean project directory. Sonnet subagents audit and clean up. Routine Lean
goes to Kimi K3.1 Pro through the Codex CLI where Open Math OS is authorized,
with GPT 6 Luna as the fallback; GPT 6.1 Sol takes hard nodes; Kimi can also
run on the Open Math OS VM. Statements are approved by you and frozen before
workers prove them; `freeze_check.py` verifies that a worker changed only the
proof holes and that the frozen declarations still elaborate to the same
types.

Everything operational — roles, models, caps, campaign phases, freezing and
sealing, escalation, quota floors — is in one editable file, the
[Claude profile](skills/lean-orchestrator/references/claude-profile.md). Its
defaults target a four-core machine, where Lean compilation is the bottleneck;
adjust the caps to yours (the profile says how). Model names are those of
November 2026; replace them as models change. The bundled scripts in
[`skills/lean-orchestrator/scripts/`](skills/lean-orchestrator/scripts/)
launch and cancel Codex and VM workers, read quotas, freeze and check approved
statements, list local tools, and count tokens; the
[Codex worker guide](skills/lean-orchestrator/references/codex-worker.md) and
[VM worker guide](skills/lean-orchestrator/references/openmathos-vm.md)
explain them.

## Paper companion

For a paper formalization, use the root templates as needed:

- [FORMALIZATION_REPORT.md](FORMALIZATION_REPORT.md): the coverage and
  correspondence record, mapping every result in the declared scope to proved
  Lean code and recording substantive departures.
- [MANUSCRIPT_RECOMMENDATIONS.md](MANUSCRIPT_RECOMMENDATIONS.md): optional
  advisory remarks on the paper.
- `lean-workflow`'s [ERRATUM.tex](skills/lean-workflow/assets/ERRATUM.tex)
  (journal paper) or
  [MANUSCRIPT_CORRECTIONS.md](skills/lean-workflow/assets/MANUSCRIPT_CORRECTIONS.md)
  (arXiv or submitted) for audited errors in the paper, and
  [CITED_WORKS_ERRATA.md](skills/lean-workflow/assets/CITED_WORKS_ERRATA.md)
  for errors in cited works. All are drafts for the user, never sent.

Obtain an independent statement review before substantial proof work on a main
result. Preserve the paper's main strategy by default; routine differences need
no report. When publication is planned, prepare a Palomar-compatible GitHub
artifact by default; publishing, submission and registration are separate,
explicitly authorized actions.

Project instructions always govern versions, permitted actions, frozen
declarations, build concurrency and public release; these skills authorize no
new Challenge holes, toolchain or license changes, publication or submission.

## Testing

[TESTING.md](TESTING.md) summarizes what was actually checked: the scripts
with stub workers, small trial campaigns on a published paper, Open Math OS
runs, and the list of what has not been tested yet. Full research-paper
formalization, Palomar submission, `lean-library` and `lean-book` remain
untested on a real project. [`validation/check_package.py`](validation/README.md)
checks the package itself and runs in CI.

## License

The instruction text is under [CC BY 4.0](LICENSE) and the Python scripts
under [Apache-2.0](LICENSES/Apache-2.0.txt); details and third-party notices
are in [ATTRIBUTION.md](ATTRIBUTION.md).
