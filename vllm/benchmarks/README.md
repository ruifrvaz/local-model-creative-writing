# VLLM Model Benchmarking Suite for Creative Writing

**Purpose:** Compare models for science fiction writing performance, quality, and resource usage.

---

## 📊 Benchmark Scripts

### Core Performance Benchmarks

| Script | Purpose | Metrics | Runtime |
|--------|---------|---------|---------|
| `1_throughput.sh` | Raw generation speed | Tokens/sec, latency | ~3 min |
| `2_context_scaling.sh` | Context length stress test | Speed vs context size | ~5 min |

### Creative Writing Benchmarks

| Script | Purpose | Metrics | Runtime |
|--------|---------|---------|---------|
| `3_creative_quality.py` | Writing quality assessment | Coherence, creativity, style | ~10 min |
| `4_long_context_coherence.py` | Story continuity over long contexts | Character/plot consistency | ~15 min |
| `7_dialog_quality.py` | Dialogue naturalness | Character voice, flow | ~8 min |
| `8_world_building.py` | Complex world descriptions | Detail, consistency | ~12 min |

### Model Comparison

| Script | Purpose | Metrics | Runtime |
|--------|---------|---------|---------|
| `5_model_comparison.sh` | Side-by-side comparison | All metrics across models | ~30 min |

---

## 🚀 Quick Start

### Benchmark Single Model (Current Server)
```bash
cd ~/scifi-llm/vllm/benchmarks

# Run all core benchmarks
./1_throughput.sh
./2_context_scaling.sh

# Test creative quality
python 3_creative_quality.py
python 4_long_context_coherence.py
```

### Compare Multiple Models
```bash
# Automated comparison of top 3 models
./5_model_comparison.sh
```

---

## 📋 Benchmark Categories Explained

### 1. **Throughput** (Speed)
- Measures tokens generated per second
- Tests with various prompt lengths (100, 1k, 10k tokens)
- Identifies optimal operating conditions

### 2. **Context Scaling** (Memory vs Performance)
- Tests 8k, 16k, 32k, 64k, 128k context lengths
- Shows speed degradation with longer contexts
- Helps choose optimal context for your use case

### 3. **Memory Profile** (Resource Efficiency)
- VRAM usage by context length
- Peak memory during generation
- Determines max concurrent users possible

### 4. **Concurrency Stress** (Multi-user)
- Simulates 1, 2, 4, 8, 16 concurrent users
- Measures throughput degradation
- Identifies breaking points

### 5. **Creative Quality** (Writing Assessment)
- Generates same prompts across models
- Compares coherence, creativity, vocabulary
- Subjective quality scoring framework

### 6. **Long Context Coherence** (Story Continuity)
- Tests character consistency over 20k+ words
- Plot coherence across chapters
- Critical for novel-length generation

### 7. **Dialog Quality** (Character Voice)
- Multi-character conversation test
- Voice distinction and naturalness
- Important for fiction writing

### 8. **World Building** (Descriptive Quality)
- Complex scene descriptions
- Technical/scientific accuracy
- Richness of detail

---

## 🎯 Recommended Benchmarking Workflow

### Phase 1: Quick Assessment (10 minutes)
```bash
./1_throughput.sh              # Is it fast enough?
python 3_creative_quality.py   # Does it write well?
```

### Phase 2: Context & Story Consistency (20 minutes)
```bash
./2_context_scaling.sh         # How does context affect speed?
python 4_long_context_coherence.py  # Can it maintain story continuity?
```

### Phase 3: Model Selection (30 minutes)
```bash
python 4_long_context_coherence.py  # Can it maintain story continuity?
```

### Phase 4: Model Comparison (30 minutes)
```bash
./5_model_comparison.sh        # Which model is best for me?
```

---

## 📈 Expected Results (RTX 5090 Baseline)

### Llama-3.1-8B-Instruct (Full Model, 64k context)
```
Throughput:        30-35 tokens/sec
Context Scaling:   35 tok/s @ 8k → 25 tok/s @ 64k
Memory Usage:      ~27GB VRAM @ 64k
Concurrency:       9 users (stable)
Creative Quality:  ⭐⭐⭐⭐ (Excellent for fiction)
Long Coherence:    ⭐⭐⭐⭐ (Strong character/plot consistency)
```

### Qwen2.5-7B-Instruct-AWQ (128k context)
```
Throughput:        35-40 tokens/sec
Context Scaling:   40 tok/s @ 8k → 30 tok/s @ 128k
Memory Usage:      ~22GB VRAM @ 128k
Concurrency:       9 users (stable)
Creative Quality:  ⭐⭐⭐⭐⭐ (Superior creative writing)
Long Coherence:    ⭐⭐⭐⭐⭐ (Excellent continuity)
```

---

## 💾 Output Format

All benchmarks create JSON reports in `results/`:
```
vllm/benchmarks/results/
├── throughput_llama-3.1-8b_2025-10-17.json
├── context_scaling_qwen2.5-7b-awq_2025-10-17.json
├── creative_quality_comparison_2025-10-17.json
└── summary_report_2025-10-17.md
```

---

## 🔍 Key Metrics for Science Fiction Writing

**Priority Metrics:**
1. ✅ **Long Context Coherence** (most important for novels)
2. ✅ **Creative Quality** (prose, vocabulary, originality)
3. ✅ **Throughput** (writing speed)
4. ✅ **Memory Efficiency** (enables longer contexts)

**Secondary Metrics:**
5. Dialog Quality (character voices)
6. World Building (descriptive richness)
7. Concurrency (multi-user support)

---

## 🎬 Next Steps

After running benchmarks:
1. Review `results/summary_report_*.md`
2. Identify best model for your needs
3. Update `serve_vllm.sh` default model
4. Fine-tune server settings based on results
