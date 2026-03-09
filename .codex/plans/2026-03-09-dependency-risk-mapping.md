# Dependency Risk Mapping for metasystem-master

Date: 2026-03-09

## Summary
- Use sibling repo `seed.yaml` `consumes` entries as the authoritative direct dependency graph.
- Reconcile conflicting directory and metadata signals inside `metasystem-master`.
- Generate a Markdown audit that distinguishes live backplane consumers from stale or archival metadata.
- Leave target-repo comparison as a runtime argument to avoid hard-coding an unresolved repo identity.

## Implementation
- Add a Python utility under `tools/scripts/` to:
  - enumerate direct dependents of `organvm-ii-poiesis/metasystem-master`
  - classify active versus archived consumers
  - flag stale metadata such as `.meta/dependencies.json`
  - flag top-level archival directories that overlap the live repo surface
  - optionally analyze a target repo for public-package, documented-runtime, and private-surface coupling
- Generate an initial Markdown audit under `docs/architecture/`.
- Clarify active versus historical directory boundaries in `README.md`.

## Assumptions
- `seed.yaml` direct dependency declarations are canonical.
- `_archive/` is historical and should not be used as the live deployment or dependency surface.
- `ecosystem.yaml` and `.meta/dependencies.json` are advisory snapshots and may lag the true graph.
