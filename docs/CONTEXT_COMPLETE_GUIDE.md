# Complete Context Window Guide for Science Fiction Writing

## 🔄 **Core Concepts**

### **Context Window = Input + Output Combined**
```
Total Context Window = Input Tokens + Output Tokens + System Tokens
```

**Critical Insight:** Output tokens consume the same context space as input tokens. As your story grows, available output space shrinks.

### **Memory Scaling (Quadratic Growth)**
```
Memory = Model_Weights + (Sequence_Length² × Hidden_Size × Layers)
```

**RTX 5090 Limits:**
- **32k context:** ~18GB VRAM
- **64k context:** ~27GB VRAM  
- **100k context:** ~30GB VRAM (RTX 5090 maximum, not 128k)

---

## 📊 **Performance vs Context Tradeoffs**

**CRITICAL:** Context window size dramatically affects generation speed!

| Context Size  | VRAM Usage | Speed @ 8k prompt | Speed @ 32k prompt | Speed @ 48k prompt | Story Capacity |
|---------------|------------|-------------------|--------------------|--------------------|----------------|
| **32k**       | ~18GB      | 50 tok/s          | 26 tok/s           | N/A (exceeds limit)| ~25k words     |
| **64k**       | ~24GB      | 23 tok/s          | 9 tok/s            | 6 tok/s            | ~50k words     |
| **100k**      | ~32GB      | 24 tok/s          | 8 tok/s            | 6 tok/s            | ~80k words     |

**Key Findings (from benchmarks):**
- 32k window: **Fastest** - Use when possible (most writing fits)
- 64k window: **Balanced** - Good for long chapters  
- 100k+ window: **Slowest** - Only for extreme cases (2-3x slower than 32k)
- Performance degrades 70-80% from small to large contexts

---

## 🎯 **Recommended Configurations**

### **RTX 5090 Configurations**

#### **Fast Config (Recommended for most writing)**
```bash
./serve_vllm.sh "meta-llama/Llama-3.1-8B-Instruct" 8000 9 32000
```
- ✅ 32k tokens (~25k words)
- ✅ **Fastest performance** (~50 tok/s @ 8k context)
- ✅ Sufficient for most chapters and scenes
- ✅ Lowest VRAM usage (~18GB)

#### **Balanced Config (Long chapters)**
```bash
./serve_vllm.sh "meta-llama/Llama-3.1-8B-Instruct" 8000 9 64000
```
- ✅ 64k tokens (~50k words)
- ⚠️ Moderate performance (~23 tok/s @ 8k context, ~9 tok/s @ 32k)
- ✅ Good for extended narrative arcs
- ⚠️ Higher VRAM usage (~24GB)

#### **Extended Context (Only when needed)**
```bash
./serve_vllm.sh "casperhansen/llama-3.1-8b-instruct-awq" 8000 9 100000
```
- ✅ 100k tokens (~75k words)
- ❌ **Slow performance** (~24 tok/s @ 8k, ~6 tok/s @ 48k)
- ⚠️ Use only for extreme long-form content
- ⚠️ Near VRAM limit (~30GB)
- ⚠️ **RTX 5090 maximum** (cannot run 128k)
- ✅ Excellent creative writing quality
- ✅ Efficient memory usage

---

## 🚨 **Context Exhaustion: Warning Signs & Prevention**

### **Warning Signs by Usage Level**
- **< 70% full:** ✅ Normal operation
- **70-85% full:** ⚠️ Shorter AI responses, slower generation
- **85-95% full:** 🟠 Very brief responses, start seeing errors
- **> 95% full:** 🚨 HTTP 400 errors, empty responses, "context length exceeded"

### **Critical Error Messages**
```json
{
  "error": {
    "message": "This model's maximum context length is 131072 tokens",
    "type": "invalid_request_error"
  }
}
```

### **Prevention Strategy**
```bash
# Monitor token usage in API responses
curl [...] | jq '.usage'

# Healthy response:
{
  "prompt_tokens": 45000,
  "completion_tokens": 2000,
  "total_tokens": 47000    # 37% of 128k limit
}

# Warning response:
{
  "prompt_tokens": 125000,
  "completion_tokens": 1000,
  "total_tokens": 126000    # 98% of 128k limit!
}
```

