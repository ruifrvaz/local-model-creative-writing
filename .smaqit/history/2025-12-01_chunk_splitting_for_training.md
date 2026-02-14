# Task 003: Visions of Gaea Training Data Preparation

**Date:** 2025-12-01

## Summary

Complete session preparing QLoRA fine-tuning data for Visions of Gaea style transfer. Covered training format decisions, agent creation, data preparation script rewrite, and chunk optimization.

---

## 1. Training Format Decisions

### User Workflow Analysis
User's writing workflow: completion-style prompting where they start a sentence/scene and expect the model to continue:
```
User prompt: "Haji and Alan walked along the street. It was night, Alan was worried about his future. Haji said,"
Expected: Model continues the narrative naturally
```

### Key Decisions Made

**System Prompts:** No system prompt in training data
- System prompt comes from Continue.dev's `scifi_writer.md` at inference time
- Including in training could conflict with inference-time prompts
- Model learns pure narrative style, not instruction-following patterns

**Training Format:** Prefix-completion (not instruction-style)
- Each training example: narrative prefix (5-10%) → narrative completion (90-95%)
- No generic instructions like "Continue this story"
- Teaches model to continue from any narrative starting point

**Base Model:** `meta-llama/Llama-3.1-8B-Instruct`
- Instruct models retain instruction-following from base training
- Can still respond to inference-time system prompts
- Better than base models for controllable generation

---

## 2. Agent Creation

Created `.github/agents/fine-tuning-trainer.md` for future training sessions:
- Documents RTX 5090 constraints
- Axolotl + QLoRA workflow
- Virtual environment: `~/.venvs/finetune`
- PyTorch 2.8.0+cu128 requirement

---

## 3. Data Preparation Script Rewrite

Rewrote `fine-tuning/training/1_prepare_data.py`:

**Before:** Re-chunked already-curated data with generic instruction prompts
**After:** Treats each curated chunk as one example with prefix-completion format

Key changes:
- `split_prefix_completion()`: Splits at sentence boundaries, 5-10% prefix ratio
- `create_training_example()`: Creates messages format without system prompt
- Filters out manuscript file and metadata files
- 90/10 train/validation split

---

## 4. Prefix Length Adjustment

Initial implementation: 5-15% prefix
User concern: 15% too long, reduces completion learning

Adjusted to: 5-10% prefix
- Shorter prefixes = more completion text to learn from
- Still enough context for model to understand continuation point

---

## 5. Token Length Analysis and Chunk Splitting

### Problem
Initial analysis revealed:
- 12 examples over 3000 tokens
- 1 example over 4000 tokens (chunk_015 at 4435 tokens)
- Config `sequence_len: 4096` would truncate largest example

### Solution
Split 5 oversized chunks at narrative boundaries:

| Original Chunk | Words | Split Into |
|----------------|-------|------------|
| chunk_015 (Mother hacking) | 3046 | 015a dinner scene (656w) + 015b bedroom/hacking (2390w) |
| chunk_030 (Specialist rescue) | 2813 | 030a stalker attack (1868w) + 030b decision to help (945w) |
| chunk_013 (Torment science pt2) | 2570 | 013a epidemiology (1095w) + 013b pathophysiology (1475w) |
| chunk_023 (Journey/bracelet) | 2658 | 023a journey discussion (944w) + 023b lobby/transformation (1714w) |
| chunk_029 (Hub infiltration) | 2570 | 029a checkpoint denied (1742w) + 029b air intake field (828w) |

### Narrative Boundary Rationale
Splits at scene changes, topic shifts, location changes rather than even word counts:
- Preserves complete narrative units (scene openings, dialogue exchanges, closures)
- Model learns proper scene structure
- Even splits would cut mid-scene, teaching arbitrary endings

---

## 6. Final Statistics

| Metric | Before Splits | After Splits |
|--------|---------------|--------------|
| Total chunks | 35 | 40 |
| Training examples | 31 | 36 |
| Validation examples | 4 | 4 |
| Max tokens | 4435 | 3682 |
| Avg tokens | 2647 | 2303 |
| Examples >4000 tokens | 1 | 0 |

---

## Files Modified

**Created:**
- `.github/agents/fine-tuning-trainer.md` - Training agent definition
- 10 split chunk files in `fine-tuning/data/raw/visions_of_gaea/` (015a/b, 030a/b, 013a/b, 023a/b, 029a/b)
- `fine-tuning/data/raw/visions_of_gaea/backup/` - Original oversized chunks

**Rewritten:**
- `fine-tuning/training/1_prepare_data.py` - Prefix-completion format

**Updated:**
- `fine-tuning/training/2_train_lora.sh` - Dataset path to `visions_training.jsonl`
- `fine-tuning/configs/qlora_style_transfer.yaml` - Dataset paths, sequence_len=4096

**Generated:**
- `fine-tuning/data/processed/visions_training.jsonl` (36 examples)
- `fine-tuning/data/processed/validation.jsonl` (4 examples)

---

## Next Steps

Training data ready. Start training:
```bash
cd ~/scifi-llm/fine-tuning/training && ./2_train_lora.sh
```

Expected:
- 36 examples × 3 epochs = ~108 training steps
- Estimated time: 2-4 hours on RTX 5090
- Output: `checkpoints/qlora-visions-style/`

Post-training:
1. Merge adapter: `python 3_merge_adapter.py --auto`
2. Validate style transfer with benchmarks
3. Configure Continue.dev to use fine-tuned model
