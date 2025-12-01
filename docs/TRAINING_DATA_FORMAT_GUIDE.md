# Training Data Format Guide

Guidelines for structuring fine-tuning data for style transfer with instruct models.

## Key Insight: Match Training Format to Usage Pattern

Your actual usage pattern determines optimal training data format.

### Usage Pattern Analysis

**Instruction-style** (NOT how creative writing works):
```
User: "Write a scene where Elena discovers the artifact"
Model: [generates complete scene]
```

**Completion-style** (actual creative writing workflow):
```
User: "Haji and Alan walked along the street. It was night, Alan was worried about his future. Haji said,"
Model: [continues naturally in author's voice]
```

## Recommended Format: Prefix-Completion

Split each training chunk into prefix (user prompt) and completion (assistant response):

```json
{
  "messages": [
    {"role": "user", "content": "The mist gradually cleared, allowing him to see in the distance a glade laying bare to the silvery night."},
    {"role": "assistant", "content": "Confidence warmed his blood and banished all his doubts, for he knew he was arriving at the heart of the forest, the cradle of life, Her dwelling..."}
  ]
}
```

### Why This Works

1. **Matches real usage**: You provide partial narrative, model continues
2. **Teaches seamless continuation**: Model learns to maintain voice mid-sentence
3. **No instruction overhead**: Model doesn't waste capacity learning instruction patterns
4. **Preserves stylistic continuity**: Prefix sets tone, completion maintains it

### Split Point Strategy

Use **varied split points** (5-15% of chunk as prefix):

| Split Ratio | Example Prefix | Purpose |
|-------------|----------------|---------|
| 5% | "Prologue\n\nA dark figure, cloaked in a hooded cape," | Short continuation |
| 10% | "The mist gradually cleared, allowing him to see..." | Medium context |
| 15% | "And so it was that after countless days of wandering, he found Her, sitting quietly..." | Rich context |

**Why varied?**
- Prevents overfitting to fixed prefix length
- Teaches completion from various narrative positions
- Better matches unpredictable real usage

### What NOT to Do

**Don't use generic instructions:**
```json
// BAD - teaches instruction-following, not style
{"role": "user", "content": "Continue writing:"}
{"role": "assistant", "content": "[2000 word chunk]"}
```

**Don't use scene-specific prompts with small datasets:**
```json
// BAD - overfits to prompt patterns with <50 examples
{"role": "user", "content": "Write a slow introspective scene in a forest:"}
```

**Don't include system prompts in training data:**
```json
// BAD - conflicts with production system prompt
{"role": "system", "content": "You are a creative writing assistant..."}
```

## System Prompt Considerations

### Why No System Prompt in Training Data

1. **Conflict risk**: Training system prompt may differ from Continue.dev config
2. **Flexibility**: Model should work with ANY system prompt at inference
3. **Wasted capacity**: System prompt understanding is already in base instruct model

### Production System Prompt

Set in Continue.dev config (`~/.continue/config.json`), not training data:
```json
{
  "models": [{
    "systemMessage": "You are a creative writing assistant helping with science fiction narrative."
  }]
}
```

## Instruct vs Base Models

### Recommendation: Use Instruct Models

Despite completion-style usage, instruct models (`Llama-3.1-8B-Instruct`) are preferred:

| Factor | Instruct Model | Base Model |
|--------|----------------|------------|
| Completion capability | ✅ Preserved | ✅ Native |
| Instruction following | ✅ Available when needed | ❌ Lost |
| System prompt support | ✅ Works | ❌ No concept |
| Continue.dev compatibility | ✅ Expected format | ⚠️ May need adaptation |
| Direction giving | ✅ "Make this more tense" | ❌ Won't understand |

### Why Instruct Models Work for Completion

- Instruction tuning is **additive**, not destructive
- Base completion capability remains intact
- Fine-tuning with prefix-completion teaches a new "mode"
- Model learns: "When user provides narrative (not question), continue it"

## Implementation

### Data Preparation Script

`fine-tuning/training/1_prepare_data.py` implements prefix-completion format:

```bash
python 1_prepare_data.py \
  --input ../data/raw/visions_of_gaea/ \
  --output ../data/processed/visions_training.jsonl \
  --min-prefix-ratio 0.05 \
  --max-prefix-ratio 0.15
```

### Example Output

Input chunk (2000 words):
```
Prologue

A dark figure, cloaked in a hooded cape, trudged wearily along a muddy path...
[continues for 2000 words]
...'Awake!' said a voice, now in a demanding tone.
```

Output training example:
```json
{
  "messages": [
    {"role": "user", "content": "Prologue\n\nA dark figure, cloaked in a hooded cape, trudged wearily along a muddy path submerged in a dense misty forest. Its sluggish footsteps resembled that of a sleepwalker stepping noisily on shallow puddles and tangled roots,"},
    {"role": "assistant", "content": "as it followed the pale green glow of fruits that hung from the thick canopy. A mournful cry wailed through the mist...[rest of chunk]"}
  ]
}
```

## Summary

| Aspect | Recommendation |
|--------|----------------|
| Training format | Prefix-completion (varied 5-15% split) |
| System prompt | None in training data |
| User prompt | Actual narrative text (prefix) |
| Model type | Instruct (preserves flexibility) |
| Prompt variation | Minimal (avoid overfitting) |

## References

- `fine-tuning/README.md` - Training workflow
- `fine-tuning/FINE_TUNING_SETUP.md` - Complete setup guide
- `.continue/README.md` - Continue.dev configuration
