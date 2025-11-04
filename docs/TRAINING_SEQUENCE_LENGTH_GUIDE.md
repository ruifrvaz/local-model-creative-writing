# Training Sequence Length vs Inference Context: Understanding the Difference

## Overview

Training sequence length and inference context window are related but fundamentally different concepts. Understanding this distinction is critical for effective fine-tuning and deployment.

---

## Core Concepts

### Training Sequence Length
**What it is:** Maximum tokens per training example during fine-tuning

**Configuration:**
```yaml
sequence_len: 2048  # In qlora_style_transfer.yaml
```

**How it works:**
- Each training example is processed independently
- Model learns patterns **within** each 2048-token sequence
- **No cross-example attention** - Example 1 cannot attend to Example 2
- Gradient updates based on patterns within individual sequences

### Inference Context Window
**What it is:** Maximum tokens the model can process during generation

**Configuration:**
```bash
./serve_vllm.sh "model_name" 8000 9 64000 0.90
#                                   ^^^^^ context length
```

**How it works:**
- Model processes all tokens in context simultaneously
- Continuous generation, one token at a time
- Each new token attends to **all previous tokens** in context
- No "reset" at sequence boundaries

---

## Key Differences

### 1. Purpose

**Training Sequence Length:**
- Determines what patterns the model can learn
- Defines scope of dependencies during weight updates
- VRAM constrained: longer sequences = more memory needed
- Example: 2048 tokens → model learns patterns within 2k-token windows

**Inference Context Window:**
- Determines what the model can "remember" during conversation
- User can provide 100k tokens of dialogue history
- KV cache constrained: longer context = more GPU memory
- Example: 64k tokens → model maintains coherence across entire context

### 2. How They Relate

**Training on 2048 tokens ≠ Can only generate 2048 tokens**

Your model:
- **Trained on:** 2048-token sequences
- **Can serve:** 128k-token context (Llama 3.1 architecture limit)

**Why this works:**
- Base model (Llama 3.1) pre-trained on sequences up to 128k
- Your fine-tuning adjusts ~0.5% of weights (LoRA rank 64)
- Long-context capability inherited from base model
- Fine-tuning teaches **style**, not **context length**

### 3. Memory Requirements

**Training (2048 sequence):**
```
VRAM = Model weights (quantized 4-bit) 
     + Gradients 
     + Optimizer states 
     + Activations for 2048 tokens
     
Total: ~17GB (QLoRA on RTX 5090)
```

**Inference (64k context):**
```
VRAM = Model weights (full precision)
     + KV cache for 64k tokens
     
Total: ~24GB (vLLM on RTX 5090)
```

**Why training costs less VRAM despite complexity:**
- QLoRA uses 4-bit quantization (vs 16-bit inference)
- Only trains adapters, not full model
- Batch size typically small (1-4 sequences)

---

## The Cross-Chunk Pattern Problem

### How Training Data Gets Chunked

Looking at `fine-tuning/training/1_prepare_data.py`:

```python
def chunk_text(text, min_tokens=500, max_tokens=2000):
    paragraphs = text.split('\n\n')
    
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    for para in paragraphs:
        para_tokens = estimate_tokens(para)
        
        if current_tokens + para_tokens > max_tokens:
            chunks.append('\n\n'.join(current_chunk))  # Save chunk
            current_chunk = [para]                      # Start NEW chunk
            current_tokens = para_tokens
        else:
            current_chunk.append(para)
            current_tokens += para_tokens
```

**Result:** Sequential, non-overlapping chunks

```
Original story (10,000 tokens):
├─ Chunk 1: Paragraphs 1-20    (tokens 0-2000)
├─ Chunk 2: Paragraphs 21-40   (tokens 2000-4000)  ← Starts where chunk 1 ended
├─ Chunk 3: Paragraphs 41-60   (tokens 4000-6000)
└─ Chunk 4: Paragraphs 61-80   (tokens 6000-8000)
```

