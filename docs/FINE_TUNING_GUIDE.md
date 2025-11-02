# Fine-Tuning Explained: A Complete Guide

## What Is Fine-Tuning?

Fine-tuning is the process of teaching an existing AI model (like Llama-3.1-8B-Instruct) to adopt a specific writing style, domain knowledge, or behavioral pattern. Think of it like teaching a professional writer to write in your personal voice.

**Key concept:** Instead of training a model from scratch (which requires millions of examples and costs hundreds of thousands of dollars), fine-tuning adjusts an already-trained model with a small dataset (10-200+ examples) to specialize its behavior.

---

## Core Components

### 1. Base Model
**What:** The pre-trained language model you start with
**Example:** `meta-llama/Llama-3.1-8B-Instruct`
**Size:** ~16GB (8 billion parameters)
**Capabilities:** Already knows grammar, facts, reasoning, basic writing

### 2. Training Data
**What:** Examples of the behavior you want to teach
**Location:** `fine-tuning/data/processed/training.jsonl`
**Format:** JSONL (JSON Lines - one training example per line)

### 3. Adapter Weights
**What:** The learned adjustments to the base model
**Location:** `fine-tuning/checkpoints/qlora-style-pipeline-test/adapter_model.safetensors`
**Size:** 6.5GB (for rank-64 LoRA)
**Purpose:** Contains the "style transfer" learned from your data

### 4. Checkpoints
**What:** Progress saves during training
**Location:** `fine-tuning/checkpoints/qlora-style-pipeline-test/checkpoint-{N}/`
**Purpose:** Resume training if interrupted, compare different training stages

---

## Training Data Format

### Structure: JSONL (JSON Lines)

