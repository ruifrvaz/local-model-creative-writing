#!/usr/bin/env python3
"""
Data Preparation Script for Fine-Tuning

Converts raw writing samples into training-ready JSONL format for style transfer.

Input:  data/raw/*.txt, *.md (your writing samples)
Output: data/processed/training.jsonl, validation.jsonl

Format: {"messages": [{"role": "system", "content": "..."}, 
                      {"role": "user", "content": "..."}, 
                      {"role": "assistant", "content": "..."}]}

Usage:
    # Activate finetune environment first
    source ~/.venvs/finetune/bin/activate
    python 1_prepare_data.py --input ../data/raw/ --output ../data/processed/training.jsonl
    python 1_prepare_data.py --input ../data/raw/ --min-tokens 300 --max-tokens 1500

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


def load_text_files(input_dir: Path) -> List[Tuple[str, str]]:
    """Load all .txt and .md files from input directory.
    
    Excludes common documentation files (README, LICENSE, etc.)
    
    Returns:
        List of (filename, content) tuples
    """
    files = []
    supported_extensions = {'.txt', '.md'}
    exclude_names = {'readme.md', 'license.md', 'changelog.md', 'contributing.md', 
                     'license.txt', 'changelog.txt', 'contributing.txt'}
    
    for filepath in input_dir.rglob('*'):
        if filepath.suffix.lower() in supported_extensions and filepath.is_file():
            # Skip documentation files
            if filepath.name.lower() in exclude_names:
                print(f"[SKIP] {filepath.name}: documentation file")
                continue
                
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip():  # Skip empty files
                        files.append((filepath.name, content))
                        print(f"[LOAD] {filepath.name}: {len(content)} chars")
            except Exception as e:
                print(f"[WARN] Failed to load {filepath.name}: {e}")
    
    print(f"[OK] Loaded {len(files)} files")
    return files


def clean_text(text: str) -> str:
    """Remove metadata, TODOs, and formatting artifacts.
    
    Args:
        text: Raw text content
        
    Returns:
        Cleaned text
    """
    # Remove common metadata patterns
    text = re.sub(r'\[TODO:.*?\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[NOTE:.*?\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[DRAFT.*?\]', '', text, flags=re.IGNORECASE)
    
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 consecutive newlines
    text = re.sub(r' {2,}', ' ', text)  # Multiple spaces to single
    
    # Remove leading/trailing whitespace per line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    return text.strip()


def estimate_tokens(text: str) -> int:
    """Rough token estimate (1 token ≈ 4 characters for English).
    
    More accurate would use tiktoken, but this is sufficient for chunking.
    """
    return len(text) // 4


def chunk_text(text: str, min_tokens: int = 500, max_tokens: int = 2000) -> List[str]:
    """Split text into chunks of roughly equal size.
    
    Strategy:
    - Split on double newlines (paragraph boundaries)
    - Combine paragraphs until target size reached
    - Ensure chunks are within min/max token range
    
    Args:
        text: Text to chunk
        min_tokens: Minimum tokens per chunk
        max_tokens: Maximum tokens per chunk
        
    Returns:
        List of text chunks
    """
    # Split into paragraphs
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    for para in paragraphs:
        para_tokens = estimate_tokens(para)
        
        # If single paragraph exceeds max, split it
        if para_tokens > max_tokens:
            # Save current chunk if exists
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_tokens = 0
            
            # Split long paragraph by sentences
            sentences = re.split(r'(?<=[.!?])\s+', para)
            temp_chunk = []
            temp_tokens = 0
            
            for sentence in sentences:
                sent_tokens = estimate_tokens(sentence)
                if temp_tokens + sent_tokens > max_tokens and temp_chunk:
                    chunks.append(' '.join(temp_chunk))
                    temp_chunk = [sentence]
                    temp_tokens = sent_tokens
                else:
                    temp_chunk.append(sentence)
                    temp_tokens += sent_tokens
            
            if temp_chunk:
                chunks.append(' '.join(temp_chunk))
        
        # Normal paragraph processing
        elif current_tokens + para_tokens > max_tokens:
            if current_chunk and current_tokens >= min_tokens:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [para]
                current_tokens = para_tokens
            else:
                # Current chunk too small, force add this paragraph anyway
                current_chunk.append(para)
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_tokens = 0
        else:
            current_chunk.append(para)
            current_tokens += para_tokens
    
    # Add remaining chunk if meets minimum size
    if current_chunk and current_tokens >= min_tokens:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks


def analyze_writing_style(chunks: List[str]) -> str:
    """Analyze writing samples to generate system prompt description.
    
    Simple heuristics to describe style:
    - Average sentence length
    - Vocabulary complexity (avg word length)
    - Dialogue vs narrative ratio
    
    Returns:
        System prompt describing writing style
    """
    total_sentences = 0
    total_words = 0
    total_chars = 0
    dialogue_lines = 0
    total_lines = 0
    
    for chunk in chunks[:10]:  # Sample first 10 chunks
        sentences = re.split(r'[.!?]+', chunk)
        total_sentences += len([s for s in sentences if s.strip()])
        
        words = chunk.split()
        total_words += len(words)
        total_chars += sum(len(w) for w in words)
        
        lines = chunk.split('\n')
        total_lines += len(lines)
        dialogue_lines += len([l for l in lines if '"' in l or '"' in l or '"' in l])
    
    avg_word_length = total_chars / total_words if total_words > 0 else 5
    avg_sentence_words = total_words / total_sentences if total_sentences > 0 else 15
    dialogue_ratio = dialogue_lines / total_lines if total_lines > 0 else 0.3
    
    # Generate style description
    if avg_word_length > 5.5:
        vocab = "sophisticated vocabulary and technical precision"
    elif avg_word_length > 4.5:
        vocab = "balanced vocabulary"
    else:
        vocab = "accessible, direct language"
    
    if avg_sentence_words > 20:
        structure = "complex, flowing sentences"
    elif avg_sentence_words > 15:
        structure = "varied sentence structure"
    else:
        structure = "concise, punchy sentences"
    
    if dialogue_ratio > 0.4:
        balance = "dialogue-heavy with atmospheric description"
    elif dialogue_ratio > 0.2:
        balance = "balanced narrative and dialogue"
    else:
        balance = "introspective, description-focused narrative"
    
    return f"You are a science fiction author with {vocab}, {structure}, and {balance}."


def generate_user_prompt(chunk: str) -> str:
    """Generate a plausible user prompt for this writing sample.
    
    Extracts key elements from the chunk to create a scene prompt.
    """
    # Simple heuristics for prompt generation
    if "said" in chunk.lower() or "asked" in chunk.lower():
        # Dialogue-heavy
        return "Continue the scene with character dialogue and interaction."
    elif any(word in chunk.lower() for word in ["entered", "walked", "moved", "stood"]):
        # Action/movement
        return "Write a scene with character movement and spatial description."
    elif any(word in chunk.lower() for word in ["thought", "felt", "realized", "wondered"]):
        # Introspection
        return "Write a character's internal thoughts and emotional response."
    elif any(word in chunk.lower() for word in ["ship", "station", "planet", "system"]):
        # Sci-fi setting
        return "Describe a science fiction setting with technical details."
    else:
        # Generic
        return "Continue the narrative in your distinctive style."


def create_training_example(chunk: str, system_prompt: str) -> Dict:
    """Create a single training example in messages format.
    
    Format:
        {"messages": [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."}
        ]}
    """
    user_prompt = generate_user_prompt(chunk)
    
    return {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": chunk}
        ]
    }


def save_jsonl(examples: List[Dict], output_path: Path):
    """Save examples to JSONL file (one JSON object per line)."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    print(f"[SAVE] {output_path}: {len(examples)} examples")


