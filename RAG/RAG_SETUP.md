# 🎉 RAG Environment Setup - Science Fiction Writing Assistant

**Setup Status:** ✅ Production Ready  
**Purpose:** Retrieval-Augmented Generation for Long-Form Fiction  
**Integration:** Transparent overlay on vLLM inference server  

---

## 📋 Executive Summary

Complete RAG implementation enabling AI agents to maintain consistency across science fiction writing by retrieving:
- **Worldbuilding Details**: Alien species, planets, technology systems
- **Character Profiles**: Personality traits, development arcs, relationships  
- **Plot Continuity**: Previous events, story progression, narrative threads
- **Style Guidelines**: Voice, conventions, writing patterns
- **Research Materials**: Scientific accuracy, cultural details

### Key Achievement
Transparent RAG proxy that works with any OpenAI-compatible tool while providing automatic context injection for creative writing consistency.

---

## 🏗️ System Architecture

### RAG Pipeline
```
VS Code/Writing Tool → RAG Proxy (8001) → vLLM Server (8000)
                           ↓
                    ChromaDB Vector Store
                    (Character/World/Plot Context)
```

### Components Stack
```
ChromaDB Vector Database
├── bge-large-en-v1.5 Embeddings (CPU optimized)
├── Semantic chunk retrieval (1000 char chunks)
├── Collection-based organization (by project)
└── Persistent storage (~/.venvs/rag)

FastAPI Proxy Server
├── OpenAI-compatible API endpoints
├── Automatic context injection
├── Query logging and analytics
└── Configurable retrieval parameters
```

---

## 📝 Prerequisites

### Running vLLM Server
```bash
# Creative writing optimized model (recommended)
./serve_vllm.sh "Qwen/Qwen2.5-7B-Instruct" 8000 9 128000

# Or default stable model  
./serve_vllm.sh  # Llama-3.1-8B-Instruct

# Verify server is running
curl http://localhost:8000/health
curl http://localhost:8000/v1/models | jq '.data[0].id'
```

### System Requirements
- **Memory**: 4GB RAM for embeddings and vector store
- **Storage**: 2GB for ChromaDB, 1GB for embeddings cache
- **CPU**: Multi-core recommended for embedding generation
- **Network**: Localhost connectivity between RAG proxy and vLLM

---

## 🚀 Step-by-Step Setup

### Step 0: Dependencies Installation
```bash
cd ~/scifi-llm/RAG
setup/0_create_venv_with_deps.sh
```

**What it installs:**
- `chromadb` - Persistent vector database
- `sentence-transformers` - Embedding generation (bge-large-en-v1.5)
- `langchain-community` - Document loading and processing
- `langchain-text-splitters` - Narrative-optimized chunking
- `unstructured` - Markdown/PDF parsing capabilities
- `openai` - Client for vLLM communication
- `fastapi` + `uvicorn` - RAG proxy server

**Creates environment:** `~/.venvs/rag` (isolated from vLLM environment)

### Step 1: Document Organization
```bash
# Create structured data directories
mkdir -p data/{characters,worldbuilding,chapters,style-guides,research}

# Example organization
data/
├── characters/
│   ├── elena-vasquez.md      # Protagonist profile
│   ├── dr-malik.md           # Supporting character
│   └── alien-ambassador.md   # Antagonist details
├── worldbuilding/
│   ├── arcturian-species.md  # Alien race details
│   ├── mars-colony.md        # Setting description
│   └── ftl-technology.md     # Tech explanations
├── chapters/
│   ├── plot-outline.md       # Story structure
│   └── chapter-summaries.md  # Event timeline
├── style-guides/
│   └── narrative-voice.md    # Writing conventions
└── research/
    └── physics-notes.md      # Scientific accuracy
```

### Step 2: Document Ingestion
```bash
setup/1_ingest.py
```

**Process details:**
- Loads `.txt` and `.md` files recursively from `data/` subdirectories
- Splits into 1000-character chunks with 200-character overlap (optimized for fiction)
- Preserves narrative context across chunk boundaries
- Outputs timestamped JSON: `chunks/chunks_YYYYMMDD_HHMMSS.json`
- Creates symlink: `chunks/chunks_latest.json`

**Customization options:**
```bash
# Larger chunks for dense worldbuilding
setup/1_ingest.py --chunk-size 1500 --chunk-overlap 300

# Smaller chunks for dialogue-heavy content
setup/1_ingest.py --chunk-size 600 --chunk-overlap 150

# Force re-processing of all documents
setup/1_ingest.py --force
```

### Step 3: Embedding Generation
```bash
setup/2_embed_and_store.py --collection scifi_world
```

**Process details:**
- Generates semantic embeddings using `bge-large-en-v1.5` (best for creative content)
- Captures character personality nuances and thematic connections
- Stores in persistent ChromaDB collection
- Enables fast semantic similarity search (~50ms per query)

