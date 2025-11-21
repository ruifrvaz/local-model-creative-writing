# Style Library

This directory contains analyzed writing styles and their corresponding generated training data for style transfer fine-tuning.

## Directory Structure

```
styles/
├── README.md                      # This file
├── [style_name]/                  # One directory per analyzed style
│   ├── STYLE_TRANSFER_GUIDE.md    # Complete style analysis (from style-analyzer)
│   ├── STYLE_STATISTICS.json      # Quantitative metrics (from style-analyzer)
│   ├── STYLE_PATTERNS.md          # Quick reference guide (from style-analyzer)
│   └── generated/                 # Generated training data (from style-transfer-generator)
│       ├── GENERATION_PLAN.md     # Universe designs and scene plans
│       ├── GENERATION_REPORT.md   # Final statistics and validation
│       ├── universe_01_[name]/    # Story universe 1
│       │   ├── scene_01_[descriptor].txt
│       │   ├── scene_02_[descriptor].txt
│       │   └── ...
│       ├── universe_02_[name]/    # Story universe 2
│       │   └── ...
│       └── ...
```

## Workflow

### 1. Analyze a Writing Style
```bash
# Use style-analyzer agent to extract style patterns from manuscript
@style-analyzer Analyze the style of [manuscript] and save as "[style_name]" style
```

**Output:** `styles/[style_name]/STYLE_TRANSFER_GUIDE.md` with complete analysis

### 2. Generate Training Data
```bash
# Use style-transfer-generator agent to create new content matching the style
@style-transfer-generator Generate training data for "[style_name]" style
```

**Output:** `styles/[style_name]/generated/` with 50-100+ scenes across multiple universes

### 3. Process for Training
```bash
# Use book-curator or prepare_data.py to chunk/format for fine-tuning
cd fine-tuning/training
python 1_prepare_data.py --input ../data/styles/[style_name]/generated/ --output ../data/processed/[style_name]_training.jsonl
```

## Example: Visions of Gaea Style

```
styles/visions_of_gaea/
├── STYLE_TRANSFER_GUIDE.md        # Second-person POV, poetic-literary voice, etc.
├── STYLE_STATISTICS.json          # Avg 16.8 words/sentence, 35% dialogue, etc.
├── STYLE_PATTERNS.md              # Quick reference cheat sheet
└── generated/
    ├── GENERATION_PLAN.md         # 6 universes designed
    ├── GENERATION_REPORT.md       # 73 scenes, 101,234 words
    ├── universe_01_lunar_excavation/
    │   ├── scene_01_anomalous_fragment.txt
    │   ├── scene_02_analysis_debate.txt
    │   └── ... (12 scenes total)
    ├── universe_02_neural_frontier/
    │   └── ... (10 scenes total)
    └── ... (6 universes total)
```

## Purpose

**Style Library enables:**
- Reusable style analysis across multiple training runs
- Multiple styles in one project (personal style, different author styles, genre styles)
- Clear separation between original manuscripts (`raw/`) and style derivatives (`styles/`)
- Organized training data generation with traceability to source style

**Use cases:**
1. **Personal style transfer** - Analyze your writing, generate diverse training data
2. **Author emulation** - Study published authors, practice their techniques
3. **Genre mastery** - Extract patterns from genre exemplars, apply to your work
4. **Style blending** - Train on multiple styles, develop hybrid voice

## File Naming Conventions

**Style names:**
- Lowercase with underscores: `visions_of_gaea`, `hard_scifi_style`, `poetic_prose`
- Descriptive and memorable
- Avoid spaces and special characters

**Scene files:**
- Format: `scene_[number]_[descriptor].txt`
- Zero-padded numbers: `01`, `02`, `03`...
- Short descriptors: 2-4 words, lowercase, underscores
- Examples: `scene_01_crisis_response.txt`, `scene_15_character_reflection.txt`

## Integration with Training Pipeline

**Single style training:**
```bash
# Train on generated content only
python 1_prepare_data.py --input ../data/styles/visions_of_gaea/generated/
```

**Multi-style training:**
```bash
# Combine multiple styles or add original manuscript chunks
cat ../data/processed/visions_of_gaea_training.jsonl \
    ../data/processed/original_chunks_training.jsonl \
    > ../data/processed/combined_training.jsonl
```

**Style-specific fine-tuning:**
```bash
# Create separate models for different styles
./2_train_lora.sh --config ../configs/visions_of_gaea_style.yaml
./2_train_lora.sh --config ../configs/hard_scifi_style.yaml
```

## Best Practices

1. **Analyze before generating** - Always run style-analyzer first
2. **Review style guides** - Verify analysis accuracy before generating data
3. **Generate diverse content** - Use multiple story universes (5-8 minimum)
4. **Validate consistency** - Check generation reports for style fidelity
5. **Iterate if needed** - Refine style guide if generated content feels off
6. **Document decisions** - Update generation plans with rationale
7. **Version control** - Commit style guides separately from generated data

## Comparison with raw/ Directory

**`raw/` directory:**
- Original manuscript files
- Book curator chunking output
- Direct text from source material
- Preserves author's original content

**`styles/` directory:**
- Style analysis documents
- Generated training data matching styles
- Multiple story universes
- NEW content in analyzed style, not original text

**Both used together:**
- Original chunks teach specific voice on specific content
- Style-matched generated content teaches generalizable patterns
- Combined training = strong style + good generalization
