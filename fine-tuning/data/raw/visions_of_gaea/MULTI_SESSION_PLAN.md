# Visions of Gaea Curation - Multi-Session Plan

**Manuscript:** Ascension Part 1 (62,884 words)
**Target Output:** ~45 chunks @ 1,200-1,500 words each
**Chunking Method:** Respect narrative boundaries (memories → scene breaks → natural pauses)

---

## Session Breakdown

### ✅ Session 1: COMPLETE (2025-11-21)
**Scope:** Prologue + Memories 1-5
**Output:** 13 chunks, 24,012 words
**Status:** Complete with 4 slightly oversized chunks (acceptable)
**Report:** `SESSION_1_REPORT.md`

### 📋 Session 2: Memories 6-8
**Estimated:** 8-12 chunks
**Complexity:** Medium (Memory 8 has action sequences with scene breaks)
**Instructions:** `SESSION_2_INSTRUCTIONS.md`
**Start prompt:** See SESSION_2_INSTRUCTIONS.md

### 📋 Session 3: Memory 9 + Start Memory 10
**Estimated:** 8-10 chunks
**Complexity:** High (Memory 10 is 323 lines - "The Gathering")
**Note:** Split Memory 10 across Sessions 3-4 for manageability

### 📋 Session 4: Complete Memory 10 + Memory 11
**Estimated:** 12-14 chunks
**Complexity:** Very High (Memory 11 is 354 lines - "Fugitives in Darm" with combat)
**Note:** Both memories have multiple POV shifts and action sequences

### 📋 Session 5: Finalization
**Estimated:** 1 epilogue chunk + cleanup
**Tasks:**
- Add Epilogue (Prelude to Ascension)
- Review all chunks for quality
- Merge/split any problematic chunks
- Generate CHUNK_METADATA.json
- Create CURATION_REPORT.md

---

## How to Resume

### Starting Any New Session:

1. **Open new chat with GitHub Copilot**
2. **Provide context:**
   ```
   Continuing Visions of Gaea manuscript curation.
   Working directory: ~/scifi-llm/fine-tuning/data/raw/visions_of_gaea/
   
   Please switch to book-curator mode and read:
   - SESSION_[X]_INSTRUCTIONS.md (current session)
   - SESSION_[X-1]_REPORT.md (previous session results)
   
   Then proceed with chunking as specified.
   ```

3. **Agent will:**
   - Read instruction file
   - Review previous progress
   - Execute chunking for assigned memories
   - Generate session report
   - Create instructions for next session

---

## Files Structure

```
fine-tuning/data/raw/visions_of_gaea/
├── ascension_part_1_manuscript.txt          # Source
├── MANUSCRIPT_ANALYSIS.md                   # Structure analysis
├── MULTI_SESSION_PLAN.md                    # This file
│
├── SESSION_1_REPORT.md                      # ✅ Complete
├── SESSION_2_INSTRUCTIONS.md                # 📋 Next session
│
├── chunk_001_prologue_awakening.txt         # ✅
├── chunk_002_ch01_history_class.txt         # ✅
├── ... (chunks 003-013)                     # ✅
├── chunk_014_ch06_*.txt                     # 📋 Session 2
├── ... (future chunks)
│
├── CHUNK_METADATA.json                      # 📋 Session 5
└── CURATION_REPORT.md                       # 📋 Session 5
```

---

## Quality Standards (All Sessions)

### Chunk Size Targets
- ✅ Ideal: 1,200-1,500 words
- ✅ Acceptable: 800-2,100 words
- ⚠️ Flag for review: < 800 or > 2,100 words

### Narrative Integrity
- ✅ Complete scenes or meaningful segments
- ✅ No mid-dialogue splits
- ✅ No orphaned character/concept introductions
- ✅ Sufficient context for standalone reading

### Special Considerations
- **Second-person POV:** Maintain "you" perspective integrity
- **Worldbuilding terms:** Keep first mentions with context
- **Scene breaks (`***`):** Prioritize as split points
- **Framing device:** Keep mystical commentary with related content

---

## Expected Timeline

- **Session 1:** ✅ Complete (13 chunks)
- **Session 2:** ~10-15 minutes (Memories 6-8)
- **Session 3:** ~15-20 minutes (Memory 9 + partial 10)
- **Session 4:** ~20-25 minutes (Complete 10 + Memory 11)
- **Session 5:** ~10-15 minutes (Epilogue + metadata + report)

**Total estimated:** ~70-90 minutes of agent processing time across 5 sessions

---

## Success Criteria (Final)

✅ 40-48 chunks created
✅ 90%+ chunks in 800-2,100 word range
✅ All memories properly segmented
✅ CHUNK_METADATA.json with complete data
✅ CURATION_REPORT.md with statistics and integration instructions
✅ Ready for `1_prepare_data.py` processing

---

## Contact Points

If issues arise:
1. Check session instruction files for guidance
2. Refer to MANUSCRIPT_ANALYSIS.md for structure
3. Review previous session reports for consistency
4. Flag problematic sections in session report for user review

---

**Next Action:** Start Session 2 with instructions in `SESSION_2_INSTRUCTIONS.md`
