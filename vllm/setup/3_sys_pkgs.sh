#!/usr/bin/env bash
set -euo pipefail
# System packages: Python venv, git, curl, jq for JSON, and build tools.
sudo apt-get update -y
sudo apt-get install -y python3-venv git curl jq build-essential

# Sanity checks: verify all essential tools are available and working.
echo "=== System Tools Verification ==="
python3 --version
echo "Python venv support: $(python3 -m venv --help | head -1)"
git --version
curl --version | head -1
jq --version
gcc --version | head -1
make --version | head -1
echo "All system tools verified successfully!"