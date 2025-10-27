# Agentic Science Fiction Writing Environment

## Hardware Specifications

**GPU:** NVIDIA GeForce RTX 5090
- VRAM: 32GB (32607 MiB)
- Compute Capability: 8.9 (Blackwell architecture)
- CUDA Cores: 21,760
- Tensor Cores: 680 (5th gen)

**CPU:** AMD Ryzen 9 7900X3D
- Cores: 12 physical cores
- Threads: 24 (SMT enabled)
- Architecture: Zen 4 with 3D V-Cache
- Base Clock: 4.4 GHz, Boost: 5.6 GHz

**Memory:**
- System RAM: 64GB DDR5 (Kingston)
- WSL2 Current Allocation: 32GB (can be increased to 48GB)
- Recommended WSL2: 48GB (leaves 16GB for Windows)

**Software Environment:**
- OS: Windows 11 + WSL2 (Ubuntu 22.04)
- CUDA: 12.8 (training) / 13.0 (inference)
- Python: 3.12.3
- PyTorch: 2.8.0 (vLLM), 2.10.0 (fine-tuning)
- Virtual Environments: ~/.venvs/{llm, rag, finetune}

## Primary Use Case

**VS Code-based science fiction writing** with RAG-enhanced local model:
- Author writes in VS Code with Continue.dev extension - NOT implemented yet
- Extension queries port 8001 (RAG proxy server)
- RAG proxy auto-retrieves context from worldbuilding documents
- Every query gets relevant character profiles, plot details, world lore
- Maintains continuity across long-form fiction

**Features:**
- Local vLLM server (port 8000) with OpenAI-compatible API
- RAG proxy server (port 8001) for context retrieval
- Supports models with 128k token context (e.g., Qwen 2.5-7B-Instruct) - Unconfirmed
- Benchmark suite for creative writing quality and coherence
- Health checks for API, concurrency, function calling
- Setup scripts for one-time installation and validation
- VS Code with Continue.dev extension - NOT implemented yet
- Fine-tuning workflow for personal narrative style - READY (QLoRA/LoRA configs, scripts, guide)

## Documentation Philosophy

**Update core documentation to reflect current state:**
- **Always update** markdown guides when making changes
- Show how things work NOW (not historical evolution)
- Update file structure diagrams to include new folders
- Update script docstrings for consistency

**Create history files for significant changes only:**
- New architectural decisions (e.g., markdown parsing strategy)
- New major features (e.g., automatic test logging)
- Dependency changes affecting workflow
- Save to `docs/history/YYYY-MM-DD_description.md`

**What qualifies as "significant":**
- ✅ New dependencies added to environment
- ✅ New output folders/files created
- ✅ Changed workflow steps or script behavior
- ✅ Format changes (e.g., JSON logging added)
- ❌ Bug fixes in existing scripts
- ❌ Documentation typo corrections
- ❌ Minor parameter tweaks

## History Documentation Guidelines

When creating or updating files in `docs/history/`, follow these principles:

### ✅ DO Include:
- **Actions taken** - What was done, what problem was solved
- **Function/method names** - e.g., `save_query_result()`, `lifespan()`
- **Package versions** - e.g., `httpx 0.27.2`, `FastAPI 0.119.0`
- **Key concepts** - Explain what and why, not how
- **Test results** - Metrics, distances, tokens, outcomes
- **Decisions and rationale** - Why choices were made
- **Files modified** - List with brief description of changes

### ❌ DO NOT Include:
- **Full code blocks** - No multi-line code examples
- **Line-by-line changes** - Describe changes, don't show them
- **Import statements** - Unless critical to understanding
- **Detailed code segments** - Keep it high-level
- **Implementation details** - Readers can check actual files

## Philosophy

History documents should tell the **story** of what happened, not serve as a code repository. 

- Focus on **decisions**, not **implementations**
- Focus on **outcomes**, not **procedures**
- Focus on **concepts**, not **syntax**

**When updating scripts:**
1. Modify the script implementation
2. Update script docstring to match (supported formats, dependencies, output)
3. Update README.md sections that reference the script
4. Update QUICK_START.md if file structure or outputs changed
5. Create history file if architectural (optional for minor changes)

**Goal**: Someone reading docs gets accurate picture of current system without digging through git history.

## Architecture

```
VS Code + Continue.dev → Port 8001 (RAG Proxy) → Port 8000 (vLLM)
                              ↓
                         Auto-retrieves:
                         - Character profiles
                         - Worldbuilding details
                         - Plot continuity
                         - Style guides
```

