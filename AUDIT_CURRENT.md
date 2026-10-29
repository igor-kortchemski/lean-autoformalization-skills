# Audit of lean-palomar-skills-updated — 29 October 2026 review

Date: **29 October 2026**. Goals: avoid over-engineering, use compute efficiently, and provide the best practical user experience.

**Implementation status:** F1 was corrected in the publication prompt; F2 and F3 were addressed in the subsequent packaging cleanup on 29 October 2026. See [validation](VALIDATION.md). The assessment below preserves the original findings, line numbers, counts, and fingerprint from before those fixes. Evidence links lead to the corresponding current files; historical line numbers may no longer align.

**Verdict at review time:** keep the six-skill architecture. The reviewed package had a proportionate core, sensible compute controls, and substantially improved task guidance. The actionable findings were one publication-prompt scope conflict and two minor installation/documentation portability issues. No need was demonstrated for another skill, installer, scheduler, evidence database, or approval process.

This assessment reviewed the files after the recommendations in the earlier [AUDIT.md](AUDIT.md) were implemented. Its resolved findings were not repeated as defects. The audit itself added only this report; implementation followed separately. Installed skills were not changed.

| Goal | Current assessment | Highest-value next step |
| --- | --- | --- |
| Not over-engineered | Good core structure; publication deliberately adopts a stronger verification baseline | Preserve the architecture and correct narrow inconsistencies |
| Compute-efficient | Strong instructions against avoidable work; actual savings remain unmeasured | Fix the prompt that can cause unnecessary candidate changes, then observe real tasks |
| Best possible UX | Clear routing, short starters, scoped reviews, and accurate outcome reporting | Align the generic publication starter with its selected destination; clarify selective installation |

**Scope, method, and limits**

Four agents used all available concurrency slots: three parallel reviewers focused on simplicity, compute, and UX; the coordinating reviewer checked current evidence, cross-skill consistency, package structure, and selected official documentation. The findings were challenged across reviewers. Reviewer agreement is analytical corroboration, not execution evidence.

The review covered all six skill entry points, five references, six UI metadata files, README, prompt suggestions, both report templates, attribution, and historical audit/validation records. License files were inventoried; legal compliance was not assessed. The local directory has no Git repository, so the reviewed snapshot is identified below by a content fingerprint rather than an invented revision.

No Lean proof task, build, Comparator run, CI workflow, installation, publication, or submission was executed. Findings concern instructions and package structure. No claim of optimal token use, CPU cost, or latency is established.

**Prioritized findings**

P2 means a meaningful correction for the next revision. P3 means a minor usability or portability improvement. No P0/P1 issue was established in this review.

| ID | Priority | Finding | Smallest correction |
| --- | --- | --- | --- |
| F1 | P2 | Generic publication starter requests GitHub presentation work for Palomar-only preparation | Condition the badge clause on GitHub being selected |
| F2 | P3 | Selective architecture installation hides its Palomar reference dependency | Name the companion skill and its conditional requirement |
| F3 | P3 | Historical audit contains workstation-specific evidence links | Use relative links internally and a portable reference for older-package evidence |

**F1 — The generic publication prompt can expand a Palomar-only task**

Evidence:

- [PROMPT_SUGGESTIONS.md](PROMPT_SUGGESTIONS.md), lines 57–63, lets the user choose “GitHub, Palomar, or both” but unconditionally asks for CI and Comparator badges in the GitHub README at line 60.
- [lean-publication/SKILL.md](skills/lean-publication/SKILL.md), lines 20–22, directs reuse of adequate presentation and CI for an existing public commit.
- [palomar.md](skills/lean-publication/references/palomar.md), lines 38–41, explicitly limits Palomar-only changes to submission requirements and says GitHub presentation improvements are not prerequisites.

**Trigger:** the user copies the generic starter, selects Palomar, and supplies an otherwise ready public commit whose README lacks the two badges. The copied prompt now directly requests a presentation change that the destination guidance would otherwise avoid. The specialized Palomar starter at lines 120–126 does not have this problem.

