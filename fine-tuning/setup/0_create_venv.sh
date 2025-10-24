#!/usr/bin/env bash
set -euo pipefail

################################################################################
# Create Fine-Tuning Virtual Environment
################################################################################
# Purpose: Create isolated Python environment for LLM fine-tuning
#
# What it does:
#   - Creates venv at ~/.venvs/finetune
#   - Upgrades pip, setuptools, wheel
#   - Prints Python/pip versions
#
# Requirements:
#   - Python 3.12+ installed
#   - Sufficient disk space (~15GB for packages)
#
# Usage: ./0_create_venv.sh
################################################################################

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Creating Fine-Tuning Virtual Environment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Location: ~/.venvs/finetune"
echo ""

# Create venv (idempotent - won't fail if exists)
echo "[CREATE] Creating virtual environment..."
python3 -m venv ~/.venvs/finetune
echo "[OK] Virtual environment created"
echo ""

# Activate the venv
echo "[ACTIVATE] Activating virtual environment..."
source ~/.venvs/finetune/bin/activate
echo "[OK] Activated"
echo ""

# Upgrade packaging tools
echo "[UPGRADE] Upgrading pip, setuptools, wheel..."
python -m pip install -U pip setuptools wheel
echo "[OK] Tools upgraded"
echo ""

# Print versions for verification
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Environment Information"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python -V
pip -V
echo ""
echo "[OK] Fine-tuning virtual environment ready!"
echo ""
echo "Next steps:"
echo "  1. Run: ./1_install_torch.sh"
echo "  2. Run: ./2_install_training_stack.sh"
