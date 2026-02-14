# QLoRA Training Explained

**Date:** November 2, 2025  
**Purpose:** Understand QLoRA fine-tuning method, configuration, and common issues

---

## What is QLoRA?

**QLoRA** (Quantized Low-Rank Adaptation) is a memory-efficient fine-tuning method that combines:

1. **4-bit quantization** of the base model (using bitsandbytes/NF4)
2. **Low-Rank Adaptation (LoRA)** for parameter-efficient training
3. **Full precision adapters** (bfloat16) for quality retention

### How It Works

```
Base Model (8B params)
    ↓
Load in 4-bit quantization (~5GB VRAM)
    ↓
Freeze all base weights
    ↓
Add small LoRA adapters (~64MB for rank 64)
    ↓
Train ONLY the adapters in bfloat16
    ↓
Merge adapters back into base model
```

**Key Insight:** Training 64M parameters (adapters) instead of 8B parameters (full model).

---

## Memory Comparison

| Method | Base Model Memory | Trainable Params | Total VRAM | RTX 5090 (32GB) |
|--------|-------------------|------------------|------------|-----------------|
| **Full Fine-Tuning** | ~16GB (bf16) | 8B | ~40GB+ | ❌ OOM |
| **LoRA** | ~16GB (bf16) | ~64M | ~20-24GB | ✅ Tight fit |
| **QLoRA** | ~5GB (4-bit) | ~64M | ~8-12GB | ✅✅ Comfortable |

---

## Our Configuration

**File:** `fine-tuning/configs/qlora_style_transfer.yaml`

### Quantization Settings
```yaml
load_in_4bit: true              # Load base model in 4-bit
adapter: qlora                  # Use QLoRA method
bnb_4bit_quant_type: nf4        # NormalFloat4 quantization
bnb_4bit_compute_dtype: bfloat16  # Compute in bf16
bnb_4bit_use_double_quant: true   # Quantize quantization constants
```

**What this means:**
- Base Llama-3.1-8B loaded at ~5GB instead of ~16GB
- Frees 11GB VRAM for training overhead
- Quality loss minimal (<2% degradation vs full precision)

### LoRA Settings
```yaml
lora_r: 64                      # Adapter rank
lora_alpha: 128                 # Scaling factor (2x rank)
lora_dropout: 0.05              # Regularization
lora_target_modules:            # Which layers to adapt
  - q_proj                      # Query projection
  - k_proj                      # Key projection
  - v_proj                      # Value projection
  - o_proj                      # Output projection
  - gate_proj                   # MLP gate
  - up_proj                     # MLP up
  - down_proj                   # MLP down
lora_modules_to_save:           # Save full precision layers
  - embed_tokens                # Required for custom tokens
  - lm_head                     # Output layer
```

**What this means:**
- 7 attention/MLP layers get LoRA adapters
- Rank 64 = good balance (32=minimal, 128=maximum)
- Alpha 128 = amplify adapter influence
- Embedding + output layers saved in full precision

### Training Parameters
```yaml
learning_rate: 0.0001           # Conservative for small dataset
num_epochs: 5                   # Multiple passes needed with 12 samples
micro_batch_size: 2             # Per-device batch
gradient_accumulation_steps: 4  # Effective batch = 8
optimizer: paged_adamw_8bit     # Memory-efficient optimizer
```

**What this means:**
- Lower LR (1e-4) prevents overfitting on 12 samples
- 5 epochs needed for style transfer with tiny dataset
- Effective batch size 8 balances stability vs speed
- 8-bit optimizer saves additional VRAM

---

## Is This Suitable for Our Use Case?

### ✅ YES - Perfect Match

| Requirement | QLoRA Solution | Status |
|-------------|----------------|--------|
| **Memory constraint** | 8-12GB vs 40GB+ full fine-tuning | ✅ Fits RTX 5090 |
| **Style transfer** | LoRA proven for stylistic adaptation | ✅ Effective |
| **Small dataset** | QLoRA works with 100-1000 samples | ✅ Acceptable |
| **vLLM deployment** | Merge adapter → full model | ✅ Compatible |
| **Inference speed** | Same as base model after merge | ✅ No overhead |

### Training Flow

```
1. QLoRA Training (RTX 5090, ~8-12GB VRAM)
   ↓
2. Save LoRA adapter (~64MB checkpoint)
   ↓
3. Merge adapter + base model → full model
   ↓
4. Deploy merged model in vLLM (~16GB VRAM)
```

---

## Common Issues

### Issue 1: Missing `torchao` Dependency

**Error:**
```
ModuleNotFoundError: No module named 'torchao'
```

**Cause:**
- Axolotl 0.13.0.dev (main branch) added `torchao` as required dependency
- Initial setup script installed Axolotl with `--no-deps` to avoid PyTorch version conflicts
- This skipped `torchao` and other dependencies

