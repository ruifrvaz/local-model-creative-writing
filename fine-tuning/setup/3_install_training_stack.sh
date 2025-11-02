#!/usr/bin/env bash
set -euo pipefail

################################################################################
# Install Training Stack (Additional Training Utilities)
################################################################################
# Purpose: Install additional training utilities (DeepSpeed, flash-attention, monitoring)
#
# What it does:
#   - Activates ~/.venvs/finetune
#   - Installs flash-attention (if not present)
#   - Installs DeepSpeed for distributed training
#   - Installs monitoring tools (wandb, tensorboard)
#   - Verifies installation
#
# Requirements:
#   - Virtual environment created (0_create_venv.sh)
#   - PyTorch 2.8.0+cu128 installed (1_install_torch.sh)
#   - Axolotl installed (2_install_axolotl.sh)
#   - ~5GB disk space for additional packages
#   - RTX 5090 or compatible GPU
#
# WSL USERS: Configure .wslconfig BEFORE running this script!
#   Flash-attention compilation requires significant memory.
#   Recommended C:\Users\<username>\.wslconfig:
#     [wsl2]
#     memory=48GB
#     processors=12
#   Then restart WSL: wsl --shutdown
#   See: docs/history/2025-11-02_flash_attention_wsl_memory_issue.md
#
# Usage: ./3_install_training_stack.sh
################################################################################

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Installing Additional Training Utilities"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Target: DeepSpeed + flash-attention + monitoring tools"
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

# Verify PyTorch and Axolotl are installed
echo "[CHECK] Verifying PyTorch installation..."
python -c "import torch; assert torch.cuda.is_available()" || {
    echo "[ERROR] PyTorch with CUDA not found!"
    echo "   Please run: ./1_install_torch.sh first"
    exit 1
}
echo "[OK] PyTorch with CUDA found"

echo "[CHECK] Verifying Axolotl installation..."
python -c "import axolotl" || {
    echo "[ERROR] Axolotl not found!"
    echo "   Please run: ./2_install_axolotl.sh first"
    exit 1
}
echo "[OK] Axolotl found"
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
    echo "   WSL USERS: If compilation crashes, configure .wslconfig first!"
    echo "   See: docs/history/2025-11-02_flash_attention_wsl_memory_issue.md"
    echo ""
    
    # Set CUDA environment and parallel compilation (used if building from source)
    export CUDA_HOME=/usr/local/cuda-12.8
    export PATH=/usr/local/cuda-12.8/bin:$PATH
    export LD_LIBRARY_PATH=/usr/local/cuda-12.8/lib64:$LD_LIBRARY_PATH
    export TORCH_CUDA_ARCH_LIST="8.9"
    # CRITICAL: MAX_JOBS controls compilation parallelization
    # Flash-attention compilation uses ~4GB per job. With 48GB WSL allocation,
    # MAX_JOBS=2 is experimental (may be faster than single-threaded).
    # If WSL crashes, reduce back to MAX_JOBS=1.
    # See: docs/history/2025-11-02_flash_attention_wsl_memory_issue.md
    
    MAX_JOBS=2 pip install flash-attn --no-build-isolation \
      --find-links https://github.com/Dao-AILab/flash-attention/releases
    echo "[OK] flash-attention installed"
fi
echo ""

# Install DeepSpeed for distributed training
echo "[INSTALL] Installing DeepSpeed..."
pip install "deepspeed>=0.15.0"
echo "[OK] DeepSpeed installed"
echo ""

# Install monitoring and utilities
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
echo "2. Prepare training data: cd training && python 1_prepare_data.py"
echo "3. Start training: cd training && ./2_train_lora.sh"
echo ""
echo "To activate this environment later:"
echo "  source ~/.venvs/finetune/bin/activate"
