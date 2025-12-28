# AI SERVICE BRIEFING TEMPLATES: COPY/PASTE READY

Use these templates to brief Copilot, Gemini, Jules, ChatGPT. Paste one per service.

---

## TEMPLATE A: For JULES (Backend Developer)

```
PROJECT: Omni-Dromenon-Engine
ROLE: Backend Implementation Phase A
PHASE: Dec 7-8 (Autonomous execution)

YOUR TASK: Implement consensus voting algorithm

DELIVERABLE: ~/Desktop/omni-dromenon-machina/core-engine/src/consensus/weighted-consensus.ts
             ~/Desktop/omni-dromenon-machina/core-engine/tests/consensus.test.ts

ALGORITHM SPEC:
- Input: Array of votes {voterId, parameter, value (0-100), weight (0.5-1.5), timestamp, location?}
- Output: {parameter, aggregated_value (0-100), confidence (0-1)}
- Temporal decay: recent votes (0-5s) weight=1.0, 5-10s weight=0.8, >10s discard
- Proximity bonus: votes within 100m get +0.2 weight
- Outlier removal: exclude votes >2 std dev from mean
- Weighted mean: final aggregation
- Confidence: 1 - (std_dev / max_value)

REQUIREMENTS:
- TypeScript, strict mode
- Unit tests: 100% coverage
- Benchmark: <1ms for 1000 votes
- No external dependencies

SUCCESS:
✓ npm run build (no errors)
✓ npm test (100% coverage)
✓ <1ms benchmark for 1000 votes

DEADLINE: Dec 8, 2025 EOD

Read: ~/Desktop/omni-dromenon-machina/core-engine/README.md first
Reference: AI_ORCHESTRATION_TIMELINE.md for full spec
```

---

## TEMPLATE B: For GEMINI (Research & Narrative)

```
PROJECT: Omni-Dromenon-Engine
ROLE: Grant Narrative Phase A
PHASE: Dec 7-8 (Autonomous execution)

YOUR TASK: Write 2-page grant narrative for Ars Electronica/Mozarteum XR Residency

DELIVERABLE: ~/Desktop/omni-dromenon-machina/GRANT_MATERIALS/ars-electronica-narrative-DRAFT.md
WORD COUNT: ~1200 words (±10%)

STRUCTURE:
1. Problem (200w): Audiences are passive spectators → need computational agency
2. Solution (350w): CAL, weighted consensus, performer override, genre-agnostic
3. Impact (300w): Artist vocabulary, audience co-creation, cultural shift
4. Timeline (200w): Months 1-7 roadmap (expand POC, deploy beta, iterate, polish)
5. Risks & Mitigations (150w): Network, adoption, latency, funding

TONE:
- Professional academic (for grant reviewers with art-tech expertise)
- Specific technical claims (cite P95 latency = 2ms validation)
- Honest about pre-beta status (increases credibility)
- Ground in theory (Rancière, Bourriaud, performance studies)

SUCCESS:
✓ 1200 words (±10%)
✓ Clear narrative arc
✓ Specific technical details + accuracy
✓ Realistic timeline
✓ No typos, professional tone
✓ Ready to submit without revision

DEADLINE: Dec 8, 2025 EOD

Read: ~/Desktop/omni-dromenon-machina/docs/theory/manifesto.md
Reference: AI_ORCHESTRATION_TIMELINE.md for full brief
```

---

## TEMPLATE C: For COPILOT (CI/CD & DevOps)

```
PROJECT: Omni-Dromenon-Engine
ROLE: CI/CD Automation Phase A
PHASE: Dec 7-8 (Autonomous execution)

YOUR TASK: Write 3 GitHub Actions workflows

DELIVERABLES:
~/Desktop/omni-dromenon-machina/.github/workflows/test.yml
~/Desktop/omni-dromenon-machina/.github/workflows/deploy-docs.yml
~/Desktop/omni-dromenon-machina/.github/workflows/release.yml

WORKFLOW 1 (test.yml):
- Trigger: Every push to main + every PR
- Steps: npm install → npm build → npm test
- Cache dependencies (<30s install)
- Report coverage + test results in PR
- Fail if tests don't pass

WORKFLOW 2 (deploy-docs.yml):
- Trigger: Push to main (only if /docs changed)
- Steps: Python 3.9+ → pip install mkdocs mkdocs-material → mkdocs build → deploy to gh-pages
- Auto-deploy to github.io

WORKFLOW 3 (release.yml):
- Trigger: git tag (e.g., git tag v0.1.0)
- Steps: Create GitHub Release + changelog
- Auto-publish to npm (if applicable)

STANDARDS:
✓ Use official GitHub Actions (actions/checkout, actions/setup-node)
✓ Cache dependencies
✓ Clear job names + descriptions
✓ Fail fast on errors
✓ Well-documented YAML

SUCCESS:
✓ All 3 workflows compile (valid YAML syntax)
✓ test.yml runs on every PR/push
✓ deploy-docs.yml builds + deploys docs
✓ release.yml triggers on git tag
✓ Ready to push to GitHub immediately

DEADLINE: Dec 8, 2025 EOD

Reference: AI_ORCHESTRATION_TIMELINE.md for full specifications
```

---

## TEMPLATE D: For CHATGPT (Content & Narrative) [PHASE C]

```
PROJECT: Omni-Dromenon-Engine
ROLE: Demo Video Script Phase C
PHASE: Dec 9-13 (After GitHub push)

YOUR TASK: Write 90-second demo video script

DELIVERABLE: ~/Desktop/omni-dromenon-machina/DEMO_VIDEO_SCRIPT.md

STRUCTURE (90 seconds):
[0-20s] PROBLEM: Show passive audience at concert. Message: "Most performances are one-way"
[20-50s] SOLUTION: Audience sliders + consensus → performance shifts. Explain in simple terms.
[50-80s] IMPACT: Show artists + audience interacting. Emphasize: performers maintain authority, audiences have agency.
[80-90s] CALL TO ACTION: "Fund this. Collaborate." Links to GitHub, contact.

FORMAT:
[TIMING] SCENE NAME
[VISUAL] What's on screen
[VOICEOVER] Exact words for narrator
[MUSIC] Sound cues
[NOTES] Special instructions

SUCCESS:
✓ 90 seconds (±5s)
✓ Clear 4-part narrative
✓ Voiceover is conversational (not robotic)
✓ Technical concepts explained simply
✓ Compelling call to action
✓ Camera/music directions are specific
✓ Ready to hand to videographer

DEADLINE: Dec 13, 2025 EOD

Reference: AI_ORCHESTRATION_TIMELINE.md for full brief
```

---

## SUMMARY: WHICH TEMPLATE FOR WHICH AI?

| AI | Template | Phase | Output |
|---|----------|-------|--------|
| Jules | A | A, B, C | Code (consensus, UIs, deployment) |
| Gemini | B | A | Grant narrative (€40k) |
| Copilot | C | A, B, C | CI/CD workflows + git automation |
| ChatGPT | D | C, D | Demo video script, grant content |

---

## HOW TO USE

1. Copy the template for your AI service
2. Paste into prompt (full text)
3. Send to AI service (Copilot, Gemini, Claude instance, etc.)
4. Wait for output (24-36 hours)
5. Check success criteria against checklist

---

**Location:** All templates stored in this file
**Usage:** Copy/paste one template per AI service
**Timing:** Brief Dec 6 evening (before you go offline)
