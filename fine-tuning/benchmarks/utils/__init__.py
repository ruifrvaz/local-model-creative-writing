"""
Fine-tuning benchmark utilities.

Shared functions for analyzing writing style and comparing model outputs.
"""

from .style_metrics import (
    calculate_lexical_diversity,
    calculate_sentence_metrics,
    detect_style_markers,
    analyze_vocabulary
)

from .comparison import (
    calculate_similarity_score,
    calculate_transfer_score,
    compare_outputs
)

__all__ = [
    'calculate_lexical_diversity',
    'calculate_sentence_metrics',
    'detect_style_markers',
    'analyze_vocabulary',
    'calculate_similarity_score',
    'calculate_transfer_score',
    'compare_outputs'
]