**What is `torchao`:**
- PyTorch native quantization library (torch architecture optimization)
- Newer alternative to bitsandbytes
- Used for Quantization-Aware Training (QAT)
- NOT needed for standard QLoRA, but Axolotl requires it

**Solution (FIXED):**
Updated `fine-tuning/setup/2_install_axolotl.sh` to include `torchao` in manual dependency list.

**If you encounter this:**
Re-run setup script:
```bash
cd fine-tuning/setup
./2_install_axolotl.sh
```

### Issue 2: Flash Attention Import Error

**Error:**
```
ImportError: undefined symbol: _ZN3c104cuda29c10_cuda_check_implementationEiPKcS2_jb
```

**Cause:**
- Flash-attention compiled for different PyTorch version
- Must match PyTorch 2.8.0+cu128 exactly

**Solution:**
```bash
source ~/.venvs/finetune/bin/activate
pip uninstall -y flash-attn
MAX_JOBS=2 pip install flash-attn --no-build-isolation
```

**See:** `.smaqit/history/2025-11-02_flash_attention_wsl_memory_issue.md`

### Issue 3: WSL Memory Crashes

**Cause:**
- Flash-attention compilation uses ~4GB per parallel job
- Default WSL limits insufficient

**Solution:**
Configure `.wslconfig` BEFORE running setup scripts:
```ini
[wsl2]
memory=48GB
processors=12
```

Restart WSL: `wsl --shutdown` (PowerShell)

---

## Training Expectations

### With 12 Samples (Current)
- **Training time:** ~30-60 minutes (5 epochs)
- **Checkpoints:** 5 total (1 per epoch)
- **Expected quality:** 20-40% style transfer (proof-of-concept)
- **Production ready:** ❌ Need 100-200+ samples

### With 100-200 Samples (Production)
- **Training time:** ~2-4 hours (3-5 epochs)
- **Expected quality:** 60-80% style transfer
- **Production ready:** ✅ Suitable for deployment

### Quality Metrics
- **Vocabulary match:** % of author's word choices used
- **Sentence structure:** Match to typical patterns
- **Overall transfer score:** 0-100% (target >60% for production)

---

## QLoRA vs Alternatives

### Full Fine-Tuning
**Pros:** Maximum quality
**Cons:** 40GB+ VRAM, risk of catastrophic forgetting
**Use when:** Multi-GPU setup, smaller models (<3B)

### Standard LoRA
**Pros:** Better quality than QLoRA, faster inference prep
**Cons:** 16-20GB VRAM for 8B models
**Use when:** VRAM headroom available

### QLoRA (Our Choice)
**Pros:** Memory efficient, proven quality, works with limited VRAM
**Cons:** Slightly lower quality than LoRA
**Use when:** Single GPU (RTX 5090), 8B+ models

---

## Verification Commands

### Check Training Setup
```bash
source ~/.venvs/finetune/bin/activate

# Verify dependencies
python -c "import torch; print('PyTorch:', torch.__version__)"
python -c "import axolotl; print('Axolotl:', axolotl.__version__)"
python -c "import torchao; print('torchao:', torchao.__version__)"
python -c "import flash_attn; print('flash-attn:', flash_attn.__version__)"
python -c "import bitsandbytes; print('bitsandbytes:', bitsandbytes.__version__)"

# Verify GPU
nvidia-smi
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

### Monitor Training
```bash
# GPU utilization
watch -n 1 nvidia-smi

# Training logs
tail -f fine-tuning/logs/training_*.log

# Checkpoint progress
ls -lh fine-tuning/checkpoints/qlora-style-pipeline-test/
```

---

## Next Steps

1. **Re-run setup to install torchao (if needed):**
   ```bash
   cd fine-tuning/setup
   ./2_install_axolotl.sh
   ```

2. **Start training:**
   ```bash
   cd ../training
   ./2_train_lora.sh
   ```

3. **After training completes:**
   - Merge adapter: `python training/3_merge_adapter.py`
   - Test with vLLM: `./serve_vllm.sh merged_models/...`
   - Benchmark quality: `benchmarks/1_voice_comparison.py`

4. **For production:**
   - Collect 100-200+ writing samples
   - Re-run data preparation with chunking
   - Retrain with larger dataset
   - Target >60% transfer score

---

## References

- **QLoRA Paper:** https://arxiv.org/abs/2305.14314
- **LoRA Paper:** https://arxiv.org/abs/2106.09685
- **Axolotl Docs:** https://github.com/OpenAccess-AI-Collective/axolotl
- **bitsandbytes:** https://github.com/TimDettmers/bitsandbytes

## Related Documentation

- `FINE_TUNING_SETUP.md` - Complete setup guide
- `fine-tuning/README.md` - Quick reference
- `.smaqit/history/2025-11-02_flash_attention_wsl_memory_issue.md` - WSL memory config
- `.smaqit/history/2025-10-30_pytorch_axolotl_rtx5090_compatibility.md` - Environment setup
