#!/home/ruifrvaz/.venvs/rag/bin/python3
"""
Step 3: Test Retrieval Quality
Purpose: Run test queries and validate retrieval accuracy
Usage: ./3_test_retrieval.py [--collection my_docs] [--interactive]

Process:
  1. Load ChromaDB collection from Step 2
  2. Initialize same embedding model (bge-large-en-v1.5)
  3. Run test queries or interactive mode
  4. Display results with similarity scores
  5. Save test results to test_results/ folder (JSON format)

Output:
  - test_results/retrieval_test_YYYYMMDD_HHMMSS.json (timestamped)
  - test_results/retrieval_test_latest.json (always latest)

Dependencies:
  - sentence-transformers: Query embedding generation
  - chromadb: Vector similarity search

Note: Uses RAG virtual environment at ~/.venvs/rag
"""

import argparse
import json
from pathlib import Path
from datetime import datetime
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# Directories
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"
TEST_RESULTS_DIR = Path(__file__).parent / "test_results"
TEST_RESULTS_DIR.mkdir(exist_ok=True)

# Embedding model (must match Step 2)
EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"


def load_vector_store(persist_dir, collection_name):
    """Load ChromaDB client and collection"""
    print(f"[LOAD] Loading vector store:")
    print(f"   Directory: {persist_dir}")
    print(f"   Collection: {collection_name}")
    
    if not persist_dir.exists():
        print(f"[ERROR] ChromaDB directory not found: {persist_dir}")
        print(f"[INFO] Run setup/2_embed_and_store.py first")
        return None, None
    
    client = chromadb.PersistentClient(
        path=str(persist_dir),
        settings=Settings(anonymized_telemetry=False)
    )
    
    try:
        collection = client.get_collection(name=collection_name)
        count = collection.count()
        print(f"[OK] Collection loaded - {count} chunks")
        return client, collection
    except Exception as e:
        print(f"[ERROR] Collection '{collection_name}' not found: {e}")
        print(f"[INFO] Available collections: {[c.name for c in client.list_collections()]}")
        return client, None


def create_embedder():
    """Load embedding model (must match Step 2)"""
    print(f"\n[EMBED] Loading model: {EMBEDDING_MODEL}")
    embedder = SentenceTransformer(EMBEDDING_MODEL)
    print(f"[OK] Model loaded")
    return embedder


def test_retrieval(collection, embedder, query, top_k=5):
    """Test retrieval with a query and return results"""
    print(f"\n{'─' * 80}")
    print(f"Query: {query}")
    print(f"{'─' * 80}")
    
    # Generate query embedding
    query_embedding = embedder.encode([query])[0]
    
    # Search
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k
    )
    
    # Display results
    if not results['documents'][0]:
        print("[WARN] No results found")
        return None
    
    print(f"\nTop {len(results['documents'][0])} results:")
    
    retrieved_results = []
    for i, (doc, distance, metadata) in enumerate(zip(
        results['documents'][0],
        results['distances'][0],
        results['metadatas'][0]
    ), 1):
        print(f"\n[{i}] Distance: {distance:.4f}")
        print(f"    Source: {metadata.get('source', 'unknown')}")
        print(f"    Length: {metadata.get('length', 'unknown')} chars")
        print(f"    Content preview: {doc[:200]}...")
        
        # Capture for logging
        retrieved_results.append({
            "rank": i,
            "distance": float(distance),
            "source": metadata.get('source', 'unknown'),
            "length": metadata.get('length', 0),
            "content_preview": doc[:200],
            "full_content": doc
        })
    
    return retrieved_results