Local LLM development environment for RTX 5090 running vLLM with FlashInfer backend, optimized for agentic science fiction writing with RAG-enhanced context retrieval.

## Core Components

- `serve_vllm.sh` - Server launcher (OpenAI-compatible API on port 8000)
- `monitor_vllm.sh` - Real-time token/memory tracking
- `stop_vllm.sh` - Graceful shutdown with resource cleanup
- `RAG/` - Retrieval-augmented generation for worldbuilding/character consistency (see `RAG/RAG_SETUP.md`)
- `vllm/setup/` - One-time installation scripts (0-7 numbered sequence)
- `vllm/health_checks/` - Validation tools (9-13 numbered)
- `vllm/benchmarks/` - Performance testing suite for creative writing quality

**Key Technical Constraints:**
- RTX 5090 requires `max_seqs=9` minimum (FlashInfer warmup limitation)
- Using `max_seqs < 9` causes `ValueError: could not broadcast input array from shape (9,) into shape (N,)`
- FlashInfer backend mandatory: `export VLLM_ATTENTION_BACKEND=FLASHINFER`
- Python 3.12.3 + PyTorch 2.8.0 + vLLM 0.10.2 + FlashInfer 0.3.0

**Environment:**
- Virtual env: `~/.venvs/llm`
- Always activate before operations: `source ~/.venvs/llm/bin/activate`
- Model cache: `~/.cache/huggingface/hub`

## Essential Workflows

### Daily Startup (Science Fiction Writing)
```bash
# Terminal 1: Start vLLM server
./serve_vllm.sh

# Terminal 2: Start RAG proxy
./serve_rag_proxy.sh scifi_world

# VS Code: Open manuscript, use Continue.dev extension
# Configure: http://localhost:8001/v1 (RAG-enhanced)
```

### Adding New Worldbuilding Documents
```bash
# Copy documents to RAG data directory
cp new_chapter.md ~/scifi-llm/RAG/data/chapters/

# Re-embed documents
cd ~/scifi-llm/RAG
./1_ingest.py
./2_embed_and_store.py

# Restart RAG proxy (Ctrl+C in Terminal 2, then:)
cd ~/scifi-llm
./serve_rag_proxy.sh scifi_world
```

### VS Code Configuration (Continue.dev)
**File:** `~/.continue/config.json`
```json
{
  "models": [{
    "title": "Qwen 2.5 7B (RAG-Enhanced)",
    "provider": "openai",
    "model": "Qwen/Qwen2.5-7B-Instruct",
    "apiBase": "http://localhost:8001/v1",
    "apiKey": "EMPTY",
    "contextLength": 100000,
    "completionOptions": {
      "temperature": 0.85,
      "maxTokens": 2000
    }
  }]
}
```

**See `docs/VSCODE_WRITING_SETUP.md` for complete VS Code setup guide.**

## Essential Workflows

### Start/Stop Server
```bash
# Default model (Llama-3.1-8B, 32k context for speed)
./serve_vllm.sh

# Custom model with specific context
./serve_vllm.sh "Qwen/Qwen2.5-14B-Instruct" 8000 9 64000 0.90
# Args: MODEL PORT MAX_SEQS CONTEXT GPU_UTIL
# Note: Larger CONTEXT values (100k+) cause 2-3x slowdown

# Stop gracefully
./stop_vllm.sh

# Monitor live (token counts, VRAM, requests)
./monitor_vllm.sh
```

### RAG Integration for Science Fiction Writing
```bash
# See RAG/README.md for complete workflow

# Quick start
cd RAG
./0_create_venv_with_deps.sh
mkdir -p data/{worldbuilding,characters,plots,research}
cp ~/scifi_docs/*.md data/worldbuilding/
./1_ingest.py
./2_embed_and_store.py --model balanced --collection scifi_world
./4_query.py "What are Elena's key traits?" --collection scifi_world
```

### Benchmark Suite
```bash
cd vllm/benchmarks

# Creative writing quality (5 writing tests)
python 3_creative_quality.py technical    # Default
python 3_creative_quality.py creative     # High temp
python 3_creative_quality.py dramatic     # Emotional

# Long context coherence (character/plot consistency)
python 4_long_context_coherence.py

# Compare models automatically
./5_model_comparison.sh

# Results stored in vllm/benchmarks/results/ as timestamped JSON
```

### Health Checks
```bash
cd vllm/health_checks
./9_health.sh           # API validation
./10_concurrency.sh     # 4 parallel requests
python 11_tool_call_test.py  # Function calling
./13_sanity_snapshot.sh # Environment dump
```

