# Context for Fine-Tuning Session

## Current System State

**Hardware:** RTX 5090 (32GB VRAM)  
**OS:** Linux (bash shell)  
**Working Directory:** `/home/ruifrvaz/scifi-llm`

**Virtual Environments:**
- vLLM: `~/.venvs/llm` (Python 3.12.3, PyTorch 2.8.0, vLLM 0.10.2, FlashInfer 0.3.0)
- RAG: `~/.venvs/rag` (separate isolation)

**Current vLLM Server:**
- Model: meta-llama/Llama-3.1-8B-Instruct
- Context: 64k tokens
- Port: 8000
- Performance: ~32-35 tok/s average

**RAG System:**
- Collection: `scifi_world` (4 chunks from example_vllm_reference.md)
- Embedding: bge-large-en-v1.5
- Proxy: Port 8001 (when running)

## Recent Accomplishments

### Documentation Accuracy ✅
- Corrected all 128k context claims → 100k max (RTX 5090 hardware limit)
- Updated performance benchmarks across all guides
- Context window impact documented: 32k=fastest, 64k=balanced, 100k=slow

### Benchmarks Validated ✅
**vLLM (all passing):**
1. Throughput: 34.2 tok/s average
2. Context scaling: 32 tok/s @ 1k → 6 tok/s @ 60k
3. Creative quality: 76.6/100 overall, 100% completion rate
4. Long context coherence: 100% character consistency across 4k tokens

**RAG (all passing):**
5. Retrieval quality: Average distance 0.96, 4 chunks
6. Full pipeline: Elena query 774+338 tokens, perfect retrieval

### RAG Monitoring Enhanced ✅
- Added query history tracking to `serve_rag_proxy.py`
- Created `/stats` endpoint (recent_queries, total_queries, chunks_available)
- Updated `monitor_rag_proxy.sh` to display actual query history

### Character Consistency Validated ✅
- Tested RAG with Elena bar scene generation
- Correctly retrieved cybernetic arm detail from source
- Verified RAG maintains worldbuilding consistency

## Fine-Tuning Infrastructure (READY)

### Documentation Created
- `fine-tuning/FINE_TUNING_SETUP.md` - Complete 400+ line guide
- `fine-tuning/README.md` - Quick reference

### Directory Structure
```
fine-tuning/
├── FINE_TUNING_SETUP.md           # Complete guide
├── README.md                      # Quick reference
├── data/
│   ├── raw/                       # Place your writing samples here (.txt, .md)
│   ├── processed/                 # Training JSONL (auto-generated)
│   └── validation/                # Test set
├── configs/
│   ├── qlora_style_transfer.yaml  # QLoRA config (8-12GB VRAM)
│   └── lora_style_transfer.yaml   # LoRA config (18-24GB VRAM)
├── scripts/
│   ├── 1_prepare_data.py          # TODO: Create data conversion script
│   ├── 2_train_lora.sh            # ✅ Training launcher (ready)
│   ├── 3_merge_adapter.py         # TODO: Create merge script
│   └── 4_compare_models.py        # TODO: Create comparison script
├── checkpoints/                   # Training outputs (auto-generated)
├── merged_models/                 # vLLM-ready models (auto-generated)
└── logs/                          # Training logs (auto-generated)
```

### Training Configs Ready
- **QLoRA** (recommended): 4-bit quantization, rank=64, lr=2e-4, 3 epochs
- **LoRA** (higher quality): No quantization, rank=64, lr=2e-4, 3 epochs
- Both use Llama-3.1-8B-Instruct as base model

## Next Session Goals

### 1. Install Training Framework
```bash
source ~/.venvs/llm/bin/activate
pip install axolotl[flash-attn,deepspeed]
```

### 2. Create Data Preparation Script
**File:** `fine-tuning/scripts/1_prepare_data.py`

**Requirements:**
- Read `.txt`/`.md` files from `data/raw/`
- Chunk into 500-2000 token examples
- Convert to JSONL with system/user/assistant format
- Generate system prompts based on writing style analysis
- Create 90/10 train/validation split
- Output: `data/processed/training.jsonl`, `validation.jsonl`

**JSONL Format:**
```jsonl
{"messages": [{"role": "system", "content": "You are a science fiction author writing in a technical, atmospheric style."}, {"role": "user", "content": "Write a scene where Elena enters the bridge during a crisis."}, {"role": "assistant", "content": "Your actual writing sample here..."}]}
```

### 3. Create Merge Script
**File:** `fine-tuning/scripts/3_merge_adapter.py`

**Requirements:**
- Load base model weights
- Apply LoRA adapter from checkpoint
- Save merged model in safetensors format
- Include tokenizer and config
- Output vLLM-compatible model

### 4. Collect Training Data
**Minimum:** 100 examples × 500+ tokens  
**Recommended:** 500-1000 examples

**Quality criteria:**
- Complete narrative passages (not fragments)
- Your natural writing style
- Diverse scenes and tones
- UTF-8 plain text
- Remove editing notes/TODOs

