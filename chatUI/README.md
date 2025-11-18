# Chat UI - VS Code Integration

The final component of the complete local AI writing system: **VS Code with Continue.dev** for ChatGPT-like interface with RAG-enhanced responses.

## System Overview

```
1. vLLM Server (Port 8000)
   ↓
2. RAG Proxy (Port 8001) → Auto-injects worldbuilding context
   ↓
3. Fine-Tuned Model (Optional) → Your personal writing style
   ↓
4. VS Code + Continue.dev → Chat interface (THIS COMPONENT)
```

## Prerequisites

- vLLM server installed (`vllm/setup/` completed)
- RAG system installed (`RAG/setup/` completed)
- VS Code installed
- Documents embedded in RAG database

## Setup (5 minutes)

### Step 1: Install Continue.dev Extension

```bash
# Install from command line
code --install-extension Continue.continue

# Or manually in VS Code:
# 1. Press Ctrl+Shift+X
# 2. Search "Continue"
# 3. Install "Continue - Codestral, Claude, and more"
```

### Step 2: Configure Continue.dev

Edit `~/.continue/config.yaml`:

```yaml
name: Local Config - vLLM + RAG
version: 1.0.0
schema: v1
models:
  - name: Llama 3.1 8B (RAG-Enhanced Writing)
    provider: openai
    model: meta-llama/Llama-3.1-8B-Instruct
    apiBase: http://localhost:8001/v1
    apiKey: EMPTY
    contextLength: 100000
    completionOptions:
      temperature: 0.85
      maxTokens: 2000
    roles:
      - chat
      - edit
      - apply
  - name: Llama 3.1 8B (Direct - No RAG)
    provider: openai
    model: meta-llama/Llama-3.1-8B-Instruct
    apiBase: http://localhost:8000/v1
    apiKey: EMPTY
    contextLength: 100000
    completionOptions:
      temperature: 0.85
      maxTokens: 2000
    roles:
      - chat
  - name: Llama 3.1 8B (Autocomplete)
    provider: openai
    model: meta-llama/Llama-3.1-8B-Instruct
    apiBase: http://localhost:8000/v1
    apiKey: EMPTY
    contextLength: 8000
    completionOptions:
      temperature: 0.7
      maxTokens: 200
    roles:
      - autocomplete
```

**Key Configuration Points:**
- **Port 8001** = RAG-enhanced (retrieves worldbuilding)
- **Port 8000** = Direct vLLM (no context retrieval)
- **Temperature 0.85** = Creative writing balance
- **maxTokens 2000** = Long-form responses

### Step 3: Start Servers

**Terminal 1 - vLLM Server:**
```bash
cd ~/scifi-llm
./serve_vllm.sh

# Wait for: "Uvicorn running on http://0.0.0.0:8000"
```

**Terminal 2 - RAG Proxy:**
```bash
cd ~/scifi-llm
./serve_rag_proxy.sh scifi_world

# Wait for: "Uvicorn running on http://0.0.0.0:8001"
```

**Verify servers are running:**
```bash
curl http://localhost:8000/health  # vLLM
curl http://localhost:8001/health  # RAG proxy
```

### Step 4: Test in VS Code

1. Open any markdown file in VS Code
2. Press **Ctrl+L** to open Continue chat panel
3. Select "Llama 3.1 8B (RAG-Enhanced Writing)" from dropdown
4. Type: "Write a 200-word science fiction scene about a captain discovering an anomaly"
5. Observe response uses your worldbuilding context

## Usage

### Chat Panel (Ctrl+L)

**Open chat sidebar:**
```
Press Ctrl+L
```

**Ask questions:**
```
"Write a scene where Elena meets the Arcturian ambassador"
"What are the limitations of FTL drives in my universe?"
"Continue this chapter maintaining the established tone"
```

**Model selection:**
- **RAG-Enhanced Writing**: Uses worldbuilding context (recommended)
- **Direct - No RAG**: Generic responses without context
- Switch between them to compare behavior

### Inline Editing (Ctrl+I)

1. Select text in your manuscript
2. Press **Ctrl+I**
3. Type instruction: "Make this more dramatic"
4. Continue rewrites the selection

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+L` | Open chat panel |
| `Ctrl+I` | Inline edit selection |
| `Ctrl+Shift+R` | Refactor selection |
| `Ctrl+Shift+M` | Add file to context |

## Testing RAG Integration

### Test 1: Compare RAG vs Direct

**Prompt:** "Write a 200-word scene about Captain Vasquez"

**With RAG (Port 8001):**
- Uses "Elena Vasquez" (from character profile)
- References "Phobos Incident" (from background)
- Shows "calm under pressure" (from personality traits)
- Mentions crew like "Lieutenant Patel" (diverse names)

**Without RAG (Port 8000):**
- Generic captain name
- No specific background
- Generic personality
- Random crew names

### Test 2: Worldbuilding Consistency

**Prompt:** "Describe an Arcturian city"

**With RAG:**
- References "floating cities" (from worldbuilding)
- Mentions "gravity-well generators" (from technology)
- Includes "telepathic communication" (from species traits)

**Without RAG:**
- Generic sci-fi city description
- No connection to established lore

### Test 3: Technical Accuracy

**Prompt:** "Explain how FTL drives work"

**With RAG:**
- "Quantum foam manipulation" (from tech docs)
- "30-second blackout" (from limitations)
- "Jump sickness" side effects (from documentation)
- "50 light-year range" (specific details)

**Without RAG:**
- Generic warp drive description
- No specific limitations
- Inconsistent with established universe

## Comparison: RAG-Enhanced vs Direct

### Example Output Analysis

**See:** `chatUI/test doc.md`

**Sample A (Direct vLLM):**
```
Captain Orion gazed out at the swirling vortex...
Ensign Vashin called out...
```
- Generic names
- No universe connection
- Generic personality

**Sample B (RAG-Enhanced):**
```
Captain Vasquez's eyes narrowed...
Lieutenant Patel replied...
"temporal fluctuations," Dr. Rodriguez called out...
```
- Uses Elena Vasquez (from RAG)
- Crew names consistent with worldbuilding
- References "temporal" effects (from FTL documentation)
- Character behavior matches personality profile

**Result:** RAG successfully injects worldbuilding context, making responses consistent with your established universe.

## Configuration Options

### For Creative Writing (Default)
```yaml
completionOptions:
  temperature: 0.85        # Creative but not random
  top_p: 0.95             # Diverse word choices
  presence_penalty: 0.6   # Avoid repetition
  frequency_penalty: 0.3  # Slight variation
  maxTokens: 2000         # Longer responses
