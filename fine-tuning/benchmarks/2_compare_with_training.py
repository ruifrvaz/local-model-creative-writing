#!/usr/bin/env python3
"""
Compare baseline and fine-tuned models against training data (ground truth).

This script measures which model is closer to the actual writing style in the training data.

Usage:
    python compare_with_training.py results/baseline_TIMESTAMP.json results/finetuned_TIMESTAMP.json
    
    # Or use latest files
    python compare_with_training.py --latest
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))
from utils import style_metrics


def analyze_training_data(training_dir: Path) -> Dict:
    """
    Analyze all training data files to establish ground truth style metrics.
    
    Args:
        training_dir: Directory containing raw training files
    
    Returns:
        Aggregated style metrics from training data
    """
    print(f"\n=== Analyzing Training Data ===")
    print(f"Directory: {training_dir}\n")
    
    all_metrics = {
        "lexical": {"diversity": [], "rare_word_ratio": [], "avg_word_length": []},
        "sentence": {"avg_sentence_length": [], "sentence_length_variance": []},
        "style_markers": {"contraction_rate": [], "dialogue_ratio": [], "passive_voice_ratio": [], "readability_score": []},
        "vocabulary": {"technical_term_density": [], "total_words": []}
    }
    
    training_files = list(training_dir.glob("*.txt"))
    print(f"Found {len(training_files)} training files")
    
    for i, file_path in enumerate(training_files, 1):
        if i % 10 == 0:
            print(f"  Processing {i}/{len(training_files)}...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read().strip()
            
            if not text or len(text) < 100:  # Skip empty or too short files
                continue
            
            metrics = style_metrics.analyze_text(text)
            
            # Aggregate metrics
            for category, values in metrics.items():
                if category in all_metrics:
                    for metric, value in values.items():
                        if metric in all_metrics[category] and isinstance(value, (int, float)):
                            all_metrics[category][metric].append(value)
        
        except Exception as e:
            print(f"  Warning: Could not process {file_path.name}: {e}")
            continue
    
    # Calculate averages
    training_metrics = {}
    for category, metrics_dict in all_metrics.items():
        training_metrics[category] = {}
        for metric, values in metrics_dict.items():
            if values:
                training_metrics[category][metric] = round(sum(values) / len(values), 3)
            else:
                training_metrics[category][metric] = 0.0
    
    print(f"\n✓ Analyzed {len(training_files)} training files")
    print(f"\nTraining Data Style Profile:")
    print(f"  Lexical Diversity: {training_metrics['lexical']['diversity']:.3f}")
    print(f"  Avg Sentence Length: {training_metrics['sentence']['avg_sentence_length']:.1f} words")
    print(f"  Contraction Rate: {training_metrics['style_markers']['contraction_rate']:.2f}%")
    print(f"  Dialogue Ratio: {training_metrics['style_markers']['dialogue_ratio']:.3f}")
    print(f"  Technical Term Density: {training_metrics['vocabulary']['technical_term_density']:.3f}")
    
    return training_metrics


def calculate_distance_to_target(model_value: float, target_value: float, 
                                 metric_type: str = "default") -> float:
    """
    Calculate how far a model's metric is from the target (training data).
    Lower distance = closer to target = better.
    
    Returns score 0-100 where 100 = perfect match.
    """
    if target_value == 0:
        return 100.0 if model_value == 0 else 0.0
    
    # Calculate percentage difference
    pct_diff = abs(model_value - target_value) / abs(target_value)
    
    # Convert to score (0% diff = 100 score, 100% diff = 0 score)
    # Allow some tolerance based on metric type
    if metric_type == "variance":
        tolerance = 1.0  # Variance can vary significantly
    elif metric_type == "rate":
        tolerance = 0.5  # Rates/ratios moderate tolerance
    else:
        tolerance = 0.3  # Default tolerance
    
    if pct_diff <= tolerance:
        score = 100.0 * (1 - pct_diff / tolerance)
    else:
        score = max(0.0, 100.0 - (pct_diff * 100.0))
    
    return round(score, 2)


def compare_model_to_training(model_metrics: Dict, training_metrics: Dict, 
                              model_name: str) -> Dict:
    """
    Compare a model's output metrics to training data metrics.
    
    Returns:
        Dictionary with category scores and overall match score
    """
    scores = {
        "lexical": {},
        "sentence": {},
        "style_markers": {},
        "vocabulary": {}
    }
    
    # Compare lexical metrics
    for metric in ["diversity", "rare_word_ratio", "avg_word_length"]:
        model_val = model_metrics["lexical"].get(metric, 0.0)
        target_val = training_metrics["lexical"].get(metric, 0.0)
        scores["lexical"][metric] = calculate_distance_to_target(model_val, target_val)
    
    # Compare sentence metrics
    for metric in ["avg_sentence_length"]:
        model_val = model_metrics["sentence"].get(metric, 0.0)
        target_val = training_metrics["sentence"].get(metric, 0.0)
        scores["sentence"][metric] = calculate_distance_to_target(model_val, target_val)
    
    # Sentence variance (allow more tolerance)
    model_val = model_metrics["sentence"].get("sentence_length_variance", 0.0)
    target_val = training_metrics["sentence"].get("sentence_length_variance", 0.0)
    scores["sentence"]["sentence_length_variance"] = calculate_distance_to_target(
        model_val, target_val, metric_type="variance"
    )
    
    # Compare style markers
    for metric in ["contraction_rate", "dialogue_ratio", "passive_voice_ratio", "readability_score"]:
        model_val = model_metrics["style_markers"].get(metric, 0.0)
        target_val = training_metrics["style_markers"].get(metric, 0.0)
        scores["style_markers"][metric] = calculate_distance_to_target(
            model_val, target_val, metric_type="rate"
        )
    
    # Compare vocabulary
    model_val = model_metrics["vocabulary"].get("technical_term_density", 0.0)
    target_val = training_metrics["vocabulary"].get("technical_term_density", 0.0)
    scores["vocabulary"]["technical_term_density"] = calculate_distance_to_target(
        model_val, target_val
    )
    
    # Calculate category averages
    category_averages = {}
    for category, metrics in scores.items():
        if metrics:
            category_averages[category] = round(sum(metrics.values()) / len(metrics), 2)
        else:
            category_averages[category] = 0.0
    
    # Overall match score (weighted average)
    weights = {
        "lexical": 0.25,
        "sentence": 0.25,
        "style_markers": 0.30,
        "vocabulary": 0.20
    }
    
    overall_match = sum(category_averages[cat] * weights[cat] for cat in weights)
    
    return {
        "model_name": model_name,
        "overall_match": round(overall_match, 2),
        "category_scores": category_averages,
        "detailed_scores": scores
    }


def compare_models_with_training(baseline_file: Path, finetuned_file: Path, 
                                 training_dir: Path, output_dir: Path) -> Dict:
    """
    Compare baseline and fine-tuned models against training data ground truth.
    """
    # Analyze training data
    training_metrics = analyze_training_data(training_dir)
    
    # Load model results
    print(f"\n=== Loading Model Results ===")
    with open(baseline_file, 'r') as f:
        baseline_data = json.load(f)
    print(f"Baseline: {baseline_file.name}")
    
    with open(finetuned_file, 'r') as f:
        finetuned_data = json.load(f)
    print(f"Fine-tuned: {finetuned_file.name}")
    
    baseline_completions = baseline_data.get("completions", [])
    finetuned_completions = finetuned_data.get("completions", [])
    
    # Aggregate metrics from all completions
    def aggregate_completion_metrics(completions):
        """Average metrics across all completions."""
        agg = {
            "lexical": {"diversity": [], "rare_word_ratio": [], "avg_word_length": []},
            "sentence": {"avg_sentence_length": [], "sentence_length_variance": []},
            "style_markers": {"contraction_rate": [], "dialogue_ratio": [], "passive_voice_ratio": [], "readability_score": []},
            "vocabulary": {"technical_term_density": []}
        }
        
        for comp in completions:
            metrics = comp.get("metrics", {})
            for category in agg:
                if category in metrics:
                    for metric in agg[category]:
                        if metric in metrics[category]:
                            value = metrics[category][metric]
                            if isinstance(value, (int, float)):
                                agg[category][metric].append(value)
        
        # Calculate averages
        result = {}
        for category in agg:
            result[category] = {}
            for metric, values in agg[category].items():
                result[category][metric] = round(sum(values) / len(values), 3) if values else 0.0
        
        return result
    
    print(f"\n=== Comparing Models to Training Data ===\n")
    
    baseline_avg_metrics = aggregate_completion_metrics(baseline_completions)
    finetuned_avg_metrics = aggregate_completion_metrics(finetuned_completions)
    
    baseline_comparison = compare_model_to_training(baseline_avg_metrics, training_metrics, "Baseline")
    finetuned_comparison = compare_model_to_training(finetuned_avg_metrics, training_metrics, "Fine-tuned")
    
    # Calculate improvement
    improvement = finetuned_comparison["overall_match"] - baseline_comparison["overall_match"]
    
    # Build results
    results = {
        "timestamp": datetime.now().isoformat(),
        "baseline_file": str(baseline_file),
        "finetuned_file": str(finetuned_file),
        "training_dir": str(training_dir),
        "num_training_files": len(list(training_dir.glob("*.txt"))),
        "training_metrics": training_metrics,
        "baseline_comparison": baseline_comparison,
        "finetuned_comparison": finetuned_comparison,
        "improvement": {
            "overall": round(improvement, 2),
            "categories": {
                cat: round(finetuned_comparison["category_scores"][cat] - baseline_comparison["category_scores"][cat], 2)
                for cat in baseline_comparison["category_scores"]
            }
        }
    }
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"training_comparison_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print(f"{'='*70}")
    print(f"MODEL COMPARISON TO TRAINING DATA")
    print(f"{'='*70}\n")
    
    print(f"Baseline Model:")
    print(f"  Overall Match: {baseline_comparison['overall_match']:.1f}%")
    for cat, score in baseline_comparison["category_scores"].items():
        print(f"    {cat.capitalize()}: {score:.1f}%")
    
    print(f"\nFine-Tuned Model:")
    print(f"  Overall Match: {finetuned_comparison['overall_match']:.1f}%")
    for cat, score in finetuned_comparison["category_scores"].items():
        print(f"    {cat.capitalize()}: {score:.1f}%")
    
    print(f"\nImprovement (Fine-tuned vs Baseline):")
    print(f"  Overall: {improvement:+.1f}%")
    for cat, imp in results["improvement"]["categories"].items():
        print(f"    {cat.capitalize()}: {imp:+.1f}%")
    
    print(f"\n{'='*70}")
    if improvement >= 10:
        print(f"✓ Strong improvement - Fine-tuning effective")
    elif improvement >= 5:
        print(f"⚠ Moderate improvement - Some style transfer")
    elif improvement > 0:
        print(f"⚠ Minimal improvement - Limited style transfer")
    else:
        print(f"✗ No improvement - Fine-tuning did not help")
    
    print(f"\n✓ Results saved: {output_file}")
    print(f"{'='*70}")
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Compare models against training data ground truth"
    )
    
    parser.add_argument('baseline_file', nargs='?', type=str,
                       help='Path to baseline results JSON file')
    parser.add_argument('finetuned_file', nargs='?', type=str,
                       help='Path to fine-tuned results JSON file')
    parser.add_argument('--latest', action='store_true',
                       help='Use the most recent baseline and finetuned files')
    parser.add_argument('--training-dir', type=str, 
                       default='../data/raw',
                       help='Directory containing training data files')
    parser.add_argument('--output-dir', type=str, default='results',
                       help='Output directory for comparison results')
    
    args = parser.parse_args()
    
    # Determine result files
    results_dir = Path(__file__).parent / args.output_dir
    training_dir = Path(__file__).parent / args.training_dir
    
    if not training_dir.exists():
        print(f"Error: Training directory not found: {training_dir}")
        sys.exit(1)
    
    if args.latest:
        baseline_files = sorted(results_dir.glob("baseline_*.json"), reverse=True)
        finetuned_files = sorted(results_dir.glob("finetuned_*.json"), reverse=True)
        
        if not baseline_files:
            print("Error: No baseline results found")
            sys.exit(1)
        if not finetuned_files:
            print("Error: No finetuned results found")
            sys.exit(1)
        
        baseline_file = baseline_files[0]
        finetuned_file = finetuned_files[0]
    elif args.baseline_file and args.finetuned_file:
        baseline_file = Path(args.baseline_file)
        finetuned_file = Path(args.finetuned_file)
        
        if not baseline_file.exists():
            print(f"Error: Baseline file not found: {baseline_file}")
            sys.exit(1)
        if not finetuned_file.exists():
            print(f"Error: Fine-tuned file not found: {finetuned_file}")
            sys.exit(1)
    else:
        print("Error: Either specify both files or use --latest")
        parser.print_help()
        sys.exit(1)
    
    # Run comparison
    compare_models_with_training(baseline_file, finetuned_file, training_dir, results_dir)


if __name__ == "__main__":
    main()
