#!/usr/bin/env python3
"""
Blind Evaluation - Human Quality Assessment

Generates A/B comparison markdown from baseline and fine-tuned results.
Outputs randomized pairs for subjective quality evaluation.

Usage:
    # Use latest results automatically
    python 3_blind_evaluation.py --latest
    
    # Specify result files explicitly
    python 3_blind_evaluation.py results/baseline_20251107_233004.json results/finetuned_20251107_233537.json
    
    # Custom output file
    python 3_blind_evaluation.py --latest --output my_evaluation.md

Outputs:
    - results/blind_evaluation_TIMESTAMP.md (or custom path)
    - Includes randomized A/B pairs + reveal section

Workflow:
    1. Generate baseline: python 1_voice_comparison.py --baseline --port 8000
    2. Generate fine-tuned: python 1_voice_comparison.py --finetuned --port 8002
    3. Create evaluation: python 3_blind_evaluation.py --latest
    4. Open markdown in VS Code, read pairs, mark preferences
    5. Scroll to reveal section, calculate win rate
"""

import argparse
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


def find_latest_results(results_dir: Path) -> Tuple[Path, Path]:
    """Find the most recent baseline and fine-tuned result files."""
    baseline_files = sorted(results_dir.glob("baseline_*.json"), reverse=True)
    finetuned_files = sorted(results_dir.glob("finetuned_*.json"), reverse=True)
    
    if not baseline_files:
        raise FileNotFoundError(f"No baseline results found in {results_dir}")
    if not finetuned_files:
        raise FileNotFoundError(f"No fine-tuned results found in {results_dir}")
    
    return baseline_files[0], finetuned_files[0]