**Impact:** inconsistent scope and unnecessary editing. If the badges enter an already-verified submission candidate, the successor snapshot requires fresh verification under [submission.md](skills/lean-publication/references/submission.md), lines 29–31. This can waste a substantial verification run, but no such run was observed. There is no inevitable duplicate run if verification has not happened yet or the README patch remains outside the submitted candidate.

**Minimal fix:** split the current sentence so the condition is explicit:

> Use Comparator for the advertised mathematical results, including small projects. For GitHub or both destinations, include CI and Comparator badges in the GitHub README.

Keep Comparator verification for Palomar. This correction changes destination routing, not the chosen verification baseline. No additional permission step is needed.

**Acceptance check:** read the generic starter with Palomar selected and an adequate public commit lacking badges. It should preserve the candidate unless a real submission requirement needs a change. Selecting GitHub or both should still request the badge pair.

**F2 — Selective installation leaves a conditional companion dependency implicit**

Evidence: [README.md](README.md), lines 102–105, describes self-contained skill entries and permits copying selected directories. However, [lean-project-architecture/SKILL.md](skills/lean-project-architecture/SKILL.md), lines 71–76, directs Palomar-sensitive design to the references inside `lean-publication`, without an availability condition or a fallback source.

**Trigger:** only `lean-project-architecture` is installed, and it is then used for Palomar-sensitive design. The named companion reference bundle is absent. The ordinary architecture path remains usable. README's recommendation to install all six for the complete route mitigates the issue; this is not a broken full installation.

**Impact:** avoidable discovery work or uncertainty about where to obtain the current policy. The package is self-contained at the directory level for its own files, but this supported task path has a cross-skill dependency that selective-install users cannot readily see.

**Minimal fix:** add one installation note and a matching condition at the handoff:

> Palomar-sensitive project design also uses the policy references in `lean-publication`; install that companion for this route. Ordinary project design can use `lean-project-architecture` alone.

An official-source fallback is another reasonable solution. Do not duplicate the policy library or introduce a dependency manager.

**Acceptance check:** a user selecting architecture alone can tell, before starting Palomar design, which additional reference bundle is needed. Installing all six should require no new ceremony.

**F3 — The historical audit is not portable with the package**

Evidence at review time: [AUDIT.md](AUDIT.md) contained **24 workstation-specific absolute file-link occurrences**: 23 pointed inside the current package, including historical lines 40 and 44, and one at historical line 70 pointed into the older sibling `lean-palomar-skills` package. All resolved on the original workstation; they depended on that location and did not travel with a copy of the package.

**Impact:** readers of a relocated or distributed package lose access to linked evidence even when the target files are present. This affects the historical report, not skill discovery or proof execution.

**Minimal fix:** use package-relative links for internal targets and put line references in the surrounding prose. For the older sibling's evidence, use a stable archive/external reference or explicitly document that external dependency; a relative path alone cannot make it self-contained. Preserve the explicit warning that the original audit's line numbers refer to an earlier snapshot; converting links must not imply that its findings describe the current files. This current report uses relative links for its internal evidence.

**Acceptance check:** static link inspection finds no workstation-rooted file targets in distributed documentation, and package-relative targets resolve after relocation.

**Simplicity: what should remain**

The minimum coherent workflow is already present: establish scope, search and prove with focused checks, update one coverage record at a coherent milestone, review changed mathematical results, and prepare one publication candidate with applicable verification.

- **One ordinary entry point.** [README.md](README.md), lines 25–26, discourages loading the full collection. Specialized skills have distinct triggers.
- **Lightweight planning.** [Architecture](skills/lean-project-architecture/SKILL.md), lines 62–65 and 83–92, avoids a new freezing system and makes extensive dependency graphs optional.
- **One coverage record.** [Orchestration](skills/lean-orchestrator/SKILL.md), lines 72–76, reuses an existing record and updates at milestones instead of creating a parallel status system.
- **Scoped review.** [Statement audit](skills/lean-statement-audit/SKILL.md), lines 55–68, preserves valid inventory entries and reserves full omission scans for the relevant boundaries.
- **Proportionate delegation.** [Orchestration](skills/lean-orchestrator/SKILL.md), lines 21–31, defaults to one proof worker and delegates independent work when the benefit justifies repeated context and coordination.