```

### For Technical Descriptions
```yaml
completionOptions:
  temperature: 0.6        # More factual
  maxTokens: 800
```

### For Dialogue
```yaml
completionOptions:
  temperature: 0.9        # Natural variation
  presence_penalty: 0.7   # Unique voices
  maxTokens: 1500
```

## Troubleshooting

### "Model not responding"
```bash
# Check servers
curl http://localhost:8000/health
curl http://localhost:8001/health

# Restart if needed
cd ~/scifi-llm
./stop_vllm.sh && ./serve_vllm.sh
./stop_rag_proxy.sh && ./serve_rag_proxy.sh scifi_world
```

### "Responses don't use my worldbuilding"
```bash
# Verify RAG has documents
cd ~/scifi-llm/RAG
ls -lh data/

# Re-embed if needed
./1_ingest.py
./2_embed_and_store.py --collection scifi_world

# Test retrieval
./benchmarks/4_query.py --interactive --collection scifi_world
```

### "Wrong model in Continue dropdown"
- Click model dropdown in chat panel
- Select "Llama 3.1 8B (RAG-Enhanced Writing)"
- Verify it shows port 8001 in config

### "Chat panel not opening"
- Verify Continue.dev extension installed
- Press `Ctrl+Shift+P` → "Continue: Open Config"
- Check config.yaml syntax is valid

## Adding More Worldbuilding

### Step 1: Add Documents
```bash
# Copy your worldbuilding files
cp ~/my-novel/characters/*.md ~/scifi-llm/RAG/data/
cp ~/my-novel/worldbuilding/*.md ~/scifi-llm/RAG/data/
```

### Step 2: Re-embed
```bash
cd ~/scifi-llm/RAG
./1_ingest.py
./2_embed_and_store.py --collection scifi_world
```

### Step 3: Restart RAG Proxy
```bash
# Ctrl+C in RAG proxy terminal, then:
cd ~/scifi-llm
./serve_rag_proxy.sh scifi_world
```

### Step 4: Test New Context
In VS Code Continue chat:
```
"What do you know about [new character/place]?"
```

Should retrieve and reference your new documents.

## Using Fine-Tuned Models

If you've trained a fine-tuned model (`fine-tuning/merged_models/`):

### Option 1: Replace Base Model
```bash
# Serve fine-tuned instead of base
./serve_vllm.sh "fine-tuning/merged_models/llama-3.1-8b-your-style"
```

Update Continue config:
```yaml
model: llama-3.1-8b-your-style  # Changed from base model
```

### Option 2: Run Both (Two Ports)
```bash
# Terminal 1: Base model
./serve_vllm.sh "meta-llama/Llama-3.1-8B-Instruct" 8000

# Terminal 2: Fine-tuned
./serve_vllm.sh "fine-tuning/merged_models/llama-3.1-8b-your-style" 8002

# Terminal 3: RAG proxy (points to 8000 or 8002)
./serve_rag_proxy.sh scifi_world
```

Add to Continue config:
```yaml
- name: Fine-Tuned + RAG
  provider: openai
  model: llama-3.1-8b-your-style
  apiBase: http://localhost:8002/v1  # Different port
  apiKey: EMPTY
  roles:
    - chat
```

## Performance

**Typical Response Times:**
- RAG retrieval: ~50ms
- Model generation: 2-5 seconds
- Total response: 3-6 seconds

**Factors affecting speed:**
- Context length (longer = slower)
- Output length (maxTokens)
- Model size (7B faster than 14B)
- GPU utilization

## Advanced: Custom Context

Modify `RAG/serve_rag_proxy.py` to customize retrieval:

```python
# Adjust retrieval parameters
def retrieve_context(query: str, top_k: int = 5) -> str:
    # For character queries, search more broadly
    if "character" in query.lower():
        top_k = 10
    
    # For worldbuilding, prioritize recent documents
    if "planet" in query.lower() or "species" in query.lower():
        # Add recency weighting
        pass
    
    # Existing retrieval logic...
```

## Complete System Status

✓ **vLLM Server** - GPU-accelerated inference  
✓ **RAG Proxy** - Automatic worldbuilding injection  
✓ **Fine-Tuning** - Personal writing style (optional)  
✓ **Chat UI** - VS Code + Continue.dev integration  

**Your local AI writing system is complete!**

## See Also

- **Main README:** `~/scifi-llm/README.md`
- **vLLM Setup:** `~/scifi-llm/vllm/VLLM_SETUP.md`
- **RAG Setup:** `~/scifi-llm/RAG/RAG_SETUP.md`
- **Fine-Tuning:** `~/scifi-llm/fine-tuning/FINE_TUNING_SETUP.md`
- **VS Code Guide:** `~/scifi-llm/docs/VSCODE_WRITING_SETUP.md`
