# Style Analysis Comparison and Validation

**Date:** 2025-11-30  
**Task:** 006_compare_biased_vs_unbiased_style_analysis

## Summary

Compared two style analysis approaches (biased vs unbiased prompts) for the "Visions of Gaea" manuscript. Ground truth verification confirmed unbiased approach produces accurate, verifiable metrics.

## Actions Taken

1. **Read all analysis outputs** from both branches (`section_analyses/` and `section_analyses_biased/`)
2. **Created comparison document** (`ANALYSIS_COMPARISON.md`) with metric-by-metric breakdown
3. **Verified scene breaks against source** — counted `***` markers in manuscript sections
4. **Scored both approaches** (27/30 unbiased vs 21/30 biased)
5. **Enhanced unbiased files** with word frequency data (body parts, signature phrases)
6. **Documented prompt engineering insight** in `docs/ANCHORING_BIAS_IN_LLM_PROMPTS.md`

## Key Findings

- Unbiased analysis matched ground truth exactly (11 scene breaks)
- Biased analysis showed significant discrepancy (17 reported, 8 in Section 1 where actual is 2)
- Example outputs in prompts may induce anchoring bias (cautious conclusion, n=1)

## Files Modified/Created

- `fine-tuning/data/styles/visions_of_gaea/ANALYSIS_COMPARISON.md` — created
- `fine-tuning/data/styles/visions_of_gaea/STYLE_STATISTICS_unbiased.json` — enhanced
- `fine-tuning/data/styles/visions_of_gaea/STYLE_PATTERNS_unbiased.md` — enhanced
- `docs/ANCHORING_BIAS_IN_LLM_PROMPTS.md` — created (scientific paper format)
- `docs/PROMPT_ENGINEERING_ANCHORING_BIAS.md` — created (extended discussion)
- `tasks/006_compare_biased_vs_unbiased_style_analysis.md` — created (completed)

## Decision

**Use unbiased analysis outputs** for style transfer generation:
- `STYLE_TRANSFER_GUIDE_unbiased.md`
- `STYLE_STATISTICS_unbiased.json`
- `STYLE_PATTERNS_unbiased.md`

## Next Steps (Parallel Execution)

These tasks can run concurrently:

| Task | Agent | Environment | Description |
|------|-------|-------------|-------------|
| **003** | Local (Axolotl) | `~/.venvs/finetune` | Fine-tune on chunked manuscript (35 chunks, ~5hrs) |
| **007** | Cloud (style-transfer-generator) | Claude API | Generate new content across universes |
| **008** | Cloud (new style-converter agent) | Claude API | Reshape existing 139 scenes to match style |

### Task 003: Fine-Tune with Manuscript Chunks
- **Run locally** on RTX 5090
- **Input:** `fine-tuning/data/raw/visions_of_gaea/chunk_*.txt`
- **Process:** `1_prepare_data.py` → `2_train_lora.sh` → `3_merge_adapter.py`
- **Duration:** ~5 hours unattended

### Task 007: Generate New Content (Cloud)
- **Run on cloud** via style-transfer-generator agent
- **Input:** Unbiased style reference files
- **Output:** New scenes in author's voice across multiple universes
- **Target:** 500+ instruction-response pairs

### Task 008: Reshape Existing Content (Cloud)
- **Create new agent:** `style-converter.md` (transforms existing content to match style)
- **Run on cloud** via new style-converter agent
- **Input:** 139 existing scenes in `fine-tuning/data/raw/`
- **Output:** Same scenes converted to second-person POV with author's voice
- **Location:** `fine-tuning/data/reshaped/`

---

## Cleanup Performed

- Removed biased agent (`.github/agents/style-analyzer.md` with examples)
- Removed biased outputs (`*_biased.*` files, `section_analyses_biased/`)
- Renamed unbiased files to standard names (removed `_unbiased` suffix)
- Archived section analyses and manuscript sections
- Moved study documentation to `docs/studies/anchoring_bias_in_llm_prompts/`
- Restored `ACCUMULATION_TEMPLATE.md` to parent directory (style-merger reference)
