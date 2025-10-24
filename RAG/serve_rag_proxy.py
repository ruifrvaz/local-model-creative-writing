#!/home/ruifrvaz/.venvs/rag/bin/python3
"""
Step 5: RAG Proxy Server
Purpose: Transparent RAG layer that intercepts all vLLM requests
Usage: ./5_serve_rag_proxy.py [--port 8001] [--collection scifi_world]

Process:
  1. Load embedding model (bge-large-en-v1.5) at startup
  2. Connect to ChromaDB collection
  3. Start FastAPI server on port 8001
  4. Intercept all OpenAI API requests
  5. Retrieve relevant context from vector database
  6. Augment messages with RAG context
  7. Forward to vLLM server (port 8000)
  8. Return response to client

Output:
  - Transparent RAG proxy on http://localhost:8001
  - OpenAI-compatible API endpoints
  - Automatic context injection for all queries

Dependencies:
  - fastapi: Web framework for proxy server
  - uvicorn: ASGI server
  - sentence-transformers: Query embedding
  - chromadb: Vector database
  - openai: vLLM client

Requirements:
  - vLLM server running: cd .. && ./serve_vllm.sh
  - ChromaDB collection exists: setup/2_embed_and_store.py

Note: Uses RAG virtual environment at ~/.venvs/rag
"""

import argparse
from contextlib import asynccontextmanager
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import uvicorn

from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from openai import OpenAI

# Directories
CHROMA_DIR = Path(__file__).parent / "chroma_db"

# Embedding model (must match Step 2)
EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"

# vLLM server configuration
VLLM_BASE_URL = "http://localhost:8000/v1"
VLLM_API_KEY = "EMPTY"

# Global state (loaded once at startup)
embedder = None
chroma_client = None
collection = None
vllm_client = None

# Query history tracking (last 10 queries)
query_history = []
MAX_HISTORY = 10

# Pydantic models for OpenAI API compatibility
class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.85
    max_tokens: Optional[int] = 800
    stream: Optional[bool] = False
    top_k: Optional[int] = 5  # RAG-specific parameter

class CompletionRequest(BaseModel):
    model: str
    prompt: str
    temperature: Optional[float] = 0.85
    max_tokens: Optional[int] = 800
    stream: Optional[bool] = False
    top_k: Optional[int] = 5  # RAG-specific parameter


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown (replaces deprecated @app.on_event)"""
    # Startup
    global embedder, chroma_client, collection, vllm_client
    
    print("━" * 80)
    print("RAG Proxy Server - Startup")
    print("━" * 80)
    print(f"Timestamp: {datetime.now()}")
    print(f"Embedding model: {EMBEDDING_MODEL}")
    print(f"Collection: {app.state.collection_name}")
    print(f"vLLM backend: {VLLM_BASE_URL}")
    print("")
    
    # Check vLLM server
    print("[CHECK] Testing vLLM server...")
    try:
        test_client = OpenAI(
            base_url=VLLM_BASE_URL,
            api_key=VLLM_API_KEY,
            http_client=None
        )
        models = test_client.models.list()
        print(f"[OK] vLLM server responding - Model: {models.data[0].id}")
    except Exception as e:
        print(f"[ERROR] vLLM server not responding: {e}")
        print(f"[INFO] Start server: cd .. && ./serve_vllm.sh")
        raise RuntimeError("vLLM server not available") from e
    
    # Load components
    embedder = load_embedder()
    chroma_client, collection = load_vector_store(CHROMA_DIR, app.state.collection_name)
    vllm_client = OpenAI(
        base_url=VLLM_BASE_URL,
        api_key=VLLM_API_KEY,
        http_client=None  # Fix httpx compatibility
    )
    
    print("")
    print("━" * 80)
    print("[OK] RAG Proxy Server ready!")
    print("━" * 80)
    print(f"Listening on: http://localhost:{app.state.port}")
    print(f"All requests will be automatically augmented with RAG context")
    print("")
    
    yield
    
    # Shutdown (cleanup if needed)
    print("\n[SHUTDOWN] RAG Proxy Server shutting down...")


app = FastAPI(
    title="RAG Proxy Server",
    description="Transparent RAG layer for vLLM - automatically augments all requests with retrieved context",
    version="1.0.0",
    lifespan=lifespan  # Modern FastAPI lifespan management
)


def load_embedder():
    """Load embedding model at startup"""
    print(f"[EMBED] Loading model: {EMBEDDING_MODEL}")
    embedder = SentenceTransformer(EMBEDDING_MODEL)
    print(f"[OK] Model loaded")
    return embedder


def load_vector_store(persist_dir: Path, collection_name: str):
    """Load ChromaDB at startup"""
    print(f"\n[CHROMA] Loading vector store:")
    print(f"   Location: {persist_dir}")
    print(f"   Collection: {collection_name}")
    
    if not persist_dir.exists():
        raise ValueError(f"ChromaDB not found at {persist_dir}. Run setup/2_embed_and_store.py first.")
    
    client = chromadb.PersistentClient(
        path=str(persist_dir),
        settings=Settings(anonymized_telemetry=False)
    )
    
    try:
        collection = client.get_collection(name=collection_name)
        print(f"[OK] Collection loaded: {collection.count()} chunks")
        return client, collection
    except Exception as e:
        raise ValueError(f"Collection '{collection_name}' not found. Run setup/2_embed_and_store.py first.")


def retrieve_context(query: str, top_k: int = 5) -> str:
    """Retrieve relevant context for query"""
    # Generate query embedding
    query_embedding = embedder.encode([query])[0]
    
    # Search
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k
    )
    
    if not results['documents'][0]:
        return ""
    
    # Format context
    context_parts = []
    for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
        source = metadata.get('source', 'unknown')
        context_parts.append(f"[Source {i}: {source}]\n{doc}")
    
    return "\n\n".join(context_parts)


def augment_messages_with_context(messages: List[Message], context: str, top_k: int) -> List[Message]:
    """Insert RAG context into message history"""
    if not context:
        return messages
    
    # Extract the user's question (last user message)
    user_query = None
    for msg in reversed(messages):
        if msg.role == "user":
            user_query = msg.content
            break
    
    if not user_query:
        return messages
    
    # Create RAG system message
    rag_system_message = Message(
        role="system",
        content=f"""You are a helpful assistant with access to the user's science fiction writing documents.
