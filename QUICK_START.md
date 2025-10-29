# VS Code Science Fiction Writing Setup

Complete local AI writing environment for science fiction with automatic worldbuilding context injection, optional fine-tuning for your writing style, and VS Code integration.

## Quick Setup Overview

1. **Install vLLM** - Get the LLM server running (15 minutes)
2. **Install RAG** - Add worldbuilding context retrieval (10 minutes)
3. **Fine-tune** - Train on your writing style (optional, 2-4 hours)
4. **VS Code Setup** - Configure writing environment (5 minutes)

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

- RTX 5090 GPU (or compatible NVIDIA GPU)
- Ubuntu 22.04+ or similar Linux distribution
- Python 3.12+
- CUDA 12.8 or 13.0
- VS Code installed
- Science fiction documents ready (for RAG)
- Personal documents ready to be converted to data sets (for fine tuning)

---

## Step 1: Install vLLM Server (15 minutes)

### 1.1: Run Setup Scripts

```bash
cd ~/scifi-llm/vllm/setup

# Run setup sequence (0-7)
./0_hf_login.sh              # HuggingFace authentication
./1_check_gpu.sh             # Verify GPU compatibility
./2_cuda_install.sh          # CUDA toolkit (if needed)
./3_sys_pkgs.sh              # System dependencies
./4_create_venv.sh           # Creates ~/.venvs/llm
./5_install_torch.sh         # PyTorch with CUDA
./6_install_llm_stack.sh     # vLLM + FlashInfer
./7_env_export.sh            # Environment variables
```

### 1.2: Start vLLM Server

```bash
cd ~/scifi-llm
./serve_vllm.sh
# Wait for: "Uvicorn running on http://0.0.0.0:8000"
```

### 1.3: Verify Installation

```bash
# Terminal 2: Test the server
curl http://localhost:8000/health
curl http://localhost:8000/v1/models

# Run health checks
cd ~/scifi-llm/vllm/health_checks
./9_health.sh               # Basic API validation
./10_concurrency.sh         # Parallel requests test
```

**Default model:** `meta-llama/Llama-3.1-8B-Instruct` (128k context, ~16GB VRAM)

See `vllm/VLLM_SETUP.md` for detailed setup instructions.

---

## Step 2: Install RAG System (10 minutes)

### 2.1: Install Dependencies

```bash
cd ~/scifi-llm/RAG
setup/0_create_venv_with_deps.sh
```

Creates `~/.venvs/rag` with ChromaDB, embeddings, and document processing tools.

### 2.2: Organize Your Documents

```bash
cd ~/scifi-llm/RAG

# Create structure
mkdir -p data/{characters,worldbuilding,chapters,style-guides}

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

### 2.3: Process Documents

```bash
cd ~/scifi-llm/RAG

# Chunk and embed
setup/1_ingest.py
setup/2_embed_and_store.py --collection scifi_world

# Verify retrieval works
benchmarks/3_test_retrieval.py --collection scifi_world
# Should show test results with retrieved chunks
```

### 2.4: Start RAG Proxy Server

```bash
# Terminal 3: Start RAG proxy (keeps vLLM running in Terminal 1)
cd ~/scifi-llm
./serve_rag_proxy.sh scifi_world
# Wait for: "RAG Proxy Server ready!"
```

**RAG proxy available at:** `http://localhost:8001`

See `RAG/RAG_SETUP.md` for detailed RAG configuration.

---

## Step 3: Fine-Tuning (Optional, 2-4 hours)

Train a model on your personal writing style for consistent narrative voice.

### 3.1: Install Training Environment

```bash
cd ~/scifi-llm/fine-tuning/setup

# Run setup sequence
./0_create_venv.sh           # Creates ~/.venvs/finetune
./1_install_torch.sh         # PyTorch with CUDA 12.8
./2_install_training_stack.sh # Axolotl + flash-attention
```

**Note:** Training stack installation takes 15-20 minutes (compiling CUDA kernels).

### 3.2: Prepare Training Data

```bash
cd ~/scifi-llm/fine-tuning

# Add your writing samples
mkdir -p data/raw
# Copy 100-1000 examples of your writing (500-2000 tokens each)
# Examples: story excerpts, character dialogues, scene descriptions

# Process data (script creation in progress)
# cd scripts && python 1_prepare_data.py
```

### 3.3: Train Model

```bash
# Configure training (edit as needed)
# Edit: configs/qlora_style_transfer.yaml
# - Set base_model: meta-llama/Llama-3.1-8B-Instruct
# - Adjust epochs, learning rate, batch size

# Start training (script in progress)
# cd scripts && ./2_train_lora.sh
# Estimated time: 2-4 hours for 1000 samples
```

### 3.4: Merge and Deploy

```bash
# Merge LoRA adapter with base model (script in progress)
# cd scripts && python 3_merge_adapter.py

# Serve fine-tuned model
# ./serve_vllm.sh merged_models/llama-3.1-8b-your-style
```

**Status:** Fine-tuning infrastructure ready, data preparation and training scripts in development.