Generic autonomy/permission guidance appears in all six entries. Some repetition is justified by independent installation. If shortening it, edit the paragraphs in place and preserve their standalone meaning. A new shared-policy skill would add another loading dependency to save a modest amount of text. This is optional polish, not a material defect.

**Compute: strong controls, with no runtime optimum established**

The current workflow already uses narrow incremental builds, checks affected consumers, preserves dependency caches, reuses searches, batches axiom probes, and changes proof route when repeated attempts produce no new evidence. See [lean-workflow](skills/lean-workflow/SKILL.md), lines 34–51 and 98–120. [Orchestration](skills/lean-orchestrator/SKILL.md), lines 49–68, coordinates shared build outputs while retaining Lake's internal parallelism. [Performance guidance](skills/lean-elaboration/SKILL.md), lines 22–35 and 50–62, requires measurement before tuning and repeats measurements when noise warrants it.

One optional clarity improvement is to put evidence inspection before execution. [Publication](skills/lean-publication/SKILL.md), lines 61–64, begins with verification in a clean checkout, then explains reuse at lines 90–96. [Statement audit](skills/lean-statement-audit/SKILL.md), lines 80–93, has a similar ordering. Both already allow reuse, so this is not evidence of actual repeated builds. A short opening sentence would make the intended order easier to follow:

> Inspect existing evidence and its candidate identity first; run only missing or invalidated checks, retaining required fresh checks.

Do not add an evidence-cache subsystem. The current identity and invalidation rules remain necessary.

Measured text footprint, using whitespace-delimited words including frontmatter:

| Reading path | Words |
| --- | ---: |
| Ordinary `lean-workflow` | 1,110 |
| Workflow plus optional proof-tools reference | 1,520 |
| All six skill entries | 5,507 |
| Publication + GitHub reference + statement audit | 3,041 |
| Publication + both destination reference sets, excluding statement audit | 3,517 |
| Entire prompt library: five starters and seven variants | 939 |

These are text sizes, not model token counts or measured compute savings. The full archive is not normal task context: historical reports are not mandatory runtime inputs, and [proof-tools.md](skills/lean-workflow/references/proof-tools.md) is loaded conditionally. Shorter text alone cannot establish better task performance.

**Publication costs are intentional policy tradeoffs**

Comparator for every published named mathematical result, including a one-theorem GitHub project, is expressly recorded in [VALIDATION.md](VALIDATION.md), lines 12–32, and [ATTRIBUTION.md](ATTRIBUTION.md), lines 20–21. It adds Challenge/Solution/configuration preparation and verification work. The package limits that surface to advertised results, reuses applicable evidence, and avoids per-helper comparison.

This is a stronger baseline than the general Lake guidance, which describes external validation in terms of higher-risk use cases. Lake also documents Linux-specific sandboxing for Comparator. The package already acknowledges compatible tooling and platform requirements. These facts explain the potential setup cost; they do not establish that this project's deliberate policy is wrong. See the official [Lake reference](https://lean-lang.org/doc/reference/latest/Build-Tools-and-Distribution/Lake/).

