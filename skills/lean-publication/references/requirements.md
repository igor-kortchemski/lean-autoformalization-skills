# Palomar requirements and sources

Checked on **28 October 2026**. This is a navigation aid, not a complete or
permanently pinned specification. Refresh the live policy, schema, and allowlists
for publication-sensitive design and the final GitHub or Palomar candidate;
refresh the pipeline when full verification is requested. Repository-specific
restrictions may be stricter. No source branch HEAD is claimed here.

## Source layout and dependencies

The [submission standard](https://github.com/PalomarRegistry/PalomarPolicy/blob/main/CONTRIBUTING.md)
governs these constraints:

| Item | Current constraint |
| --- | --- |
| Repository | Public GitHub snapshot, full 40-character commit, at most 500 MiB |
| Lake | Exactly one Lakefile at the selected project root; commit the manifest as the straightforward reproducible layout |
| Lean source | `module`; at most 10,000 physical lines per Lean file, including unused/generated files |
| Exceptions | `.git` and `.lake` excluded; `lakefile.lean` exempt only from module header; no `.lean` symlinks |
| Challenge | At most 1,000 lines and 100 KiB; aim comfortably below both |
| Git dependencies | Public credential-free GitHub HTTPS sources, pinned to full commits |
| Path dependencies | Generally allowed only inside the same snapshot; local policy may prohibit them |
| Repository content | No submodules, Git LFS pointers, or compiled outputs outside `.lake` |
| License | One recognized root license file, consistent with the metadata |

Preserve declaration visibility and exposed bodies required by the module
system. An allowed draft Challenge is not permission for extra proof holes in
the implementation. Inspect definitions behind the compared types as well as
the headline signatures.

Solution axiom closures may contain only `propext`, `Classical.choice`, and
`Quot.sound`: no `sorryAx`, native-evaluation axioms, or custom axioms.
Native-evaluation axiom names depend on the pinned toolchain. This applies
transitively to the actual proofs, not just to the visible Solution file.

## Toolchain and statement closure

The current minimum is `v4.35.0-rc2` in
[toolchains.json](https://raw.githubusercontent.com/PalomarRegistry/PalomarSubmission/main/toolchains.json).
Recheck it rather than automatically selecting this old minimum. When the project
uses canonical Mathlib, its toolchain must exactly equal the resolved,
authenticated Mathlib revision's toolchain, including patch and release-candidate
suffix. Do not update an existing project without its required authorization.

The [Challenge allowlist](https://raw.githubusercontent.com/PalomarRegistry/PalomarSubmission/main/allowed-challenge-repositories.json)
currently lists Mathlib, Tau Ceti, and CSLib roots with authenticated revisions
and manifest closures. The latter two have qualified trust. A registered
project is not automatically an admissible statement dependency. Prefer a
Mathlib-only interface when adequate; verify the entire import closure.

## Metadata and mathematical account

Read the current [official metadata example](https://github.com/PalomarRegistry/PalomarTemplate/blob/main/formalization.yaml)
and its linked schema. At this check it uses `version: v0.4`, project identity,
human authors and maintainers, license, classifications, sources, scope, proof
status, automation, fidelity, and review. Distinguish bibliographic authors
from other contributors. Explain original results versus new proofs of known
results, and identify any substantive development behind a wrapper.

Report actual evidence. Exclude deliberate Challenge holes from implementation
proof-hole counts; do not turn an unknown count into zero. Explain every
advertised theorem in ordinary mathematical language and disclose deviations.

## Authority and changing documentation

The [protocol specification](https://github.com/PalomarRegistry/PalomarPolicy/blob/main/docs/specification.md)
defines the publication and verification contract. Mechanical success and
source fidelity are distinct; registration is not human peer review.

Some overview/template prose differed at the check date, notably over CSLib
and verifier implementation details. Read the binding standard and protocol,
then the current machine policy and official report. Do not silently choose
the weakest interpretation. If a conflict affects the intended deposit,
resolve it or state that compliance remains unconfirmed.
