# VS Code Science Fiction Writing Setup

Complete local AI writing environment for science fiction with automatic worldbuilding context injection. Setup in 15 minutes.

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│  VS Code + Continue.dev Extension                   │
│  (Your writing environment)                         │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ HTTP Request
                  │ "Describe Elena's reaction..."
                  ▼
┌─────────────────────────────────────────────────────┐
│  RAG Proxy Server (Port 8001)                       │
│  ~/scifi-llm/serve_rag_proxy.sh                     │
├─────────────────────────────────────────────────────┤
│  1. Receives query                                  │
│  2. Embeds with bge-large-en-v1.5                   │
│  3. Searches ChromaDB (vector database)             │
│  4. Retrieves top 5 relevant chunks:                │
│     - Elena's character profile                     │
│     - Previous emotional reactions                  │
│     - Relevant chapter context                      │
│  5. Injects into system message                     │
│  6. Forwards to vLLM                                │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ HTTP Forward (augmented prompt)
                  ▼
┌─────────────────────────────────────────────────────┐
│  vLLM Server (Port 8000)                            │
│  ~/scifi-llm/serve_vllm.sh                          │
├─────────────────────────────────────────────────────┤
│  - Llama-3.1-8B or Qwen2.5-7B                       │
│  - GPU inference on RTX 5090                        │
│  - Generates response with full context             │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ Response
                  ▼
            [Back to VS Code]
```

## What You Get

- Local AI co-author running on your GPU
- RAG vector database running on your CPU
- Automatic retrieval of worldbuilding/character context
- Maintains story continuity across chapters
- Private (no cloud APIs, no costs)
- Fast (2-5 second responses)
- Works with any OpenAI-compatible VS Code extension

## Prerequisites

- RTX 5090 GPU
- vLLM installed and working (`./serve_vllm.sh` runs)
- VS Code installed
- Science fiction documents ready

## Step 1: Install RAG (5 minutes)

```bash
cd ~/scifi-llm/RAG
./0_create_venv_with_deps.sh
```

Creates `~/.venvs/rag` with ChromaDB, embeddings, and document processing tools.

## Step 2: Organize Your Documents (5 minutes)

```bash
cd ~/scifi-llm/RAG/data

# Create structure
mkdir -p characters worldbuilding chapters style-guides

# Add your documents (examples)
# Characters: Elena's profile, crew bios
# Worldbuilding: Alien species, planets, technology
# Chapters: Summaries, outlines
# Style: Voice guide, conventions
```

**Example structure:**
```
data/
├── characters/
│   ├── elena-vasquez.md
│   └── dr-malik.md
├── worldbuilding/
│   ├── arcturian-species.md
│   └── ftl-technology.md
├── chapters/
│   └── plot-outline.md
└── style-guides/
    └── narrative-voice.md
```

## Step 3: Process Documents (2 minutes)

```bash
cd ~/scifi-llm/RAG

# Chunk and embed
./1_ingest.py
./2_embed_and_store.py --collection scifi_world

# Verify retrieval works
./3_test_retrieval.py
# Try query: "Elena's personality"
# Should return relevant chunks
```

## Step 4: Install VS Code Extension (1 minute)

**Option A: Continue.dev (Recommended)**
1. Open VS Code
2. Extensions → Search "Continue"
3. Install "Continue - Codestral, Claude, and more"

**Option B: Cody**
1. Extensions → Search "Cody"
2. Install "Cody AI"

## Step 5: Configure Extension (2 minutes)

### For Continue.dev

Create/edit `~/.continue/config.json`:

```json
{
  "models": [
    {
      "title": "Qwen 2.5 7B - Science Fiction (RAG)",
      "provider": "openai",
      "model": "Qwen/Qwen2.5-7B-Instruct",
      "apiBase": "http://localhost:8001/v1",
      "apiKey": "EMPTY",
      "contextLength": 128000,
      "completionOptions": {
        "temperature": 0.85,
        "top_p": 0.95,
        "presence_penalty": 0.6,
        "maxTokens": 2000
      }
    }
  ],
  "tabAutocompleteModel": {
    "title": "Qwen 2.5 7B",
    "provider": "openai",
    "model": "Qwen/Qwen2.5-7B-Instruct",
    "apiBase": "http://localhost:8001/v1",
    "apiKey": "EMPTY"
  }
}
```

### For Cody

Settings → Extensions → Cody → Custom Configuration:

```json
{
  "cody.serverEndpoint": "http://localhost:8001",
  "cody.autocomplete.enabled": true
}
```

## Step 6: Start Servers

```bash
# Terminal 1: vLLM server
cd ~/scifi-llm && ./serve_vllm.sh
# Wait for "Uvicorn running on http://0.0.0.0:8000"

