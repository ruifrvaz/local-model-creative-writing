#!/usr/bin/env python3
"""
Data Preparation Script for Fine-Tuning (Completion Format)

Converts curated manuscript chunks into training-ready JSONL format for style transfer.
Uses prefix-completion format that matches actual creative writing workflow.

Input:  data/raw/[book_name]/chunk_*.txt (curated chunks from book-curator)
Output: data/processed/training.jsonl, validation.jsonl

Format: {"messages": [{"role": "user", "content": "[prefix]"}, 
                      {"role": "assistant", "content": "[completion]"}]}

The prefix is the first 5-15% of the chunk (narrative setup).
The completion is the remaining 85-95% (what model learns to generate).

No system prompt in training - that comes from Continue.dev at inference time.
This matches real usage: user provides partial narrative, model continues it.

Usage:
    source ~/.venvs/finetune/bin/activate
    python 1_prepare_data.py --input ../data/raw/visions_of_gaea/ --output ../data/processed/visions_training.jsonl
    python 1_prepare_data.py --input ../data/raw/visions_of_gaea/ --preview  # Show examples

Note: Run this script from within the finetune virtual environment
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import random


# Check if running in correct virtual environment
def check_venv():
    """Verify script is running in finetune venv."""
    venv_path = os.environ.get('VIRTUAL_ENV', '')
    if 'finetune' not in venv_path:
        print("[ERROR] This script must run in the finetune virtual environment!")
        print("   Please run: source ~/.venvs/finetune/bin/activate")
        print(f"   Current env: {venv_path or 'None'}")
        sys.exit(1)


check_venv()


def load_chunk_files(input_dir: Path) -> List[Tuple[str, str]]:
    """Load chunk files from input directory.
    
    Expects curated chunks from book-curator agent.
    Excludes documentation files and the full manuscript.
    
    Returns:
        List of (filename, content) tuples, sorted by filename
    """
    files = []
    supported_extensions = {'.txt', '.md'}
    exclude_patterns = {
        'readme', 'license', 'changelog', 'contributing',
        'manuscript_analysis', 'chunk_metadata', 'curation_report'
    }
    
    for filepath in sorted(input_dir.glob('*')):
        if filepath.suffix.lower() not in supported_extensions:
            continue
        if not filepath.is_file():
            continue
            
        # Skip documentation and metadata files
        name_lower = filepath.stem.lower()
        if any(pattern in name_lower for pattern in exclude_patterns):
            print(f"[SKIP] {filepath.name}: metadata/documentation file")
            continue
        
        # Skip the full manuscript if chunks exist
        if 'manuscript' in name_lower and not name_lower.startswith('chunk'):
            print(f"[SKIP] {filepath.name}: full manuscript (using chunks instead)")
            continue
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                if content.strip():
                    files.append((filepath.name, content))
                    word_count = len(content.split())
                    print(f"[LOAD] {filepath.name}: {word_count} words")
        except Exception as e:
            print(f"[WARN] Failed to load {filepath.name}: {e}")
    
    print(f"[OK] Loaded {len(files)} chunk files")
    return files


def clean_text(text: str) -> str:
    """Light cleaning - preserve author's formatting choices.
    
    Only removes obvious artifacts, not stylistic elements.
    """
    # Remove common metadata patterns
    text = re.sub(r'\[TODO:.*?\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[NOTE:.*?\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[DRAFT.*?\]', '', text, flags=re.IGNORECASE)
    
    # Normalize excessive whitespace (but preserve paragraph breaks)
    text = re.sub(r'\n{4,}', '\n\n\n', text)  # Max 3 consecutive newlines
    text = re.sub(r' {3,}', '  ', text)  # Max 2 consecutive spaces
    
    return text.strip()


def estimate_tokens(text: str) -> int:
    """Rough token estimate (1 token ≈ 4 characters for English)."""
    return len(text) // 4


def find_sentence_boundary(text: str, target_pos: int, search_range: int = 200) -> int:
    """Find nearest sentence boundary to target position.
    
    Searches for sentence-ending punctuation (.!?) followed by space or newline.
    Returns position after the punctuation.
    """
    # Define search window
    start = max(0, target_pos - search_range)
    end = min(len(text), target_pos + search_range)
    
    # Find all sentence boundaries in window
    boundaries = []
    for match in re.finditer(r'[.!?]["\']?\s', text[start:end]):
        abs_pos = start + match.end()
        distance = abs(abs_pos - target_pos)
        boundaries.append((abs_pos, distance))
    
    if boundaries:
        # Return closest boundary
        boundaries.sort(key=lambda x: x[1])
        return boundaries[0][0]
    
    # Fallback: try to find any whitespace near target
    for match in re.finditer(r'\s', text[start:end]):
        abs_pos = start + match.end()
        if abs(abs_pos - target_pos) < 50:
            return abs_pos
    
    # Last resort: use target position
    return target_pos


def split_prefix_completion(
    text: str, 
    min_prefix_ratio: float = 0.05, 
    max_prefix_ratio: float = 0.15
) -> Tuple[str, str]:
    """Split text into prefix (user prompt) and completion (assistant response).
    
    Uses varied split points at sentence boundaries for natural breaks.
    
    Args:
        text: Full chunk text
        min_prefix_ratio: Minimum prefix length as ratio of total (default 5%)
        max_prefix_ratio: Maximum prefix length as ratio of total (default 15%)
        
    Returns:
        Tuple of (prefix, completion)
    """
    text_len = len(text)
    
    # Random split ratio within range
    split_ratio = random.uniform(min_prefix_ratio, max_prefix_ratio)
    target_split = int(text_len * split_ratio)
    
    # Find nearest sentence boundary
    split_pos = find_sentence_boundary(text, target_split)
    
    # Ensure we have meaningful prefix and completion
    min_prefix_chars = 100  # At least ~25 tokens
    min_completion_chars = 500  # At least ~125 tokens
    
    if split_pos < min_prefix_chars:
        split_pos = find_sentence_boundary(text, min_prefix_chars)
    
    if text_len - split_pos < min_completion_chars:
        # Not enough completion - find earlier split
        split_pos = find_sentence_boundary(text, text_len - min_completion_chars)
    
    prefix = text[:split_pos].strip()
    completion = text[split_pos:].strip()
    
    return prefix, completion


def create_training_example(prefix: str, completion: str) -> Dict:
    """Create a single training example in completion format.
    
    No system prompt - that comes from Continue.dev at inference time.
    
    Format:
        {"messages": [
            {"role": "user", "content": "[narrative prefix]"},
            {"role": "assistant", "content": "[narrative completion]"}
        ]}
    """
    return {
        "messages": [
            {"role": "user", "content": prefix},
            {"role": "assistant", "content": completion}
        ]
    }


def save_jsonl(examples: List[Dict], output_path: Path):
    """Save examples to JSONL file (one JSON object per line)."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    print(f"[SAVE] {output_path}: {len(examples)} examples")


