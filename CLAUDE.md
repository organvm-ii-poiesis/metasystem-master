# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Meta-Repository Context

**omni-dromenon-machina** serves dual roles:

1. **Performance System**: Real-time audience-participatory performance platform (12 coordinated repositories)
2. **Universal Orchestrator**: Autonomous development system for ALL repositories in `/Users/4jp/Workspace/`

### Universal Orchestrator Mode

When functioning as universal orchestrator:
- Scans `/Users/4jp/Workspace/` for projects with `seed.yaml` files
- Manages autonomous multi-agent development across discovered projects
- Provides shared agent system (Architect, Implementer, Reviewer, Tester, Maintainer)
- Coordinates GitHub Actions CI/CD across managed repositories

**Managed Projects** (examples):
- `life-my--midst--in/` - Interactive CV system (has seed.yaml)
- Any other workspace project with `seed.yaml`

See `/Users/4jp/Workspace/UNIVERSAL-ORCHESTRATOR-ARCHITECTURE.md` for complete orchestrator architecture.

---

## Project Overview: Performance System

Omni-Dromenon-Engine is a real-time audience-participatory performance system. It enables collective audience control over live artistic performances through weighted consensus algorithms, with performers maintaining override authority.

**Core innovation:** Spatial and temporal weighting of audience inputs creates emergent group dynamics while preserving performer agency.

---

## Multi-Repository Architecture

This is a **master coordination repository** managing 12 sub-repositories:

### Core System (4 repos)
- `core-engine/` — WebSocket server, consensus algorithm, parameter bus
- `performance-sdk/` — React UI components (performer dashboard + audience interface)
- `client-sdk/` — WebSocket client library
- `audio-synthesis-bridge/` — OSC gateway for external synthesizers

### Theory & Documentation (2 repos)
- `docs/` — Technical specifications, API guides, deployment guides
- `academic-publication/` — Research papers, conference submissions

### Reference Implementations (4 repos)
- `example-generative-music/` — Music POC (P95 latency: 2ms ✅)
- `example-generative-visual/` — Visual art reference
- `example-choreographic-interface/` — Choreography reference
- `example-theatre-dialogue/` — Theatre/dialogue reference

### Community & Infrastructure (2 repos)
- `artist-toolkit-and-templates/` — Grant templates, deployment guides
- `.github/` — Organization-level CI/CD configuration

---

## System Architecture

### Three-Layer System

1. **Core Engine** (`core-engine/`)
   - WebSocket server (Express + Socket.io) with two namespaces: `/audience` and `/performer`
   - Parameter Bus: Event-driven pub/sub system (`bus/parameter-bus.ts`)
   - Consensus Engine: Weighted voting aggregation (`consensus/parameter-aggregation.ts`, `consensus/weighted-voting.ts`)
   - OSC Bridge: External synthesizer integration (`osc/osc-bridge.ts`)

2. **Performance SDK** (`performance-sdk/`)
   - React components split into three modules:
     - `performer-dashboard/` - Override controls, live parameter monitoring
     - `audience-interface/` - Parameter sliders, voting panels
     - `shared/` - Types, utilities, constants

3. **Audio Synthesis Bridge** (`audio-synthesis-bridge/`)
   - OSC server for external audio engines (SuperCollider, Max/MSP)
   - WebAudio synthesis engine for browser-based audio
   - Parameter mapping between consensus values and synthesis controls

### Data Flow

```
Audience Input → Parameter Bus → Consensus Aggregator → Performer Override (optional) → Output
                      ↓                                           ↓
                 Batch Processing                          WebSocket Broadcast
                      ↓                                           ↓
              Weighted Computation                    Performer Dashboard + OSC
```

**Key constraint:** P95 latency target is <2ms (validated in proof-of-concept).

---

## Development Commands

### Working Across All Repos

```bash
# From master repository root
cd /Users/4jp/Workspace/omni-dromenon-machina/omni-dromenon-machina

# Run command in all repos
for repo in core-engine performance-sdk client-sdk audio-synthesis-bridge; do
  (cd $repo && npm install)
done

# Build all repos
for repo in core-engine performance-sdk client-sdk audio-synthesis-bridge; do
  (cd $repo && npm run build)
done
```

### Core Engine

```bash
cd core-engine

# Development with hot reload
npm run dev

# Build TypeScript
npm run build

# Run all tests
npm test

# Run specific test file
npx vitest run tests/consensus.test.ts

# Benchmark consensus latency
npm run test:bench

# Production server
npm run build && npm start
```

