---
name: lean-library
description: Build, maintain, or audit a reusable Lean library that other researchers, Mathlib, or Tau Ceti could use. Covers layering and namespaces, a build in which green means checked, one repository check, client-facing API design, documentation, API changes, an outside-consumer test, upstream routes, and an audit for public reuse. Use when setting up a library, turning campaign code into one, reviewing its public API, preparing an upstream candidate, or auditing it for reuse; not for proving a result (lean-workflow), choosing the encoding of one paper's statements (lean-project-architecture), or publishing a release (lean-publication).
license: CC-BY-4.0
---

# Build a reusable Lean library

The output is a library that someone else can install, understand, apply, and
extend, and from which suitable parts can later move upstream. Read the
project's instructions, pins, existing decisions, and coverage record first.
Frozen statements, approvals, quarantine rules, and build limits remain binding.
This skill does not authorize changing public statements, names, pins,
dependencies, the license, or publication; those are design decisions for the
owner. Prove results with `lean-workflow`, review source fidelity with
`lean-statement-audit`, and publish with `lean-publication`.

Apply the rules to the assigned scope. An ordinary helper lemma needs only the
layering and API rules below; the check, documentation, and consumer rules apply
at layer, release, and upstream milestones.

## Record the library's choices in `AGENTS.md`

The other skills assume a paper companion. A library states in its
`AGENTS.md`, which Codex workers read and briefs repeat:

- its coverage record: the index mapping source claims to exact declarations
  (for example `COVERAGE.md`), which plays the part of `FORMALIZATION_REPORT.md`;
- its publication target and Comparator scope. `lean-publication` and
  `lean-project-architecture` default to Palomar-compatible artifacts and
  Comparator for every advertised named result; a library names the results a
  Challenge covers, or states that it publishes with the axiom check only and
  labels its releases accordingly;