def load_results(filepath: Path) -> Dict:
    """Load results from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def generate_blind_evaluation(baseline_data: Dict, finetuned_data: Dict, 
                              baseline_file: str, finetuned_file: str) -> str:
    """Generate markdown with randomized A/B comparisons."""
    
    # Verify same prompts
    baseline_completions = baseline_data["completions"]
    finetuned_completions = finetuned_data["completions"]
    
    if len(baseline_completions) != len(finetuned_completions):
        raise ValueError(f"Mismatched completion counts: {len(baseline_completions)} vs {len(finetuned_completions)}")
    
    # Build markdown
    lines = []
    lines.append("# Blind Evaluation - Voice Comparison\n")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"**Baseline file:** `{baseline_file}`\n")
    lines.append(f"**Fine-tuned file:** `{finetuned_file}`\n")
    lines.append(f"**Total pairs:** {len(baseline_completions)}\n")
    lines.append("---\n\n")
    
    lines.append("## Instructions\n\n")
    lines.append("For each pair below:\n")
    lines.append("1. Read both outputs carefully\n")
    lines.append("2. Consider: Which feels more natural? More engaging? Better paced?\n")
    lines.append("3. Mark your preference in the brackets: `[X] A`, `[X] B`, or `[X] No preference`\n")
    lines.append("4. Briefly note your reasoning\n")
    lines.append("5. After all pairs, scroll to the **Reveal** section to see which was which\n")
    lines.append("6. Calculate win rate: (Fine-tuned wins / Total pairs) × 100%\n\n")
    lines.append("**Target:** Fine-tuned should win >60% for production deployment\n\n")
    lines.append("---\n\n")
    
    # Store reveal information
    reveal_info = []
    
    # Generate pairs with randomization
    for i, (baseline_comp, finetuned_comp) in enumerate(zip(baseline_completions, finetuned_completions), 1):
        prompt_id = baseline_comp["prompt_id"]
        prompt_text = baseline_comp["prompt"]
        category = baseline_comp["category"]
        
        baseline_output = baseline_comp["output"]
        finetuned_output = finetuned_comp["output"]
        
        # Randomize A/B order
        is_baseline_first = random.choice([True, False])
        
        if is_baseline_first:
            output_a = baseline_output
            output_b = finetuned_output
            reveal_a = "baseline"
            reveal_b = "fine-tuned"
        else:
            output_a = finetuned_output
            output_b = baseline_output
            reveal_a = "fine-tuned"
            reveal_b = "baseline"
        
        # Store for reveal
        reveal_info.append({
            "pair_num": i,
            "prompt_id": prompt_id,
            "a": reveal_a,
            "b": reveal_b
        })
        
        # Generate pair section
        lines.append(f"## Pair {i}/{len(baseline_completions)}\n\n")
        lines.append(f"**Prompt ID:** `{prompt_id}` ({category})\n\n")
        lines.append(f"**Prompt:**\n> {prompt_text}\n\n")
        lines.append("---\n\n")
        
        lines.append("### Output A\n\n")
        lines.append(f"{output_a}\n\n")
        
        lines.append("---\n\n")
        
        lines.append("### Output B\n\n")
        lines.append(f"{output_b}\n\n")
        
        lines.append("---\n\n")
        
        lines.append("**Your preference:**\n")
        lines.append("- [ ] Output A\n")
        lines.append("- [ ] Output B\n")
        lines.append("- [ ] No preference\n\n")
        
        lines.append("**Reasoning:**\n")
        lines.append("_[Your notes here]_\n\n")
        
        lines.append("---\n\n")
    
    # Add reveal section
    lines.append("# Reveal Section\n\n")
    lines.append("**⚠️ SPOILERS BELOW - Complete your evaluation before scrolling further!**\n\n")
    lines.append("---\n\n")
    lines.append("## Model Identity by Pair\n\n")
    
    for reveal in reveal_info:
        lines.append(f"**Pair {reveal['pair_num']}** (`{reveal['prompt_id']}`): "
                    f"A = **{reveal['a']}**, B = **{reveal['b']}**\n\n")
    
    lines.append("---\n\n")
    lines.append("## Calculating Win Rate\n\n")
    lines.append("1. Count how many times you preferred the **fine-tuned** output\n")
    lines.append("2. Divide by total pairs (excluding 'no preference')\n")
    lines.append("3. Multiply by 100 for percentage\n\n")
    lines.append("**Example:**\n")
    lines.append("- Fine-tuned wins: 8\n")
    lines.append("- Baseline wins: 3\n")
    lines.append("- No preference: 1\n")
    lines.append("- Win rate: 8 / (8 + 3) × 100 = 72.7%\n\n")
    lines.append("**Interpretation:**\n")
    lines.append("- **>60%:** Fine-tuned is subjectively better → Ready for production\n")
    lines.append("- **40-60%:** Mixed results → Consider more training data or evaluation\n")
    lines.append("- **<40%:** Baseline is better → Training may have degraded quality\n\n")
    
    return "".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate blind A/B evaluation from baseline and fine-tuned results"
    )
    
    # Input mode
    parser.add_argument('--latest', action='store_true',
                       help='Use most recent baseline and fine-tuned results')
    parser.add_argument('files', nargs='*',
                       help='Baseline and fine-tuned JSON files (2 required if --latest not used)')
    
    # Output configuration
    parser.add_argument('--output', type=str,
                       help='Output markdown file (default: results/blind_evaluation_TIMESTAMP.md)')
    parser.add_argument('--results-dir', type=str, default='results',
                       help='Results directory (default: results)')
    
    # Random seed for reproducibility
    parser.add_argument('--seed', type=int,
                       help='Random seed for A/B order (for reproducibility)')
    
    args = parser.parse_args()
    
    # Validate input mode
    if not args.latest and len(args.files) != 2:
        parser.error("Must either use --latest or provide exactly 2 JSON files")
    if args.latest and args.files:
        parser.error("Cannot use --latest with explicit file paths")
    
    # Set random seed if provided
    if args.seed:
        random.seed(args.seed)
        print(f"Using random seed: {args.seed}")
    
    results_dir = Path(__file__).parent / args.results_dir
    
    # Find or load input files
    if args.latest:
        print("Finding latest results...")
        baseline_path, finetuned_path = find_latest_results(results_dir)
        print(f"  Baseline: {baseline_path.name}")
        print(f"  Fine-tuned: {finetuned_path.name}")
    else:
        baseline_path = Path(args.files[0])
        finetuned_path = Path(args.files[1])
        
        if not baseline_path.exists():
            raise FileNotFoundError(f"Baseline file not found: {baseline_path}")
        if not finetuned_path.exists():
            raise FileNotFoundError(f"Fine-tuned file not found: {finetuned_path}")
    
    # Load results
    print("\nLoading results...")
    baseline_data = load_results(baseline_path)
    finetuned_data = load_results(finetuned_path)
    
    print(f"  Baseline: {len(baseline_data['completions'])} completions")
    print(f"  Fine-tuned: {len(finetuned_data['completions'])} completions")
    
    # Generate evaluation markdown
    print("\nGenerating blind evaluation...")
    markdown = generate_blind_evaluation(
        baseline_data, finetuned_data,
        baseline_path.name, finetuned_path.name
    )
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = results_dir / f"blind_evaluation_{timestamp}.md"
    
    # Save evaluation
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(markdown)
    
    print(f"\n✓ Blind evaluation saved: {output_path}")
    print(f"\nNext steps:")
    print(f"1. Open in VS Code: code {output_path}")
    print(f"2. Read each pair and mark your preferences")
    print(f"3. Scroll to Reveal section to see which was which")
    print(f"4. Calculate win rate (target: >60% for fine-tuned)")
    
    return output_path


if __name__ == "__main__":
    main()
