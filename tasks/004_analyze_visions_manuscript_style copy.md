# Analyze Visions of Gaea Manuscript Style

**Priority:** 2  
**State:** In Progress  
**Created:** 2025-11-24  
**Updated:** 2025-11-29  
**Depends On:** Task 002 (Completed)

## Description

Extract comprehensive narrative style patterns from the Visions of Gaea manuscript using the style-analyzer agent. The full manuscript (62,884 words) causes timeout issues when analyzed as a single document. Break the manuscript into manageable sections and accumulate the analysis to create a complete style transfer guide.

## Current Progress

### Completed Steps
- ✅ Manuscript split into 3 sections (~21k words each)
- ✅ Section analyses completed via 3 parallel approaches:
  - `styleTransfer/analyzer_biased` - Standard style-analyzer with examples
  - `styleTransfer/analyzer_unbiased` - Unbiased analyzer without pre-conditioning
  - `styleTransfer/analyzer_templated` - Template-guided analyzer
- ✅ All 9 section analyses available (3 sections × 3 prompts)
- ✅ Results merged into 3 branches (one per prompt approach)

### Next Step: Merge Section Analyses
Use the new **style-merger** agent to combine section analyses into unified guide.

**Agent:** `.github/agents/style-merger.md`

**Branches with section analyses:**
- `remotes/origin/styleTransfer/analyzer_biased`
- `remotes/origin/styleTransfer/analyzer_unbiased`
- `remotes/origin/styleTransfer/analyzer_templated`

### Merge Workflow (×3 branches)
```
# For each branch:
1. Checkout branch section_analyses/ to local
2. Invoke style-merger agent
3. Verify unified outputs
4. Compare results across the 3 branches
5. Select best unified guide or synthesize
```

## Problem

**Original Issue:**
- style-analyzer agent times out when processing the complete manuscript
- 62,884 words exceeds reasonable processing time/token limits
- Need style analysis to generate training data with style-transfer-generator

**Solution Implemented:**
- Split manuscript into 3 sections (~21k words each)
- Ran 3 parallel analysis approaches (biased, unbiased, templated)
- Created style-merger agent for combining results

## Acceptance Criteria

### 1. Manuscript Segmentation ✅ COMPLETED
- [x] Split `ascension_part_1_manuscript.txt` into 3 sections
- [x] Section 1: Lines 1-606 (~21k words) - Prologue through Memory 5
- [x] Section 2: Lines 607-1212 (~21k words) - Memories 6-9
- [x] Section 3: Lines 1213-1818 (~21k words) - Memories 10-11 + Epilogue
- [x] Save sections to `fine-tuning/data/styles/visions_of_gaea/manuscript_sections/`
- [x] Verify total word count matches original (62,884 words)

### 2. Section Analyses ✅ COMPLETED (3 approaches)
- [x] Run style-analyzer on all 3 sections
- [x] Generate section-specific STYLE_GUIDE.md files
- [x] Extract section-specific STYLE_STATISTICS.json files
- [x] Generate section-specific STYLE_PATTERNS.md files
- [x] Results available in 3 branches (biased, unbiased, templated)

### 3. Pattern Accumulation (style-merger agent)
- [ ] Run style-merger on `styleTransfer/analyzer_biased` branch
- [ ] Run style-merger on `styleTransfer/analyzer_unbiased` branch
- [ ] Run style-merger on `styleTransfer/analyzer_templated` branch
- [ ] Compare unified guides from all 3 approaches
- [ ] Select or synthesize best unified guide

### 4. Unified Style Guide Generation
- [ ] Create final `STYLE_TRANSFER_GUIDE.md`
- [ ] Create final `STYLE_STATISTICS.json`
- [ ] Create final `STYLE_PATTERNS.md`
- [ ] Merge to main branch

### 5. Validation
- [ ] Verify guide covers all 10 analysis domains
- [ ] Check consistency of identified patterns
- [ ] Ensure vocabulary coverage is comprehensive
- [ ] Test guide with style-transfer-generator on sample prompt

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

### Completed Steps (1-5)
Section splitting and analysis already done. See branches:
- `remotes/origin/styleTransfer/analyzer_biased`
- `remotes/origin/styleTransfer/analyzer_unbiased`
- `remotes/origin/styleTransfer/analyzer_templated`

### Step 6: Merge Section Analyses (Current Step)

**For each of the 3 branches:**

```bash
# 1. Checkout section analyses from branch
cd /home/ruifrvaz/scifi-llm
git checkout remotes/origin/styleTransfer/analyzer_biased -- \
  fine-tuning/data/styles/visions_of_gaea/section_analyses/

# 2. Invoke style-merger agent
@style-merger Merge the section analyses for "visions_of_gaea" style 
from fine-tuning/data/styles/visions_of_gaea/section_analyses/ 
into unified guide files in fine-tuning/data/styles/visions_of_gaea/

# 3. Save results (e.g., copy to branch-specific folder or commit)
# 4. Reset and repeat for next branch
git checkout -- fine-tuning/data/styles/visions_of_gaea/
```

### Step 7: Compare and Select Best Guide

After running merger on all 3 branches:
1. Compare unified guides from each approach
2. Evaluate: consistency, completeness, actionability
3. Select best guide OR synthesize from multiple
4. Commit final unified guide to main

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
- **Analyzer (Unbiased):** `.github/agents/style-analyzer-unb.md`
- **Merger:** `.github/agents/style-merger.md` (NEW)
- **Generator:** `.github/agents/style-transfer-generator.md` (for validation)

### Documentation
- **Style Library:** `fine-tuning/data/styles/README.md`
- **Accumulation Reference:** `fine-tuning/data/styles/visions_of_gaea/ACCUMULATION_TEMPLATE.md`
- **Agent Workflow:** `docs/history/2025-11-22_style_transfer_agents.md`

## Notes

### Timeline Estimate (Updated)
- ~~Manuscript splitting: ~5 minutes~~ ✅ Done
- ~~Section analyses: ~2-3 hours~~ ✅ Done (9 runs completed)
- **Merge analyses (×3 branches): ~30-60 minutes** ← Current step
- Compare and select: ~15-30 minutes
- Validation test: ~15 minutes
- **Remaining Total:** ~1-2 hours

### Available Section Analyses

**Branch: styleTransfer/analyzer_biased**
- Uses standard style-analyzer with embedded Visions of Gaea examples
- May bias toward expected patterns

**Branch: styleTransfer/analyzer_unbiased**
- Uses style-analyzer-unb without pre-conditioning
- Should extract patterns purely from manuscript content

**Branch: styleTransfer/analyzer_templated**
- Uses template-guided approach
- Structured analysis with consistent output format

### Merge Strategy

Use **style-merger** agent (`.github/agents/style-merger.md`):
1. Reads all 9 section files (3 sections × 3 file types)
2. Calculates weighted averages for metrics
3. Identifies patterns by frequency (all/2/1 sections)
4. Produces unified guide with prioritized directives

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
