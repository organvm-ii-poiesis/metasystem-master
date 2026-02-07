# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- pnpm workspace configuration with `packages/*` and `examples/*`
- Shared `tsconfig.base.json` (ES2022, strict mode)
- Multi-AI orchestration CLI (`packages/orchestrate/`) integrated from omni-orchestrate
- Hero README with architecture diagram, package table, quick start
- Comprehensive `.gitignore` for monorepo
- Root `LICENSE` (MIT)
- `CHANGELOG.md` (this file)

### Changed
- **Monorepo restructure**: Consolidated 12 separate git repositories into a single monorepo
  - Core packages moved to `packages/` (core-engine, performance-sdk, client-sdk, audio-synthesis-bridge)
  - Examples moved to `examples/` (generative-music, generative-visual, choreographic-interface, theatre-dialogue)
  - Documentation consolidated under `docs/` (guides, specs, plans, architecture, business, community)
  - Infrastructure moved to `infra/` (docker, gcp, nginx, web)
  - Scripts moved to `tools/scripts/`
  - Config files moved to `.config/`
- Package names normalized to `@omni-dromenon/*` scope
- CI workflow updated for monorepo (pnpm, path-based triggers)
- `docker-compose.yml` updated for new directory structure
- `CLAUDE.md` and `AGENTS.md` rewritten for monorepo layout

### Removed
- All nested `.git/` directories (histories preserved via `git filter-repo` merges)
- Obsolete multi-repo scripts (PUSH_ALL_REPOS.sh, DEPLOY_ALL.sh, etc.)
- Handoff artifacts (FINAL_HANDOFF.txt, DOWNLOAD_INSTRUCTIONS.txt, etc.)
- Dead files (syntax.css, README.md.bak)
- Root-level duplicates (terraform.tf, nginx.conf, index.html, styles.css)
- Stale docs (GEMINI.md, TODO.md)
- Tracked `_archive/` contents (now gitignored)
