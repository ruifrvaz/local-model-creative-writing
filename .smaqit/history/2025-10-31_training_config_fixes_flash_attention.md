# Training Configuration Fixes and Flash Attention Issue

**Date:** October 31, 2025  
**Category:** Fine-tuning configuration debugging  
**Impact:** Identified multiple config issues preventing training, flash-attention incompatibility with PyTorch 2.8.0

## Session Context

Following the PyTorch 2.8.0 + Axolotl migration (see 2025-10-30_pytorch_axolotl_rtx5090_compatibility.md), attempted first training run with proof-of-concept dataset (12 training samples, 2 validation samples from 17 chapter files).

## Problems Discovered

### 1. Setup Script Numbering Conflict

**Issue:** Two scripts both named `2_*.sh` in `fine-tuning/setup/`:
- `2_install_axolotl.sh` (new, installs Axolotl from main)
- `2_install_training_stack.sh` (old, redundant Axolotl installation)

**Root cause:** When creating `2_install_axolotl.sh`, didn't check for existing numbered scripts.

**Solution:**
- Renamed `2_install_training_stack.sh` → `3_install_training_stack.sh`
- Removed redundant Axolotl installation from script 3
- Script 3 now only installs: flash-attention, DeepSpeed, monitoring tools
- Deleted unused `activate_finetune.sh` helper (not referenced anywhere)

**Final setup sequence (0-3):**
```bash
0_create_venv.sh           # Create ~/.venvs/finetune
1_install_torch.sh         # PyTorch 2.8.0+cu128
2_install_axolotl.sh       # Axolotl from main + dependencies
3_install_training_stack.sh # DeepSpeed + flash-attn + monitoring
```

### 2. Wandb (Weights & Biases) Configuration Error

**Issue:** Training crashed immediately with truncated logs (162 lines, only showed config).

**Root cause:** Config had `wandb_project: scifi-style-transfer` but script set `WANDB_DISABLED=true`. Axolotl tried to initialize wandb without authentication, causing silent crash.

**What is wandb:**
- ML experiment tracking platform (wandb.ai)
- Logs metrics, visualizations, hyperparameters
- Requires account + authentication
- Not essential for local training

**Solution:** Commented out wandb settings in config:
```yaml
# wandb_project: scifi-style-transfer
# wandb_watch:
# wandb_log_model:
```

### 3. Data Format Mismatch

**Issue:** `ValueError: text input must be of type str...`

**Root cause:** Config specified `type: completion` (expects plain text) but data uses chat format with `messages` array.

**Data format:**
```jsonl
{"messages": [
  {"role": "system", "content": "You are a sci-fi author..."},
  {"role": "user", "content": "Write a scene..."},
  {"role": "assistant", "content": "FULL CHAPTER TEXT"}
]}
```

**Solution:** Changed dataset type:
```yaml
datasets:
  - path: data/processed/training.jsonl
    type: chat_template  # Was: completion
    field: messages
```

### 4. Missing LoRA Parameter

**Issue:** `ValueError: Please set lora_modules_to_save to ['embed_tokens', 'lm_head'] when using an adapter and changing the special tokens.`

**Root cause:** Using custom Llama-3 special tokens requires saving embedding layers.

**Solution:** Added to config:
```yaml
lora_modules_to_save:
  - embed_tokens
  - lm_head
```

### 5. Flash Attention Import Error (UNRESOLVED)

**Issue:** 
```
ImportError: flash_attn_2_cuda.cpython-312-x86_64-linux-gnu.so: 
undefined symbol: _ZN3c104cuda29c10_cuda_check_implementationEiPKcS2_jb
```

**Root cause:** Flash-attention library compiled for different PyTorch version (likely 2.6.0). PyTorch 2.8.0 has different CUDA symbols.

**Attempted workaround:** Disabled flash_attention in config:
```yaml
flash_attention: false
attn_implementation: sdpa  # Scaled dot-product attention
```

**User decision:** Don't disable flash-attention. Needs proper fix (reinstall flash-attn for PyTorch 2.8.0).

**Status:** Training paused until flash-attention reinstalled.

## Data Preparation Discovery

**Question raised:** "Why only 12 training samples from 17 chapter files?"

**Analysis:**
- Input: 17 chapter files in `data/raw/`
- Output: 14 total samples (12 train + 2 validation)
- Missing: 3 files (likely README.md or filtered by size)

**Key finding:** Each chapter became ONE sample (not chunked).

