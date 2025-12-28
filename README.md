# 4jp Metasystem

**Autonomous Development Ecosystem**

This workspace is managed by the **Omni-Dromenon Machina** (Universal Orchestrator), which coordinates development across multiple distinct projects.

## 🧠 The Orchestrator
- **[omni-dromenon-machina](./omni-dromenon-machina)**: The central nervous system. It runs autonomous agents, manages CI/CD, and enforces architectural constraints across the workspace.

## 🌍 Managed Workspaces

### Active Projects
- **[life-my--midst--in](./life-my--midst--in)**: Interactive CV/Résumé system with identity masking.
  - *Status:* Active Development (Codex Agents)
  - *Tech:* Next.js, Neo4j, TypeScript
  - *Docs:* [Architecture](./life-my--midst--in/ARCH-001-system-architecture.md), [Seed](./life-my--midst--in/seed.yaml)

- **[gamified-coach-interface](./gamified-coach-interface)**: 3D Holographic fitness strategy platform.
  - *Status:* Live Prototype
  - *Tech:* React, Three.js, Python
  - *Docs:* [Architecture](./gamified-coach-interface/ARCHITECTURE.md), [Seed](./gamified-coach-interface/seed.yaml)

- **[trade-perpetual-future](./trade-perpetual-future)**: Non-custodial Solana trading terminal.
  - *Status:* Production Ready
  - *Tech:* React, Solana Web3.js, Drift Protocol
  - *Docs:* [Readme](./trade-perpetual-future/README.md), [Seed](./trade-perpetual-future/seed.yaml)

### Tools & Utilities
- **[my--father-mother](./my--father-mother)**: Local memory augmentation and clipboard manager.
- **[mail_automation](./mail_automation)**: Gmail processing agents.
- **[mcp-servers](./mcp-servers)**: Local Model Context Protocol infrastructure.

## 🔗 Architecture
The system is defined by `4jp-metasystem.yaml`, which maps the relationships between the Orchestrator and its managed satellites.

```mermaid
graph TD
    A[Omni-Dromenon Machina] -->|Orchestrates| B[life-my--midst--in]
    A -->|Monitors| C[gamified-coach-interface]
    A -->|Indexes| D[my--father-mother]
    A -->|Deploys| E[trade-perpetual-future]
    
    subgraph Shared Infrastructure
    F[@4jp/design-system]
    G[Identity Wallet (Solana)]
    end
    
    B --> F
    C --> F
    E --> G
    A --> G
```

## 🚀 Operations
To invoke the orchestrator:
```bash
cd omni-dromenon-machina
# Run autonomous development cycle
npm run orchestrate
```

## 📚 Grand Index
- **Orchestrator Docs:** `omni-dromenon-machina/docs/`
- **Identity Theory:** `life-my--midst--in/packages/schema/README.md`
- **Trading Specs:** `trade-perpetual-future/docs/guides/FEATURES.md`