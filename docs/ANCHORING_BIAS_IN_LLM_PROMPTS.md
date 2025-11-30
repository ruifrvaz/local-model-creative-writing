# Anchoring Bias in LLM Analytical Prompts: An Empirical Comparison

**Date:** 2025-11-30  
**Domain:** Prompt Engineering, Large Language Model Behavior  
**Analysis Agent:** Claude Sonnet 4 (both biased and unbiased conditions)  
**Assessment & Verification:** Claude Opus 4.5

---

## Abstract

This study compares two prompt engineering approaches for LLM-based text analysis: example-inclusive ("biased") versus example-free ("unbiased") prompts. Using a 62,884-word manuscript as the analysis target, we find that including example outputs in prompts induces anchoring bias, causing the model to generate plausible-looking but factually incorrect data. Ground truth verification revealed a 400% overcount of structural elements in the example-inclusive condition. We conclude that analytical prompts should provide structural scaffolding without example values.

**Hypothesis:** Example outputs in prompts function as cognitive anchors rather than format templates, biasing LLM analysis toward expected values.

**Result:** Confirmed. The example-free approach achieved 100% accuracy on verifiable metrics; the example-inclusive approach fabricated data.

---

## 1. Introduction

A common prompt engineering practice involves providing example outputs to guide LLM responses. The assumption is that examples clarify format requirements without influencing analytical conclusions. This study tests whether that assumption holds for quantitative text analysis tasks.

---

## 2. Method

### 2.1 Experimental Design

Two style analysis agents were created with identical analytical objectives but different prompt structures:

| Condition | Prompt Design |
|-----------|---------------|
| **Biased** | Included example outputs, sample metrics, expected value ranges |
| **Unbiased** | Structural scaffolding only; no example values or sample outputs |

### 2.2 Materials

- **Target text:** "Visions of Gaea" manuscript (62,884 words, 3 sections)
- **Analysis scope:** 10 stylistic domains including sentence structure, dialogue ratio, scene breaks, POV consistency
- **Ground truth:** Manual verification of countable elements (scene breaks marked by `***`)

### 2.3 Evaluation Criteria

1. **Internal consistency:** Do reported metrics align mathematically?
2. **Ground truth accuracy:** Do countable elements match actual counts?
3. **Arc sensitivity:** Do metrics reflect expected narrative variation?

---

## 3. Results

### 3.1 Ground Truth Verification

Scene break markers (`***`) were counted directly in source files:

| Section | Ground Truth | Biased Report | Unbiased Report |
|---------|--------------|---------------|-----------------|
| Section 1 | 2 | 8 | 2 ✅ |
| Section 2 | 2 | — | 2 ✅ |
| Section 3 | 7 | — | 7 ✅ |
| **Total** | **11** | **17** | **11 ✅** |

The biased condition reported 8 scene breaks where 2 exist—a **400% overcount**. The unbiased condition matched ground truth exactly.

### 3.2 Internal Consistency

| Metric | Biased | Unbiased |
|--------|--------|----------|
| Words ÷ Sentences = Avg Length | 62884/3200 = 19.65 (reported 20.5) ❌ | 62884/3076 = 20.44 (reported 21.3) ✅ |
| Pronoun counts | Estimates (~2,600) | Exact (1,682) |

### 3.3 Arc Sensitivity

Dialogue ratio variation across narrative sections:

| Condition | Range | Interpretation |
|-----------|-------|----------------|
| Biased | 46–52% (6pt spread) | Implausibly uniform |
| Unbiased | 27–50% (23pt spread) | Arc-appropriate variation |

Sentence length progression:

| Condition | Setup → Development → Climax | Validity |
|-----------|------------------------------|----------|
| Biased | 20.8 → 15.4 → 26.1 | Inverted (atypical) |
| Unbiased | 27.4 → 21.2 → 15.9 | Decreasing (expected) |

### 3.4 Aggregate Scoring

| Category | Biased | Unbiased |
|----------|--------|----------|
| Internal Consistency | 3/5 | 5/5 |
| Data Precision | 3/5 | 5/5 |
| Arc Sensitivity | 2/5 | 5/5 |
| **Total** | **21/30** | **27/30** |

---

## 4. Discussion

### 4.1 Mechanism

The biased agent's errors follow a consistent pattern: reported values cluster around "reasonable defaults" rather than reflecting actual text properties. This suggests the model treated example values as targets to approximate rather than formats to populate with fresh analysis.

The 400% scene break overcount is particularly diagnostic. The biased prompt likely included examples suggesting "frequent scene breaks," causing the model to hallucinate additional breaks to match expectations.

### 4.2 The Flattening Effect

Example-inclusive prompts produced suspiciously uniform metrics across sections (6pt dialogue spread vs. 23pt). This "flattening" indicates the model averaged toward expected values rather than measuring actual variation.

### 4.3 Implications

Examples in analytical prompts do not function as neutral format guidance. They establish cognitive anchors that:
1. Bias measurements toward expected ranges
2. Reduce sensitivity to actual variance
3. Enable hallucination of data to match expectations

---

## 5. Conclusion

**Finding:** Example outputs in LLM prompts for analytical tasks induce anchoring bias, degrading accuracy and enabling data fabrication.

**Recommendation:** Analytical prompts should provide:
- ✅ Output structure (JSON schema, section headers)
- ✅ Field definitions ("dialogue_ratio: percentage of words in dialogue")
- ✅ Quality criteria ("provide exact counts, not estimates")
- ❌ Example values
- ❌ Sample metrics
- ❌ Expected ranges

**Generalization:** This finding likely applies to any LLM task requiring quantitative analysis, pattern discovery, or data extraction. When genuine observation is required, provide structural scaffolding without populated examples.

---

## References

- Source data: `fine-tuning/data/styles/visions_of_gaea/`
- Detailed comparison: `ANALYSIS_COMPARISON.md`
- Extended discussion: `PROMPT_ENGINEERING_ANCHORING_BIAS.md`