Each line in `training.jsonl` is a complete training example:

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a science fiction author with balanced vocabulary, concise, punchy sentences, and balanced narrative and dialogue."
    },
    {
      "role": "user",
      "content": "Continue the scene with character dialogue and interaction."
    },
    {
      "role": "assistant",
      "content": "\"She's not going to believe this.\"\n\n\"Then we'll show her.\" Elena looked at the anomaly..."
    }
  ]
}
```

### Message Roles Explained

| Role | Purpose | Example |
|------|---------|---------|
| **system** | Defines the writing style/persona | "You are a science fiction author with..." |
| **user** | The writing prompt | "Continue the scene with character dialogue..." |
| **assistant** | Your actual chapter text (the "correct answer") | Full chapter excerpt showing your style |

### How the Model Learns

1. **Reads the system message** → Understands the target style
2. **Reads the user prompt** → Knows what task to perform
3. **Compares its output to the assistant message** → Adjusts to match your style
4. **Repeats 1000s of times** → Gradually adopts your writing patterns

### Dataset Size Requirements

| Examples | Expected Quality | Use Case |
|----------|------------------|----------|
| 10-20 | 20-40% style transfer | Proof of concept, testing |
| 50-100 | 40-60% style transfer | Noticeable style adoption |
| 100-200 | 60-80% style transfer | Production quality |
| 500+ | 80-95% style transfer | Professional deployment |

**Current project:** 12 training examples → expect 20-40% style transfer

---

## Checkpoint System

### What Are Checkpoints?

Checkpoints are **save points** created during training. Like saving a video game, they capture the model's state at specific moments so you can:
- Resume training if interrupted
- Compare performance at different stages
- Roll back if later training degrades quality

### Checkpoint Directory Structure

```
checkpoints/qlora-style-pipeline-test/
├── adapter_model.safetensors      # FINAL trained adapter (6.5GB)
├── adapter_config.json            # Configuration for the adapter
├── tokenizer.json                 # Text tokenization rules (17MB)
├── tokenizer_config.json          # Tokenizer settings
├── special_tokens_map.json        # Special tokens (BOS, EOS, PAD, etc.)
├── chat_template.jinja            # Chat formatting template
├── config.json                    # Model configuration
├── checkpoint-2/                  # Save at epoch 0.8
│   ├── adapter_model.safetensors  # Adapter weights at step 2
│   ├── optimizer.pt               # Optimizer state (400MB)
│   ├── scheduler.pt               # Learning rate scheduler state
│   ├── trainer_state.json         # Training metrics
│   └── rng_state.pth              # Random number generator state
├── checkpoint-4/                  # Save at epoch 1.6
└── checkpoint-5/                  # FINAL save at epoch 2.8
```

### Key Files Explained

| File | Size | Purpose | Keep After Training? |
|------|------|---------|---------------------|
| `adapter_model.safetensors` | 6.5GB | **The trained style weights** | ✅ YES - Required for inference |
| `adapter_config.json` | 1KB | Configuration (rank, alpha, target modules) | ✅ YES - Required for inference |
| `tokenizer.json` | 17MB | Converts text ↔ tokens | ✅ YES - Required for inference |
| `optimizer.pt` | 400MB | Training optimizer state | ❌ NO - Only for resuming training |
| `trainer_state.json` | 1KB | Metrics (loss, memory usage, progress) | ⚠️ OPTIONAL - Useful for analysis |
| `rng_state.pth` | 1KB | Reproducibility state | ❌ NO - Only for exact reproduction |

### Checkpoint Naming Convention

- **checkpoint-N**: N is the training step number
- **Step 2** = After processing 2 batches of training data
- **Step 4** = After processing 4 batches of training data
- **Step 5** = Final step (training completed here)

### When Checkpoints Are Created

Checkpoints save automatically based on configuration in `configs/qlora_style_transfer.yaml`:

```yaml
save_strategy: steps
save_steps: 2           # Save every 2 training steps
save_total_limit: 3     # Keep only the 3 most recent checkpoints
```

**Your training:** 5 total steps → checkpoints at step 2, 4, and 5 (final)

---

## Adapter Configuration Deep Dive

### File: `adapter_config.json`

```json
{
  "base_model_name_or_path": "meta-llama/Llama-3.1-8B-Instruct",
  "peft_type": "LORA",
  "r": 64,
  "lora_alpha": 128,
  "lora_dropout": 0.05,
  "target_modules": [
    "q_proj", "k_proj", "v_proj", "o_proj",
    "gate_proj", "up_proj", "down_proj"
  ],
  "modules_to_save": ["embed_tokens", "lm_head"],
  "task_type": "CAUSAL_LM"
}
```

### Critical Parameters

| Parameter | Value | Explanation |
|-----------|-------|-------------|
| `base_model_name_or_path` | Llama-3.1-8B-Instruct | The original model being adapted |
| `peft_type` | LORA | Parameter-Efficient Fine-Tuning method used |
| `r` (rank) | 64 | Number of "style dimensions" to learn (higher = more expressive) |
| `lora_alpha` | 128 | Scaling factor for adapter influence (typically 2x rank) |
| `lora_dropout` | 0.05 | Dropout rate to prevent overfitting (5% of weights dropped) |
| `target_modules` | 7 modules | Which transformer components get adapted |
| `modules_to_save` | embed_tokens, lm_head | Full modules saved (not just adapters) |

### Target Modules Explained

| Module | Purpose in Transformer |
|--------|------------------------|
| `q_proj` | Query projection (attention: what to look for) |
| `k_proj` | Key projection (attention: what's available) |
| `v_proj` | Value projection (attention: what to retrieve) |
| `o_proj` | Output projection (attention: combine results) |
| `gate_proj` | Gating mechanism (feed-forward: what to activate) |
| `up_proj` | Up-projection (feed-forward: expand representation) |
| `down_proj` | Down-projection (feed-forward: compress back) |

**Why these modules?** They control how the model pays attention to context and generates tokens - the core of writing style.

### Rank (r) vs Model Size Trade-off

| Rank | Adapter Size | Style Capacity | VRAM (Training) | Quality |
|------|-------------|----------------|-----------------|---------|
| 8 | ~800MB | Low | 8-10GB | Basic style hints |
| 16 | ~1.6GB | Medium-Low | 9-11GB | Noticeable patterns |
| 32 | ~3.2GB | Medium | 10-12GB | Clear style adoption |
| 64 | **~6.5GB** | **High** | **12-14GB** | **Strong style transfer** |
| 128 | ~13GB | Very High | 16-18GB | Maximum expressiveness |

**Current choice:** Rank 64 balances quality and memory efficiency for RTX 5090 (32GB VRAM)

---

## Training Metrics and Progress

### File: `checkpoint-2/trainer_state.json`

```json
{
  "epoch": 1.0,
  "global_step": 2,
  "total_flos": 1007375351808000.0,
  "train_batch_size": 2,
  "max_steps": 5,
  "log_history": [
    {
      "epoch": 0,
      "eval_loss": 2.217,
      "eval_runtime": 1.37,
      "eval_samples_per_second": 1.455,
      "memory/max_active (GiB)": 13.14,
      "memory/max_allocated (GiB)": 13.14,
      "memory/device_reserved (GiB)": 13.74
    }
  ]
}
```

### Key Metrics Explained

| Metric | Value | What It Means |
|--------|-------|---------------|
| **eval_loss** | 2.217 → 2.137 | How "wrong" the model is (lower = better) |
| **epoch** | 2.8 | How many times training passed through full dataset |
| **global_step** | 2 → 5 | Total training batches processed |
| **memory/max_active** | 13.14 GB | Peak VRAM used during evaluation |
| **train_runtime** | 103 seconds | Total training time |
| **train_loss** | 2.137 | Final training loss |

### Understanding Loss Values

| Loss Range | Interpretation |
|------------|----------------|
| **3.0+** | Model is confused, outputs random/incoherent text |
| **2.0-2.5** | Model is learning patterns, starting to match style |
| **1.5-2.0** | Good style adoption, coherent outputs |
| **1.0-1.5** | Excellent style match, production quality |
| **< 1.0** | Risk of overfitting (memorizing instead of learning) |

**Your final loss (2.137):** Model learned patterns but dataset was small. Expected for 12 training examples.

### Memory Usage Breakdown

| Component | VRAM Usage |
|-----------|------------|
| Base model (4-bit quantized) | ~5GB |
| Adapter weights (rank 64) | ~6.5GB |
| Gradients and optimizer states | ~3-4GB |
| Activation memory | ~2-3GB |
| **Total peak** | **17.49 GB** |
| **Typical training** | **9-10 GB** |

**Why the difference?** Peak occurs during model loading and first forward pass. Training stabilizes lower.

---

## QLoRA Training Method

### What is QLoRA?

**QLoRA** = Quantized Low-Rank Adaptation

Combines two techniques:
1. **4-bit Quantization**: Compress base model from 16GB → ~5GB
2. **LoRA**: Train small adapter weights instead of full model

### Memory Comparison

| Method | Base Model Size | Training VRAM | Adapter Size |
|--------|----------------|---------------|--------------|
| Full Fine-Tuning | 16GB (bfloat16) | 40-60GB | 16GB |
| LoRA | 16GB (bfloat16) | 24-32GB | 6.5GB |
| **QLoRA** | **5GB (4-bit NF4)** | **9-14GB** | **6.5GB** |

**Benefit:** Fits 8B model training on consumer GPU (RTX 5090 with 32GB VRAM)

### 4-bit NF4 Quantization

**NF4** = NormalFloat4 - a 4-bit data type optimized for neural network weights

```
Original (bfloat16): 16 bits per parameter → 8B params × 16 bits = 16GB
Quantized (NF4): 4 bits per parameter → 8B params × 4 bits = 4GB (~5GB with overhead)
```

**Quality impact:** Minimal loss for inference, ~2-3% degradation in fine-tuning quality

### LoRA Adapters

Instead of modifying all 8 billion parameters, LoRA:
1. Freezes the base model weights
2. Adds small "adapter" matrices to specific layers
3. Trains only the adapters (64 dimensions per layer)

**Math:**
```
Original weight matrix: W (4096 × 4096) = 16M parameters
LoRA adapter: A (4096 × 64) + B (64 × 4096) = 524K parameters
Compression: 30x fewer parameters to train!
```

### Training Configuration

From `configs/qlora_style_transfer.yaml`:

```yaml
load_in_4bit: true          # Enable 4-bit quantization
adapter: qlora              # Use QLoRA method
lora_r: 64                  # Rank (style dimensions)
lora_alpha: 128             # Scaling factor
lora_dropout: 0.05          # Prevent overfitting
lora_target_modules:        # Which layers to adapt
  - q_proj
  - k_proj
  - v_proj
  - o_proj
  - gate_proj
  - up_proj
  - down_proj