### What the Model Can and Cannot Learn

**✅ Model WILL Learn (within-chunk patterns):**
- Vocabulary and word choice (appears in any chunk)
- Sentence structure (paragraphs fit in chunks)
- Dialogue patterns (conversations fit in 2k tokens)
- Scene pacing (setup → action → resolution within chunk)
- Technical descriptions (complete explanations in chunk)
- Character voice (personality evident in single scenes)

**❌ Model CANNOT Learn (cross-chunk patterns):**
- Multi-chapter story arcs spanning 6000+ tokens
- Character development across multiple scenes (if scenes in different chunks)
- Foreshadowing → payoff separated by 3000+ tokens
- Plot threads that resolve later than 2048 tokens

### Example: The Broken Pattern Problem

**Original narrative (6000 tokens):**
```
[Tokens 0-2000]:
"Crisis emerges. Elena investigates. Discovers anomaly.
Team debates response. Elena proposes risky solution..."

[Tokens 2000-4000]:
"...but Marcus objects on safety grounds. Council votes.
Elena proceeds cautiously. Initial tests show promise..."

[Tokens 4000-6000]:
"...leading to breakthrough. Solution validated.
Crisis resolved. Elena reflects on risk vs reward."
```

**After chunking into training examples:**

**Training Example 1 (Batch 1):**
```
System: "You are a science fiction author..."
User: "Continue the scene..."
Assistant: "Crisis emerges. Elena investigates... [ends at token 2048]
             ...Elena proposes risky solution"
```

**Training Example 2 (Batch 2 - SEPARATE):**
```
System: "You are a science fiction author..."
User: "Continue the scene..."
Assistant: "but Marcus objects... [starts at token 2000]
             ...Initial tests show promise"
```

**Training Example 3 (Batch 3 - SEPARATE):**
```
System: "You are a science fiction author..."
User: "Continue the scene..."
Assistant: "leading to breakthrough... [starts at token 4000]
             ...Elena reflects on risk vs reward"
```

### What Gets Lost

**The model learns:**
- Example 1: Stories often involve "Elena proposes risky solution" near the end
- Example 2: Stories often start with "but Marcus objects" 
- Example 3: Stories often start with "leading to breakthrough"

**The model does NOT learn:**
- That "Elena proposes risky solution" connects to "but Marcus objects"
- That "Initial tests show promise" leads to "breakthrough"
- The complete narrative arc from crisis → debate → resolution

**Why:** Each training batch processes independently. No attention mechanism connects tokens in Example 1 to tokens in Example 2.

---

## Why This Isn't Catastrophic

### 1. Style Transfer Works Within Chunks

**Your fine-tuning goal:** Teach the model your writing voice

**Voice manifests in:**
- Word choice ✅ (visible in any 500-token sample)
- Sentence rhythm ✅ (evident in paragraphs)
- Technical precision ✅ (shows in descriptions)
- Dialogue style ✅ (clear in conversations)
- Pacing ✅ (scene structure fits in 2k tokens)

**All of these fit comfortably within 2048-token chunks.**

### 2. Base Model Provides Structural Knowledge

**Llama 3.1 pre-training:**
- Trained on millions of complete novels
- Learned: crisis → complication → resolution arcs
- Understands: foreshadowing, character development, plot threads
- Knows: how scenes connect into chapters, chapters into stories

**Your fine-tuning:**
- Doesn't teach story structure (base model already knows)
- Teaches: "Write these structures in MY voice"
- Adjusts: vocabulary, pacing, tone, technical detail level

### 3. Repeated Patterns Get Learned

**If a pattern appears in multiple chunks:**

```
Chunk 1:  [Crisis emerges] → [Technical analysis] → [Debate]
Chunk 5:  [Crisis emerges] → [Technical analysis] → [Debate]
Chunk 12: [Crisis emerges] → [Technical analysis] → [Debate]
```

**Model learns:** "Crisis → Technical analysis → Debate" is a common pattern