def run_test_queries(collection, embedder, top_k=5):
    """Run a set of test queries and log results"""
    # Define test queries based on science fiction worldbuilding content
    test_queries = [
        "What are Elena's personality traits?",
        "Tell me about the Arcturian homeworld atmosphere",
        "How does the FTL drive work?",
        "What happened in the previous chapter?",
        "Describe the Arcturian species",
    ]
    
    print("\n" + "━" * 80)
    print("Running Test Queries")
    print("━" * 80)
    
    # Capture all results
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "collection": collection.name,
        "embedding_model": EMBEDDING_MODEL,
        "top_k": top_k,
        "total_queries": len(test_queries),
        "queries": []
    }
    
    for query in test_queries:
        results = test_retrieval(collection, embedder, query, top_k)
        if results:
            test_results["queries"].append({
                "query": query,
                "results": results
            })
    
    print("\n" + "━" * 80)
    
    # Save results to JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = TEST_RESULTS_DIR / f"retrieval_test_{timestamp}.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n[SAVE] Test results saved to: {results_file}")
    
    # Also save as latest
    latest_file = TEST_RESULTS_DIR / "retrieval_test_latest.json"
    with open(latest_file, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    print(f"[SAVE] Latest results: {latest_file}")
    
    return test_results


def print_test_statistics(test_results):
    """Print summary statistics from test results"""
    if not test_results or not test_results.get("queries"):
        return
    
    print("\n" + "━" * 80)
    print("Test Statistics Summary")
    print("━" * 80)
    
    all_distances = []
    for query_result in test_results["queries"]:
        for result in query_result["results"]:
            all_distances.append(result["distance"])
    
    if all_distances:
        avg_distance = sum(all_distances) / len(all_distances)
        min_distance = min(all_distances)
        max_distance = max(all_distances)
        
        print(f"\nDistance Scores (lower = better match):")
        print(f"   Average: {avg_distance:.4f}")
        print(f"   Best (min): {min_distance:.4f}")
        print(f"   Worst (max): {max_distance:.4f}")
        print(f"   Total retrievals: {len(all_distances)}")
    
    print(f"\nQueries tested: {test_results['total_queries']}")
    print(f"Collection: {test_results['collection']}")
    print(f"Top-K per query: {test_results['top_k']}")


def interactive_mode(collection, embedder, top_k=5):
    """Interactive query mode"""
    print("\n" + "━" * 80)
    print("Interactive Mode - Enter queries (type 'quit' to exit)")
    print("━" * 80)
    
    while True:
        try:
            query = input("\nQuery: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("[INFO] Exiting interactive mode")
                break
            
            test_retrieval(collection, embedder, query, top_k)
            
        except KeyboardInterrupt:
            print("\n[INFO] Exiting interactive mode")
            break
        except Exception as e:
            print(f"[ERROR] {e}")


def main():
    parser = argparse.ArgumentParser(description="Test retrieval quality")
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
        help="Number of results to retrieve (default: 5)"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    
    args = parser.parse_args()
    
    print("━" * 80)
    print("Step 3: Test Retrieval Quality")
    print("━" * 80)
    print(f"Timestamp: {datetime.now()}")
    print(f"Embedding model: {EMBEDDING_MODEL}")
    print(f"Collection: {args.collection}")
    print(f"Top-K: {args.top_k}")
    print("")
    
    # Load vector store
    client, collection = load_vector_store(CHROMA_DIR, args.collection)
    
    if not collection:
        return
    
    # Load embedder
    embedder = create_embedder()
    
    if args.interactive:
        # Interactive mode
        interactive_mode(collection, embedder, args.top_k)
    else:
        # Run test queries and log results
        test_results = run_test_queries(collection, embedder, args.top_k)
        
        # Print statistics
        print_test_statistics(test_results)
    
    print("\n━" * 80)
    print("[COMPLETE] Retrieval testing complete!")
    print("━" * 80)
    print(f"\n[INFO] Test results directory: {TEST_RESULTS_DIR}")
    print(f"[NEXT] Next step: benchmarks/4_query.py 'Your question here'")
    print(f"[TIP] Run with --interactive for custom queries")
    print(f"[TIP] View results: cat {TEST_RESULTS_DIR}/retrieval_test_latest.json | jq")
    print("")


if __name__ == "__main__":
    main()
