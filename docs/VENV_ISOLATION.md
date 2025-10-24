# RAG Virtual Environment Isolation

## Why Separate Virtual Environments?

### Avoids Dependency Conflicts

RAG uses an isolated virtual environment at `~/.venvs/rag` instead of sharing `~/.venvs/llm` with vLLM.

**Key conflicts prevented:**
- vLLM requires `openai==2.3.0` while RAG uses `openai==1.54.3`
- ChromaDB and LangChain add 30+ dependencies that could conflict with vLLM's stack
- Allows independent updates without cross-contamination

**Benefits:**
- ✅ Zero dependency conflicts
- ✅ Clean separation (GPU inference vs CPU document processing)
- ✅ Independent updates
- ✅ Easier debugging

### Environment Structure

```
~/.venvs/
├── llm/          # vLLM + PyTorch GPU stack (existing)
│   ├── vllm==0.10.2
│   ├── torch==2.8.0 (CUDA 12.8)
│   ├── flashinfer==0.3.0
│   └── openai==2.3.0
│
└── rag/          # RAG tools (new, isolated)
    ├── chromadb==0.4.22
    ├── sentence-transformers==2.2.2
    ├── langchain-community==0.2.16
    ├── langchain-text-splitters==0.2.4
    └── openai==1.54.3
```

## Setup and Usage

### One-Time Installation
```bash
cd ~/scifi-llm/RAG
./0_create_venv_with_deps.sh
```

Creates `~/.venvs/rag/` with all dependencies (chromadb, sentence-transformers, langchain, openai).

### Daily Usage
```bash
./1_ingest.py              # Auto-uses rag venv
./2_embed_and_store.py     # Auto-uses rag venv
./3_test_retrieval.py      # Auto-uses rag venv
./4_query.py "question"    # Auto-uses rag venv
```

**No manual activation needed!** Scripts use direct shebang: `#!/home/ruifrvaz/.venvs/rag/bin/python3`

### Manual Activation (Optional)
```bash
# For interactive Python work
source ~/.venvs/rag/bin/activate
```

## Communication Between Environments

```
┌─────────────────────┐
│   vLLM Server       │
│   (llm venv)        │
│   localhost:8000    │
└──────────┬──────────┘
           │ HTTP API
           │ (OpenAI compatible)
           │
┌──────────▼──────────┐
│   RAG Scripts       │
│   (rag venv)        │
│   OpenAI client     │
└─────────────────────┘
```

- **vLLM**: Runs in `llm` venv, serves on port 8000
- **RAG**: Runs in `rag` venv, queries vLLM via HTTP
- **Protocol**: OpenAI-compatible API (no shared Python dependencies needed!)

## Independent Updates

```bash
# Update RAG tools without touching vLLM
source ~/.venvs/rag/bin/activate
pip install --upgrade chromadb sentence-transformers

# Update vLLM without touching RAG
source ~/.venvs/llm/bin/activate
pip install --upgrade vllm
```

## Disk Space

### vLLM Environment (~8GB)
- PyTorch with CUDA: ~3GB
- vLLM + dependencies: ~2GB
- FlashInfer: ~500MB
- Transformers + models: ~2GB
- Other packages: ~500MB

### RAG Environment (~4GB)
- ChromaDB: ~200MB
- sentence-transformers: ~500MB
- Embedding models (cached): ~2GB
  - bge-large-en-v1.5: ~1.5GB
- LangChain: ~300MB
- Other packages: ~1GB

**Total**: ~12GB for both environments (acceptable on modern systems)

## Troubleshooting

**"ImportError: No module named chromadb"**
→ RAG venv not created yet: `./0_create_venv_with_deps.sh`

**"ModuleNotFoundError: No module named sentence_transformers"**

### "Connection refused" in Step 4
→ vLLM server not running: `cd .. && ./serve_vllm.sh`

### RAG script uses wrong Python
→ Make scripts executable: `chmod +x *.py`
→ Run with `./script.py` not `python script.py`