**Statistical learning across examples compensates for missing within-example connections.**

### 4. Generation Is Autoregressive, Not Chunked

**Common misconception:**
> "If trained on 2k chunks, will output repeat every 2k tokens?"

**Reality:**
```
Generation process (continuous, no chunks):
Token 1:    Attends to prompt
Token 2:    Attends to [prompt, token 1]
Token 3:    Attends to [prompt, token 1, token 2]
...
Token 5000: Attends to ALL previous 4999 tokens + prompt

No reset. No chunking. Continuous probability flow.
```

**Training chunks affect WHAT patterns are learned, not HOW generation works.**

---

## When Cross-Chunk Patterns Matter

### Scenario 1: Teaching Unique Long-Form Structures

**Problem:**
You have a unique narrative technique spanning 5000 tokens:
- Foreshadowing in chapter 1 (tokens 0-2000)
- Red herrings in chapter 2 (tokens 2000-4000)
- Payoff in chapter 3 (tokens 4000-6000)

This pattern appears **once** in your training data.

**Result:**
Model cannot learn this specific arc structure because chunks are isolated.

**Solution:**
- Use overlapping chunks (50% overlap)
- Increase sequence_len to 4096+ (requires more VRAM)
- Include multiple examples of this arc structure

### Scenario 2: Complex Character Development

**Problem:**
Character transformation across 8000 tokens:
- Chunk 1: Character skeptical of AI
- Chunk 2: Character experiences AI benefits
- Chunk 3: Character becomes AI advocate

**Result:**
Model learns each state independently, not the transformation arc.

**Solution:**
- Ensure transformation arcs fit within 2048 tokens
- Or provide many examples of similar transformations
- Or increase sequence length

### Scenario 3: Mystery/Suspense Structures

**Problem:**
Clue planting and resolution:
- Chunk 1: Subtle clue mentioned (token 500)
- Chunk 4: Clue becomes critical (token 6500)

**Result:**
Model doesn't learn the connection between clue and payoff.

**Solution:**
- Keep mystery arcs within 2048 tokens
- Or use overlapping chunks
- Or accept that base model's mystery structure knowledge is sufficient

---

## Optimization Strategies

### Option 1: Current Approach (Recommended for Style Transfer)

**Configuration:**
```yaml
sequence_len: 2048
sample_packing: false
```

**Pros:**
- ✅ Fits in VRAM (~17GB)
- ✅ Fast training (~5 minutes for 51 examples)
- ✅ Sufficient for learning style
- ✅ Simple data preparation

**Cons:**
- ❌ Cannot learn unique cross-chunk patterns
- ❌ Relies on base model for long-range structure

**Best for:**
- Style transfer
- Voice matching
- Technical vocabulary
- Dialogue patterns

### Option 2: Overlapping Chunks

**Implementation:**
```python
def chunk_with_overlap(text, chunk_size=2000, overlap=1000):
    chunks = []
    start = 0
    
    while start < len(tokens):
        end = start + chunk_size
        chunks.append(tokens[start:end])
        start += (chunk_size - overlap)  # 50% overlap
    
    return chunks
```

**Pros:**
- ✅ Model sees cross-chunk connections
- ✅ Learns patterns spanning chunk boundaries
- ✅ Better for unique long-form structures

**Cons:**
- ❌ Trains on duplicate content (wastes compute)
- ❌ Requires 2x more training examples
- ❌ Slower training (more examples to process)

**Best for:**
- Teaching unique narrative arcs
- Complex character development
- Multi-scene plot structures

### Option 3: Longer Sequences

**Configuration:**
```yaml
sequence_len: 4096  # Double current length
```

**Pros:**
- ✅ Learns longer patterns directly
- ✅ No duplicate training content
- ✅ Better pattern recognition

**Cons:**
- ❌ ~28GB VRAM required (might OOM on RTX 5090)
- ❌ Slower training (2-4x longer)
- ❌ Fewer examples per training run

