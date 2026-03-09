# OmniDramanon Cold Storage

This directory preserves historical OmniDramanon-era material that no longer
belongs in the live `metasystem-master` root.

Use this directory for reference only.

- `deploy-scaffold/` contains old deploy exports and handoff bundles.
- `bundles/` contains archived zip and tarball artifacts.
- `metadata/` contains preserved stale snapshots that used to live at the root.
- `extracted/` contains leftover extracted archive material kept for provenance.

Do not use anything in this directory as current truth for:

- dependency mapping
- deployment shape
- package boundaries
- current documentation

For live repo structure, use `packages/`, `examples/`, `infra/`, `docs/`, and
the root manifests. For current downstream dependency truth, use sibling repo
`seed.yaml` `consumes` entries.
