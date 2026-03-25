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

**Organ:** ORGAN-II (Art) | **Tier:** flagship | **Status:** GRADUATED
**Org:** `organvm-ii-poiesis` | **Repo:** `metasystem-master`

### Edges
- **Produces** → `unspecified`: creative-artifact
- **Consumes** ← `ORGAN-I`: theory-artifact

### Siblings in Art
`core-engine`, `performance-sdk`, `example-generative-music`, `example-choreographic-interface`, `showcase-portfolio`, `archive-past-works`, `case-studies-methodology`, `learning-resources`, `example-generative-visual`, `example-interactive-installation`, `example-ai-collaboration`, `docs`, `a-mavs-olevm`, `a-i-council--coliseum`, `.github` ... and 16 more

### Governance
- Consumes Theory (I) concepts, produces artifacts for Commerce (III).

*Last synced: 2026-03-25T22:27:08Z*

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
| system | any | phase-closing-and-forward-plan | METADOC: Phase-Closing Commemoration & Forward Attack Plan |
| system | any | research-standards | METADOC: Architectural Typology & Research Standards |
| system | any | sop-ecosystem | METADOC: SOP Ecosystem — Taxonomy, Inventory & Coverage |
| system | any | autonomous-content-syndication | SOP: Autonomous Content Syndication (The Broadcast Protocol) |
| system | any | autopoietic-systems-diagnostics | SOP: Autopoietic Systems Diagnostics (The Mirror of Eternity) |
| system | any | background-task-resilience | background-task-resilience |
| system | any | cicd-resilience-and-recovery | SOP: CI/CD Pipeline Resilience & Recovery |
| system | any | community-event-facilitation | SOP: Community Event Facilitation (The Dialectic Crucible) |
| system | any | context-window-conservation | context-window-conservation |
| system | any | conversation-to-content-pipeline | SOP — Conversation-to-Content Pipeline |
| system | any | cross-agent-handoff | SOP: Cross-Agent Session Handoff |
| system | any | cross-channel-publishing-metrics | SOP: Cross-Channel Publishing Metrics (The Echo Protocol) |
| system | any | data-migration-and-backup | SOP: Data Migration and Backup Protocol (The Memory Vault) |
| system | any | document-audit-feature-extraction | SOP: Document Audit & Feature Extraction |
| system | any | dynamic-lens-assembly | SOP: Dynamic Lens Assembly |
| system | any | essay-publishing-and-distribution | SOP: Essay Publishing & Distribution |
| system | any | formal-methods-applied-protocols | SOP: Formal Methods Applied Protocols |
| system | any | formal-methods-master-taxonomy | SOP: Formal Methods Master Taxonomy (The Blueprint of Proof) |
| system | any | formal-methods-tla-pluscal | SOP: Formal Methods — TLA+ and PlusCal Verification (The Blueprint Verifier) |
| system | any | generative-art-deployment | SOP: Generative Art Deployment (The Gallery Protocol) |
| system | any | market-gap-analysis | SOP: Full-Breath Market-Gap Analysis & Defensive Parrying |
| system | any | mcp-server-fleet-management | SOP: MCP Server Fleet Management (The Server Protocol) |
| system | any | multi-agent-swarm-orchestration | SOP: Multi-Agent Swarm Orchestration (The Polymorphic Swarm) |
| system | any | network-testament-protocol | SOP: Network Testament Protocol (The Mirror Protocol) |
| system | any | open-source-licensing-and-ip | SOP: Open Source Licensing and IP (The Commons Protocol) |
| system | any | performance-interface-design | SOP: Performance Interface Design (The Stage Protocol) |
| system | any | pitch-deck-rollout | SOP: Pitch Deck Generation & Rollout |
| system | any | polymorphic-agent-testing | SOP: Polymorphic Agent Testing (The Adversarial Protocol) |
| system | any | promotion-and-state-transitions | SOP: Promotion & State Transitions |
| system | any | recursive-study-feedback | SOP: Recursive Study & Feedback Loop (The Ouroboros) |
| system | any | repo-onboarding-and-habitat-creation | SOP: Repo Onboarding & Habitat Creation |
| system | any | research-to-implementation-pipeline | SOP: Research-to-Implementation Pipeline (The Gold Path) |
| system | any | security-and-accessibility-audit | SOP: Security & Accessibility Audit |
| system | any | session-self-critique | session-self-critique |
| system | any | smart-contract-audit-and-legal-wrap | SOP: Smart Contract Audit and Legal Wrap (The Ledger Protocol) |
| system | any | source-evaluation-and-bibliography | SOP: Source Evaluation & Annotated Bibliography (The Refinery) |
| system | any | stranger-test-protocol | SOP: Stranger Test Protocol |
| system | any | strategic-foresight-and-futures | SOP: Strategic Foresight & Futures (The Telescope) |
| system | any | styx-pipeline-traversal | SOP: Styx Pipeline Traversal (The 7-Organ Transmutation) |
| system | any | system-dashboard-telemetry | SOP: System Dashboard Telemetry (The Panopticon Protocol) |
| system | any | the-descent-protocol | the-descent-protocol |
| system | any | the-membrane-protocol | the-membrane-protocol |
| system | any | theoretical-concept-versioning | SOP: Theoretical Concept Versioning (The Epistemic Protocol) |
| system | any | theory-to-concrete-gate | theory-to-concrete-gate |
| system | any | typological-hermeneutic-analysis | SOP: Typological & Hermeneutic Analysis (The Archaeology) |

