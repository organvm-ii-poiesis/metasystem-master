# 🏗️ PLAN-003: Activating the Critic & The Architect

**Spec:** `specs/REQ-003-activation.md`
**Context:** `core-engine`
**Goal:** Deploy autonomous review and indexing agents.

## 1. Architecture

### A. The Critic Agent (`src/orchestrator/critic.ts`)
A service that subscribes to the `systemBus` and reacts to `repo.pull_request` events.
*   **Prompt:** Uses a "Critic Persona" to evaluate code against `seed.yaml` constraints.
*   **Action:** Uses `gh api` or Octokit to post review comments.

### B. The Architect (Indexing Script)
A standalone tool `scripts/index_universe.py` that chunks the 115 repos and prepares them for RAG.
*   **Store:** For the prototype, we will use a JSON-based "Search Index" or a local ChromaDB instance if available.

## 2. Execution Steps

### Step 1: Implement the Critic
1.  [ ] **Create Agent:** `core-engine/src/orchestrator/critic.ts`.
2.  [ ] **Wire to Bus:** In `server.ts`, initialize the `CriticAgent` and subscribe it to `systemBus`.
3.  [ ] **Mock Review:** Test using `scripts/test_neural_link.py` by sending a `pull_request` event.

### Step 2: Implement the Architect (Indexer)
1.  [ ] **Create Indexer:** `scripts/index_universe.py`.
2.  [ ] **Scan Workspace:** Iterate through `~/Workspace/{Org}/{Repo}`.
3.  [ ] **Chunking:** Extract `README.md` and key source files.
4.  [ ] **Store:** Create `data/universe_index.json`.

## 3. Dependencies
*   `GITHUB_TOKEN` (Scoped for all 3 Orgs).
*   `GEMINI_API_KEY`.
