# Science Fiction Writing with Local LLMs

## Hardware Specifications

**GPU:** NVIDIA RTX 5090 (Blackwell)
- VRAM: 32GB total
- Compute Capability: sm_120 (8.9)
- Requires PyTorch 2.8.0+ with CUDA 12.8+ for full support
- Requires `VLLM_ATTENTION_BACKEND=FLASHINFER`
- Minimum `max_seqs=9` (FlashInfer warmup requirement)

**System Memory:**
- Total RAM: 64GB DDR5
- WSL2 allocation: 48GB (REQUIRED for flash-attention compilation)
- Configured in `C:\Users\<username>\.wslconfig`:
  ```ini
  [wsl2]
  memory=48GB
  processors=12
  ```
- Restart WSL after changes: `wsl --shutdown` (PowerShell)
- See: `docs/history/2025-11-02_flash_attention_wsl_memory_issue.md`

**Software Environment:**
- OS: Windows 11 + WSL2 (Ubuntu 22.04)
- CUDA: 12.8 (training) / 13.0 (inference)
- Python: 3.12.3
- PyTorch: 2.8.0+cu128 (vLLM + fine-tuning, RTX 5090 Blackwell sm_120 support)
- Virtual Environments: ~/.venvs/{llm, rag, finetune}

## Primary Use Case

**VS Code-based science fiction writing** with RAG-enhanced local model:
- Author writes in VS Code with Continue.dev extension
- Extension queries port 8001 (RAG proxy server)
- RAG proxy auto-retrieves context from worldbuilding documents
- Every query gets relevant character profiles, plot details, world lore
- Maintains continuity across long-form fiction

**Features:**
- Setup scripts for one-time installation and validation
- Local vLLM server (port 8000) with OpenAI-compatible API
- RAG proxy server (port 8001) for context retrieval
- Supports models with 128k token context (e.g., Qwen 2.5-7B-Instruct) - Unconfirmed
- Benchmark suite for creative writing quality and coherence
- Health checks for API, concurrency, function calling
- VS Code with Continue.dev extension (see chatUI/README.md)
- Fine-tuning workflow for personal narrative style - READY (QLoRA/LoRA configs, scripts, guide)

## Starting or resuming chats

To ensure continuity across chat sessions, **When user starts new chat with "analyze" or "recap":**
- **Always read the latest history file first** (`docs/history/` sorted by date)
- **Always read all readme files** (e.g., RAG/README.md, vllm/README.md)
- **Always scan the tasks folder to see if there are any open tasks**
- Use all this content to understand recent changes and decisions then proceed with standard analysis and suggestions


## Finalizing chats

**When user says "wrap up" or "summarize":**
- **Create history file if session qualifies as significant** (see Documentation Philosophy)
- Filename: `docs/history/YYYY-MM-DD_description.md`
- Include: Actions taken, problems solved, decisions made, files modified, next steps
- Focus on **what** and **why**, not implementation details
- Update this history file as the session reference for next chat
- **Do NOT create** separate RESUME or TODO files (history file serves this purpose)

## Task Management

**When user types "create task - [title]":**
- Create new task file in `tasks/` directory
- Filename: `tasks/NNN_task_title.md` (NNN = next available number, zero-padded to 3 digits)
- Include: Title, priority (1-5, where 1=highest), description, acceptance criteria
- Tasks are numbered sequentially starting at 001

**When user types "what's next" or asks about tasks:**
- Read all task files in `tasks/` directory
- Show as many tasks as the user asks sorted by priority (1 first) then by number
- Display: number, title, priority
- Limit to top 5-10 tasks unless user requests more

**Task file format:**
```markdown
# [Task Title]

**Priority:** [1-5]  
**Status:** Not Started | In Progress | Completed | Blocked  
**Created:** YYYY-MM-DD

## Description
[Clear description of what needs to be done]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Notes
[Optional additional context]
```

## Documentation Philosophy