Linked skills: cicd-resilience-and-recovery, continuous-learning-agent, evaluation-to-growth, genesis-dna, multi-agent-workforce-planner, promotion-and-state-transitions, quality-gate-baseline-calibration, repo-onboarding-and-habitat-creation, structural-integrity-audit


**Prompting (Anthropic)**: context 200K tokens, format: XML tags, thinking: extended thinking (budget_tokens)


## Ecosystem Status

- **delivery**: 0/3 live, 1 planned
- **content**: 0/2 live, 1 planned
- **community**: 0/1 live, 0 planned

Run: `organvm ecosystem show metasystem-master` | `organvm ecosystem validate --organ II`


## Entity Identity (Ontologia)

**UID:** `ent_repo_01KKKX3RVJK1NJPGZ9JTRSSN77` | **Matched by:** primary_name

Resolve: `organvm ontologia resolve metasystem-master` | History: `organvm ontologia history ent_repo_01KKKX3RVJK1NJPGZ9JTRSSN77`


## Live System Variables (Ontologia)

| Variable | Value | Scope | Updated |
|----------|-------|-------|---------|
| `active_repos` | 64 | global | 2026-03-25 |
| `archived_repos` | 54 | global | 2026-03-25 |
| `ci_workflows` | 106 | global | 2026-03-25 |
| `code_files` | 0 | global | 2026-03-25 |
| `dependency_edges` | 60 | global | 2026-03-25 |
| `operational_organs` | 8 | global | 2026-03-25 |
| `published_essays` | 29 | global | 2026-03-25 |
| `repos_with_tests` | 0 | global | 2026-03-25 |
| `sprints_completed` | 33 | global | 2026-03-25 |
| `test_files` | 0 | global | 2026-03-25 |
| `total_organs` | 8 | global | 2026-03-25 |
| `total_repos` | 127 | global | 2026-03-25 |
| `total_words_formatted` | 0 | global | 2026-03-25 |
| `total_words_numeric` | 0 | global | 2026-03-25 |
| `total_words_short` | 0K+ | global | 2026-03-25 |

Metrics: 9 registered | Observations: 15536 recorded
Resolve: `organvm ontologia status` | Refresh: `organvm refresh`


## System Density (auto-generated)

AMMOI: 56% | Edges: 41 | Tensions: 33 | Clusters: 5 | Adv: 7 | Events(24h): 23754
Structure: 8 organs / 127 repos / 1654 components (depth 17) | Inference: 98% | Organs: META-ORGANVM:64%, ORGAN-I:55%, ORGAN-II:47%, ORGAN-III:55% +4 more
Last pulse: 2026-03-25T22:27:04 | Δ24h: +3.5% | Δ7d: n/a


## Dialect Identity (Trivium)

**Dialect:** AESTHETIC_FORM | **Classical Parallel:** Music | **Translation Role:** The Poetry — proves formal structures have sensory form

Strongest translations: III (structural), V (analogical), VI (analogical)

Scan: `organvm trivium scan II <OTHER>` | Matrix: `organvm trivium matrix` | Synthesize: `organvm trivium synthesize`

<!-- ORGANVM:AUTO:END -->


## ⚡ Conductor OS Integration
This repository is a managed component of the ORGANVM meta-workspace.
- **Orchestration:** Use `conductor patch` for system status and work queue.
- **Lifecycle:** Follow the `FRAME -> SHAPE -> BUILD -> PROVE` workflow.
- **Governance:** Promotions are managed via `conductor wip promote`.
- **Intelligence:** Conductor MCP tools are available for routing and mission synthesis.
