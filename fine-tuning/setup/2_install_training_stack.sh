#!/usr/bin/env bash
set -euo pipefail

################################################################################
# Install Training Stack (Axolotl + Dependencies)
################################################################################
# Purpose: Install Axolotl framework with all training dependencies
#
# What it does:
#   - Activates ~/.venvs/finetune
#   - Installs core ML libraries (transformers, accelerate, peft)
#   - Installs Axolotl with flash-attention and DeepSpeed
#   - Verifies installation
#
# Requirements:
#   - Virtual environment created (0_create_venv.sh)
#   - PyTorch installed (1_install_torch.sh)
#   - ~10GB disk space for training packages
#   - RTX 5090 or compatible GPU
#
# Usage: ./2_install_training_stack.sh
################################################################################

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Installing Training Stack"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Target: Axolotl + flash-attention + DeepSpeed"
echo ""

# Activate the venv
echo "[VENV] Activating virtual environment..."
if [ ! -f ~/.venvs/finetune/bin/activate ]; then
    echo "[ERROR] Virtual environment not found at ~/.venvs/finetune/"
    echo "   Please run: ./0_create_venv.sh first"
    exit 1
fi

source ~/.venvs/finetune/bin/activate || {
    echo "[ERROR] Failed to activate virtual environment"
    echo "   Check if ~/.venvs/finetune/bin/activate exists and is readable"
    exit 1
}
echo "[OK] Virtual environment activated"
echo ""

# Verify PyTorch is installed
echo "[CHECK] Verifying PyTorch installation..."
python -c "import torch; assert torch.cuda.is_available()" || {
    echo "[ERROR] PyTorch with CUDA not found!"
    echo "   Please run: ./1_install_torch.sh first"
    exit 1
}
echo "[OK] PyTorch with CUDA found"
echo ""

# Upgrade pip and tools
echo "[UPGRADE] Upgrading pip, setuptools, wheel..."
python -m pip install -U pip setuptools wheel
pip cache purge
echo "[OK] Tools upgraded"
echo ""

# Install ninja for parallel compilation (in case flash-attn builds from source)
echo "[INSTALL] Installing ninja (parallel build system)..."
pip install ninja
echo "[OK] ninja installed"
echo ""

# Install core ML libraries
echo "[INSTALL] Installing core ML libraries..."
echo "   This includes: transformers, accelerate, peft, bitsandbytes"
pip install \
  "transformers>=4.45.0" \
  "accelerate>=0.34.0" \
  "peft>=0.13.0" \
  "bitsandbytes>=0.44.0" \
  "datasets>=3.0.0" \
  "tokenizers>=0.21.0" \
  "sentencepiece>=0.2.0" \
  "safetensors>=0.4.5" \
  "huggingface-hub>=0.35.0"
echo "[OK] Core libraries installed"
echo ""

# Check if flash-attention is already installed
echo "[CHECK] Checking for flash-attention..."
if python -c "import flash_attn" 2>/dev/null; then
    echo "[OK] flash-attention already installed"
    python -c "import flash_attn; print(f'   Version: {flash_attn.__version__}')"
else
    echo "[INSTALL] Installing flash-attention (pre-built wheel)..."
    echo "   Trying GitHub releases first (~30 seconds if available)..."
    echo "   If no pre-built wheel exists, will compile with ninja (15-20 minutes)"
    echo ""
    
    # Set CUDA environment and parallel compilation (used if building from source)
    export CUDA_HOME=/usr/local/cuda-12.8
    export PATH=/usr/local/cuda-12.8/bin:$PATH
    export LD_LIBRARY_PATH=/usr/local/cuda-12.8/lib64:$LD_LIBRARY_PATH
    export TORCH_CUDA_ARCH_LIST="8.9"
    export MAX_JOBS=1  # ULTRA-CONSERVATIVE: Single-threaded to prevent OOM
    
    pip install flash-attn --no-build-isolation \
      --find-links https://github.com/Dao-AILab/flash-attention/releases
    echo "[OK] flash-attention installed"
fi
echo ""

# Install Axolotl with DeepSpeed
echo "[INSTALL] Installing Axolotl with DeepSpeed..."
echo "   This will download ~5GB and take several minutes..."
pip install "axolotl[deepspeed]"
echo "[OK] Axolotl installed"
echo ""

# Install additional utilities
echo "[INSTALL] Installing additional utilities..."
pip install \
  "wandb" \
  "tensorboard" \
  "scipy" \
  "scikit-learn"
echo "[OK] Utilities installed"
echo ""

# Print versions for verification
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Installed Package Versions"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python - <<'PY'
import importlib.metadata as m
packages = [
    "torch", "transformers", "accelerate", "peft", 
    "bitsandbytes", "axolotl", "flash-attn", "deepspeed"
]
for p in packages:
    try:
        print(f"{p:20s} {m.version(p)}")
    except:
        print(f"{p:20s} NOT INSTALLED")
PY
echo ""

echo "[OK] Training stack installation complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Next Steps"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Add your writing samples to: fine-tuning/data/raw/"
echo "2. Create data preparation script: fine-tuning/scripts/1_prepare_data.py"
echo "3. Prepare training data: cd scripts && python 1_prepare_data.py"
echo "4. Start training: cd scripts && ./2_train_lora.sh"
echo ""
echo "To activate this environment later:"
echo "  source ~/.venvs/finetune/bin/activate"
