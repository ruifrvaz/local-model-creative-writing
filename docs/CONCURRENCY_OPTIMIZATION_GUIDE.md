# vLLM Concurrency Optimization for RTX 5090

## RTX 5090 FlashInfer Requirement

RTX 5090 requires **minimum `max_seqs=9`** for FlashInfer warmup. Lower values cause array broadcast errors.

**Error Pattern:**
```
max_seqs=1: ValueError: could not broadcast input array from shape (9,) into shape (1,)
max_seqs=2: ValueError: could not broadcast input array from shape (9,) into shape (2,)
max_seqs=8: ValueError: could not broadcast input array from shape (9,) into shape (8,)
max_seqs=9: ✅ Works - FlashInfer can complete warmup
```

## Core Tradeoff

Lower `max_seqs` = more VRAM per request = longer context windows + faster generation.

However, RTX 5090 is **locked to minimum `max_seqs=9`** due to hardware/driver requirements.

## Performance Table

**Note:** Speed varies significantly by context window size and current fill level.

| max_seqs | Context Window | Speed @ Low Fill | Speed @ High Fill | VRAM/Request | Use Case |
|----------|----------------|------------------|-------------------|--------------|----------|
| 9 | 32k tokens | ~50 tok/s | ~32 tok/s @ 16k | ~1GB | RTX 5090 (fastest) |
| 9 | 64k tokens | ~32 tok/s | ~6 tok/s @ 48k | ~1.9GB | RTX 5090 (balanced) |
| 9 | 100k tokens | ~32 tok/s | ~6 tok/s @ 60k | ~3GB | RTX 5090 (extended, slow) |

## Optimal Configurations

### RTX 5090 Fast (Recommended Starting Point)
```bash
./serve_vllm.sh "meta-llama/Llama-3.1-8B-Instruct" 8000 9 32000
```
- 32k tokens (~25k words)
- ~50 tok/s @ low context, ~32 tok/s @ 16k
- Best speed for short stories and scenes

### RTX 5090 Balanced (Novel Chapters)
```bash
./serve_vllm.sh "meta-llama/Llama-3.1-8B-Instruct" 8000 9 64000
```
- 64k tokens (~50k words)
- ~32 tok/s @ low context, ~6 tok/s @ 48k
- Good balance for chapter-length fiction

### RTX 5090 Extended Context (Use When Necessary)
```bash
./serve_vllm.sh "casperhansen/llama-3.1-8b-instruct-awq" 8000 9 100000
```
- 100k tokens (~75k words)
- ⚠️ **Slow:** ~32 tok/s @ low context, ~6 tok/s @ 60k+
- AWQ quantization frees VRAM for longer contexts
- Use only when >64k context is required
- **RTX 5090 maximum:** 100k (not 128k)

### High Concurrency (16 sequences)
```bash
./serve_vllm.sh "model" 8000 16 32768
```
- 32k tokens (~25k words)
- Many concurrent users
- Public API usage

## Context vs Concurrency Formula

**RTX 5090 Constraint:** Minimum `max_seqs=9` required by FlashInfer

```
Available_Context = (Total_VRAM - Model_Size) / max_seqs
32GB RTX 5090: (32GB - 15GB) / 9 = ~1.9GB per sequence = 64k tokens

With AWQ (10GB model): (32GB - 10GB) / 9 = ~2.4GB per sequence = ~100k tokens (RTX 5090 max)
```

## Monitoring
```bash
# Check context usage
curl -X POST http://localhost:8000/v1/chat/completions [...] | jq '.usage'

# Monitor VRAM
watch -n 5 "nvidia-smi --query-gpu=memory.used --format=csv,noheader"
```

## Key Takeaway

RTX 5090 requires `max_seqs=9` minimum due to FlashInfer warmup requirements. Use AWQ models to maximize context length within this constraint.

## 🔄 Concurrency Tradeoffs Overview

| Max Sequences | VRAM per Request | Total Context Capacity | Generation Speed | Quality | Best For |
|---------------|------------------|------------------------|------------------|---------|----------|
| **9** | ~1.9GB | 64k tokens | Fast | High | RTX 5090 standard (minimum) |
| **9 (AWQ)** | ~2.4GB | 100k tokens | Fast | High | RTX 5090 with AWQ models (max) |
| **16** | ~1GB | 32k tokens | Medium | Good | Higher concurrency needs |

**Note:** RTX 5090 cannot use `max_seqs < 9` due to FlashInfer requirements.

---

## 💾 VRAM Allocation Deep Dive

### How vLLM Allocates Memory
```
Total VRAM = Model Weights + (KV Cache × Max Concurrent Sequences)
```