### Performance SDK

```bash
cd performance-sdk

# Development server (Vite)
npm run dev

# Build components
npm run build

# Run tests
npm test

# Lint TypeScript/React
npm run lint
```

### Audio Synthesis Bridge

```bash
cd audio-synthesis-bridge

# Development mode
npm run dev

# Build
npm run build

# Tests
npm test
```

### Example Implementations

All examples follow the same pattern:
```bash
cd example-{generative-music,generative-visual,choreographic-interface,theatre-dialogue}

# Start server (connects to core-engine)
npm start

# Development mode with auto-reload
npm run dev

# Run integration tests
npm test
```

---

## Configuration

### Environment Variables (core-engine)
- `PORT` (default: 3000) - Server port
- `REDIS_URL` (default: localhost:6379) - Session state store
- `OSC_OUT_PORT` (default: 57121) - OSC output port
- `CONSENSUS_WINDOW_MS` (default: 1000) - Voting window duration

### Consensus Weighting
Configured in `core-engine/src/types/consensus.ts`:
- `spatialAlpha` - Weight for distance from stage
- `temporalBeta` - Weight for input recency
- `consensusGamma` - Weight for clustering alignment
- Genre-specific presets available: `GENRE_PRESETS`

---

## Key Architectural Patterns

### Parameter Bus Events
All inter-component communication uses typed events (`BusEvent` enum):
- `AUDIENCE_INPUT_BATCH` - Batched audience inputs for consensus
- `CONSENSUS_UPDATE` - New consensus value computed
- `PERFORMER_OVERRIDE` - Performer override applied
- `SESSION_START/PAUSE/RESUME/END` - Session lifecycle

Subscribe to events:
```typescript
bus.subscribe(BusEvent.CONSENSUS_UPDATE, (result) => {
  // Handle consensus result
});
```

### Performer Override Modes
Three override strategies (`performer-subscriptions.ts`):
- `absolute` - Replace consensus value entirely
- `blend` - Mix with consensus (specify `blendFactor`)
- `lock` - Freeze parameter (ignore audience input)

### Consensus Computation
The aggregator (`parameter-aggregation.ts`) processes inputs in batches:
1. Collects inputs within `inputWindowMs` window
2. Applies spatial weights (distance from stage)
3. Applies temporal weights (exponential decay)
4. Applies consensus weights (clustering alignment)
5. Computes weighted average
6. Applies smoothing and outlier rejection
7. Checks for performer overrides
8. Broadcasts result

---

## Testing Strategy

### Unit Tests
- Consensus algorithms: `core-engine/tests/consensus.test.ts`
- Parameter bus: `core-engine/tests/bus.test.ts`
- OSC bridge: `core-engine/tests/osc-bridge.test.ts`

Use Vitest for all tests. Import test utilities:
```typescript
import { describe, it, expect, beforeEach } from 'vitest';
```

### Integration Tests
Example implementations include integration tests validating end-to-end latency.

### Benchmarks
Performance-critical code has dedicated benchmarks in `core-engine/benchmarks/`.

---

## Project Coordination

This is a multi-repository project coordinated through `_COORDINATION_DOCS/`:
- Phase-based development plan (A through D)
- AI service orchestration templates
- Validation checklists

**Key coordination documents:**
- `_COORDINATION_DOCS/HANDOFF_MASTER.md` - Master orchestration plan
- `_COORDINATION_DOCS/PHASE_A_BRIEFING_TEMPLATES.md` - AI briefing templates
- `_COORDINATION_DOCS/AI_ORCHESTRATION_TIMELINE.md` - Phase breakdown
- `_COORDINATION_DOCS/PER_REPO_KEYS.md` - Per-repository entry points
- `_COORDINATION_DOCS/FINAL_SUMMARY.md` - Validation checklist

**Do not modify coordination docs unless explicitly requested.**

---

## Repository Layout

```
omni-dromenon-machina/
├── core-engine/                     # Main WebSocket server (TypeScript)
├── performance-sdk/                 # React UI components (TypeScript + React)
├── client-sdk/                      # WebSocket client library (TypeScript)
├── audio-synthesis-bridge/          # OSC gateway (TypeScript)
├── docs/                            # Technical specs and guides
├── academic-publication/            # Papers and conference submissions
├── example-generative-music/        # Music reference (JavaScript)
├── example-generative-visual/       # Visual art reference (JavaScript)
├── example-choreographic-interface/ # Choreography reference (JavaScript)
├── example-theatre-dialogue/        # Theatre/dialogue reference (JavaScript)
├── artist-toolkit-and-templates/    # Grant templates and deployment guides
├── .github/                         # Organization-level CI/CD
├── _COORDINATION_DOCS/              # Phase planning and AI orchestration
├── _archive/                        # Historical backups
└── CLAUDE.md                        # This file
```

