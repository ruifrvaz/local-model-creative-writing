"""
Style analysis metrics for comparing writing voice.

Functions to extract quantitative style features from text:
- Lexical diversity and vocabulary richness
- Sentence structure and complexity
- Style markers (contractions, passive voice, etc.)
- Genre-specific patterns

All functions return numeric scores for programmatic comparison.
"""

import re
from collections import Counter
from typing import Dict, List
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import pos_tag
import textstat


def ensure_nltk_data():
    """Download required NLTK data if not present."""
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('taggers/averaged_perceptron_tagger')
    except LookupError:
        nltk.download('punkt', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)


def calculate_lexical_diversity(text: str) -> Dict[str, float]:
    """
    Calculate vocabulary richness metrics.
    
    Returns:
        - diversity: unique_words / total_words
        - rare_word_ratio: proportion of uncommon words
        - avg_word_length: mean character count per word
    """
    words = word_tokenize(text.lower())
    words = [w for w in words if w.isalnum()]  # Remove punctuation
    
    if not words:
        return {"diversity": 0.0, "rare_word_ratio": 0.0, "avg_word_length": 0.0}
    
    unique_words = set(words)
    diversity = len(unique_words) / len(words)
    avg_word_length = sum(len(w) for w in words) / len(words)
    
    # Approximate rare word detection (words > 8 chars as proxy)
    rare_words = [w for w in words if len(w) > 8]
    rare_word_ratio = len(rare_words) / len(words)
    
    return {
        "diversity": round(diversity, 3),
        "rare_word_ratio": round(rare_word_ratio, 3),
        "avg_word_length": round(avg_word_length, 2)
    }


def calculate_sentence_metrics(text: str) -> Dict[str, float]:
    """
    Calculate sentence structure metrics.
    
    Returns:
        - avg_sentence_length: words per sentence
        - sentence_length_variance: consistency of pacing
        - num_sentences: total sentence count
    """
    sentences = sent_tokenize(text)
    
    if not sentences:
        return {
            "avg_sentence_length": 0.0,
            "sentence_length_variance": 0.0,
            "num_sentences": 0
        }
    
    sentence_lengths = []
    for sent in sentences:
        words = word_tokenize(sent)
        words = [w for w in words if w.isalnum()]
        sentence_lengths.append(len(words))
    
    avg_length = sum(sentence_lengths) / len(sentence_lengths)
    
    # Calculate variance
    if len(sentence_lengths) > 1:
        mean = avg_length
        variance = sum((x - mean) ** 2 for x in sentence_lengths) / len(sentence_lengths)
    else:
        variance = 0.0
    
    return {
        "avg_sentence_length": round(avg_length, 2),
        "sentence_length_variance": round(variance, 2),
        "num_sentences": len(sentences)
    }


def detect_style_markers(text: str) -> Dict[str, float]:
    """
    Detect stylistic patterns and markers.
    
    Returns:
        - contraction_rate: contractions per 100 words
        - dialogue_ratio: dialogue words / total words (approximate)
        - passive_voice_ratio: passive constructions per 100 sentences
        - readability_score: Flesch Reading Ease
    """
    words = word_tokenize(text)
    total_words = len([w for w in words if w.isalnum()])
    
    if total_words == 0:
        return {
            "contraction_rate": 0.0,
            "dialogue_ratio": 0.0,
            "passive_voice_ratio": 0.0,
            "readability_score": 0.0
        }
    
    # Contraction detection
    contractions = re.findall(r"\b\w+'\w+\b", text)
    contraction_rate = (len(contractions) / total_words) * 100
    
    # Dialogue detection (approximate: count quoted text)
    dialogue_matches = re.findall(r'"([^"]*)"', text)
    dialogue_words = sum(len(word_tokenize(d)) for d in dialogue_matches)
    dialogue_ratio = dialogue_words / total_words if total_words > 0 else 0.0
    
    # Passive voice detection (simple heuristic: was/were + past participle)
    sentences = sent_tokenize(text)
    passive_count = 0
    for sent in sentences:
        # Simple pattern: was/were followed by VBN (past participle)
        if re.search(r'\b(was|were|been|be|being)\s+\w+ed\b', sent, re.IGNORECASE):
            passive_count += 1
    
    passive_ratio = (passive_count / len(sentences)) * 100 if sentences else 0.0
    
    # Readability score
    try:
        readability = textstat.flesch_reading_ease(text)
    except:
        readability = 0.0
    
    return {
        "contraction_rate": round(contraction_rate, 2),
        "dialogue_ratio": round(dialogue_ratio, 3),
        "passive_voice_ratio": round(passive_ratio, 2),
        "readability_score": round(readability, 2)
    }


def analyze_vocabulary(text: str) -> Dict[str, any]:
    """
    Analyze vocabulary usage and patterns.
    
    Returns:
        - total_words: word count
        - unique_words: unique word count
        - top_words: 10 most frequent words
        - technical_term_density: words with capitals/numbers
    """
    words = word_tokenize(text.lower())
    words = [w for w in words if w.isalnum()]
    
    if not words:
        return {
            "total_words": 0,
            "unique_words": 0,
            "top_words": [],
            "technical_term_density": 0.0
        }
    
    word_freq = Counter(words)
    top_words = [word for word, count in word_freq.most_common(10)]
    
    # Technical terms: words with capitals or numbers in original text
    technical_pattern = re.findall(r'\b[A-Z][a-z]*(?:[A-Z][a-z]*)*\b|\b\w*\d+\w*\b', text)
    technical_density = len(technical_pattern) / len(words)
    
    return {
        "total_words": len(words),
        "unique_words": len(set(words)),
        "top_words": top_words,
        "technical_term_density": round(technical_density, 3)
    }


def analyze_text(text: str) -> Dict[str, any]:
    """
    Comprehensive text analysis combining all metrics.
    
    Args:
        text: Input text to analyze
    
    Returns:
        Dictionary with all style metrics
    """
    ensure_nltk_data()
    
    return {
        "lexical": calculate_lexical_diversity(text),
        "sentence": calculate_sentence_metrics(text),
        "style_markers": detect_style_markers(text),
        "vocabulary": analyze_vocabulary(text)
    }
