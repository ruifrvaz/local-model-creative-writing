# Local Model Creative Writing

A complete local AI writing environment for science fiction and creative writing, featuring GPU-accelerated inference with vLLM, Retrieval-Augmented Generation (RAG) for worldbuilding consistency, and optional fine-tuning for your personal writing style.

## Overview

This project provides a full-featured, privacy-focused AI writing assistant that runs entirely on your local hardware. No cloud APIs, no monthly subscriptions, no data sharing. Perfect for authors who want AI assistance while maintaining complete control over their creative work.

### What You Get

- **Local LLM Server**: GPU-accelerated inference using vLLM with OpenAI-compatible API
- **RAG System**: Automatic retrieval of worldbuilding, character profiles, and plot context
- **VS Code Integration**: Seamless writing experience with Continue.dev
- **Fine-Tuning**: Train models on your writing style for consistent narrative voice
- **Privacy First**: Everything runs locally—your stories never leave your machine
- **Fast**: 2-5 second response times on RTX 5090
- **Flexible**: Works with Llama, Qwen, Mistral, and other open models

## Key Features

### 🚀 vLLM Server (Port 8000)
- OpenAI-compatible API endpoint
- FlashInfer optimization for RTX 5090
- Support for 32k-128k context windows
- Multiple model options (8B-70B parameters)
- Prometheus metrics for monitoring

### 📚 RAG System (Port 8001)
- Transparent proxy layer for automatic context injection
- ChromaDB vector database for semantic search
- Organize documents by: characters, worldbuilding, chapters, style guides
- Maintains story continuity across long-form fiction
- ~50ms retrieval latency

### ✍️ Fine-Tuning
- QLoRA/LoRA training for style transfer
- Train on your own writing samples
- Benchmark suite for voice comparison
- Merge adapters for deployment
- Isolated training environment

### 🔧 VS Code Integration
- Continue.dev extension support (recommended)
- Cody extension support
- Inline editing with AI
- Context-aware completions
- Custom keyboard shortcuts

## Quick Start

### Prerequisites

- NVIDIA GPU (RTX 5090 recommended, RTX 3090/4090 compatible)
- Ubuntu 22.04+ or similar Linux distribution
- Python 3.12+
- CUDA 12.8 or 13.0
- 64GB RAM (32GB allocated to WSL2 if on Windows)
- VS Code installed

### Installation

**Step 1: Install vLLM Server (~15 minutes)**

```bash
cd vllm/setup

./0_hf_login.sh              # HuggingFace authentication
./1_check_gpu.sh             # Verify GPU compatibility
./2_cuda_install.sh          # CUDA toolkit (if needed)
./3_sys_pkgs.sh              # System dependencies
./4_create_venv.sh           # Creates ~/.venvs/llm
./5_install_torch.sh         # PyTorch with CUDA
./6_install_llm_stack.sh     # vLLM + FlashInfer
./7_env_export.sh            # Environment variables
```

**Step 2: Install RAG System (~10 minutes)**

```bash
cd RAG

setup/0_create_venv_with_deps.sh    # Creates ~/.venvs/rag
mkdir -p data/{characters,worldbuilding,chapters,style-guides}
# Add your documents to data/ directories
setup/1_ingest.py                   # Chunk documents
setup/2_embed_and_store.py          # Generate embeddings
```

**Step 3: Configure VS Code (~5 minutes)**

Install Continue.dev extension and configure `~/.continue/config.json`:

```json
{
  "models": [{
    "title": "Qwen 2.5 7B (RAG-Enhanced)",
    "provider": "openai",
    "model": "Qwen/Qwen2.5-7B-Instruct",
    "apiBase": "http://localhost:8001/v1",
    "apiKey": "EMPTY",
    "contextLength": 128000,
    "completionOptions": {
      "temperature": 0.85,
      "maxTokens": 2000
    }
  }]
}
```

See [QUICK_START.md](QUICK_START.md) for complete setup instructions.

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│  VS Code + Continue.dev Extension                   │
│  (Your writing environment)                         │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ HTTP Request
                  ▼
┌─────────────────────────────────────────────────────┐
│  RAG Proxy Server (Port 8001)                       │
│  ./serve_rag_proxy.sh                               │
├─────────────────────────────────────────────────────┤
│  1. Receives query                                  │
│  2. Searches ChromaDB vector database               │
│  3. Retrieves relevant context:                     │
│     - Character profiles                            │
│     - Worldbuilding details                         │
│     - Plot continuity                               │
│  4. Injects context into system message             │
│  5. Forwards to vLLM                                │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ HTTP Forward (augmented prompt)
                  ▼
┌─────────────────────────────────────────────────────┐
│  vLLM Server (Port 8000)                            │
│  ./serve_vllm.sh                                    │
├─────────────────────────────────────────────────────┤
│  - GPU inference on RTX 5090                        │
│  - Llama-3.1-8B or Qwen2.5-7B                       │
│  - FlashInfer optimization                          │
│  - Generates contextually-aware response            │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ Response
                  ▼
            [Back to VS Code]
