#!/usr/bin/env bash
set -euo pipefail
# Create a dedicated venv under your home folder (idempotent if exists).
python3 -m venv ~/.venvs/llm
# Activate the venv for this shell only.
source ~/.venvs/llm/bin/activate
# Ensure modern packaging tools.
python -m pip install -U pip setuptools wheel
# Print versions for logging.
python -V
pip -V