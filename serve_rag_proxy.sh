#!/usr/bin/env bash
set -euo pipefail

################################################################################
# Serve RAG Proxy Server
################################################################################
# Purpose: Start transparent RAG layer that augments all vLLM requests
#
# What it does:
#   - Starts proxy server on port 8001
#   - Intercepts all requests
#   - Automatically retrieves relevant context
#   - Forwards augmented requests to vLLM (port 8000)
#
# Prerequisites:
#   - RAG environment created: cd RAG && setup/0_create_venv_with_deps.sh
#   - Documents embedded: cd RAG && setup/2_embed_and_store.py
#   - vLLM server running on port 8000
#
# Usage: ./serve_rag_proxy.sh [collection_name]
################################################################################

COLLECTION="${1:-scifi_world}"
PORT=8001

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Starting RAG Proxy Server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Collection: $COLLECTION"
echo "Proxy Port: $PORT"
echo "vLLM Backend: http://localhost:8000"
echo ""

# Check if vLLM is running
echo "[CHECK] Testing vLLM server..."
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "[ERROR] vLLM server not responding on port 8000"
    echo "   Start it with: ./serve_vllm.sh"
    exit 1
fi
echo "[OK] vLLM server is running"
echo ""

# Check if RAG environment exists
RAG_VENV="$HOME/.venvs/rag"
if [ ! -d "$RAG_VENV" ]; then
    echo "[ERROR] RAG virtual environment not found at $RAG_VENV"
    echo "   Create it with: cd RAG && setup/0_create_venv_with_deps.sh"
    exit 1
fi
echo "[OK] RAG environment found"
echo ""

# Check if ChromaDB exists
CHROMA_DIR="$(dirname "$0")/RAG/chroma_db"
if [ ! -d "$CHROMA_DIR" ]; then
    echo "[ERROR] ChromaDB not found at $CHROMA_DIR"
    echo "   Create it with: cd RAG && setup/2_embed_and_store.py"
    exit 1
fi
echo "[OK] ChromaDB found"
echo ""

# Start proxy server
echo "[START] Starting RAG Proxy Server..."
echo ""
cd "$(dirname "$0")/RAG"
exec ./serve_rag_proxy.py --port "$PORT" --collection "$COLLECTION"
