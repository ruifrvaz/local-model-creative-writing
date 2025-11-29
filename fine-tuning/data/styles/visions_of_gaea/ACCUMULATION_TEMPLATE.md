# Style Analysis Accumulation Reference

**Purpose:** Reference document for style-merger agent workflow  
**Task:** 004_analyze_visions_manuscript_style.md  
**Updated:** 2025-11-29

---

## Overview

This document serves as a reference for the **style-merger** agent when combining section analyses into a unified style guide. The agent reads from `section_analyses/` and outputs to this directory.

**Agent:** `.github/agents/style-merger.md`

---

## Input Files (section_analyses/)

| File | Purpose |
|------|---------|
| `section_[N]_STYLE_TRANSFER_GUIDE.md` | Detailed analysis per section |
| `section_[N]_STYLE_STATISTICS.json` | Quantitative metrics |
| `section_[N]_STYLE_PATTERNS.md` | Pattern catalog |

---

## Output Files (this directory)

| File | Purpose |
|------|---------|
| `STYLE_TRANSFER_GUIDE.md` | Unified guide for style-transfer-generator |
| `STYLE_STATISTICS.json` | Accumulated metrics with ranges |
| `STYLE_PATTERNS.md` | Comprehensive pattern catalog |

---

## Merge Strategy Summary

### Quantitative Data

| Data Type | Merge Method |
|-----------|--------------|
| Averages | Weighted average by word count |
| Ranges | Union (min of mins, max of maxs) |
| Ratios | Weighted average + variance note |
| Counts | Sum total |
| Lists | Union with frequency tracking |

### Qualitative Data

| Pattern Presence | Priority | Treatment |
|------------------|----------|-----------|
| All 3 sections | CRITICAL | Core style, non-negotiable |
| 2 sections | HIGH | Strong indicator |
| 1 section only | CONTEXTUAL | Arc-specific, document when to use |

### Variance Classification

| Variance | Action |
|----------|--------|
| ±5% | Report single value |
| ±15% | Report average with note |
| >15% | Report range, explain arc variation |

---

## 10 Analysis Domains

1. **POV & Narrative Distance** - Voice type, consistency, examples
2. **Prose Rhythm & Sentence Structure** - Lengths, patterns, paragraphs
3. **Dialogue Patterns** - Ratio, tags, attribution style
4. **Description Style** - Sensory balance, density, show/tell
5. **Pacing & Information Flow** - Scene transitions, arc variations
6. **Chapter/Scene Structure** - Breaks, lengths, memory format
7. **Worldbuilding Integration** - Terminology, introduction method
8. **Tone & Emotional Register** - Restraint, physical manifestation
9. **Character Voice Differentiation** - Speech patterns, markers
10. **Technical Choices** - Italics, tense, formatting conventions

---

## Invocation

```
@style-merger Merge the section analyses for "visions_of_gaea" style 
from fine-tuning/data/styles/visions_of_gaea/section_analyses/ 
into unified guide files in fine-tuning/data/styles/visions_of_gaea/
```

---

## Post-Merge Validation

After merge completes, verify:

- [ ] `STYLE_TRANSFER_GUIDE.md` exists and covers all 10 domains
- [ ] `STYLE_STATISTICS.json` has valid JSON structure
- [ ] `STYLE_PATTERNS.md` categorizes patterns by frequency
- [ ] All section data represented in unified files
- [ ] No unresolved contradictions remain
- [ ] Generator directives are actionable

---

## Next Step

After successful merge, invoke style-transfer-generator:

```
@style-transfer-generator Generate training data for "visions_of_gaea" style
```

---

## Reference: Terminology Guide

The following sections provide terminology reference for understanding analysis outputs.

### POV Types

| Type | Description | Example |
|------|-------------|---------|
| First-Person | "I" narrator | *"I couldn't shake the feeling..."* |
| Second-Person | "You" address | *"You step into the corridor..."* |
| Third-Limited | One character's view | *"Sarah wondered if anyone noticed."* |
| Third-Omniscient | Multiple perspectives | *"While John searched, Maria discovered..."* |

### Sentence Metrics

| Category | Words | Usage |
|----------|-------|-------|
| Very Short | 1-5 | Emphasis, impact |
| Short | 6-12 | Clarity, pace |
| Medium | 13-20 | Standard narrative |
| Long | 21-30 | Complex ideas |
| Very Long | 31+ | Literary, flowing |

### Dialogue Ratios

| Type | Percentage | Style |
|------|------------|-------|
| Dialogue-Heavy | 60-80% | Screenplay-like |
| Balanced | 40-60% | Typical novel |
| Prose-Heavy | 20-40% | Literary |
| Minimal | <20% | Action/philosophical |

### Variance Patterns

| Level | Range | Interpretation |
|-------|-------|----------------|
| Low | ±5% | Highly consistent |
| Medium | ±15% | Normal variation |
| High | >15% | Arc-dependent or inconsistent |

### Worldbuilding Density

| Level | Terms/1000 words |
|-------|------------------|
| Sparse | <5 |
| Moderate | 5-15 |
| Rich | 15-30 |
| Dense | 30+ |
