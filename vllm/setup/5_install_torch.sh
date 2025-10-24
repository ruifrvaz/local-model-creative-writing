#!/usr/bin/env bash
set -euo pipefail

# Activate the venv created earlier
echo "[VENV] Activating virtual environment..."
if [ ! -f ~/.venvs/llm/bin/activate ]; then
    echo "[ERROR] ERROR: Virtual environment not found at ~/.venvs/llm/"
    echo "   Please run: ./4_create_venv.sh first"
    exit 1
fi

source ~/.venvs/llm/bin/activate || {
    echo "[ERROR] ERROR: Failed to activate virtual environment"
    echo "   Check if ~/.venvs/llm/bin/activate exists and is readable"
    exit 1
}
echo "[OK] Virtual environment activated"
echo

# Install PyTorch 2.8.0 stable for CUDA 12.8 (matches working configuration)
pip install -U pip
pip install --pre torch torchvision torchaudio \
  --index-url https://download.pytorch.org/whl/nightly/cu128

# Verify CUDA is available
python - <<'PY'
import torch, sys
print("torch", torch.__version__, "cuda", torch.version.cuda, "cuda_avail", torch.cuda.is_available())
sys.exit(0 if torch.cuda.is_available() else 1)
PY

echo "[OK] PyTorch nightly installed successfully with CUDA support!"