**Collection management:**
```bash
# Separate collections for different projects
setup/2_embed_and_store.py --collection project_alpha
setup/2_embed_and_store.py --collection project_beta

# Different embedding models
setup/2_embed_and_store.py --model balanced  # bge-large-en-v1.5 (default)
setup/2_embed_and_store.py --model speed     # all-MiniLM-L6-v2 (faster)
setup/2_embed_and_store.py --model quality   # all-mpnet-base-v2 (highest quality)
```

### Step 4: Retrieval Testing
```bash
benchmarks/3_test_retrieval.py --collection scifi_world
```

**Validation process:**
- Runs predefined test queries relevant to science fiction writing
- Shows retrieved chunks with relevance scores (distance metrics)
- Validates character consistency and worldbuilding accuracy
- **Automatically saves results**: `test_results/retrieval_test_YYYYMMDD_HHMMSS.json`

**Interactive testing:**
```bash
# Custom query testing
benchmarks/3_test_retrieval.py --interactive --collection scifi_world

# Adjust retrieval parameters
benchmarks/3_test_retrieval.py --top-k 10 --collection scifi_world

# View saved test results
cat test_results/retrieval_test_latest.json | jq
```

**Quality metrics to monitor:**
- **Distance scores**: Lower = better match (typically 0.4-1.3 range)
- **Content relevance**: Retrieved chunks should contain expected information
- **Coverage**: Important details should be findable with reasonable queries

---

## 🔧 Usage Modes

### Mode A: RAG Proxy Server (Production)

**Start the proxy:**
```bash
cd ~/scifi-llm
./serve_rag_proxy.sh scifi_world

# Output confirms readiness:
# [OK] RAG Proxy Server ready!
# Listening on: http://localhost:8001
```

**Benefits:**
- ✅ **Universal compatibility**: Works with any OpenAI-compatible tool
- ✅ **Transparent operation**: Same API, automatic context injection  
- ✅ **Tool integration**: VS Code, Aider, Continue.dev, custom scripts
- ✅ **Parameter control**: Adjust `top_k`, temperature via API
- ✅ **Always-on**: Persistent server for writing sessions

**Usage examples:**
```bash
# curl test
curl http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Llama-3.1-8B-Instruct",
    "messages": [{"role": "user", "content": "Describe Elena'\''s reaction to the alien homeworld"}],
    "top_k": 5
  }'

# Python client
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8001/v1", api_key="EMPTY")
response = client.chat.completions.create(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[{"role": "user", "content": "What are the Arcturian abilities?"}]
)
```

### Mode B: Direct Query Script (Development)

**Interactive queries:**
```bash
# Character development
benchmarks/4_query.py "How does Elena handle leadership pressure?" --collection scifi_world

# Worldbuilding consistency  
benchmarks/4_query.py "What are the limitations of FTL technology?" --collection scifi_world

# Plot continuity
benchmarks/4_query.py "What happened in the last encounter with the alien fleet?" --collection scifi_world

# Interactive session
benchmarks/4_query.py --interactive --collection scifi_world
```

**Advanced options:**
```bash
# More context for complex scenes
benchmarks/4_query.py "question" --top-k 10 --collection scifi_world

# Technical descriptions (lower creativity)
benchmarks/4_query.py "question" --temperature 0.6 --collection scifi_world

# Extended creative responses
benchmarks/4_query.py "question" --max-tokens 1000 --collection scifi_world
```

**Automatic logging:**
- All queries saved to: `query_results/rag_query_YYYYMMDD_HHMMSS.json`
- Includes retrieved context, generation parameters, and response
- Latest result symlinked: `query_results/rag_query_latest.json`

---

## 🔄 Workflow Integration

### VS Code + Continue.dev Setup

**Install Continue.dev extension:**
1. Open VS Code Extensions
2. Search "Continue"
3. Install "Continue - Codestral, Claude, and more"

**Configure `~/.continue/config.json`:**
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

**Writing workflow:**
1. Open manuscript in VS Code
2. Press `Ctrl+L` to open Continue.dev chat
3. Select "Qwen 2.5 7B - Science Fiction (RAG)"
4. Ask questions about characters, plot, worldbuilding
5. AI automatically retrieves relevant context and maintains consistency

### Adding New Content

**When you add new documents:**
```bash
# 1. Add documents to appropriate data/ subdirectory
cp new-character.md ~/scifi-llm/RAG/data/characters/

# 2. Re-process all documents  
cd ~/scifi-llm/RAG
setup/1_ingest.py

# 3. Re-generate embeddings
setup/2_embed_and_store.py --collection scifi_world

# 4. Test retrieval quality
benchmarks/3_test_retrieval.py --collection scifi_world

# 5. Restart RAG proxy (if running)
# Ctrl+C in RAG proxy terminal, then:
cd ~/scifi-llm && ./serve_rag_proxy.sh scifi_world
```

