# Fine-Tuning Setup Guide

**Purpose:** Train Llama-3.1-8B-Instruct to match your personal narrative style  
**Method:** QLoRA (Quantized Low-Rank Adaptation) for memory efficiency  
**Hardware:** RTX 5090 (32GB VRAM) - sufficient for 7-14B models

---

## Overview

Fine-tuning captures your **writing style** (voice, pacing, word choice, sentence structure) while RAG maintains **worldbuilding consistency** (characters, plot, lore). Combined approach:
- Base model → Your narrative voice
- RAG system → Accurate character/world details
- Result: Fiction that sounds like you with perfect continuity

---

## Quick Start

```bash
# 1. Prepare your writing samples
cd fine-tuning
python training/1_prepare_data.py --input data/raw/ --output data/processed/

# 2. Train with QLoRA (memory efficient)
./training/2_train_lora.sh

# 3. Merge adapter with base model
python training/3_merge_adapter.py --checkpoint checkpoints/final/ --output merged_models/llama-3.1-8b-your-style

# 4. Test with vLLM
cd ..
./serve_vllm.sh "fine-tuning/merged_models/llama-3.1-8b-your-style" 8000 9 64000

# 5. Compare quality
cd benchmarks
python 6_style_transfer_quality.py
```

---

## Training Approaches

### QLoRA (Recommended)
**Pros:**
- Memory efficient (~8-12GB VRAM for 8B models)
- Fast training (2-4 hours for 1000 samples)
- Good quality retention
- Easy to merge with base model

**Cons:**
- Slightly lower quality than full fine-tuning
- Requires quantization step

**When to use:** Always start here. Fits comfortably on RTX 5090.

### LoRA (Alternative)
**Pros:**
- Better quality than QLoRA
- Faster inference after merging
- No quantization artifacts

**Cons:**
- Higher VRAM (~16-20GB for 8B models)
- Longer training time

**When to use:** If QLoRA quality insufficient and you have VRAM headroom.

### Full Fine-Tuning (Not Recommended)
**Cons:**
- Requires 40GB+ VRAM for 8B models
- Risk of catastrophic forgetting
- Much longer training

**When to use:** Only with multi-GPU setup or smaller models (<3B).

---

## Data Preparation

### Minimum Requirements
- **Samples:** 100-1000 examples (more = better style capture)
- **Length:** 500-2000 tokens per example
- **Quality:** Complete narrative passages (not fragments)
- **Diversity:** Different scenes, tones, characters

### What to Include
✅ **Narrative prose** - Your descriptive writing  
✅ **Character introspection** - Internal thoughts, emotions  
✅ **Scene descriptions** - Settings, atmosphere  
✅ **Action sequences** - Your pacing style  
✅ **Dialogue with attribution** - "Elena said" patterns  

❌ **Avoid:**
- Dialogue-only excerpts (loses narrative voice)
- Incomplete sentences/fragments
- Editing notes or metadata
- Extremely short samples (<200 tokens)

### Training Format (JSONL)

```jsonl
{"messages": [{"role": "system", "content": "You are a science fiction author writing in a technical, atmospheric style."}, {"role": "user", "content": "Write a scene where Elena enters the bridge during a crisis."}, {"role": "assistant", "content": "The bridge doors hissed open. Elena stepped through, her cybernetic arm reflecting the crimson emergency lighting..."}]}
{"messages": [{"role": "system", "content": "You are a science fiction author writing in a technical, atmospheric style."}, {"role": "user", "content": "Describe the Arcturian homeworld at sunset."}, {"role": "assistant", "content": "Three moons rose over Karantha's violet sky. The floating cities cast long shadows across the gravity-well generators below..."}]}
```

**Key points:**
- One JSON object per line (not pretty-printed)
- System prompt establishes your writing style descriptor
- User prompt provides scene/context
- Assistant response is YOUR actual writing

---

## Workflow Steps

### Step 1: Organize Your Writing Samples

```bash
fine-tuning/data/raw/
├── novel_chapter_01.txt
├── novel_chapter_02.txt
├── short_story_alpha.txt
└── scene_fragments.txt
```

