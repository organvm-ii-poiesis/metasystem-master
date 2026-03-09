# CLAUDE.md

This file provides guidance to Claude Code when working with this monorepo.

## Project Overview

**omni-dromenon-machina** is a real-time audience-participatory performance system. It enables collective audience control over live artistic performances through weighted consensus algorithms, with performers maintaining override authority.

**Core innovation:** Spatial and temporal weighting of audience inputs creates emergent group dynamics while preserving performer agency. P95 latency target: <2ms.

## Monorepo Structure

```
omni-dromenon-machina/
  .config/                      Tooling configs
  .github/                      CI/CD, community health
  docs/                         All documentation
    academic/                   Research papers
    architecture/               System architecture
    business/                   Prospecting, grant narratives
    community/                  Artist toolkit, templates
    flow-patterns/              Harmonic flow system
    guides/                     Setup, deployment, reference
    plans/                      Development plans
    reference/                  POC v0.1.0
    specs/                      Technical specifications
  examples/                     Reference implementations
    generative-music/           Music POC
    generative-visual/          Visual art reference
    choreographic-interface/    Choreography reference
    theatre-dialogue/           Theatre/dialogue reference
  infra/                        Infrastructure-as-code
    docker/                     Dockerfiles, compose
    gcp/                        Terraform, Cloud Run
    nginx/                      Reverse proxy config
    web/                        Static site (index.html)
  packages/                     Source code (pnpm workspaces)
    core-engine/                @omni-dromenon/core-engine (TypeScript)
    performance-sdk/            @omni-dromenon/performance-sdk (React)
    client-sdk/                 @omni-dromenon/client-sdk (TypeScript)
    audio-synthesis-bridge/     @omni-dromenon/audio-synthesis-bridge (TypeScript)
    orchestrate/                Multi-AI orchestration CLI (Python)
  tools/                        Build scripts, utilities
    scripts/                    Python/bash automation
    dreamcatcher/               Async sovereignty module
```

## Development Commands

### Workspace-Wide

```bash
pnpm install          # Install all dependencies
pnpm build            # Build all TypeScript packages
pnpm dev              # Start all packages in dev mode
pnpm test             # Run all tests
pnpm run typecheck    # Type-check all packages
```

### Core Engine

```bash
cd packages/core-engine
pnpm dev              # Development with hot reload (tsx)
pnpm build            # Build TypeScript
pnpm test             # Run tests (Vitest)
pnpm run test:bench   # Benchmark consensus latency
```

### Performance SDK

```bash
cd packages/performance-sdk
pnpm dev              # Development server (Vite)
pnpm build            # Build components
pnpm test             # Run tests
pnpm run lint         # Lint TypeScript/React
```

### Examples

All examples follow the same pattern:
```bash
cd examples/{generative-music,generative-visual,choreographic-interface,theatre-dialogue}
pnpm dev              # Start dev server
pnpm test             # Run integration tests
```

### Docker

```bash
docker compose up             # Full stack (core + SDK + Redis + Nginx)
docker compose up core-engine # Single service
```

### Python Orchestrate

```bash
cd packages/orchestrate
pip install -r requirements.txt
python src/orchestrator.py
```

## System Architecture

### Three-Layer System

1. **Core Engine** (`packages/core-engine/`)
   - WebSocket server (Express + Socket.io): `/audience` and `/performer` namespaces
   - Parameter Bus: Event-driven pub/sub (`src/bus/parameter-bus.ts`)
   - Consensus Engine: Weighted voting (`src/consensus/weighted-voting.ts`, `src/consensus/parameter-aggregation.ts`)
   - OSC Bridge: External synthesizer integration (`src/osc/osc-bridge.ts`)

2. **Performance SDK** (`packages/performance-sdk/`)
   - React components: `performer-dashboard/`, `audience-interface/`, `shared/`

3. **Audio Synthesis Bridge** (`packages/audio-synthesis-bridge/`)
   - OSC server + WebAudio engine + parameter mapping

### Data Flow

```
Audience Input -> Parameter Bus -> Consensus Aggregator -> Performer Override -> Output
                       |                                          |
                  Batch Processing                         WebSocket Broadcast
                       |                                          |
               Weighted Computation                    Dashboard + OSC
```

## Key Patterns

### Parameter Bus Events (`BusEvent` enum)
- `AUDIENCE_INPUT_BATCH` - Batched audience inputs
- `CONSENSUS_UPDATE` - New consensus value
- `PERFORMER_OVERRIDE` - Performer override applied
- `SESSION_START/PAUSE/RESUME/END` - Session lifecycle

### Performer Override Modes
- `absolute` - Replace consensus entirely
- `blend` - Mix with consensus (blendFactor)
- `lock` - Freeze parameter

### Consensus Computation Steps
1. Collect inputs within `inputWindowMs` window
2. Apply spatial weights (distance from stage)
3. Apply temporal weights (exponential decay)
4. Apply consensus weights (clustering alignment)
5. Compute weighted average
6. Apply smoothing and outlier rejection
7. Check for performer overrides
8. Broadcast result

## Configuration

### Environment Variables (core-engine)
- `PORT` (default: 3000)
- `REDIS_URL` (default: localhost:6379)
- `OSC_OUT_PORT` (default: 57121)
- `CONSENSUS_WINDOW_MS` (default: 1000)

