# Curate Visions of Gaea Training Dataset

**Priority:** 1  
**State:** Open  
**Created:** 2025-11-21

## Description

Create a detailed, properly chunked training dataset from "Visions of Gaea" for fine-tuning. The dataset should capture the narrative style, worldbuilding, and character voices while being optimally structured for QLoRA/LoRA training.

## Background

Current training data consists of 139 scene files (188,331 words) from 8 story universes. "Visions of Gaea" represents a complete, cohesive narrative that could strengthen style transfer when properly curated into training examples.

## Acceptance Criteria

### 1. Source Material Organization
- [ ] Locate all "Visions of Gaea" manuscript files
- [ ] Identify total word count and chapter structure
- [ ] Catalog character POVs and narrative arcs
- [ ] Document worldbuilding elements (planets, technology, species)

### 2. Chunking Strategy
- [ ] Determine optimal chunk size (target: 900-2,100 words based on current dataset)
- [ ] Define chunking boundaries:
  - Scene breaks (natural stopping points)
  - POV shifts
  - Chapter segments
  - Complete narrative units
- [ ] Ensure chunks maintain narrative coherence
- [ ] Avoid mid-dialogue or mid-action splits

### 3. Data Quality Standards
- [ ] Each chunk should be a complete narrative unit (beginning, middle, end)
- [ ] Preserve character voice consistency within chunks
- [ ] Maintain worldbuilding context (don't orphan references)
- [ ] Include sufficient context for standalone comprehension
- [ ] Filter out incomplete scenes or fragments

### 4. Metadata Extraction
- [ ] Tag each chunk with:
  - Character POV
  - Scene type (action, dialogue, introspective, exposition)
  - Story arc / chapter
  - Word count
  - Narrative tension level (if applicable)
- [ ] Document recurring themes and motifs

### 5. Technical Implementation
- [ ] Create processing script: `fine-tuning/training/prepare_visions_of_gaea.py`
- [ ] Input: Raw manuscript files (`.md`, `.txt`, or `.docx`)
- [ ] Output: JSONL format matching current training structure
- [ ] Validation: Ensure proper formatting for Axolotl
- [ ] Test with sample to verify chunk quality

### 6. Dataset Statistics
- [ ] Calculate:
  - Total chunks created
  - Average chunk word count
  - Distribution across scene types
  - POV character distribution
  - Total training tokens (approximate)
- [ ] Compare to existing 139-scene dataset
- [ ] Document expected training time impact

### 7. Integration with Existing Dataset
- [ ] Decide: Append to current dataset or create separate collection
- [ ] If appending: Verify balanced representation across universes
- [ ] If separate: Create new training config for Gaea-only fine-tuning
- [ ] Update `fine-tuning/data/raw/` organization

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