The badge pair is also deliberate. When both badges use one workflow, they show one aggregate status. GitHub documents its badges as workflow-status indicators, not independent evidence for each contained job. The current [GitHub guide](skills/lean-publication/references/github.md), lines 38–50, correctly requires disclosure, forbids fabricated comparison success, and avoids duplicate runs or badge infrastructure. Preserve those protections. See [GitHub's badge documentation](https://docs.github.com/en/actions/how-tos/monitor-workflows/add-a-status-badge).

Palomar's complete preflight and the user's decision about the returned review are not gratuitous approval steps invented by these skills. The current official protocol requires full mechanical preflight and review-bound registration consent. Removing these steps in pursuit of lower friction would make the workflow unsuitable for that service. See the [Palomar agent protocol](https://submit.palomar-registry.org/llms.txt).

This audit recommends retaining the chosen baseline. Any later decision to make Comparator optional for ordinary GitHub publication should be an explicit policy change informed by observed cost and the desired verification guarantees.

**User-experience walkthroughs**

These are instruction-level walkthroughs, not executed end-to-end tasks.

| Request | Expected behavior from current instructions | Assessment |
| --- | --- | --- |
| Repair one lemma | Use workflow, narrow checks, no new paper-wide inventory | Clear and proportionate |
| Complete one result in an unchanged paper | Reuse inventory; review changed result and affected dependencies | Previous whole-paper-rescan issue addressed |
| Resume after a proof-route change | Preserve valid statement review; refresh affected correspondence and mechanical evidence | Previous reuse issue addressed |
| Prepare Palomar from an adequate public commit | Reuse documentation and applicable checks | Specialized starter works; generic starter has F1 |
| Install architecture alone for Palomar design | Obtain publication policy references | Companion dependency needs F2 clarification |
| Upgrade the older package | Preserve customizations and retire `palomar-deposit` | README lines 119–123 address the earlier migration gap |
| Continue with prior publication authorization | Reuse authorization; report actual destination states | No new blanket confirmation loop |

The distinction between prepared, verified, published, submitted, and registered is particularly useful: [publication](skills/lean-publication/SKILL.md), lines 115–119, requires concrete paths or URLs and preserves partial successes. Keep it. The short starters and readable UI names also help users begin without restating the entire policy collection.

**Static validation performed for this audit**

| Check | Observed result before adding this report |
| --- | --- |
| Package inventory | 27 content files plus one `.DS_Store`; 18 Markdown files |
| Skill structure | 6 entry points, 87–131 lines each; 5 references; 6 UI metadata files |
| YAML parsing | All 6 frontmatters and 6 UI metadata files parsed with PyYAML 6.0.3 |
| Basic metadata checks | Names match directories; descriptions and declared license present; UI names and short-description lengths checked |
| Markdown file links | 49 occurrences resolve locally; 24 use absolute workstation paths, all in historical `AUDIT.md` |
| Text hygiene | Balanced fenced code blocks; no CRLF files or symlinks found |
| Runtime claims | No Lean or publication execution; no token, CPU, or latency benchmark |

These are basic checks, not complete host-schema validation or a rendered MacDown/QLMarkdown review. The new report contains no mathematical expressions requiring renderer-specific delimiters. The Finder file should be excluded from any future archive as [README.md](README.md), lines 110–113, already directs; its presence does not affect skill behavior.

Reviewed content fingerprint, excluding `.DS_Store` and this new report:

```text
SHA-256: be7f82c3f010bd6000a022cf931de728964e93ebfcfe8c4f2d1e98b82d63a4d7
```

The fingerprint hashes the concatenation of lexicographically sorted relative paths, a tab, each file's SHA-256, and a newline. It identifies the 27-file reviewed snapshot without altering it.

Selected live sources were spot-checked on 29 October 2026: Lake, GitHub badge documentation, Palomar's agent protocol, and the [Palomar submission standard](https://github.com/PalomarRegistry/PalomarPolicy/blob/main/CONTRIBUTING.md). This was not a complete recertification of every dated Palomar constraint or a deposit compliance check.

**Recommended order of work**

1. Correct F1's destination condition. It is the clearest scope issue and the only finding with a concrete path to avoidable verification cost.
2. Address F2 and F3 with small documentation edits. Preserve the historical audit and the six existing skill boundaries.
3. Optionally put evidence reuse first in verification sections. Retain current safeguards; avoid new mechanisms.
4. Observe the next representative real tasks before further optimization.

A lightweight measurement pass needs only three tasks and existing project notes:

| Task | Question to answer |
| --- | --- |
| Local proof repair with unchanged statement | Does it stay on focused checks without an unnecessary broad audit? |
| Paper milestone including a resumption | Are valid inventory, review, search, and mechanical evidence reused correctly? |
| Palomar-only preparation from an already-verified public commit | Are adequate presentation and applicable checks reused without unnecessary candidate changes? |

For each, record scope, toolchain/cache conditions, elapsed time, model usage across all agents when available, build CPU time when available, build/review counts, and unnecessary user interruptions. Keep total compute separate from elapsed time: parallelism can reduce latency while increasing aggregate work. Mark missing measurements unavailable. Compare equivalent scope and retain mathematical fidelity, trust policy, and useful reporting. Repeat only when noise or a concrete change justifies it; no benchmark framework or mandatory telemetry is needed.