## Critical Patterns

### Model Selection
**Creative writing (long context):**
- `meta-llama/Llama-3.1-8B-Instruct` - Default, proven stable, 128k support, ~16GB VRAM
- `Qwen/Qwen2.5-7B-Instruct` - **Superior for fiction**, 128k support, ~14GB VRAM
- `casperhansen/qwen2.5-14b-instruct-awq` - Quantized 14B, best quality, 128k support, ~10GB VRAM

**⚠️ Context window performance impact:** Larger windows (100k+) cause 2-3x slowdown. Start with 32k, increase only if needed.

**Context length for fiction:**
- **Short scenes/dialogues:** 32k tokens (fastest, ~50 tok/s @ 1k input, ~32 tok/s @ 16k)
- **Novel chapters:** 64k tokens (balanced, ~32 tok/s @ 1k, ~6 tok/s @ 48k)
- **Full story arcs:** 100k+ tokens (⚠️ slow, ~32 tok/s @ 1k, ~6 tok/s @ 60k, use only when necessary)

### Context vs Concurrency Tradeoff
```
Available_Context = (32GB - Model_Size) / max_seqs
With max_seqs=9: ~2-3GB per request = 64k-100k token contexts (RTX 5090 max: 100k)
With max_seqs=16: ~1GB per request = 32k token contexts
```

### Benchmark Interpretation
**Creative quality scores (3_creative_quality.py):**
- Overall: Weighted average (25% vocab, 25% structure, 50% creativity)
- Completion rate: % of outputs ending naturally (not hitting max_tokens)
- Target: >80% natural completions for production
- `finish_reason: "stop"` = good, `"length"` = truncated

**Long context coherence (4_long_context_coherence.py):**
- Tests character consistency over 20k+ words
- Critical for novel-length generation

### Common Issues

**Server won't start:**
```bash
# Kill existing processes
pkill -f "vllm serve"
lsof -i :8000  # Check port usage

# Verify GPU
nvidia-smi
```

**Out of memory:**
- Use AWQ quantized models (`casperhansen/*-awq`)
- Reduce context: `./serve_vllm.sh MODEL 8000 9 64000`
- Lower GPU util: `./serve_vllm.sh MODEL 8000 9 100000 0.85`

**Slow first run:**
- Downloads model files (~16GB for 8B models)
- Compiles CUDA kernels (~30-60s)
- Subsequent starts: ~30s

## Project Conventions

**Script numbering:**
- 0-7: Setup workflow (run once in sequence)
- 8: Server launcher (kept at root for quick access)
- 9-13: Health checks and utilities
- Benchmarks use descriptive names (1_throughput.sh, 3_creative_quality.py)

**Error handling:**
- All bash scripts use `set -euo pipefail`
- Scripts echo progress with prefixes: `[TEST]`, `[OK]`, `[ERROR]`, `[WARN]`
- Non-zero exits on failures

**Documentation style:**
- Tables for comparisons (not prose)
- Direct commands over explanations
- Specific numbers (not ranges)
- No emojis or motivational language
- See `AGENTS.md` for full style guide

**Tone configurations:**
Creative quality benchmark supports 5 writing tones with distinct generation parameters in `TONE_CONFIGS` dict. Each tone has system prompt in `SYSTEM_PROMPTS` dict.

## API Usage

**OpenAI-compatible endpoints:**
```bash
# Base URL: http://localhost:8000

# Chat completion
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Llama-3.1-8B-Instruct",
    "messages": [{"role": "user", "content": "Write a sci-fi scene"}],
    "max_tokens": 500,
    "temperature": 0.9
  }'

# List models
curl http://localhost:8000/v1/models

# Prometheus metrics
curl http://localhost:8000/metrics
```

**Key metrics from `/metrics`:**
- `vllm:prompt_tokens_total` - Input tokens processed
- `vllm:generation_tokens_total` - Output tokens generated
- `vllm:request_success_total` - Completed requests
- Monitor via `monitor_vllm.sh` for real-time tracking

## File Organization