---

## 📝 **Context Management Strategies**

### **Strategy 1: Dynamic Response Sizing**
```python
def adaptive_max_tokens(current_usage, context_limit):
    remaining = context_limit - current_usage
    
    if remaining > 20000:
        return 15000  # Large responses OK
    elif remaining > 10000:
        return 5000   # Medium responses  
    elif remaining > 5000:
        return 2000   # Small responses
    else:
        return 500    # Emergency mode
```

### **Strategy 2: Chapter-by-Chapter Workflow**
```bash
1. Write chapter with AI (~30k tokens)
2. Save chapter separately
3. Start fresh session with clean context
4. Reference previous chapters via summary
```

### **Strategy 3: Rolling Context Window**
```bash
Recent content:    60k tokens (detailed)
Plot summary:      10k tokens (compressed)
Available output:  58k tokens (plenty of room)
```

---

## 🔧 **Practical Implementation**

### **Context Health Monitoring Script**
```bash
#!/bin/bash
# Check context usage (adjust limit based on your config)
CONTEXT_LIMIT=64000  # Current RTX 5090 default

RESPONSE=$(curl -s -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hi"}],"max_tokens":1}')

TOTAL_TOKENS=$(echo "$RESPONSE" | jq -r '.usage.total_tokens')
USAGE_PERCENT=$((TOTAL_TOKENS * 100 / CONTEXT_LIMIT))

if [ $USAGE_PERCENT -gt 95 ]; then
    echo "🚨 CRITICAL: ${USAGE_PERCENT}% full - RESET REQUIRED"
elif [ $USAGE_PERCENT -gt 80 ]; then
    echo "⚠️ WARNING: ${USAGE_PERCENT}% full - Monitor closely"
else
    echo "✅ HEALTHY: ${USAGE_PERCENT}% full"
fi
```

### **Emergency Recovery**
```bash
# When context hits 95% full:
1. Save current work
2. Generate story summary (~2k tokens)
3. Start fresh session with summary
4. Continue writing with clean context
```

---

## 🧮 **Capacity Planning for Writers**

### **100k Context Distribution**
```
Available: 100,000 tokens (~75,000 words)

Recommended allocation:
├─Story content:     60,000 tokens (~45,000 words)
├─Character notes:    8,000 tokens (~6,000 words)
├─World building:     8,000 tokens (~6,000 words)
├─Plot outline:       4,000 tokens (~3,000 words)
├─AI responses:      18,000 tokens (~13,500 words)
└─System overhead:    2,000 tokens

Total: 100,000 tokens
```

### **Content Type Guidelines**
| Content Type | Recommended Context | Token Count | Example Use |
|--------------|-------------------|-------------|-------------|
| **Novel Chapter** | 100k | ~75k words | Complete character arcs (RTX 5090 max) |
| **Long Story** | 64k | ~50k words | Major plot developments |
| **Scenes** | 32k | ~25k words | Individual scenes |
| **Dialogue** | 16k | ~12k words | Character interactions |

---

## 💡 **Best Practices Summary**

### **For Science Fiction Writing:**
1. **Start with 32k-64k context** for best speed, use 100k only when necessary
2. **Monitor token usage** in every API response
3. **Reserve 20-30% context** for AI output
4. **Use AWQ models** when you need more context headroom (max 100k on RTX 5090)
5. **Implement chapter breaks** before hitting 90% usage
6. **Keep character/world summaries** for context efficiency

### **Model Recommendations:**
- **Best overall:** `Qwen/Qwen2.5-7B-Instruct` (excellent creative writing)
- **Memory efficient:** `casperhansen/llama-3.1-8b-instruct-awq` (more context headroom)
- **Maximum quality:** `casperhansen/qwen2.5-14b-instruct-awq` (if VRAM allows)

---

## 🎯 **Quick Reference**

```bash
# Start optimized for science fiction
./serve_vllm.sh "Qwen/Qwen2.5-7B-Instruct" 8000 8 65536

# Monitor health
./vllm/health_checks/9_health.sh

# Check context usage
curl -X POST http://localhost:8000/v1/chat/completions [...] | jq '.usage'

# Emergency reset when context full
./stop.sh
./serve_vllm.sh
```