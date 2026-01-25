# 🧠 Omni-Dromenon Machina: Metasystem Context
**Last Sync:** Dec 28, 2025
**Status:** SOVEREIGN / ACTIVE
**Current Phase:** Phase 6 (Evolution)

## 📍 System State
The Metasystem has transitioned from construction to operation.
*   **Infrastructure:** Flat hierarchy at `~/Workspace/omni-dromenon-machina`.
*   **Intelligence:** 
    *   **The Architect:** Active. Query via `python3 scripts/ask_origin.py "Question"`.
    *   **The Critic:** Active. Wired to `core-engine` event bus.
    *   **The Index:** `data/universe_index.json` tracks 83 repositories.
*   **Connectivity:**
    *   **Neural Link:** Redis Pub/Sub + Webhooks active on `localhost:3000`.
    *   **Guild:** Repositories deployed to `github.com/4444JPP` (Pending transfer to `labores-profani-crux`).

## 🛠️ Key Tools & Scripts
| Script | Purpose |
| :--- | :--- |
| `scripts/daily_ritual.py` | **Start Here.** Syncs, Inoculates, and Indexes the Universe. |
| `scripts/ask_origin.py` | RAG-based query tool for project history (Gemini 2.5). |
| `scripts/test_neural_link.py` | Verifies the Event Bus and Webhook ingestion. |
| `scripts/init_guild_remotes.sh` | Deploys commercial assets to GitHub. |

## 🗺️ The Map (Organization)
1.  **Metasystem Master:** `omni-dromenon-machina` (The Brain).
2.  **Origin:** `4444JPP` (The Archive - 46/52 Restored).
3.  **Alchemist:** `ivviiviivvi` (The Lab).
4.  **Guild:** `labores-profani-crux` (The Shop).

## ⏭️ Active Quests
1.  **Transfer Guild:** Move `trade-perpetual`, `gamified-coach`, `enterprise-plugin` to the `labores-profani-crux` Org.
2.  **Dreamcatcher:** Connect `core-engine` to Generative AI for the visual performance.
3.  **Routine:** Ensure `daily_ritual.py` runs every morning.

## 🔐 Secrets & Keys
*   `GEMINI_API_KEY`: Required for `ask_origin.py`.
*   `GITHUB_TOKEN`: Required for restoration and Git ops.
*   Managed via 1Password / Environment Variables.