```
scifi-llm/
├── serve_vllm.sh, monitor_vllm.sh, stop_vllm.sh  # Daily operations
├── RAG/                       # Science fiction writing RAG system
│   ├── RAG_SETUP.md                 # Complete RAG setup
│   ├── README.md, RAG_SETUP.md      # Documentation
│   ├── serve_rag_proxy.py           # RAG proxy server
│   ├── setup/                       # Setup scripts
│   │   ├── 0_create_venv_with_deps.sh
│   │   ├── 1_ingest.py
│   │   └── 2_embed_and_store.py
│   ├── benchmarks/                  # Testing and query tools
│   │   ├── 3_test_retrieval.py
│   │   ├── 4_query.py
│   │   ├── query_results/           # Query logs (auto-generated)
│   │   └── test_results/            # Test logs (auto-generated)
│   ├── data/                        # Science fiction materials
│   │   ├── worldbuilding/           # Planets, aliens, technology
│   │   ├── characters/              # Character profiles
│   │   ├── plots/                   # Story outlines
│   │   └── research/                # Scientific background
│   ├── chunks/                      # Processed chunks (auto-generated)
│   └── chroma_db/                   # Vector store (auto-generated)
├── vllm/
│   ├── setup/             # 0-7: Installation sequence
│   ├── health_checks/     # 9-13: Testing tools
│   └── benchmarks/        # Creative writing performance tests
│       ├── 3_creative_quality.py      # Writing assessment (5 tones)
│       ├── 4_long_context_coherence.py  # Story continuity
│       ├── 5_model_comparison.sh
│       └── results/       # JSON outputs with timestamps
├── docs/
│   ├── CONCURRENCY_OPTIMIZATION_GUIDE.md  # max_seqs tuning
│   ├── SCIENCE_FICTION_WRITING_GUIDE.md   # Creative writing tips
│   └── history/           # Benchmark change logs
├── fine-tuning/           # Style transfer training (QLoRA/LoRA)
│   ├── FINE_TUNING_SETUP.md     # Complete training guide
│   ├── README.md                # Quick reference
│   ├── configs/                 # QLoRA and LoRA training configs
│   ├── scripts/                 # Data prep, training, merging
│   ├── data/                    # Training samples (raw/processed)
│   ├── checkpoints/             # Training checkpoints (auto-generated)
│   └── merged_models/           # Final models for vLLM (auto-generated)
├── AGENTS.md              # Documentation style guide
└── VLLM_QUICK_REFERENCE.md  # Quick command reference
```

## When Making Changes

**Documentation update checklist:**
1. **Modify the code/script** - Implement the change
2. **Update script docstrings** - Reflect new behavior, dependencies, outputs
3. **Update README files** - Modify sections describing the script
4. **Update RAG_SETUP.md** - If file structure or outputs changed
5. **Update file structure diagrams** - Add new folders (chunks/, test_results/)
6. **Create history file** - If architecturally significant (see Philosophy section)

**Adding benchmarks:**
- Use descriptive names (not just numbers)
- Save JSON results to `vllm/benchmarks/results/` with timestamps
- Include model name, generation params, and metrics in output
- Log changes to `docs/history/YYYY-MM-DD_description.md`
- Update relevant guides if workflow changes

**Adding RAG components:**
- Follow `RAG/RAG_SETUP.md` for architecture
- Organize materials: `data/{worldbuilding,characters,plots,research}`
- Test retrieval quality: Character consistency, plot continuity
- Use `balanced` or `quality` embedding models for nuanced fiction
- Store collections by project: `--collection story_alpha`
- RAG queries count as normal API calls (monitor with `monitor_vllm.sh`)
- **Update RAG/README.md and RAG_SETUP.md to reflect changes**
- **Create history file if adding dependencies or changing workflow**

**Modifying RAG scripts:**
- Update script docstring: Supported formats, dependencies, process, output
- If adding dependencies: Update `0_create_venv_with_deps.sh` comments and install steps
- If creating new folders: Add to file structure in README.md and RAG_SETUP.md
- If changing outputs: Update "Daily Operations" table in README.md
- Test the complete workflow after changes

**Benchmarking creative writing:**
- `3_creative_quality.py` supports 5 tones: creative, technical, dramatic, poetic, gritty
- Target: >80% natural completions (not hitting max_tokens)
- Test character consistency with `4_long_context_coherence.py`
- Log results to `vllm/benchmarks/results/` with timestamps

**Modifying server config:**
- Test with `vllm/health_checks/9_health.sh` after changes
- Verify concurrency with `10_concurrency.sh`
- Update `VLLM_QUICK_REFERENCE.md` if changing defaults

**Writing documentation:**
- Follow rules in `AGENTS.md` (1000 word max, tables over prose)
- No emojis, no "Let me explain", no motivational language
- Direct commands, specific numbers, copy-paste examples
- Keep examples up-to-date with current file paths and folder names
