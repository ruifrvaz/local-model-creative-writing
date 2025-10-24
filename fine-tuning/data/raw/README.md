# Raw Training Data

Place your writing samples here in plain text format (`.txt` or `.md`).

## Guidelines

### What to Include
- Complete narrative passages (not fragments)
- 500-2000 tokens per file
- Your natural writing style
- Diverse scenes and tones

### File Format
```
my_novel_chapter_01.txt
short_story_alpha.txt
scene_fragments_collection.txt
```

### Quality Checklist
✅ Plain text (UTF-8 encoding)  
✅ Remove editing notes, TODOs  
✅ Keep natural paragraph breaks  
✅ Include dialogue with attribution  
✅ Complete sentences (no mid-sentence cuts)  

❌ Avoid:
- Dialogue-only excerpts
- Metadata or formatting codes
- Mixed author styles
- Incomplete fragments

## Next Steps

After adding your files:
```bash
cd ../..
python scripts/1_prepare_data.py --input data/raw/ --output data/processed/training.jsonl
```

This will convert your writing into training format.
