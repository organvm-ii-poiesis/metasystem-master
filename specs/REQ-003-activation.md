# 📝 REQ-003: Activation (Autonomous Agents)

**Status:** DRAFT
**Owner:** Omni-Dromenon Machina (Architect)
**Target:** Phase 4 of Master Plan

## 1. Executive Summary
"Activation" is the process of delegating system oversight to autonomous agents. We are deploying two primary entities:
1.  **The Critic:** An automated PR reviewer and quality gatekeeper.
2.  **The Architect:** A memory-retrieval agent capable of grounded reasoning over the Origin (4444JPP) and Metasystem state.

## 2. Core Requirements

### 2.1. The Critic (CI/CD Bot)
*   **Location:** Integrated into `core-engine`.
*   **Trigger:** GitHub Webhook (`pull_request`).
*   **Action:**
    1.  Receive PR diff.
    2.  Check `seed.yaml` for project-specific constraints.
    3.  Analyze code for alignment with Metasystem standards (via LLM).
    4.  Post automated review comment on GitHub.

### 2.2. The Architect (Deep Memory)
*   **Location:** `cognitive-archaelogy-tribunal` (or equivalent service).
*   **Mechanism:** Retrieval Augmented Generation (RAG).
*   **Action:**
    1.  Scan and chunk all 115 repositories.
    2.  Generate vector embeddings.
    3.  Store in a local Vector Store (ChromaDB or similar).
    4.  Provide a CLI interface for the user to query historical code patterns.

## 3. Implementation Plan

### Step 1: LLM Integration
Configure `core-engine` to use Gemini/OpenAI/Anthropic APIs for reasoning.

### Step 2: PR Review Logic
Implement the `CriticAgent` in `src/orchestrator/critic.ts`.

### Step 3: Vector Indexing
Set up a RAG pipeline to index `~/Workspace`.

## 4. Acceptance Criteria
1.  [ ] A mock PR webhook triggers a code review response in the logs.
2.  [ ] A CLI command can retrieve the implementation of a specific feature from a 2023 Origin repo.
