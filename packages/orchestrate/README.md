# Omni-Orchestrate

**Multi-AI Orchestration CLI for the Omni-Performative Engine Project**

A command-line tool that coordinates research, validation, and synthesis across 5 AI services (Perplexity, Gemini, ChatGPT, Copilot, Grok) in a structured pipeline with gate validation.

---

## Overview

```
PHASE 1: RESEARCH VALIDATION (Perplexity)
  ├─ Precedent verification
  ├─ Funding landscape mapping
  └─ [GATE 1: Human review]

PHASE 2: SPECIFICATION HARDENING (Gemini)
  ├─ Edge-case matrix (5×5)
  ├─ Latency/constraint validation
  └─ [GATE 2: Human review]

PHASE 3: MESSAGING SYNTHESIS (ChatGPT)
  ├─ NSF grant narrative
  ├─ NEH grant narrative
  ├─ Ars Electronica narrative
  ├─ Artist statement
  └─ [GATE 3: Human review]

PHASE 4: IMPLEMENTATION PLANNING (Copilot)
  ├─ Code architecture review
  ├─ Budget allocation
  └─ [GATE 4: Human review]

PHASE 5: VULNERABILITY AUDIT (Grok)
  ├─ Assumption critique
  ├─ Failure scenario modeling
  └─ [GATE 5: Final synthesis]
```

---

## Installation

```bash
# Clone or copy this directory
cd omni-orchestrate

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt
```

---

## Configuration

### 1. Copy the config template

```bash
cp config.yaml.template config.yaml
```

### 2. Set API keys

Either edit `config.yaml` directly:

```yaml
api_keys:
  perplexity: "pplx-xxxxxxxxxxxx"
  gemini: "AIzaSyxxxxxxxxxx"
  chatgpt: "sk-xxxxxxxxxxxx"
  grok: "xai-xxxxxxxxxxxx"
```

Or use environment variables:

```bash
export PERPLEXITY_API_KEY="pplx-xxxxxxxxxxxx"
export GEMINI_API_KEY="AIzaSyxxxxxxxxxx"
export OPENAI_API_KEY="sk-xxxxxxxxxxxx"
export GROK_API_KEY="xai-xxxxxxxxxxxx"
```

### 3. Verify setup

```bash
python src/orchestrator.py status --services all
```

Expected output:
```
Service Status:
------------------------------
  ✓ perplexity
  ✓ gemini
  ✓ chatgpt
  ✓ copilot
  ✓ grok
```

---

## Usage

### Run Full Pipeline

```bash
# Run all phases with gate validation
python src/orchestrator.py run --phase all --gates --output-dir ./results

# Run with human review pauses at each gate
python src/orchestrator.py run --phase all --pause-at-gate
```

### Run Single Phase

```bash
# Run only Phase 1 (Research Validation)
python src/orchestrator.py run --phase research-validation

# Run Phase 2 with pause at gate
python src/orchestrator.py run --phase spec-hardening --pause-at-gate
```

### Available Phases

| Phase | Name | Service |
|-------|------|---------|
| 1 | `research-validation` | Perplexity |
| 2 | `spec-hardening` | Gemini |
| 3 | `messaging-synthesis` | ChatGPT |
| 4 | `implementation-planning` | Copilot |
| 5 | `vulnerability-audit` | Grok |

### Check Service Status

```bash
python src/orchestrator.py status --services all
```

### Estimate Costs

```bash
python src/orchestrator.py estimate --phases all
```

### Generate Synthesis Report

```bash
python src/orchestrator.py synthesis --input-dir ./results --format markdown
```

---

## Output Structure

