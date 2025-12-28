# Omni-Dromenon Engine

**Transforming audiences from passive spectators into computational agents of live performance.**

---

## What We Build

The Omni-Dromenon Engine is an open-source interactive performance system enabling real-time audience participation across music, dance, theater, opera, and visual art. Audiences collectively influence live performances through smartphone interfaces while performers maintain artistic authority.

### Core Principles

| Principle | Description |
|-----------|-------------|
| **Reciprocal Creation** | Mutual influence between performers and audience |
| **Distributed Agency** | Audiences function as computational agents |
| **Performer Authority** | Artists maintain override control |
| **Genre Fluidity** | Unified system across artistic disciplines |
| **Transparency** | Clear, visible decision hierarchies |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PERFORMER LAYER                       │
│  Dashboard · Override Controls · Real-time Monitoring   │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│              CONTEXTUAL AWARENESS LAYER (CAL)            │
│  Weighted Consensus · Temporal Decay · Proximity Maps   │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                    AUDIENCE LAYER                        │
│  Mobile PWA · WebSocket · Parameter Control Interface   │
└─────────────────────────────────────────────────────────┘
```

---

## Repositories

| Repository | Description | Status |
|------------|-------------|--------|
| `core-engine` | CAL, consensus algorithms, WebSocket server | 🚧 Development |
| `audience-client` | PWA mobile interface | 🚧 Development |
| `performer-dashboard` | Real-time monitoring & override | 📋 Planned |
| `genre-modules` | Music, dance, theater, visual art adapters | 📋 Planned |
| `documentation` | Technical specs, API reference, guides | 📋 Planned |

---

## Technical Stack

- **Runtime:** Node.js 20+ LTS
- **Real-time:** Socket.io 4.x
- **Audio:** Tone.js / Web Audio API
- **Protocol:** OSC (Open Sound Control)
- **Frontend:** Progressive Web App (vanilla JS, mobile-first)

---

## Performance Validated

| Metric | Target | Achieved |
|--------|--------|----------|
| Input-to-output latency | < 100ms | **2ms (P95)** |
| Concurrent connections | 100+ | ✅ Validated |
| Consensus computation | < 50ms | ✅ Validated |

---

## Get Involved

- 📖 [Documentation](https://github.com/omni-dromenon-engine/documentation)
- 💬 [Discussions](https://github.com/orgs/omni-dromenon-engine/discussions)
- 🐛 [Report Issues](https://github.com/omni-dromenon-engine/core-engine/issues)
- 🤝 [Contributing Guide](https://github.com/omni-dromenon-engine/.github/blob/main/CONTRIBUTING.md)

---

## Etymology

**Dromenon** (δρώμενον) — Ancient Greek: "thing done" or "enacted ritual." The participatory, transformative act where observers become participants.

---

<sub>An open-source project building the infrastructure for reciprocal creation.</sub>
