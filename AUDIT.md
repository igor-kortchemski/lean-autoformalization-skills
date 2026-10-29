# Audit of lean-palomar-skills-updated

Date: **29 October 2026**. Goals: avoid over-engineering, minimize unnecessary compute, and improve user experience.

**Implementation status:** the recommendations were implemented on 29 October
2026; see [implementation and validation](VALIDATION.md). The audit below is
retained as the original assessment. Its evidence, counts, and line numbers
refer to the pre-implementation snapshot and are not a description of the
revised files.

Evidence links now use package-relative paths and lead to the corresponding
current files. Line numbers still refer to the historical audited snapshot.
The older package cited below is external historical evidence, not bundled here.

**Verdict:** keep the six-skill architecture. It is already proportionate and has strong defaults for focused builds, optional tooling, autonomous work, and reuse. The most useful improvements are to make review reuse precise, keep intermediate audits local, document the renamed-skill upgrade, and shorten the user's prompts. A new orchestration framework, installer, evidence database, or additional skill would add little value.

| Goal | Assessment | Most useful change |
| --- | --- | --- |
| Not over-engineered | Good structural design; some repeated policy and overly broad defaults | Keep the existing boundaries; trim wording and scope restrictions correctly |
| Compute efficiency | Sensible instructions; actual cost improvements are unmeasured | Reuse review components per result and avoid repeated whole-paper inventories |
| Best possible UX | Clear routing and authorization boundaries; upgrade and prompt friction remain | Add a migration note and short task-oriented starter prompts |

Five findings follow. **P2** means a meaningful issue to fix in the next revision; **P3** means useful polish. No critical defect was established. Risks inferred from instructions are distinguished from observed execution failures.

**Review scope and evidence**

Four agents worked on the audit, using all available concurrency slots: three parallel reviewers covered simplicity, compute, and UX; the coordinating reviewer checked cross-skill consistency, package structure, and selected official Palomar sources. Findings were consolidated and checked against the actual files. Multiple reviewers agreeing is supporting analysis, not runtime verification.

The review covered all six skill entry points, five reference documents, six UI metadata files, README, prompts, both templates, validation notes, and attribution. License files were inventoried; this was not a legal audit. The older sibling package was consulted only to verify the publication-skill rename.

Observed baseline, before adding this report:

| Check | Result |
| --- | --- |
| Package contents | 26 files excluding two Finder metadata files; 17 Markdown files |
| Skill entry points | 6; 89–130 lines each; 5,057 whitespace-delimited words in total |
| Ordinary workflow entry | 1,098 words |
| Prompt library | 11 prompt blocks; 1,951 words in the whole file |
| YAML parsing | All 6 frontmatters and 6 UI metadata files parsed with Ruby YAML |
| Basic metadata checks | Skill names match directory names; expected frontmatter keys and basic UI fields present |
| Local Markdown links | All 23 relative file-link occurrences resolve; no local fragment links to check |
| Other static checks | No symlinks, CRLF files, or Lean source files found |

These are text and structure measurements, not token counts, benchmarks, or full host-schema validation. No skills were installed, no Lean project was built, and no publication or submission was executed. The existing [validation record](VALIDATION.md) (line 126) appropriately acknowledges the absence of runtime performance evidence.

**F1 · P2 — Audit reuse can preserve an obsolete claim about the paper's proof**

Evidence: [audit reuse criteria](skills/lean-statement-audit/SKILL.md) (line 79), lines 79–85, distinguish mechanical evidence, which includes proof bodies, from substantive audit reuse, which names source, elaborated statement, and semantic dependencies. Yet the same audit also [checks proof correspondence](skills/lean-statement-audit/SKILL.md) (line 65), including bypassed novel methods and manuscript gaps. The incomplete reuse condition also appears in [publication](skills/lean-publication/SKILL.md) (line 68), [coordination](skills/lean-orchestrator/SKILL.md) (line 82), and the [paper prompt](PROMPT_SUGGESTIONS.md) (line 75).

