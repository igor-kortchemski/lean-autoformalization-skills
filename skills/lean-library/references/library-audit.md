# Audit a Lean library for public reuse

Use this procedure when asked to audit an existing library, or before a release
or an upstream proposal. It assesses three destinations separately: an
independent library that other researchers adopt, Mathlib, and Tau Ceti.

## Rules

- **Read-only by default.** Do not refactor sources, change statements or
  definitions, upgrade dependencies, alter the license, commit, publish, open
  pull requests, or contact maintainers unless separately asked. Temporary
  probes and test projects go in an isolated directory.
- **Assurance no stronger than the checks.** A build, a text search for
  `sorry`, and a sampled semantic review are different evidence. Mark each
  check as exhaustive, sampled, blocked, or not performed.
- **Pinned baseline.** Audit with the project's pins. Check current upstream
  policies separately, and never attribute a newer environment's result to the
  audited snapshot.
- **Reuse evidence** only when its snapshot, configuration, commands, and
  coverage match, and say so.
- Write one report, normally `LEAN_LIBRARY_AUDIT.md`, and keep logs and test
  projects apart.

For a large library, run the mechanical checks exhaustively, review central
definitions and advertised results first, and sample the rest deliberately.
Several reviewers can own separate areas (statement fidelity by layer; API and
interoperability; documentation, packaging, and a clean build); the
coordinator verifies each substantive finding against the source before it
enters the report.

## What to check

1. **Baseline.** Repository, branch, commit, uncommitted or untracked changes;
   toolchain, Lake configuration, resolved Mathlib and other dependency
   revisions; advertised modules and main declarations; CI jobs, lint and axiom
   mechanisms; informal sources available for statement review.
2. **Build and installation.** Which files the default build covers, and which
   advertised modules or examples it omits. Follow the documented setup in a
   clean environment where practical. Look for untracked local dependencies,
   absolute paths, unpublished forks, and machine-specific configuration.
   Separate code or packaging failures from network, tool, or resource limits.
3. **Trust.** A transitive axiom audit over every supported declaration,
   definitions included; a few `#print axioms` commands do not establish a
   repository-wide result. Inspect each hole, added axiom, native evaluation,
   and conditional theorem for what it actually affects. `classical` and
   `noncomputable` are not defects.
4. **Fidelity.** Compare central results and the definitions they use with
   their documented meaning: implicit parameters, section variables, instance
   assumptions, quantifier order, elaborated types. Ask whether a special case,
   stronger hypothesis, or different convergence notion replaced the intended
   result; whether hypotheses are satisfiable in intended examples; whether the
   conclusion hides in a structure field or predicate; whether boundary cases
   are handled; whether names and documentation claim more than is proved.
   A real Bochner integral equal to zero does not give integrability: Mathlib
   assigns zero to non-integrable functions.
5. **Interoperability and API.** Search the pinned dependencies before
   recommending a new abstraction or claiming duplication, comparing exact
   types. Check bridges for specialized representations, useful generality,
   and API completeness as in the skill's client rules.
6. **Dependencies and downstream effects.** Upward imports, cycles, heavy
   imports, results trapped in unsuitable files; global instances, coercions,
   notation, `simp` sets and automation that change unrelated proofs;
   unexplained resource limits. Measure only concrete risks. For a Mathlib
   candidate, name each non-Mathlib dependency in its closure.
7. **Outside consumer.** As in the skill: a separate project, narrow public
   imports, at least one new composition, recorded friction.
8. **Documentation and maintenance.** Scope, versions, installation, imports,
   principal results, conventions, limitations, compiled examples, generated
   API documentation, license and provenance of incorporated code, attribution,
   release and migration policy, maintainer. Never relicense or assert legal
   compatibility without a basis.

## Report format

**A. Executive assessment.** One paragraph per destination: can another
researcher use the snapshot now; which components are plausible Mathlib
candidates and what they need; which fit a Tau Ceti roadmap. Principal
blockers, demonstrated strengths, scope of assurance. No numerical scores.

**B. Baseline and coverage.** The exact snapshot and pins, and a table of the
checks: what ran, on what scope, with what outcome, and what was not performed
and why. Keep source inspection, execution, and inference apart.

**C. Prioritized findings.**

| Level | Meaning |
| --- | --- |
| P0 | An advertised result is materially misrepresented, or trust or completeness differs materially from the claim |
| P1 | A substantial obstacle to public use, reliable maintenance, or a stated integration goal |
| P2 | A concrete improvement to reuse, interoperability, documentation, or maintainability |
| P3 | Minor polish, aggregated |

Each substantive finding gives its goal, location (file, declaration, line),
evidence (the statement, configuration, or command output), consequence,
smallest useful remedy, how to verify the fix, and confidence (confirmed,
likely, needs evidence). Do not invent findings to fill a category.

**D. Ordered remediation plan.** Adoption blockers first, then quality gates
that change no API, then changes needing design decisions (public statements,
names, imports, dependencies), then each upstream route. Recommend incremental
work, and list the strengths to preserve.

Stop expanding a check once its evidence answers the question; broaden it when
a defect suggests a pattern. The audit is complete when every requested area
has an evidence-backed assessment or an explicit limitation, and the next
useful changes are clear.
