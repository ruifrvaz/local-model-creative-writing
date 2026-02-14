# Curate Visions of Gaea Training Dataset

**Priority:** 1  
**State:** Completed  
**Created:** 2025-11-21  
**Completed:** 2025-11-24  
**Archive:** `docs/archives/002_visions_of_gaea_curation/`

## Description

Create a detailed, properly chunked training dataset from "Visions of Gaea" for fine-tuning. The dataset should capture the narrative style, worldbuilding, and character voices while being optimally structured for QLoRA/LoRA training.

## Background

Current training data consists of 139 scene files (188,331 words) from 8 story universes. "Visions of Gaea" represents a complete, cohesive narrative that could strengthen style transfer when properly curated into training examples.

## Completion Summary

**Status:** ✅ All acceptance criteria met

### Results Achieved

**Curation Complete (Nov 21-24, 2025):**
- ✅ 35 chunks created (chunk_001 through chunk_035)
- ✅ 63,302 total words processed (100.7% of source manuscript)
- ✅ 91% optimal sizing (900-2,100 words per chunk)
- ✅ 100% narrative integrity (no forced splits)
- ✅ Complete manuscript coverage (Prologue + 11 Memories + Epilogue)

**Quality Metrics:**
- Average chunk size: 1,809 words
- Scene distribution: 40% action, 31% dialogue, 14% introspection, 14% exposition
- POV consistency: 97% second-person maintained
- Token estimate: ~82,300 total training tokens

**Documentation:**
- 5 session reports documenting curation process
- Complete quality analysis and validation
- Training configuration recommendations
- All metadata archived in `docs/archives/002_visions_of_gaea_curation/`

**Files Location:**
- Chunks: `fine-tuning/data/raw/visions_of_gaea/chunk_*.txt`
- Source: `fine-tuning/data/raw/visions_of_gaea/ascension_part_1_manuscript.txt`
- Archive: `docs/archives/002_visions_of_gaea_curation/` (reports, session notes, temp files)

## Next Steps

**Training Pipeline:**
1. Run `fine-tuning/training/1_prepare_data.py` to generate JSONL
2. Configure `fine-tuning/configs/qlora_style_transfer.yaml`
3. Execute `fine-tuning/training/2_train_lora.sh`
4. Validate with `fine-tuning/benchmarks/1_voice_comparison.py`

**Estimated training time:** 4.5-6 hours (RTX 5090, QLoRA, 3 epochs)

## Technical Considerations

### Chunk Size Guidelines
Based on current dataset (900-2,100 words/scene):
- **Minimum:** 800 words (ensure sufficient context)
- **Target:** 1,200-1,500 words (sweet spot for training)
- **Maximum:** 2,500 words (avoid overly long sequences)
- **Reasoning:** Balances context window usage vs training efficiency

### JSONL Format
```json
{
  "conversations": [
    {
      "from": "system",
      "value": "You are a science fiction writer with expertise in character-driven narratives."
    },
    {
      "from": "human", 
      "value": "Write a scene where [context/prompt]"
    },
    {
      "from": "assistant",
      "value": "[Scene text from Visions of Gaea chunk]"
    }
  ]
}
```

### Prompt Engineering
Each chunk needs a corresponding prompt that:
- Describes the scene context (setting, characters, situation)
- Specifies narrative requirements (POV, tone, pacing)
- Provides enough direction without over-constraining
- Allows model to learn style patterns, not just memorize text

### Quality Filters
- Exclude:
  - Scene fragments < 800 words
  - Non-narrative text (tables of contents, author notes)
  - Incomplete dialogue exchanges
  - Orphaned references without context
- Include:
  - Complete scenes with clear narrative arc
  - Balanced mix of scene types
  - Representative character voices
  - Key worldbuilding moments

## Processing Workflow

1. **Extract source text** → Identify scene boundaries
2. **Chunk scenes** → Apply size guidelines and coherence rules
3. **Generate prompts** → Create contextual writing instructions per chunk
4. **Format JSONL** → Convert to training format
5. **Validate** → Check format, sizes, prompt quality
6. **Merge/organize** → Integrate with existing dataset or separate
7. **Document** → Create dataset card with statistics

## Expected Outcomes

**Dataset size estimate (assuming 80k word manuscript):**
- ~50-70 chunks (avg 1,200 words each)
- ~100k-120k training tokens
- Combined with existing 139 scenes → ~200 total training examples

**Training impact:**
- Increased Gaea universe representation
- Stronger style consistency for that narrative
- Better generalization with more diverse examples
- 2-4 hour training time (similar to current)

## Dependencies

- Access to "Visions of Gaea" manuscript files
- Python environment: `~/.venvs/finetune`
- Libraries: `tiktoken` (token counting), `json`, `pathlib`
- Reference: Existing `fine-tuning/training/1_prepare_data.py` script

## Notes

### Considerations for Prompt Generation
- Avoid overly specific prompts (reduces generalization)
- Include variety: "Write a tense scene", "Describe [character]'s internal conflict", etc.
- Some prompts should be minimal: "Continue this story"
- Balance specificity with flexibility

### Scene Type Distribution Goals
Aim for balanced representation:
- 30% Action/External conflict
- 25% Dialogue/Interaction
- 25% Introspection/Character development  
- 20% Worldbuilding/Exposition

### Future Enhancements
- Audio transcription if dictated scenes exist
- Multiple versions of same scene for variation
- Chain-of-thought prompts for complex narrative decisions
- Style intensity labels (high/medium/low authorial voice)

## Related Files

- `fine-tuning/training/1_prepare_data.py` - Existing data preparation script
- `fine-tuning/configs/qlora_style_transfer.yaml` - Training configuration
- `docs/FINE_TUNING_GUIDE.md` - Complete fine-tuning workflow
- `docs/QLORA_TRAINING_GUIDE.md` - QLoRA method details

## References

- Current dataset: 139 scenes, 188,331 words, avg 1,355 words/scene
- Optimal training sequence length: 1,024-2,048 tokens (see `docs/TRAINING_SEQUENCE_LENGTH_GUIDE.md`)
- Axolotl format requirements: Conversation-style JSONL with system/user/assistant roles