def main():
    parser = argparse.ArgumentParser(description="Prepare training data from writing samples")
    parser.add_argument('--input', type=str, default='../data/raw/',
                        help='Input directory with .txt/.md files')
    parser.add_argument('--output', type=str, default='../data/processed/training.jsonl',
                        help='Output JSONL file path')
    parser.add_argument('--min-tokens', type=int, default=500,
                        help='Minimum tokens per chunk')
    parser.add_argument('--max-tokens', type=int, default=2000,
                        help='Maximum tokens per chunk')
    parser.add_argument('--split', type=float, default=0.9,
                        help='Train/validation split ratio (0.9 = 90% train)')
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed for reproducibility')
    
    args = parser.parse_args()
    
    # Set random seed
    random.seed(args.seed)
    
    # Setup paths
    input_dir = Path(args.input)
    output_path = Path(args.output)
    output_dir = output_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    val_path = output_dir / 'validation.jsonl'
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("Data Preparation for Fine-Tuning")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Input:  {input_dir}")
    print(f"Output: {output_path}")
    print(f"Chunk:  {args.min_tokens}-{args.max_tokens} tokens")
    print(f"Split:  {args.split:.0%} train / {1-args.split:.0%} validation")
    print("")
    
    # Load files
    print("[STEP 1/5] Loading text files...")
    files = load_text_files(input_dir)
    
    if not files:
        print("[ERROR] No text files found in input directory!")
        print(f"   Checked: {input_dir}")
        print(f"   Supported: .txt, .md")
        return
    
    # Clean and combine text
    print("\n[STEP 2/5] Cleaning text...")
    all_text = []
    for filename, content in files:
        cleaned = clean_text(content)
        all_text.append(cleaned)
        print(f"[CLEAN] {filename}: {len(content)} → {len(cleaned)} chars")
    
    combined_text = '\n\n'.join(all_text)
    print(f"[OK] Total text: {len(combined_text)} chars (~{estimate_tokens(combined_text)} tokens)")
    
    # Chunk text
    print(f"\n[STEP 3/5] Chunking text ({args.min_tokens}-{args.max_tokens} tokens)...")
    chunks = chunk_text(combined_text, args.min_tokens, args.max_tokens)
    print(f"[OK] Created {len(chunks)} chunks")
    
    if len(chunks) < 10:
        print("[WARN] Very few chunks created. Consider:")
        print("   - Adding more writing samples")
        print("   - Reducing --min-tokens threshold")
        print("   - Checking if input files contain substantial text")
    
    # Analyze style and generate system prompt
    print("\n[STEP 4/5] Analyzing writing style...")
    system_prompt = analyze_writing_style(chunks)
    print(f"[STYLE] {system_prompt}")
    
    # Create training examples
    print("\n[STEP 5/5] Creating training examples...")
    examples = [create_training_example(chunk, system_prompt) for chunk in chunks]
    
    # Shuffle and split
    random.shuffle(examples)
    split_idx = int(len(examples) * args.split)
    train_examples = examples[:split_idx]
    val_examples = examples[split_idx:]
    
    # Save
    save_jsonl(train_examples, output_path)
    save_jsonl(val_examples, val_path)
    
    # Summary
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("Summary")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Training examples:   {len(train_examples)}")
    print(f"Validation examples: {len(val_examples)}")
    print(f"Total examples:      {len(examples)}")
    print(f"\nSystem prompt: {system_prompt}")
    print(f"\nNext step:")
    print(f"  Configure: ../configs/qlora_style_transfer.yaml")
    print(f"  Then run:  ./2_train_lora.sh")


if __name__ == '__main__':
    main()