### Consensus Weighting
Configured in `packages/core-engine/src/types/consensus.ts`:
- `spatialAlpha`, `temporalBeta`, `consensusGamma`
- Genre-specific presets: `GENRE_PRESETS`

## Testing

- **Framework:** Vitest for all TypeScript packages
- **Core tests:** `packages/core-engine/tests/`
- **Benchmarks:** `packages/core-engine/benchmarks/`
- Import: `import { describe, it, expect } from 'vitest'`

## Coding Style

- TypeScript: 2-space indent, semicolons, strict mode
- File naming: `kebab-case` for server modules, PascalCase for React components
- Package scope: `@omni-dromenon/*`
- Node version: >=18.0.0

## Technical Constraints

- Two WebSocket namespaces: `/audience` (many clients) and `/performer` (few, authenticated)
- Audience inputs are always batched - never process individually
- Performers can always override any parameter (core design principle)
- Redis required for session state in core-engine

## Performance Targets

- WebSocket latency: P95 < 2ms
- Consensus computation: < 1ms for 100 concurrent users
- Memory: < 500MB per service at 1000 connections

<!-- ORGANVM:AUTO:START -->
## System Context (auto-generated — do not edit)

**Organ:** ORGAN-II (Art) | **Tier:** flagship | **Status:** PUBLIC_PROCESS
**Org:** `organvm-ii-poiesis` | **Repo:** `metasystem-master`

### Edges
- **Produces** → `unspecified`: creative-artifact
- **Consumes** ← `ORGAN-I`: theory-artifact

### Siblings in Art
`core-engine`, `performance-sdk`, `example-generative-music`, `example-choreographic-interface`, `showcase-portfolio`, `archive-past-works`, `case-studies-methodology`, `learning-resources`, `example-generative-visual`, `example-interactive-installation`, `example-ai-collaboration`, `docs`, `a-mavs-olevm`, `a-i-council--coliseum`, `.github` ... and 14 more

### Governance
- Consumes Theory (I) concepts, produces artifacts for Commerce (III).

*Last synced: 2026-03-08T20:11:34Z*

## Session Review Protocol

At the end of each session that produces or modifies files:
1. Run `organvm session review --latest` to get a session summary
2. Check for unimplemented plans: `organvm session plans --project .`
3. Export significant sessions: `organvm session export <id> --slug <slug>`
4. Run `organvm prompts distill --dry-run` to detect uncovered operational patterns

Transcripts are on-demand (never committed):
- `organvm session transcript <id>` — conversation summary
- `organvm session transcript <id> --unabridged` — full audit trail
- `organvm session prompts <id>` — human prompts only


## Active Directives

| Scope | Phase | Name | Description |
|-------|-------|------|-------------|
| system | any | prompting-standards | Prompting Standards |
| system | any | research-standards-bibliography | APPENDIX: Research Standards Bibliography |
| system | any | research-standards | METADOC: Architectural Typology & Research Standards |
| system | any | sop-ecosystem | METADOC: SOP Ecosystem — Taxonomy, Inventory & Coverage |
| system | any | autopoietic-systems-diagnostics | SOP: Autopoietic Systems Diagnostics (The Mirror of Eternity) |
| system | any | cicd-resilience-and-recovery | SOP: CI/CD Pipeline Resilience & Recovery |
| system | any | cross-agent-handoff | SOP: Cross-Agent Session Handoff |
| system | any | document-audit-feature-extraction | SOP: Document Audit & Feature Extraction |
| system | any | essay-publishing-and-distribution | SOP: Essay Publishing & Distribution |
| system | any | market-gap-analysis | SOP: Full-Breath Market-Gap Analysis & Defensive Parrying |
| system | any | pitch-deck-rollout | SOP: Pitch Deck Generation & Rollout |
| system | any | promotion-and-state-transitions | SOP: Promotion & State Transitions |
| system | any | repo-onboarding-and-habitat-creation | SOP: Repo Onboarding & Habitat Creation |
| system | any | research-to-implementation-pipeline | SOP: Research-to-Implementation Pipeline (The Gold Path) |
| system | any | security-and-accessibility-audit | SOP: Security & Accessibility Audit |
| system | any | session-self-critique | session-self-critique |
| system | any | source-evaluation-and-bibliography | SOP: Source Evaluation & Annotated Bibliography (The Refinery) |
| system | any | stranger-test-protocol | SOP: Stranger Test Protocol |
| system | any | strategic-foresight-and-futures | SOP: Strategic Foresight & Futures (The Telescope) |
| system | any | typological-hermeneutic-analysis | SOP: Typological & Hermeneutic Analysis (The Archaeology) |

Linked skills: evaluation-to-growth


**Prompting (Anthropic)**: context 200K tokens, format: XML tags, thinking: extended thinking (budget_tokens)

<!-- ORGANVM:AUTO:END -->


## ⚡ Conductor OS Integration
This repository is a managed component of the ORGANVM meta-workspace.
- **Orchestration:** Use `conductor patch` for system status and work queue.
- **Lifecycle:** Follow the `FRAME -> SHAPE -> BUILD -> PROVE` workflow.
- **Governance:** Promotions are managed via `conductor wip promote`.
- **Intelligence:** Conductor MCP tools are available for routing and mission synthesis.
