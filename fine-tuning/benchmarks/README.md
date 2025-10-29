# Fine-Tuning Benchmarks

## Purpose

Measure style transfer effectiveness by comparing model output **before** and **after** fine-tuning. Tests whether the model successfully learned the target writing voice from training data.

## Benchmark Structure

### 1. Voice Comparison Test (`1_voice_comparison.py`)

**Measures:**
- Vocabulary richness (unique words, word diversity)
- Sentence structure (avg length, complexity, variation)
- Stylistic markers (contractions, passive voice, dialogue ratio)
- Tone consistency (technical vs creative language)

**Process:**
1. Load test prompts (unseen during training)
2. Generate completions from base model (port 8000)
3. Generate completions from fine-tuned model (port 8002)
4. Compare outputs using style metrics
5. Calculate transfer score (0-100%)

**Output:** JSON with side-by-side comparison, quantitative scores

### 2. Style Consistency Test (`2_style_consistency.py`)

**Measures:**
- Consistency across multiple prompts
- Adherence to training data style patterns
- Deviation from base model behavior

**Process:**
1. Generate 10 completions per model
2. Measure intra-model variance (consistency)
3. Compare against training data baseline
4. Identify which style elements transferred successfully

**Output:** JSON with variance metrics, transferability ranking

### 3. Blind Evaluation Test (`3_blind_evaluation.py`)

**Measures:**
- Human-readable comparison (for manual review)
- Side-by-side outputs without labels

**Process:**
1. Generate paired completions (base vs fine-tuned)
2. Randomize order (A/B testing format)
3. Output markdown for human evaluation
4. Optional: Track manual preference scores

**Output:** Markdown file with randomized pairs

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

### Before Fine-Tuning
```bash
# 1. Start base model
./serve_vllm.sh "meta-llama/Llama-3.1-8B-Instruct"

# 2. Generate baseline
cd fine-tuning/benchmarks
python 1_voice_comparison.py --baseline --port 8000

# Results saved to: results/baseline_TIMESTAMP.json
```

### After Fine-Tuning
```bash
# 1. Start fine-tuned model on alternate port
./serve_vllm.sh "fine-tuning/merged_models/llama-3.1-8b-user-style" 8002

# 2. Generate comparison (both models running)
cd fine-tuning/benchmarks
python 1_voice_comparison.py \
  --baseline-port 8000 \
  --finetuned-port 8002 \
  --compare

# Results saved to: results/comparison_TIMESTAMP.json

# 3. Optional: Blind evaluation
python 3_blind_evaluation.py \
  --baseline-port 8000 \
  --finetuned-port 8002

# Results saved to: results/blind_eval_TIMESTAMP.md
```

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

**Install:**
```bash
source ~/.venvs/finetune/bin/activate
pip install openai nltk textstat
python -m nltk.downloader punkt averaged_perceptron_tagger
```

## Files Structure

```
fine-tuning/benchmarks/
├── README.md                    # This file
├── 1_voice_comparison.py        # Main comparison benchmark (TODO)
├── 2_style_consistency.py       # Variance analysis (TODO)
├── 3_blind_evaluation.py        # Human evaluation format (TODO)
├── test_prompts.json            # Standard test set (TODO)
├── results/                     # Auto-generated outputs
│   ├── baseline_TIMESTAMP.json
│   ├── comparison_TIMESTAMP.json
│   └── blind_eval_TIMESTAMP.md
└── utils/                       # Shared analysis functions (TODO)
    ├── __init__.py
    ├── style_metrics.py         # Vocabulary, structure analysis
    └── comparison.py            # Score calculation
```

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