# Terminal 2: RAG proxy
./serve_rag_proxy.sh scifi_world
# Wait for "RAG Proxy Server ready!"
```

## Step 7: Test in VS Code

1. Open manuscript in VS Code
2. Press `Ctrl+L` (Continue) or open Cody chat
3. Select "Qwen 2.5 7B - Science Fiction (RAG)"
4. Ask: "Who is Elena Vasquez?"

AI should respond with info from your character documents.

## How It Works

When you ask "Describe Elena's reaction to the alien homeworld":

1. Continue.dev sends request to port 8001
2. RAG proxy embeds query and searches ChromaDB
3. Retrieves relevant chunks:
   - `characters/elena-vasquez.md` (personality)
   - `worldbuilding/alien-planets.md` (planet details)
   - `chapters/chapter-05.md` (previous reactions)
4. Injects context into system message
5. Forwards augmented request to vLLM (port 8000)
6. vLLM generates contextually-aware response
7. Returns to VS Code

Result: Consistent writing that remembers your universe!

## Daily Usage

### Start Servers
```bash
# Terminal 1: vLLM
cd ~/scifi-llm && ./serve_vllm.sh

# Terminal 2: RAG proxy
./serve_rag_proxy.sh scifi_world
```

### Write in VS Code
- Open manuscript
- `Ctrl+L` to open chat
- AI automatically retrieves context from your documents

### Add New Documents
```bash
# 1. Add document
cp new-character.md ~/scifi-llm/RAG/data/characters/

# 2. Re-process
cd ~/scifi-llm/RAG
./1_ingest.py
./2_embed_and_store.py

# 3. Restart RAG proxy (Ctrl+C in Terminal 2)
cd ~/scifi-llm && ./serve_rag_proxy.sh scifi_world
```

## Configuration Details

### Port Configuration
- **8000** = Direct vLLM (no RAG, general queries)
- **8001** = RAG proxy (automatic context for writing) ⭐

### Components
- **vLLM Server:** GPU-accelerated inference (~18GB VRAM)
- **RAG Proxy:** Context injection layer (~2GB RAM, CPU)
- **ChromaDB:** Vector database (~4GB disk)
- **Embeddings:** bge-large-en-v1.5 (CPU)

### Performance
- Retrieval: ~50ms
- Generation: ~2-5 seconds
- Total: ~3-5 seconds per query

## Keyboard Shortcuts (Continue.dev)

| Shortcut | Action |
|----------|--------|
| `Ctrl+L` | Open chat sidebar |
| `Ctrl+I` | Inline edit with AI |
| `Ctrl+Shift+R` | Refactor selection |
| `Ctrl+M` | Add selection to context |

## Optimization Settings

### Creative Writing Parameters
- Chunk size: 1000 chars (preserves narrative context)
- Embedding: bge-large-en-v1.5 (semantic understanding)
- Temperature: 0.85 (creative but consistent)
- Top-K: 5 chunks (balanced context)
- Presence penalty: 0.6 (reduces repetition)

### Model Options
- Llama-3.1-8B-Instruct (default, stable, 128k context)
- Qwen2.5-7B-Instruct (excellent creative writing, 128k)
- Qwen2.5-14B-Instruct-AWQ (best quality, 128k, 10GB VRAM)

## Troubleshooting

### "Model not responding"
```bash
# Check servers
curl http://localhost:8000/health  # vLLM
curl http://localhost:8001/health  # RAG proxy
```

### "No context from my documents"
```bash
# Test retrieval
cd ~/scifi-llm/RAG
./3_test_retrieval.py --interactive
> Query: "test your specific content"
```

### "Wrong/outdated context"
```bash
# Re-embed everything
cd ~/scifi-llm/RAG
./1_ingest.py --force
./2_embed_and_store.py
# Restart proxy
```

### Monitor Activity
```bash
./monitor_vllm.sh       # GPU usage, token stats
./monitor_rag_proxy.sh  # RAG query logs
```

## Advanced Configuration

See `docs/VSCODE_WRITING_SETUP.md` for:
- Retrieval parameter tuning (`top_k`, chunk size)
- Creative writing parameter customization
- Document templates for consistency
- Pre-prompts for different writing modes

## Additional Documentation

- **Complete Guide:** `docs/VSCODE_WRITING_SETUP.md`
- **RAG Workflow:** `RAG/README.md`
- **Model Options:** `docs/SCIENCE_FICTION_WRITING_GUIDE.md`
- **Quick Reference:** `VLLM_QUICK_REFERENCE.md`

---

**You're ready to write with an AI that remembers your entire universe!** 🚀
