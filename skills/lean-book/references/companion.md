# The reading companion

The companion lets a reader find a book item and reach the Lean declarations.
It is not a dependency of the mathematical library.

## Components and authority

| Component | Role |
| --- | --- |
| Lean library | Definitions, statements, and proofs, usable downstream |
| Correspondence records | Locators, scope, differences, and review decisions |
| Companion | Book-order table, original exposition where useful, status display |
| API documentation | Exact declaration types, imports, and source links (doc-gen4) |
| Generated export | Revision-specific validation and correspondence data |

Each editorial field has one home. If a catalog and a blueprint coexist, one
generates or references the other's overlapping data; nobody updates status in
two places.

## Version 1

Build doc-gen4 API documentation in a nested project and generate a table from
the catalog, in book order, linking items and declarations to doc-gen4 anchors.
Include precise source references, covered and missing parts, and generated
validation and correspondence statuses. Any prose is independently written;
link formal statements and useful compiled examples at the matching revision.

The library builds without the companion toolchain. Pin the tools to commits;
when doc-gen4 imports the library, use the same Lean toolchain and Mathlib
revision as the library. Keep a working existing stack unless a concrete
benefit justifies migrating it.

Use Verso Blueprint or classic leanblueprint only when dependency-graph
planning or substantial exposition calls for a blueprint. Use documented
interfaces: Verso Blueprint describes `vbp query` JSON as unstable, and
leanblueprint's `\leanok` is an author's assertion, not an acceptance check. Do
not maintain two complete companions.

Search, additional navigation routes, keyboard-specific UI, and dependency
graphs are optional later improvements. Live editing needs a running Lean
server, so it is not part of a static version 1.

## Rights in published output

Publish original Lean code, independently written explanations, and precise
references. Check generated HTML, search indexes, exports, logs, and
downloadable artifacts for book text before each deployment. Reproducing
publisher material needs established rights; this skill gives no legal
clearance. State the license of original code and of original prose, and keep
third-party attribution and license notices.