See `fine-tuning/FINE_TUNING_SETUP.md` for complete fine-tuning guide (when ready).

---

## Step 4: Configure VS Code (5 minutes)

### 4.1: Install Extension

**Option A: Continue.dev (Recommended)**
1. Open VS Code
2. Extensions → Search "Continue"
3. Install "Continue - Codestral, Claude, and more"

**Option B: Cody**
1. Extensions → Search "Cody"
2. Install "Cody AI"

### 4.2: Configure Extension

**For Continue.dev**

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

**For Cody**

Settings → Extensions → Cody → Custom Configuration:

```json
{
  "cody.serverEndpoint": "http://localhost:8001",
  "cody.autocomplete.enabled": true
}
```

### 4.3: Test in VS Code

1. Open manuscript in VS Code
2. Press `Ctrl+L` (Continue) or open Cody chat
3. Select "Qwen 2.5 7B - Science Fiction (RAG)"
4. Ask: "Who is Elena Vasquez?"

AI should respond with info from your character documents.

---

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

---

## Daily Usage

### Start Servers (3 options)

**Option A: vLLM only (fastest)**
```bash
cd ~/scifi-llm && ./serve_vllm.sh
# Use http://localhost:8000/v1 in Continue.dev
```

**Option B: vLLM + RAG (recommended for fiction)**
```bash
# Terminal 1: vLLM
cd ~/scifi-llm && ./serve_vllm.sh

# Terminal 2: RAG proxy
./serve_rag_proxy.sh scifi_world
# Use http://localhost:8001/v1 in Continue.dev
```

**Option C: Fine-tuned model + RAG (your writing style)**
```bash
# Terminal 1: Fine-tuned model
cd ~/scifi-llm && ./serve_vllm.sh merged_models/llama-3.1-8b-your-style

# Terminal 2: RAG proxy
./serve_rag_proxy.sh scifi_world
# Use http://localhost:8001/v1 in Continue.dev
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
setup/1_ingest.py
setup/2_embed_and_store.py --collection scifi_world

# 3. Restart RAG proxy (Ctrl+C in Terminal 2)
cd ~/scifi-llm && ./serve_rag_proxy.sh scifi_world
```

---

## Configuration Details

### Port Configuration
- **8000** = Direct vLLM (no RAG, general queries)
- **8001** = RAG proxy (automatic context for writing) ⭐

### Virtual Environments
- **~/.venvs/llm** - vLLM server (isolated)
- **~/.venvs/rag** - RAG system (isolated)
- **~/.venvs/finetune** - Training environment (isolated)

### Components
- **vLLM Server:** GPU-accelerated inference (~16-28GB VRAM)
- **RAG Proxy:** Context injection layer (~2GB RAM, CPU)
- **ChromaDB:** Vector database (~2-4GB disk)
- **Embeddings:** bge-large-en-v1.5 (CPU)
- **Training Stack:** Axolotl + flash-attention (GPU)

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
- Chunk overlap: 200 chars (maintains continuity)
- Embedding: bge-large-en-v1.5 (semantic understanding)
- Temperature: 0.85 (creative but consistent)
- Top-K: 5 chunks (balanced context)
- Presence penalty: 0.6 (reduces repetition)

### Model Options
- meta-llama/Llama-3.1-8B-Instruct (default, stable, 128k context - 100k max for rtx 5090)
- Qwen/Qwen2.5-7B-Instruct (excellent creative writing, 128k)
- casperhansen/qwen2.5-14b-instruct-awq (best quality, 128k, ~10GB VRAM)

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
benchmarks/4_query.py --interactive --collection scifi_world
> Query: "test your specific content"
```

### "Wrong/outdated context"
```bash
# Re-embed everything
cd ~/scifi-llm/RAG
setup/1_ingest.py
setup/2_embed_and_store.py --collection scifi_world
# Restart proxy (Ctrl+C in Terminal 2, then:)
cd ~/scifi-llm && ./serve_rag_proxy.sh scifi_world
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

### Setup Guides
- **vLLM Setup:** `vllm/VLLM_SETUP.md` (complete installation)
- **RAG Setup:** `RAG/RAG_SETUP.md` (detailed implementation)
- **Fine-tuning Setup:** `fine-tuning/FINE_TUNING_SETUP.md` (training guide)
- **VS Code Integration:** `docs/VSCODE_WRITING_SETUP.md` (advanced config)

### Quick References
- **vLLM Commands:** `docs/VLLM_QUICK_REFERENCE.md`
- **RAG Workflow:** `RAG/README.md`
- **Creative Writing:** `docs/SCIENCE_FICTION_WRITING_GUIDE.md`
- **Context Optimization:** `docs/CONTEXT_COMPLETE_GUIDE.md`

### Workflow Guides
- **Concurrency Tuning:** `docs/CONCURRENCY_OPTIMIZATION_GUIDE.md`
- **RAG Retrieval:** `docs/RAG_RETRIEVAL_GUIDE.md`
- **Environment Isolation:** `docs/VENV_ISOLATION.md`

---

**You're ready to write with an AI that remembers your entire universe!** 🚀
