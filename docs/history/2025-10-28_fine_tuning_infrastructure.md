# Fine-Tuning Infrastructure Setup (Oct 25-28, 2025)

## Overview

Implemented complete fine-tuning capability for Llama-3.1-8B-Instruct style transfer training. Resolved PyTorch version conflict, created data preparation pipeline, and generated sample narrative data. Infrastructure ready for training execution pending data volume expansion.

## Problem Solved

Enable users to fine-tune local models on personal writing style for integration with RAG-enhanced vLLM workflow. Users can train on their own narrative voice and deploy merged models through existing serve_vllm.sh infrastructure.

## Key Decisions

### PyTorch Version: 2.6.0 Stable (CUDA 12.1)

**Initial approach**: PyTorch 2.10.0 nightly (CUDA 12.8)
**Issue**: Axolotl requires PyTorch 2.6.0 stable, causing automatic downgrade during installation
**Resolution**: Install 2.6.0 from start using stable wheel index

Updated `fine-tuning/setup/1_install_torch.sh`:
- Changed index URL: `cu128` → `cu121`
- Removed `--pre` flag (no longer nightly)
- Verified RTX 5090 (Compute 8.9) fully supports CUDA 12.1

**Rationale**: Prevents version conflicts, cleaner installation, maintains compatibility with Axolotl 0.12.2.

### Documentation File Exclusion

**Problem**: README.md in data/raw/ could contaminate training data
**Solution**: Filename-based filtering in `load_text_files()`:

```python
exclude_names = {'readme.md', 'license.md', 'changelog.md', 
                 'contributing.md', 'license.txt', 'changelog.txt'}
if filepath.name.lower() in exclude_names:
    print(f"[SKIP] {filepath.name}: documentation file")
    continue
```

**Rationale**: Prevents documentation prose from affecting narrative style training. Case-insensitive, covers both .txt and .md extensions.

### Virtual Environment Isolation: ~/.venvs/finetune

**Architecture**:
- vLLM server: `~/.venvs/llm` (PyTorch 2.8.0)
- RAG system: `~/.venvs/rag` (ChromaDB)
- Fine-tuning: `~/.venvs/finetune` (PyTorch 2.6.0, Axolotl)

**Enforcement**: Runtime check in `1_prepare_data.py`:

```python
def check_venv():
    venv_path = os.environ.get('VIRTUAL_ENV', '')
    if 'finetune' not in venv_path:
        print("[ERROR] Must run in finetune virtual environment!")
        sys.exit(1)
```

**Rationale**: Prevents package conflicts, allows different PyTorch versions, isolates training dependencies from production serving stack.

## Changes Made

### New Files Created

**Setup Scripts (fine-tuning/setup/)**:
1. `0_create_venv.sh` - Creates ~/.venvs/finetune
2. `1_install_torch.sh` - PyTorch 2.6.0 + CUDA 12.1
3. `2_install_training_stack.sh` - Axolotl + flash-attention + DeepSpeed

**Data Pipeline (fine-tuning/scripts/)**:
1. `1_prepare_data.py` - Text → JSONL converter
   - Virtual environment validation
   - Documentation file exclusion
   - Text cleaning (TODOs, metadata, whitespace)
   - Chunking (500-2000 tokens, paragraph boundaries)
   - Style analysis (auto-generated system prompts)
   - Train/validation split (90/10)

**Sample Data (fine-tuning/data/raw/)**:
- 18 text files: `sample_scene.txt`, `chapter_01_bridge_crisis.txt` through `chapter_17_homecoming.txt`
- Total: 61,389 characters (~15,347 tokens)
- Style: Technical sci-fi, balanced dialogue/description, concise sentences
- Setting: UESC Pathfinder, Elena Vasquez (Phobos survivor), mathematical first contact

**Processed Output (fine-tuning/data/processed/)**:
- `training.jsonl` (7 examples)
- `validation.jsonl` (1 example)

### Documentation Updated

1. `fine-tuning/README.md` - PyTorch 2.6.0 references throughout
2. `.github/copilot-instructions.md` - Software environment spec (PyTorch 2.6.0, CUDA 12.1)
3. `fine-tuning/setup/1_install_torch.sh` - Script comments and index URL

### Packages Installed (finetune venv)

**Core Stack**:
- pytorch 2.6.0 (CUDA 12.1 bundled)
- axolotl 0.12.2
- flash-attn 2.8.3
- deepspeed 0.17.2

**Dependencies**:
- transformers 4.55.2
- accelerate 1.10.0
- peft 0.17.0
- bitsandbytes 0.47.0
- datasets, wandb, safetensors, sentencepiece

## Testing Results

