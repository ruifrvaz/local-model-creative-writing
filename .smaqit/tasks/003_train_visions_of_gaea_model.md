# Train Fine-Tuned Model on Visions of Gaea Dataset

**Priority:** 1  
**Status:** Not Started  
**Created:** 2025-11-24  
**Depends On:** Task 002 (Completed), Task 006 (Completed)

## Description

Train QLoRA fine-tuned model using the curated Visions of Gaea manuscript chunks (35 files, 63,302 words) to learn the author's distinctive second-person narrative voice.

**Training Data:** `fine-tuning/data/raw/visions_of_gaea/chunk_*.txt` (35 chunks)

## Acceptance Criteria

- [ ] Run `1_prepare_data.py` to convert chunks to JSONL format
- [ ] Verify token counts per chunk (target: all < 4096 tokens)
- [ ] Update `configs/qlora_style_transfer.yaml` with correct paths
- [ ] Generate baseline benchmarks before training
- [ ] Execute training with `./training/2_train_lora.sh`
- [ ] Merge adapter with `3_merge_adapter.py --auto`
- [ ] Validate transfer score >60%
- [ ] Document final metrics

## Technical Details

- **Source:** 35 curated chunks from original manuscript
- **Total Words:** 63,302
- **Estimated Tokens:** ~82,300
- **Training Time:** ~5 hours on RTX 5090

## Notes

This uses the original manuscript text directly. For expanded training data with synthetic content, see Task 007 (style-transfer-generator).

## Background

Task 002 completed manuscript curation, producing 35 training-ready chunks (63,302 words) with excellent quality metrics:
- 91% optimal sizing (900-2,100 words)
- 100% narrative integrity
- Balanced scene distribution (40% action, 31% dialogue, 14% introspection, 14% exposition)
- 97% second-person POV consistency

**Reference:** `docs/archives/002_visions_of_gaea_curation/CURATION_REPORT.md` for complete dataset analysis.

## Acceptance Criteria

### 1. Data Preparation
- [ ] Run `1_prepare_data.py` to convert chunks to JSONL format
- [ ] Verify JSONL structure matches Axolotl requirements
- [ ] Calculate token counts per chunk (target: all < 4096 tokens)
- [ ] Create validation split (10%, ~3-4 chunks)
- [ ] Document final dataset statistics (chunks, tokens, file size)

### 2. Training Configuration
- [ ] Update `configs/qlora_style_transfer.yaml`:
  - [ ] Set `sequence_len: 4096` (accommodates largest chunks)
  - [ ] Set `micro_batch_size: 1` (memory safety)
  - [ ] Set `gradient_accumulation_steps: 8` (effective batch = 8)
  - [ ] Set `num_epochs: 3` (105 training examples)
  - [ ] Set `learning_rate: 0.0002` (QLoRA standard)
  - [ ] Configure dataset path to processed JSONL
- [ ] Verify configuration passes Axolotl validation

### 3. Pre-Training Baseline
- [ ] Start base model on port 8000 (`meta-llama/Llama-3.1-8B-Instruct`)
- [ ] Run `benchmarks/1_voice_comparison.py --baseline --port 8000`
- [ ] Save baseline results for post-training comparison
- [ ] Document baseline metrics (vocabulary, structure, style markers)

### 4. Training Execution
- [ ] Activate finetune environment (`source ~/.venvs/finetune/bin/activate`)
- [ ] Start training: `./training/2_train_lora.sh`
- [ ] Monitor progress with `./monitoring/monitor_training.sh`
- [ ] Track validation loss convergence
- [ ] Verify checkpoints saved (every 0.5 epoch)
- [ ] Document training time and final loss values

### 5. Model Merging
- [ ] Run `training/3_merge_adapter.py --auto` (selects best checkpoint)
- [ ] Verify merged model location: `merged_models/llama-3.1-8b-visions-style/` or similar
- [ ] Test model loads without errors
- [ ] Document final model size and location

### 6. Post-Training Validation
- [ ] Start fine-tuned model on port 8002
- [ ] Run `benchmarks/1_voice_comparison.py --finetuned --port 8002`
- [ ] Compare with baseline results
- [ ] Calculate transfer score and category improvements
- [ ] Run `benchmarks/3_blind_evaluation.py --latest` for subjective quality
- [ ] Evaluate blind comparison results (target: >60% fine-tuned preference)

