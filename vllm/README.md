# LLM Setup Scripts for RTX 5090 Blackwell

This directory contains a complete workflow for setting up and running local LLMs on NVIDIA RTX 5090 (Blackwell) hardware with vLLM and FlashInfer.

## Directory Structure

```
vllm/
├── README.md                   # This file
├── setup/                      # Installation scripts (run once)
│   ├── 0_hf_login.sh
│   ├── 1_check_gpu.sh
│   ├── 2_cuda_install.sh
│   ├── 3_sys_pkgs.sh
│   ├── 4_create_venv.sh
│   ├── 5_install_torch.sh
│   ├── 6_install_llm_stack.sh
│   └── 7_env_export.sh
├── health_checks/              # Testing & maintenance
│   ├── 9_health.sh
│   ├── 10_concurrency.sh
│   ├── 11_tool_call_test.py
│   └── 13_sanity_snapshot.sh
└── benchmarks/                 # Performance testing
    ├── 1_throughput.sh
    ├── 2_context_scaling.sh
    ├── 3_creative_quality.py
    ├── 4_long_context_coherence.py
    ├── 5_model_comparison.sh
    └── results/                # JSON outputs
```

## Initial Setup (Run Once)

Execute the setup workflow scripts in order:

```bash
cd vllm/setup

# Step 0: Authenticate with HuggingFace (optional, for gated models)
./0_hf_login.sh

# Steps 1-7: System setup
./1_check_gpu.sh            # Verify GPU is visible to WSL
./2_cuda_install.sh         # Install CUDA Toolkit 13.0
./3_sys_pkgs.sh             # Install system dependencies
./4_create_venv.sh          # Create Python virtual environment
./5_install_torch.sh        # Install PyTorch with CUDA
./6_install_llm_stack.sh    # Install vLLM + FlashInfer stack
./7_env_export.sh           # Set environment variables
```

## Daily Usage

After initial setup, typical workflow:

```bash
# Start server (runs in background)
./serve_vllm.sh

# In same or different terminal - validate server
./vllm/health_checks/9_health.sh

# When done - stop server
./stop_vllm.sh
```

## Testing & Validation

```bash
cd vllm/health_checks

./9_health.sh               # API endpoint validation
./10_concurrency.sh         # Parallel request testing (4 requests)
python 11_tool_call_test.py # Tool calling capabilities
./13_sanity_snapshot.sh     # Environment snapshot
```

## Script Reference

### Setup Scripts (`setup/`)

| Script | Purpose | Run Frequency |
|--------|---------|---------------|
| `0_hf_login.sh` | HuggingFace authentication | Once (token persists) |
| `1_check_gpu.sh` | Verify GPU passthrough | Once (diagnostic) |
| `2_cuda_install.sh` | Install CUDA Toolkit 13.0 | Once |
| `3_sys_pkgs.sh` | System dependencies | Once |
| `4_create_venv.sh` | Create virtual environment | Once |
| `5_install_torch.sh` | Install PyTorch 2.8.0 | Once |
| `6_install_llm_stack.sh` | Install vLLM + FlashInfer | Once |
| `7_env_export.sh` | Set environment variables | Once |

### Server Script (root)

| Script | Purpose | Usage |
|--------|---------|-------|
| `serve_vllm.sh` | Start vLLM server | Daily (quick access) |

Default model: `meta-llama/Llama-3.1-8B-Instruct`  
Custom model: `./serve_vllm.sh "Qwen/Qwen2.5-14B-Instruct"`

### Health Check Scripts (`health_checks/`)

| Script                    | Purpose               | When to Run           |
|--------                   |---------              |-------------          |
| `9_health.sh`             | API validation        | After server start    |
| `10_concurrency.sh`       | Load testing          | Verify performance    |
| `11_tool_call_test.py`    | Function calling test | Validate features     |
| `stop.sh`                 | Graceful shutdown     | End of session        |
| `13_sanity_snapshot.sh`   | Environment snapshot  | Troubleshooting       |

## Key Features

- **FlashInfer Optimization**: 2-4x faster attention on RTX 5090
- **Stable Configuration**: Tested package versions (PyTorch 2.8.0, vLLM 0.10.2)
- **OpenAI Compatible**: Drop-in replacement for OpenAI API
- **32k Context**: Full context window support
- **Robust Error Handling**: All scripts use `set -euo pipefail`

## Environment Variables

```bash
VLLM_ATTENTION_BACKEND=FLASHINFER  # Use FlashInfer backend
VLLM_USE_XFORMERS=0                # Disable xFormers (conflicts)
```

These are set by `vllm/setup/7_env_export.sh` and persisted in `~/.bashrc`.
- Default port: `8000`
- Virtual environment: `~/.venvs/llm`
- FlashInfer backend optimized for Blackwell architecture

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