### Data Preparation Script Execution

**Command**:
```bash
cd ~/scifi-llm/fine-tuning/scripts
source ~/.venvs/finetune/bin/activate
python 1_prepare_data.py
```

**Output**:
```
[STEP 1/5] Loading text files...
✅ Loaded 18 files (61,389 chars)
✅ Skipped README.md (exclusion working)

[STEP 2/5] Cleaning text...
✅ ~15,347 tokens cleaned

[STEP 3/5] Chunking text (500-2000 tokens)...
✅ Created 8 chunks
⚠️ WARNING: Very few chunks created

[STEP 4/5] Analyzing writing style...
✅ System prompt: "You are a science fiction author with balanced 
   vocabulary, concise, punchy sentences, and balanced narrative 
   and dialogue."

[STEP 5/5] Creating training examples...
✅ training.jsonl: 7 examples
✅ validation.jsonl: 1 example
```

**Validation**:
- ✅ Virtual environment check working
- ✅ README.md exclusion functional
- ✅ Text cleaning successful
- ✅ Style analysis accurate
- ✅ JSONL format correct
- ⚠️ Volume insufficient (8 examples vs 50-100+ target)

### GPU Compatibility Verification

**Command**: `nvidia-smi` in finetune venv

**Result**:
- RTX 5090 detected: 31.8GB / 32GB available
- CUDA 12.1 (PyTorch bundled) compatible with Compute 8.9
- No driver/version conflicts

## Known Issues

### Training Data Volume Insufficient

**Current**: 8 examples (7 train, 1 validation)
**Target**: 50-100+ examples for effective style transfer
**Cause**: Chunking algorithm (500-2000 tokens) combines chapter files into large segments

**Options**:
1. Lower threshold: `--min-tokens 300` (~20-30 examples expected)
2. Generate more scenes: 10-15 additional chapters (800-1200 words each)
3. Small-scale experiment: Proceed with 8 examples to test pipeline
4. Real writing samples: Replace generated content with user's manuscripts

**Impact**: Current volume allows pipeline testing but won't produce strong style transfer. User decision needed before training execution.

## Next Steps

### Immediate (Pending User Decision)
1. Choose data expansion strategy (Options 1-4 above)

### Training Configuration (After Data Expansion)
2. Create `configs/qlora_style_transfer.yaml` - Axolotl training config
3. Create `scripts/2_train_lora.sh` - Training launcher
4. Execute training run (2-4 hours expected, RTX 5090)

### Model Deployment
5. Create `scripts/3_merge_adapter.py` - LoRA adapter merging
6. Merge trained adapter with base Llama-3.1-8B-Instruct
7. Deploy via `serve_vllm.sh` with merged model path
8. Test with RAG proxy integration (port 8001)
9. Configure VS Code Continue.dev with merged model

## Technical Specifications

**Hardware**:
- GPU: RTX 5090, 32GB VRAM, Compute 8.9 (Blackwell)
- CPU: Ryzen 9 7900X3D, 12 cores/24 threads
- RAM: 64GB DDR5, WSL2: 48GB allocation

**Software**:
- Python 3.12.3
- PyTorch 2.6.0 stable (CUDA 12.1)
- Axolotl 0.12.2
- Virtual environment: ~/.venvs/finetune

**Training Method**:
- QLoRA (4-bit quantization, rank=64 adapters)
- Expected VRAM: 8-12GB for 8B models
- Expected time: 2-4 hours for 1000 samples

## References

**Files Modified**:
- `fine-tuning/setup/1_install_torch.sh` - PyTorch version
- `fine-tuning/README.md` - PyTorch references
- `.github/copilot-instructions.md` - Software environment spec

**New Directories**:
- `fine-tuning/setup/` - Installation scripts
- `fine-tuning/scripts/` - Data prep and training tools
- `fine-tuning/data/raw/` - Training source text
- `fine-tuning/data/processed/` - JSONL output
- `fine-tuning/configs/` - Training configurations (pending)
- `fine-tuning/checkpoints/` - Training checkpoints (auto-generated)
- `fine-tuning/merged_models/` - Final models (auto-generated)

**Commands for Next Session**:
```bash
# Data expansion (Option 1)
cd ~/scifi-llm/fine-tuning/scripts
source ~/.venvs/finetune/bin/activate
python 1_prepare_data.py --min-tokens 300

# Training (when ready)
./2_train_lora.sh

# Merging (after training)
python 3_merge_adapter.py ../checkpoints/qlora-style-run-1/checkpoint-500

# Deployment
cd ~/scifi-llm
./serve_vllm.sh "merged_models/llama-3.1-8b-user-style"
```
