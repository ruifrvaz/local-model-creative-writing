# Fine-Tuning Benchmarks

## Purpose

Measure style transfer effectiveness by comparing model output **before** and **after** fine-tuning. Tests whether the model successfully learned the target writing voice from training data.

## Benchmark Scripts

### 1. `1_voice_comparison.py` - Model Output Generation

**Purpose:** Generate completions from models and extract style metrics

**Modes:**
- `--baseline --port 8000` - Generate from base model only
- `--finetuned --port 8002` - Generate from fine-tuned model only

**Measures:**
- Vocabulary richness (unique words, word diversity)
- Sentence structure (avg length, complexity, variation)
- Stylistic markers (contractions, passive voice, dialogue ratio)
- Technical term density

**Output:** JSON files with completions and computed metrics
- `results/baseline_TIMESTAMP.json`
- `results/finetuned_TIMESTAMP.json`
- `results/comparison_TIMESTAMP.json` (compare mode only)

**Note:** Compare mode requires both models running simultaneously, which is not possible on RTX 5090 with FlashInfer's `max_seqs=9` requirement (both 8B models need ~32GB VRAM total).

---

### 2. `2_compare_with_training.py` - Ground Truth Comparison

**Purpose:** Measure which model is closer to your actual writing style

**Process:**
1. Analyzes all training data files (87 files) to establish ground truth style metrics
2. Loads existing baseline and fine-tuned result JSONs
3. Compares both models to training data profile
4. Calculates improvement scores

**Measures:**
- Distance from training data for each metric category
- Overall match score (0-100% per model)
- Improvement: fine-tuned vs baseline
- Category-specific improvements (lexical, sentence, style_markers, vocabulary)

**Output:** JSON file with detailed comparison
- `results/training_comparison_TIMESTAMP.json`

**Usage:**
```bash
# Use latest results automatically
python 2_compare_with_training.py --latest

# Or specify files explicitly
python 2_compare_with_training.py results/baseline_TIMESTAMP.json results/finetuned_TIMESTAMP.json
```

**This is the correct approach** - measures actual improvement toward your writing style, not arbitrary differences between models.

---

### 3. `3_blind_evaluation.py` - Human Quality Assessment

**Purpose:** Subjective evaluation to feel the quality difference between models

**Process:**
1. Generates side-by-side comparisons from existing result JSONs
2. Randomizes output order (A/B labels shuffled)
3. Creates markdown file for human evaluation
4. Reveals which model produced which output after review

**Why this matters:**
- Metrics measure style similarity, but not **quality** or **naturalness**
- Human evaluation catches issues metrics miss (awkward phrasing, unnatural flow)
- Validates that style transfer improved writing, not just changed it

**Output:** Interactive markdown evaluation form
- `results/blind_evaluation_TIMESTAMP.md`

**Usage:**
```bash
# Generate blind evaluation from latest results
python 3_blind_evaluation.py --latest

# Or specify result files
python 3_blind_evaluation.py results/baseline_20251107.json results/finetuned_20251107.json
```

**Evaluation workflow:**
1. Script generates markdown with pairs of outputs (A/B)
2. You read both outputs and note which feels better
3. Mark your preference: A, B, or no preference
4. Scroll to bottom to reveal which was baseline/fine-tuned
5. Calculate win rate: fine-tuned wins / total comparisons

**Target:** Fine-tuned should win >60% of blind comparisons for deployment

---

## Test Prompts

**Location:** `benchmarks/test_prompts.json`

**Format:**
```json
{
  "prompts": [
    {
      "id": "scene_01",
      "prompt": "Elena stood at the observation window...",
      "category": "narrative_description",
      "expected_style": "concise, technical vocabulary"
    }
  ]
}
```

**Categories:**
- `narrative_description` - Scene-setting prose
- `dialogue` - Character conversations
- `technical_exposition` - Scientific explanations
- `emotional_introspection` - Character thoughts/feelings
- `action_sequence` - Fast-paced events

## Metrics Reference

### Vocabulary Metrics
- **Lexical diversity**: `unique_words / total_words`
- **Rare word usage**: % of words outside common 5000
- **Technical term density**: Domain-specific vocabulary frequency

### Sentence Structure Metrics
- **Avg sentence length**: Words per sentence
- **Sentence length variance**: Consistency of pacing
- **Clause complexity**: Avg clauses per sentence

### Style Markers
- **Contraction rate**: "don't" vs "do not"
- **Passive voice ratio**: Passive constructions per 100 sentences
- **Dialogue ratio**: Dialogue words / total words
- **Paragraph length**: Avg sentences per paragraph

### Transfer Score
**Formula:**
```
transfer_score = weighted_average([
  vocab_similarity * 0.25,
  structure_similarity * 0.25,
  style_marker_match * 0.30,
  tone_consistency * 0.20
])
```

**Interpretation:**
- 0-30%: Minimal transfer (model unchanged)
- 31-60%: Partial transfer (some style elements learned)
- 61-85%: Strong transfer (clear style adoption)
- 86-100%: Excellent transfer (matches training data closely)

## Workflow

### Step 1: Generate Baseline (Before Fine-Tuning)
```bash
# Start base model
cd ~/scifi-llm
./serve_vllm.sh "meta-llama/Llama-3.1-8B-Instruct"

# Generate baseline completions
cd fine-tuning/benchmarks
source ~/.venvs/finetune/bin/activate
python 1_voice_comparison.py --baseline --port 8000

# Results saved to: results/baseline_TIMESTAMP.json
```

### Step 2: Train Model
```bash
cd ~/scifi-llm/fine-tuning/training
source ~/.venvs/finetune/bin/activate
./2_train_lora.sh
python 3_merge_adapter.py --auto
```

