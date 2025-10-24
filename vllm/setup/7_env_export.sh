#!/usr/bin/env bash
set -euo pipefail
# FlashInfer: High-performance attention kernels optimized for modern GPUs (especially Blackwell).
# Provides 2-4x speedup over standard attention for transformer inference on RTX 5090.
# Persist FlashInfer selection so future shells pick it up automatically.
grep -q '^export VLLM_ATTENTION_BACKEND=FLASHINFER' ~/.bashrc || echo 'export VLLM_ATTENTION_BACKEND=FLASHINFER' >> ~/.bashrc
# Ensure CUDA env is present for future shells too (idempotent guards).
grep -q '/usr/local/cuda/bin' ~/.bashrc || echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
grep -q '/usr/local/cuda/lib64' ~/.bashrc || echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
# Load now so you don't need a new terminal for this run.
export VLLM_ATTENTION_BACKEND=FLASHINFER
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
echo "VLLM_ATTENTION_BACKEND=$VLLM_ATTENTION_BACKEND"