#!/usr/bin/env bash
set -euo pipefail

# Activate the venv
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

# Upgrade pip and tools first
python -m pip install -U pip setuptools wheel
pip cache purge

# Install proven stable versions (matches working configuration)
pip install \
  "numpy==1.26.4" \
  "vllm==0.10.2" \
  "flashinfer-python==0.3.0" --extra-index-url https://flashinfer.ai/whl/nightly/ \
  "huggingface_hub==0.35.3" \
  "tokenizers==0.21.2" \
  "sentencepiece==0.2.0" \
  "safetensors==0.4.5"

# Additional tools
pip install transformers openai accelerate
# Replace deprecated pynvml import to silence warnings.
pip install -U nvidia-ml-py

# Print versions for logging.
python - <<'PY'
import importlib.metadata as m
for p in ["vllm","transformers","flashinfer-python","openai"]:
    try: print(p, m.version(p))
    except: print(p, "not installed")
PY