### Step 3: Generate Fine-Tuned Completions
```bash
# Stop base model, start fine-tuned model
cd ~/scifi-llm
./stop_vllm.sh
./serve_vllm.sh "fine-tuning/merged_models/llama-3.1-8b-qlora-style-pipeline-test" 8002

# Generate fine-tuned completions
cd fine-tuning/benchmarks
source ~/.venvs/finetune/bin/activate
python 1_voice_comparison.py --finetuned --port 8002

# Results saved to: results/finetuned_TIMESTAMP.json
```

### Step 4: Compare Against Training Data
```bash
cd ~/scifi-llm/fine-tuning/benchmarks
source ~/.venvs/finetune/bin/activate
python 2_compare_with_training.py --latest

# Results saved to: results/training_comparison_TIMESTAMP.json
```

**Interpretation:**
- Overall match >60%: Strong style transfer, ready for deployment
- Overall match 40-60%: Moderate transfer, consider more training data
- Overall match <40%: Minimal transfer, review training data quality
- Improvement >10%: Fine-tuning effective
- Improvement 5-10%: Moderate improvement
- Improvement <5%: Limited benefit from fine-tuning

### Step 5: Blind Evaluation (Optional but Recommended)
```bash
cd ~/scifi-llm/fine-tuning/benchmarks
source ~/.venvs/finetune/bin/activate
python 3_blind_evaluation.py --latest

# Open results/blind_evaluation_TIMESTAMP.md
# Read outputs, mark preferences, reveal at bottom
```

**Why do this:**
- Metrics don't capture subjective quality
- You'll immediately feel if fine-tuning improved naturalness
- Catches issues like awkward phrasing that metrics miss
- Target: Fine-tuned wins >60% of comparisons

## Output Format

### Voice Comparison JSON
```json
{
  "timestamp": "2025-10-29T14:30:00",
  "baseline_model": "meta-llama/Llama-3.1-8B-Instruct",
  "finetuned_model": "llama-3.1-8b-user-style",
  "test_prompts": 10,
  "transfer_score": 72.5,
  "metrics": {
    "vocabulary": {
      "baseline_diversity": 0.68,
      "finetuned_diversity": 0.71,
      "similarity_score": 85.2
    },
    "sentence_structure": {
      "baseline_avg_length": 18.3,
      "finetuned_avg_length": 14.7,
      "similarity_score": 68.9
    }
  },
  "detailed_results": [
    {
      "prompt_id": "scene_01",
      "baseline_output": "...",
      "finetuned_output": "...",
      "metrics": {...}
    }
  ]
}
```

### Blind Evaluation Markdown
```markdown
# Blind Evaluation - Fine-Tuning Comparison

## Pair 1
**Prompt:** Elena stood at the observation window...

**Output A:**
[completion text]

**Output B:**
[completion text]

**Your preference:** [ ] A  [ ] B  [ ] No preference
**Reasoning:** ___________

---
## Reveal
Output A: fine-tuned
Output B: baseline
```

## Integration with Training Workflow

**Updated training sequence:**
1. Prepare data (`1_prepare_data.py`)
2. **Generate baseline benchmark** ← NEW
3. Train model (`2_train_lora.sh`)
4. Merge adapter (`3_merge_adapter.py`)
5. **Compare benchmark results** ← NEW
6. Deploy if transfer_score > 60%

## Dependencies

**Python packages (finetune venv):**
- `openai` - API client for querying both models
- `nltk` - Sentence tokenization, POS tagging
- `textstat` - Readability metrics
- Standard library: `json`, `argparse`, `datetime`

**Installation:**
Dependencies are installed automatically by `fine-tuning/setup/3_install_training_stack.sh`.

To install manually if needed:
```bash
source ~/.venvs/finetune/bin/activate
pip install openai nltk textstat
python -m nltk.downloader punkt averaged_perceptron_tagger
```

## Files Structure

```
fine-tuning/benchmarks/
├── README.md                      # This file
├── 1_voice_comparison.py          # Generate completions + metrics ✓ IMPLEMENTED
├── 2_compare_with_training.py     # Compare to training data ground truth ✓ IMPLEMENTED
├── 3_blind_evaluation.py          # Human quality assessment ✓ IMPLEMENTED
├── test_prompts.json              # Standard test set (12 prompts) ✓ READY
├── results/                       # Auto-generated outputs
│   ├── baseline_TIMESTAMP.json
│   ├── finetuned_TIMESTAMP.json
│   ├── training_comparison_TIMESTAMP.json  # From 2_compare_with_training.py
│   └── blind_evaluation_TIMESTAMP.md       # From 3_blind_evaluation.py
└── utils/                         # Shared analysis functions ✓ IMPLEMENTED
    ├── __init__.py
    ├── style_metrics.py           # Extract vocabulary, structure, style metrics
    └── comparison.py              # Calculate similarity scores
```

## Completion Behavior

**Note on `finish_reason`:**
- `length`: Hit max_tokens limit (200) - **Normal for creative writing**
- `stop`: Natural completion (model found stopping point)
- High `length` ratio is expected for narrative prompts - not an error

**Target metrics:**
- Transfer score: >60% for production deployment
- Category scores: Should show improvement in style_markers and sentence structure

## Notes

**Port management:**
- Base model: Port 8000 (default vLLM)
- Fine-tuned model: Port 8002 (for side-by-side comparison)
- Allows simultaneous testing without server restarts

**Test prompt selection:**
- Use prompts **not seen** during training
- Cover all style categories (narrative, dialogue, technical)
- Match genre/domain of training data
- 10-15 prompts sufficient for meaningful comparison

**Automation:**
- Benchmarks run via Python scripts (not bash)
- JSON output for programmatic analysis
- Markdown output for human review
- Integrate into `2_train_lora.sh` as optional post-training step
