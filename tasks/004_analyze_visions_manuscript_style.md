# Analyze Visions of Gaea Manuscript Style

**Priority:** 2  
**State:** Open  
**Created:** 2025-11-24  
**Depends On:** Task 002 (Completed)

## Description

Extract comprehensive narrative style patterns from the Visions of Gaea manuscript using the style-analyzer agent. The full manuscript (62,884 words) causes timeout issues when analyzed as a single document. Break the manuscript into manageable sections and accumulate the analysis to create a complete style transfer guide.

## Problem

**Current Issue:**
- style-analyzer agent times out when processing the complete manuscript
- 62,884 words exceeds reasonable processing time/token limits
- Need style analysis to generate training data with style-transfer-generator

**Impact:**
- Cannot proceed with style-matched training data generation
- Blocks expansion of training dataset beyond 35 curated chunks
- Limits ability to use style-analyzer + style-transfer-generator workflow

## Proposed Solution

**Multi-Section Analysis Approach:**
1. Split manuscript into 3 approximately equal sections (~21k words each)
2. Run style-analyzer on each section independently
3. Accumulate and merge the style patterns across all sections
4. Generate unified STYLE_TRANSFER_GUIDE.md combining all analyses

**Why 3 sections:**
- ~21,000 words per section is manageable for agent processing
- Provides good coverage across narrative arc (beginning, middle, end)
- Small enough to avoid timeouts, large enough to capture style patterns
- Represents different story phases (setup, action, climax/resolution)

## Acceptance Criteria

### 1. Manuscript Segmentation
- [ ] Split `ascension_part_1_manuscript.txt` into 3 sections
- [ ] Section 1: Lines 1-606 (~21k words) - Prologue through Memory 5
- [ ] Section 2: Lines 607-1212 (~21k words) - Memories 6-9
- [ ] Section 3: Lines 1213-1818 (~21k words) - Memories 10-11 + Epilogue
- [ ] Save sections to `fine-tuning/data/styles/visions_of_gaea/manuscript_sections/`
- [ ] Verify total word count matches original (62,884 words)

### 2. Section 1 Analysis (Setup Phase)
- [ ] Run style-analyzer on section 1
- [ ] Generate `section_1_STYLE_GUIDE.md`
- [ ] Extract `section_1_STYLE_STATISTICS.json`
- [ ] Document patterns from prologue and early worldbuilding
- [ ] Verify analysis completes without timeout

### 3. Section 2 Analysis (Development Phase)
- [ ] Run style-analyzer on section 2
- [ ] Generate `section_2_STYLE_GUIDE.md`
- [ ] Extract `section_2_STYLE_STATISTICS.json`
- [ ] Document patterns from action and conflict development
- [ ] Compare vocabulary/metrics with section 1

### 4. Section 3 Analysis (Climax/Resolution)
- [ ] Run style-analyzer on section 3
- [ ] Generate `section_3_STYLE_GUIDE.md`
- [ ] Extract `section_3_STYLE_STATISTICS.json`
- [ ] Document patterns from climax and transformation scenes
- [ ] Compare with sections 1-2 for consistency

### 5. Pattern Accumulation
- [ ] Merge vocabulary lists from all 3 sections
- [ ] Calculate aggregate statistics (avg sentence length, etc.)
- [ ] Identify patterns present across all sections (consistent style)
- [ ] Identify section-specific patterns (pacing/tone shifts)
- [ ] Create unified pattern catalog

### 6. Unified Style Guide Generation
- [ ] Combine analyses into single `STYLE_TRANSFER_GUIDE.md`
- [ ] Include examples from all 3 sections
- [ ] Aggregate statistics in `STYLE_STATISTICS.json`
- [ ] Document style evolution across narrative (if any)
- [ ] Create `STYLE_PATTERNS.md` with comprehensive pattern list