### 5. Training Workflow
```bash
# 1. Prepare data
python scripts/1_prepare_data.py --input data/raw/ --output data/processed/

# 2. Train
./scripts/2_train_lora.sh configs/qlora_style_transfer.yaml

# 3. Merge
python scripts/3_merge_adapter.py \
  --checkpoint checkpoints/qlora-style-run-1/checkpoint-XXX \
  --output merged_models/llama-3.1-8b-your-style

# 4. Test
cd ..
./serve_vllm.sh "fine-tuning/merged_models/llama-3.1-8b-your-style" 8000 9 64000
```

## Technical Notes

### RTX 5090 Constraints
- **FlashInfer backend required:** `export VLLM_ATTENTION_BACKEND=FLASHINFER`
- **Minimum sequences:** `max_seqs=9` (warmup limitation)
- **Context maximum:** 100k tokens (hardware limit, not model limit)
- **Training capacity:** QLoRA fits 8B models with ~8-12GB VRAM

### Training Expectations (QLoRA on 8B Model)
- **VRAM usage:** 8-12GB during training
- **Speed:** ~40-50 tokens/sec
- **Time:** ~2-4 hours for 1000 samples × 3 epochs
- **Quality:** Good style capture with proper data

### Training Parameters (QLoRA Config)
- **LoRA rank:** 64 (balance between capacity and speed)
- **Learning rate:** 2e-4 (higher than factual learning)
- **Epochs:** 3 (typical for style transfer)
- **Batch size:** 4 per device, 4 gradient accumulation (effective=16)
- **Sequence length:** 2048 tokens

### vLLM Integration
- Fine-tuned models must be merged (vLLM doesn't support adapters)
- Load like any model: `./serve_vllm.sh "path/to/merged_model"`
- Works with RAG proxy: Start vLLM on 8000, RAG proxy on 8001
- Combined: Your style + worldbuilding consistency

## Key Resources

**Documentation to reference:**
- `fine-tuning/FINE_TUNING_SETUP.md` - Complete training guide
- `fine-tuning/README.md` - Quick start
- `docs/SCIENCE_FICTION_WRITING_GUIDE.md` - Writing optimization
- `RAG/RAG_SETUP.md` - RAG integration guide

**Config files:**
- `fine-tuning/configs/qlora_style_transfer.yaml` - Recommended training config
- `fine-tuning/configs/lora_style_transfer.yaml` - Higher quality alternative

**Scripts ready:**
- `fine-tuning/scripts/2_train_lora.sh` - Training launcher (executable)

**Scripts needed:**
- `fine-tuning/scripts/1_prepare_data.py` - Data conversion (high priority)
- `fine-tuning/scripts/3_merge_adapter.py` - Adapter merge (required before vLLM)
- `fine-tuning/scripts/4_compare_models.py` - Quality comparison (optional)

## Common Issues & Solutions

**Out of memory during training:**
- Reduce batch size: `per_device_train_batch_size: 2`
- Increase gradient accumulation: `gradient_accumulation_steps: 8`
- Reduce LoRA rank: `lora_r: 32`

**Training loss not decreasing:**
- Increase learning rate: `3e-4` instead of `2e-4`
- Check data quality (remove duplicates, ensure variety)
- Increase epochs: 5 instead of 3

**Model outputs gibberish:**
- Learning rate too high (reduce to `1e-4`)
- Overfitting (use earlier checkpoint)
- Bad training data (check encoding)

**vLLM can't load merged model:**
- Verify safetensors exist in output directory
- Check config.json and tokenizer files present
- Test load with transformers library first

## Session History

Previous sessions logged in:
- `docs/history/2025-10-24_benchmarks_and_rag_validation.md`
- `docs/history/2025-10-19_rag_workflow_summary.md`
- `docs/history/2025-10-19_retrieval_test_logging.md`
- `docs/history/2025-10-19_rag_steps_4_5_completion.md`
- `docs/history/2025-10-19_rag_markdown_support.md`
- `docs/history/2025-10-18_benchmark_improvements.md`

## Quick Commands Reference

```bash
# Activate environments
source ~/.venvs/llm/bin/activate   # vLLM + training
source ~/.venvs/rag/bin/activate   # RAG only

# Server operations
./serve_vllm.sh                    # Start vLLM (default model)
./serve_vllm.sh "MODEL" PORT SEQS CTX GPU  # Custom config
./stop_vllm.sh                     # Stop vLLM
./serve_rag_proxy.sh scifi_world   # Start RAG proxy
./monitor_vllm.sh                  # Monitor vLLM
./monitor_rag_proxy.sh             # Monitor RAG

# Benchmarks
cd benchmarks
./1_throughput.sh                  # Token generation speed
./2_context_scaling.sh             # Context window performance
python 3_creative_quality.py       # Writing quality
python 4_long_context_coherence.py # Character consistency

# RAG
cd RAG
./3_test_retrieval.py              # Test embedding quality
./4_query.py "question"            # Query with RAG
```

## Ready to Begin

All infrastructure in place. Next steps:
1. Install Axolotl training framework
2. Create `1_prepare_data.py` script (convert writing → JSONL)
3. Create `3_merge_adapter.py` script (merge LoRA → full model)
4. Collect your writing samples
5. Begin training journey

**Goal:** Train Llama-3.1-8B-Instruct to capture your personal narrative style while maintaining RAG worldbuilding consistency.
