# Style Transfer Agent System

**Date:** November 22, 2025  
**Purpose:** Created tandem agent workflow for analyzing manuscript style and generating matching training data

## Overview

Built two-agent system for fine-tuning personal writing style:
1. **style-analyzer** - Extracts narrative patterns from original manuscripts
2. **style-transfer-generator** - Creates diverse training scenes matching extracted style

Added unbiased analyzer variant for benchmarking without pre-conditioning.

## Problem Solved

**Challenge:** Fine-tuning requires large, diverse datasets in target style. Can't use only original manuscript (overfitting risk). Need 50-100+ scenes across multiple story universes that match author's voice exactly.

**Solution:** Automated workflow that analyzes any manuscript's stylistic fingerprint, then generates training data matching those patterns across independent story universes.

## Components Created

### 1. Style Analyzer Agent (`.github/agents/style-analyzer.md`)

**Purpose:** Deep narrative style extraction across 10 analysis domains

**Analysis Domains:**
- POV & Narrative Distance
- Prose Rhythm & Sentence Structure
- Dialogue Patterns
- Description Style
- Pacing & Information Flow
- Chapter/Scene Structure
- Worldbuilding Integration
- Tone & Emotional Register
- Character Voice Differentiation
- Technical Choices (tense, formatting, typography)

**Outputs** (saved to `fine-tuning/data/styles/[name]/`):
- `STYLE_TRANSFER_GUIDE.md` - Complete style specification with examples
- `STYLE_STATISTICS.json` - Quantitative metrics (sentence lengths, vocabulary, dialogue ratios)
- `STYLE_PATTERNS.md` - Identified recurring patterns and techniques

**Features:**
- Vocabulary fingerprinting (word frequency, rare word density, technical terms)
- Quantitative metrics (sentence length ranges, paragraph sizes, dialogue percentages)
- Pattern recognition (recurring phrases, structural templates, sensory emphasis)
- Example extraction from source manuscript for reference

### 2. Style Transfer Generator Agent (`.github/agents/style-transfer-generator.md`)

**Purpose:** Generate training data matching analyzed style guide

**Core Workflow:**
1. Read `STYLE_TRANSFER_GUIDE.md` from specified style
2. Design independent story universes (varied genres, settings, conflicts)
3. Plan diverse scene types (crisis, introspection, conflict, discovery, problem-solving)
4. Generate 800-2,100 word scenes matching guide metrics ±10%
5. Validate each scene against style specifications
6. Repeat across multiple universes for diversity

**Quality Controls:**
- Per-scene validation (POV consistency, metric matching, style fidelity)
- Per-universe validation (internal consistency, no character name conflicts)
- Cross-universe validation (style homogeneity, no voice drift)

**Prevents Overfitting:**
- Multiple independent story universes (user-determined count)
- No character name duplication across universes
- Setting/conflict/theme variety
- Scene type balance (not all action, not all dialogue)

**Outputs** (saved to `fine-tuning/data/styles/[name]/generated/`):
- Individual markdown files per scene
- Organized by universe for tracking
- Ready for `training/1_prepare_data.py` processing

**Initial Specs:**
- Originally: 833 lines, 4,285 words, ~5,570 tokens
- Optimized: 531 lines (36% reduction) by condensing examples
- Hard constraints removed: Universe counts and genre types now flexible

### 3. Unbiased Style Analyzer (`.github/agents/style-analyzer-unbiased.md`)

**Purpose:** Benchmarking version without pre-conditioning examples

**Key Differences from Standard Analyzer:**
- No Visions of Gaea examples embedded
- Generic placeholder text in templates
- Empty vocabulary/pattern sections
- Tests analytical capability without bias

**Use Case:** Validate that analyzer extracts patterns from manuscript itself, not from embedded examples. Enables A/B comparison of analysis quality.

### 4. Style Library Documentation (`fine-tuning/data/styles/README.md`)

**Documents:**
- Directory structure for style analyses
- Workflow integration with training pipeline
- Difference between `raw/` (original text) and `styles/` (analysis + generated)
- Example usage patterns

## Directory Structure Changes

```
fine-tuning/
├── data/
│   ├── raw/               # Original manuscript chunks (book-curator output)
│   ├── styles/            # NEW: Style analyses and generated training data
│   │   ├── README.md      # Style library documentation
│   │   └── [style_name]/  # Per-style analysis
│   │       ├── STYLE_TRANSFER_GUIDE.md
│   │       ├── STYLE_STATISTICS.json
│   │       ├── STYLE_PATTERNS.md
│   │       └── generated/ # Generated training scenes
│   │           └── universe_*/
```

## Usage Workflow