```

## Daily Usage

### Start Writing Environment

```bash
# Terminal 1: Start vLLM server
./serve_vllm.sh

# Terminal 2: Start RAG proxy
./serve_rag_proxy.sh scifi_world

# VS Code: Open your manuscript and start writing
# Press Ctrl+L to chat with AI
```

### Stop Servers

```bash
./stop_vllm.sh
./stop_rag_proxy.sh
```

### Monitor Performance

```bash
./monitoring/monitor_vllm.sh         # GPU usage, token stats
./monitoring/monitor_rag_proxy.sh    # RAG query logs
```

## Project Structure

```
local-model-creative-writing/
├── README.md                    # This file
├── QUICK_START.md              # Complete setup guide
├── serve_vllm.sh               # Start vLLM server
├── serve_rag_proxy.sh          # Start RAG proxy
├── stop_vllm.sh                # Stop vLLM server
├── stop_rag_proxy.sh           # Stop RAG proxy
├── monitoring/                 # Performance monitoring scripts
│   ├── monitor_vllm.sh            # Monitor vLLM performance
│   ├── monitor_rag_proxy.sh       # Monitor RAG queries
│   ├── monitor_rag_context.sh     # Monitor RAG context retrieval
│   └── monitor_training.sh        # Monitor fine-tuning progress
├── vllm/                       # vLLM server setup
│   ├── README.md                  # vLLM documentation
│   ├── VLLM_SETUP.md              # Detailed setup guide
│   ├── setup/                     # Installation scripts (0-7)
│   ├── health_checks/             # Testing tools (9-13)
│   └── benchmarks/                # Performance tests
├── RAG/                        # RAG system
│   ├── README.md                  # RAG documentation
│   ├── RAG_SETUP.md               # Detailed implementation guide
│   ├── serve_rag_proxy.py         # RAG proxy server
│   ├── setup/                     # Setup scripts
│   ├── benchmarks/                # Testing and query tools
│   ├── data/                      # Your documents (user-created)
│   ├── chunks/                    # Processed chunks (auto-generated)
│   └── chroma_db/                 # Vector database (auto-generated)
├── fine-tuning/                # Style transfer training
│   ├── README.md                  # Fine-tuning documentation
│   ├── FINE_TUNING_SETUP.md       # Complete training guide
│   ├── setup/                     # Installation scripts
│   ├── configs/                   # QLoRA/LoRA configurations
│   ├── training/                  # Training scripts
│   ├── benchmarks/                # Voice comparison tests
│   └── data/                      # Training samples
├── chatUI/                     # VS Code integration
│   ├── README.md                  # Continue.dev setup guide
│   └── test doc.md                # RAG validation examples
├── tasks/                      # Task tracking
│   └── 001_configure_continue_for_creative_writing.md
└── docs/                       # Additional documentation
    ├── VSCODE_WRITING_SETUP.md    # VS Code configuration
    ├── SCIENCE_FICTION_WRITING_GUIDE.md
    ├── CONTEXT_COMPLETE_GUIDE.md
    ├── RAG_RETRIEVAL_GUIDE.md
    ├── CONCURRENCY_OPTIMIZATION_GUIDE.md
    ├── VLLM_QUICK_REFERENCE.md
    ├── archives/                  # Completed task artifacts
    └── history/                   # Architecture change logs