def print_example_preview(examples: List[Dict], count: int = 2):
    """Print preview of generated examples."""
    print(f"\n[PREVIEW] First {count} examples:")
    print("─" * 70)
    
    for i, example in enumerate(examples[:count]):
        prefix = example["messages"][0]["content"]
        completion = example["messages"][1]["content"]
        
        # Truncate for display
        prefix_preview = prefix[:300] + "..." if len(prefix) > 300 else prefix
        completion_preview = completion[:300] + "..." if len(completion) > 300 else completion
        
        print(f"\n[Example {i+1}]")
        print(f"USER ({len(prefix)} chars, ~{estimate_tokens(prefix)} tokens):")
        print(f"  {prefix_preview}")
        print(f"\nASSISTANT ({len(completion)} chars, ~{estimate_tokens(completion)} tokens):")
        print(f"  {completion_preview}")
        print("─" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Prepare training data using prefix-completion format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process curated chunks
  python 1_prepare_data.py --input ../data/raw/visions_of_gaea/
  
  # Custom prefix ratios (how much text becomes the prompt)
  python 1_prepare_data.py --input ../data/raw/visions_of_gaea/ --min-prefix 0.08 --max-prefix 0.12
  
  # Preview generated examples
  python 1_prepare_data.py --input ../data/raw/visions_of_gaea/ --preview
        """
    )
    parser.add_argument('--input', type=str, default='../data/raw/',
                        help='Input directory with chunk files')
    parser.add_argument('--output', type=str, default='../data/processed/training.jsonl',
                        help='Output JSONL file path')
    parser.add_argument('--min-prefix', type=float, default=0.05,
                        help='Minimum prefix length as ratio (default: 0.05 = 5%%)')
    parser.add_argument('--max-prefix', type=float, default=0.15,
                        help='Maximum prefix length as ratio (default: 0.15 = 15%%)')
    parser.add_argument('--split', type=float, default=0.9,
                        help='Train/validation split ratio (0.9 = 90%% train)')
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed for reproducibility')
    parser.add_argument('--preview', action='store_true',
                        help='Show preview of generated examples')
    
    args = parser.parse_args()
    
    # Validate ratios
    if args.min_prefix >= args.max_prefix:
        print("[ERROR] --min-prefix must be less than --max-prefix")
        sys.exit(1)
    if args.min_prefix < 0.02 or args.max_prefix > 0.30:
        print("[WARN] Unusual prefix ratios. Recommended range: 0.05-0.15")
    
    # Set random seed
    random.seed(args.seed)
    
    # Setup paths
    input_dir = Path(args.input)
    output_path = Path(args.output)
    output_dir = output_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    val_path = output_dir / 'validation.jsonl'
    
    print("━" * 70)
    print("Data Preparation for Fine-Tuning (Completion Format)")
    print("━" * 70)
    print(f"Input:        {input_dir}")
    print(f"Output:       {output_path}")
    print(f"Prefix ratio: {args.min_prefix:.0%}-{args.max_prefix:.0%}")
    print(f"Split:        {args.split:.0%} train / {1-args.split:.0%} validation")
    print(f"Seed:         {args.seed}")
    print()
    
    # Load chunk files
    print("[STEP 1/3] Loading chunk files...")
    files = load_chunk_files(input_dir)
    
    if not files:
        print("[ERROR] No chunk files found!")
        print(f"   Checked: {input_dir}")
        print(f"   Expected: chunk_*.txt files from book-curator")
        sys.exit(1)
    
    # Process chunks into prefix-completion pairs
    print(f"\n[STEP 2/3] Creating prefix-completion pairs...")
    examples = []
    stats = {
        'total_words': 0,
        'prefix_tokens': [],
        'completion_tokens': []
    }
    
    for filename, content in files:
        # Clean text
        cleaned = clean_text(content)
        word_count = len(cleaned.split())
        stats['total_words'] += word_count
        
        # Split into prefix and completion
        prefix, completion = split_prefix_completion(
            cleaned, 
            args.min_prefix, 
            args.max_prefix
        )
        
        # Track statistics
        prefix_tokens = estimate_tokens(prefix)
        completion_tokens = estimate_tokens(completion)
        stats['prefix_tokens'].append(prefix_tokens)
        stats['completion_tokens'].append(completion_tokens)
        
        # Create training example
        example = create_training_example(prefix, completion)
        examples.append(example)
        
        print(f"[SPLIT] {filename}: {prefix_tokens} prefix → {completion_tokens} completion tokens")
    
    # Shuffle and split
    print(f"\n[STEP 3/3] Saving files...")
    random.shuffle(examples)
    split_idx = int(len(examples) * args.split)
    train_examples = examples[:split_idx]
    val_examples = examples[split_idx:]
    
    # Save
    save_jsonl(train_examples, output_path)
    if val_examples:
        save_jsonl(val_examples, val_path)
    else:
        print(f"[INFO] No validation examples (dataset too small for {1-args.split:.0%} split)")
    
    # Statistics
    avg_prefix = sum(stats['prefix_tokens']) / len(stats['prefix_tokens'])
    avg_completion = sum(stats['completion_tokens']) / len(stats['completion_tokens'])
    
    print("\n" + "━" * 70)
    print("Summary")
    print("━" * 70)
    print(f"Total chunks:        {len(files)}")
    print(f"Total words:         {stats['total_words']:,}")
    print(f"Training examples:   {len(train_examples)}")
    print(f"Validation examples: {len(val_examples)}")
    print(f"\nToken statistics:")
    print(f"  Avg prefix:     {avg_prefix:.0f} tokens (~{avg_prefix*4:.0f} chars)")
    print(f"  Avg completion: {avg_completion:.0f} tokens (~{avg_completion*4:.0f} chars)")
    print(f"  Prefix range:   {min(stats['prefix_tokens'])}-{max(stats['prefix_tokens'])} tokens")
    
    # Preview
    if args.preview:
        print_example_preview(examples)
    
    print(f"\n[OK] Data preparation complete!")
    print(f"\nFormat: Prefix-completion (no system prompt)")
    print(f"System prompt will come from Continue.dev at inference time.")
    print(f"\nNext steps:")
    print(f"  1. Review: head -1 {output_path} | python -m json.tool")
    print(f"  2. Configure: ../configs/qlora_style_transfer.yaml")
    print(f"  3. Train: ./2_train_lora.sh")


if __name__ == '__main__':
    main()
