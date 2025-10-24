# RAG System for Science Fiction Writing

This directory contains a complete Retrieval-Augmented Generation workflow for science fiction writing, enabling AI agents to maintain consistency across long-form fiction by retrieving relevant worldbuilding, character, and plot context.

## Directory Structure

```
RAG/
├── README.md                   # This file
├── RAG_SETUP.md               # Detailed setup and implementation guide
├── serve_rag_proxy.py         # Transparent RAG proxy server
├── setup/
│   ├── 0_create_venv_with_deps.sh # Dependencies installation
│   ├── 1_ingest.py                # Document chunking
│   └── 2_embed_and_store.py       # Embedding generation
├── benchmarks/
│   ├── 3_test_retrieval.py        # Search quality testing
│   ├── 4_query.py                 # Direct query interface
│   ├── test_results/              # Retrieval test logs (auto-generated)
│   └── query_results/             # Query logs (auto-generated)
├── data/                      # Science fiction documents
│   ├── characters/            # Character profiles
│   ├── worldbuilding/         # Planets, species, technology
│   ├── chapters/              # Plot summaries, outlines
│   └── style-guides/          # Writing conventions
├── chunks/                    # Processed document chunks (auto-generated)
└── chroma_db/                 # Vector database (auto-generated)
```

## Initial Setup (Run Once)

Execute the RAG workflow scripts in order:

```bash
cd ~/scifi-llm/RAG

# Step 0: Install dependencies in isolated environment
setup/0_create_venv_with_deps.sh  # Creates ~/.venvs/rag

# Step 1: Organize your science fiction materials
mkdir -p data/{characters,worldbuilding,chapters,style-guides}
# Add your documents to appropriate directories

# Step 2: Process documents
setup/1_ingest.py                  # Chunk documents for optimal retrieval
setup/2_embed_and_store.py --collection scifi_world  # Generate semantic embeddings

# Step 3: Validate retrieval quality
benchmarks/3_test_retrieval.py --collection scifi_world
```

## Daily Usage

### Start RAG-Enhanced Writing Environment
```bash
# Terminal 1: Start vLLM server (if not running)
cd ~/scifi-llm && ./serve_vllm.sh

# Terminal 2: Start RAG proxy server
cd ~/scifi-llm && ./serve_rag_proxy.sh scifi_world
# RAG proxy available at: http://localhost:8001
```

### Query Options

**Option A: RAG Proxy Server (Recommended - Transparent)**
```bash
# Works with any OpenAI-compatible tool
curl http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Llama-3.1-8B-Instruct",
    "messages": [{"role": "user", "content": "What are Elena'\''s personality traits?"}]
  }'

# Configure VS Code Continue.dev to use http://localhost:8001/v1
```

**Option B: Direct Query Script**
```bash
# Character consistency check
benchmarks/4_query.py "What are Captain Elena's key personality traits?" --collection scifi_world

# Worldbuilding query  
benchmarks/4_query.py "Describe the Arcturian homeworld atmosphere" --collection scifi_world

# Interactive mode
benchmarks/4_query.py --interactive --collection scifi_world
```

## Daily Operations

| Script | Purpose | Usage |
|--------|---------|-------|
| `setup/0_create_venv_with_deps.sh` | Install RAG dependencies | One-time setup |
| `setup/1_ingest.py` | Chunk documents | When adding new content |
| `setup/2_embed_and_store.py` | Generate embeddings | After ingestion |
| `benchmarks/3_test_retrieval.py` | Validate search quality | After embedding |
| `benchmarks/4_query.py` | Direct RAG queries | Creative writing assistance |
| `serve_rag_proxy.py` | Transparent RAG proxy | Daily writing sessions |

## Integration with Writing Tools

### VS Code + Continue.dev
Configure `~/.continue/config.json`:
```json
{
  "models": [{
    "title": "Qwen 2.5 7B (RAG-Enhanced)",
    "provider": "openai", 
    "model": "Qwen/Qwen2.5-7B-Instruct",
    "apiBase": "http://localhost:8001/v1",
    "apiKey": "EMPTY"
  }]
}
```

### Benefits
- **Automatic Context**: Retrieves relevant worldbuilding details for every query
- **Character Consistency**: Maintains personality traits across chapters
- **Plot Continuity**: References previous story events accurately
- **Style Adherence**: Follows established writing conventions

## Performance

**Expected timings (RTX 5090):**
- Document ingestion: ~10s per 100 documents
- Embedding generation: ~30s per 1000 chunks (CPU)
- Retrieval speed: ~50ms per query
- Total response time: ~3-6s (retrieval + generation)

## Environment Variables

These are set by `RAG/setup/0_create_venv_with_deps.sh` and activated automatically:
- `PYTHONPATH`: Includes RAG modules
- Virtual environment: `~/.venvs/rag`
- ChromaDB persistence: `RAG/chroma_db/`

For complete setup details and troubleshooting, see `RAG_SETUP.md`.