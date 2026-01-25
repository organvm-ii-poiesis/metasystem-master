# Omni-Performative Engine — Proof of Concept

Real-time audience-controlled performance system demonstrating reciprocal creation through distributed agency.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  AUDIENCE CLIENTS (React PWA)                               │
│  - No app install required                                   │
│  - 3 control parameters: intensity, density, pitch          │
│  - Real-time visualization of collective state              │
└───────────────────────────┬─────────────────────────────────┘
                            │ WebSocket (Socket.io)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  CONSENSUS SERVER (Node.js + TypeScript)                    │
│  - Connection management + heartbeat                        │
│  - Weighted consensus aggregation                           │
│  - OSC output to synthesis engine                           │
│  - Performer override channel                               │
└───────────────────────────┬─────────────────────────────────┘
                            │ OSC (UDP port 57120)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  SYNTHESIS ENGINE (SuperCollider)                           │
│  - Generative audio patch                                   │
│  - Parameter-to-sound mapping                               │
│  - Low-latency audio output                                 │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Node.js 18+ 
- SuperCollider 3.12+ (for audio synthesis)
- Docker + Docker Compose (optional, for containerized deployment)

### Option A: Local Development

**1. Start the server:**

```bash
cd server
npm install
npm run dev
```

Server runs on `http://localhost:3001`

**2. Start the client:**

```bash
cd client
npm install
npm start
```

Client runs on `http://localhost:3000`

**3. Start SuperCollider:**

Open SuperCollider IDE, then:

```supercollider
// Boot the server
s.boot;

// Load the OSC receiver
"supercollider/osc_receiver.scd".load;
```

**4. Test the system:**

- Open multiple browser tabs to `http://localhost:3000`
- Move the sliders
- Observe collective state visualization
- Listen to audio output respond to collective input

### Option B: Docker Compose

```bash
docker-compose up --build
```

Access client at `http://localhost:3000`

Note: SuperCollider requires local installation for audio output.

## Project Structure

```
omni-performative-engine/
├── server/                 # Node.js consensus server
│   ├── src/
│   │   ├── index.ts       # Entry point, Socket.io setup
│   │   ├── consensus.ts   # Aggregation algorithms
│   │   ├── osc.ts         # OSC output to SuperCollider
│   │   └── types.ts       # TypeScript interfaces
│   └── package.json
├── client/                 # React PWA audience interface
│   ├── src/
│   │   ├── App.tsx        # Main application
│   │   ├── components/    # UI components
│   │   └── hooks/         # Socket.io hook
│   └── package.json
├── supercollider/          # Audio synthesis
│   ├── osc_receiver.scd   # OSC listener + routing
│   └── synth_defs.scd     # Instrument definitions
├── docker-compose.yml
└── README.md
```

## Control Parameters

| Parameter | Range | Description |
|-----------|-------|-------------|
| `intensity` | 0.0 - 1.0 | Overall energy/volume of the output |
| `density` | 0.0 - 1.0 | Rhythmic/textural complexity |
| `pitch` | 0.0 - 1.0 | Harmonic center / frequency range |

## Consensus Modes

The server supports multiple aggregation strategies:

1. **Arithmetic Mean** (default): Simple average of all inputs
2. **Weighted Mean**: Inputs weighted by connection duration
3. **Median**: Robust to outliers
4. **Mode Clustering**: Groups similar inputs, selects dominant cluster

Configure via environment variable:

```bash
CONSENSUS_MODE=weighted npm run dev
```

## Performer Override

The performer interface (planned) will support:

- **Lock Parameter**: Freeze a parameter, ignoring audience input
- **Bias**: Add offset to collective input (-0.5 to +0.5)
- **Range Constraint**: Limit parameter to subset of full range
- **Emergency Reset**: Return all parameters to default

## Latency Targets

| Segment | Target | Measurement |
|---------|--------|-------------|
| Client → Server | < 50ms | WebSocket round-trip |
| Consensus computation | < 10ms | Per aggregation cycle |
| Server → SuperCollider | < 5ms | OSC UDP local |
| SuperCollider → Audio | < 20ms | Buffer size dependent |
| **Total** | **< 100ms** | End-to-end |

## Development Roadmap

### Week 1: Core Loop ✓
- [x] Project scaffolding
- [ ] Socket.io connection management
- [ ] Single parameter round-trip

### Week 2: Consensus Engine
- [ ] Multi-client handling
- [ ] Aggregation algorithms
- [ ] State broadcast

### Week 3: Synthesis Mapping
- [ ] SuperCollider integration
- [ ] Parameter → audio mapping
- [ ] Latency profiling

### Week 4: UX Polish
- [ ] Visual feedback
- [ ] Performer override panel
- [ ] Mobile optimization

### Week 5: Documentation + Demo
- [ ] Demo video recording
- [ ] Technical report
- [ ] Grant materials

## License

AGPL-3.0 — Copyleft ensures derivative works remain open.

## References

- [Socket.io Documentation](https://socket.io/docs/v4/)
- [SuperCollider OSC Communication](https://doc.sccode.org/Guides/OSC_communication.html)
- [node-osc Library](https://github.com/MylesBorins/node-osc)