```
results/
├── phase1_research_validation/
│   ├── precedent_verification.json
│   ├── precedent_verification.md
│   ├── funding_landscape.json
│   ├── funding_landscape.md
│   └── gate_result.json
├── phase2_spec_hardening/
│   ├── edge_case_matrix.json
│   ├── edge_case_matrix.md
│   ├── latency_constraints.json
│   └── gate_result.json
├── phase3_messaging_synthesis/
│   ├── grant_narrative_nsf.json
│   ├── grant_narrative_nsf.md
│   ├── grant_narrative_neh.json
│   ├── grant_narrative_ars.json
│   ├── artist_statement.json
│   └── gate_result.json
├── phase4_implementation_planning/
│   ├── code_architecture.json
│   ├── budget_allocation.json
│   └── gate_result.json
├── phase5_vulnerability_audit/
│   ├── assumption_critique.json
│   └── failure_scenarios.json
├── aggregated_results.json
└── EXECUTIVE_REPORT.md
```

---

## Prompt Templates

All prompt templates are in the `prompts/` directory:

```
prompts/
├── phase1_research/
│   ├── precedent_verification.txt
│   └── funding_landscape.txt
├── phase2_specification/
│   ├── edge_case_matrix.txt
│   └── latency_constraints.txt
├── phase3_messaging/
│   ├── grant_narrative_nsf.txt
│   ├── grant_narrative_neh.txt
│   ├── grant_narrative_ars.txt
│   └── artist_statement.txt
├── phase4_implementation/
│   ├── code_architecture.txt
│   └── budget_allocation.txt
├── phase5_vulnerability/
│   ├── assumption_critique.txt
│   └── failure_scenarios.txt
└── gates/
    └── all_gates.txt
```

### Customizing Prompts

Edit the `.txt` files in `prompts/` to customize for your project. Use `{placeholder}` syntax for dynamic substitution:

```
You are validating research for {project_name}.

CLAIMS TO VERIFY:
{precedent_claims}
```

Pass context when running:

```python
orchestrator.run_phase(phase, context={
    "project_name": "My Project",
    "precedent_claims": "..."
})
```

---

## Gate Validation

Each phase (except Phase 5) has a gate validation step that checks:

### Gate 1 (Research)
- ≥80% claims verified with sources
- ≥10 funding opportunities identified
- ≥3 near-term deadlines
- No contradicted claims

### Gate 2 (Specification)
- 25/25 edge cases populated
- Critical issues have mitigations
- Latency constraint achievable

### Gate 3 (Messaging)
- Multiple narrative variants generated
- Artist statement present
- Cross-narrative coherence

### Gate 4 (Implementation)
- Architecture reviewed
- Budget includes ≥20% contingency
- Timeline realistic

### Gate 5 (Vulnerability)
- All 6 assumption categories covered
- ≥10 failure scenarios
- Actionable mitigations

---

## API Cost Estimates

| Service | Tasks | Est. Tokens | Est. Cost |
|---------|-------|-------------|-----------|
| Perplexity | 2 | 6,000 | $0.01 |
| Gemini | 2 | 16,000 | $0.02 |
| ChatGPT | 4 | 16,000 | $0.16 |
| Copilot | 2 | 6,000 | $0.06 |
| Grok | 2 | 6,000 | $0.03 |
| **Total** | **12** | **50,000** | **~$0.30** |

*Actual costs depend on response length and may vary.*

---

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Formatting

```bash
black src/
```

### Type Checking

```bash
mypy src/
```

---

## Troubleshooting

### "Service not configured"
- Check that the API key is set in `config.yaml` or environment
- Run `python src/orchestrator.py status` to verify

### "Prompt template not found"
- Ensure prompt files exist in `prompts/{phase_name}/`
- Check file extension (`.txt`, `.md`, or `.prompt`)

### Timeout errors
- Increase `timeout_seconds` in `config.yaml`
- Reduce `parallel_limit` to avoid rate limits

### Gate validation fails
- Review output in `results/phaseN_*/gate_result.json`
- Address recommendations before re-running

---

## License

MIT License - See LICENSE file for details.

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

---

*Built for the Omni-Performative Engine project*