**RTX 5090 (32GB) Examples with FlashInfer min_seqs=9:**
```bash
# Standard model (max_seqs=9):
Model: 15GB + KV Cache: 1.9GB × 9 = 32GB total
→ Can handle 64k token contexts

# AWQ model (max_seqs=9):  
Model: 10GB + KV Cache: 2.4GB × 9 = 32GB total
→ Can handle 128k token contexts

# Higher concurrency (max_seqs=16):
Model: 15GB + KV Cache: 1GB × 16 = 31GB total  
→ Limited to ~32k token contexts
```

vLLM Memory Layout (32GB RTX 5090, max_seqs=9):
┌─────────────────────────────────────┐
│ Model Weights: 15GB (FIXED)         │ ← Never changes
├─────────────────────────────────────┤
│ KV Cache Pool: 16GB (PRE-ALLOCATED) │ ← Fixed at startup
│ ├─ Slot 1: [████████░░░░░░░░░░░]    │ ← Partially used
│ ├─ Slot 2: [██░░░░░░░░░░░░░░░░░░]    │ ← Small usage
│ ├─ Slot 3: [░░░░░░░░░░░░░░░░░░░░]    │ ← Empty
│ └─ Slots 4-9: [Empty...]            │
├─────────────────────────────────────┤
│ Workspace: 1GB (VARIABLE)           │ ← Only this changes!
└─────────────────────────────────────┘

### The Key Insight

vLLM **pre-allocates** KV cache memory for ALL possible concurrent sequences, even if they're not being used. Lower concurrency = more memory per sequence = longer possible contexts.

**RTX 5090 Limitation:** FlashInfer requires minimum 9 sequences to be allocated, limiting maximum per-sequence context compared to other GPUs.

---

## ⚡ Performance Benefits of Lower Concurrency

**General Principle:** Lower `max_seqs` values give better performance per request.

**RTX 5090 Reality:** Locked to minimum `max_seqs=9`, so optimizations focus on model choice (AWQ vs full precision) rather than sequence count.

### 1. Generation Speed

```bash
# RTX 5090 with max_seqs=9 (required):
- Minimum context switching overhead
- Good GPU compute per request
- Typical generation: 32-50 tok/s (varies by context window size)

# Higher sequences (max_seqs=16):
- More context switching between requests  
- Shared compute resources
- Slower per-request: 20-30 tokens/s
```

### 2. Context Window Capacity

```bash
# Low concurrency benefits:
✅ Full memory bandwidth per request
✅ Optimal cache utilization  
✅ No memory fragmentation
✅ Better attention computation efficiency

# High concurrency drawbacks:
❌ Memory bandwidth split across requests
❌ Cache thrashing between sequences
❌ Memory fragmentation overhead
❌ Attention computation conflicts
```

### **3. Context Window Capacity**
```bash
# max_seqs=9: Limited to ~64k tokens
# max_seqs=16: Limited to ~32k tokens
```

---

## 🎯 Optimal Configurations for Creative Writing

### **Single Author (Best Performance - RTX 5090 Safe)**
```bash
./serve_vllm.sh "Qwen/Qwen2.5-7B-Instruct" 8000 9 64000
```
**Benefits:**
- ✅ RTX 5090 compatible (meets min_seqs=9 requirement)
- ✅ Good context for novel chapters (64k tokens)
- ✅ Balanced performance (~32 tok/s @ 1k, ~6 tok/s @ 48k)
- ✅ Stable and reliable

### RTX 5090 Maximum Context (AWQ Model)
```bash
./serve_vllm.sh "casperhansen/qwen2.5-7b-instruct-awq" 8000 9 100000
```
**Benefits:**
- ✅ RTX 5090 compatible (meets min_seqs=9 requirement)
- ✅ Extended context for full story arcs (100k tokens - RTX 5090 max)
- ⚠️ **Slower performance** (~32 tok/s @ 1k, ~6 tok/s @ 60k context)
- ✅ Better VRAM efficiency via quantization
- ⚠️ Use only when >64k context is truly necessary

### Multi-User Server (Higher Throughput)
```bash
./serve_vllm.sh "Qwen/Qwen2.5-7B-Instruct" 8000 16 32768
```
**Benefits:**
- ✅ More simultaneous users (up to 16)
- ✅ Good overall throughput
- ❌ Limited context per user (32k)
- ❌ Slower individual responses

---

## 🧠 Why This Matters for Science Fiction Writing

### Context Length Impact

```
RTX 5090 with max_seqs=9:
  - Full models: 64k tokens = Complete chapters
  - AWQ models: 100k tokens = Full story arcs 
  
With max_seqs=16:
  - Full models: 32k tokens = Single scenes
  - AWQ models: 64k tokens = Long scenes
```

### Story Coherence Benefits

**With max_seqs=9 and 32k context:**
- ✅ Best generation speed (~50 tok/s @ small inputs)
- ✅ Good for short stories and scenes
- ⚠️ Limited to ~25k words of context

**With max_seqs=9 and 64k context:**
- ✅ Maintain character consistency across chapters
- ✅ Track plot threads through story arcs
- ✅ Preserve world-building details (~50k words)
- ⚠️ Slower at high context usage (~6 tok/s @ 48k)

