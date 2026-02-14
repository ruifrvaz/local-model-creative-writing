# Compare Biased vs Unbiased Style Analysis

**Priority:** 1  
**Status:** Completed  
**Created:** 2025-11-30  
**Completed:** 2025-11-30

## Description

Compare two parallel style analysis approaches for the "Visions of Gaea" manuscript:
- **Biased:** Agent with example outputs in prompts (`.github/agents/style-analyzer.md`)
- **Unbiased:** Agent with structural scaffolding only (`.github/agents/style-analyzer-unb.md`)

Determine which approach produces more accurate, internally consistent analysis for use in style transfer training data generation.

## Acceptance Criteria

- [x] Run both agents on the same manuscript sections
- [x] Compare outputs across all metrics (sentence length, dialogue ratio, scene breaks, POV)
- [x] Verify countable metrics against ground truth (scene breaks)
- [x] Score both approaches on consistency, precision, and arc sensitivity
- [x] Document findings with methodology
- [x] Select winner for use in style-transfer-generator workflow

## Results

**Winner:** Unbiased approach (27/30 vs 21/30)

**Key Finding:** Ground truth verification revealed unbiased analysis matched actual scene break counts exactly (11 total). Biased analysis reported 17 (significant discrepancy in Section 1: reported 8, actual 2).

**Outputs:**
- `docs/ANCHORING_BIAS_IN_LLM_PROMPTS.md` — Scientific paper documenting methodology and findings
- `docs/PROMPT_ENGINEERING_ANCHORING_BIAS.md` — Extended discussion of anchoring mechanism
- `fine-tuning/data/styles/visions_of_gaea/ANALYSIS_COMPARISON.md` — Detailed metric comparison

**Recommendation:** Use unbiased analysis outputs (`*_unbiased.*` files) for style transfer generation.

## Notes

The comparison revealed a potential prompt engineering insight: example outputs in analytical prompts may function as cognitive anchors rather than neutral format templates. This is documented as a cautious recommendation pending further study across different models and tasks.
