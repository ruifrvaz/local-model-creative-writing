#!/usr/bin/env bash
set -euo pipefail

################################################################################
# Step 0: Install RAG Dependencies in Separate Virtual Environment
################################################################################
# Purpose: Create isolated RAG environment to avoid conflicts with vLLM
#
# What this installs in ~/.venvs/rag:
#   - chromadb: Vector database with persistence
#   - sentence-transformers: Embedding models (CPU-based)
#   - langchain-community: Document loaders
#   - langchain-text-splitters: Text chunking utilities
#   - openai: Client for vLLM server (OpenAI-compatible)
#   - unstructured: Document parsing (markdown, PDF, etc.)
#   - markdown: Markdown parsing library (dependency for unstructured)
#
# Why separate venv?
#   - Avoids dependency conflicts with vLLM
#   - RAG can use different package versions
#   - Cleaner separation of concerns
#   - Can update RAG independently
#
# Prerequisites:
#   - Python 3.12 available
#   - vLLM server running on port 8000 (for Step 4)
#
# Usage: ./0_create_venv_with_deps.sh
################################################################################

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[INSTALL] RAG Dependencies Installation (Separate Virtual Environment)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Check if Python 3.12 is available
echo "[CHECK] Checking Python version..."
PYTHON_CMD=$(which python3.12 || which python3 || which python)
PYTHON_VERSION=$($PYTHON_CMD --version)
echo "   Found: $PYTHON_VERSION at $PYTHON_CMD"
if [[ ! "$PYTHON_VERSION" =~ "3.12" ]]; then
    echo "[WARN] Warning: Expected Python 3.12, got $PYTHON_VERSION"
    echo "   Continuing anyway..."
fi
echo ""

# Create RAG virtual environment
RAG_VENV="$HOME/.venvs/rag"
if [ -d "$RAG_VENV" ]; then
    echo "[VENV] Virtual environment already exists at $RAG_VENV"
    echo "   Remove it? [y/N] "
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "[VENV] Removing old environment..."
        rm -rf "$RAG_VENV"
    else
        echo "[VENV] Using existing environment"
    fi
fi

if [ ! -d "$RAG_VENV" ]; then
    echo "[VENV] Creating new virtual environment at $RAG_VENV..."
    $PYTHON_CMD -m venv "$RAG_VENV"
    echo "[OK] Virtual environment created"
else
    echo "[OK] Using existing virtual environment"
fi
echo ""

# Activate the virtual environment
echo "[VENV] Activating virtual environment..."
source "$RAG_VENV/bin/activate" || {
    echo "[ERROR] Failed to activate virtual environment"
    exit 1
}
echo "[OK] Virtual environment activated: $RAG_VENV"
echo ""

# Install RAG dependencies
echo "[INSTALL] Installing RAG packages..."
echo ""

echo "[INSTALL] Step 1/5: Upgrading pip..."
python -m pip install -U pip setuptools wheel

echo ""
echo "[INSTALL] Step 2/5: Installing ChromaDB (vector database)..."
pip install chromadb==0.5.23

echo ""
echo "[INSTALL] Step 3/5: Installing sentence-transformers (embeddings)..."
pip install sentence-transformers==3.3.1

echo ""
echo "[INSTALL] Step 4/5: Installing LangChain components..."
pip install langchain-community==0.3.14 langchain-text-splitters==0.3.4

echo ""
echo "[INSTALL] Step 5/5: Installing document parsing..."
pip install unstructured markdown

echo ""
echo "[INSTALL] Step 6/7: Installing OpenAI client (for vLLM)..."
pip install openai==1.54.3

echo ""
echo "[INSTALL] Step 7/8: Fixing httpx compatibility..."
pip install "httpx==0.27.2" --quiet

echo ""
echo "[INSTALL] Step 8/8: Installing FastAPI and Uvicorn (for proxy server)..."
pip install fastapi uvicorn

echo ""
echo "[TEST] Verifying installations..."
python - <<'PY'
import importlib.metadata as m

packages = {
    "chromadb": "Vector database",
    "sentence-transformers": "Embedding models",
    "langchain-community": "Document loaders",
    "langchain-text-splitters": "Text chunking",
    "unstructured": "Document parsing",
    "markdown": "Markdown parser",
    "openai": "vLLM client",
    "fastapi": "Proxy server framework",
    "uvicorn": "ASGI server"
}

print("\nInstalled packages:")
print("─" * 60)
for pkg, desc in packages.items():
    try:
        version = m.version(pkg)
        print(f"✓ {pkg:25} {version:15} - {desc}")
    except:
        print(f"✗ {pkg:25} {'NOT FOUND':15} - {desc}")
        
print("─" * 60)
PY

echo ""
echo "[TEST] Testing imports..."
python - <<'PY'
try:
    import chromadb
    import sentence_transformers
    import langchain_community
    import langchain_text_splitters
    import unstructured
    import markdown
    from openai import OpenAI
    import fastapi
    import uvicorn
    print("[OK] All imports successful!")
except ImportError as e:
    print(f"[ERROR] Import failed: {e}")
    exit(1)
PY

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[OK] RAG dependencies installed successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "[INFO] RAG Virtual Environment:"
echo "   Location: $RAG_VENV"
echo "   Activate: source $RAG_VENV/bin/activate"
echo ""
echo "[INFO] All RAG scripts will auto-activate this environment"
echo ""
echo "[NEXT] Next steps:"
echo "   1. Add documents to RAG/data/"
echo "   2. Run: setup/1_ingest.py"
echo "   3. Run: setup/2_embed_and_store.py"
echo "   4. Run: benchmarks/3_test_retrieval.py"
echo "   5. Run: benchmarks/4_query.py 'Your question here'"
echo ""
echo "[NOTE] vLLM server must be running (port 8000) for Step 4"
echo ""