**With max_seqs=9 and 100k+ context:**
- ✅ Full novel chapter coherence (~75k+ words)
- ✅ Complex plot thread tracking
- ❌ **Significantly slower** (~6 tok/s @ 60k context)
- ⚠️ Use only when absolutely necessary

---

## 📊 Real-World Performance Testing

### Benchmark Results (RTX 5090, Llama-3.1-8B)

**Note:** Performance heavily depends on context window size, not just max_seqs.

| Concurrency | Context Window | Speed @ 1k Input | Speed @ High Context | Memory Efficiency |
|-------------|----------------|------------------|----------------------|-------------------|
| **9 seqs** | 32k | ~50 tok/s | ~32 tok/s @ 16k | 85% |
| **9 seqs** | 64k | ~32 tok/s | ~6 tok/s @ 48k | 85% |
| **9 seqs** | 100k | ~32 tok/s | ~6 tok/s @ 60k | 85% |
| **16 seqs** | 32k | 22 tok/s | Unknown | 65% |

### Quality Comparison

**32k Config (9 seqs, fastest):**
- Best generation speed (~50 tok/s @ small inputs, ~32 tok/s @ 16k)
- Good for short scenes and dialogues
- Limited context for long-form fiction

**64k Config (9 seqs, balanced):**
- Consistent character voices across chapters
- Good world-building coherence
- Solid plot development
- Reliable dialogue consistency

**AWQ Config (9 seqs, 100k context):**
- Full story arc coherence
- Complex plot thread tracking
- ⚠️ **Significantly slower** (~32 tok/s @ 1k, ~6 tok/s @ 60k)
- Use only when >64k context is truly necessary

**High Concurrency (16 seqs, 32k context):**
- Scene-level consistency only
- Requires frequent character/plot reinforcement
- Simpler narrative structure
- More generic responses due to limited context
- Frequent repetition of character descriptions
- Plot inconsistencies across scene breaks
- Simpler narrative structure

---

## 🔧 Practical Recommendations

### For Science Fiction Novelists (RTX 5090)

```bash
# Recommended: AWQ model for maximum context (RTX 5090 max: 100k)
./serve_vllm.sh "casperhansen/qwen2.5-7b-instruct-awq" 8000 9 100000

# Alternative: Full precision model with standard context
./serve_vllm.sh "Qwen/Qwen2.5-7B-Instruct" 8000 9 64000
```

### For Collaborative Writing

```bash
# Small writing group (2-4 people) - still meets RTX 5090 requirement
./serve_vllm.sh "Qwen/Qwen2.5-7B-Instruct" 8000 9 64000

# Larger team with more concurrent users
./serve_vllm.sh "Qwen/Qwen2.5-7B-Instruct" 8000 16 32768
```

### Model Selection Strategy

**For maximum context on RTX 5090:**
1. Use AWQ quantized models (frees 30-40% VRAM)
2. Keep `max_seqs=9` (FlashInfer requirement)
3. Allocate saved VRAM to longer contexts (100k tokens max on RTX 5090)

---

## ⚠️ **Important Considerations**

### **Memory Pressure Signs**
Watch for these warning signs when pushing context limits:
```bash
# GPU memory monitoring
nvidia-smi dmon -s u -d 1

# Warning signs:
- Memory usage > 95%
- Frequent garbage collection
- Slower response times
- "CUDA out of memory" errors
```

### Context vs Concurrency Calculator

**RTX 5090 with FlashInfer (min_seqs=9):**



---

## 🎯 Key Takeaways

### For RTX 5090 Creative Writing:

1. **Minimum `max_seqs=9`** due to FlashInfer warmup requirement
2. **Context window size matters:** 32k=fastest (~50 tok/s), 64k=balanced (~32→6 tok/s), 100k+=slow (~6 tok/s @ 60k)
3. **Start with 32k or 64k** for best performance, increase only if needed
4. **Full GPU resources** per request = optimal model performance within constraints

### Recommended Starting Point:

```bash
# Best balance of speed and context for RTX 5090
./serve_vllm.sh "Qwen/Qwen2.5-7B-Instruct" 8000 9 32000

# Or for longer chapters (slower but more context)
./serve_vllm.sh "casperhansen/qwen2.5-7b-instruct-awq" 8000 9 64000
```

**32k context = ~25,000 words input, excellent speed (~50 tok/s @ small inputs)**
**64k context = ~50,000 words input, balanced performance (~32 tok/s @ 1k, ~6 tok/s @ 48k)**

---

## 🔍 Testing Your Setup

```bash
# Verify server is running with correct max_seqs
curl http://localhost:8000/health

# Test generation speed
cd vllm/health_checks
./9_health.sh

# Monitor VRAM usage
watch -n 5 "nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader"
```