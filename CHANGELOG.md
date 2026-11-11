# Changelog

What was tested is summarized in [TESTING.md](TESTING.md); the history of the
adaptation is in [ATTRIBUTION.md](ATTRIBUTION.md).

## 2.0.0 — 11 November 2026

A new edition in which Claude Code coordinates the campaign. Skills of the same
name changed: read the [README](README.md) again before replacing an
installation of the first edition, and keep one edition per discovery location.

- **Eight skills instead of six.** `lean-library` layers, checks, documents and
  audits a reusable library, with a repository check (`check_library.py`);
  `lean-book` sets up the formalization of a book by other authors, with
  correspondence records and honest coverage claims.
- **`lean-orchestrator` for Claude Code as coordinator.** One editable
  [Claude profile](skills/lean-orchestrator/references/claude-profile.md) holds
  the roles, models, caps, campaign phases, freezing and sealing, escalation
  and quota floors. Sonnet subagent definitions (`lean-auditor`,
  `lean-sonnet-worker`, `lean-readback`) audit and clean up; background Codex
  workers write Lean, with GPT models or, through the Codex CLI, Open Math OS
  models. The Open Math OS VM route is unofficial and unsupported.
- **Scripts** (Apache-2.0): `codex_worker.py` launches, follows and cancels
  Codex workers, with a time limit and a choice among several accounts;
  `codex_quota.py` and `openmathos_quota.py` read quotas; `vm_worker.py` runs
  VM workers; `freeze_check.py` checks that workers changed only the proof
  holes of approved statements, by text and by elaborated type;
  `token_ledger.py` counts tokens per agent; `tool_probe.py` lists local tools.
- **Statement fidelity.** A blind read-back of each main statement; checks for
  content hidden in hypotheses, class fields or hollow definitions; handling of
  unused hypotheses (ideas adapted from AutoformBot, see
  [ATTRIBUTION.md](ATTRIBUTION.md)).
- **Paper companion.** `FORMALIZATION_REPORT.md` gains corrections to the paper,
  verification and assumptions with one status per check, and an account of
  how the formalization was produced; `lean-workflow` adds templates for an
  erratum, manuscript corrections and errata to cited works.
- **Optional Lean Beam** probes on the Claude side; background workers do not
  use it.
- **Packaging.** `TESTING.md` replaces `VALIDATION.md`;
  `PROPOSED_STATEMENT_CHECKPOINT.md` is removed, its checkpoint being part of
  [`lean-statement-audit`](skills/lean-statement-audit/SKILL.md#early-statement-checkpoint).
  A package check (`validation/check_package.py`) runs in CI.

## First edition — 29 October 2026

Six skills adapted from Scott Armstrong's collection: `lean-workflow`,
`lean-project-architecture`, `lean-statement-audit`, `lean-elaboration`,
`lean-orchestrator` and `lean-publication`, with an early statement checkpoint
and Palomar-compatible publication defaults. Not tagged.
