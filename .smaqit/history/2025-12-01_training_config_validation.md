# Training Config Validation Session

**Date:** 2025-12-01

## Summary

Reviewed, fixed, and validated both QLoRA and LoRA training configurations for Visions of Gaea style transfer. Both configs passed 3-step quick tests and are ready for full training runs.

## Actions Taken

### 1. Training Data Verification
- Confirmed 36 training examples in `visions_training.jsonl`
- Confirmed 4 validation examples in `validation.jsonl`
- Data format: prefix-completion with `chat_template` type

### 2. QLoRA Config Fixes (`qlora_style_transfer.yaml`)
- **Validation setup**: Changed from `eval_steps` to `test_datasets` to use pre-split validation data
- **Removed**: `eval_steps` (incompatible with `val_set_size: 0`)
- **Commented out**: `lora_modules_to_save: [embed_tokens, lm_head]` - not needed for style transfer without new tokens
- **Result**: Reduced trainable params from 196M to 168M (13% reduction)

### 3. LoRA Config Rewrite (`lora_style_transfer.yaml`)
- Completely rewrote outdated config with:
  - Correct dataset paths (`data/processed/visions_training.jsonl`)
  - Proper `chat_template` type
  - `sequence_len: 4096` (was 2048)
  - `warmup_ratio: 0.1` instead of fixed steps
  - `gradient_accumulation_steps: 4`
  - `adamw_torch` optimizer
  - `test_datasets` for validation

### 4. Quick Tests with `--max_steps=3`
Both configs tested successfully:

| Config | Runtime | VRAM | Trainable Params | Throughput | Final Loss |
|--------|---------|------|------------------|------------|------------|
| QLoRA | 57s | 17.5GB | 168M | ~560 tok/s | 2.78 |
| LoRA | 25s | 24.4GB | 168M | ~2200 tok/s | 2.68 |

## Key Decisions

### LoRA vs QLoRA for RTX 5090
- **Recommendation**: Use LoRA (full bf16 precision)
- **Rationale**: 32GB VRAM easily fits ~24GB LoRA training, ~4x faster than QLoRA, no precision loss from quantization

### lora_modules_to_save Decision
- **Commented out** rather than removed
- **Reason**: Training embed_tokens/lm_head only needed when adding new tokens to vocabulary
- **Style transfer**: Base model's byte-level BPE handles "neurolink", "Balthazar" etc. via subword tokenization

## Files Modified
- `fine-tuning/configs/qlora_style_transfer.yaml` - Fixed validation, commented lora_modules_to_save
- `fine-tuning/configs/lora_style_transfer.yaml` - Complete rewrite

## Next Steps
1. Run full LoRA training: `./2_train_lora.sh configs/lora_style_transfer.yaml`
2. Merge adapter with base model: `python 3_merge_adapter.py --auto`
3. Validate style transfer quality with benchmarks
4. Consider updating `2_train_lora.sh` default to use LoRA config

## Technical Notes

### CLI Override Testing
Axolotl supports `--max_steps=N` CLI override for quick config validation:
```bash
python -m axolotl.cli.train config.yaml --max_steps=3
```
This runs only 3 gradient updates regardless of epoch settings, useful for:
- Verifying config syntax
- Checking VRAM requirements
- Testing data loading
- Validating output directory creation
