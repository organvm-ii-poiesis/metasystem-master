# metasystem-master Backplane Audit

Generated: 2026-03-09 16:07 UTC

## Summary
- Direct dependents from sibling `seed.yaml` files: 11
- Active or candidate dependents: 8
- Archived dependents still pointing at the backplane: 3
- Promotion states in the current blast radius: ARCHIVED: 3, CANDIDATE: 8
- Target repo analysis: not run. Re-run with `--target-repo <path-or-name>`.

## Current Direct Dependents

| Repo | Org | Lifecycle | Promotion | Notes |
| --- | --- | --- | --- | --- |
| `a-i-council--coliseum` | `organvm-ii-poiesis` | `active` | `CANDIDATE` | Depends on organvm-ii-poiesis/metasystem-master; organvm-ii-poiesis/metasystem-master |
| `audio-synthesis-bridge` | `organvm-ii-poiesis` | `active` | `CANDIDATE` | Depends on organvm-ii-poiesis/metasystem-master; organvm-ii-poiesis/metasystem-master |
| `client-sdk` | `organvm-ii-poiesis` | `active` | `CANDIDATE` | Depends on organvm-ii-poiesis/metasystem-master; organvm-ii-poiesis/metasystem-master |
| `core-engine` | `omni-dromenon-machina` | `active` | `CANDIDATE` | Depends on metasystem-master for manifest and orchestration; omni-dromenon-machina/metasystem-master |
| `docs` | `omni-dromenon-machina` | `archived` | `ARCHIVED` | organvm-ii-poiesis/metasystem-master |
| `example-choreographic-interface` | `organvm-ii-poiesis` | `active` | `CANDIDATE` | Depends on organvm-ii-poiesis/metasystem-master; organvm-ii-poiesis/metasystem-master |
| `example-generative-music` | `organvm-ii-poiesis` | `active` | `CANDIDATE` | Depends on organvm-ii-poiesis/metasystem-master; organvm-ii-poiesis/metasystem-master |
| `example-generative-visual` | `omni-dromenon-machina` | `archived` | `ARCHIVED` | organvm-ii-poiesis/metasystem-master |
| `example-interactive-installation` | `organvm-ii-poiesis` | `active` | `CANDIDATE` | Depends on organvm-ii-poiesis/metasystem-master; organvm-ii-poiesis/metasystem-master |
| `example-theatre-dialogue` | `organvm-ii-poiesis` | `active` | `CANDIDATE` | Depends on organvm-ii-poiesis/metasystem-master; organvm-ii-poiesis/metasystem-master |
| `performance-sdk` | `omni-dromenon-machina` | `archived` | `ARCHIVED` | organvm-ii-poiesis/metasystem-master |

## Confusion Sources

- None detected.

## Cleanup Direction

- Treat `packages/`, `examples/`, `infra/`, and `docs/` as the live repo surface.
- Keep historical OmniDramanon artifacts under `docs/reference/omnidramanon-cold-storage/` and out of the repo root.

## Target Repo Analysis

- No target repo was supplied, so version-bump analysis is intentionally omitted.
