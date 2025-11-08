"""
Comparison and scoring functions for fine-tuning benchmarks.

Calculates similarity scores between baseline and fine-tuned outputs:
- Individual metric similarity (vocabulary, structure, style)
- Weighted transfer score (overall effectiveness)
- Statistical significance testing

All functions accept metric dictionaries from style_metrics.py.
"""

import math
from typing import Dict, List


def calculate_metric_similarity(baseline_value: float, finetuned_value: float, 
                                 target_value: float = None, 
                                 tolerance: float = 0.15) -> float:
    """
    Calculate similarity score for a single metric.
    
    Args:
        baseline_value: Baseline model metric value
        finetuned_value: Fine-tuned model metric value
        target_value: Optional target value from training data
        tolerance: Acceptable deviation range (default 15%)
    
    Returns:
        Similarity score 0-100
    """
    if target_value is not None:
        # Score based on how close fine-tuned is to target vs baseline
        baseline_distance = abs(baseline_value - target_value)
        finetuned_distance = abs(finetuned_value - target_value)
        
        if baseline_distance == 0:
            return 100.0 if finetuned_distance == 0 else 50.0
        
        # Calculate improvement ratio
        improvement = (baseline_distance - finetuned_distance) / baseline_distance
        score = 50 + (improvement * 50)  # Scale to 0-100
        return max(0.0, min(100.0, score))
    
    else:
        # Score based on absolute difference
        diff = abs(baseline_value - finetuned_value)
        relative_diff = diff / (abs(baseline_value) + 1e-10)  # Avoid division by zero
        
        if relative_diff <= tolerance:
            score = 100.0 - (relative_diff / tolerance) * 100.0
        else:
            score = max(0.0, 100.0 - (relative_diff * 100.0))
        
        return max(0.0, min(100.0, score))


def compare_lexical_metrics(baseline: Dict, finetuned: Dict, 
                            target: Dict = None) -> Dict[str, float]:
    """
    Compare lexical diversity metrics.
    
    Returns individual and aggregate lexical similarity scores.
    """
    metrics = ["diversity", "rare_word_ratio", "avg_word_length"]
    scores = {}
    
    for metric in metrics:
        baseline_val = baseline.get(metric, 0.0)
        finetuned_val = finetuned.get(metric, 0.0)
        target_val = target.get(metric) if target else None
        
        scores[metric] = calculate_metric_similarity(
            baseline_val, finetuned_val, target_val
        )
    
    scores["aggregate"] = sum(scores.values()) / len(scores)
    return scores


def compare_sentence_metrics(baseline: Dict, finetuned: Dict,
                             target: Dict = None) -> Dict[str, float]:
    """
    Compare sentence structure metrics.
    
    Returns individual and aggregate sentence similarity scores.
    """
    metrics = ["avg_sentence_length", "sentence_length_variance"]
    scores = {}
    
    for metric in metrics:
        baseline_val = baseline.get(metric, 0.0)
        finetuned_val = finetuned.get(metric, 0.0)
        target_val = target.get(metric) if target else None
        
        scores[metric] = calculate_metric_similarity(
            baseline_val, finetuned_val, target_val
        )
    
    scores["aggregate"] = sum(scores.values()) / len(scores)
    return scores


def compare_style_markers(baseline: Dict, finetuned: Dict,
                          target: Dict = None) -> Dict[str, float]:
    """
    Compare stylistic markers.
    
    Returns individual and aggregate style similarity scores.
    """
    metrics = ["contraction_rate", "dialogue_ratio", "passive_voice_ratio", "readability_score"]
    scores = {}
    
    for metric in metrics:
        baseline_val = baseline.get(metric, 0.0)
        finetuned_val = finetuned.get(metric, 0.0)
        target_val = target.get(metric) if target else None
        
        scores[metric] = calculate_metric_similarity(
            baseline_val, finetuned_val, target_val, tolerance=0.20
        )
    
    scores["aggregate"] = sum(scores.values()) / len(scores)
    return scores


