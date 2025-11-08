"""
Fine-tuning benchmark utilities.

Shared functions for analyzing writing style and comparing model outputs.
"""

from . import style_metrics
from . import comparison

__all__ = ['style_metrics', 'comparison']