**Update core documentation to reflect current state:**
- **Always update** markdown guides when making changes
- Show how things work NOW (not historical evolution except on history files)
- Update file structure diagrams to include new folders
- Update script docstrings for consistency

**Documentation file placement rules:**
- ✅ **All guide/reference documentation** → `docs/` directory only
- ✅ **Component-specific setup guides** → `{component}/*_SETUP.md` (e.g., `RAG/RAG_SETUP.md`, `fine-tuning/FINE_TUNING_SETUP.md`)
- ✅ **Component README files** → `{component}/README.md` (e.g., `RAG/README.md`, `vllm/README.md`)
- ✅ **History/changelog files** → `docs/history/YYYY-MM-DD_description.md`
- ❌ **DO NOT create** standalone `.md` files in component directories (use docs/ instead)
- ❌ **DO NOT create** `WORKFLOW.md`, `GUIDE.md`, or similar in component folders (use docs/)

**Exception:** Only `README.md` and `*_SETUP.md` files are allowed outside `docs/`. All other documentation goes in `docs/`.

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

## Virtual Environment Dependency Map

**~/.venvs/llm (vLLM inference):**
- PyTorch: 2.8.0+cu128
- vLLM: 0.10.2
- FlashInfer: 0.3.0
- Purpose: Run vLLM server for inference

**~/.venvs/rag (RAG system):**
- PyTorch: 2.8.0+cu128
- ChromaDB: Latest
- Sentence-Transformers: Latest
- Purpose: Document embedding and retrieval

**~/.venvs/finetune (Training):**
- PyTorch: 2.8.0+cu128 (MUST match vLLM for compatibility)
- Axolotl: main branch (installed with `--no-deps` to avoid torch pins)
- DeepSpeed: Latest
- Purpose: QLoRA/LoRA fine-tuning

## WSL Configuration (CRITICAL for Fine-Tuning)

**Flash-attention compilation requires significant memory allocation.**

**Required configuration (`C:\Users\<username>\.wslconfig`):**
```ini
[wsl2]
memory=48GB
processors=12
```

**After editing, restart WSL:**
```powershell
# Windows PowerShell (run as administrator)
wsl --shutdown
wsl
```

**Why this is needed:**
- Flash-attention compiles C++/CUDA kernels from source
- Each compilation job uses ~2-4GB RAM
- Default WSL allocation (50% of system RAM) insufficient
- Without proper config, WSL crashes during `pip install flash-attn`
- Script uses `MAX_JOBS=1` to prevent crashes even with 48GB

**See:** `docs/history/2025-11-02_flash_attention_wsl_memory_issue.md`

## Setup Script Organization

**vLLM inference setup (`vllm/setup/`):**
```
0_create_venv.sh          → Create ~/.venvs/llm
1_install_pytorch.sh      → PyTorch 2.8.0+cu128
2_install_vllm.sh         → vLLM + FlashInfer
3_install_flash_attn.sh   → Flash Attention 2
4_download_models.sh      → Cache models
5_install_openai.sh       → API client
6_verify_gpu.sh           → Test CUDA/GPU
7_test_installation.sh    → End-to-end validation
```

**RAG system setup (`RAG/setup/`):**
```
0_create_venv_with_deps.sh → Create ~/.venvs/rag + all dependencies
1_ingest.py                → Parse markdown to chunks
2_embed_and_store.py       → Create ChromaDB collections
```

**Fine-tuning setup (`fine-tuning/setup/`):**
```
0_create_venv.sh           → Create ~/.venvs/finetune
1_install_torch.sh         → PyTorch 2.8.0+cu128
2_install_axolotl.sh       → Axolotl from main (--no-deps)
3_install_training_stack.sh → DeepSpeed + flash-attention + monitoring
```