**Criteria:**
- Plain text format (`.txt` or `.md`)
- UTF-8 encoding
- Remove author notes, TODOs, editing comments
- Keep paragraph breaks natural

### Step 2: Convert to Training Format

**Script:** `training/1_prepare_data.py`

```bash
python training/1_prepare_data.py \
  --input data/raw/ \
  --output data/processed/training.jsonl \
  --min-tokens 500 \
  --max-tokens 2000 \
  --split 0.9
```

**What it does:**
- Chunks text into examples (500-2000 tokens)
- Generates system/user/assistant format
- Creates train/validation split (90/10)
- Outputs: `training.jsonl`, `validation.jsonl`

**System prompt generation:**
The script analyzes your writing to create descriptive prompts:
- Vocabulary complexity level
- Sentence structure patterns (simple/complex/varied)
- Typical paragraph length
- Dialogue vs narrative ratio

### Step 3: Configure Training Parameters

**File:** `configs/qlora_style_transfer.yaml`

```yaml
# Model
base_model: meta-llama/Llama-3.1-8B-Instruct
model_type: LlamaForCausalLM

# QLoRA Configuration
load_in_4bit: true
bnb_4bit_quant_type: nf4
bnb_4bit_compute_dtype: bfloat16

# LoRA Parameters
lora_r: 64              # Rank (higher = more capacity, more VRAM)
lora_alpha: 128         # Scaling factor (typically 2x rank)
lora_dropout: 0.05
lora_target_modules:
  - q_proj
  - k_proj
  - v_proj
  - o_proj
  - gate_proj
  - up_proj
  - down_proj

# Training Parameters
learning_rate: 2e-4     # Higher for style transfer than factual learning
num_epochs: 3           # Typically 2-4 for style
per_device_batch_size: 4
gradient_accumulation_steps: 4  # Effective batch = 16
warmup_steps: 100
max_seq_length: 2048

# Optimization
optimizer: paged_adamw_8bit
lr_scheduler_type: cosine
weight_decay: 0.01
gradient_checkpointing: true

# Output
output_dir: checkpoints/qlora-style-run-1
save_steps: 100
logging_steps: 10
```

**Key Parameters Explained:**

**lora_r (Rank):**
- 32: Minimal, fast, less style capture
- 64: **Recommended** - Good balance
- 128: Maximum style capture, slower, more VRAM

**learning_rate:**
- 1e-4: Conservative (safer, may need more epochs)
- 2e-4: **Recommended** for style transfer
- 5e-4: Aggressive (risk of overfitting)

**num_epochs:**
- 2: Minimum for noticeable style
- 3: **Recommended** starting point
- 5+: Risk of overfitting (model memorizes training data)

### Step 4: Launch Training

**Script:** `training/2_train_lora.sh`

```bash
#!/bin/bash
set -euo pipefail

# Activate vLLM environment (has PyTorch, CUDA)
source ~/.venvs/llm/bin/activate

# Set efficient training flags
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export WANDB_DISABLED=true  # Disable if not using Weights & Biases

# Launch training
python -m axolotl.cli.train configs/qlora_style_transfer.yaml

echo "[DONE] Training complete. Checkpoints in checkpoints/qlora-style-run-1"
```

**Expected output:**
```
[INFO] Loading base model: meta-llama/Llama-3.1-8B-Instruct
[INFO] Applying QLoRA (rank=64)
[INFO] Training samples: 900 | Validation: 100
[INFO] Starting training...

Epoch 1/3: 100%|████████| 225/225 [1:24:12<00:00, train_loss=1.23]
Validation: perplexity=12.4

Epoch 2/3: 100%|████████| 225/225 [1:23:58<00:00, train_loss=0.87]
Validation: perplexity=9.8

Epoch 3/3: 100%|████████| 225/225 [1:24:05<00:00, train_loss=0.71]
Validation: perplexity=8.2

[DONE] Best checkpoint: checkpoints/qlora-style-run-1/checkpoint-675
```

**Training time estimates (RTX 5090):**
- 100 samples: ~30 minutes
- 500 samples: ~2 hours
- 1000 samples: ~4 hours

