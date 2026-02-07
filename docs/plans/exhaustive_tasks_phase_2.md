# Feature Implementation Plan: Exhaustive Tasks Phase 2

## 📋 Todo Checklist
- [ ] **Unified CI/CD**: Implement root-level dispatch workflows in `omni-dromenon-machina` to trigger downstream builds.
- [ ] **Shared Component Library**: Extract common UI components (e.g., "Neo-Brutalist" cards, buttons) into a new `@4jp/design-system` package within `life-my--midst--in`.
- [ ] **Centralized Auth**: prototype the "Identity Wallet" login flow using Solana adapter in `omni-dromenon-sdk`.
- [ ] **Cross-Repo Testing**: Implement `runIntegrationTest` in `OrchestratorTester` to spin up Docker containers for E2E testing.
- [ ] **Documentation**: Generate a "Grand Index" in the root workspace `README.md` linking to all project docs.
- [ ] Final Review and Testing

## 🔍 Analysis & Investigation

### Current State
- **Metasystem**: Fully integrated and deployed. Orchestrator sees all 7 projects.
- **CI/CD**: `life-my--midst--in` has a workflow, others rely on manual scripts.
- **UI**: Fragmented. `gamified-coach` and `omni-dromenon` share aesthetic but not code.
- **Auth**: Fragmented. `omni` uses secrets, `trade` uses wallets.

### Dependencies
- **Solana Wallet Adapter**: Needed for centralized auth.
- **Docker**: Needed for integration testing.
- **Turbo**: Used in `life-my--midst--in` for package management.

### Challenges
- **Auth Bridging**: Connecting a Solana wallet signature to a backend JWT for a non-web3 app (`omni-dromenon`) requires careful cryptographic verification.
- **Component Extraction**: Moving code from a standalone repo (`gamified-coach`) to a monorepo package (`@4jp/design-system`) involves refactoring imports and dependencies.

## 📝 Implementation Plan

### Prerequisites
- `omni-dromenon-machina` live.
- `life-my--midst--in` accessible.

### Step-by-Step Implementation

1. **Step 1: Shared Design System**
   - **Context**: Unify UI.
   - Files to modify: `../life-my--midst--in/packages/design-system`.
   - Action: Create a new package. Extract `Card`, `Button`, `NeonText` from `omni-dromenon-sdk` and `gamified-coach-interface`.

2. **Step 2: Unified CI Dispatch**
   - **Context**: Automate builds.
   - Files to modify: `omni-dromenon-machina/.github/workflows/dispatch.yml`.
   - Action: Create a workflow that listens for `repository_dispatch` or pushes and triggers builds in satellite repos via API.

3. **Step 3: Identity Wallet Prototype**
   - **Context**: Unified Login.
   - Files to modify: `omni-dromenon-machina/performance-sdk/src/auth/WalletLogin.tsx`.
   - Action: specific implementation of SIWS (Sign In With Solana).

4. **Step 4: Cross-Repo Integration Tests**
   - **Context**: Verify the "Symbiote".
   - Files to modify: `omni-dromenon-machina/core-engine/src/orchestrator/tester.ts`.
   - Action: Add `runIntegrationTest` which uses `dockerode` or shell commands to spin up the stack and curl endpoints.

### Testing Strategy
- **Design System**: Storybook (if added) or import into `web` app.
- **Auth**: successful login with Phantom wallet -> JWT issuance.
- **Integration**: `tester.ts` reports success after spinning up containers.

## 🎯 Success Criteria
- **Shared UI**: `omni-dromenon` consumes components from `@4jp/design-system`.
- **Unified Auth**: One wallet login accesses Dashboard.
- **Automated E2E**: Orchestrator can prove the whole system works together.
