# Fine-Tuning for Style Transfer

Train Llama-3.1-8B-Instruct to match your personal narrative style.

## Quick Start

```bash
# 0. Install training environment (one-time setup)
cd fine-tuning/setup
./0_create_venv.sh
./1_install_torch.sh
./2_install_training_stack.sh

# 1. Activate training environment
source ~/.venvs/finetune/bin/activate

# 2. Add your writing samples
cp ~/my_novel/*.txt data/raw/

# 3. Prepare training data
cd ../scripts
python 1_prepare_data.py --input ../data/raw/ --output ../data/processed/training.jsonl

# 4. Train (QLoRA, ~2-4 hours)
./2_train_lora.sh

# 5. Merge adapter with base model
python 3_merge_adapter.py \
  --checkpoint ../checkpoints/qlora-style-run-1/checkpoint-XXX \
  --output ../merged_models/llama-3.1-8b-your-style

# 6. Test with vLLM
cd ../../
./serve_vllm.sh "fine-tuning/merged_models/llama-3.1-8b-your-style" 8000 9 64000
```

## Directory Structure

```
fine-tuning/
├── FINE_TUNING_SETUP.md           # Complete guide (read this first)
├── README.md                      # This file
├── setup/                         # One-time installation scripts
│   ├── 0_create_venv.sh              # Create ~/.venvs/finetune
│   ├── 1_install_torch.sh            # Install PyTorch 2.8.0
│   └── 2_install_training_stack.sh   # Install Axolotl + dependencies
├── data/
│   ├── raw/                       # Your writing samples (.txt, .md)
│   ├── processed/                 # Converted training data (.jsonl)
│   └── validation/                # Test set for evaluation
├── configs/
│   ├── qlora_style_transfer.yaml  # QLoRA config (recommended)
│   └── lora_style_transfer.yaml   # LoRA config (higher quality)
├── scripts/
│   ├── 1_prepare_data.py          # Convert text → JSONL (TODO)
│   ├── 2_train_lora.sh            # Training launcher
│   ├── 3_merge_adapter.py         # Merge adapter → full model (TODO)
│   └── 4_compare_models.py        # Base vs fine-tuned comparison (TODO)
├── checkpoints/                   # Training checkpoints (auto-generated)
├── merged_models/                 # Final models for vLLM (auto-generated)
└── logs/                          # Training logs (auto-generated)
```

## Installation

### One-Time Setup (Isolated Environment)

Fine-tuning uses a **separate virtual environment** (`~/.venvs/finetune`) to avoid polluting the vLLM server environment.

```bash
cd fine-tuning/setup

# 0. Create virtual environment (~10 seconds)
./0_create_venv.sh

# 1. Install PyTorch 2.8.0 with CUDA 12.8 (2-5 minutes, ~5GB)
./1_install_torch.sh

# 2. Install Axolotl training framework (15-30 minutes, ~10GB)
./2_install_training_stack.sh
```

**Total installation:** ~15GB disk space, 20-35 minutes

**Packages installed:**
- PyTorch 2.8.0 nightly (matches vLLM environment)
- Axolotl (training framework)
- flash-attention (fast kernels)
- DeepSpeed (distributed training)
- transformers, accelerate, peft, bitsandbytes
- wandb, tensorboard (logging)

### Environment Isolation Strategy

| Environment | Location | Purpose | Packages |
|-------------|----------|---------|----------|
| vLLM server | `~/.venvs/llm` | Serving models | vLLM, FlashInfer |
| Fine-tuning | `~/.venvs/finetune` | Training models | Axolotl, DeepSpeed |
| RAG | `~/.venvs/rag` | Retrieval | ChromaDB, sentence-transformers |

**Benefits:**
- Training failures don't break serving
- Can test different package versions
- Easy rollback if issues occur

**To activate for training:**
```bash
source ~/.venvs/finetune/bin/activate
```

## Prerequisites

**Hardware:** RTX 5090 (32GB VRAM) sufficient for 8B models with QLoRA

## Training Methods

### QLoRA (Recommended)
- Memory: ~8-12GB VRAM for 8B models
- Time: ~2-4 hours for 1000 samples
- Quality: Very good for style transfer
- Config: `configs/qlora_style_transfer.yaml`

### LoRA (Higher Quality)
- Memory: ~18-24GB VRAM for 8B models
- Time: ~3-5 hours for 1000 samples
- Quality: Slightly better than QLoRA
- Config: `configs/lora_style_transfer.yaml`

## Data Requirements

**Minimum:** 100 examples of 500-2000 tokens each  
**Recommended:** 500-1000 examples  
**Quality over quantity:** Clean, complete passages

## Integration with RAG

Fine-tuned model + RAG proxy = Your voice + World consistency

```bash
# Start vLLM with fine-tuned model
./serve_vllm.sh "fine-tuning/merged_models/llama-3.1-8b-your-style" 8000 9 64000

# Start RAG proxy (uses vLLM on port 8000)
./serve_rag_proxy.sh scifi_world

# VS Code: Point Continue.dev to http://localhost:8001/v1
```

## Troubleshooting

**Out of memory:**
- Use QLoRA instead of LoRA
- Reduce batch size in config
- Reduce LoRA rank (64 → 32)

**Low quality output:**
- Need more training samples
- Increase LoRA rank (64 → 128)
- Train for more epochs (3 → 5)

**Training loss not decreasing:**
- Increase learning rate (2e-4 → 3e-4)
- Check data quality
- Verify JSONL format

See `FINE_TUNING_SETUP.md` for complete troubleshooting guide.

## Next Steps

1. **Install training environment:** `cd setup && ./0_create_venv.sh && ./1_install_torch.sh && ./2_install_training_stack.sh`
2. **Read complete guide:** `FINE_TUNING_SETUP.md` for detailed workflow
3. **Collect writing samples:** Your prose (500+ tokens each)
4. **Create data prep script:** `scripts/1_prepare_data.py` (converts text → JSONL)
5. **Start training:** Activate `~/.venvs/finetune` and run training
6. **Test merged model:** Use benchmarks and RAG proxy

## Setup Scripts

| Script | Purpose | Duration | Disk Space |
|--------|---------|----------|------------|
| `setup/0_create_venv.sh` | Create `~/.venvs/finetune` | 10s | 50MB |
| `setup/1_install_torch.sh` | PyTorch 2.8.0 + CUDA 12.8 | 2-5 min | ~5GB |
| `setup/2_install_training_stack.sh` | Axolotl + flash-attn + DeepSpeed | 15-30 min | ~10GB |

## Resources

- Setup Guide: `FINE_TUNING_SETUP.md`
- Writing Guide: `../docs/SCIENCE_FICTION_WRITING_GUIDE.md`
- Benchmarks: `../benchmarks/6_style_transfer_quality.py` (TODO)
- RAG Integration: `../RAG/README.md`
