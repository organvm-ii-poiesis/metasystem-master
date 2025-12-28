# Repository Entry Points (Per-Repo Keys)

**For each AI service: Where to start in each repository**

---

## ENTRY POINTS BY REPOSITORY

### core-engine
**Phase A Owner:** Jules (consensus algorithm)
**Entry:** `src/consensus/weighted-consensus.ts` (CREATE NEW FILE)
**Structure:**
```
core-engine/
├── src/
│   ├── server.ts (existing - validated POC)
│   ├── consensus/
│   │   └── weighted-consensus.ts ← CREATE HERE
│   └── types/
├── tests/
│   └── consensus.test.ts ← CREATE HERE
├── benchmarks/
│   └── consensus-bench.ts ← CREATE HERE
├── package.json (has npm scripts)
└── README.md
```

### performance-sdk
**Phase B/C Owner:** Jules
**Entry:** `src/components/` 
**Status:** Scaffolding (will be React components)

### audio-synthesis-bridge
**Phase B/C Owner:** Jules
**Entry:** `src/index.ts`
**Status:** Scaffolding (OSC gateway)

### .github (Special Org Repo)
**Phase A Owner:** Copilot
**Entry:** `workflows/`
**Create:**
```
.github/
├── workflows/
│   ├── test.yml ← CREATE HERE
│   ├── deploy-docs.yml ← CREATE HERE
│   └── release.yml ← CREATE HERE
├── profile/README.md (org intro)
├── ISSUE_TEMPLATE/ (templates)
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
└── [other org files]
```

### docs
**Phase A Owner:** Gemini (review + synthesis)
**Entry:** `theory/manifesto.md`, `specs/`
**Status:** Scaffolding

### academic-publication
**Phase D Owner:** Human
**Entry:** `papers/`, `submissions/`
**Status:** Planning

### artist-toolkit-and-templates
**Phase D Owner:** ChatGPT
**Entry:** Grant templates, prospecting letters
**Status:** Templates provided

### example-generative-music
**Current Owner:** Keep as validated POC
**Entry:** `src/server.ts` (VALIDATED - P95=2ms)
**Do NOT modify during Phase A**

### example-generative-visual
**Phase C Owner:** Jules
**Entry:** `src/` 
**Status:** Scaffolding

### example-choreographic-interface
**Phase C Owner:** Jules
**Entry:** `src/`
**Status:** Scaffolding

### example-theatre-dialogue
**Phase C Owner:** ChatGPT
**Entry:** `src/`
**Status:** Scaffolding

### client-sdk
**Phase B/C Owner:** Jules
**Entry:** `src/index.ts`
**Status:** Scaffolding (WebSocket client)

---

## PHASE A FOCUS (Dec 7-8)

Only 3 repos have Phase A work:
1. **core-engine/** → Jules (consensus algorithm)
2. **.github/** → Copilot (workflows)
3. **docs/** → Gemini (review manifesto)

All other repos are untouched during Phase A.

---

## SAFE TO MODIFY (Phase A)

✅ `core-engine/src/consensus/` (new files)
✅ `.github/workflows/` (new files)
✅ Any documentation files

❌ `example-generative-music/src/server.ts` (validated POC - LEAVE ALONE)

---

## Path References for AI Services

**Base path (for all relative paths):**
`/Users/4jp/Desktop/omni-dromenon-machina/`

**Jules work goes to:**
- `/Users/4jp/Desktop/omni-dromenon-machina/core-engine/src/consensus/weighted-consensus.ts`
- `/Users/4jp/Desktop/omni-dromenon-machina/core-engine/tests/consensus.test.ts`
- `/Users/4jp/Desktop/omni-dromenon-machina/core-engine/benchmarks/consensus-bench.ts`

**Gemini work goes to:**
- `/Users/4jp/Desktop/omni-dromenon-machina/GRANT_MATERIALS/ars-electronica-narrative-DRAFT.md`

**Copilot work goes to:**
- `/Users/4jp/Desktop/omni-dromenon-machina/.github/workflows/test.yml`
- `/Users/4jp/Desktop/omni-dromenon-machina/.github/workflows/deploy-docs.yml`
- `/Users/4jp/Desktop/omni-dromenon-machina/.github/workflows/release.yml`

---

All paths use actual directories. All files are to be created fresh during Phase A execution.
