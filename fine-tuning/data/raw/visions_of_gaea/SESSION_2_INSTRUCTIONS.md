# Session 2 Instructions: Chunking Memories 6-8

**Date Started:** 2025-11-21
**Current Progress:** 13/~45 chunks complete (29%)
**Mode:** book-curator

---

## Quick Start for New Chat Session

When starting the new chat session, provide this context:

```
I'm continuing the chunking process for "Visions of Gaea - Ascension Part 1" manuscript.

Session 1 completed: Prologue + Memories 1-5 (13 chunks created)
Now starting Session 2: Memories 6-8

Working directory: ~/scifi-llm/fine-tuning/data/raw/visions_of_gaea/

Please continue in book-curator mode and:
1. Read SESSION_1_REPORT.md for context
2. Chunk Memory 6 (lines 672-757)
3. Chunk Memory 7 (lines 758-828)
4. Chunk Memory 8 (lines 829-988)
5. Generate SESSION_2_REPORT.md when complete

proceed
```

---

## Session 2 Scope

### Memory 6: Tales of the long departed
- **Lines:** 672-757 (86 lines)
- **Estimated:** ~1,500-2,000 words
- **Strategy:** Likely 1-2 chunks depending on scene breaks
- **Content:** Demography indoctrination, odyrs discussion, mentor conflict

### Memory 7: Mother
- **Lines:** 758-828 (71 lines)
- **Estimated:** ~1,300-1,800 words
- **Strategy:** Likely 1-2 chunks
- **Content:** Alan's evening at home, accessing the Source, interaction with Evander/Hampy

### Memory 8: Desperate Measures
- **Lines:** 829-988 (160 lines)
- **Estimated:** ~3,000-3,500 words
- **Strategy:** 2-3 chunks (contains scene break markers `***`)
- **Content:** Von Howitt's escape with specimen A, Mentalist Vittas confrontation
- **Note:** Check for `***` markers to find natural split points

---

## Chunking Guidelines Reminder

### Target Metrics
- **Minimum:** 800 words
- **Ideal range:** 1,200-1,500 words
- **Maximum:** 2,100 words

### Prioritized Break Points
1. Memory boundaries (strongest)
2. Scene breaks (`***` markers)
3. POV character shifts
4. Location/time changes
5. Tonal shifts (action → introspection)

### Quality Checks
- Each chunk must be a complete narrative unit
- No orphaned references (character/term first mentions need context)
- Complete dialogue exchanges
- Sufficient context for standalone reading

---

## Files to Reference

- `ascension_part_1_manuscript.txt` - Source manuscript
- `MANUSCRIPT_ANALYSIS.md` - Structure analysis (11 memories + prologue)
- `SESSION_1_REPORT.md` - What was completed in Session 1
- Existing chunks: `chunk_001` through `chunk_013`

---

## Expected Outputs

### New Chunk Files
- `chunk_014_ch06_*.txt` (Memory 6 start)
- `chunk_015_ch06_*.txt` or `chunk_015_ch07_*.txt` (depending on split)
- `chunk_016_ch07_*.txt` through `chunk_0XX_ch08_*.txt`

### Session Report
- `SESSION_2_REPORT.md` (similar format to SESSION_1_REPORT.md)

---

## Session 2 Success Criteria

✅ Memories 6-8 fully chunked (estimated 8-12 chunks)
✅ All chunks within 800-2,100 word range
✅ Natural narrative boundaries respected
✅ SESSION_2_REPORT.md generated
✅ SESSION_3_INSTRUCTIONS.md created for next session

---

## Notes for Next Agent

- **Oversized chunks from Session 1:** Consider splitting if they cause issues:
  - chunk_001 (2,179 words) - Prologue is naturally long, likely OK
  - chunk_006 (2,343 words) - Shelter arrival scene
  - chunk_007 (2,130 words) - Race prep, may be fine
  - chunk_013 (2,570 words) - Torment science, consider splitting if time permits

- **Memory 8 specifics:** Contains Von Howitt's escape narrative with multiple perspectives and action sequences. Use scene breaks to maintain tension/pacing.

- **Estimated completion time:** Session 2 should take 10-15 minutes of processing time (your time, not user wait time)
