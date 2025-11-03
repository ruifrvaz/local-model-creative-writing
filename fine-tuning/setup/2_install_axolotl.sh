#!/usr/bin/env bash
set -euo pipefail

################################################################################
# Install Axolotl from Main Branch
################################################################################
# Purpose: Install latest Axolotl from GitHub main (RTX 5090 compatible)
#
# What it does:
#   - Installs Axolotl from main branch WITHOUT pulling outdated dependencies
#   - Manually installs compatible dependencies (transformers, accelerate, etc.)
#   - Avoids Axolotl's pinned torch 2.6.x requirement (incompatible with sm_120)
#   - Verifies installation and compatibility
#
# Requirements:
#   - Virtual environment created (0_create_venv.sh)
#   - PyTorch 2.9.0+ nightly with CUDA 12.8 (1_install_torch.sh)
#
# Idempotent: Partial - reinstalls Axolotl each run but checks dependencies
# Usage: ./2_install_axolotl.sh
################################################################################

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Installing Axolotl Training Framework"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Target: Axolotl main branch (RTX 5090 Blackwell compatible)"
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
    exit 1
}
echo "[OK] Virtual environment activated"
echo ""

# Verify PyTorch is installed
echo "[CHECK] Verifying PyTorch installation..."
TORCH_OK=$(python -c "
import sys
try:
    import torch
    version = torch.__version__
    cuda = torch.version.cuda if hasattr(torch.version, 'cuda') else None
    major, minor = map(int, version.split('.')[:2])
    
    if major < 2 or (major == 2 and minor < 8):
        print(f'[ERROR] PyTorch {version} too old - need 2.8.0+')
        sys.exit(1)
    
    if not cuda or cuda.split('.')[0] < '12':
        print(f'[ERROR] CUDA {cuda} too old - need 12.8+')
        sys.exit(1)
    
    print(f'[OK] PyTorch {version} with CUDA {cuda}')
    sys.exit(0)
except ImportError:
    print('[ERROR] PyTorch not found - run ./1_install_torch.sh first')
    sys.exit(1)
" 2>&1)

echo "$TORCH_OK"
if [ $? -ne 0 ]; then
    echo ""
    echo "Next step:"
    echo "  Run: ./1_install_torch.sh"
    exit 1
fi
echo ""

# Install Axolotl WITHOUT dependencies (avoid torch 2.6.x pin)
echo "[INSTALL] Installing Axolotl from main branch (without dependencies)..."
echo "   This avoids Axolotl's pinned torch==2.6.x requirement"
echo "   Using GitHub main for latest RTX 5090 compatibility"
pip install --no-deps git+https://github.com/axolotl-ai-cloud/axolotl.git
echo "[OK] Axolotl installed"
echo ""

# Install compatible dependencies manually
echo "[INSTALL] Installing compatible dependencies..."
echo "   transformers, accelerate, datasets, peft, bitsandbytes, trl, torchao, etc."
echo "   NOTE: Intentionally NOT installing autoawq (not needed for QLoRA training)"
echo "         AWQ is for inference quantization, we use bitsandbytes for QLoRA"
pip install \
  transformers \
  accelerate \
  datasets \
  peft \
  bitsandbytes \
  trl \
  torchao \
  sentencepiece \
  einops \
  scipy \
  scikit-learn \
  tensorboard \
  wandb \
  packaging \
  psutil \
  pyyaml \
  requests \
  safetensors \
  tokenizers \
  typing-extensions
echo "[OK] Dependencies installed"
echo ""

# Verify Axolotl installation
echo "[VERIFY] Testing Axolotl import..."
python -c "
import axolotl
import transformers
import accelerate
import peft
import bitsandbytes as bnb
import trl
import torchao
print('[OK] All core imports successful')
print(f'Axolotl version: {axolotl.__version__}')
print(f'Transformers: {transformers.__version__}')
print(f'Accelerate: {accelerate.__version__}')
print(f'PEFT: {peft.__version__}')
print(f'TRL: {trl.__version__}')
print(f'torchao: {torchao.__version__}')
"

if [ $? -eq 0 ]; then
    echo ""
    echo "[OK] Axolotl installed successfully!"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Installation Complete"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Stack summary:"
    python -c "
import torch
print(f'  PyTorch: {torch.__version__}')
print(f'  CUDA: {torch.version.cuda}')
print(f'  GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')
import axolotl, transformers, peft
print(f'  Axolotl: {axolotl.__version__}')
print(f'  Transformers: {transformers.__version__}')
print(f'  PEFT: {peft.__version__}')
"
    echo ""
    echo "Next step:"
    echo "  cd ../training && ./2_train_lora.sh"
else
    echo ""
    echo "[ERROR] Axolotl installation failed!"
    echo "   Check the error messages above"
    exit 1
fi