**Trigger and impact:** a theorem initially follows the paper's novel construction. Its proof is then replaced with an application of an existing theorem, while its type and defining mathematical objects stay unchanged. Mechanical checks must be refreshed, but the written substantive-review criteria do not explicitly invalidate the earlier “paper argument checked” conclusion. Reuse can therefore preserve inaccurate provenance even though the Lean result remains correct. This is an instruction-level gap, not an observed false audit in a completed project.

**Smallest fix:** separate reuse by the claim supported. Preserve statement-fidelity review when its semantic inputs are unchanged; recheck the affected proof-correspondence finding when the proof route or relevant proof dependencies change. A tactic-only refactoring need not trigger a complete source audit.

Suggested wording:

> Reuse each review component only while the inputs supporting its conclusion remain unchanged. Proof-correspondence findings also depend on the proof route and relevant implementation dependencies. After a proof change, check whether that correspondence changed; refresh affected findings and preserve the rest, including their review status.

Apply the same distinction at the existing reuse sites. No separate evidence schema is needed.

**F2 · P2 — Intermediate audits can expand into repeated whole-paper inventories**

Evidence: the [ordinary workflow](skills/lean-workflow/SKILL.md) (line 125) calls for a statement audit at main-theorem or coverage milestones. The [audit coverage instructions](skills/lean-statement-audit/SKILL.md) (line 57), lines 57–63, call for independently inventorying every in-scope claim and scanning for omissions at coherent milestones. The [paper prompt](PROMPT_SUGGESTIONS.md) (line 75) repeats that milestone trigger.

**Trigger and impact:** a whole-paper campaign has an established inventory and finishes one more theorem. A cautious agent can interpret the next audit as another traversal of every claim in the paper, or invalidate an entire prior audit when one declaration changes. This consumes reading and reasoning time without necessarily improving the changed result's review.

The opening scope instructions and existing reuse language permit a narrower reading. Therefore this is a scope ambiguity and plausible compute risk, **not proof that every compliant agent must repeat the entire audit**. For illustration, ten full scans of an unchanged 100-claim paper involve 1,000 claim visits; that is an explanatory example, not a measured workload.

**Smallest fix:** explicitly establish and independently check the inventory initially; preserve valid entries individually; audit changed results and affected dependencies at intermediate milestones. Repeat the whole-scope omission scan when the source or declared scope changes and before claiming whole-paper completion. A request for one theorem should stay scoped to that theorem and its relevant dependencies.

Keep this in the existing coverage record. Preserve full coverage obligations and independent review at meaningful boundaries.

**F3 · P2 — An overlay upgrade leaves the retired publication skill discoverable**

Evidence: the [README replacement notice](README.md) (line 85) replaces `palomar-deposit` with `lean-publication`. The [installation instructions](README.md) (line 90), lines 90–104, describe copying directories and avoiding duplicate names. The earlier `lean-palomar-skills` package inspected for this audit had `name: palomar-deposit` in `skills/palomar-deposit/SKILL.md` (line 2), with an overlapping Palomar task description. That older package is external historical evidence and is not bundled here.

**Trigger and impact:** an existing user copies the updated directories over an installation of the older package. Five existing names are replaced and `lean-publication` is added. The differently named `palomar-deposit` directory remains. The intended unified publication workflow now has two discoverable entry points with different versions of the instructions.

This follows deterministically from overlay copying; it does not establish that any current installation is broken. The existing duplicate-name warning does not cover differently named replacements.

**Smallest fix:** add an explicit upgrade paragraph:

> When upgrading from the earlier package, inspect the installed `palomar-deposit` directory or symlink, preserve any local customizations, and retire that entry after installing `lean-publication`. Update explicit references to the old name and check that only the intended publication entry remains discoverable.

An installer or compatibility alias is unnecessary.

**F4 · P2 — The everyday workflow applies a trust restriction more broadly than publication does**

