#!/home/ruifrvaz/.venvs/rag/bin/python3
"""
Step 2: Generate Embeddings and Store in Vector Database
Purpose: Load chunks, create embeddings, store in ChromaDB
Usage: ./2_embed_and_store.py [--collection my_docs]

Process:
  1. Load chunks from Step 1 (chunks_latest.json)
  2. Initialize embedding model (BAAI/bge-large-en-v1.5, CPU-based)
  3. Generate embeddings for all chunks (batch processing)
  4. Store embeddings + metadata in ChromaDB (persistent storage)

Dependencies:
  - sentence-transformers: Embedding generation (bge-large-en-v1.5)
  - chromadb: Vector database with persistence

Note: Uses RAG virtual environment at ~/.venvs/rag
"""

import argparse
import json
import time
from pathlib import Path
from datetime import datetime
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# Directories
CHUNKS_DIR = Path(__file__).parent / "chunks"
CHROMA_DIR = Path(__file__).parent / "chroma_db"

# Embedding model - optimized for science fiction writing
# Using bge-large-en-v1.5 for best semantic understanding of:
# - Character personality nuances
# - Thematic connections
# - Worldbuilding details
# - Plot coherence
EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"  # 1024 dims


def load_chunks(chunks_file):
    """Load chunks from JSON file"""
    print(f"[LOAD] Loading chunks from: {chunks_file}")
    
    if not chunks_file.exists():
        print(f"[ERROR] Chunks file not found: {chunks_file}")
        print(f"[INFO] Run setup/1_ingest.py first")
        return None
    
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks_data = json.load(f)
    
    print(f"[OK] Loaded {chunks_data['total_chunks']} chunks")
    print(f"   Created: {chunks_data['timestamp']}")
    
    return chunks_data


def create_embedder():
    """Initialize embedding model (runs on CPU)"""
    print(f"\n[EMBED] Initializing embedding model:")
    print(f"   Model: {EMBEDDING_MODEL}")
    print(f"   Device: CPU (runs separate from vLLM GPU)")
    
    embedder = SentenceTransformer(EMBEDDING_MODEL)
    
    # Get embedding dimension
    test_embedding = embedder.encode(["test"])
    dim = len(test_embedding[0])
    print(f"[OK] Model loaded - Embedding dimension: {dim}")
    
    return embedder, dim


def generate_embeddings(chunks_data, embedder, batch_size=32):
    """Generate embeddings for all chunks"""
    chunks = chunks_data['chunks']
    total = len(chunks)
    
    print(f"\n[EMBED] Generating embeddings:")
    print(f"   Total chunks: {total}")
    print(f"   Batch size: {batch_size}")
    
    # Extract text content
    texts = [chunk['content'] for chunk in chunks]
    
    # Generate embeddings with progress
    start_time = time.time()
    embeddings = embedder.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True
    )
    elapsed = time.time() - start_time
    
    print(f"[OK] Embeddings generated")
    print(f"   Time: {elapsed:.2f}s")
    print(f"   Speed: {total/elapsed:.1f} chunks/sec")
    
    return embeddings


def create_vector_store(persist_dir):
    """Initialize ChromaDB client"""
    print(f"\n[STORE] Initializing ChromaDB:")
    print(f"   Directory: {persist_dir}")
    
    persist_dir.mkdir(parents=True, exist_ok=True)
    
    client = chromadb.PersistentClient(
        path=str(persist_dir),
        settings=Settings(
            anonymized_telemetry=False,
            allow_reset=True
        )
    )
    
    print(f"[OK] ChromaDB initialized")
    
    return client


def store_embeddings(client, collection_name, chunks_data, embeddings):
    """Store chunks and embeddings in ChromaDB collection"""
    chunks = chunks_data['chunks']
    
    print(f"\n[STORE] Storing in collection: {collection_name}")
    print(f"   Chunks: {len(chunks)}")
    
    # Delete existing collection if it exists
    try:
        client.delete_collection(name=collection_name)
        print(f"[INFO] Deleted existing collection: {collection_name}")
    except:
        pass
    
    # Create collection
    collection = client.create_collection(
        name=collection_name,
        metadata={
            "description": "RAG document store",
            "created_at": datetime.now().isoformat(),
            "total_chunks": len(chunks)
        }
    )
    
    # Prepare data for batch insert
    ids = [f"chunk_{chunk['id']}" for chunk in chunks]
    documents = [chunk['content'] for chunk in chunks]
    metadatas = [
        {
            **chunk['metadata'],
            "chunk_id": chunk['id'],
            "length": chunk['length']
        }
        for chunk in chunks
    ]
    
    # Store in batches
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        end_idx = min(i + batch_size, len(chunks))
        
        collection.add(
            ids=ids[i:end_idx],
            embeddings=embeddings[i:end_idx].tolist(),
            documents=documents[i:end_idx],
            metadatas=metadatas[i:end_idx]
        )
        
        print(f"[PROGRESS] Stored {end_idx}/{len(chunks)} chunks", end='\r')
    
    print(f"\n[OK] All chunks stored in ChromaDB")
    
    # Verify
    count = collection.count()
    print(f"[VERIFY] Collection contains {count} items")
    
    return collection


def main():
    parser = argparse.ArgumentParser(description="Generate embeddings and store in vector DB")
    parser.add_argument(
        "--collection",
        type=str,
        default="scifi_world",
        help="ChromaDB collection name (default: scifi_world)"
    )
    parser.add_argument(
        "--chunks-file",
        type=str,
        default=str(CHUNKS_DIR / "chunks_latest.json"),
        help="Chunks JSON file (default: chunks_latest.json)"
    )
    
    args = parser.parse_args()
    
    print("━" * 80)
    print("Step 2: Generate Embeddings and Store in Vector Database")
    print("━" * 80)
    print(f"Timestamp: {datetime.now()}")
    print(f"Embedding model: {EMBEDDING_MODEL} (optimized for fiction)")
    print(f"Collection: {args.collection}")
    print("")
    
    # Load chunks
    chunks_file = Path(args.chunks_file)
    chunks_data = load_chunks(chunks_file)
    
    if not chunks_data:
        return
    
    # Create embedder
    embedder, dim = create_embedder()
    
    # Generate embeddings
    embeddings = generate_embeddings(chunks_data, embedder)
    
    # Create vector store
    client = create_vector_store(CHROMA_DIR)
    
    # Store embeddings
    collection = store_embeddings(client, args.collection, chunks_data, embeddings)
    
    print("\n━" * 80)
    print("[COMPLETE] Embeddings generated and stored!")
    print("━" * 80)
    print(f"\n[INFO] Vector database:")
    print(f"   Location: {CHROMA_DIR}")
    print(f"   Collection: {args.collection}")
    print(f"   Chunks: {collection.count()}")
    print(f"   Embedding model: {EMBEDDING_MODEL}")
    print(f"   Embedding dim: {dim}")
    print(f"\n[NEXT] Next step: benchmarks/3_test_retrieval.py --collection {args.collection}")
    print("")


if __name__ == "__main__":
    main()