### 7. Quality Assessment
- [ ] Verify style transfer metrics:
  - [ ] Transfer score >60% (overall style adoption)
  - [ ] Vocabulary overlap >70% (author's word choices)
  - [ ] Sentence structure >65% (rhythm, pacing)
  - [ ] Style markers >50% (second-person POV, italics)
  - [ ] POV consistency >80% (maintains second-person)
- [ ] Manual testing with narrative prompts
- [ ] Document specific improvements vs baseline

### 8. Deployment Decision
- [ ] If metrics meet targets: Deploy to production (replace base model)
- [ ] If metrics below targets: Analyze issues, adjust config, retrain
- [ ] Document final decision and rationale
- [ ] Update vLLM server config if deploying

## Technical Specifications

### Dataset Details
- **Source:** `fine-tuning/data/raw/visions_of_gaea/chunk_*.txt` (35 files)
- **Total Words:** 63,302
- **Estimated Tokens:** ~82,300 tokens
- **Average Chunk:** 1,809 words (~2,352 tokens)
- **Size Range:** 375-2,813 words (~488-3,657 tokens)

### Training Parameters (Recommended)

**Model:** `meta-llama/Llama-3.1-8B-Instruct`  
**Method:** QLoRA (4-bit quantization)  
**Sequence Length:** 4,096 tokens  
**Batch Size:** 1 (micro) × 8 (gradient accumulation) = 8 effective  
**Learning Rate:** 2e-4  
**Epochs:** 3  
**LoRA Rank:** 16  
**LoRA Alpha:** 32  
**LoRA Dropout:** 0.05  

**Hardware:** RTX 5090 (32GB VRAM)  
**Memory Usage:** ~25GB VRAM peak  
**Training Time:** 4.5-6 hours (estimated)

### Expected Outcomes

**Style Characteristics to Learn:**
- **Narrative Voice:** Second-person POV ("you") with italicized internal monologue
- **Philosophical Commentary:** Omniscient narrator interjections
- **Worldbuilding Integration:** Natural use of technical terms (Units, sentinels, Torment)
- **Action Sequences:** Varied pacing with sensory detail
- **Emotional Tone:** Restraint without melodrama, physical reactions showing emotion
- **Dialogue:** Character-specific speech patterns, multilayered communication

**Success Indicators:**
- Model generates second-person POV consistently
- Uses italics for internal thought appropriately
- Integrates worldbuilding terms without info-dumping
- Maintains emotional restraint in intense scenes
- Shows philosophical depth in narrative commentary

## Workflow Steps

### Step 1: Data Preparation (5-10 minutes)
```bash
cd fine-tuning/training
source ~/.venvs/finetune/bin/activate

python 1_prepare_data.py \
  --input ../data/raw/visions_of_gaea/ \
  --output ../data/processed/visions_training.jsonl \
  --min-tokens 400 \
  --max-tokens 4000 \
  --sequence-length 4096

# Verify output
wc -l ../data/processed/visions_training.jsonl
head -1 ../data/processed/visions_training.jsonl | jq '.'
```

### Step 2: Configure Training (5 minutes)
```bash
# Edit fine-tuning/configs/qlora_style_transfer.yaml
# Update sequence_len, dataset path, batch size
# Verify with: axolotl validate configs/qlora_style_transfer.yaml
```

### Step 3: Generate Baseline (10-15 minutes)
```bash
# Terminal 1: Start base model
cd ~/scifi-llm
./serve_vllm.sh "meta-llama/Llama-3.1-8B-Instruct"

# Terminal 2: Benchmark baseline
cd fine-tuning/benchmarks
source ~/.venvs/finetune/bin/activate
python 1_voice_comparison.py --baseline --port 8000
```

### Step 4: Execute Training (4.5-6 hours)
```bash
# Terminal 1: Start training
cd ~/scifi-llm/fine-tuning/training
source ~/.venvs/finetune/bin/activate
./2_train_lora.sh

# Terminal 2: Monitor progress
cd ~/scifi-llm
./monitoring/monitor_training.sh
```

### Step 5: Merge Adapter (2-5 minutes)
```bash
cd ~/scifi-llm/fine-tuning/training
source ~/.venvs/finetune/bin/activate
python 3_merge_adapter.py --auto
```

### Step 6: Validate Results (10-15 minutes)
```bash
# Terminal 1: Start fine-tuned model
cd ~/scifi-llm
./stop_vllm.sh
./serve_vllm.sh "fine-tuning/merged_models/llama-3.1-8b-visions-style" 8002

# Terminal 2: Benchmark fine-tuned
cd fine-tuning/benchmarks
source ~/.venvs/finetune/bin/activate
python 1_voice_comparison.py --finetuned --port 8002

# Compare results
python 2_compare_with_training.py --latest

# Blind evaluation
python 3_blind_evaluation.py --latest
```

## Success Metrics

### Quantitative Targets
- **Transfer Score:** >60% (indicates strong style adoption)
- **Vocabulary Match:** >70% (uses author's word choices)
- **Sentence Structure:** >65% (matches rhythm and pacing)
- **Style Markers:** >50% (second-person POV, formatting conventions)
- **POV Consistency:** >80% (maintains narrative perspective)

### Qualitative Targets
- Generates coherent second-person narratives on demand
- Uses italics appropriately for internal monologue
- Integrates technical worldbuilding naturally (no exposition dumps)
- Maintains emotional restraint in dramatic scenes
- Shows philosophical depth without pretension
- Handles action sequences with varied pacing
- Creates distinct character voices in dialogue

### Blind Evaluation Targets
- Fine-tuned model wins >60% of blind comparisons
- Human evaluators note improved naturalness
- Style feels consistent with source material
- No awkward phrasing or unnatural constructions

## Dependencies

**Completed:**
- ✅ Task 002: Visions of Gaea curation (35 chunks ready)
- ✅ Fine-tuning environment setup (`~/.venvs/finetune`)
- ✅ Training scripts validated (`2_train_lora.sh` tested)
- ✅ Benchmark suite ready (`1_voice_comparison.py`, `2_compare_with_training.py`, `3_blind_evaluation.py`)

**Required During Execution:**
- vLLM server for baseline/fine-tuned model testing
- RTX 5090 with 32GB VRAM available
- ~100GB free disk space (model checkpoints)
- 4.5-6 hours of uninterrupted training time

## Troubleshooting

### Out of Memory During Training
- Reduce `sequence_len` from 4096 to 3072 (truncates 3 largest chunks)
- Reduce `micro_batch_size` to 1 (already minimum)
- Reduce `lora_r` from 16 to 8 (less expressive but smaller)

### Training Loss Not Decreasing
- Increase `learning_rate` from 2e-4 to 3e-4
- Verify dataset quality (check JSONL format)
- Ensure sufficient training steps (35 chunks × 3 epochs = 105 steps)

### Low Transfer Score After Training
- Train for more epochs (3 → 5)
- Increase LoRA rank (16 → 32 for more expressiveness)
- Review training data quality (ensure style patterns present)
- Consider more training examples (add more manuscripts)

### Model Generates Generic Text
- Style signal may be weak - increase LoRA alpha (32 → 64)
- Training may have overfit - check validation loss curve
- Base model may be too strong - try smaller base (3B instead of 7B)

## Related Files

### Data Files
- **Chunks:** `fine-tuning/data/raw/visions_of_gaea/chunk_*.txt` (35 files)
- **Source:** `fine-tuning/data/raw/visions_of_gaea/ascension_part_1_manuscript.txt`
- **Archive:** `docs/archives/002_visions_of_gaea_curation/` (metadata, reports)

### Configuration Files
- **QLoRA Config:** `fine-tuning/configs/qlora_style_transfer.yaml`
- **Training Script:** `fine-tuning/training/2_train_lora.sh`
- **Merge Script:** `fine-tuning/training/3_merge_adapter.py`

### Documentation
- **Setup Guide:** `fine-tuning/FINE_TUNING_SETUP.md`
- **QLoRA Guide:** `docs/QLORA_TRAINING_GUIDE.md`
- **Benchmark Guide:** `fine-tuning/benchmarks/README.md`
- **Dataset Report:** `docs/archives/002_visions_of_gaea_curation/CURATION_REPORT.md`

## Notes

### Timeline Estimate
- Data preparation: ~10 minutes
- Configuration: ~5 minutes
- Baseline benchmark: ~15 minutes
- Training execution: ~5 hours
- Model merging: ~5 minutes
- Validation benchmark: ~15 minutes
- Blind evaluation: ~30 minutes (human review)
- **Total:** ~6.5 hours (mostly unattended training)

### Post-Completion Actions
- Update task status to "Completed"
- Document final metrics in completion summary
- Create history file if significant decisions made
- Consider deploying to production if metrics meet targets
- Archive training logs and checkpoints if successful

### Future Enhancements
- Combine with other training data (139 existing scenes from 8 universes)
- Use style-analyzer + style-transfer-generator for expanded dataset
- Experiment with LoRA (full precision) for higher quality
- Test different base models (Qwen2.5-7B, Qwen2.5-14B)
- Fine-tune on multiple manuscripts for broader style range