### Step 5: Merge Adapter with Base Model

**Why merge?**
- vLLM requires full models (doesn't support adapter loading)
- Faster inference than adapter-on-the-fly
- Easier distribution/deployment

**Script:** `training/3_merge_adapter.py`

```bash
python training/3_merge_adapter.py \
  --base-model meta-llama/Llama-3.1-8B-Instruct \
  --adapter checkpoints/qlora-style-run-1/checkpoint-675 \
  --output merged_models/llama-3.1-8b-your-style
```

**What it does:**
- Loads base model weights
- Applies LoRA adapter weights
- Saves merged model in vLLM-compatible format
- Includes tokenizer and config

**Output:**
```
merged_models/llama-3.1-8b-your-style/
├── config.json
├── generation_config.json
├── model-00001-of-00004.safetensors
├── model-00002-of-00004.safetensors
├── model-00003-of-00004.safetensors
├── model-00004-of-00004.safetensors
├── model.safetensors.index.json
├── special_tokens_map.json
├── tokenizer.json
└── tokenizer_config.json
```

### Step 6: Test with vLLM

```bash
# Start server with fine-tuned model
./serve_vllm.sh "fine-tuning/merged_models/llama-3.1-8b-your-style" 8000 9 64000

# Test with simple query
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "fine-tuning/merged_models/llama-3.1-8b-your-style",
    "messages": [{"role": "user", "content": "Write a scene where Elena checks the ship sensors."}],
    "max_tokens": 500,
    "temperature": 0.9
  }'
```

### Step 7: Quality Comparison

**Benchmark:** `benchmarks/6_style_transfer_quality.py`

```bash
cd benchmarks

# Test base model
./serve_vllm.sh  # Default Llama-3.1-8B
python 6_style_transfer_quality.py --model base --output results/style_base.json

# Test fine-tuned model
./serve_vllm.sh "fine-tuning/merged_models/llama-3.1-8b-your-style"
python 6_style_transfer_quality.py --model finetuned --output results/style_finetuned.json

# Compare
python 6_style_transfer_quality.py --compare results/style_base.json results/style_finetuned.json
```

**Metrics evaluated:**
- **Vocabulary match:** Percentage of your frequent words/phrases used
- **Sentence length distribution:** Matches your typical patterns
- **Paragraph structure:** Description vs dialogue ratio
- **Pacing markers:** Action verbs, transition phrases
- **Overall style score:** 0-100 (aim for 75+)

---

## Quality Validation

### Before/After Comparison

**Prompt:** "Write a tense scene where Elena discovers an anomaly on the ship's sensors."

**Base Model (Llama-3.1-8B-Instruct):**
> Elena rushed to the bridge. "What's wrong?" she asked.
> 
> Marcus pointed at the screen. "There's something out there."
> 
> She looked at the readings carefully. Her heart raced as she realized what it meant.

**Style:** Generic, dialogue-heavy, lacks atmospheric detail.

**Fine-Tuned Model (Your Style):**
> The bridge doors hissed open before Elena reached them. Marcus stood at the sensor array, his shoulders rigid.
> 
> "Show me." She crossed the deck in four strides, her cybernetic arm already reaching for the console controls.
> 
> The holographic display flickered to life. Radiation signatures danced across the quantum foam—patterns that shouldn't exist this far from any stellar body. Her pulse quickened. She'd seen readings like this once before. On Phobos.

**Style:** Atmospheric, technical details, internal reactions, character-specific details (cybernetic arm, Phobos reference).

### Success Indicators

✅ **Natural vocabulary:** Uses your specific word choices  
✅ **Consistent pacing:** Matches your paragraph rhythm  
✅ **Authentic voice:** Sounds like you wrote it  
✅ **Character awareness:** Incorporates established details  
✅ **Technical balance:** Right level of sci-fi terminology  

❌ **Warning signs:**
- Reverts to generic language
- Loses your sentence structure patterns
- Ignores established character traits
- Too formal or too casual vs your baseline

---

## Integration with RAG System

### Combined Workflow

```bash
# Terminal 1: Start vLLM with fine-tuned model
./serve_vllm.sh "fine-tuning/merged_models/llama-3.1-8b-your-style" 8000 9 64000

# Terminal 2: Start RAG proxy (automatically uses port 8000 vLLM)
./serve_rag_proxy.sh scifi_world

# VS Code: Configure Continue.dev
# URL: http://localhost:8001/v1 (RAG proxy on fine-tuned model)
```

**What you get:**
1. **Your narrative voice** from fine-tuning
2. **World consistency** from RAG retrieval
3. **Transparent operation** - RAG injects context automatically

**VS Code config** (`~/.continue/config.json`):
```json
{
  "models": [{
    "title": "Your Style + RAG",
    "provider": "openai",
    "model": "fine-tuning/merged_models/llama-3.1-8b-your-style",
    "apiBase": "http://localhost:8001/v1",
    "apiKey": "EMPTY",
    "contextLength": 64000,
    "completionOptions": {
      "temperature": 0.85,
      "maxTokens": 2000
    }
  }]
}
```

### Example: Fine-Tuned + RAG in Action

**Your request in VS Code:**
> Continue the story. Elena enters the stellar bar after a difficult shift.

**What happens:**
1. RAG retrieves: Elena's character profile, cybernetic arm, Phobos trauma
2. Fine-tuned model generates in YOUR style
3. Output maintains character consistency AND your voice

**Generated text:**
> Elena pushed through the stellar bar's double doors, letting them swing shut behind her. The low rumble of conversation barely registered. She found an empty booth in the back—the kind where shadows pooled thick enough to discourage company.
> 
> Her cybernetic arm caught the dim lighting as she signaled the server. Metal and flesh, forever joined by a decision she'd made in three seconds on the Phobos station. The arm worked flawlessly. It was the memories that malfunctioned.

**Analysis:**
- ✅ **Style:** Your pacing, paragraph structure, introspection depth
- ✅ **Consistency:** Cybernetic arm retrieved from RAG
- ✅ **Voice:** Technical details balanced with emotion (your pattern)
- ✅ **Character:** Phobos trauma (RAG) + solitary behavior (your style)

---

## Troubleshooting

### Training Issues

**Out of memory during training:**
```bash
# Reduce batch size in config
per_device_batch_size: 2  # Was 4
gradient_accumulation_steps: 8  # Was 4 (keeps effective batch = 16)

# Or reduce LoRA rank
lora_r: 32  # Was 64
lora_alpha: 64  # Was 128
```

**Training loss not decreasing:**
- Increase learning rate: `3e-4` instead of `2e-4`
- Check data quality: Remove duplicates, ensure variety
- Increase epochs: Try 5 instead of 3
- Verify data format: Validate JSONL structure

**Model outputs gibberish after training:**
- Learning rate too high (reduce to `1e-4`)
- Too many epochs (overfitting - use earlier checkpoint)
- Bad training data (check for encoding issues)

### Merging Issues

**vLLM can't load merged model:**
```bash
# Verify safetensors format
ls merged_models/llama-3.1-8b-your-style/*.safetensors

# Check config exists
cat merged_models/llama-3.1-8b-your-style/config.json

# Test load without vLLM
python training/test_model_load.py --model merged_models/llama-3.1-8b-your-style
```

**Model size larger than expected:**
- Merged model should be ~16GB (same as base)
- If 32GB+: Merge created duplicate layers (re-run merge)
- Check: `du -sh merged_models/llama-3.1-8b-your-style`

### Quality Issues

**Fine-tuned model lost capabilities:**
- Learning rate too high (catastrophic forgetting)
- Too many epochs on small dataset
- Solution: Use earlier checkpoint or retrain with `lr=1e-4`

**Style not captured:**
- Not enough training samples (need 300+ minimum)
- Samples too short (<500 tokens)
- LoRA rank too low (increase to 128)
- Learning rate too low (increase to `3e-4`)

**Style inconsistent:**
- Training data too diverse (different authors mixed in)
- Need validation split to catch overfitting
- Try longer training with lower learning rate

---

## Hardware Requirements

### RTX 5090 (32GB VRAM)

**QLoRA Training:**
- 7B models: ~8-12GB VRAM ✅
- 8B models: ~10-14GB VRAM ✅
- 14B models: ~18-22GB VRAM ✅
- 30B+ models: OOM ❌

**LoRA Training (no quantization):**
- 7B models: ~16-20GB VRAM ✅
- 8B models: ~18-24GB VRAM ✅
- 14B models: ~28-32GB VRAM ⚠️ (tight fit)

**Inference (merged model):**
- Same as base model requirements
- 8B: ~16GB VRAM
- 14B: ~28GB VRAM

### Performance Expectations

**Training speed (8B model, RTX 5090):**
- QLoRA: ~40-50 tokens/sec
- LoRA: ~60-80 tokens/sec
- Batch size 4, sequence length 2048

**Time estimates:**
- 500 samples × 3 epochs = ~2 hours (QLoRA)
- 1000 samples × 3 epochs = ~4 hours (QLoRA)

---

## Tools Comparison

### Axolotl (Recommended)
**Pros:**
- One config file for everything
- Excellent QLoRA support
- Great documentation
- Active community

**Install:**
```bash
source ~/.venvs/llm/bin/activate
pip install axolotl[flash-attn,deepspeed]
```

### Unsloth
**Pros:**
- Fastest training speed (2-4x faster)
- Easy setup
- Good for experimentation

**Cons:**
- Less configuration control
- Fewer advanced features

### HuggingFace PEFT
**Pros:**
- Official library
- Maximum flexibility
- Best documentation

**Cons:**
- More boilerplate code
- Steeper learning curve

### LLaMA-Factory
**Pros:**
- Web UI for training
- No code required
- Good for beginners

**Cons:**
- Less control
- Not optimized for 5090

---

## Best Practices

### Dataset Preparation
1. **Quality over quantity:** 300 good examples > 1000 mediocre ones
2. **Clean data:** Remove metadata, TODOs, incomplete sentences
3. **Diverse samples:** Different scenes, tones, narrative modes
4. **Natural chunks:** Don't split mid-scene or mid-paragraph
5. **Validation set:** Hold out 10% to detect overfitting

### Training Strategy
1. **Start conservative:** Low learning rate, few epochs
2. **Monitor validation:** Loss should decrease consistently
3. **Save checkpoints:** Every 100 steps (can revert if quality drops)
4. **Test early:** Generate samples after epoch 1 to check progress
5. **Compare often:** Benchmark against base model regularly

### Model Management
1. **Version checkpoints:** Name by date/iteration (`run-20251024-v1`)
2. **Track hyperparameters:** Save config with each checkpoint
3. **Document changes:** Note what worked/failed in training log
4. **Keep base model:** Don't delete - needed for future merges
5. **Backup merged models:** Training takes hours, protect the output

---

## Next Steps

1. **Collect writing samples:** Gather 500-1000 tokens × 100+ examples
2. **Install training tools:** Set up Axolotl in vLLM environment
3. **Prepare data:** Run `1_prepare_data.py` on your samples
4. **Train QLoRA:** Start with default config, 3 epochs
5. **Merge adapter:** Create full model for vLLM
6. **Test quality:** Run `6_style_transfer_quality.py` benchmark
7. **Iterate:** Adjust hyperparameters based on results
8. **Deploy:** Use with RAG proxy for writing workflow

---

## Resources

**Documentation:**
- Axolotl: https://github.com/OpenAccess-AI-Collective/axolotl
- QLoRA paper: https://arxiv.org/abs/2305.14314
- PEFT library: https://huggingface.co/docs/peft

**Community:**
- r/LocalLLaMA - Training tips and troubleshooting
- Axolotl Discord - Active support channel
- HuggingFace forums - PEFT/LoRA discussions

**Guides:**
- "Fine-tuning LLaMA for Creative Writing" (community guide)
- "QLoRA on Consumer GPUs" (optimization tips)
- "Style Transfer vs Instruction Tuning" (methodology comparison)
