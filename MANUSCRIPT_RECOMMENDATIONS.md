# Manuscript recommendations

These observations arise from formalization and may help human readers. This
file does not authorize the formalizer to rewrite or expand the manuscript, and
it may remain empty. Clarity and optional recommendations are advisory; an
unresolved correctness issue must still be repaired or explicitly qualified
before claiming that the manuscript is correct.

Use three categories:

- **Correctness issue:** the manuscript needs repair or an explicit qualification.
- **Clarity recommendation:** likely to improve understanding.
- **Optional observation:** potentially useful but not worth interrupting the
  formalization.

## R1 — [Short title]

- **Location:** [section, result, page, or paragraph]
- **Category:** [Correctness issue / Clarity recommendation / Optional observation]
- **Observation:** [what the formalization revealed]
- **Recommendation:** [specific proposed improvement]
- **Reason:** [why this helps correctness or understanding]
- **Priority:** [High / Normal / Optional]
- **Status:** [Pending / Accepted / Rejected / Implemented]

Useful observations include:

- hidden or ambiguous assumptions;
- quantifier order and dependence of constants;
- implicit domain restrictions or boundary cases;
- notation introduced too early or used too little;
- a conceptually important lemma that deserves a name;
- a clearer decomposition revealed by the formal proof;
- redundant hypotheses or a natural strengthening;
- a simpler proof route that the manuscript might adopt;
- places where the written proof is more intuitive and should remain even if
  Lean uses a different implementation.

Do not fill this file with tactic choices, code organization, or recommendations
whose only benefit is shorter Lean code. A correctness issue should also be
recorded in the existing equivalent coverage record or `FORMALIZATION_REPORT.md`
when it affects coverage or correspondence.
