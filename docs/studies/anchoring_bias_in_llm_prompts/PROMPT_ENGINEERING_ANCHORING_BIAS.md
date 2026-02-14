# Prompt Engineering: The Anchoring Bias Problem

**Date:** 2025-11-30  
**Context:** Comparison of biased vs unbiased style analysis agents  
**Finding:** Example-based prompts cause anchoring bias that degrades analysis accuracy

---

## The Experiment

Two parallel style analysis agents were created to analyze the same manuscript ("Visions of Gaea", 62,884 words):

| Agent | Prompt Design | Hypothesis |
|-------|---------------|------------|
| **Biased** | Included example outputs, expected format templates, sample metrics | Examples would help model understand requirements |
| **Unbiased** | Neutral prompts asking for raw observation without structural guidance | Blank slate would force genuine observation |

---

## Results

**Winner: Unbiased Analysis (27/30 vs 21/30)**

| Category | Biased | Unbiased |
|----------|--------|----------|
| Internal Consistency | 3/5 | 5/5 |
| Data Precision | 3/5 | 5/5 |
| Arc Sensitivity | 2/5 | 5/5 |

---

## Key Evidence

### 1. The Flattening Effect

The biased analysis showed **suspiciously uniform metrics** across narrative sections:

| Metric | Biased Range | Unbiased Range |
|--------|--------------|----------------|
| Dialogue ratio | 46-52% (6pt spread) | 27-50% (23pt spread) |
| Sentence length | 15.4-26.1 (inverted arc) | 15.9-27.4 (logical arc) |

The tight variance in the biased analysis is **implausible** for a narrative with distinct setup, development, and climax phases.

### 2. The Inverted Arc Problem

**Biased sentence arc:**
- Section 1 (Setup): 20.8 words avg
- Section 2 (Development): 15.4 words avg ← shortest
- Section 3 (Climax): 26.1 words avg ← longest

**Unbiased sentence arc:**
- Section 1 (Setup): 27.4 words avg ← longest
- Section 2 (Development): 21.2 words avg
- Section 3 (Climax): 15.87 words avg ← shortest

The unbiased pattern (sentences shorten toward climax) aligns with standard narrative craft — action sequences use shorter, punchier sentences. The biased pattern is atypical and likely incorrect.

### 3. Ground Truth Verification: The Smoking Gun

Scene breaks (`***`) in the manuscript were counted directly:

| Section | **Actual Count** | Biased Report | Unbiased Report |
|---------|------------------|---------------|-----------------|
| Section 1 | **2** | 8 | 2 ✅ |
| Section 2 | **2** | — | 2 ✅ |
| Section 3 | **7** | — | 7 ✅ |
| **Total** | **11** | 17 | 11 ✅ |

**The biased analysis reported 8 scene breaks in Section 1. The actual count is 2.**

This is a 400% overcount — not a rounding error or estimation variance, but **fabricated data**. The biased agent hallucinated 6 scene breaks that do not exist in the manuscript.

The unbiased analysis matches ground truth exactly across all sections.

### 4. Additional Mathematical Verification

| Check | Biased | Unbiased |
|-------|--------|----------|
| Total words ÷ sentences = avg | 62884/3200 = 19.65 (reported 20.5) ❌ | 62884/3076 = 20.44 (reported 21.3) ✅ |
| Pronoun counts | Estimates (~2,600) | Exact (1,682) |
| Scene breaks total | 17 ❌ | 11 ✅ |

The biased analysis used estimates and rounded numbers. The unbiased analysis provided exact counts that verify against source material.

---

## Why Examples Cause Anchoring

### The Anchoring Heuristic

When shown example metrics like "dialogue ratio: 45%", the model:
1. Treats 45% as a "reasonable default"
2. Adjusts observations toward this anchor
3. Reports values that "feel right" rather than counting precisely

### Confirmation Bias

When shown example patterns like "sentence length varies by scene type", the model:
1. Finds evidence supporting this pattern
2. Downplays contradictory evidence
3. Fits observations to match expected conclusions

### Template Compliance Over Observation

With a structured template containing examples, the model:
1. Prioritizes filling all fields
2. Generates plausible-looking data to complete sections
3. Uses estimates when precise counting is tedious

---

## The Mechanism

Examples don't function as **format templates** — they function as **cognitive anchors**.

The LLM treats examples as "ground truth to approximate" rather than "structure to fill with fresh data."

```
INTENDED BEHAVIOR:
  Example → "This is the format, now analyze the actual content"

ACTUAL BEHAVIOR:
  Example → "These are reasonable values, generate similar ones"
```

---

## Prompt Engineering Guidelines

### ✅ DO Provide

| Element | Purpose | Example |
|---------|---------|---------|
| Output structure | Format guidance | JSON schema, section headers |
| Field definitions | Clarity | "dialogue_ratio: percentage of words in dialogue" |
| Scope instructions | Boundaries | "Analyze sections 1-3 independently" |
| Quality criteria | Standards | "Provide exact counts, not estimates" |

### ❌ DON'T Provide

| Element | Risk | Example |
|---------|------|---------|
| Example values | Anchoring | "dialogue_ratio: 45%" |
| Sample metrics | Bias toward average | "average sentence: 18-22 words" |
| Pattern conclusions | Confirmation bias | "sentence length typically varies by scene" |
| Complete example outputs | Template matching | Full sample analysis |

---

## Recommended Prompt Structure

**Instead of:**
```
Analyze the dialogue ratio. Example output:
{
  "dialogue_ratio": 45,
  "range": [40, 50]
}
```

**Use:**
```
Analyze the dialogue ratio.
- Count total words in dialogue (inside quotation marks)
- Count total words in section
- Calculate percentage
- Report exact values, not estimates

Output format:
{
  "dialogue_ratio": <calculated percentage>,
  "range": [<min across subsections>, <max across subsections>]
}
```

---

## Application to Style Analysis

The `style-analyzer` agent should:

1. **Request raw observation first** — Let the model discover patterns before naming them
2. **Avoid metric examples** — Don't suggest what "typical" values look like
3. **Require exact counts** — Force precise measurement over estimation
4. **Validate mathematically** — Check that reported values are internally consistent
5. **Apply formatting post-analysis** — Structure the output after raw analysis is complete

---

## Implications Beyond Style Analysis

This finding applies to any LLM task requiring:
- Quantitative analysis
- Pattern discovery
- Comparative assessment
- Data extraction

**Rule of thumb:** When you want genuine analysis, give the model a blank canvas with structural scaffolding, not a paint-by-numbers template.

---

## References

- `fine-tuning/data/styles/visions_of_gaea/ANALYSIS_COMPARISON.md` — Full quantitative comparison
- `.smaqit/history/2025-11-30_style_analysis_comparison_and_enhancement.md` — Session history
- `.github/agents/style-analyzer.md` — Agent using unbiased approach