### Step 1: Analyze Manuscript Style
```
@style-analyzer Analyze the style of "Visions of Gaea" manuscript from fine-tuning/data/raw/ and save as "visions_of_gaea" style
```
**Output:** Complete style guide in `styles/visions_of_gaea/`

### Step 2: Generate Training Data
```
@style-transfer-generator Generate training data for "visions_of_gaea" style across multiple universes
```
**Output:** Scenes across independent story universes in `styles/visions_of_gaea/generated/`

### Step 3: Prepare Combined Dataset
```bash
cd fine-tuning/training
./1_prepare_data.py
# Processes both raw/ and styles/*/generated/ into training format
```

### Step 4: Train Model
```bash
./2_train_lora.sh
# Fine-tunes on combined dataset (original + generated)
```

### Step 5: Benchmark
```bash
cd ../benchmarks
python 1_voice_comparison.py
# Measures style transfer quality (target: >70% match)
```

## Technical Decisions

### Flexible Constraints
**Changed:** Removed hard requirements for 5-8 universes and 50-100 scenes  
**Rationale:** User needs flexibility based on training goals. Some projects need 30 scenes, others need 150+. Genre variety should be user-determined, not prescriptive.

**Implementation:**
- "Multiple universes" instead of "5-8 universes"
- "Sufficient for training needs" instead of "50-100 scenes"
- "User-determined genres" instead of specific genre recommendations

### Size Optimization
**Problem:** Original generator agent was 833 lines (4,285 words, ~5,570 tokens)  
**Solution:** Condensed examples from verbose demonstrations to concise principles  
**Result:** 531 lines (36% reduction), estimated ~3,500 tokens

**Approach:**
- Reduced example sizes, not specifications
- Changed multi-line code blocks to single-line summaries
- Condensed workflow walkthroughs to essential steps
- All capabilities preserved

### Unbiased Analysis Variant
**Problem:** Examples in standard analyzer could bias pattern detection  
**Solution:** Created separate unbiased version with no embedded examples  
**Use Case:** Benchmarking to validate analyzer extracts patterns from input manuscript, not from internal examples

## Integration Points

### With Book Curator
- Curator outputs to `data/raw/` (original manuscript chunks)
- Analyzer reads from `data/raw/` to extract style
- Generator outputs to `data/styles/[name]/generated/`
- Training script processes both directories

### With Fine-Tuning Pipeline
- `1_prepare_data.py` discovers all markdown in `raw/` and `styles/*/generated/`
- Converts to JSONL format for Axolotl
- Combines original manuscript with generated style-matched content
- Prevents overfitting while maintaining style fidelity

### With Benchmarking
- `1_voice_comparison.py` measures style transfer quality
- Compares baseline model vs. fine-tuned model
- Metrics: Vocabulary overlap, sentence structure, style markers, tone
- Target: >60% style match for production, >70% ideal

## Expected Outcomes

### Before Style Transfer Workflow
- Training on 19 chunks from Visions of Gaea (34,807 words)
- Risk: Overfitting to specific plot/characters
- Expected style match: 45-55%

### After Style Transfer Workflow
- Training on 19 original chunks + 50-100+ generated scenes
- Total corpus: 100,000+ words across diverse content
- Expected style match: >70% (improved generalization)
- Model learns "how to write like author" not "how to write Visions of Gaea"

## Next Steps

1. **Test analyzer on Visions of Gaea manuscript** - Extract complete style guide
2. **Benchmark unbiased vs. biased analyzer** - Validate pattern extraction quality
3. **Generate training data** - Create 50-100 scenes across multiple universes
4. **Complete manuscript curation** - Finish Task 002 (currently 42% complete)
5. **Full training run** - Combine original + generated (121+ total chunks)
6. **Validate results** - Benchmark fine-tuned model with `1_voice_comparison.py`

## Files Modified

**Created:**
- `.github/agents/style-analyzer.md` (complete with examples)
- `.github/agents/style-transfer-generator.md` (optimized from 833→531 lines)
- `.github/agents/style-analyzer-unbiased.md` (benchmarking variant)
- `fine-tuning/data/styles/README.md` (style library documentation)

**Not Modified:**
- Training scripts (already support multiple data sources)
- Benchmark scripts (ready to measure style transfer quality)
- RAG system (independent workflow)

## Key Metrics

- **Agent size:** 531 lines, ~3,500 tokens (optimized from 833 lines, 5,570 tokens)
- **Analysis domains:** 10 narrative style dimensions
- **Scene templates:** 5 types (crisis, introspection, conflict, problem-solving, discovery)
- **Quality validation:** 3 levels (per-scene, per-universe, cross-universe)
- **Flexibility:** Universe count and genres user-determined (no hard constraints)