---

## 📊 Configuration Optimization

### Chunk Size Guidelines

| Content Type | Chunk Size | Overlap | Reason |
|--------------|------------|---------|--------|
| Character profiles | 1000 chars | 200 | Preserve personality context |
| Worldbuilding | 1500 chars | 300 | Dense information requires larger chunks |
| Dialogue scenes | 600 chars | 150 | Shorter chunks for conversational flow |
| Technical specs | 800 chars | 200 | Balance detail with searchability |

### Retrieval Parameters

| Scenario | Top-K | Temperature | Use Case |
|----------|-------|-------------|----------|
| Specific facts | 3-5 | 0.6-0.7 | Character names, dates, technical details |
| Creative scenes | 5-7 | 0.8-0.9 | Atmospheric descriptions, emotional contexts |
| Plot development | 7-10 | 0.7-0.8 | Multiple story threads, complex relationships |
| Worldbuilding | 8-12 | 0.6-0.8 | Comprehensive setting details |

### Embedding Model Performance

| Model | Quality | Speed | VRAM | Best For |
|-------|---------|-------|------|----------|
| `bge-large-en-v1.5` | Excellent | Medium | ~2GB | Fiction, nuanced content (default) |
| `all-mpnet-base-v2` | Very Good | Fast | ~1GB | Balanced performance |
| `all-MiniLM-L6-v2` | Good | Very Fast | ~500MB | Quick prototyping |

---

## 🚨 Troubleshooting

### Common Issues

**"ImportError" or "ModuleNotFoundError"**
```bash
# Solution: Ensure RAG environment is created
setup/0_create_venv_with_deps.sh

# Verify installation
source ~/.venvs/rag/bin/activate
python -c "import chromadb, sentence_transformers; print('✅ Dependencies OK')"
```

**"vLLM server not responding"**
```bash
# Solution: Start vLLM server first
cd ~/scifi-llm && ./serve_vllm.sh

# Verify connection
curl http://localhost:8000/health
```

**"Collection not found"**
```bash
# Solution: Generate embeddings first
setup/2_embed_and_store.py --collection scifi_world

# List available collections
python -c "import chromadb; client = chromadb.PersistentClient('./chroma_db'); print(client.list_collections())"
```

**"Poor retrieval quality"**
```bash
# Solution 1: Adjust chunk size for your content
setup/1_ingest.py --chunk-size 1500 --chunk-overlap 300

# Solution 2: Increase retrieval breadth
benchmarks/4_query.py "question" --top-k 10

# Solution 3: Use higher quality embeddings
setup/2_embed_and_store.py --model quality --collection scifi_world
```

**"RAG proxy connection refused"**
```bash
# Solution: Check port availability
ss -tlnp | grep :8001

# Restart proxy server
cd ~/scifi-llm && ./serve_rag_proxy.sh scifi_world
```

### Performance Monitoring

**Check retrieval test logs:**
```bash
# View latest test results
cat test_results/retrieval_test_latest.json | jq '.queries[].results[] | {rank, distance, source}'

# Monitor query performance
tail -f query_results/rag_query_latest.json
```

**Monitor vector database:**
```bash
# Check collection stats
python -c "
import chromadb
client = chromadb.PersistentClient('./chroma_db')
collection = client.get_collection('scifi_world')
print(f'Documents: {collection.count()}')
"
```

---

## 🔮 Advanced Configuration

### Multiple Projects

**Organize by project:**
```bash
# Project Alpha (hard sci-fi)
setup/2_embed_and_store.py --collection alpha_universe
./serve_rag_proxy.sh alpha_universe  # Port 8001

# Project Beta (space opera) 
setup/2_embed_and_store.py --collection beta_universe
./serve_rag_proxy.sh beta_universe  # Configure different port if needed
```

### Custom Embedding Pipeline

**For specialized content:**
```python
# Custom chunking strategy in 1_ingest.py
# Modify CHUNK_SIZE and CHUNK_OVERLAP for your narrative style

# Custom embedding model in 2_embed_and_store.py  
# Switch to domain-specific models for technical or literary content
```

### Integration with Other Tools

**Aider integration:**
```bash
# Use RAG-enhanced model with Aider
aider --openai-api-base http://localhost:8001/v1 --model meta-llama/Llama-3.1-8B-Instruct
```

**Custom scripts:**
```python
# Use RAG proxy in your own scripts
import openai
client = openai.OpenAI(base_url="http://localhost:8001/v1", api_key="EMPTY")
# All requests automatically get RAG context
```

---

For daily usage patterns and quick reference commands, see `README.md`.