---

## Common Development Patterns

### Adding a New Parameter
1. Define in `core-engine/src/types/performance.ts` (extend `ParameterDefinition`)
2. Add to `DEFAULT_PARAMETERS` array
3. Update UI components in `performance-sdk/shared/constants/parameters.ts`
4. Add synthesis mapping in `audio-synthesis-bridge/src/bridge/parameter-mapper.ts`

### Creating a New Example Implementation
1. Copy structure from `example-generative-music/`
2. Implement consensus integration in `src/server/consensus.js`
3. Create client interface in `src/public/`
4. Add integration test in `tests/`

### Modifying Consensus Algorithm
1. Update weighting logic in `core-engine/src/consensus/weighted-voting.ts`
2. Add tests in `core-engine/tests/consensus.test.ts`
3. Run benchmarks: `npm run test:bench`
4. Verify P95 latency remains <2ms

### Working with Coordination Docs
**When to read:**
- Starting work: Read `_COORDINATION_DOCS/PHASE_A_BRIEFING_TEMPLATES.md`
- Understanding vision: Read `_COORDINATION_DOCS/HANDOFF_MASTER.md`
- Before validation: Read `_COORDINATION_DOCS/FINAL_SUMMARY.md`

**When to modify:**
- Only when explicitly instructed
- Never during autonomous phases
- Always track changes in coordination doc changelog

---

## Multi-Repo Operations

### Push All Repos to GitHub

```bash
# From master repository root
./PUSH_ALL_REPOS.sh
```

See `PUSH_TO_GITHUB_INSTRUCTIONS.md` for details.

### Sync Across Repos

```bash
# Update all repos
for repo in */; do
  (cd $repo && git pull)
done

# Install dependencies in all repos
for repo in core-engine performance-sdk client-sdk audio-synthesis-bridge; do
  (cd $repo && npm install)
done
```

---

## Important Constraints

### Technical Constraints
- **Two WebSocket namespaces:** Always distinguish between `/audience` (many clients) and `/performer` (few clients, authenticated)
- **TypeScript strict mode:** Enabled in all TypeScript repos
- **Node version:** Requires Node.js >=18.0.0
- **Redis dependency:** Core engine uses Redis for session state (local development defaults to localhost:6379)
- **OSC output:** Port 57121 is standard for SuperCollider integration
- **Audience inputs are batched:** Never process individual inputs—always use `AUDIENCE_INPUT_BATCH` events
- **Performer authority:** Performers can always override any parameter; this is a core design principle

### Organizational Constraints
- **Multi-repo coordination:** Changes that span repos must be coordinated via `_COORDINATION_DOCS/`
- **Phase-based development:** Follow phases A→D as defined in coordination docs
- **Validation gates:** Human validation required at phase boundaries
- **Autonomous periods:** During autonomous phases (e.g., Dec 7-8), only log actions, don't request input

### Universal Orchestrator Constraints
- **When operating as orchestrator:** Respect `seed.yaml` constraints in managed projects
- **Discovery mode:** Auto-discover projects in `/Users/4jp/Workspace/` with `seed.yaml`
- **Agent boundaries:** Read access to workspace, write access only to allowed paths per `seed.yaml`
- **Quality gates:** Enforce test coverage, linting, type-checking per project rules

---

## Performance Targets

- **WebSocket latency:** P95 < 2ms (audience input → consensus output)
- **Consensus computation:** < 1ms for 100 concurrent audience members
- **Memory usage:** < 500MB per service at 1000 concurrent connections
- **CPU usage:** < 50% under normal load

---

## Related Projects in Workspace

If `seed.yaml` exists in these projects, they are managed by this orchestrator:

- `life-my--midst--in/` - Interactive CV/résumé system with autonomous development
- (Other projects will be auto-discovered)

See `UNIVERSAL-ORCHESTRATOR-ARCHITECTURE.md` in workspace root for full details.

---

**Last Updated:** 2025-12-26
**Universal Orchestrator:** Enabled
**Performance System:** 12 repositories coordinated