def compare_vocabulary(baseline: Dict, finetuned: Dict,
                       target: Dict = None) -> Dict[str, float]:
    """
    Compare vocabulary usage patterns.
    
    Returns vocabulary overlap and technical term similarity.
    """
    scores = {}
    
    # Compare technical term density
    baseline_tech = baseline.get("technical_term_density", 0.0)
    finetuned_tech = finetuned.get("technical_term_density", 0.0)
    target_tech = target.get("technical_term_density") if target else None
    
    scores["technical_density"] = calculate_metric_similarity(
        baseline_tech, finetuned_tech, target_tech
    )
    
    # Compare word count patterns (should be similar for same prompts)
    baseline_words = baseline.get("total_words", 0)
    finetuned_words = finetuned.get("total_words", 0)
    
    if baseline_words > 0:
        word_count_ratio = finetuned_words / baseline_words
        # Ideal ratio is 0.8-1.2 (similar verbosity)
        if 0.8 <= word_count_ratio <= 1.2:
            scores["verbosity"] = 100.0 - abs(1.0 - word_count_ratio) * 100.0
        else:
            scores["verbosity"] = max(0.0, 100.0 - abs(1.0 - word_count_ratio) * 200.0)
    else:
        scores["verbosity"] = 50.0
    
    scores["aggregate"] = sum(scores.values()) / len(scores)
    return scores


def calculate_transfer_score(baseline_metrics: Dict, finetuned_metrics: Dict,
                             target_metrics: Dict = None,
                             weights: Dict[str, float] = None) -> Dict[str, float]:
    """
    Calculate overall style transfer score.
    
    Args:
        baseline_metrics: Metrics from baseline model
        finetuned_metrics: Metrics from fine-tuned model
        target_metrics: Optional metrics from training data
        weights: Custom weights for each metric category
    
    Returns:
        Dictionary with category scores and overall transfer score
    """
    if weights is None:
        weights = {
            "lexical": 0.25,
            "sentence": 0.25,
            "style_markers": 0.30,
            "vocabulary": 0.20
        }
    
    # Compare each category
    lexical_scores = compare_lexical_metrics(
        baseline_metrics.get("lexical", {}),
        finetuned_metrics.get("lexical", {}),
        target_metrics.get("lexical") if target_metrics else None
    )
    
    sentence_scores = compare_sentence_metrics(
        baseline_metrics.get("sentence", {}),
        finetuned_metrics.get("sentence", {}),
        target_metrics.get("sentence") if target_metrics else None
    )
    
    style_scores = compare_style_markers(
        baseline_metrics.get("style_markers", {}),
        finetuned_metrics.get("style_markers", {}),
        target_metrics.get("style_markers") if target_metrics else None
    )
    
    vocab_scores = compare_vocabulary(
        baseline_metrics.get("vocabulary", {}),
        finetuned_metrics.get("vocabulary", {}),
        target_metrics.get("vocabulary") if target_metrics else None
    )
    
    # Calculate weighted transfer score
    transfer_score = (
        lexical_scores["aggregate"] * weights["lexical"] +
        sentence_scores["aggregate"] * weights["sentence"] +
        style_scores["aggregate"] * weights["style_markers"] +
        vocab_scores["aggregate"] * weights["vocabulary"]
    )
    
    return {
        "transfer_score": round(transfer_score, 2),
        "category_scores": {
            "lexical": round(lexical_scores["aggregate"], 2),
            "sentence": round(sentence_scores["aggregate"], 2),
            "style_markers": round(style_scores["aggregate"], 2),
            "vocabulary": round(vocab_scores["aggregate"], 2)
        },
        "detailed_scores": {
            "lexical": lexical_scores,
            "sentence": sentence_scores,
            "style_markers": style_scores,
            "vocabulary": vocab_scores
        }
    }


def compare_outputs(baseline_text: str, finetuned_text: str,
                   baseline_metrics: Dict = None, finetuned_metrics: Dict = None,
                   target_metrics: Dict = None) -> Dict:
    """
    Complete comparison of two text outputs.
    
    Args:
        baseline_text: Output from baseline model
        finetuned_text: Output from fine-tuned model
        baseline_metrics: Pre-computed metrics (optional)
        finetuned_metrics: Pre-computed metrics (optional)
        target_metrics: Target metrics from training data (optional)
    
    Returns:
        Complete comparison report with scores and metrics
    """
    from . import style_metrics
    
    # Compute metrics if not provided
    if baseline_metrics is None:
        baseline_metrics = style_metrics.analyze_text(baseline_text)
    
    if finetuned_metrics is None:
        finetuned_metrics = style_metrics.analyze_text(finetuned_text)
    
    # Calculate transfer score
    scores = calculate_transfer_score(baseline_metrics, finetuned_metrics, target_metrics)
    
    return {
        "baseline_text": baseline_text,
        "finetuned_text": finetuned_text,
        "baseline_metrics": baseline_metrics,
        "finetuned_metrics": finetuned_metrics,
        "comparison": scores
    }