**Before modifying ANY setup script:**
1. **Script numbering convention** - Setup scripts are numbered 0-n in sequence order
2. **Check for conflicts** - Don't create duplicate numbers (e.g., two scripts named `2_*.sh`)
3. **Virtual environment isolation** - `~/.venvs/{llm, rag, finetune}` have different dependencies
4. **Dependency alignment** - PyTorch versions MUST match across related scripts

**Script Numbering Rules (NEVER VIOLATE):**
```
0-n:     Setup workflow (run ONCE in SEQUENCE)
n+1-t:   Health checks and utilities (run as needed)
Other:   Descriptive names (benchmarks, servers, monitors)
```

**Examples of CORRECT numbering:**
- ✅ vLLM setup: 0_create_venv.sh → 1_install_pytorch.sh → 2_install_vllm.sh → 3_install_flash_attn.sh
- ✅ RAG setup: 0_create_venv_with_deps.sh → 1_ingest.py → 2_embed_and_store.py
- ✅ Fine-tuning: 0_create_venv.sh → 1_install_torch.sh → 2_install_axolotl.sh → 3_install_training_stack.sh
- ❌ WRONG: Two scripts both named `2_*.sh` in same directory
- ❌ WRONG: Skipping numbers (0 → 2 → 4)

**When creating new setup scripts:**
1. Check existing numbered scripts in that directory
2. Use next available number in sequence
3. Update ALL documentation to reflect new sequence
4. Read complete workflow 0→n to verify order

## Setup Script Troubleshooting Philosophy

**When dependency or installation issues arise:**
- ❌ **DO NOT** propose installing packages manually, such as via `pip install`
- ❌ **DO NOT** suggest one-off fixes outside the setup workflow
- ✅ **DO** identify the root cause in the setup script
- ✅ **DO** fix the issue directly in the appropriate setup script
- ✅ **DO** update script documentation to reflect the fix, no need to mention there was a fix
- ✅ **DO** update documentation to reflect the latest fixed state
- ✅ **DO** document the issue in docs if significant
- ✅ **DO** verify the complete setup sequence still works (0→n)

**Examples:**
- Missing dependency `torchao`: Fix in `2_install_axolotl.sh`, NOT `pip install torchao`
- Flash-attention error: Fix in `3_install_training_stack.sh`, NOT manual reinstall
- Version mismatch: Update dependency list in setup script, NOT override

**Rationale:**
- Setup scripts are the source of truth
- Manual fixes don't persist across environments
- Future users hit the same issues
- Reproducibility requires complete, working setup sequence

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

**Fine-tuning voice comparison (fine-tuning/benchmarks/1_voice_comparison.py):**
- Transfer score: Measures style adoption (0-100%)
- Target: >60% for production deployment
- Compares baseline vs fine-tuned model outputs
- Metrics: vocabulary, sentence structure, style markers, tone
- Run before training (baseline) and after (comparison)

## Project Conventions

**Script numbering:**
- 0-n: Setup workflow (run once in sequence)
- n+1-t: Health checks and utilities
- Benchmarks use descriptive names (1_throughput.sh, 3_creative_quality.py)
- Server launchers not numbered (kept at root for quick access)

**Error handling:**
- All bash scripts use `set -euo pipefail`
- Scripts echo progress with prefixes: `[TEST]`, `[OK]`, `[ERROR]`, `[WARN]`
- Non-zero exits on failures

**Documentation style:**
- Tables for comparisons (not prose)
- Direct commands over explanations
- Specific numbers (not ranges)
- No "Let me explain", emojis or motivational language

**Tone configurations:**
Creative quality benchmark supports 5 writing tones with distinct generation parameters in `TONE_CONFIGS` dict. Each tone has system prompt in `SYSTEM_PROMPTS` dict.

**Key metrics from `/metrics`:**
- `vllm:prompt_tokens_total` - Input tokens processed
- `vllm:generation_tokens_total` - Output tokens generated
- `vllm:request_success_total` - Completed requests
- Monitor via `monitor_vllm.sh` for real-time tracking

## File Organization

