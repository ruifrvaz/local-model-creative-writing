# Reshape Existing Content to Match Style

**Priority:** 3  
**Status:** Not Started  
**Created:** 2025-11-30  
**Depends On:** Task 006 (Completed)

## Description

Transform the existing generated scenes (139 files across 8 universes in `fine-tuning/data/raw/`) to match the Visions of Gaea narrative style. This preserves plot and worldbuilding while converting voice, POV, and stylistic elements.

## Source Content

Located in `fine-tuning/data/raw/`:
- `ai_gov_scene_*.txt` (15 files) — AI governance themes
- `asteroid_scene_*.txt` (10 files) — Asteroid mining
- `chapter_*.txt` (17 files) — First contact narrative
- `colony_mandate_*.txt` (5 files) — Colony bureaucracy
- `colony_scene_*.txt` (15 files) — Mars colony life
- `exoplanet_scene_*.txt` (15 files) — Exoplanet exploration
- `gen_ship_scene_*.txt` (17 files) — Generation ship
- `jump_drive_scene_*.txt` (20 files) — Jump drive technology
- `mars_seven_*.txt` (15 files) — Mars research station
- `station_dip_scene_*.txt` (15 files) — Station diplomacy

**Total:** ~139 existing scenes to reshape

## Reference Files (Unbiased Analysis)

- `fine-tuning/data/styles/visions_of_gaea/STYLE_TRANSFER_GUIDE_unbiased.md`
- `fine-tuning/data/styles/visions_of_gaea/STYLE_STATISTICS_unbiased.json`
- `fine-tuning/data/styles/visions_of_gaea/STYLE_PATTERNS_unbiased.md`

## Acceptance Criteria

- [ ] Create reshaping prompt/agent that applies style guide to existing content
- [ ] Process existing scenes through style transformation
- [ ] Validate transformed content:
  - [ ] POV converted to second person
  - [ ] Dialogue ratio adjusted to 27-50%
  - [ ] Sentence rhythm matches reference patterns
  - [ ] Italicized internal monologue added appropriately
- [ ] Store reshaped content in `fine-tuning/data/reshaped/`
- [ ] Compare original vs reshaped for quality assurance
- [ ] Convert to JSONL format for training

## Transformation Rules

**From → To:**
- Third person → Second person POV
- Generic dialogue tags → Minimal attribution pattern
- Exposition blocks → Integrated worldbuilding
- Direct emotion statements → Physical manifestation
- Neutral narration → Philosophical undertone

## Output Location

`fine-tuning/data/reshaped/` (mirrors raw/ structure)

## Notes

This reuses existing plot content with style transformation. For entirely new content generation, see Task 007.
