#!/usr/bin/env bash
set -euo pipefail

# Fail early if GPU passthrough is not working.
command -v nvidia-smi >/dev/null || { echo "GPU not visible in WSL. Fix Windows driver."; exit 1; }

# Refresh package lists.
sudo apt-get update -y

# Install NVIDIA's CUDA 13.0 toolkit if not already present (idempotent).
if ! dpkg -s cuda-toolkit-13-0 >/dev/null 2>&1; then
  wget -qO /tmp/cuda-keyring.deb https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.1-1_all.deb
  sudo dpkg -i /tmp/cuda-keyring.deb
  sudo apt-get update -y
  sudo apt-get install -y cuda-toolkit-13-0
fi

# Add CUDA binaries and libraries to your shell environment only once.
grep -q '/usr/local/cuda/bin' ~/.bashrc || echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
grep -q '/usr/local/cuda/lib64' ~/.bashrc || echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc

# Load the updated environment in the current shell for this script.
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

# Confirm nvcc is available and prints its version.
nvcc --version