**Current sample structure:**
- 1 sample = 1 entire chapter (~6000+ tokens)
- Script has chunking logic (`chunk_text` function) but wasn't used
- Should be: 1 chapter → 5-10 chunks → 5-10 samples

**Impact:**
- 12 samples = proof-of-concept only
- Expected transfer score: 20-40% (below 60% production threshold)
- Production needs: 100-200+ samples (properly chunked)

**User decision:** Proceed with 12 samples for testing, re-chunk data later for production.

## Files Modified

**Configuration:**
- `fine-tuning/configs/qlora_style_transfer.yaml`
  - Commented out wandb settings
  - Changed `type: completion` → `type: chat_template`
  - Added `lora_modules_to_save: [embed_tokens, lm_head]`
  - Changed `flash_attention: true` → `flash_attention: false` (temporary)
  - Added `attn_implementation: sdpa`

**Setup scripts:**
- Renamed: `fine-tuning/setup/2_install_training_stack.sh` → `3_install_training_stack.sh`
- Updated: Script 3 to only install DeepSpeed/flash-attn/monitoring (removed Axolotl)
- Deleted: `fine-tuning/setup/activate_finetune.sh` (unused helper)

**Documentation:**
- `fine-tuning/README.md` - Updated setup sequence (0-3), script descriptions, table
- `.github/copilot-instructions.md` - Updated file structure, added critical warnings section
- `docs/history/2025-10-30_pytorch_axolotl_rtx5090_compatibility.md` - Added script 3 info

## Training Attempts Log

All attempts failed at different stages:

1. **Attempt 1:** Wandb initialization crash (silent failure)
2. **Attempt 2:** Data format error (`completion` vs `chat_template`)
3. **Attempt 3:** Missing `lora_modules_to_save` parameter
4. **Attempt 4:** Flash-attention import error (CUDA symbol mismatch)
5. **Attempt 5:** User stopped to avoid disabling flash-attention

**Current config state:**
- Wandb: disabled ✓
- Data type: chat_template ✓
- LoRA params: complete ✓
- Flash attention: disabled (needs proper fix)

## Next Steps (Resume Tomorrow)

### Immediate: Fix Flash Attention
```bash
source ~/.venvs/finetune/bin/activate
pip uninstall -y flash-attn
pip install flash-attn --no-build-isolation
# Test import
python -c "import flash_attn; print(flash_attn.__version__)"
```

### Then: Start Training
```bash
cd fine-tuning/training
./2_train_lora.sh
# Monitor: tail -f logs/training_*.log
```

**Expected outcomes:**
- Training time: ~30-60 minutes (12 samples, 5 epochs)
- Checkpoints: `checkpoints/qlora-style-pipeline-test/`
- Limited style transfer (20-40%) due to small dataset

### Future: Improve Data Quality
```bash
cd fine-tuning/training
python 1_prepare_data.py --input ../data/raw/ \
  --min-tokens 500 --max-tokens 2000 \
  --split 0.9
# Expected: 85-170 samples with proper chunking
```

## Lessons Learned

1. **Script numbering is critical** - Always check existing scripts before creating new ones
2. **Wandb errors are silent** - Disable explicitly if not using
3. **Data format matters** - `completion` vs `chat_template` are fundamentally different
4. **Flash-attention version-sensitive** - Must match PyTorch version exactly
5. **Chunking is essential** - 1 sample per chapter is insufficient for fine-tuning
6. **Config validation happens late** - Axolotl doesn't catch errors until model loading

## Technical Details

**Flash-attention compilation:**
- Compiled against specific PyTorch CUDA API
- PyTorch 2.8.0 changed CUDA symbol names
- Needs recompilation: `pip install flash-attn --no-build-isolation --force-reinstall`

**Sample packing efficiency:**
- Axolotl reported: `sample_packing_eff_est: 0.84` (84% GPU utilization)
- Max steps calculated: 5 steps (12 samples / batch_size 8 × 5 epochs)

**Training would run if flash-attn fixed:**
- QLoRA 4-bit quantization
- Batch size: 8 (micro_batch 2 × grad_accum 4)
- Learning rate: 1e-4 (conservative for small dataset)
- Optimizer: paged_adamw_8bit (memory efficient)

## Project Conventions Reminder

**Setup script numbering (NEVER VIOLATE):**
- 0-n: Setup workflow (run ONCE in SEQUENCE)
- Check existing scripts before adding new ones
- Update ALL documentation when changing sequence
- Test complete workflow 0→n after changes

**Added to copilot-instructions.md:**
- Critical warnings section at top
- Script numbering rules with examples
- Virtual environment dependency map
- Setup script organization for all components
