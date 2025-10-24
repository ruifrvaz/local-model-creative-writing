#!/home/ruifrvaz/.venvs/rag/bin/python3
"""
Step 1: Document Ingestion and Chunking
Purpose: Load documents from data/ directory and split into chunks
Usage: ./1_ingest.py [--chunk-size 1000] [--chunk-overlap 200]

Supported formats:
  - .txt files (plain text)
  - .md files (markdown - formatting stripped for clean embeddings)

Dependencies:
  - unstructured: Parses markdown and strips formatting syntax
  - markdown: Markdown parsing library (required by unstructured)

Note: Uses RAG virtual environment at ~/.venvs/rag
"""

import argparse
import json
from pathlib import Path
from datetime import datetime
from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Directories
DATA_DIR = Path(__file__).parent / "data"
CHUNKS_DIR = Path(__file__).parent / "chunks"
CHUNKS_DIR.mkdir(exist_ok=True)


def load_documents(data_dir):
    """Load all documents from data directory"""
    print(f"[LOAD] Loading documents from: {data_dir}")
    
    if not data_dir.exists():
        print(f"[ERROR] Data directory does not exist: {data_dir}")
        print(f"[INFO] Creating directory: {data_dir}")
        data_dir.mkdir(parents=True, exist_ok=True)
        print(f"[INFO] Please add documents to {data_dir}/ and run again")
        return []
    
    # Load text and markdown files
    loaders = {
        "txt": DirectoryLoader(
            str(data_dir),
            glob="**/*.txt",
            loader_cls=TextLoader,
            show_progress=True
        ),
        "md": DirectoryLoader(
            str(data_dir),
            glob="**/*.md",
            loader_cls=UnstructuredMarkdownLoader,
            show_progress=True
        ),
    }
    
    documents = []
    for file_type, loader in loaders.items():
        try:
            docs = loader.load()
            print(f"[OK] Loaded {len(docs)} {file_type.upper()} files")
            documents.extend(docs)
        except ModuleNotFoundError as e:
            if "unstructured" in str(e) or "markdown" in str(e):
                print(f"[ERROR] Missing {file_type.upper()} support: {e}")
                print(f"[FIX] Install missing packages:")
                print(f"   source ~/.venvs/rag/bin/activate")
                print(f"   pip install unstructured markdown")
            else:
                print(f"[WARN] No {file_type.upper()} files found or error: {e}")
        except Exception as e:
            print(f"[WARN] No {file_type.upper()} files found or error: {e}")
    
    return documents


def chunk_documents(documents, chunk_size=1000, chunk_overlap=200):
    """Split documents into chunks with overlap"""
    print(f"\n[CHUNK] Splitting documents:")
    print(f"   Chunk size: {chunk_size} characters (~{chunk_size*0.75:.0f} words)")
    print(f"   Overlap: {chunk_overlap} characters")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documents)
    
    print(f"[OK] Created {len(chunks)} chunks")
    
    # Stats
    chunk_lengths = [len(chunk.page_content) for chunk in chunks]
    avg_length = sum(chunk_lengths) / len(chunk_lengths) if chunk_lengths else 0
    
    print(f"\n[STATS] Chunk statistics:")
    print(f"   Total chunks: {len(chunks)}")
    print(f"   Average length: {avg_length:.0f} characters")
    print(f"   Min length: {min(chunk_lengths) if chunk_lengths else 0}")
    print(f"   Max length: {max(chunk_lengths) if chunk_lengths else 0}")
    
    return chunks


def save_chunks(chunks, output_file):
    """Save chunks to JSON file"""
    print(f"\n[SAVE] Saving chunks to: {output_file}")
    
    chunks_data = {
        "timestamp": datetime.now().isoformat(),
        "total_chunks": len(chunks),
        "chunks": [
            {
                "id": i,
                "content": chunk.page_content,
                "metadata": chunk.metadata,
                "length": len(chunk.page_content)
            }
            for i, chunk in enumerate(chunks)
        ]
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chunks_data, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Chunks saved successfully")
    print(f"   File: {output_file}")
    print(f"   Size: {output_file.stat().st_size / 1024:.1f} KB")


def main():
    parser = argparse.ArgumentParser(description="Ingest and chunk documents")
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Chunk size in characters (default: 1000)"
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="Overlap between chunks (default: 200)"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default=str(DATA_DIR),
        help=f"Data directory (default: {DATA_DIR})"
    )
    
    args = parser.parse_args()
    
    print("━" * 80)
    print("Step 1: Document Ingestion and Chunking")
    print("━" * 80)
    print(f"Timestamp: {datetime.now()}")
    print(f"Data directory: {args.data_dir}")
    print("")
    
    # Load documents
    data_dir = Path(args.data_dir)
    documents = load_documents(data_dir)
    
    if not documents:
        print("\n[ERROR] No documents found!")
        print(f"[INFO] Add .txt or .md files to: {data_dir}/")
        print("[INFO] Example:")
        print(f"   cp ../AGENTS.md {data_dir}/")
        print(f"   cp ../docs/*.md {data_dir}/")
        return
    
    # Chunk documents
    chunks = chunk_documents(documents, args.chunk_size, args.chunk_overlap)
    
    if not chunks:
        print("\n[ERROR] No chunks created!")
        return
    
    # Save chunks
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = CHUNKS_DIR / f"chunks_{timestamp}.json"
    save_chunks(chunks, output_file)
    
    # Also save as latest for easy access
    latest_file = CHUNKS_DIR / "chunks_latest.json"
    save_chunks(chunks, latest_file)
    
    print("\n━" * 80)
    print("[COMPLETE] Document ingestion complete!")
    print("━" * 80)
    print(f"\n[NEXT] Next step: setup/2_embed_and_store.py")
    print(f"[TIP] View chunks: cat {latest_file} | jq '.chunks[0]'")
    print("")


if __name__ == "__main__":
    main()