- where errors found in its sources go (`lean-workflow`'s registers apply);
- its pins, namespace rule, maintainer, and the installed skill tag.

## Layer the library by mathematics

Keep imports flowing one way:

```text
Mathlib and other approved dependencies
  -> generic auxiliary mathematics
  -> topic theories, for example deterministic before probabilistic
  -> source-specific statements and applications (papers, books)
```

This is a dependency principle, not a directory layout. Check it with an
import-closure scan, not by directory names: nothing generic may import an
application layer. Importing a basic topic module should not pull in the whole
library; `lake shake` reports unused imports, and a convenience aggregator
stays optional.

- Name namespaces after the topic, matching the folder (`Lib.Probability`,
  `Lib.Topology`), not after the application that first needed the lemma.
  Moving generic lemmas out of an application namespace later is a breaking
  rename of every one of them.
- Put source numbering (a paper's Theorem 2.3, a book's Lemma 4.22) in
  docstrings and the coverage index, never as the only name of a declaration.
  Cite as Mathlib does: the source is an entry of `docs/references.bib`, and
  docstrings use one fixed form, such as `[Author2021], Lemma 4.22`, which
  doc-gen4 links to the bibliography.
- Give each definition and convention one authoritative home.
- Keep layers that could move upstream free of vendored or non-Mathlib
  packages. Split a basic API (carrier, σ-algebra, operations) from the
  construction that needs the vendored package, and parameterize over a
  supplier (for example of a Wiener process) instead of importing a global
  construction.
- Let paper or book projects depend on the library rather than copy it, and
  keep experimental code outside the supported import closure.

## Configure the build so that green means checked

`lake build` checks only the import closure of its roots: a file that nothing
imports is never compiled, so it can be broken under a green CI. Declare the
library as one `lean_lib` with `globs = ["Lib.*"]` and make it the default
target. Keep examples and regression files in a separate directory, such as
`LibTest/`, outside the default target and compiled by the check.

Set the library's options in the Lake configuration as Mathlib does:
`autoImplicit = false`, `maxSynthPendingDepth = 3` (so instance search behaves
as it will upstream), and Mathlib's style linters with the `weak.` prefix
(`weak.linter.style.native`, `weak.linter.style.maxHeartbeats`,
`weak.linter.style.longFile = 1500`, and `weak.linter.style.header` if the
library targets Mathlib, whose copyright header it requires), so that a module
importing only core or Batteries still compiles. Do not set `warningAsError`
there: it would break the campaign mode below and turn a consumer's
deprecation warnings into errors. The check fails on warnings instead
(`lake build --wfail`), as Mathlib's CI does. Use the module system when the
pinned toolchain and Mathlib do. Pin Lean and Mathlib exactly (`rev` is a full
commit) and commit `lake-manifest.json`. An upgrade is its own commit, changing
`lean-toolchain`, the Lake configuration and the manifest together, followed by
the full check.
These files are owner decisions; during a campaign the orchestrator's freeze
record also covers them, so any change, a Mathlib bump included, needs the
user's approval and a new record.

Vendor a non-Mathlib source only with a `vendor/<package>/README.md` recording
its upstream URL, commit, license, and every compatibility edit; keep its
per-file notices and the library's toolchain.

Avoid `set_option` in library code. Give each unavoidable one the narrowest
scope (`in`) and a comment; heartbeat raises are local and commented, which the
style linter enforces. `backward.*` options are transition flags that a later
Lean release may remove, breaking every proof that uses them at once: track
their count and replace them by explicit `unfold`, `show`, `erw`, or a
definitional lemma. Tau Ceti forbids `set_option` entirely.

## Keep one repository check, run identically by CI

Copy [`assets/check_library.py`](assets/check_library.py) to `scripts/check.py`
and set its constants. It builds every library and vendored module explicitly
with `lake build --wfail`, compiles the example files with warnings as errors,
generates from the current checkout an audit that imports every module and
checks the axiom closure of every constant, private and generated ones
included, against `propext`, `Classical.choice` and `Quot.sound`, and runs
`#lint only docBlame`. The module list is discovered, never maintained by hand. Each example file is compiled on
its own, so it imports library modules and dependencies, not other examples;
do not declare the example directory as a `lean_lib`.
Keep drafts outside the library's folder: the check audits everything in it.
With `--names FILE`, the check also reads the declarations of the coverage
index, one per line, fails on a name that does not resolve, and reports the
names that depend on `sorryAx`.

During a campaign, frozen statements carry registered `sorry` holes
(`lean-orchestrator`). Run `check.py --allow-sorry` on the campaign branch: it
builds without `--wfail`, lists the declarations that depend on `sorryAx`, and
still fails on any other axiom. It accepts any `sorry`; the orchestrator's
`freeze_check.py` checks that only registered holes remain. The supported
branch and every release pass without it.

CI runs exactly this command with the Mathlib cache (`lean-action` with
`use-mathlib-cache`). Add a second, non-blocking job for Mathlib's linters: in
its disposable checkout, add `weak.linter.mathlibStandardSet = true` to the
Lake configuration (a TOML configuration takes no option from the command
line), build the library, report the warnings, then run
`check.py --lint-report` for the environment linters (`#lint`, Mathlib's own
included). Once it reports nothing, make it blocking: `lake build --wfail` and
`check.py --lint-report --strict`. A `nolint` needs a reason in the docstring.

Text searches for `sorry`, `admit`, `axiom`, `native_decide`, `opaque`,
`implemented_by`, `@[extern]`, `debug.skipKernelTC` and heartbeat raises are
discovery tools; the generated audit is the evidence for the axiom closure. It
neither replays declarations in the kernel nor shows that statements say what
is intended. For a release, also replay the default targets in the kernel in
CI: `lake check` exports them, replays them, and refuses non-standard axioms
(its sandbox needs `bwrap`, so Linux); `lean-action` offers the same through
its `leanchecker` input. Use Comparator for the results a Challenge covers.

## Design the API from a client's side

For each central object, a client should be able to:

- construct examples and recover the defining properties;
- prove equality through extensionality or characterization lemmas;
- apply natural operations (map or postcomposition, restriction, composition,
  scaling, transport) with their `simp`, continuity, measurability, and
  Lipschitz lemmas;
- rewrite basic expressions without unfolding the implementation, which stays
  confined behind constructors, a recursor, and `simp` equations;
- connect the object to Mathlib through equivalences or bridge lemmas when a
  specialized representation is justified.

Hold the public surface to these rules:

- `simp` lemmas are in simp normal form (the `simpNF` linter) and do not loop.
- No unused arguments (the `unusedArguments` linter), except a hypothesis that
  fixes the domain where a definition means what it should. Examples are a
  probability assumption without which a product measure is `0`, or compactness
  without which a Hausdorff distance takes the junk value `0`. Keep such a
  hypothesis with `@[nolint unusedArguments]` and a docstring giving the
  reason; a named binder also gets a leading `_`, as `lean-workflow` asks for
  a source hypothesis that Lean does not need.
- Global instances only on the library's own types; notation scoped; new
  instances and attributes checked for effects on downstream `simp` and
  instance search.
- A second structure on the same carrier lives on a type synonym, joined by an
  equivalence or homeomorphism, so the default one is never silently replaced.
  An example is a complete metric with the same topology as the usual one.
- Hard conclusions are theorems, not structure fields or bundled predicates.
  Totalized and junk values outside the intended domain are documented and
  fenced by hypotheses: a finiteness assumption that blocks a `⊤` junk value,
  integrability stated next to a signed identity, explicit non-null
  conditioning events.
- Degenerate cases (empty, deterministic, periodic, boundary parameters) are
  handled or excluded for a stated mathematical reason.
- Names follow Mathlib's conventions; argument order, implicit arguments, and
  dot notation are usable; supporting lemmas are public and implementation
  helpers private.

Take the weakest hypotheses that an actual or natural use justifies, for
example `[NormedSpace ℝ E]` with a real factor rather than `[NormedRing E]`;
do not chase maximal generality. Add generality additively: a wrapper theorem
under the weaker hypothesis leaves a frozen statement untouched. Every repeated
client workaround (unfolding, casts, quotient representatives) is a candidate
missing lemma; justify each proposed lemma by the client proof it shortens.

## Document for a mathematician arriving cold

The README gives scope and maturity, installation (Elan, `lake exe cache get`,
`lake build`, the check), a consumer `[[require]]` snippet, one compiled
example, the main results with declaration names, the conventions a user
would trip on, and the license. At the first public release, add the
maintainer, version and pin policy, and contribution rules (the check, no
holes or new axioms, the AI-use policies of upstream targets). doc-gen4
supplies the module map and API index.

- Use three status words: available, in progress, planned. Date every figure.
  Mark superseded report sections as historical. The README must never
  contradict the coverage index.
- Every public definition, structure, and class has a docstring (`docBlame`
  reports nothing; it does not check theorems), main theorems have one too, and
  every module has a module docstring with its role and main interfaces.
- Compile the README's code blocks in the example directory.
- Generate API documentation with doc-gen4 from a nested project, such as
  `docs/build/`, that requires the library by path; publishing it is optional.
- Label agent-operational files (handovers, roadmaps, `AGENTS.md`) as internal
  or keep them out of the published tree; no absolute local paths.

## Change the API deliberately

Record notable changes in `CHANGELOG.md`. Before version 1.0, a renamed or
moved public declaration needs only its changelog line; afterwards add
`@[deprecated (since := "YYYY-MM-DD")]` aliases, as Mathlib does, unless the
destination forbids a compatibility layer. Rebuild known consumers, such as
paper projects, against a breaking change in a scratch copy and record the
result.

Changes to public statements, names, imports, or dependencies need the owner's
decision. A frozen statement changes only through the project's freeze
protocol, with a successor record linked to the old one, which is kept. A
release is a tagged commit that passes the check, with a changelog entry and
the version in the Lake configuration.

## Test as an outside user

At a layer or release milestone, create a separate Lake project outside the
source tree, with the same toolchain, requiring the library by path before
publication and by a published `rev` afterwards. Use narrow public imports;
under the module system the consumer file is itself a `module` with ordinary
imports, without `import all`, so that a missing `public` shows. Write at
least one genuinely new composition of library results with Mathlib,
side conditions discharged in a concrete setting; `#check` or a copied proof
proves nothing. Record every friction (a namespace to open, a missing lemma, a
lemma in an unexpected module) and keep the good examples in the example
directory as regression tests. A path dependency does not test public
fetchability, and reused build artifacts test resolution, not compilation: say
which kind of check ran.

## Prepare upstream routes separately

Mathlib and Tau Ceti are different routes with different rules; see
[references/upstream.md](references/upstream.md). Agents prepare code and
factual handoffs. They never open pull requests, post on GitHub or Zulip, or
contact maintainers without the user's authorization, and never write the
community messages that a policy reserves for a human contributor. After a
result is merged upstream and available at the pin, migrate its users, remove
the local duplicate, and keep its source mapping.

## Audit a library for reuse

When asked, or before a release or an upstream proposal, audit the library
read-only with [references/library-audit.md](references/library-audit.md):
exact baseline and coverage, build and trust, fidelity of central results,
API and interoperability, dependencies, an outside consumer, documentation and
maintenance, separate verdicts for an independent library, Mathlib and Tau
Ceti, and prioritized findings with an ordered remediation plan. Record later
remediation in a status table appended to the audit, with commits.
