# Generate Synthetic Training Data with Style Transfer

**Priority:** 2  
**Status:** Not Started  
**Created:** 2025-11-30  
**Depends On:** Task 006 (Completed)

## Description

Use the `style-transfer-generator` agent to create new fictional content that matches the Visions of Gaea narrative style. This expands the training dataset beyond the original manuscript by generating scenes in different universes while preserving the author's voice.

## Reference Files (Unbiased Analysis - Task 006 Winner)

- `fine-tuning/data/styles/visions_of_gaea/STYLE_TRANSFER_GUIDE_unbiased.md`
- `fine-tuning/data/styles/visions_of_gaea/STYLE_STATISTICS_unbiased.json`
- `fine-tuning/data/styles/visions_of_gaea/STYLE_PATTERNS_unbiased.md`

## Acceptance Criteria

- [ ] Run style-transfer-generator agent (`.github/agents/style-transfer-generator.md`)
- [ ] Generate content across multiple universes (AI governance, asteroid mining, colony, etc.)
- [ ] Target: 500+ instruction-response pairs
- [ ] Validate generated content against style metrics:
  - [ ] Second-person POV consistency >80%
  - [ ] Dialogue ratio within 27-50% range
  - [ ] Sentence length patterns match reference
- [ ] Store generated data in `fine-tuning/data/generated/`
- [ ] Convert to JSONL format for training

## Technical Details

**Agent:** `.github/agents/style-transfer-generator.md`

**Style Targets (from unbiased analysis):**
- POV: Second person present tense
- Avg sentence length: 21.3 words (range 15.9-27.4)
- Dialogue ratio: 27-50% (arc-dependent)
- Scene breaks: `***` markers
- Italics: Internal monologue with `...` framing

**Output Location:** `fine-tuning/data/generated/style_transfer/`

## Notes

This creates entirely new content in the author's voice. For reshaping existing content, see Task 008.