```

## Documentation

### Setup Guides
- **[QUICK_START.md](QUICK_START.md)** - Complete setup walkthrough
- **[vllm/VLLM_SETUP.md](vllm/VLLM_SETUP.md)** - vLLM installation details
- **[RAG/RAG_SETUP.md](RAG/RAG_SETUP.md)** - RAG system implementation
- **[fine-tuning/FINE_TUNING_SETUP.md](fine-tuning/FINE_TUNING_SETUP.md)** - Training guide

### Component Documentation
- **[vllm/README.md](vllm/README.md)** - vLLM server overview
- **[RAG/README.md](RAG/README.md)** - RAG workflow reference
- **[fine-tuning/README.md](fine-tuning/README.md)** - Fine-tuning quick reference

### Advanced Topics
- **[docs/VSCODE_WRITING_SETUP.md](docs/VSCODE_WRITING_SETUP.md)** - VS Code configuration
- **[docs/SCIENCE_FICTION_WRITING_GUIDE.md](docs/SCIENCE_FICTION_WRITING_GUIDE.md)** - Writing workflow
- **[docs/CONTEXT_COMPLETE_GUIDE.md](docs/CONTEXT_COMPLETE_GUIDE.md)** - Context optimization
- **[docs/RAG_RETRIEVAL_GUIDE.md](docs/RAG_RETRIEVAL_GUIDE.md)** - Retrieval tuning
- **[docs/VLLM_QUICK_REFERENCE.md](docs/VLLM_QUICK_REFERENCE.md)** - Command reference

## Recommended Models

### Science Fiction Writing (Long Context)

| Model | Parameters | Context | VRAM | Quality |
|-------|------------|---------|------|---------|
| `meta-llama/Llama-3.1-8B-Instruct` | 8B | 128k | ~16GB | Excellent (default) |
| `Qwen/Qwen2.5-7B-Instruct` | 7B | 128k | ~14GB | Superior creative writing |
| `Qwen/Qwen2.5-14B-Instruct` | 14B | 128k | ~28GB | Professional quality |
| `casperhansen/qwen2.5-14b-instruct-awq` | 14B (quantized) | 128k | ~10GB | Best quality/VRAM ratio |

See `serve_vllm.sh` for complete model list and recommendations.

## Performance

**Hardware: RTX 5090, 32GB VRAM, 64GB RAM**

- **Retrieval**: ~50ms per query
- **Generation**: 2-5 seconds (depends on context and output length)
- **Total Response**: 3-6 seconds
- **Throughput**: 20-50 tokens/second (varies by context window size)

**Context Window Impact:**
- 32k context: Fastest (~50 tok/s @ 8k input)
- 64k context: Balanced (~23 tok/s @ 8k, ~8 tok/s @ 32k)
- 100k context: Slower (~24 tok/s @ 8k, ~6 tok/s @ 48k)

## Use Cases

### Science Fiction Novel Writing
- Character consistency across chapters
- Worldbuilding detail retrieval
- Plot continuity tracking
- Style guide adherence

### Short Story Development
- Character profile management
- Setting/atmosphere consistency
- Dialogue style matching

### Worldbuilding
- Technology documentation
- Species/culture details
- Historical timeline consistency

## Troubleshooting

### Server Not Responding

```bash
# Check vLLM server
curl http://localhost:8000/health

# Check RAG proxy
curl http://localhost:8001/health

# View logs
./monitoring/monitor_vllm.sh
./monitoring/monitor_rag_proxy.sh
```

### No Context from Documents

```bash
# Test retrieval
cd RAG
benchmarks/4_query.py --interactive --collection scifi_world

# Re-embed documents
setup/1_ingest.py
setup/2_embed_and_store.py --collection scifi_world
```

### Out of Memory

- Use smaller context window: `./serve_vllm.sh MODEL PORT 9 32000`
- Use quantized models (AWQ variants)
- Reduce `max_seqs` parameter (increases latency, decreases VRAM)

See individual component README files for detailed troubleshooting.

## Hardware Requirements

### Minimum
- NVIDIA RTX 3090 (24GB VRAM)
- 32GB RAM
- 100GB free disk space
- Ubuntu 20.04+

### Recommended
- NVIDIA RTX 5090 (32GB VRAM)
- 64GB RAM (32GB for WSL2)
- 200GB free disk space
- Ubuntu 22.04+

### Optimal
- NVIDIA RTX 5090 or multiple GPUs
- 128GB RAM
- NVMe SSD with 500GB+ free space
- Ubuntu 22.04+ or Debian 12+

## Environment Isolation

This project uses isolated virtual environments to prevent dependency conflicts:

- **`~/.venvs/llm`** - vLLM server (vLLM, FlashInfer)
- **`~/.venvs/rag`** - RAG system (ChromaDB, sentence-transformers)
- **`~/.venvs/finetune`** - Training (Axolotl, DeepSpeed)

See [docs/VENV_ISOLATION.md](docs/VENV_ISOLATION.md) for details.

## Contributing

Contributions are welcome! This project is designed for:

- Creative writers using local LLMs
- AI researchers exploring RAG architectures
- Developers building writing tools
- Open source model enthusiasts

Please ensure:
- Scripts use `set -euo pipefail` for error handling
- Documentation is updated for any workflow changes
- Test your changes with the health check scripts
- Follow existing naming conventions (numbered setup scripts)

## License

This project is provided as-is for educational and creative writing purposes. Please review individual component licenses:

- vLLM: Apache 2.0
- ChromaDB: Apache 2.0
- Axolotl: Apache 2.0
- Model licenses vary by provider (Llama, Qwen, Mistral)

## Acknowledgments

Built with:
- [vLLM](https://github.com/vllm-project/vllm) - Fast LLM inference
- [FlashInfer](https://github.com/flashinfer-ai/flashinfer) - Optimized attention kernels
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Axolotl](https://github.com/OpenAccess-AI-Collective/axolotl) - Fine-tuning framework
- [Continue.dev](https://continue.dev/) - VS Code AI extension

Special thanks to the open source AI community for making local creative writing with LLMs possible.

## Support

For issues, questions, or feature requests:
1. Check the relevant README file for your component
2. Review troubleshooting sections
3. Consult the documentation in `docs/`
4. Open an issue on GitHub

---

**Ready to write science fiction with an AI that remembers your entire universe!** 🚀
