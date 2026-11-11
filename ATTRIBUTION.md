# Attribution and adaptation

Adapted from **LeanAutoformalizationSkills by Scott Armstrong**,
[upstream repository](https://github.com/scottnarmstrong/LeanAutoformalizationSkills),
local source revision `1837b95b3d5a9fd8d311367603902ad7fe261adf`.
Copyright © 2026 Scott Armstrong. The original material is licensed under
[Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/);
the full license and its warranty disclaimer are reproduced in [LICENSE](LICENSE).

This adaptation was first prepared with Codex on 28 October 2026 and revised on
29 October and 2 November 2026. It condenses and reorganizes the instructions into
six skills, combines everyday proof advice, and makes the heavier project machinery
conditional. The 29 October revision adds the paper-companion coverage guidance
and replaces the earlier `palomar-deposit` entry with one `lean-publication`
skill for GitHub, Palomar, or both. That skill combines the collection's Palomar
workflow with public-release guidance adapted from the upstream collection,
using shared preparation and destination-specific references.
The same-day audit revision clarifies selective review reuse and upgrade steps,
aligns trust-policy scope, and shortens prompts and autonomy guidance.
The publication default now includes Comparator for advertised mathematical
results of any project size, with CI and Comparator badges in GitHub READMEs.
The early statement checkpoint adds independent review before substantial main
or dependent proof work, with focused review reuse and standalone skill routing.
GitHub publication artifacts now target Palomar compatibility by default, while
full Palomar preflight and registry actions remain separate requested work.
The 2 November edition is prepared as a separate copy for Codex orchestration.
It adds a configurable operating profile for models, efforts and machine resources,
plus direct Claude Code delegation guidance and campaign prompts. It retains the
six skills, the existing mathematical checks and the publication workflow.
The 4 November 2026 edition, prepared with Claude Code, is a further separate
copy that makes Claude Code the coordinator, following the setup described in
Scott Armstrong's post
[Autoformalization is now very easy](https://www.scottnarmstrong.com/2026/10/autoformalization-is-now-very-easy/):
Opus coordinates, Sonnet subagents audit and clean up, and GPT workers launched
as background Codex processes write most of the Lean. It replaces the Codex profile and
Claude worker guide with a Claude profile, a Codex worker guide and optional
Claude subagent definitions, adds scripts that launch and cancel Codex
workers and read Codex quotas through `codex app-server`, and adapts the
README, prompts and package check, following two audits and a review recorded
in the author's unpublished development notes.
The other five skills were copied unchanged; since 6 November 2026,
`lean-workflow` and `lean-statement-audit` also differ.
The revision of 6 November 2026 adapts three ideas from
[AutoformBot](https://github.com/facebookresearch/autoform-bot) release 0.6.0,
copyright © 2026 Meta Platforms, Inc. and affiliates, under the MIT license
(same terms as [LICENSES/MIT.txt](LICENSES/MIT.txt)): the blind read-back of a
statement (the `lean-readback` agent and the read-back step of campaign
phase 3), its list of content hidden in hypotheses, class fields or hollow
definitions (in `lean-statement-audit`), and its handling of unused hypotheses
(in `lean-workflow` and the Claude profile). They are rewritten in this
package's words; no AutoformBot file is copied.
The revision of 8 November 2026 adds two skills written for this edition with
Claude Code. `lean-library` gathers the practices of one of the author's
reusable Lean libraries and of its two library audits and their briefs; its
`assets/check_library.py` is adapted from that library's repository check and
lint report scripts, which are licensed under Apache-2.0 (same terms as
[LICENSES/Apache-2.0.txt](LICENSES/Apache-2.0.txt)). `lean-book` draws on the
author's project brief for formalizing a textbook and on the audit of that
brief; it contains no text of the book.
The revision of 9 November 2026 revises these two skills after two audits; the
`lean-book` revision was drafted by a Codex worker on Open Math OS (Kimi K3.1
Pro) and reviewed with Claude Code.
The six-skill edition of 29 October 2026 was the first published in this
repository; version 2.0.0 (11 November 2026) replaces it with the Claude Code
orchestrator edition described above.
The instruction text in this adaptation is offered under CC BY 4.0, subject to
the third-party terms below. This is not an official release or endorsement by
Scott Armstrong or Palomar.

The upstream collection credits [cameronfreer/lean4-skills](https://github.com/cameronfreer/lean4-skills)
under the MIT license and [leanprover/skills](https://github.com/leanprover/skills)
under Apache-2.0. Their license texts are retained in [LICENSES/MIT.txt](LICENSES/MIT.txt)
and [LICENSES/Apache-2.0.txt](LICENSES/Apache-2.0.txt). No upstream executable
scripts, tests, or reference files are copied into the skills in this package.

Palomar facts are summarized from the official sources linked beside them.
No Palomar source code or templates are bundled, and this package does not
license their contents or any user's Lean project or manuscript.

## Licenses at a glance

The author of this adaptation is Igor Kortchemski; it was prepared with Codex
and Claude Code, as described above.

| Material | License |
| --- | --- |
| Instruction text: the skills' Markdown files, agent definitions, templates and root documents | [CC BY 4.0](LICENSE), adapted from Scott Armstrong's collection, subject to the third-party terms above |
| Python scripts written for this package: `skills/lean-orchestrator/scripts/` and `validation/` | [Apache-2.0](LICENSES/Apache-2.0.txt), Copyright © 2026 Igor Kortchemski |
| `skills/lean-library/assets/check_library.py` | [Apache-2.0](LICENSES/Apache-2.0.txt), adapted with modifications from the scripts of one of the author's Lean libraries, described above |

Each script carries an `SPDX-License-Identifier` line.