**Best for:**
- Novel-length fine-tuning
- Complex story arcs
- When VRAM is abundant (A100, H100)

### Option 4: Sample Packing

**Configuration:**
```yaml
sequence_len: 2048
sample_packing: true  # Pack multiple short examples into one sequence
```

**Pros:**
- ✅ Efficient VRAM usage
- ✅ Faster training (less padding)
- ✅ Good for varied-length samples

**Cons:**
- ❌ Introduces artificial transitions between examples
- ❌ Model might learn these transitions as "style"
- ❌ Not recommended for narrative continuity

**Best for:**
- Short writing samples (poems, flash fiction)
- Mixed-length content
- Maximizing throughput

---

## Practical Recommendations

### For Science Fiction Novel Writing (Your Use Case)

**Current setup is optimal:**
```yaml
sequence_len: 2048
sample_packing: false
```

**Rationale:**
1. **Style transfer focus** - Voice fits in 2k tokens
2. **Base model provides structure** - Llama 3.1 knows story arcs
3. **VRAM efficient** - 17GB allows frequent experimentation
4. **Fast iteration** - ~5 min training enables rapid testing

**RAG compensates for long-range patterns:**
- Retrieves character details from worldbuilding docs
- Provides plot context from previous chapters
- Grounds hallucinations with factual references

**Combined approach:**
```
Fine-tuning (2048 tokens):  Teaches your voice
RAG retrieval:              Provides long-range context
Base model:                 Supplies narrative structure
Inference (64k context):    Applies all three during generation
```

### When to Increase Sequence Length

**Increase to 4096 if:**
- Your writing style includes long, continuous scenes (3000+ tokens)
- Unique narrative patterns span multiple chapters
- Character arcs require 3000+ tokens to manifest
- You have 32GB+ VRAM available

**Warning signs current length is limiting:**
- Model generates good style but poor scene transitions
- Character development feels disjointed
- Plot threads introduced but never resolved
- Narrative arcs incomplete even with good prompting

### When to Use Overlapping Chunks

**Use overlaps if:**
- Teaching specific long-form techniques (e.g., mystery structure)
- Training data includes unique patterns not in base model
- Willing to accept 2x training time for better arc learning
- Can dedicate computational resources to experimentation

**Test with:**
- 25% overlap first (less overhead)
- Evaluate if cross-chunk learning improves output
- Balance training cost vs quality gain

---

## Testing Your Model's Limitations

### Experiment 1: Scene Transition Quality

**Prompt:**
```
"Write a complete story arc: Character faces crisis, seeks solution, 
encounters obstacles, achieves resolution. Make it 3000 words."
```

**Evaluate:**
- Does the arc flow naturally?
- Are transitions smooth or choppy?
- Does resolution connect to crisis effectively?

**If poor:** Sequence length might be limiting long-range coherence.

### Experiment 2: Character Development

**Prompt:**
```
"Show character transformation from skeptic to believer over 4000 words.
Include specific turning points and gradual attitude shifts."
```

**Evaluate:**
- Is transformation gradual or sudden?
- Are intermediate states well-developed?
- Does payoff connect to setup?

**If poor:** Model may not have learned transformation arcs from training.

### Experiment 3: Foreshadowing

**Prompt:**
```
"Write opening scene that foreshadows later revelation. 
Then write revelation scene 3000 words later that references the foreshadowing."
```

**Evaluate:**
- Does model maintain connection across 3000 words?
- Is callback to foreshadowing natural?
- Or does it feel disconnected?

**If poor:** Consider longer sequences or overlapping chunks.

---

## Mathematical Deep Dive

### Attention Mechanism During Training

**Within a training batch:**
```
Sequence: [token₁, token₂, ..., token₂₀₄₈]

Attention matrix (causal):
        t₁   t₂   t₃  ... t₂₀₄₈
t₁    [ 1    0    0       0   ]
t₂    [ 1    1    0       0   ]
t₃    [ 1    1    1       0   ]
...
t₂₀₄₈ [ 1    1    1  ...  1   ]
```

