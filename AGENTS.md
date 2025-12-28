# Repository Guidelines

Global policy: /Users/4jp/AGENTS.md applies and cannot be overridden.

## Project Structure & Module Organization
This workspace is a deployment bundle plus a multi-repo source tree. Key paths:
- `omni-dromenon-machina/` is the master directory holding the actual codebases: `core-engine/`, `performance-sdk/`, `client-sdk/`, `audio-synthesis-bridge/`, example apps (`example-*`), `docs/`, `academic-publication/`, and `artist-toolkit-and-templates/`.
- `omni-dromenon-deploy/` contains the deployment scaffold (Docker, GCP, scripts, web assets).
- Root-level infrastructure files include `docker-compose.yml`, `Dockerfile.*`, `nginx.conf`, `terraform.tf`, and the static site (`index.html`, `styles.css`).

## Build, Test, and Development Commands
Run commands from the repo root unless noted.
- Bootstrap and local run: `./SETUP_AND_RUN.sh` (setup/extract) then `./START_LOCAL_IPHONE.sh` (starts Docker services and prints a LAN URL).
- Local stack: `docker-compose -f docker-compose.yml up` (core engine, SDK, Redis, Firestore emulator, nginx, optional audio bridge).
- Core engine: `cd omni-dromenon-machina/core-engine && npm run dev` (TSX watch), `npm run build`, `npm test`, `npm run test:bench`.
- Performance SDK: `cd omni-dromenon-machina/performance-sdk && npm run dev` (Vite), `npm run build`, `npm run test`, `npm run lint`.
- Example apps are standalone; follow their `package.json` scripts (e.g., `example-generative-music` uses `npm run dev`).

## Coding Style & Naming Conventions
- TypeScript/JavaScript uses 2-space indentation and semicolons (see `omni-dromenon-machina/core-engine/src`).
- File naming: `kebab-case` for server modules (e.g., `parameter-bus.ts`), PascalCase for React components (e.g., `VotingPanel.tsx`), and `useX.ts` for hooks.
- Keep shared types in each package’s local `src`/`shared` areas rather than inventing new cross-package folders.

## Testing Guidelines
- Core engine and performance SDK use Vitest (`npm test`).
- Tests appear alongside source (e.g., `core-engine/src/consensus/tests.ts`) or in package-local `tests/` directories.
- No repo-wide coverage thresholds are configured; add tests per package when changing behavior.

## Commit & Pull Request Guidelines
- Each folder under `omni-dromenon-machina/` is its own Git repo; commit and PR within the specific subproject.
- Current history is minimal and uses `Initial commit: <repo>` messages. Use short, imperative summaries and add a scope when helpful (e.g., `core-engine: tighten consensus weights`).
- PRs should list touched packages, include commands run and results, and attach screenshots for UI changes in `performance-sdk` or example UIs.

## Security & Configuration Tips
- Keep secrets out of the repo; use environment variables or local `.env` files referenced by the deployment docs.
- For Docker-based local runs, set any required env vars (e.g., `GCP_PROJECT_ID`) before starting the stack.