Evidence: [lean-workflow](skills/lean-workflow/SKILL.md) (line 108), lines 108–117, makes module conventions conditional on Palomar but unconditionally says to avoid `native_decide`, `bv_decide`, and other routes introducing native-evaluation axioms. The [publication skill](skills/lean-publication/SKILL.md) (line 60), lines 60–63, instead applies project axiom policy and reserves Palomar-specific restrictions for Palomar. The [performance skill](skills/lean-elaboration/SKILL.md) (line 66) also scopes that restriction to Palomar.

**Trigger and impact:** a GitHub-only project permits a computational proof route under its existing trust policy. The everyday workflow still discourages it unconditionally. This can narrow useful proof choices and make behavior surprising when moving between skills. The concern is inconsistent policy scope; no claim is made about measured speedups or the implementation of every tactic across Lean versions.

**Smallest fix:** make the ordinary workflow explicitly follow the project's trust policy and apply the Palomar axiom restrictions when Palomar is a target. Inspect actual transitive axiom closures with the pinned toolchain. Retain the prohibitions on unapproved holes and custom axioms.

If the entire collection is intentionally restricted to Palomar-compatible proof methods even for GitHub-only work, state that default clearly and align the publication instructions. Do not leave that design choice implicit.

**F5 · P3 — Long starter prompts repeat policy already supplied by the skills**

Evidence: the [default prompt](PROMPT_SUGGESTIONS.md) (line 15) is 196 words; the [paper prompt](PROMPT_SUGGESTIONS.md) (line 46) is 294 words. Seven prompts contain a near-identical 58-word autonomy paragraph, totaling 406 words, about 21% of the prompt document. Similar autonomy paragraphs across the six skill entries occupy approximately 492 words, about 10% of their combined text.

**Trigger and impact:** a user copies a long prompt and must distinguish actual task parameters from general instructions already loaded by invoking the skill. Maintaining multiple copies also increases the chance of inconsistent guidance, as the reuse wording illustrates.

Only one prompt is normally used, and the README correctly discourages loading all skills. Consequently the repeated prompt paragraph adds about 58 words to a typical selected prompt, **not 406 words to every run**. Text reduction alone does not establish lower total execution cost.

**Smallest fix:** lead with three to five short starters for a target, a paper, an audit, resumption, and publication. Keep detailed variants optional. Compress the common autonomy guidance within each skill while preserving standalone usability; do not introduce a shared policy-loader skill.

For example:

```text
Use $lean-workflow to complete [target] from [source/locator], including
integration and verification. Preserve the mathematical scope and existing
project rules. Report the proved exports, checks, and remaining obligations.
```

Publication prompts should still specify destinations and whether the request authorizes preparation, publication, submission, or registration. Those distinctions carry real meaning.

**What to preserve**

- **Task-based loading:** [README](README.md) (line 14) gives a clear default and keeps specialized skills conditional. Merging everything into one large entry would undermine that benefit.
- **Proportionate checking:** [focused build targets and consumer checks](skills/lean-workflow/SKILL.md) (line 39), [batched axiom queries and evidence reuse](skills/lean-workflow/SKILL.md) (line 113), and [shared publication verification](skills/lean-publication/SKILL.md) (line 71) address genuine sources of wasted work.
- **Measured performance work:** [lean-elaboration](skills/lean-elaboration/SKILL.md) (line 22) requires comparable baselines, identifies bottlenecks, preserves caches, and distinguishes a larger budget from a faster proof.
- **Deliberate parallelism:** [lean-orchestrator](skills/lean-orchestrator/SKILL.md) (line 21) recognizes duplicated context and coordination cost, requires independent work, and coordinates shared builds. This audit's explicit request for maximum agents is not a reason to change that default.
- **Minimal project machinery:** small plans, existing coverage records, optional manuscript recommendations, and no mandatory per-helper reviews remain appropriate.
- **Publication UX:** reuse existing CI, citation files, and adequate documentation; keep websites, Blueprint, releases, and archival optional. Separate prepared, verified, published, submitted, and registered outcomes.
- **Necessary decisions only:** keep autonomous continuation and reuse of existing authorization. Palomar's review-dependent registration decision is an external requirement: its [live service protocol](https://submit.palomar-registry.org/llms.txt) requires showing the returned review and letting the user decide. It should not be removed as “ceremony.”