**Each token attends to all previous tokens in its sequence.**

**Across training batches:**
```
Batch 1: Sequence A [tokens 1-2048]
Batch 2: Sequence B [tokens 1-2048]  ← SEPARATE, no attention to Batch 1

Attention matrix CANNOT connect:
- Token 2048 from Batch 1
- Token 1 from Batch 2
```

### Gradient Flow Implications

**What gets updated:**
```
Loss computed on: Batch N only
Gradients flow through: Tokens within Batch N only
Weight updates reflect: Patterns in Batch N only
```

**Cross-batch patterns:**
```
If pattern spans Batch 1 → Batch 2:
- Partial pattern in Batch 1 creates gradient G₁
- Partial pattern in Batch 2 creates gradient G₂
- G₁ and G₂ are independent (not coordinated)
- Model learns fragments, not complete pattern
```

**Exception: Statistical repetition:**
```
If same pattern appears complete in multiple batches:
Pattern in Batch 1:  [Setup → Resolution]
Pattern in Batch 5:  [Setup → Resolution]
Pattern in Batch 12: [Setup → Resolution]

Gradients G₁, G₅, G₁₂ all reinforce same pattern
Model learns pattern through repetition across batches
```

### Why Inference Doesn't Chunk

**Generation process:**
```python
context = prompt_tokens
for step in range(max_new_tokens):
    # Attention over ENTIRE context (no limit except max_model_len)
    logits = model(context)  
    
    # Sample next token
    next_token = sample(logits[-1])
    
    # Append to context (continuous growth)
    context = torch.cat([context, next_token])
```

**Key difference:**
- Training: Fixed sequences, isolated batches
- Inference: Growing context, continuous attention

**No "reset" at training sequence boundaries during generation.**

---

## Common Misconceptions

### ❌ Misconception 1: "Trained on 2k chunks = generates in 2k chunks"

**Reality:** Training chunks determine what patterns are learned. Generation is continuous, one token at a time, with full attention to all previous tokens.

### ❌ Misconception 2: "Output will repeat every 2048 tokens"

**Reality:** Repetition occurs due to probability loops, poor prompting, or low temperature - NOT because of training sequence length.

### ❌ Misconception 3: "Can't generate longer than training sequence"

**Reality:** Base model was pre-trained on 128k sequences. Fine-tuning doesn't remove this capability.

### ❌ Misconception 4: "Need sequence_len = max_model_len"

**Reality:** Training on 2048 teaches patterns. Inference at 128k applies those patterns across longer context.

### ❌ Misconception 5: "Overlapping chunks always better"

**Reality:** Overlaps help for unique long-form patterns, but waste compute on style transfer. Trade-offs depend on goals.

---

## Summary

**Training Sequence Length:**
- Defines scope of pattern learning during fine-tuning
- Each example processed independently (no cross-example attention)
- Patterns must fit within sequence_len to be learned directly
- Statistical repetition across examples compensates for chunk isolation

**Inference Context Window:**
- Defines how much context model can process during generation
- Continuous, growing context with full attention
- No relationship to training sequence length
- Limited only by architecture (128k for Llama 3.1) and VRAM

**For Style Transfer:**
- 2048-token sequences sufficient (style visible in short samples)
- Base model provides long-range structure
- RAG provides factual grounding
- No need for longer sequences or overlaps

**For Complex Long-Form Learning:**
- Consider 4096+ sequences or overlapping chunks
- Verify VRAM capacity (longer sequences = more memory)
- Balance training cost vs quality improvement
- Test if base model knowledge already sufficient

**Key Insight:**
Training on 2048-token chunks teaches the model "how to write like you" within scenes. The base model's pre-training provides "how to connect scenes into stories." During inference, both combine across whatever context length you provide (up to 128k).

You're teaching voice and style, not story architecture. The chunks are fine.