Use the following retrieved context to inform your responses. If the context is relevant, reference it naturally.
If the context doesn't help, rely on your general knowledge.

Retrieved Context (from top {top_k} relevant chunks):
{context}"""
    )
    
    # Insert after any existing system message, or at the start
    new_messages = []
    system_added = False
    for msg in messages:
        if msg.role == "system" and not system_added:
            new_messages.append(msg)
            new_messages.append(rag_system_message)
            system_added = True
        else:
            new_messages.append(msg)
    
    # If no system message existed, add RAG context at start
    if not system_added:
        new_messages.insert(0, rag_system_message)
    
    return new_messages


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "RAG Proxy Server",
        "status": "running",
        "vllm_backend": VLLM_BASE_URL,
        "collection": app.state.collection_name,
        "chunks": collection.count() if collection else 0,
        "model": EMBEDDING_MODEL
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions endpoint with automatic RAG"""
    try:
        # Extract user query for RAG retrieval
        user_query = None
        for msg in reversed(request.messages):
            if msg.role == "user":
                user_query = msg.content
                break
        
        if not user_query:
            raise HTTPException(status_code=400, detail="No user message found")
        
        # Retrieve context
        print(f"[RAG] Query: {user_query[:100]}...")
        context = retrieve_context(user_query, top_k=request.top_k)
        print(f"[RAG] Retrieved {len(context)} chars of context")
        
        # Track query
        query_history.append({
            "timestamp": datetime.now().isoformat(),
            "query": user_query[:200],  # First 200 chars
            "context_length": len(context),
            "model": request.model
        })
        if len(query_history) > MAX_HISTORY:
            query_history.pop(0)
        
        # Augment messages with context
        augmented_messages = augment_messages_with_context(
            request.messages, 
            context,
            request.top_k
        )
        
        # Forward to vLLM
        print(f"[VLLM] Forwarding to {VLLM_BASE_URL}")
        response = vllm_client.chat.completions.create(
            model=request.model,
            messages=[{"role": msg.role, "content": msg.content} for msg in augmented_messages],
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=request.stream
        )
        
        if request.stream:
            # Handle streaming response
            async def generate():
                for chunk in response:
                    yield f"data: {chunk.model_dump_json()}\n\n"
                yield "data: [DONE]\n\n"
            
            return StreamingResponse(generate(), media_type="text/event-stream")
        else:
            # Return regular response
            return response.model_dump()
    
    except Exception as e:
        print(f"[ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/completions")
async def completions(request: CompletionRequest):
    """OpenAI-compatible completions endpoint with automatic RAG"""
    try:
        # Retrieve context
        print(f"[RAG] Query: {request.prompt[:100]}...")
        context = retrieve_context(request.prompt, top_k=request.top_k)
        print(f"[RAG] Retrieved {len(context)} chars of context")
        
        # Augment prompt with context
        augmented_prompt = f"""Retrieved Context:
{context}

User Query:
{request.prompt}

Response:"""
        
        # Forward to vLLM
        print(f"[VLLM] Forwarding to {VLLM_BASE_URL}")
        response = vllm_client.completions.create(
            model=request.model,
            prompt=augmented_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=request.stream
        )
        
        if request.stream:
            # Handle streaming response
            async def generate():
                for chunk in response:
                    yield f"data: {chunk.model_dump_json()}\n\n"
                yield "data: [DONE]\n\n"
            
            return StreamingResponse(generate(), media_type="text/event-stream")
        else:
            # Return regular response
            return response.model_dump()
    
    except Exception as e:
        print(f"[ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "rag_proxy": "healthy",
        "embedder": "loaded" if embedder else "not loaded",
        "vector_store": "connected" if collection else "not connected",
        "chunks": collection.count() if collection else 0,
        "vllm_backend": VLLM_BASE_URL
    }


@app.get("/stats")
async def stats():
    """RAG proxy statistics and recent queries"""
    return {
        "total_queries": len(query_history),
        "recent_queries": query_history[-5:],  # Last 5 queries
        "chunks_available": collection.count() if collection else 0,
        "embedding_model": EMBEDDING_MODEL
    }


def main():
    parser = argparse.ArgumentParser(
        description="RAG Proxy Server - Transparent RAG layer for vLLM"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Port to listen on (default: 8001)"
    )
    parser.add_argument(
        "--collection",
        type=str,
        default="scifi_world",
        help="ChromaDB collection name (default: scifi_world)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    
    args = parser.parse_args()
    
    # Store in app state for startup handler
    app.state.collection_name = args.collection
    app.state.port = args.port
    
    # Run server
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info"
    )


if __name__ == "__main__":
    main()
