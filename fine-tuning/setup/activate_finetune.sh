#!/usr/bin/env bash

################################################################################
# Activate Fine-Tuning Environment with CUDA 12.8
################################################################################
# Purpose: Activate finetune venv with proper CUDA paths for compilation
#
# Usage: source ./activate_finetune.sh
#        (Must use 'source' to set variables in current shell)
################################################################################

# Activate the venv
source ~/.venvs/finetune/bin/activate

# Set CUDA 12.8 paths (for flash-attention compilation)
export CUDA_HOME=/usr/local/cuda-12.8
export PATH=/usr/local/cuda-12.8/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12.8/lib64:$LD_LIBRARY_PATH
export TORCH_CUDA_ARCH_LIST="8.9"  # RTX 5090

echo "[OK] Fine-tuning environment activated with CUDA 12.8"
echo "   CUDA_HOME: $CUDA_HOME"
echo "   Python: $(which python)"
