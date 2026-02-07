# Reference Implementations

This directory contains reference implementations and proof-of-concept code preserved for benchmarking and historical reference.

## Contents

### poc-v0.1.0/

Original proof-of-concept implementation of the omni-performative engine. This minimal implementation demonstrates the core real-time audience control loop with SuperCollider integration.

**Preserved from:** `omni-performative-engine/`
**Archive date:** 2026-01-24

#### Structure
- `server/` - Node.js WebSocket server with consensus algorithm
- `client/` - React PWA for audience interaction
- `supercollider/` - OSC receiver and synth definitions
- `docker-compose.yml` - Container orchestration
- `README.md` - Original documentation

#### Key Metrics (from POC)
- Client → Server: < 50ms
- Consensus computation: < 10ms
- Server → SuperCollider: < 5ms
- SuperCollider → Audio: < 20ms
- **Total latency: < 100ms**

## Usage

Reference implementations are read-only. Use for:
- Benchmarking against production implementation
- Understanding original architecture decisions
- Debugging regression issues