**Small additional improvements**

The [report template](FORMALIZATION_REPORT.md) (line 31) contains two sample rows marked `Complete`. Label them explicitly as examples to replace, or use neutral placeholder rows, so a copied template does not initially resemble real verification evidence.

At worker-to-reviewer handoffs, pass the existing command, target, result, and relevant output location alongside the changed files. The current reuse rules already allow this; one practical example could make them easier to follow. Reuse should remain conditional on unchanged inputs. Do not add a new ledger or mandate duplicate builds.

Exclude `.DS_Store` and `skills/.DS_Store` from future distribution archives. Their presence in this local folder is packaging noise, not a runtime defect, and does not refute historical checks on a different archive.

**Recommended change order and validation**

1. Correct review-component reuse and intermediate audit scope together. These improve both confidence and cost.
2. Add the renamed-skill migration note and align trust-policy scope.
3. Shorten the starter prompts and mark template examples clearly.

Keep the implementation to edits in the existing documents. Use the following scenarios to review the revision; a permanent test framework is unnecessary.

| Scenario | Expected behavior after revision |
| --- | --- |
| Proof route changes; theorem type and source stay fixed | Refresh affected correspondence findings and mechanical evidence; preserve applicable statement review |
| Tactic-only refactoring with the same mathematical route | Check the changed proof; avoid a gratuitous full-paper review |
| One theorem finishes in an unchanged large paper | Review that result and affected dependencies; reuse the established inventory |
| Declared scope changes, or whole-paper completion is claimed | Reconcile the full inventory and scan for omitted claims |
| Old package is upgraded by copying directories | Retire the old publication entry deliberately; preserve customizations |
| GitHub-only task permits a computational proof method | Follow the declared project trust policy; do not silently impose Palomar policy |
| Both destinations have applicable verified evidence | Share covered checks; retain mandatory Palomar verification and accurate candidate identity |
| A preparation request reaches external publication | Deliver the concrete candidate; perform only already-authorized external actions |

To evaluate compute and UX claims, observe a few representative real tasks after these edits: a local proof repair, a paper milestone, an interrupted-task resumption, and publication preparation. Record elapsed time, available token/CPU measurements, build invocations, repeated reviews, and unnecessary user questions in existing notes. Compare equivalent scope and cache conditions and check that the mathematical and reporting quality is preserved. Until then, describe these changes as expected improvements rather than proven savings.

**Limits and provenance**

Selected live Palomar checks on 29 October 2026 supported the retained full-preflight and registration boundaries: the [submission policy](https://raw.githubusercontent.com/PalomarRegistry/PalomarPolicy/main/CONTRIBUTING.md), [agent protocol](https://submit.palomar-registry.org/llms.txt), and [workflow definition](https://github.com/PalomarRegistry/PalomarSubmission/blob/main/.github/workflows/submission.yml) were inspected. The [toolchain policy](https://raw.githubusercontent.com/PalomarRegistry/PalomarSubmission/main/toolchains.json) still reported the minimum recorded in the package. This was a limited spot-check of moving sources, not a complete policy/schema certification or an immutable policy snapshot.

The source folder is not a Git checkout. Its 26 non-Finder files had aggregate SHA-256 `de9efa4efa645cdd4a96559e783123de0595c2f6d3ce0b2e37787a581019671b` before this report was added. The aggregate hashes the concatenation, in sorted relative-path order, of each UTF-8 path, a NUL byte, and that file's binary SHA-256 digest. This identifies the reviewed local content without implying a repository commit.

At audit delivery, only this document had been added; the skill instructions,
templates, installation state, and historical validation record were unchanged.
