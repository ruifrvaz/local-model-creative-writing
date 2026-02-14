# PyTorch 2.8.0 + Axolotl RTX 5090 Compatibility

**Date:** October 30, 2025  
**Category:** Fine-tuning infrastructure upgrade  
**Impact:** Critical - Enables training on RTX 5090 Blackwell (sm_120)

## Problem Statement

Training pipeline failed with RTX 5090 due to PyTorch version incompatibility:
- Initial attempt used PyTorch 2.6.0+cu124 (from old Axolotl requirements)
- RTX 5090 Blackwell architecture (sm_120) not supported by PyTorch <2.8.0
- Error: `NVIDIA GeForce RTX 5090 with CUDA capability sm_120 is not compatible with the current PyTorch installation`
- Axolotl 0.12.2 pinned to `torch==2.6.0` in requirements (outdated)

## Solution Overview

Upgraded to PyTorch 2.8.0+cu128 and Axolotl from main branch:
1. Uninstalled old PyTorch 2.6.0+cu124
2. Installed PyTorch 2.8.0 with CUDA 12.8 from stable index (not nightly)
3. Removed Axolotl with pinned dependencies
4. Installed Axolotl from GitHub main without dependencies (`--no-deps`)
5. Manually installed compatible dependency versions

## Key Decisions

**Why PyTorch 2.8.0 instead of 2.10.0 nightly?**
- User requested alignment with vLLM stack (already using 2.8.0)
- Stable release more reliable than nightly builds
- Proven compatibility with CUDA 12.8 and RTX 5090 sm_120
- Avoids potential API changes in cutting-edge nightlies

**Why Axolotl from main instead of PyPI release?**
- Latest PyPI release (0.12.2) pins `torch==2.6.0` (incompatible)
- Main branch has no torch version pins (accepts 2.8.0+)
- Installing with `--no-deps` prevents downgrade to 2.6.0
- Allows manual installation of compatible dependencies

## Technical Details

**PyTorch Installation:**
```bash
pip install torch==2.8.0 torchvision torchaudio \
  --index-url https://download.pytorch.org/whl/cu128
```

**Verification:**
- PyTorch: 2.8.0+cu128
- CUDA: 12.8
- Compute capability: sm_120 (recognized without warnings)
- GPU: NVIDIA GeForce RTX 5090

**Axolotl Installation:**
```bash
pip uninstall -y axolotl xformers torchao
pip install --no-deps git+https://github.com/axolotl-ai-cloud/axolotl.git
pip install --upgrade transformers accelerate datasets peft trl bitsandbytes
```

**Dependency Versions (final):**
- axolotl: 0.13.0.dev (from main)
- transformers: 4.57.1
- accelerate: 1.11.0
- peft: 0.17.1
- trl: 0.24.0
- bitsandbytes: 0.48.2

## Configuration Changes

**Fixed Axolotl config validation errors** (newer Axolotl API stricter):

1. **Mutually exclusive parameters removed:**
   - `evals_per_epoch` (conflicts with `eval_steps`)
   - `warmup_ratio` (conflicts with `warmup_steps`)

2. **Required parameters added:**
   - `micro_batch_size: 2` (required alongside `gradient_accumulation_steps`)

3. **Type corrections:**
   - `wandb_watch: false` → `wandb_watch:` (empty string, not boolean)
   - `wandb_log_model: false` → `wandb_log_model:` (empty string, not boolean)

**Final config summary:**
- QLoRA 4-bit quantization with bfloat16
- LoRA rank 64, alpha 128
- Batch size 2, gradient accumulation 4 (effective batch 8)
- Learning rate 1e-4, 5 epochs (small dataset optimization)
- Eval every 10 steps

## Files Modified

**Setup Scripts:**
- `fine-tuning/setup/0_create_venv.sh` - Unchanged
- `fine-tuning/setup/1_install_torch.sh`
  - Updated to install PyTorch 2.8.0 with CUDA 12.8
  - Added idempotency check (version detection)
  - Force uninstall before install to ensure cu128 versions
  - Updated docstring and version checks

- `fine-tuning/setup/2_install_axolotl.sh` (CREATED)
  - New script for Axolotl main installation
  - Installs without dependencies to avoid torch downgrade
  - Manually installs compatible dependency stack
  - Verification step tests all imports

- `fine-tuning/setup/3_install_training_stack.sh` (RENAMED from 2_install_training_stack.sh)
  - Removed redundant Axolotl installation (handled by script 2)
  - Now only installs: flash-attention, DeepSpeed, monitoring tools
  - Updated to follow numbered workflow convention (0-3 sequence)
  - Verifies both PyTorch and Axolotl before proceeding

**Training Configuration:**
- `fine-tuning/configs/qlora_style_transfer.yaml`
  - Removed `evals_per_epoch` (mutually exclusive)
  - Removed `warmup_ratio` (mutually exclusive)
  - Added `micro_batch_size: 2` (required)
  - Changed wandb booleans to empty strings

