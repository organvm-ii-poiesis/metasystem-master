# Repository Guidelines

Global policy: /Users/4jp/AGENTS.md applies and cannot be overridden.

## Project Structure & Module Organization

This is a **pnpm monorepo**. Key paths:

- `packages/` - Source code workspaces:
  - `core-engine/` - WebSocket server, consensus algorithm, parameter bus (TypeScript)
  - `performance-sdk/` - React UI components (TypeScript/React)
  - `client-sdk/` - WebSocket client library (TypeScript)
  - `audio-synthesis-bridge/` - OSC gateway (TypeScript)
  - `orchestrate/` - Multi-AI orchestration CLI (Python)
- `examples/` - Reference implementations (generative-music, generative-visual, choreographic-interface, theatre-dialogue)
- `docs/` - All documentation (architecture, guides, specs, plans, business, community)
- `infra/` - Docker, GCP, nginx, static site
- `tools/` - Build scripts, utilities

## Build, Test, and Development Commands

Run from monorepo root:
- `pnpm install` - Install all dependencies
- `pnpm build` - Build all TypeScript packages
- `pnpm dev` - Start all packages in dev mode
- `pnpm test` - Run all tests
- `docker compose up` - Full stack (core engine, SDK, Redis, nginx)

Per-package: `cd packages/core-engine && pnpm dev`, `pnpm build`, `pnpm test`

## Coding Style & Naming Conventions

- TypeScript: 2-space indent, semicolons, strict mode
- File naming: `kebab-case` for server modules, PascalCase for React components
- Package scope: `@omni-dromenon/*`
- Shared types stay in each package's local `src/shared/` area

## Testing Guidelines

- All TypeScript packages use Vitest (`pnpm test`)
- Tests in package-local `tests/` directories
- Add tests when changing behavior

## Commit & Pull Request Guidelines

- Single monorepo - commit and PR within this repository
- Use short, imperative commit summaries with scope when helpful (e.g., `core-engine: tighten consensus weights`)
- PRs should list touched packages, include test results

## Security & Configuration

- Keep secrets out of the repo; use environment variables or `.env` files
- For Docker-based local runs, set required env vars before starting the stack
