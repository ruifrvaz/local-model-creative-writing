#!/usr/bin/env bash
set -euo pipefail
# Step 0: HuggingFace Authentication
# 
# This step sets up HuggingFace authentication to access gated models like:
# - meta-llama/Llama-3.1-8B-Instruct
# - meta-llama/Llama-3.1-70B-Instruct
# - Other Meta/Llama models requiring authentication
#
# You'll need a HuggingFace account and access token from:
# https://huggingface.co/settings/tokens

echo "[AUTH] Setting up HuggingFace Authentication..."
echo "   This allows access to gated models like Llama"
echo "   You'll need:"
echo "   1. HuggingFace account"
echo "   2. Access token from https://huggingface.co/settings/tokens"
echo "   3. Acceptance of model license agreements"
echo

# Activate the virtual environment
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

# Check if huggingface-cli is available
if ! command -v huggingface-cli &> /dev/null; then
    echo "[ERROR] huggingface-cli not found. Installing..."
    pip install huggingface-hub
fi

echo "🔐 Starting HuggingFace login process..."
echo "   Paste your HF token when prompted"
echo "   Answer 'n' to git credential storage (not needed for inference)"
echo

# Login to HuggingFace
huggingface-cli login

echo
echo "[OK] HuggingFace authentication complete!"
echo "   You can now access gated models like Llama"
echo "   Run ./serve_vllm.sh to start the server"