```

---

## Training Pipeline Workflow

### Overview

```
Raw Chapters → Data Preparation → Training → Checkpoints → Merged Model → vLLM Deployment
```

### Step-by-Step Process

#### 1. Data Preparation (`training/1_prepare_data.py`)

**Input:** Raw chapter text files (`data/raw/chapter_*.txt`)

**Process:**
- Reads each chapter
- Chunks into conversation-sized segments
- Formats as JSONL with system/user/assistant messages
- Splits into training (85%) and validation (15%)

**Output:**
- `data/processed/training.jsonl` (12 examples)
- `data/processed/validation.jsonl` (2 examples)

**Example transformation:**

```
INPUT (chapter_01_bridge_crisis.txt):
"She's not going to believe this."
"Then we'll show her." Elena looked at the anomaly...

OUTPUT (training.jsonl):
{
  "messages": [
    {"role": "system", "content": "You are a science fiction author..."},
    {"role": "user", "content": "Continue the scene..."},
    {"role": "assistant", "content": "\"She's not going to believe this...\""}
  ]
}
```

#### 2. Training (`training/2_train_lora.sh`)

**Command:**
```bash
accelerate launch -m axolotl.cli.train configs/qlora_style_transfer.yaml
```

**Process:**
1. Load base model in 4-bit (Llama-3.1-8B-Instruct)
2. Initialize LoRA adapters (rank 64)
3. Load training data (12 examples)
4. Train for 5 steps (2.8 epochs)
5. Save checkpoints every 2 steps
6. Evaluate on validation data

**Duration:** ~103 seconds (1.7 minutes) for 12 examples

**Output:**
- `checkpoints/qlora-style-pipeline-test/checkpoint-{2,4,5}/`
- `logs/training_*.log`

#### 3. Checkpoint Selection

**Automatic:** Final checkpoint (`checkpoint-5`) used by default

**Manual comparison:**
```bash
# Compare loss values across checkpoints
cat checkpoints/*/trainer_state.json | grep eval_loss

# Or use tensorboard (if logging enabled)
tensorboard --logdir checkpoints/
```

#### 4. Adapter Merging (`training/3_merge_adapters.sh`)

**Purpose:** Combine base model + adapter → single deployable model

**Process:**
- Load base model (Llama-3.1-8B-Instruct)
- Load adapter weights (`adapter_model.safetensors`)
- Merge adapter into base model weights
- Save merged model in bfloat16 format

**Output:** `merged_models/qlora-style-{timestamp}/` (~16GB)

#### 5. vLLM Deployment

**Command:**
```bash
./serve_vllm.sh "merged_models/qlora-style-20251102/Llama-3.1-8B-Instruct"
```

**Result:** API server on port 8000 serving your style-adapted model

---

## File Structure Reference

```
fine-tuning/
├── data/
│   ├── raw/                          # Original chapter files
│   │   ├── chapter_01_bridge_crisis.txt
│   │   ├── chapter_02_medical_bay.txt
│   │   └── ... (17 chapters total)
│   ├── processed/                    # Training data (auto-generated)
│   │   ├── training.jsonl            # 12 training examples
│   │   └── validation.jsonl          # 2 validation examples
│   └── validation/                   # (Future: hold-out test set)
│
├── configs/
│   ├── qlora_style_transfer.yaml     # QLoRA training config
│   └── lora_style_transfer.yaml      # Full LoRA config (higher VRAM)
│
├── training/
│   ├── 1_prepare_data.py             # Convert chapters → JSONL
│   ├── 2_train_lora.sh               # Run training
│   └── 3_merge_adapters.sh           # Merge adapter + base model
│
├── checkpoints/                      # Training progress saves
│   └── qlora-style-pipeline-test/
│       ├── adapter_model.safetensors # FINAL adapter (6.5GB) ✅
│       ├── adapter_config.json       # Configuration ✅
│       ├── tokenizer.json            # Tokenization rules ✅
│       ├── checkpoint-2/             # Epoch 0.8 save
│       ├── checkpoint-4/             # Epoch 1.6 save
│       └── checkpoint-5/             # Epoch 2.8 FINAL save
│
├── merged_models/                    # Deployed models (auto-generated)
│   └── qlora-style-{timestamp}/      # Base + adapter merged (~16GB)
│
├── logs/                             # Training logs (auto-generated)
│   └── training_20251102-230852.log  # Full training output
│
└── monitor_training.sh               # Real-time training monitor
```

---

## Common Questions

### Q: Why is the adapter 6.5GB for only 12 training examples?

**A:** Adapter size depends on **rank** and **model architecture**, not dataset size.

```
Rank 64 × 7 target modules × ~150 transformer layers × parameter size = ~6.5GB
```

More training data improves **quality**, not adapter size.

### Q: What's the difference between checkpoints and the final adapter?

**A:** The final adapter **is** checkpoint-5. The top-level `adapter_model.safetensors` is a copy of `checkpoint-5/adapter_model.safetensors` for convenience.

### Q: Can I use the adapter directly without merging?

**A:** Yes! vLLM supports loading adapters separately:

```bash
vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --enable-lora \
  --lora-modules style=checkpoints/qlora-style-pipeline-test
```

**Benefit:** Can load multiple adapters and swap between them dynamically.

### Q: How do I improve style transfer quality?

**A:** Three approaches:

1. **More training data** (50-200+ examples)
2. **Higher rank** (64 → 128, requires more VRAM)
3. **Better data quality** (clean, consistent style in source material)

### Q: What if training loss stops decreasing?

**A:** Possible causes:

- **Overfitting:** Model memorized examples (add more data or increase dropout)
- **Learning rate too low:** Training stuck (increase learning rate)
- **Dataset too small:** 12 examples hit quality ceiling (add more data)
- **Convergence:** Model learned all it can from data (expected)

### Q: How do I resume training from a checkpoint?

**A:** Update `configs/qlora_style_transfer.yaml`:

```yaml
resume_from_checkpoint: checkpoints/qlora-style-pipeline-test/checkpoint-5
num_epochs: 5  # Train for 5 MORE epochs
```

Then run `./training/2_train_lora.sh` again.

### Q: Can I fine-tune a different base model?

**A:** Yes! Edit `configs/qlora_style_transfer.yaml`:

```yaml
base_model: Qwen/Qwen2.5-7B-Instruct  # Or any HuggingFace model
```

Ensure the model supports the architecture (most decoder-only LLMs work).

---

## Performance Expectations

### Training Speed

| GPU | 8B Model (QLoRA) | Training Time (12 examples, 5 steps) |
|-----|------------------|-------------------------------------|
| RTX 4090 (24GB) | ~2-3 min | Fits comfortably |
| RTX 5090 (32GB) | **~1.7 min** | Plenty of headroom |
| A100 (40GB) | ~1.5 min | Overkill for this size |

### Style Transfer Quality

| Dataset Size | Expected Transfer | Loss Range | Production Ready? |
|--------------|------------------|------------|-------------------|
| 10-20 examples | 20-40% | 2.0-2.5 | ❌ Proof of concept only |
| 50-100 examples | 40-60% | 1.5-2.0 | ⚠️ Noticeable but inconsistent |
| 100-200 examples | 60-80% | 1.2-1.8 | ✅ Production quality |
| 500+ examples | 80-95% | 1.0-1.5 | ✅ Professional deployment |

**Your current training:** 12 examples → 20-40% transfer → **suitable for testing, not production**

### Next Steps for Production Quality

1. **Gather more training data:**
   - Re-chunk chapters into smaller segments (500-1000 tokens each)
   - Target: 100-200 training examples
   - Maintain consistent style across all examples

2. **Re-run training:**
   ```bash
   cd fine-tuning
   ./training/1_prepare_data.py --chunk-size 800 --overlap 100
   ./training/2_train_lora.sh
   ```

3. **Benchmark quality:**
   ```bash
   cd benchmarks
   python 1_voice_comparison.py  # Compare baseline vs fine-tuned
   ```

4. **Iterate:**
   - Review outputs
   - Identify style gaps
   - Add targeted training examples
   - Re-train until transfer reaches 60-80%

---

## Troubleshooting

### Out of Memory (OOM) Errors

**Symptoms:** Training crashes with CUDA OOM

**Solutions:**
1. Reduce `micro_batch_size` in config (2 → 1)
2. Enable gradient checkpointing (already enabled in QLoRA config)
3. Reduce rank (64 → 32)
4. Use smaller base model (8B → 7B)

### Training Loss Not Decreasing

**Symptoms:** Loss stays flat or increases

**Solutions:**
1. Increase learning rate (1e-4 → 5e-4)
2. Check data quality (ensure examples are correctly formatted)
3. Reduce regularization (lora_dropout: 0.05 → 0.0)
4. Train longer (5 steps → 10 steps)

### Poor Style Transfer After Training

**Symptoms:** Model doesn't write in your style

**Solutions:**
1. **Most common:** Add more training data (12 → 100+)
2. Increase rank (64 → 128)
3. Increase lora_alpha (128 → 256)
4. Verify data quality (check examples match desired style)
5. Train longer (5 epochs → 10 epochs)

### Checkpoints Not Saving

**Symptoms:** No checkpoint directories created

**Solutions:**
1. Check `save_steps` in config (should be > 0)
2. Verify output directory permissions
3. Ensure enough disk space (~20GB per checkpoint)
4. Check logs for write errors

---

## Best Practices

### Data Preparation
- ✅ Use consistent formatting across all examples
- ✅ Include diverse scenarios (dialogue, narration, description)
- ✅ Maintain 85/15 train/validation split
- ✅ Remove any formatting artifacts (markdown, HTML, etc.)
- ❌ Don't include extremely short or long examples (500-2000 tokens ideal)
- ❌ Don't mix different writing styles in training set

### Training Configuration
- ✅ Start with proven configs (QLoRA defaults)
- ✅ Use gradient checkpointing for memory efficiency
- ✅ Enable bf16 for RTX 5090 (faster than fp16)
- ✅ Save checkpoints frequently (every 2-5 steps)
- ❌ Don't train to zero loss (indicates overfitting)
- ❌ Don't use huge batch sizes (2-4 is optimal for small datasets)

### Checkpoint Management
- ✅ Keep final checkpoint + 1-2 intermediate saves
- ✅ Document which checkpoint produced best results
- ✅ Delete optimizer.pt files after training completes
- ❌ Don't delete checkpoints until merged model is validated
- ❌ Don't store unnecessary intermediate checkpoints (disk space)

### Deployment
- ✅ Test merged model with benchmark suite before production
- ✅ Use adapter-only loading for multi-style serving
- ✅ Monitor quality with automated benchmarks
- ❌ Don't deploy without human evaluation of outputs
- ❌ Don't assume more training = better quality (diminishing returns)

---

## Additional Resources

- **QLoRA Paper:** https://arxiv.org/abs/2305.14314
- **LoRA Paper:** https://arxiv.org/abs/2106.09685
- **Axolotl Documentation:** https://github.com/OpenAccess-AI-Collective/axolotl
- **PEFT Library:** https://github.com/huggingface/peft
- **vLLM Adapter Guide:** https://docs.vllm.ai/en/latest/models/lora.html

---

## Quick Reference Commands

```bash
# Prepare training data
cd fine-tuning
./training/1_prepare_data.py

# Start training
./training/2_train_lora.sh

# Monitor training (in separate terminal)
./monitor_training.sh

# Merge adapter with base model
./training/3_merge_adapters.sh

# Test merged model
cd ../vllm
./serve_vllm.sh "fine-tuning/merged_models/qlora-style-{timestamp}"

# Benchmark quality
cd fine-tuning/benchmarks
python 1_voice_comparison.py
```

---

**Last Updated:** 2025-11-02  
**Project:** scifi-llm fine-tuning pipeline  
**Training Result:** 12 examples, 2.8 epochs, loss 2.137, 20-40% style transfer
