#!/usr/bin/env bash
set -euo pipefail

################################################################################
# Install PyTorch for Fine-Tuning
################################################################################
# Purpose: Install PyTorch with CUDA support (compatible with Axolotl)
#
# What it does:
#   - Activates ~/.venvs/finetune
#   - Installs PyTorch 2.6.0 stable with CUDA 12.1 support
#   - Verifies CUDA availability
#
# Requirements:
#   - Virtual environment created (0_create_venv.sh)
#   - NVIDIA GPU with CUDA 12.1+
#   - ~5GB disk space for PyTorch packages
#
# Usage: ./1_install_torch.sh
################################################################################

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Installing PyTorch for Fine-Tuning"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Target: PyTorch 2.6.0 stable with CUDA 12.1"
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

# Upgrade pip
echo "[UPGRADE] Upgrading pip..."
pip install -U pip
echo "[OK] pip upgraded"
echo ""

# Install PyTorch (stable version compatible with Axolotl)
echo "[INSTALL] Installing PyTorch 2.6.0 stable with CUDA 12.1..."
echo "   This will download ~5GB of packages..."
pip install torch torchvision torchaudio \
  --index-url https://download.pytorch.org/whl/cu121
echo "[OK] PyTorch installed"
echo ""

# Verify CUDA is available
echo "[VERIFY] Checking CUDA availability..."
python - <<'PY'
import torch, sys
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA version: {torch.version.cuda}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU device: {torch.cuda.get_device_name(0)}")
    print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
sys.exit(0 if torch.cuda.is_available() else 1)
PY

if [ $? -eq 0 ]; then
    echo ""
    echo "[OK] PyTorch installed successfully with CUDA support!"
    echo ""
    echo "Next step:"
    echo "  Run: ./2_install_training_stack.sh"
else
    echo ""
    echo "[ERROR] CUDA not available! Check your GPU drivers and CUDA installation."
    exit 1
fi