**Training Script:**
- `fine-tuning/training/2_train_lora.sh`
  - Updated docstring: PyTorch 2.6.0 → 2.8.0

**Documentation:**
- `fine-tuning/README.md`
  - Updated setup step: `2_install_training_stack.sh` → split into `2_install_axolotl.sh` + `3_install_training_stack.sh`
  - Added inline comments about PyTorch 2.8.0 and RTX 5090
  - Updated script numbering to follow 0-3 sequence
  - Updated setup table with correct script names and durations

- `fine-tuning/FINE_TUNING_SETUP.md`
  - Updated hardware specs to mention Blackwell sm_120 and PyTorch 2.8.0
  - Updated Axolotl installation section with new scripts
  - Fixed training script example (venv path)

- `.github/copilot-instructions.md`
  - Updated PyTorch version: "2.8.0 (vLLM), 2.6.0 (fine-tuning)" → "2.8.0+cu128 (vLLM + fine-tuning)"
  - Updated file structure: setup scripts now 0-3 sequence (0_create_venv, 1_install_torch, 2_install_axolotl, 3_install_training_stack)
  - Added note about RTX 5090 sm_120 support

## Testing Results

**Import Test:**
```
Axolotl: 0.13.0.dev
Transformers: 4.57.1
Accelerate: 1.11.0
PEFT: 0.17.1
[OK] All imports successful
```

**Training Launch:**
```
compute_capability: sm_120
torch_version: 2.8.0
load_in_4bit: true
bf16: true
batch_size: 8
lora_r: 64
```

Configuration validated successfully, training initialized without errors.

## Known Limitations

**Dependency Warnings (non-critical):**
- Minor version mismatches between Axolotl dev and installed packages
- Example: `accelerate==1.10.1` (required) vs `1.11.0` (installed)
- These are recommendations, not hard requirements
- All imports successful, training functional

**Dataset Size:**
- Current: 12 training samples, 2 validation samples
- Production recommendation: 50-100+ samples
- This is a proof-of-concept run to validate pipeline

## Impact on Workflow

**Before (broken):**
```bash
source ~/.venvs/finetune/bin/activate
./2_train_lora.sh
# Error: sm_120 not compatible with PyTorch 2.6.0
```

**After (working):**
```bash
source ~/.venvs/finetune/bin/activate  # Now has PyTorch 2.8.0+cu128
./2_train_lora.sh  # Training starts successfully
```

**Setup workflow updated:**
```bash
cd fine-tuning/setup
./0_create_venv.sh           # Creates ~/.venvs/finetune
./1_install_torch.sh         # PyTorch 2.8.0+cu128
./2_install_axolotl.sh       # Axolotl main + dependencies
./3_install_training_stack.sh  # DeepSpeed + flash-attention + monitoring
```

## Project Conventions Applied

**Script numbering follows project standard:**
- `0-n`: Setup workflow (run once in sequence)
- Fine-tuning setup now properly numbered: 0 → 1 → 2 → 3
- Each script has single responsibility:
  - 0: Create virtual environment
  - 1: Install PyTorch with correct CUDA version
  - 2: Install Axolotl without dependency conflicts
  - 3: Install additional training utilities (DeepSpeed, monitoring)

**This aligns with existing conventions:**
- vLLM setup: 0-7 numbered sequence
- RAG setup: 0-2 numbered sequence
- Health checks: 9-13 numbered (separate from setup)

1. **Bleeding-edge hardware requires careful version management**
   - RTX 5090 Blackwell sm_120 only supported in PyTorch 2.8.0+
   - PyPI releases lag behind hardware support
   - Sometimes need to install from source/main branch

2. **Version pins can block upgrades**
   - Axolotl's `torch==2.6.0` pin prevented compatibility
   - `--no-deps` flag essential for breaking dependency locks
   - Manual dependency installation gives more control

3. **Configuration validation gets stricter**
   - Newer Axolotl enforces mutual exclusivity
   - Type checking stricter (booleans vs strings)
   - Always test config after upgrading frameworks

4. **Alignment with existing stack beneficial**
   - Using same PyTorch version as vLLM (2.8.0) simplifies environment
   - Reduces confusion about "which version for which task"
   - Makes troubleshooting easier

## Next Steps

- Training run in progress (30-60 minutes expected)
- Create `3_merge_adapter.py` script for LoRA weight merging
- Implement voice comparison benchmarks (currently TODO)
- Expand training dataset to 50+ samples for production use

## References

- PyTorch CUDA 12.8 index: https://download.pytorch.org/whl/cu128
- Axolotl GitHub: https://github.com/axolotl-ai-cloud/axolotl
- RTX 5090 specs: Blackwell architecture, sm_120, 32GB VRAM
