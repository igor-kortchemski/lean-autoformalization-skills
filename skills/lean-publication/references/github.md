# GitHub publication and reader experience

Use for GitHub or both destinations. Reuse the existing repository, working CI,
documentation, and citation files. The community
[LeanProject template](https://github.com/leanprover-community/LeanProject) is a
reference for substantial projects, not a required migration for a small one.

For published mathematical results, prepare the artifact under the current
[Palomar requirements](requirements.md), including the interface and metadata in
[palomar.md](palomar.md). A GitHub-only request still uses this artifact default;
it does not request full Palomar preflight, submission, or registration. Report
incompatibilities with existing project constraints before changing them.

## Help readers find, check, and use the result

Make the README answer four questions near the top:

- **What is proved?** Link the paper and main Lean declarations, give a brief
  mathematical summary and honest status, and explain material assumptions or
  gaps. Link the shared correspondence record for full scope and proof-route
  differences. Keep internal process logs out of the main reading path.
- **Where do I start?** Give a clear entry file and, when useful, a short module
  map. Use meaningful names, module explanations, and docstrings for the public
  mathematical interface. A reader should find the main statements without
  installing Lean.
- **How do I verify it?** Provide a copyable quick start with the actual clone
  URL, the cited release checkout when applicable, prerequisites, cache retrieval,
  and build/check commands. Link the
  [Lean setup guide](https://leanprover-community.github.io/install/project.html)
  and explain opening the project folder in VS Code. Normally use
  `lake exe cache get` for Mathlib projects; reproduce committed pins without
  `lake update`. Test the commands on the candidate.
- **How do I cite or help?** Credit authors and contributors, state the license
  and maintenance status, and give citation and issue/pull-request guidance.
  A short paragraph can suffice; reuse an existing `CONTRIBUTING.md`.

For new citation metadata, prefer `CITATION.cff`; retain an adequate existing
file such as `CITATION.bib`. Distinguish the paper citation from the formalization
artifact and verify the metadata. GitHub's
[citation feature](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files)
formats CFF citations and also links other recognized citation files. A code
license does not automatically cover manuscript text, figures, or reused data.

Place both **CI** and **Comparator** badges near the README title, linked to the
actual checks for the intended branch. Follow GitHub's
[workflow badge guidance](https://docs.github.com/en/actions/how-tos/monitor-workflows/add-a-status-badge),
including explicit branch selection. Prefer separate existing statuses when
available. If one workflow backs both, keep both labelled badges and disclose
that they show the same aggregate workflow status; do not imply separate job
signals or successful comparison when that job was skipped. Reuse the workflow
without duplicate runs, a custom badge server, or infrastructure solely for
display. Do not silently substitute one combined badge for the requested pair.
State missing, pending, or incompatible checks honestly; never fabricate a pass.
A branch badge does not certify a release commit: link its actual verification
evidence separately. During local preparation, prepare the badge links and mark
checks unrun until their real destinations and results are available.

Use a succinct repository description and relevant topics. Verify rendered maths
and links. Preserve the user's Markdown conventions; use inline `$...$` and
display `$$` on separate lines, with blank lines around display blocks and no
undefined macros.

## Keep tooling proportionate

Start with one ordinary build workflow, preferably maintained
[lean-action](https://github.com/leanprover/lean-action), on pushes and pull
requests with dependency caching. Reuse working CI. Comparator verification is
the default for published named mathematical results, including a single theorem
or a small GitHub-only project; project size alone is no exemption.

Keep its verification surface small:

- A source-reviewed Challenge states the advertised results and their semantic
  definitions independently of proof implementation. Govern any deliberate
  Challenge holes under project policy; never import them into proof code.
- A proved Solution exposes the matching declarations. Reconcile the comparison
  list with every advertised result and inspect relevant definition dependencies.
- A reviewed configuration identifies Challenge, Solution, theorem names, and
  permitted axioms. Apply Palomar's axiom allowlist and any stricter project
  policy. Report conflicts with an established trust policy; never permit
  `sorryAx` in a claimed proof or loosen policy merely to make a check pass.
- A reproducible check uses pinned, compatible tooling and records the candidate,
  configuration, compared declarations, and actual outcome. Prefer supported
  modern tooling; do not upgrade an existing toolchain without authorization.

Use the pinned toolchain's supported interface; current Lake integrates
`lake comparator` and uses a Linux sandbox by default. Consult
[Challenges and External Checkers](https://lean-lang.org/doc/reference/latest/Build-Tools-and-Distribution/Lake/)
for configuration and platform requirements. Prefer a compatible Linux check
over disabling isolation. Run comparison at meaningful integration/publication
checkpoints, rather than after every helper edit. Reuse an equivalent full
Palomar preflight for the same candidate and comparison scope.

Explain concrete exceptions, such as an incompatible frozen toolchain or an
application with no advertised mathematical results. Record the missing or
inapplicable check and next step; do not manufacture a passing badge. Keep ordinary
builds and applicable axiom checks. Avoid fixed runner cleanup scripts, platform
matrices, and release automation without a concrete need.

For larger developments, use
[Lean Blueprint](https://github.com/PatrickMassot/leanblueprint) when mathematical
exposition and dependency navigation help, and
[doc-gen4](https://github.com/leanprover/doc-gen4) for searchable API documentation
on GitHub Pages. Reuse an existing site or community template, keep documentation
tooling separate from ordinary proof builds, and check the rendered navigation
and theorem links. A README and linked Lean sources can suffice for a small
project. Do not add a site merely to decorate the release.

## Prepare or publish the requested artifact

For a new public export, include all advertised proofs and required modules,
declared public dependencies, toolchain/configuration/manifest, documentation,
and licenses. Exclude generated `.lake` output and private working material.
Inspect the tree and any history being published, preserving provenance. Keep
the development checkout intact when an isolated export is appropriate.

A GitHub Release is optional for a repository publication request. When
requested, prepare its tag, exact commit, and concise notes identifying the
paper version, scope, verification, and limitations. Preserve cited releases;
subsequent changes receive a new version rather than moving the old tag.

If Zenodo archival is requested, follow the
[GitHub integration](https://docs.github.com/en/repositories/archiving-a-github-repository/referencing-and-citing-content),
enable it before the release intended for automatic archival, and verify the
returned record and version DOI. Do not claim archival merely because the
GitHub release exists. Reuse an existing archival setup.

Complete authorized repository, CI, Pages, or release actions, then verify their
actual URLs and status. Preparation alone does not authorize pushing, changing
visibility, deploying a site, or uploading an archive. Report those actions as
pending when outside scope; do not add new permission requests when the user's
existing instruction already authorizes them.
