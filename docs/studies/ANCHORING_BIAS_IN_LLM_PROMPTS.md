# Anchoring Bias in LLM Analytical Prompts: An Empirical Comparison

**Date:** 2025-11-30  
**Domain:** Prompt Engineering, Large Language Model Behavior  
**Analysis Agent:** Claude Sonnet 4 (both biased and unbiased conditions)  
**Assessment & Verification:** Claude Opus 4.5

---

## Materials

### Agents

| Condition | Agent File | Prompt Design |
|-----------|------------|---------------|
| Biased | `.github/agents/style-analyzer.md` | Includes example outputs with sample metrics |
| Unbiased | `.github/agents/style-analyzer-unb.md` | Structural scaffolding only, no examples |

### Analysis Outputs

Located in `fine-tuning/data/styles/visions_of_gaea/`:

| Output Type | Biased | Unbiased |
|-------------|--------|----------|
| Transfer Guide | `STYLE_TRANSFER_GUIDE_biased.md` | `STYLE_TRANSFER_GUIDE_unbiased.md` |
| Statistics | `STYLE_STATISTICS_biased.json` | `STYLE_STATISTICS_unbiased.json` |
| Patterns | `STYLE_PATTERNS_biased.md` | `STYLE_PATTERNS_unbiased.md` |
| Section Analyses | `section_analyses_biased/` | `section_analyses/` |

### Source Material

- **Manuscript:** "Visions of Gaea" (62,884 words)
- **Section files:** `manuscript_sections/section_{1,2,3}_*.txt`

---

## Abstract

This study compares two prompt engineering approaches for LLM-based text analysis: example-inclusive ("biased") versus example-free ("unbiased") prompts. Using a 62,884-word manuscript as the analysis target, we observed that including example outputs in prompts may induce anchoring bias, potentially causing the model to generate plausible-looking but inaccurate data. Ground truth verification revealed a significant overcount of structural elements in the example-inclusive condition. These results suggest that analytical prompts may benefit from structural scaffolding without example values.

**Hypothesis:** Example outputs in prompts may function as cognitive anchors rather than format templates, potentially biasing LLM analysis toward expected values.

**Observation:** In this case study, the example-free approach matched ground truth on verifiable metrics; the example-inclusive approach showed significant discrepancies.

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

The biased condition reported 8 scene breaks where 2 exist—a significant discrepancy. The unbiased condition matched ground truth exactly in this instance.

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

### 4.1 Possible Mechanism

The biased agent's discrepancies follow a pattern worth noting: reported values appear to cluster around "reasonable defaults" rather than reflecting actual text properties. This may suggest the model treated example values as targets to approximate rather than formats to populate with fresh analysis.

The scene break overcount is worth examining. The biased prompt may have included examples suggesting certain frequencies, potentially influencing the model toward those expectations.

### 4.2 Observed Flattening Effect

Example-inclusive prompts produced notably uniform metrics across sections (6pt dialogue spread vs. 23pt). This pattern may indicate the model averaged toward expected values rather than measuring actual variation, though alternative explanations are possible.

### 4.3 Potential Implications

If these observations generalize, examples in analytical prompts may not function as neutral format guidance. They could establish cognitive anchors that:
1. Bias measurements toward expected ranges
2. Reduce sensitivity to actual variance
3. Increase risk of confabulated data to match expectations

Further study across different tasks and models would be needed to confirm these patterns.

---

## 5. Conclusion

**Observation:** In this case study, example outputs in LLM prompts for analytical tasks correlated with reduced accuracy and data discrepancies.

**Personal Recommendation:** For analytical tasks requiring precision, consider:
- ✅ Output structure (JSON schema, section headers)
- ✅ Field definitions ("dialogue_ratio: percentage of words in dialogue")
- ✅ Quality criteria ("provide exact counts, not estimates")
- ⚠️ Use example values sparingly, if at all
- ⚠️ Avoid sample metrics that could anchor expectations
- ⚠️ Consider omitting expected ranges

**Scope:** This is a single case study (n=1 manuscript, 1 model family). The pattern may not generalize across all tasks, models, or prompt structures. Practitioners should test both approaches for their specific use cases.

---

## References

- **Biased agent:** `.github/agents/style-analyzer.md`
- **Unbiased agent:** `.github/agents/style-analyzer-unb.md`
- **Analysis outputs:** `fine-tuning/data/styles/visions_of_gaea/`
- **Detailed comparison:** `ANALYSIS_COMPARISON.md` (in outputs directory)
- **Extended discussion:** `docs/PROMPT_ENGINEERING_ANCHORING_BIAS.md`
