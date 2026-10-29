# Search and proof tools

Use the pinned checkout as the authority for names and APIs. These are tools to
try when useful, not a checklist for every lemma.

## Finding the missing ingredient

- Search project modules and `.lake/packages/mathlib/Mathlib` with `rg`. Search
  both the mathematical word and the namespace of the object being manipulated.
- Open neighboring declarations: often the theorem you need is a specialization,
  converse, `_iff` variant, or an application of a bundled map's API.
- Use `#check` and small `example` probes to test the full type and necessary
  instances. Do not guess a theorem's argument order from its name.
- Try `exact?`, `apply?`, `rw?`, or `simp?` if available in the pinned imports.
  Keep the resulting explicit proof rather than the discovery command.
- Before broadening imports, find the provider module for the symbol. Verify
  import changes by compilation: instances and syntax can be indirect needs.

## Translating an argument

| Mathematical step | Useful proof shape |
| --- | --- |
| Introduce data or a hypothesis | `intro`, `rintro` |
| Use existence or a conjunction | `obtain`, `rcases` |
| Construct existence or a pair | `refine`, `use`, `constructor` |
| Identify the right goal representation | `show`, `change`, a type annotation |
| Chain identities or estimates | `calc` with named intermediate facts |
| Equality of functions or structures | `ext`, then the component API |
| Rewrite under a binder | `simp_rw` or a focused `conv` |
| Finish algebra or arithmetic | `ring`, `linarith`, `nlinarith`, `omega` |
| Prove a sign or regularity side condition | `positivity`, `continuity`, `measurability`, where available |

If Lean cannot infer the ambient space, annotate it at the first ambiguous
expression. If two encodings are equivalent, prove one bridge lemma and reuse
it. Repeated large unfolding lists usually indicate a missing local API.

For measure/probability arguments, check finiteness, measurability, coercions,
and whether a quantity lives in `ℝ`, `ℝ≥0`, or `ℝ≥0∞` before rewriting. An
`ENNReal.toReal` conversion can require a non-infinity hypothesis; do not lose
that condition by replacing a source quantity with a real-valued surrogate.

For estimates, make constant dependence explicit before entering arithmetic
tactics. Keep nonlinear and transcendental facts as named inequalities when
possible. Tune performance only when a profile or repeated failure justifies it.

Name lemmas by their mathematical operation or conclusion; reuse established
namespace and suffix conventions. Add docstrings for source-facing declarations,
non-obvious encodings, and important side conditions, rather than narrating tactics.