### 7. Validation
- [ ] Verify guide covers all 10 analysis domains
- [ ] Check consistency of identified patterns
- [ ] Ensure vocabulary coverage is comprehensive
- [ ] Validate metrics align with curation report findings
- [ ] Test guide with style-transfer-generator on sample prompt

### 8. Documentation
- [ ] Document segmentation methodology
- [ ] Record any style variations between sections
- [ ] Note strengths/limitations of accumulated approach
- [ ] Save section analyses to archives for reference

## Technical Specifications

### Manuscript Sections

**Section 1: Prologue through Memory 5 (Lines 1-606)**
- Approx 21,000 words
- Coverage: Awakening, history class, morning discussion, racing, retreat, Torment science
- Narrative phase: Setup and worldbuilding introduction
- Key elements: POV establishment, technical terminology introduction, character voice setup

**Section 2: Memories 6-9 (Lines 607-1212)**
- Approx 21,000 words
- Coverage: Lunch, Mother hacking, specimen retrieval, morning ride, Odyr lesson
- Narrative phase: Development and conflict escalation
- Key elements: Action sequences, philosophical depth, relationship dynamics

**Section 3: Memories 10-11 + Epilogue (Lines 1213-1818)**
- Approx 20,884 words
- Coverage: The Gathering, Hub infiltration, chase, battle, transformation, death, transcendence
- Narrative phase: Climax and resolution
- Key elements: Intense action, emotional restraint in dramatic scenes, transformation prose

### Line Count Calculation
```bash
# Total lines: 1,818
# Section 1: lines 1-606 (33%)
# Section 2: lines 607-1212 (33%)
# Section 3: lines 1213-1818 (34%)
```

### Directory Structure
```
fine-tuning/data/styles/visions_of_gaea/
├── manuscript_sections/
│   ├── section_1_prologue_to_memory5.txt
│   ├── section_2_memory6_to_memory9.txt
│   └── section_3_memory10_to_epilogue.txt
├── section_analyses/
│   ├── section_1_STYLE_GUIDE.md
│   ├── section_1_STYLE_STATISTICS.json
│   ├── section_1_STYLE_PATTERNS.md
│   ├── section_2_STYLE_GUIDE.md
│   ├── section_2_STYLE_STATISTICS.json
│   ├── section_2_STYLE_PATTERNS.md
│   ├── section_3_STYLE_GUIDE.md
│   ├── section_3_STYLE_STATISTICS.json
│   └── section_3_STYLE_PATTERNS.md
├── STYLE_TRANSFER_GUIDE.md (unified)
├── STYLE_STATISTICS.json (accumulated)
└── STYLE_PATTERNS.md (comprehensive)
```

## Workflow Steps

### Step 1: Create Directory Structure
```bash
cd fine-tuning/data/styles
mkdir -p visions_of_gaea/{manuscript_sections,section_analyses}
```

### Step 2: Split Manuscript into Sections
```bash
cd fine-tuning/data/raw/visions_of_gaea

# Section 1: Lines 1-606
head -606 ascension_part_1_manuscript.txt > \
  ../../styles/visions_of_gaea/manuscript_sections/section_1_prologue_to_memory5.txt

# Section 2: Lines 607-1212
sed -n '607,1212p' ascension_part_1_manuscript.txt > \
  ../../styles/visions_of_gaea/manuscript_sections/section_2_memory6_to_memory9.txt

# Section 3: Lines 1213-1818
tail -n +1213 ascension_part_1_manuscript.txt > \
  ../../styles/visions_of_gaea/manuscript_sections/section_3_memory10_to_epilogue.txt

# Verify word counts
wc -w ../../styles/visions_of_gaea/manuscript_sections/*.txt
```

### Step 3: Analyze Section 1
```
@style-analyzer Analyze the style of section 1 (Prologue through Memory 5) from 
fine-tuning/data/styles/visions_of_gaea/manuscript_sections/section_1_prologue_to_memory5.txt 
and save analysis to fine-tuning/data/styles/visions_of_gaea/section_analyses/ 
with prefix "section_1_"
```