```
scifi-llm/
├── serve_vllm.sh, serve_rag_proxy.sh        # Server launchers
├── stop_vllm.sh, stop_rag_proxy.sh          # Graceful shutdown
├── monitor_vllm.sh, monitor_rag_proxy.sh    # Real-time monitoring
├── monitor_training.sh                      # Fine-tuning progress monitor
├── QUICK_START.md                           # VS Code setup guide
├── RAG/                       # Science fiction writing RAG system
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
│   ├── data/                        # Source documents (user-created)
│   │   └── example_vllm_reference.md  # Example document
│   ├── chunks/                      # Processed chunks (auto-generated)
│   └── chroma_db/                   # Vector store (auto-generated)
├── vllm/
│   ├── README.md, VLLM_SETUP.md     # Documentation
│   ├── setup/                       # 0-7: Installation sequence
│   ├── health_checks/               # 9-13: Testing tools
│   └── benchmarks/                  # Creative writing performance tests
│       ├── 1_throughput.sh, 2_context_scaling.sh
│       ├── 3_creative_quality.py      # Writing assessment (5 tones)
│       ├── 4_long_context_coherence.py  # Story continuity
│       ├── 5_model_comparison.sh
│       ├── README.md
│       └── results/                   # JSON outputs with timestamps
├── docs/
│   ├── CONCURRENCY_OPTIMIZATION_GUIDE.md
│   ├── CONTEXT_COMPLETE_GUIDE.md
│   ├── FINE_TUNING_GUIDE.md         # Complete fine-tuning guide
│   ├── QLORA_TRAINING_GUIDE.md      # QLoRA training method guide
│   ├── RAG_RETRIEVAL_GUIDE.md
│   ├── SCIENCE_FICTION_WRITING_GUIDE.md
│   ├── VENV_ISOLATION.md
│   ├── VLLM_QUICK_REFERENCE.md
│   ├── VSCODE_WRITING_SETUP.md
│   └── history/                     # Architecture change logs
├── fine-tuning/                     # Style transfer training (QLoRA/LoRA)
│   ├── README.md, FINE_TUNING_SETUP.md  # Documentation
│   ├── setup/                       # Installation scripts (0-3)
│   │   ├── 0_create_venv.sh
│   │   ├── 1_install_torch.sh       # PyTorch 2.8.0+cu128 (RTX 5090 sm_120)
│   │   ├── 2_install_axolotl.sh     # Axolotl from main (no torch pins)
│   │   └── 3_install_training_stack.sh  # DeepSpeed + flash-attention + monitoring
│   ├── configs/                     # Training configs
│   │   ├── qlora_style_transfer.yaml
│   │   └── lora_style_transfer.yaml
│   ├── training/                    # Training workflow scripts
│   │   ├── 1_prepare_data.py
│   │   └── 2_train_lora.sh
│   ├── benchmarks/                  # Voice comparison tests
│   │   ├── README.md                    # Benchmarking guide
│   │   ├── 1_voice_comparison.py        # Pre/post style metrics (TODO)
│   │   ├── 2_style_consistency.py       # Variance analysis (TODO)
│   │   ├── 3_blind_evaluation.py        # Human evaluation (TODO)
│   │   ├── test_prompts.json            # Standard test set
│   │   ├── utils/                       # Style analysis functions (TODO)
│   │   └── results/                     # Benchmark outputs (auto-generated)
│   ├── data/
│   │   ├── raw/                     # Training source files
│   │   ├── processed/               # JSONL training data
│   │   └── validation/
│   ├── checkpoints/                 # Training checkpoints (auto-generated)
│   ├── merged_models/               # Final models for vLLM (auto-generated)
│   └── logs/                        # Training logs (auto-generated)
└── chatUI/                          # Chat interface (optional)
```

## When Making Changes

**Writing documentation:**
- Direct commands, specific numbers
- No copy-paste examples
- Keep examples up-to-date with current file paths and folder names

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