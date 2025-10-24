# Science Fiction Writing Configuration Guide

**Date:** October 16, 2025  
**Focus:** Optimized setups for creative writing with long context

---

## 🚀 **Quick Start for Science Fiction Writing**

### RTX 5090 Default Configuration (64k tokens)
```bash
./serve_vllm.sh
# Uses: Llama-3.1-8B-Instruct with 64k context, 9 sequence slots (RTX 5090 minimum)
```

### Enhanced Context (AWQ Models)
```bash
# For maximum context (100k tokens) on RTX 5090
./serve_vllm.sh "casperhansen/llama-3.1-8b-instruct-awq" 8000 9 100000

# Alternative creative writing model
./serve_vllm.sh "casperhansen/qwen2.5-7b-instruct-awq" 8000 9 100000
```

### RTX 5090 Constraint
All configurations require minimum `max_seqs=9` due to FlashInfer warmup requirements.

## 📚 Context Length Guide for Writers

| Content Type            | Recommended Context | Token Count     | Example                 |
|-------------------------|---------------------|-----------------|-------------------------|
| **Full Novel Chapter**  | 100k tokens         | ~75,000 words   | Complete character arcs |
| **Novella Section**     | 64k tokens          | ~50,000 words   | Major plot developments |
| **Long Short Story**    | 32k tokens          | ~25,000 words   | Complete short stories  |
| **Scene/Dialog**        | 16k tokens          | ~12,000 words   | Single scenes           |
| **Character Sketch**    | 8k tokens           | ~6,000 words    | Character backgrounds   |

### 🎯 **Context Limit Strategy for Writers**

**Key Concept:** Context limit = maximum tokens in ONE single request (input + output combined)

#### Safe Token Planning:
```
For 64k context limit:
- Your story input: 50,000 words = ~53,000 tokens
- AI continuation: 8,000 words = ~11,000 tokens  
- Total: 64,000 tokens = RIGHT AT LIMIT ✅

For 100k context window configuration:
- Your novel chapter: 90,000 words = ~120,000 tokens
- AI response: 6,000 words = ~8,000 tokens
- Total: 128,000 tokens = EXCEEDS LIMIT ❌
- **RTX 5090 Maximum:** 100k tokens (~75,000 words input)
- **Note:** 100k windows cause significant slowdown (~6 tok/s @ 48k+ context)
```

#### What Happens at Context Limit:
- **Error response:** "maximum context length exceeded"
- **Solution:** Reduce input text or max_tokens parameter
- **Remember:** Each request is independent - no accumulation across calls

### 📝 **What Counts as Tokens? (Writer's Guide)**

**Everything you send to the API counts toward your context limit:**

#### Token Breakdown for a Writing Request:
```
Your API Request:
┌─────────────────────────────────────────┐
│ System Prompt:        100 tokens    ✅  │
│ Character Details:    200 tokens    ✅  │
│ World/Ship Lore:      500 tokens    ✅  │
│ Story So Far:      53,000 tokens    ✅  │
│ Your Instruction:      50 tokens    ✅  │
├─────────────────────────────────────────┤
│ INPUT TOTAL:       53,850 tokens        │
│                                         │
│ AI Generated Scene: 1,500 tokens    ✅  │
├─────────────────────────────────────────┤
│ TOTAL CONTEXT:     55,350 tokens        │
│ (out of 64,000 limit)                   │
└─────────────────────────────────────────┘
```

#### Real Writing Scenario:
```
Task: "Write a scene where two characters encounter an enemy ship"

What Counts:
✅ Character names and backstories (Sarah Chen, Marcus Rodriguez)
✅ Ship details (USS Artemis, specifications, crew)
✅ Background lore (Mars refugees, mission details)
✅ Previous chapters (all story context you provide)
✅ Your writing instruction
✅ AI's generated scene

What DOESN'T Count:
❌ JSON formatting (brackets, property names like "role", "content")
❌ API metadata (request ID, timestamps)
❌ HTTP headers
```

#### Context Growth Over Your Novel:

| Writing Stage | Input Tokens | Output Space | Notes |
|--------------|--------------|--------------|-------|
| **Chapter 1** | 5,000 | 59,000 available | Plenty of room! |
| **Chapter 5** | 30,000 | 34,000 available | Still comfortable |
| **Chapter 10** | 60,000 | 4,000 available | Approaching limit ⚠️ |