### Step 4: Analyze Section 2
```
@style-analyzer Analyze the style of section 2 (Memories 6-9) from 
fine-tuning/data/styles/visions_of_gaea/manuscript_sections/section_2_memory6_to_memory9.txt 
and save analysis to fine-tuning/data/styles/visions_of_gaea/section_analyses/ 
with prefix "section_2_"
```

### Step 5: Analyze Section 3
```
@style-analyzer Analyze the style of section 3 (Memories 10-11 + Epilogue) from 
fine-tuning/data/styles/visions_of_gaea/manuscript_sections/section_3_memory10_to_epilogue.txt 
and save analysis to fine-tuning/data/styles/visions_of_gaea/section_analyses/ 
with prefix "section_3_"
```

### Step 6: Accumulate Analyses (Manual or Script-Assisted)
```bash
# Compare vocabulary across sections
cd fine-tuning/data/styles/visions_of_gaea/section_analyses

# Extract common patterns
# Merge statistics
# Create unified guide

# Or use custom accumulation script (to be created if needed)
```

### Step 7: Generate Unified Guide
Create `STYLE_TRANSFER_GUIDE.md` combining:
- POV patterns (should be consistent: second-person)
- Vocabulary (union of all section vocabularies)
- Sentence structures (averaged metrics with ranges)
- Dialogue patterns (examples from all sections)
- Description styles (sensory detail approach)
- Pacing variations (note differences between setup/action/climax)
- Worldbuilding integration (technical term usage)
- Tone (emotional restraint patterns)
- Character voice (Alan's consistent voice)
- Technical choices (italics, ***, tense)

### Step 8: Validate with Generator
```
@style-transfer-generator Generate 1 test scene using the unified "visions_of_gaea" 
style guide to verify completeness and accuracy
```

## Success Metrics

### Processing Success
- ✅ All 3 sections analyzed without timeout
- ✅ Each section produces complete style guide
- ✅ Statistics extracted for all sections
- ✅ Patterns identified consistently

### Style Consistency
- **POV:** 95%+ second-person across all sections
- **Vocabulary:** 70%+ overlap in core narrative terms
- **Sentence Structure:** Avg length within ±10% across sections
- **Patterns:** 80%+ of identified patterns present in 2+ sections

### Guide Completeness
- ✅ Covers all 10 analysis domains
- ✅ Includes examples from each narrative phase
- ✅ Vocabulary list contains 200+ distinctive terms
- ✅ Metrics match curation report findings (1,809 avg words/chunk)

### Usability
- ✅ style-transfer-generator successfully uses unified guide
- ✅ Generated scenes match source manuscript style
- ✅ Guide provides actionable writing instructions

## Alternative Approaches Considered

### Option A: Use Curated Chunks (Rejected)
- **Pro:** Chunks already exist, pre-validated
- **Con:** 35 separate analyses would be fragmented
- **Con:** Harder to accumulate patterns across many small files
- **Reason for rejection:** Too granular, doesn't capture narrative flow

### Option B: Analyze Memories Individually (Less Optimal)
- **Pro:** Natural narrative boundaries
- **Con:** 11+ separate analyses to merge
- **Con:** Some memories are very short (<2k words)
- **Reason for rejection:** Too many small analyses, uneven sizes

### Option C: Two Sections (Considered)
- **Pro:** Fewer analyses to merge
- **Con:** ~31k words per section may still timeout
- **Con:** Less granular coverage of narrative arc
- **Reason for rejection:** Risk of timeouts still present

### Option D: Selected Passages (Rejected)
- **Pro:** Could pick representative examples
- **Con:** May miss important style patterns
- **Con:** Sampling bias
- **Reason for rejection:** Not comprehensive enough

**Chosen: Three Equal Sections** - Best balance of processing feasibility, narrative coverage, and manageable accumulation.

## Dependencies

**Completed:**
- ✅ Task 002: Visions of Gaea curation (provides source manuscript)
- ✅ style-analyzer agent available
- ✅ style-transfer-generator agent available (for validation)

**Required:**
- Source manuscript: `fine-tuning/data/raw/visions_of_gaea/ascension_part_1_manuscript.txt`
- Storage space: ~500KB for section files + analyses
- Agent processing time: ~30-60 minutes per section (estimated)

## Troubleshooting

### Section Still Times Out
- Split further into 6 sections (~10k words each)
- Use even smaller chunks (by memory, 5k-8k words)
- Process most critical sections only (e.g., skip epilogue)

### Inconsistent Patterns Across Sections
- Normal for narrative arc progression
- Document variations in unified guide
- Note pacing shifts (setup → climax)
- Treat as style evolution, not inconsistency

### Accumulated Guide Too Complex
- Prioritize patterns present in 2+ sections
- Omit section-specific quirks
- Focus on core style elements (POV, voice, worldbuilding)
- Simplify to essential writing instructions

### Generator Can't Use Unified Guide
- Guide may be too detailed
- Condense to key patterns only
- Provide clearer examples
- Test iteratively with simpler prompts

## Related Files

### Source Material
- **Manuscript:** `fine-tuning/data/raw/visions_of_gaea/ascension_part_1_manuscript.txt`
- **Curation Report:** `docs/archives/002_visions_of_gaea_curation/CURATION_REPORT.md`
- **Chunks:** `fine-tuning/data/raw/visions_of_gaea/chunk_*.txt` (35 files)

### Output Location
- **Sections:** `fine-tuning/data/styles/visions_of_gaea/manuscript_sections/`
- **Section Analyses:** `fine-tuning/data/styles/visions_of_gaea/section_analyses/`
- **Unified Guide:** `fine-tuning/data/styles/visions_of_gaea/STYLE_TRANSFER_GUIDE.md`

### Agents
- **Analyzer:** `.github/agents/style-analyzer.md`
- **Generator:** `.github/agents/style-transfer-generator.md` (for validation)

### Documentation
- **Style Library:** `fine-tuning/data/styles/README.md`
- **Agent Workflow:** `docs/history/2025-11-22_style_transfer_agents.md`

## Notes

### Timeline Estimate
- Manuscript splitting: ~5 minutes
- Section 1 analysis: ~30-60 minutes (agent processing)
- Section 2 analysis: ~30-60 minutes
- Section 3 analysis: ~30-60 minutes
- Pattern accumulation: ~30-60 minutes (manual review and merging)
- Unified guide creation: ~30 minutes
- Validation test: ~15 minutes
- **Total:** 3-5 hours (mostly agent processing time)

### Pattern Accumulation Strategy

**For consistent patterns (should match across sections):**
- POV (second-person "you")
- Italics usage (internal monologue)
- Scene break markers (***)
- Technical terminology
- Emotional restraint

**For variable patterns (may differ by section):**
- Pacing (faster in action, slower in exposition)
- Dialogue density (higher in social scenes)
- Description detail (more in worldbuilding, less in action)
- Tone (wonder → fear → transcendence)

**Accumulation approach:**
- **Union** for vocabulary (collect all unique terms)
- **Average** for metrics (sentence length, paragraph size)
- **Common patterns** for style markers (present in 2+ sections)
- **Range** for variable elements (min-max pacing)

### Post-Completion Actions
- Update task status to "Completed"
- Archive section analyses for reference
- Use unified guide with style-transfer-generator to create training data
- Document any limitations or section-specific findings
- Consider applying same approach to future manuscripts

### Future Enhancements
- Automate accumulation with Python script
- Create section comparison tool (highlights differences)
- Develop pattern weighting system (more important patterns scored higher)
- Build style consistency checker (validates generated scenes against guide)
