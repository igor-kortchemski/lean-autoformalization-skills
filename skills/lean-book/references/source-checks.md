# Checks between the book and a Lean statement

Apply what is relevant while designing and reviewing a statement. The
elaborated statement and the definitions behind its notation are what count,
not the source code's appearance.

## Reading the source

- Read the whole claim and the conventions it inherits from its section,
  chapter, and the book's preliminaries; a standing assumption stated once
  applies to everything after it.
- Treat converted text as fallible. Compare uncertain formulas, quantifiers,
  indices, and labels with the page image, and expect silent typo "fixes" by a
  transcriber in both directions.
- Read the errata register entry for the item, and the entries of the results
  its proof uses.
- Identify the parts of a multipart result and the assumptions each part uses.

## Any book

- Quantifier order and the dependence of constants: a uniform constant must not
  become dependent on a parameter.
- Hypotheses introduced implicitly by instances, coercions, or section
  variables.
- Empty cases, boundary values, and degenerate parameters.
- Totalized operations outside their intended domain (division by zero, junk
  values of a supremum, a real integral of a non-integrable function), and
  whether a default value does the mathematical work.
- Whether a hypothesis supplies the conclusion, or the hypotheses are jointly
  unsatisfiable in the intended examples.
- Whether a structure field or predicate carries the hard conclusion.

## Probability and measure theory

- Measurability versus almost-everywhere measurability; the σ-algebras and
  measures actually used.
- Pointwise equality, almost-sure equality, equality in distribution,
  modifications, and indistinguishability.
- One null set for each parameter versus one common null set.
- Integrability, finiteness, σ-finiteness, probability normalization, and
  extended-valued arithmetic.
- Standard Borel, topological, separability, completeness, nonemptiness, and
  countability assumptions, and the book's own names for them.
- Versions of conditional expectations and distributions, completion of
  σ-algebras, and changes of the underlying measure.
- Filtrations, stopping times, index sets, and path regularity.
- A random variable "with law μ" in the book against a push-forward measure in
  Mathlib, and the bridge between them.

Add a short checklist for another field when the book needs one, and keep it
next to this file.
