# Feature Implementation Plan: Phase E - Expansion & Entropy

## 📋 Todo Checklist
- [ ] **Identity OS (`life-my--midst--in`)**: Implement the "Mask Editor" UI.
- [ ] **Strategy Core (`gamified-coach`)**: Connect the 3D hologram to real Identity data.
- [ ] **Orchestrator (`omni-dromenon`)**: Implement "Dream Scenarios" for targeted autonomous improvement.
- [ ] **Infrastructure**: Terraform/IaC for satellite project deployment.
- [ ] **Docs**: Create a "Grand Index" in the root workspace.

## 🔍 Analysis & Investigation

### Current State
- **Orchestrator**: Active, Triple-Agent (Architect/Builder/Critic), monitoring 7 projects.
- **Identity OS**: `life-my--midst--in` has a `schema` package but the `web` app is a skeleton (`next dev` works but UI is empty).
- **Strategy Core**: `gamified-coach-interface` has a `StrategyCore.js` (Three.js) but it's isolated and uses mock states ('idle', 'glitching').
- **Metasystem**: `4jp-metasystem.yaml` is the source of truth.

### The Gap
The "Nervous System" (Omni) is built, but the "Body" (Identity) and "Mind" (Strategy) are still embryonic. They need content and connection.

## 📝 Implementation Plan

### 1. Identity OS: The Mask Editor
**Objective:** Create a UI to edit the `seed.yaml` genome visually.
- **Location:** `life-my--midst--in/apps/web`.
- **Tech:** React Hook Form + Zod (from `packages/schema`).
- **Feature:** A "Mask Switcher" that changes the user's active persona (e.g., "Developer" -> "Artist").

### 2. Strategy Core: Neural Link
**Objective:** Feed real data into the `StrategyCore` hologram.
- **Location:** `gamified-coach-interface/src/main.js` & `StrategyCore.js`.
- **Action:** 
    1. Connect to `omni-dromenon-core` via WebSocket (`socket.io-client`).
    2. Listen for `metasystem:health` events.
    3. Map Health -> Visual State:
        - All Green -> "Success" state (Green glow).
        - Drift Detected -> "Glitching" state (Orange vertices).
        - Error -> "Critical" state (Red pulse).

### 3. Orchestrator: Dream Scenarios
**Objective:** Give the `NightWatchman` specific missions beyond just "fix drift".
- **Location:** `omni-dromenon-machina/core-engine/src/dreamcatcher/scenarios`.
- **Scenarios:**
    - `UI_POLISH`: "Scan all CSS files and normalize colors to the design system."
    - `SECURE_CORE`: "Scan all dependencies and upgrade if vulnerable."
    - `CHAOS_MONKEY`: "Randomly introduce a minor drift to test recovery."

### 4. Infrastructure: Satellite Launch
**Objective:** Deploy the satellites to the cloud so they are accessible public URLs.
- **Location:** `omni-dromenon-deploy/gcp`.
- **Action:** Create `cloud-run-service.yaml` for `gamified-coach` and `identity-os`.

## 🎯 Success Criteria
- **Visual Synergy:** The `gamified-coach` hologram turns RED when I break a test in `life-my--midst--in`.
- **Identity Control:** I can edit my "Mask" in `life-my--midst--in` and see the changes reflected in the Metasystem.
- **Autonomous Evolution:** The Orchestrator wakes up at night and optimizes the CSS of the Identity OS without human intervention.
