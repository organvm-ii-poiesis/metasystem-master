# Omni-Dromenon-Engine

**Real-time audience-participatory performance system**

> *Dromenon* (δρώμενον): "the thing done" — the primordial act from which all performance emerged, before drama separated from ritual.

---

## The Research Question

**Can audiences function as computational agents who collectively influence live performance parameters while performers maintain artistic authority?**

## Core Principles

1. **Performance as Mutable State** — No two performances are identical
2. **Audience as Computational Agent** — Spectators become distributed processing units
3. **Performer Authority Preservation** — Artists maintain override control
4. **Genre Fluidity** — One system adapts across music, dance, theatre, visual art
5. **Reciprocal Creation** — Mutual influence between all participants
6. **Transparency in Hierarchy** — Clear authority with visible decision-making

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CORE ENGINE                              │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐ │
│  │  WebSocket  │──│   Weighted   │──│   Parameter Bus    │ │
│  │   Server    │  │  Consensus   │  │   (pub/sub)        │ │
│  └─────────────┘  └──────────────┘  └─────────────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   Audience    │   │   Performer   │   │  Synthesis    │
│   Interface   │   │   Dashboard   │   │   Bridges     │
│  (mobile web) │   │  (override)   │   │  (OSC/MIDI)   │
└───────────────┘   └───────────────┘   └───────────────┘
```

## Repositories

| Repository | Description | Status |
|------------|-------------|--------|
| [core-engine](./core-engine) | Server, consensus, parameter bus | PoC Validated |
| [performance-sdk](./performance-sdk) | React UI components | Scaffolding |
| [audio-synthesis-bridge](./audio-synthesis-bridge) | OSC ↔ Web Audio | Scaffolding |
| [docs](./docs) | Theory, specs, guides | In Progress |
| [example-generative-music](./example-generative-music) | Audio synthesis demo | PoC Ready |
| [example-generative-visual](./example-generative-visual) | Graphics demo | Scaffolding |
| [example-choreographic-interface](./example-choreographic-interface) | Dance/motion demo | Scaffolding |
| [example-theatre-dialogue](./example-theatre-dialogue) | Dialogue demo | Scaffolding |
| [academic-publication](./academic-publication) | Papers, presentations | Template |
| [artist-toolkit-and-templates](./artist-toolkit-and-templates) | Grants, playbooks | In Progress |

## Quick Start

```bash
# Clone the core engine
git clone https://github.com/omni-dromenon-engine/core-engine
cd core-engine

# Install and run
npm install
npm run dev

# Open in browser
# Audience: http://localhost:3000
# Performer: http://localhost:3000/performer
```

## Technical Validation

**P95 Latency: 2ms** (target: <100ms)  
**Message Delivery: 100%**  
**Architecture: Genre-agnostic modular design**

## Contributing

See [CONTRIBUTING.md](./.github/CONTRIBUTING.md) for guidelines.

We welcome:
- 🎵 Composers and musicians
- 💃 Choreographers and dancers  
- 🎭 Theatre makers and directors
- 🎨 Visual artists and designers
- 💻 Developers and researchers

## Philosophical Foundation

This system instantiates the principle that **"everything is change"** — treating performance as mutable state, audiences as computational agents, and the theatrical event as a negotiated emergence rather than a fixed transmission.

See [docs/theory/philosophy](./docs/theory/philosophy) for the full theoretical framework.

## License

MIT © Anthony Padavano

## Contact

- Email: 4444@ivi374iviorf.org
- Organization: [ivviiviivvi](https://github.com/ivviiviivvi)
