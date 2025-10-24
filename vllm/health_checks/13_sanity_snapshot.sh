#!/usr/bin/env bash
set -euo pipefail

################################################################################
# Step 13: Environment Snapshot - Verify Installation
################################################################################
# Purpose: Quick snapshot of Python environment, packages, and GPU status
# Usage: ./13_sanity_snapshot.sh
################################################################################

# Activate venv
echo "[VENV] Activating virtual environment..."
if [ ! -f ~/.venvs/llm/bin/activate ]; then
    echo "[ERROR] Virtual environment not found at ~/.venvs/llm/"
    exit 1
fi

source ~/.venvs/llm/bin/activate || {
    echo "[ERROR] Failed to activate virtual environment"
    exit 1
}
echo "[OK] Virtual environment activated"
echo

echo "================================================================================"
echo "Environment Snapshot - $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================================================"
echo

# Python and package versions
echo "[INFO] Python & Core Packages:"
python - <<'PY'
import torch, importlib.metadata as m, os, sys

print(f"  Python: {sys.version.split()[0]}")
print(f"  PyTorch: {torch.__version__} (CUDA {torch.version.cuda})")
print(f"  CUDA Available: {torch.cuda.is_available()}")

packages = ["numpy", "vllm", "flashinfer-python", "transformers", "openai", "triton"]
for p in packages:
    try: 
        print(f"  {p}: {m.version(p)}")
    except: 
        print(f"  {p}: [NOT INSTALLED]")

# Environment vars
print(f"\n  VLLM_ATTENTION_BACKEND: {os.environ.get('VLLM_ATTENTION_BACKEND', '[NOT SET]')}")
PY

echo

# GPU information
echo "[INFO] GPU Status:"
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,driver_version,memory.total,memory.used \
        --format=csv,noheader | sed 's/^/  /'
    echo
    nvidia-smi | head -10 | sed 's/^/  /'
else
    echo "  [WARN] nvidia-smi not available"
fi

echo

# CUDA compiler
echo "[INFO] CUDA Compiler:"
if command -v nvcc &> /dev/null; then
    nvcc --version | tail -1 | sed 's/^/  /'
else
    echo "  [WARN] nvcc not found"
fi

echo
echo "================================================================================"
echo "[OK] Snapshot complete"
echo "================================================================================