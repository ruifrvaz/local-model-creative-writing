#!/home/ruifrvaz/.venvs/rag/bin/python3
"""
Step 4: RAG Query Pipeline
Purpose: Complete RAG workflow - retrieve context and generate answers with vLLM
Usage: ./4_query.py "Your question here" [--collection scifi_world] [--interactive]

Process:
  1. Check vLLM server availability (localhost:8000)
  2. Load ChromaDB collection from Step 2
  3. Load embedding model (bge-large-en-v1.5)
  4. Retrieve top-K relevant chunks using semantic search
  5. Format chunks as context (max 4000 chars)
  6. Query vLLM with context + user question
  7. Display answer, sources, distances, and token usage
  8. Save query results to query_results/ folder (JSON format)

Output:
  - Generated answer using retrieved context
  - Source citations with similarity distances
  - Token usage statistics (prompt + completion)
  - query_results/rag_query_YYYYMMDD_HHMMSS.json (timestamped)
  - query_results/rag_query_latest.json (always latest)

Dependencies:
  - sentence-transformers: Query embedding generation
  - chromadb: Vector similarity search
  - openai: vLLM API client (OpenAI-compatible)
  
Requirements:
  - vLLM server running: cd .. && ./serve_vllm.sh
  - ChromaDB collection exists: setup/2_embed_and_store.py

Note: Uses RAG virtual environment at ~/.venvs/rag
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from openai import OpenAI

# Directories
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"
QUERY_RESULTS_DIR = Path(__file__).parent / "query_results"
QUERY_RESULTS_DIR.mkdir(exist_ok=True)

# Embedding model (must match Step 2)
EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"

# vLLM server configuration
VLLM_BASE_URL = "http://localhost:8000/v1"
VLLM_API_KEY = "dummy"  # vLLM doesn't require auth


def check_vllm_server():
    """Check if vLLM server is running"""
    try:
        client = OpenAI(
            base_url=VLLM_BASE_URL,
            api_key=VLLM_API_KEY,
            http_client=None  # Disable proxy handling
        )
        models = client.models.list()
        model_name = models.data[0].id
        print(f"[OK] vLLM server running - Model: {model_name}")
        return model_name
    except Exception as e:
        print(f"[ERROR] vLLM server not responding: {e}")
        print(f"[INFO] Start server: cd .. && ./serve_vllm.sh")
        return None


def load_vector_store(persist_dir, collection_name):
    """Load ChromaDB collection"""
    print(f"[LOAD] Loading collection: {collection_name}")
    
    if not persist_dir.exists():
        print(f"[ERROR] ChromaDB not found: {persist_dir}")
        print(f"[INFO] Run setup/2_embed_and_store.py first")
        return None, None
    
    client = chromadb.PersistentClient(
        path=str(persist_dir),
        settings=Settings(anonymized_telemetry=False)
    )
    
    try:
        collection = client.get_collection(name=collection_name)
        print(f"[OK] Collection loaded - {collection.count()} chunks")
        return client, collection
    except Exception as e:
        print(f"[ERROR] Collection not found: {e}")
        return client, None


def create_embedder():
    """Load embedding model (must match Step 2)"""
    print(f"[EMBED] Loading model: {EMBEDDING_MODEL}")
    embedder = SentenceTransformer(EMBEDDING_MODEL)
    print(f"[OK] Model loaded")
    return embedder


def retrieve_chunks(collection, embedder, query, top_k=5):
    """Retrieve most relevant chunks"""
    print(f"\n[RETRIEVE] Searching for relevant chunks...")
    print(f"   Query: {query}")
    print(f"   Top-K: {top_k}")
    
    # Generate query embedding
    query_embedding = embedder.encode([query])[0]
    
    # Search
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k
    )
    
    if not results['documents'][0]:
        print("[WARN] No results found")
        return None
    
    print(f"[OK] Retrieved {len(results['documents'][0])} chunks")
    
    return {
        "documents": results['documents'][0],
        "distances": results['distances'][0],
        "metadatas": results['metadatas'][0]
    }


def format_context(retrieved, max_length=4000):
    """Format retrieved chunks into context string"""
    context_parts = []
    current_length = 0
    
    for i, (doc, metadata) in enumerate(zip(retrieved['documents'], retrieved['metadatas']), 1):
        source = metadata.get('source', 'unknown')
        chunk_text = f"[Source {i}: {source}]\n{doc}\n"
        chunk_length = len(chunk_text)
        
        if current_length + chunk_length > max_length:
            break
        
        context_parts.append(chunk_text)
        current_length += chunk_length
    
    return "\n".join(context_parts)


def query_vllm(query, context, model_name, temperature=0.7, max_tokens=500):
    """Query vLLM with retrieved context"""
    print(f"\n[GENERATE] Querying vLLM...")
    print(f"   Model: {model_name}")
    print(f"   Context length: {len(context)} chars")
    
    # Create OpenAI client
    client = OpenAI(
        base_url=VLLM_BASE_URL,
        api_key=VLLM_API_KEY,
        http_client=None  # Disable proxy handling
    )
    
    # Build messages
    system_message = f"""Answer the user's question using the provided context.
If the answer is not in the context, say so clearly.
Be concise and cite relevant sources when possible.

