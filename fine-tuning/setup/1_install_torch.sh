#!/usr/bin/env bash
set -euo pipefail

################################################################################
# Install PyTorch for Fine-Tuning
################################################################################
# Purpose: Install PyTorch with CUDA 12.8 support (RTX 5090 compatible)
#
# What it does:
#   - Checks if PyTorch is already installed with correct CUDA version
#   - Skips installation if PyTorch cu128 is already present (idempotent)
#   - Installs/upgrades PyTorch with CUDA 12.8 if needed
#   - Verifies CUDA availability and RTX 5090 support (sm_120)
#
# Requirements:
#   - Virtual environment created (0_create_venv.sh)
#   - NVIDIA GPU with CUDA 12.8+ drivers
#   - ~5GB disk space for PyTorch packages
#
# Idempotent: Yes - safe to run multiple times
# Usage: ./1_install_torch.sh
################################################################################

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Installing PyTorch for Fine-Tuning"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Target: PyTorch 2.8.0 with CUDA 12.8 (RTX 5090 Blackwell sm_120, vLLM-aligned)"
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

# Check if PyTorch is already installed with correct version
echo "[CHECK] Checking for existing PyTorch installation..."
set +e  # Temporarily disable exit on error for version check
TORCH_CHECK=$(python -c "
import sys
try:
    import torch
    cuda_version = torch.version.cuda if hasattr(torch.version, 'cuda') else None
    torch_version = torch.__version__
    
    needs_upgrade = False
    if cuda_version:
        cuda_major, cuda_minor = map(int, cuda_version.split('.')[:2])
        # Parse torch version more carefully (handle 2.8.0+cu128 format)
        torch_parts = torch_version.split('+')[0].split('.')
        torch_major, torch_minor = int(torch_parts[0]), int(torch_parts[1])
        
        # Need PyTorch 2.8.0 with CUDA 12.8 for RTX 5090 sm_120 (vLLM-aligned)
        if torch_major != 2 or torch_minor != 8:
            needs_upgrade = True
            print(f'UPGRADE_NEEDED|Current: torch {torch_version} cu{cuda_major}.{cuda_minor}, need torch 2.8.0 cu12.8')
        elif cuda_major < 12 or (cuda_major == 12 and cuda_minor < 8):
            needs_upgrade = True
            print(f'UPGRADE_NEEDED|Current: torch {torch_version} cu{cuda_major}.{cuda_minor}, need cu12.8')
        else:
            print(f'OK|torch {torch_version} cu{cuda_major}.{cuda_minor}')
    else:
        needs_upgrade = True
        print(f'UPGRADE_NEEDED|torch {torch_version} has no CUDA support')
    
    sys.exit(1 if needs_upgrade else 0)
except ImportError:
    print('NOT_INSTALLED|torch not found')
    sys.exit(1)
" 2>&1)

TORCH_STATUS=$?
set -e  # Re-enable exit on error
echo "$TORCH_CHECK"

if [ $TORCH_STATUS -eq 0 ]; then
    echo "[OK] PyTorch 2.8.0 with CUDA 12.8 already installed"
    echo "[SKIP] No reinstallation needed"
    echo ""
    echo "Next step:"
    echo "  Run: ./2_install_axolotl.sh"
    exit 0
fi

echo "[INFO] PyTorch needs installation or upgrade to 2.8.0"
echo ""

# Upgrade pip
echo "[UPGRADE] Upgrading pip, wheel, setuptools..."
pip install --upgrade pip wheel setuptools
echo "[OK] pip, wheel, setuptools upgraded"
echo ""

# Install PyTorch 2.8.0 with CUDA 12.8 (RTX 5090 Blackwell sm_120 support, vLLM-aligned)
echo "[INSTALL] Installing PyTorch 2.8.0 with CUDA 12.8..."
echo "   This will download ~2.5GB of packages..."
echo "   CUDA 12.8 required for RTX 5090 Blackwell architecture (sm_120)"
echo "   Using PyTorch 2.8.0 (same version as vLLM for compatibility)"
echo "   Force reinstalling to ensure cu128 versions are installed"
pip uninstall -y torch torchvision torchaudio || true
pip install torch==2.8.0 torchvision torchaudio \
  --index-url https://download.pytorch.org/whl/cu128
echo "[OK] PyTorch 2.8.0 installed"
echo ""

# Verify CUDA is available
echo "[VERIFY] Checking CUDA availability and RTX 5090 support..."
python - <<'PY'
import torch, sys
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA version: {torch.version.cuda}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    device_name = torch.cuda.get_device_name(0)
    compute_cap = torch.cuda.get_device_capability(0)
    print(f"GPU device: {device_name}")
    print(f"Compute capability: sm_{compute_cap[0]}{compute_cap[1]}")
    print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    
    # Check if RTX 5090 is properly supported (sm_120)
    if "RTX 5090" in device_name and compute_cap != (12, 0):
        print(f"[WARN] RTX 5090 detected but compute capability is {compute_cap}, expected (12, 0)")
        print(f"[WARN] This may indicate CUDA version mismatch")
        
sys.exit(0 if torch.cuda.is_available() else 1)
PY

if [ $? -eq 0 ]; then
    echo ""
    echo "[OK] PyTorch installed successfully with CUDA support!"
    echo ""
    echo "Next step:"
    echo "  Run: ./2_install_axolotl.sh"
else
    echo ""
    echo "[ERROR] CUDA not available! Check your GPU drivers and CUDA installation."
    exit 1
fi
