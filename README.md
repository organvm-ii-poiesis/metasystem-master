# Omni-Dromenon Engine (metasystem-master)

[![CI](https://github.com/organvm-ii-poiesis/metasystem-master/actions/workflows/ci.yml/badge.svg)](https://github.com/organvm-ii-poiesis/metasystem-master/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-pending-lightgrey)](https://github.com/organvm-ii-poiesis/metasystem-master)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/organvm-ii-poiesis/metasystem-master/blob/main/LICENSE)
[![Organ II](https://img.shields.io/badge/Organ-II%20Poiesis-EC4899)](https://github.com/organvm-ii-poiesis)
[![Status](https://img.shields.io/badge/status-active-brightgreen)](https://github.com/organvm-ii-poiesis/metasystem-master)
[![TS+Python](https://img.shields.io/badge/lang-TS%2BPython-informational)](https://github.com/organvm-ii-poiesis/metasystem-master)


[![ORGAN-II: Poiesis](https://img.shields.io/badge/ORGAN--II-Poiesis-6a1b9a?style=flat-square)](https://github.com/organvm-ii-poiesis)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)
[![TypeScript](https://img.shields.io/badge/TypeScript-strict-blue?style=flat-square)](tsconfig.base.json)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square)](packages/orchestrate)
[![pnpm Workspace](https://img.shields.io/badge/pnpm-workspace-F69220?style=flat-square)](pnpm-workspace.yaml)
[![Node](https://img.shields.io/badge/node-%3E%3D18.0.0-339933?style=flat-square)](package.json)
[![Status](https://img.shields.io/badge/status-active--development-yellow?style=flat-square)]()

> A real-time audience-participatory performance engine where collective audience input shapes live art through weighted consensus algorithms — while performers retain expressive override authority.

[Artistic Purpose](#artistic-purpose) | [Conceptual Approach](#conceptual-approach) | [System Architecture](#system-architecture) | [Package Reference](#package-reference) | [Installation](#installation) | [Quick Start](#quick-start) | [Working Examples](#working-examples) | [API Reference](#api-reference) | [Configuration Deep Dive](#configuration-deep-dive) | [Theory Implemented](#theory-implemented) | [Portfolio & Exhibition](#portfolio--exhibition) | [Cross-References](#cross-references) | [Contributing](#contributing) | [License & Author](#license--author)

---

## Artistic Purpose

Live performance has always been a negotiation between performers and audiences. Applause, silence, laughter, restlessness — these are the audience's instruments, and performers have always read them, consciously or not. But these feedback channels are coarse. An audience member cannot communicate "I want the texture to thin out while the harmonic tension increases." They can only clap or not clap. The performer receives a blurred aggregate of approval or discomfort, filtered through the performer's own interpretive biases.

Omni-Dromenon Engine makes this negotiation explicit and fine-grained. Audience members control continuous performance parameters — mood, tempo, intensity, density, texture, harmony, rhythm, spatial positioning — through their phones. Their inputs are aggregated in real time through a three-axis weighted consensus algorithm that accounts for spatial proximity (closer to the stage = higher weight), temporal recency (recent inputs outweigh stale ones), and cluster agreement (inputs that align with emerging consensus carry more weight). The result is a continuously updated set of values that shape the performance: what key the music is in, how fast the dancer moves, which branch of a theatrical narrative unfolds next.

The critical design decision — the one that separates this from polling or voting apps — is **performer override**. The performer is never subordinate to the crowd. Three override modes (`absolute`, `blend`, and `lock`) give the performer graduated control: they can fully override a parameter, blend their intent with the audience's at any ratio, or lock a parameter against audience input entirely. This produces a creative dynamic that does not exist in conventional performance: the audience is genuinely shaping the art, but the performer retains the authority to resist, redirect, or amplify what the audience wants. The resulting performances are neither dictated by the crowd nor indifferent to it. They are negotiated in real time, at sub-second latency, across every parameter the performer exposes.

This system exists because the tools for live interactive performance are either too simple (binary voting, applause meters) or too complex (custom Max/MSP patches that take months to build for each new piece). Omni-Dromenon provides a general-purpose engine that works across genres — electronic music, ballet, opera, installation art, interactive theatre — while remaining configurable enough that each genre can tune the weighting algorithm to match its aesthetic priorities.

---

## Conceptual Approach

### The Democratic Instrument

Most interactive performance systems treat the audience as a data source: inputs go in, decisions come out, the system is transparent. Omni-Dromenon treats the audience as a **co-performer** operating a collective instrument. Each audience member's phone becomes a control surface, but no single person controls the output. The consensus algorithm produces emergent group behavior — tendencies, swells, sudden convergences, gradual drifts — that no individual intended but that the group collectively authored.

This design is rooted in a specific philosophical position about authorship in live art: that the most interesting creative outcomes emerge from constrained negotiation, not from unilateral control or pure democracy. The performer's override authority is not a safety valve — it is a compositional tool. A performer who senses the audience pulling toward intensity can resist, creating tension that the audience then pushes harder against, which the performer eventually releases. This dynamic is impossible in systems where either party has absolute control.

### Spatial and Temporal Weighting

Not all inputs are equal, and the system explicitly acknowledges this through its weighting model. Spatial weighting uses exponential decay from the stage position: an audience member standing two meters from a dancer has more influence than one at the back of a 500-seat theatre. This is not an arbitrary hierarchy — it reflects the physical reality that proximity to a performance creates a qualitatively different relationship to it. The person in the front row is in the performer's peripheral vision, breathing the same air, sharing the same acoustic space. Their inputs should carry more weight because they are in a more intimate dialogue with the performer.

Temporal weighting ensures that the system responds to the audience's current state, not its historical average. Inputs decay exponentially within a configurable window (default: 5 seconds). An audience member who was enthusiastic three minutes ago but has since disengaged does not continue to push the consensus. The system forgets, in the same way that a performer reading a room forgets that the audience was energetic during the opening number — what matters is how they feel right now.

Consensus weighting detects clusters: when multiple audience members converge on similar values, their agreement amplifies their collective weight. This creates a natural feedback loop where emerging consensus becomes self-reinforcing, producing decisive group movements rather than a perpetual average.

### Genre Presets as Aesthetic Configuration

The three weighting axes (`spatialAlpha`, `temporalBeta`, `consensusGamma`) must sum to approximately 1.0, and their relative values encode aesthetic priorities. The system ships with five genre presets, defined in [`packages/core-engine/src/types/consensus.ts`](packages/core-engine/src/types/consensus.ts):

| Genre | Spatial (alpha) | Temporal (beta) | Consensus (gamma) | Aesthetic Rationale |
|-------|---------|----------|-----------|-------------------|
| Electronic Music | 0.3 | 0.5 | 0.2 | Temporal responsiveness drives rhythmic immediacy |
| Ballet | 0.5 | 0.2 | 0.3 | Spatial proximity to the dancer is the primary relationship |
| Opera | 0.2 | 0.3 | 0.5 | Collective agreement produces dramatic coherence |
| Installation | 0.7 | 0.1 | 0.2 | Location within the installation space is almost everything |
| Theatre | 0.4 | 0.3 | 0.3 | Balanced — narrative responsiveness requires all three axes |

These are not arbitrary numbers. Each encodes a claim about what matters most in that genre's audience-performer relationship. A ballet audience's spatial position relative to the dancer is the primary determinant of their aesthetic experience; an electronic music audience's moment-to-moment energy matters more than where they are standing. The presets are starting points — every deployment can tune them for a specific piece.

---

## System Architecture

### Three-Layer Design

```
┌─────────────────────────────────────────────────────────────────┐
│                         NGINX REVERSE PROXY                     │
│                    (infra/nginx/nginx.conf)                      │
├──────────────────────┬──────────────────────────────────────────┤
│                      │                                          │
│  ┌───────────────────▼──────────────────┐                      │
│  │         CORE ENGINE (Port 3000)       │                      │
│  │    packages/core-engine/              │                      │
│  │                                       │                      │
│  │  ┌──────────┐  ┌──────────────────┐  │   ┌───────────────┐ │
│  │  │ Express  │  │  Socket.io       │  │   │  Redis 7      │ │
│  │  │ REST API │  │  /audience  ns   │  │◄──│  Session State │ │
│  │  │          │  │  /performer ns   │  │   │  (Port 6379)  │ │
│  │  └────┬─────┘  └──────┬───────────┘  │   └───────────────┘ │
│  │       │               │              │                      │
│  │  ┌────▼───────────────▼───────────┐  │   ┌───────────────┐ │
│  │  │       PARAMETER BUS            │  │   │  ChromaDB      │ │
│  │  │  Event-driven pub/sub          │  │   │  Vector Store  │ │
│  │  │  (src/bus/parameter-bus.ts)    │  │◄──│  Long-term     │ │
│  │  └────────────┬───────────────────┘  │   │  Memory        │ │
│  │               │                      │   │  (Port 8000)  │ │
│  │  ┌────────────▼───────────────────┐  │   └───────────────┘ │
│  │  │     CONSENSUS AGGREGATOR       │  │                      │
│  │  │  Weighted voting + smoothing   │  │                      │
│  │  │  Cluster analysis + outliers   │  │                      │
│  │  │  (src/consensus/*.ts)          │  │                      │
│  │  └────────────┬───────────────────┘  │                      │
│  │               │                      │                      │
│  │  ┌────────────▼───────────────────┐  │                      │
│  │  │     OSC BRIDGE                 │  │                      │
│  │  │  SuperCollider / Max/MSP       │  │                      │
│  │  │  (src/osc/osc-bridge.ts)       │  │                      │
│  │  └────────────────────────────────┘  │                      │
│  └───────────────────────────────────────┘                      │
│                                                                  │
│  ┌───────────────────────────────────────┐                      │
│  │     PERFORMANCE SDK (Port 3001)       │                      │
│  │    packages/performance-sdk/          │                      │
│  │                                       │                      │
│  │  React 18 + Vite + Socket.io-client   │                      │
│  │  ┌──────────────┐ ┌────────────────┐ │                      │
│  │  │  Audience UI  │ │ Performer      │ │                      │
│  │  │  Sliders,     │ │ Dashboard,     │ │                      │
│  │  │  Voting Panel │ │ Override Panel │ │                      │
│  │  └──────────────┘ └────────────────┘ │                      │
│  └───────────────────────────────────────┘                      │
│                                                                  │
│  ┌───────────────────────────────────────┐                      │
│  │     AUDIO SYNTHESIS BRIDGE            │                      │
│  │    packages/audio-synthesis-bridge/   │                      │
│  │                                       │                      │
│  │  OSC Server + WebAudio Engine         │                      │
│  │  Parameter Mapping + Synthesis        │                      │
│  └───────────────────────────────────────┘                      │
└──────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Phone Input → WebSocket /audience → Parameter Bus → Batch Aggregation
                                          │
                                    Consensus Engine
                                    (spatial × temporal × cluster weights)
                                          │
                                    Outlier Rejection → Smoothing
                                          │
                                    Performer Override Check
                                    (absolute | blend | lock)
                                          │
                              ┌───────────┼───────────┐
                              ▼           ▼           ▼
                        Audience UI   Performer    OSC Output
                        (live values) Dashboard   (SuperCollider)
```

All audience inputs are **batched, never processed individually**. The consensus loop runs on a configurable interval (default: 50ms), computing weighted averages across the batch window, applying outlier rejection via z-score filtering (threshold: 2.5 standard deviations), exponential smoothing (factor: 0.3), and performer override resolution before broadcasting to all connected clients and OSC endpoints simultaneously.

### WebSocket Namespaces

The server maintains two strictly separated Socket.io namespaces:

- **`/audience`** — Many concurrent clients (target: 1,000+). Receives parameter sliders and location updates; emits consensus values and session state.
- **`/performer`** — Few authenticated clients. Full session control: start/pause/resume/end. Override any parameter. Receives real-time snapshots with participant counts and bus statistics.

Authentication is namespace-scoped: audience connections are anonymous (identified by `clientId`), while performer connections require a shared secret via the `auth` event before gaining override privileges.

---

## Package Reference

This is a **pnpm monorepo** (`pnpm@9.15.0`) with five packages and four example applications:

### `@omni-dromenon/core-engine`

The real-time WebSocket server. Express 4 + Socket.io 4 + Redis 4. Implements the consensus algorithm, parameter bus, OSC bridge, and session lifecycle.

| Component | Path | Purpose |
|-----------|------|---------|
| Server entry | `src/server.ts` | Express + Socket.io initialization, namespace routing |
| Parameter Bus | `src/bus/parameter-bus.ts` | Typed event emitter with 16 event types |
| Audience Inputs | `src/bus/audience-inputs.ts` | Input validation, rate limiting, batch collection |
| Performer Subs | `src/bus/performer-subscriptions.ts` | Auth, override management, session commands |
| Weighted Voting | `src/consensus/weighted-voting.ts` | Three-axis weighting, cluster analysis, smoothing |
| Aggregation | `src/consensus/parameter-aggregation.ts` | Per-parameter state, snapshot creation |
| OSC Bridge | `src/osc/osc-bridge.ts` | SuperCollider/Max integration via `osc` library |
| Type System | `src/types/consensus.ts`, `performance.ts` | Zod-validated schemas, genre presets |
| Middleware | `src/middleware/auth.ts`, `rate-limit.ts`, `validation.ts` | Request pipeline |
| Benchmarks | `benchmarks/latency-test.ts` | P95 latency validation |

**Dependencies:** Express, Socket.io, Redis, osc, Zod. **Dev:** TypeScript 5.3, tsx, Vitest.

### `@omni-dromenon/performance-sdk`

React 18 component library for performer and audience interfaces. Built with Vite.

| Component | Path | Purpose |
|-----------|------|---------|
| Audience Sliders | `src/audience-interface/components/ParameterSlider.tsx` | Touch-optimized parameter controls |
| Voting Panel | `src/audience-interface/components/VotingPanel.tsx` | Discrete voting interface |
| Connection Hook | `src/audience-interface/hooks/useConnection.ts` | WebSocket lifecycle management |
| Voting Hook | `src/audience-interface/hooks/useVoting.ts` | Input debouncing and submission |
| Live Parameters | `src/performer-dashboard/components/LiveParameters.tsx` | Real-time consensus visualization |
| Override Panel | `src/performer-dashboard/components/OverridePanel.tsx` | Three-mode override controls |
| Performer Status | `src/performer-dashboard/components/PerformerStatus.tsx` | Session state and bus statistics |
| Bus Subscription | `src/performer-dashboard/hooks/useBusSubscription.ts` | Server-push event binding |
| Override Hook | `src/performer-dashboard/hooks/useOverride.ts` | Override request/clear lifecycle |
| Wallet Login | `src/auth/WalletLogin.tsx` | Solana wallet adapter integration |

**Peer deps:** React 18, React DOM 18. **Dependencies:** Socket.io-client, React Router 6, Solana wallet adapter stack (`@solana/wallet-adapter-*`, `@solana/web3.js`).

### `@omni-dromenon/audio-synthesis-bridge`

Translates consensus parameter values into audio control signals. Dual output: OSC messages (for SuperCollider, Max/MSP, Ableton) and WebAudio API (for browser-native synthesis).

| Component | Path | Purpose |
|-----------|------|---------|
| Bridge Entry | `src/bridge/index.ts` | Initialization, routing |
| Parameter Mapper | `src/bridge/parameter-mapper.ts` | Consensus values to synthesis params |
| OSC Server | `src/osc/osc-server.ts` | UDP message dispatch |
| Message Parser | `src/osc/message-parser.ts` | Incoming OSC parsing |
| Audio Context | `src/webaudio/audio-context.ts` | Browser AudioContext management |
| Synthesis Engine | `src/webaudio/synthesis-engine.ts` | Web Audio synthesis |

### `@omni-dromenon/client-sdk`

Lightweight WebSocket client for embedding audience participation into any web page. Intended for third-party integrations where the full Performance SDK is unnecessary.

### `packages/orchestrate`

A Python-based multi-AI orchestration CLI. Dispatches prompts to multiple LLM providers (ChatGPT, Gemini, Copilot, Grok, Perplexity) through a gated pipeline with five phases: research, specification, messaging, implementation, vulnerability analysis. Each gate validates outputs before advancing.

| Component | Path | Purpose |
|-----------|------|---------|
| Orchestrator | `src/orchestrator.py` | Pipeline execution engine |
| Gate Validator | `src/utils/gate_validator.py` | Phase gate validation logic |
| Prompt Templates | `src/utils/prompt_templates.py` | Phase-specific prompt construction |
| Result Aggregator | `src/utils/result_aggregator.py` | Multi-provider response synthesis |
| Service Handlers | `src/services/*.py` | Provider-specific API adapters |

---

## Installation

### Prerequisites

- **Node.js** >= 18.0.0
- **pnpm** >= 8.0.0 (recommended: 9.15.0)
- **Docker** + **Docker Compose** (for Redis, ChromaDB, full-stack deployment)
- **Python** 3.11+ (for the `orchestrate` package only)
- **SuperCollider** (optional, for audio synthesis via OSC)

### From Source

```bash
# Clone the repository
git clone https://github.com/organvm-ii-poiesis/metasystem-master.git
cd metasystem-master

# Install all dependencies (pnpm workspaces)
pnpm install

# Build all TypeScript packages
pnpm build

# Run all tests
pnpm test
```

### Docker (Full Stack)

```bash
# Start all services: core-engine, performance-sdk, Redis, ChromaDB, Nginx
docker compose up

# Services will be available at:
#   Core Engine:      http://localhost:3000
#   Performance SDK:  http://localhost:3001
#   ChromaDB:         http://localhost:8000
#   Redis:            localhost:6379
#   Nginx (proxy):    http://localhost:80
```

### Docker (Core Engine Only)

```bash
docker compose up core-engine redis
```

### Python Orchestrator

```bash
cd packages/orchestrate
pip install -r requirements.txt
python src/orchestrator.py
```

---

## Quick Start

### 1. Start the Core Engine

```bash
cd packages/core-engine
pnpm dev
```

The server starts on port 3000 with two WebSocket namespaces:

```
╔═══════════════════════════════════════════════════════╗
║         OMNI-DROMENON-ENGINE CORE SERVER              ║
╠═══════════════════════════════════════════════════════╣
║  WebSocket (Audience):   ws://localhost:3000/audience  ║
║  WebSocket (Performer):  ws://localhost:3000/performer ║
║  REST Health:            GET /health                   ║
║  REST Session:           GET /session                  ║
║  REST Values:            GET /values                   ║
╚═══════════════════════════════════════════════════════╝
```

### 2. Start the Performance SDK

```bash
cd packages/performance-sdk
pnpm dev
```

Opens the React dashboard on port 3001. Navigate to `/performer` for the override panel or `/audience` for the input interface.

### 3. Connect as an Audience Member

```javascript
import { io } from "socket.io-client";

const socket = io("ws://localhost:3000/audience", {
  query: { clientId: "audience-001" }
});

socket.on("session:state", (state) => {
  console.log("Parameters:", state.parameters);
  console.log("Current values:", state.values);
});

// Send a parameter input (normalized 0-1)
socket.emit("input", { parameter: "mood", value: 0.8 });

// Update spatial location (for proximity weighting)
socket.emit("location", { x: 25, y: 10, zone: "front" });

// Receive live consensus values
socket.on("values", (values) => {
  console.log("Consensus:", values);
});
```

### 4. Connect as a Performer

```javascript
const performer = io("ws://localhost:3000/performer", {
  query: { performerId: "performer-001", displayName: "Conductor" }
});

// Authenticate
performer.emit("auth", { secret: process.env.PERFORMER_SECRET });

performer.on("auth:success", () => {
  // Start the session
  performer.emit("session:start");

  // Override mood to maximum intensity
  performer.emit("override", {
    parameter: "mood",
    value: 1.0,
    mode: "absolute"
  });

  // Blend with audience — 70% performer, 30% audience
  performer.emit("override", {
    parameter: "tempo",
    value: 0.9,
    mode: "blend",
    blendFactor: 0.7
  });

  // Lock density so audience cannot change it
  performer.emit("override", {
    parameter: "density",
    value: 0.4,
    mode: "lock"
  });

  // Clear an override, returning control to audience
  performer.emit("override:clear", { parameter: "mood" });
});

// Receive real-time snapshots
performer.on("snapshot", (snap) => {
  console.log(`${snap.participants} participants, values:`, snap.values);
});
```

### 5. Verify the System

```bash
# Health check
curl http://localhost:3000/health

# Current session state
curl http://localhost:3000/session

# Live consensus values
curl http://localhost:3000/values
```

---

## Working Examples

The `examples/` directory contains four genre-specific reference implementations, each a self-contained pnpm package:

### Generative Music

```bash
cd examples/generative-music
pnpm install && pnpm dev
```

Audience members control pitch, rhythm, and intensity. The server computes consensus and forwards values to SuperCollider via OSC. Includes a custom `osc-bridge.js` that maps consensus parameters to synthesis control signals, a performer HTML dashboard, and an integration test suite.

**Files:** `src/server/consensus.js` (simplified weighting), `src/server/osc-bridge.js` (SuperCollider output), `src/public/client.js` (audience UI), `src/public/performer.html` (override panel).

### Generative Visual

```bash
cd examples/generative-visual
pnpm install && pnpm dev
```

Audience controls drive WebGL shaders in real time. Custom vertex and fragment shaders (`src/shaders/vertex.glsl`, `src/shaders/fragment.glsl`) receive consensus parameters as uniforms. Color palette, distortion intensity, and animation speed respond to collective audience input.

### Choreographic Interface

```bash
cd examples/choreographic-interface
pnpm install && pnpm dev
```

Integrates pose detection (`src/motion/pose-detector.js`) with consensus-weighted movement mapping (`src/motion/movement-mapper.js`). Designed for dance performances where a camera tracks the performer's body and audience input modulates the movement interpretation — how literally or abstractly the body's motion is translated to visual/sonic output.

### Theatre Dialogue

```bash
cd examples/theatre-dialogue
pnpm install && pnpm dev
```

A branching narrative engine where audience consensus selects dialogue paths. The `src/dialogue/script-engine.js` loads a tree-structured script and the `src/dialogue/branch-selector.js` maps consensus values to branch decisions. Performers can lock branches to prevent audience from derailing critical narrative beats.

---

## API Reference

### REST Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Server health, session ID, participant counts, uptime |
| `GET` | `/session` | Full session state: parameters, venue geometry, current values, bus stats |
| `GET` | `/values` | Current consensus values for all parameters |

### WebSocket Events — Audience (`/audience`)

| Direction | Event | Payload | Description |
|-----------|-------|---------|-------------|
| Server → Client | `session:state` | `{ sessionId, status, parameters, values }` | Sent on connection |
| Client → Server | `input` | `{ parameter: string, value: number }` | Parameter input (0-1) |
| Client → Server | `location` | `{ x: number, y: number, zone?: string }` | Spatial position update |
| Server → Client | `values` | `Record<string, number>` | Consensus broadcast (50ms interval) |
| Server → Client | `input:rejected` | `{ reason: string }` | Rate limit or validation failure |
| Server → Client | `error` | `{ code: string, message: string }` | Session not active, etc. |

### WebSocket Events — Performer (`/performer`)

| Direction | Event | Payload | Description |
|-----------|-------|---------|-------------|
| Client → Server | `auth` | `{ secret: string }` | Authentication handshake |
| Server → Client | `auth:success` | `{ performerId }` | Grants override privileges |
| Server → Client | `auth:failed` | `{ reason }` | Invalid credentials |
| Client → Server | `override` | `{ parameter, value, mode, blendFactor?, durationMs? }` | Apply override |
| Server → Client | `override:success` | `{ override }` | Override accepted |
| Client → Server | `override:clear` | `{ parameter }` | Remove override |
| Client → Server | `session:start` | — | Begin performance session |
| Client → Server | `session:pause` | — | Pause (requires `canPause` permission) |
| Client → Server | `session:resume` | — | Resume paused session |
| Client → Server | `session:end` | — | End (requires `canEnd` permission) |
| Server → Client | `values` | `Record<string, number>` | Consensus broadcast |
| Server → Client | `snapshot` | `{ timestamp, participants, values }` | Real-time analytics |

### Parameter Bus Events (Internal)

The `ParameterBus` class (`src/bus/parameter-bus.ts`) is a typed `EventEmitter` with 16 event types:

```typescript
enum BusEvent {
  AUDIENCE_INPUT       = 'audience:input',
  AUDIENCE_INPUT_BATCH = 'audience:input:batch',
  CONSENSUS_UPDATE     = 'consensus:update',
  CONSENSUS_SNAPSHOT   = 'consensus:snapshot',
  PERFORMER_OVERRIDE   = 'performer:override',
  PERFORMER_OVERRIDE_CLEAR = 'performer:override:clear',
  PERFORMER_COMMAND    = 'performer:command',
  SESSION_START        = 'session:start',
  SESSION_PAUSE        = 'session:pause',
  SESSION_RESUME       = 'session:resume',
  SESSION_END          = 'session:end',
  PARTICIPANT_JOIN     = 'participant:join',
  PARTICIPANT_LEAVE    = 'participant:leave',
  PARTICIPANT_UPDATE   = 'participant:update',
  ERROR                = 'error',
  WARNING              = 'warning',
  STATS                = 'stats',
}
```

All payloads are strongly typed via `BusEventPayloads` interface map. The bus collects throughput statistics (inputs/sec, consensus updates/sec, active subscribers, latency) and emits them every second on the `STATS` event.

---

## Configuration Deep Dive

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `3000` | Core engine HTTP/WebSocket port |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection for session state |
| `OSC_OUT_PORT` | `57121` | UDP port for OSC output to SuperCollider |
| `CONSENSUS_WINDOW_MS` | `1000` | Input aggregation window |
| `GCP_PROJECT_ID` | `omni-dromenon` | Google Cloud project (for Firestore) |
| `GEMINI_API_KEY` | — | For AI-driven orchestration features |
| `CHROMA_URL` | `http://chroma:8000` | ChromaDB vector store endpoint |
| `LOG_LEVEL` | `debug` | Logging verbosity |

### Consensus Weighting Configuration

The `WeightingConfig` interface controls all aspects of the consensus algorithm:

```typescript
interface WeightingConfig {
  spatialAlpha: number;      // Weight of spatial proximity (0-1)
  spatialDecayRate: number;  // Exponential decay rate for distance
  temporalBeta: number;      // Weight of input recency (0-1)
  temporalWindowMs: number;  // Time window for input relevance (ms)
  temporalDecayRate: number; // Exponential decay rate for time
  consensusGamma: number;    // Weight of cluster agreement (0-1)
  clusterThreshold: number;  // Max value difference for cluster membership
  smoothingFactor: number;   // Exponential smoothing (0 = no change, 1 = instant)
  outlierThreshold: number;  // Z-score threshold for outlier rejection
}
```

**Defaults:** `spatialAlpha: 0.3`, `temporalBeta: 0.5`, `consensusGamma: 0.2`, `temporalWindowMs: 5000`, `smoothingFactor: 0.3`, `outlierThreshold: 2.5`.

### Venue Geometry

Performance spaces are modeled as 2D coordinate systems with named zones:

```typescript
const DEFAULT_VENUE: VenueGeometry = {
  width: 100, height: 100,
  stagePosition: { x: 50, y: 0 },
  zones: [
    { id: 'front',  bounds: { xMin: 0, xMax: 100, yMin: 0,  yMax: 30 },  spatialWeight: 1.0 },
    { id: 'middle', bounds: { xMin: 0, xMax: 100, yMin: 30, yMax: 70 },  spatialWeight: 0.8 },
    { id: 'back',   bounds: { xMin: 0, xMax: 100, yMin: 70, yMax: 100 }, spatialWeight: 0.6 },
  ],
  maxCapacity: 500,
};
```

Zone-based spatial weights are base multipliers applied before the distance-decay calculation. A front-section audience member receives the full spatial weight; a back-section member starts at 0.6x before distance decay further reduces it.

### Session Configuration

```typescript
const DEFAULT_SESSION_CONFIG: SessionConfig = {
  allowAudienceInput: true,
  allowPerformerOverride: true,
  recordingEnabled: true,
  maxParticipants: 1000,
  inputRateLimitMs: 100,    // Max 10 inputs/second per client
  consensusIntervalMs: 50,  // 20 consensus computations/second
  oscEnabled: true,
  oscHost: '127.0.0.1',
  oscPort: 57120,
};
```

### Default Performance Parameters

Four parameters ship out of the box; additional parameters can be added via the `ParameterDefinition` interface:

| Parameter | Category | Default | OSC Address | Description |
|-----------|----------|---------|-------------|-------------|
| `mood` | MOOD | 0.5 | `/performance/mood` | Emotional color (dark to bright) |
| `tempo` | TEMPO | 0.5 | `/performance/tempo` | Speed/pace of performance |
| `intensity` | INTENSITY | 0.3 | `/performance/intensity` | Energy level (calm to intense) |
| `density` | DENSITY | 0.4 | `/performance/density` | Textural complexity (sparse to dense) |

Each parameter supports optional MIDI CC mapping (`midiCC` field) and can be individually configured for audience control, performer control, and smoothing behavior.

---

## Theory Implemented

Omni-Dromenon does not exist in a vacuum. It implements specific theoretical frameworks developed in ORGAN-I (Theory) and the broader organvm system.

### From `recursive-engine` (ORGAN-I)

The consensus algorithm's self-reinforcing cluster weighting implements a recursive feedback loop: audience agreement amplifies agreement, producing emergent macro-behavior from micro-inputs. This is a direct application of the recursive systems theory formalized in [`organvm-i-theoria/recursive-engine`](https://github.com/organvm-i-theoria/recursive-engine--generative-entity) — specifically the principle that system identity emerges from iterated self-reference under constraint. In Omni-Dromenon, the constraint is the performer's override authority; the self-reference is the consensus algorithm's sensitivity to its own prior state (via smoothing); and the emergent identity is the performance itself, which is authored by neither audience nor performer alone but by their iterated negotiation.

### From `organon-noumenon--ontogenetic-morphe` (ORGAN-I)

The spatial weighting model — where proximity to the stage creates qualitatively different influence — operationalizes the distinction between phenomenal and noumenal experience explored in [`organvm-i-theoria/organon-noumenon--ontogenetic-morphe`](https://github.com/organvm-i-theoria/organon-noumenon--ontogenetic-morphe). The audience member in the front row has a phenomenally richer experience (visual detail, acoustic proximity, shared breath) than the one in the back. The weighting system translates this phenomenal difference into computational influence, asserting that richer experience should carry more authority in shaping the art. This is a philosophical claim embedded in code.

### From the Manifestos

Two theoretical documents within this repository articulate the conceptual foundations:

- **[The Stage That Breathes](docs/theory/manifestos/stage-that-breathes.md)** — argues that a performance space becomes alive when it responds to its inhabitants, and that Omni-Dromenon's parameter bus is the circulatory system of that living stage.
- **[Reciprocal Creation](docs/theory/manifestos/reciprocal-creation.md)** — defines the aesthetic theory of constrained negotiation: art is most interesting when authorship is shared but not equal, when power is explicit but not absolute.

### Flow Patterns

The `docs/flow-patterns/` directory contains YAML specifications for harmonic progressions, gate definitions, flow notation, and organ-flow manifests that formalize the relationship between consensus parameters and artistic output trajectories. These are not ornamental — they define the vocabulary of possible performance arcs and are consumed by the orchestration system during pre-performance configuration.

---

## Portfolio & Exhibition

This system is designed for live deployment. Target contexts include:

### Grant-Eligible Exhibitions

- **Ars Electronica** (Linz) — a draft narrative for submission is in [`docs/business/GRANT_MATERIALS/ars-electronica-narrative-DRAFT.md`](docs/business/GRANT_MATERIALS/ars-electronica-narrative-DRAFT.md)
- **NIME** (New Interfaces for Musical Expression) — the spatial weighting model is a novel contribution to HCI/music technology
- **Transmediale** (Berlin) — the philosophical framework (constrained negotiation, democratic instrument) aligns with their media art focus

### Venue Types

The system's infrastructure accommodates:

- **Concert halls** (500-2000 seats): Standard front/middle/back zone model, OSC output to house sound system
- **Black box theatres** (50-200 seats): High spatial resolution, intimate proximity weighting
- **Galleries/installations** (walk-through): `installation` genre preset with 0.7 spatial alpha — position in the space is almost everything
- **Outdoor/festival** (1000+ participants): Relaxed latency requirements, emphasis on consensus clustering
- **iPhone deployment**: A dedicated quick-start guide ([`docs/guides/IPHONE_QUICK_START.md`](docs/guides/IPHONE_QUICK_START.md)) covers PWA-style audience participation via mobile Safari

### Documentation for Proposals

The `docs/community/` directory provides production-ready templates:

- [`festival-rider.md`](docs/community/deployment-playbooks/festival-rider.md) — technical requirements for venue production managers
- [`indie-venue-setup.md`](docs/community/deployment-playbooks/indie-venue-setup.md) — stripped-down deployment for small spaces
- [`budget-checklist.md`](docs/community/grant-resources/budget-checklist.md) — line-item template for grant budgets
- [`proposal-template.md`](docs/community/grant-resources/proposal-template.md) — narrative scaffold for funding applications
- [`collaboration-agreement.md`](docs/community/templates/collaboration-agreement.md) — legal template for artist collaborations
- [`artist-bio-template.md`](docs/community/artist-prospecting/artist-bio-template.md) and [`cv-template.md`](docs/community/artist-prospecting/cv-template.md) — formatted materials for submission packets

---

## Cross-References

Omni-Dromenon is the **ORGAN-II flagship** within the organvm eight-organ creative-institutional system. It connects to:

### ORGAN-I (Theory)

- **[recursive-engine](https://github.com/organvm-i-theoria/recursive-engine--generative-entity)** — Formal recursive systems theory. Omni-Dromenon's consensus feedback loop is an applied instance.
- **[organon-noumenon--ontogenetic-morphe](https://github.com/organvm-i-theoria/organon-noumenon--ontogenetic-morphe)** — Epistemological framework. The spatial weighting model operationalizes phenomenal proximity.

### ORGAN-III (Commerce)

- **[public-record-data-scrapper](https://github.com/organvm-iii-ergon/public-record-data-scrapper)** — Demonstrates the same data-pipeline architecture (ingestion, transformation, output) applied to public records rather than audience inputs.

### ORGAN-IV (Orchestration)

- **[agentic-titan](https://github.com/organvm-iv-taxis/agentic-titan)** — System-wide orchestration agent. Omni-Dromenon's `orchestrate` CLI is a domain-specific analogue; agentic-titan operates at the cross-organ level.

### ORGAN-V (Public Process)

- **[public-process](https://github.com/organvm-v-logos/public-process)** — The public-process methodology documentation includes Omni-Dromenon's development as a case study of building complex creative-technical systems in public.

### System Context

- **[meta-organvm](https://github.com/meta-organvm)** — The umbrella organization coordinating all eight organs. Omni-Dromenon is the ORGAN-II flagship, one of ~79 repositories across 8 GitHub organizations in the organvm creative-institutional system.

---

## Contributing

Contributions span four domains. The project follows a phase-based development model — check [`docs/plans/`](docs/plans/) for current priorities.

### Code Contributions

```bash
# Fork and clone
git clone https://github.com/<your-fork>/metasystem-master.git
cd metasystem-master
pnpm install

# Create a feature branch
git checkout -b feature/your-feature-name

# Make changes, run tests
pnpm test
pnpm build

# Type-check all packages
pnpm run typecheck

# Commit (conventional commits)
git commit -m "feat(consensus): add adaptive smoothing factor"

# Push and open a PR against master
git push origin feature/your-feature-name
```

Commit types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`. Scope should reference the affected package (e.g., `consensus`, `performance-sdk`, `audio-bridge`, `orchestrate`).

### Artistic Contributions

Open an issue using the [Artistic Collaboration template](.github/ISSUE_TEMPLATE/artistic_collaboration.md). Describe the genre, medium, and how Omni-Dromenon would be integrated. The project actively seeks collaborations with:

- Electronic musicians interested in audience-driven synthesis
- Choreographers exploring collective audience influence on movement
- Theatre directors working with branching narratives
- Installation artists designing spatially-aware interactive environments
- Visual artists creating consensus-driven generative imagery
- Opera companies interested in collective narrative steering

### Research Contributions

Open an issue using the [Research Contribution template](.github/ISSUE_TEMPLATE/research_contribution.md). Areas of active interest:

- Consensus algorithm variants (Byzantine fault tolerance for adversarial audiences, adaptive weighting that learns from performer override patterns)
- Latency optimization below the current P95 < 2ms target
- Spatial weighting models for non-rectangular venues (amphitheatres, in-the-round, site-specific outdoor)
- Longitudinal studies of audience behavior across multiple performances
- Machine learning approaches to genre preset optimization based on performer satisfaction scores

### Documentation

The `docs/` directory contains 200+ files across academic templates, deployment guides, architectural specifications, theory manifestos, and community resources. Documentation contributions — particularly performer guides, genre-specific customization guides, and venue setup playbooks — are especially welcome. The documentation uses MkDocs (`docs/mkdocs.yml`) for structured site generation.

---

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| WebSocket latency (P95) | < 2ms | Core engine benchmarks |
| Consensus computation | < 1ms for 100 concurrent users | `packages/core-engine/benchmarks/` |
| Memory per service | < 500MB at 1,000 connections | Docker stats |
| Audience capacity | 1,000+ simultaneous clients | Load testing |
| Input rate limit | 10 inputs/second per client | Server-side enforcement |
| Consensus broadcast | 20 updates/second (50ms interval) | Configurable |

---

## Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Runtime | Node.js | >= 18.0.0 |
| Package Manager | pnpm | 9.15.0 |
| Language | TypeScript | 5.3 (strict mode, ES2022 target) |
| Server | Express | 4.18 |
| WebSocket | Socket.io | 4.7 |
| Validation | Zod | 3.22 |
| UI Framework | React | 18.2 |
| Build Tool | Vite | 5.0 |
| Testing | Vitest | 1.1 |
| Audio Protocol | OSC (via `osc` npm) | 2.4 |
| Session State | Redis | 7 (Alpine) |
| Vector Store | ChromaDB | Latest |
| Blockchain | Solana Web3.js | 1.91 |
| Infrastructure | Docker Compose | — |
| Cloud | GCP (Terraform, Cloud Run) | — |
| Python (Orchestrator) | Python | 3.11+ |

---

## License & Author

**License:** [MIT](LICENSE)

**Author:** Anthony Padavano ([@4444J99](https://github.com/4444J99))

**Organization:** [organvm-ii-poiesis](https://github.com/organvm-ii-poiesis) (ORGAN-II: Poiesis)

**System:** [meta-organvm](https://github.com/meta-organvm) — the eight-organ creative-institutional system coordinating ~79 repositories across theory, art, commerce, orchestration, public process, community, and marketing.

---

<sub>This README is a Silver Sprint portfolio document for the organvm system. It is written for grant reviewers, hiring managers, and collaborators who want to understand what Omni-Dromenon does, why it exists, and how it fits within a larger creative-institutional architecture. For developer-focused quick reference, see [`docs/guides/QUICK_REFERENCE.md`](docs/guides/QUICK_REFERENCE.md). For the full documentation site, see [`docs/mkdocs.yml`](docs/mkdocs.yml).</sub>