Context:
{context}"""
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": query}
    ]
    
    # Query
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature
    )
    
    print(f"[OK] Response generated")
    print(f"   Tokens: {response.usage.prompt_tokens} prompt + {response.usage.completion_tokens} completion")
    
    return response


def save_query_result(query, result, collection_name, model_name, retrieved):
    """Save query result to JSON file"""
    timestamp = datetime.now()
    timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
    
    # Build detailed result structure
    query_log = {
        "timestamp": timestamp.isoformat(),
        "collection": collection_name,
        "embedding_model": EMBEDDING_MODEL,
        "llm_model": model_name,
        "query": query,
        "answer": result["answer"],
        "usage": result["usage"],
        "sources": [
            {
                "rank": i + 1,
                "distance": float(distance),
                "source": metadata.get("source", "unknown"),
                "chunk_index": metadata.get("chunk_index"),
                "length": len(doc),
                "content": doc
            }
            for i, (doc, distance, metadata) in enumerate(zip(
                retrieved['documents'],
                retrieved['distances'],
                retrieved['metadatas']
            ))
        ]
    }
    
    # Save timestamped file
    timestamped_file = QUERY_RESULTS_DIR / f"rag_query_{timestamp_str}.json"
    with open(timestamped_file, 'w') as f:
        json.dump(query_log, f, indent=2)
    
    # Save latest file
    latest_file = QUERY_RESULTS_DIR / "rag_query_latest.json"
    with open(latest_file, 'w') as f:
        json.dump(query_log, f, indent=2)
    
    print(f"\n[SAVED] Query result: {timestamped_file.name}")


def rag_query(query, collection, embedder, model_name, collection_name, top_k=5, temperature=0.7, max_tokens=500):
    """Complete RAG pipeline"""
    print("\n" + "━" * 80)
    print("RAG Query Pipeline")
    print("━" * 80)
    print(f"Query: {query}")
    print("")
    
    # 1. Retrieve
    retrieved = retrieve_chunks(collection, embedder, query, top_k)
    
    if not retrieved:
        print("[ERROR] No relevant context found")
        return None
    
    # 2. Format context
    context = format_context(retrieved)
    
    # 3. Query LLM
    response = query_vllm(query, context, model_name, temperature, max_tokens)
    
    # 4. Build result
    result = {
        "answer": response.choices[0].message.content,
        "sources": retrieved['documents'],
        "distances": retrieved['distances'],
        "usage": {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }
    }
    
    # 5. Save to JSON
    save_query_result(query, result, collection_name, model_name, retrieved)
    
    # 6. Display results
    print("\n" + "━" * 80)
    print("ANSWER")
    print("━" * 80)
    print(response.choices[0].message.content)
    
    print("\n" + "━" * 80)
    print("SOURCES")
    print("━" * 80)
    for i, (doc, distance, metadata) in enumerate(zip(
        retrieved['documents'],
        retrieved['distances'],
        retrieved['metadatas']
    ), 1):
        print(f"\n[{i}] Distance: {distance:.4f}")
        print(f"    Source: {metadata.get('source', 'unknown')}")
        print(f"    Preview: {doc[:150]}...")
    
    print("\n" + "━" * 80)
    print("USAGE")
    print("━" * 80)
    print(f"Prompt tokens: {response.usage.prompt_tokens}")
    print(f"Completion tokens: {response.usage.completion_tokens}")
    print(f"Total tokens: {response.usage.total_tokens}")
    
    return result


def main():
    parser = argparse.ArgumentParser(description="RAG query pipeline for science fiction writing")
    parser.add_argument(
        "query",
        type=str,
        nargs="?",
        help="Question to ask (or use --interactive)"
    )
    parser.add_argument(
        "--collection",
        type=str,
        default="scifi_world",
        help="ChromaDB collection name (default: scifi_world)"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of chunks to retrieve (default: 5, use 10 for worldbuilding)"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.85,
        help="LLM temperature (default: 0.85 for creative writing)"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=800,
        help="Max tokens in response (default: 800)"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Interactive query mode"
    )
    
    args = parser.parse_args()
    
    print("━" * 80)
    print("Step 4: RAG Query Pipeline - Science Fiction Writing")
    print("━" * 80)
    print(f"Timestamp: {datetime.now()}")
    print(f"Embedding model: {EMBEDDING_MODEL}")
    print("")
    
    # Check vLLM server
    model_name = check_vllm_server()
    if not model_name:
        return
    
    # Load vector store
    client, collection = load_vector_store(CHROMA_DIR, args.collection)
    if not collection:
        return
    
    # Load embedder
    embedder = create_embedder()
    
    # Query or interactive mode
    if args.interactive:
        print("\n" + "━" * 80)
        print("Interactive RAG Mode - Enter queries (type 'quit' to exit)")
        print("━" * 80)
        
        while True:
            try:
                query = input("\nQuery: ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("[INFO] Exiting")
                    break
                
                rag_query(
                    query, collection, embedder, model_name, args.collection,
                    args.top_k, args.temperature, args.max_tokens
                )
                
            except KeyboardInterrupt:
                print("\n[INFO] Exiting")
                break
            except Exception as e:
                print(f"[ERROR] {e}")
    
    elif args.query:
        # Single query
        rag_query(
            args.query, collection, embedder, model_name, args.collection,
            args.top_k, args.temperature, args.max_tokens
        )
        
        print("\n[TIP] Run with --interactive for multiple queries")
    
    else:
        print("[ERROR] No query provided")
        print("[INFO] Usage: ./4_query.py 'Your question here'")
        print("[INFO] Or use: ./4_query.py --interactive")


if __name__ == "__main__":
    main()