#### Strategies for Long Novels:

**Strategy 1: Full Context (Early Story)**
- Include entire story history
- Perfect consistency and continuity
- Use when under 50k tokens

**Strategy 2: Summarized Context (Mid Story)**
- Brief summary of early chapters: 3-5k tokens
- Full text of recent chapters: 15-20k tokens
- Room for longer AI responses

**Strategy 3: Rolling Window (Long Novel)**
- Key plot points and character arcs: 3k tokens
- Last 3-5 chapters in full: 15k tokens
- Maximum output capacity: ~45k tokens available

**Pro Tip:** The model doesn't remember previous API calls. Each request is fresh, so you control exactly what context to include!

## Recommended Models for Science Fiction

### Best Overall (Creative + Stable)
```bash
# Qwen2.5-7B - Excellent creative writing, 128k support
# Start with 32k context for speed, increase if needed
./serve_vllm.sh "Qwen/Qwen2.5-7B-Instruct" 8000 9 32000

# Llama-3.1-8B - Default, proven reliable for fiction
./serve_vllm.sh "meta-llama/Llama-3.1-8B-Instruct" 8000 9 32000
```

### Maximum Quality (If VRAM Allows)
```bash
# Qwen2.5-14B AWQ - Best prose quality with efficient memory
./serve_vllm.sh "casperhansen/qwen2.5-14b-instruct-awq"

# Qwen2.5-14B Full - Maximum quality (needs ~28GB VRAM)
./serve_vllm.sh "Qwen/Qwen2.5-14B-Instruct"
```

### Memory Efficient (For Longer Context)
```bash
# Llama-3.1-8B AWQ - Great quality, uses only ~6GB VRAM
./serve_vllm.sh "casperhansen/llama-3.1-8b-instruct-awq"

# Allows much longer context with remaining VRAM (RTX 5090 max: 100k)
./serve_vllm.sh "casperhansen/llama-3.1-8b-instruct-awq" 8000 9 100000
```

## ⚡ Performance vs Context Tradeoffs

### **RTX 5090 (32GB VRAM) Capacity with max_seqs=9:**

| Model + Context | VRAM Usage | Max Story Length | Quality |
|----------------|------------|------------------|---------|
| **Llama-3.1-8B @ 64k** | ~30GB | Novella chapters | ⭐⭐⭐⭐ |
| **Llama-8B-AWQ @ 100k** | ~24GB | Full chapters | ⭐⭐⭐⭐ |
| **Qwen2.5-7B-AWQ @ 100k** | ~22GB | Complete arcs | ⭐⭐⭐⭐⭐ |
| **Qwen2.5-14B-AWQ @ 64k** | ~28GB | Professional prose | ⭐⭐⭐⭐⭐ |

### Recommended Starting Points:

**For Science Fiction Novels:**
```bash
# Best balance of quality and context (meets RTX 5090 min_seqs=9)
./serve_vllm.sh "Qwen/Qwen2.5-7B-Instruct" 8000 9 100000
```

**For Maximum Writing Quality:**
```bash
# Best prose generation (if you have 28GB+ VRAM available)
./serve_vllm.sh "casperhansen/qwen2.5-14b-instruct-awq" 8000 9 100000
```

**For Higher Concurrency:**
```bash
# More simultaneous users with shorter contexts
./serve_vllm.sh "casperhansen/llama-3.1-8b-instruct-awq" 8000 16 64000
```

## 🔧 Usage Examples

### Start High-Context Server
```bash
# 32k context for fast generation (recommended starting point)
./serve_vllm.sh "Qwen/Qwen2.5-7B-Instruct" 8000 9 32000

# 64k context for longer chapters (balanced performance)
./serve_vllm.sh "Qwen/Qwen2.5-7B-Instruct" 8000 9 64000

# Verify it's working
./vllm/health_checks/9_health.sh

# Test with a creative prompt
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen2.5-7B-Instruct",
    "messages": [{"role": "user", "content": "Write the opening scene of a hard science fiction novel set on a generation ship 200 years into its journey to Proxima Centauri. Focus on the daily life of an engineer discovering an anomaly in the ship'"'"'s rotation."}],
    "max_tokens": 2000,
    "temperature": 0.8
  }'
```

### Monitor Performance
```bash
# Real-time vLLM performance monitoring
./monitor_vllm.sh

# Basic VRAM check
nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader
```