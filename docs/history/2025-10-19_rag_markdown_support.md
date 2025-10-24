# RAG Markdown Support Implementation

**Date**: October 19, 2025  
**Context**: Added proper markdown document support to RAG pipeline  
**Issue**: Initial markdown loading failed due to missing dependencies

---

## Problem Analysis

When testing the RAG workflow with `example_vllm_reference.md`, the ingestion script failed because:

1. **UnstructuredMarkdownLoader** requires the `unstructured` package
2. The `unstructured` package requires the `markdown` library as a dependency
3. Neither package was included in the initial RAG environment setup

### Why This Matters

Loading markdown as plain text would cause **data pollution**:
- Formatting characters (`#`, `**`, `*`, `-`, etc.) would be embedded
- Queries wouldn't match well due to markdown syntax interference
- Token space wasted on formatting characters
- Example: `**Elena Vasquez**` embeds differently than `Elena Vasquez`

The `unstructured` package properly parses markdown structure and extracts clean text, resulting in better embeddings and retrieval quality.

---

## Solution Implemented

### 1. Installed Missing Packages

```bash
source ~/.venvs/rag/bin/activate
pip install unstructured markdown
```

### 2. Updated Step 0: `0_create_venv_with_deps.sh`

**Header Documentation**
```bash
# What this installs in ~/.venvs/rag:
#   - chromadb: Vector database with persistence
#   - sentence-transformers: Embedding models (CPU-based)
#   - langchain-community: Document loaders
#   - langchain-text-splitters: Text chunking utilities
#   - openai: Client for vLLM server (OpenAI-compatible)
#   - unstructured: Document parsing (markdown, PDF, etc.)        # ← ADDED
#   - markdown: Markdown parsing library (dependency)              # ← ADDED
```

**Installation Steps**
```bash
echo ""
echo "[INSTALL] Step 4/5: Installing LangChain components..."
pip install langchain-community==0.3.14 langchain-text-splitters==0.3.4

echo ""
echo "[INSTALL] Step 5/6: Installing document parsing..."          # ← NEW STEP
pip install unstructured markdown                                  # ← ADDED

echo ""
echo "[INSTALL] Step 6/6: Installing OpenAI client (for vLLM)..."  # ← RENUMBERED
pip install openai==1.54.3
```

**Verification Dictionary**
```python
packages = {
    "chromadb": "Vector database",
    "sentence-transformers": "Embedding models",
    "langchain-community": "Document loaders",
    "langchain-text-splitters": "Text chunking",
    "unstructured": "Document parsing",        # ← ADDED
    "markdown": "Markdown parser",             # ← ADDED
    "openai": "vLLM client"
}
```

**Import Tests**
```python
import chromadb
import sentence_transformers
import langchain_community
import langchain_text_splitters
import unstructured        # ← ADDED
import markdown            # ← ADDED
from openai import OpenAI
```

### 3. Updated Step 1: `1_ingest.py`

**Enhanced Docstring**
```python
"""
Step 1: Document Ingestion and Chunking
Purpose: Load documents from data/ directory and split into chunks
Usage: ./1_ingest.py [--chunk-size 1000] [--chunk-overlap 200]

Supported formats:                                                 # ← ADDED SECTION
  - .txt files (plain text)
  - .md files (markdown - formatting stripped for clean embeddings)

Dependencies:                                                      # ← ADDED SECTION
  - unstructured: Parses markdown and strips formatting syntax
  - markdown: Markdown parsing library (required by unstructured)

Note: Uses RAG virtual environment at ~/.venvs/rag
"""
```

**Improved Error Handling**
```python
documents = []
for file_type, loader in loaders.items():
    try:
        docs = loader.load()
        print(f"[OK] Loaded {len(docs)} {file_type.upper()} files")
        documents.extend(docs)
    except ModuleNotFoundError as e:                               # ← ADDED
        if "unstructured" in str(e) or "markdown" in str(e):       # ← ADDED
            print(f"[ERROR] Missing {file_type.upper()} support: {e}")
            print(f"[FIX] Install missing packages:")
            print(f"   source ~/.venvs/rag/bin/activate")
            print(f"   pip install unstructured markdown")
        else:
            print(f"[WARN] No {file_type.upper()} files found or error: {e}")
    except Exception as e:
        print(f"[WARN] No {file_type.upper()} files found or error: {e}")
```

---

## Testing Results

### Before Fix
```
Error loading file /home/ruifrvaz/scifi-llm/RAG/data/example_vllm_reference.md
[WARN] No MD files found or error: No module named 'unstructured'
[ERROR] No documents found!
```

### After Fix
```
[OK] Loaded 1 MD files

[CHUNK] Splitting documents:
   Chunk size: 1000 characters (~750 words)
   Overlap: 200 characters
[OK] Created 4 chunks

[STATS] Chunk statistics:
   Total chunks: 4
   Average length: 772 characters
   Min length: 333
   Max length: 997
```

### Verification of Clean Text Extraction
```bash
$ cat chunks/chunks_latest.json | jq -r '.chunks[0].content' | head -10
Example Science Fiction Worldbuilding Document

The Arcturian Homeworld

Planet: Arcturus IV (local name: Karantha)

Atmosphere: Thin but breathable, oxygen-nitrogen mix with 15%...
```

**Result**: ✅ No markdown formatting characters (`#`, `**`, `-`) in output  
**Outcome**: Clean text ready for embedding

---

## Benefits

1. **Better Embeddings**: Clean text without markdown syntax noise
2. **Improved Retrieval**: Queries match content, not formatting
3. **Token Efficiency**: No wasted space on formatting characters
4. **Future-Proof**: Setup script now installs all required dependencies
5. **Better UX**: Clear error messages guide users if packages are missing
6. **Documentation**: Explains why markdown parsing is necessary

---

## Files Modified

1. `/home/ruifrvaz/scifi-llm/RAG/0_create_venv_with_deps.sh`
   - Added unstructured/markdown to header comments
   - Added Step 5/6 for document parsing installation
   - Updated verification tests
   - Renumbered existing Step 5 → Step 6

2. `/home/ruifrvaz/scifi-llm/RAG/1_ingest.py`
   - Enhanced docstring with supported formats
   - Added dependencies section
   - Improved error handling with helpful fix instructions

---

## Dependencies Added

| Package | Version | Purpose |
|---------|---------|---------|
| `unstructured` | latest | Document parsing framework (markdown, PDF, DOCX, etc.) |
| `markdown` | latest | Markdown to HTML conversion (required by unstructured) |

**Note**: These packages are now part of the standard RAG environment setup.

---

## Next Steps

- ✅ Step 0: RAG environment with all dependencies
- ✅ Step 1: Document ingestion with markdown support
- 🔄 Step 2: Embedding and storage (ready to proceed)
- ⏳ Step 3: Retrieval testing
- ⏳ Step 4: Query pipeline

---

## Related Documentation

- **Original Setup**: `scifi-llm/RAG/QUICK_START.md`
- **Implementation Guide**: `scifi-llm/RAG/RAG_IMPLEMENTATION_GUIDE.md`
- **Test Document**: `scifi-llm/RAG/data/example_vllm_reference.md`
- **Output Chunks**: `scifi-llm/RAG/chunks/chunks_latest.json`
