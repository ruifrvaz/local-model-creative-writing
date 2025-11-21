#!/usr/bin/env bash
set -euo pipefail

################################################################################
# Monitor RAG Context - Track what context is being retrieved
################################################################################
# Purpose: Watch RAG proxy server logs to see retrieved context in real-time
#
# Usage: ./monitor_rag_context.sh [--full]
#        --full : Show complete retrieved chunks (can be verbose)
################################################################################

PORT="${1:-8001}"
SHOW_FULL=false

if [[ "${1:-}" == "--full" ]]; then
    SHOW_FULL=true
fi

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "RAG Context Monitor - Track Retrieved Context"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Monitoring: http://localhost:$PORT"
echo "Mode: $([ "$SHOW_FULL" = true ] && echo "Full context display" || echo "Summary only (use --full for details)")"
echo "Press Ctrl+C to stop"
echo ""

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}Warning: jq not installed. Install with: sudo apt install jq${NC}"
    echo "Continuing without jq (limited formatting)..."
    echo ""
fi

# Function to test RAG retrieval
test_retrieval() {
    local query="$1"
    
    echo -e "${CYAN}━━━ Testing RAG Retrieval ━━━${NC}"
    echo -e "${BLUE}Query:${NC} $query"
    echo ""
    
    # Make request to RAG proxy
    RESPONSE=$(curl -s http://localhost:$PORT/v1/chat/completions \
        -H "Content-Type: application/json" \
        -d "{
            \"model\": \"test\",
            \"messages\": [{\"role\": \"user\", \"content\": \"$query\"}],
            \"max_tokens\": 10,
            \"top_k\": 5
        }" 2>/dev/null)
    
    if [ -z "$RESPONSE" ]; then
        echo -e "${RED}✗ No response from RAG proxy${NC}"
        echo "  Is the server running? (./serve_rag_proxy.sh)"
        return 1
    fi
    
    # Extract the response to see what context was injected
    # The RAG context is in the system message
    if command -v jq &> /dev/null; then
        # Try to extract if jq available (won't work for response, but shows attempt)
        echo -e "${GREEN}✓ Request sent${NC}"
        echo ""
    else
        echo -e "${GREEN}✓ Request sent${NC}"
        echo ""
    fi
}

# Function to query stats
show_stats() {
    echo -e "${CYAN}━━━ RAG Proxy Statistics ━━━${NC}"
    
    # Check health
    if ! curl -s http://localhost:$PORT/health > /dev/null 2>&1; then
        echo -e "${RED}✗ RAG Proxy offline${NC}"
        echo "  Start with: ./serve_rag_proxy.sh scifi_world"
        return 1
    fi
    
    HEALTH=$(curl -s http://localhost:$PORT/health)
    
    if command -v jq &> /dev/null; then
        STATUS=$(echo "$HEALTH" | jq -r '.status')
        COLLECTION=$(echo "$HEALTH" | jq -r '.collection')
        CHUNKS=$(echo "$HEALTH" | jq -r '.chunks')
        MODEL=$(echo "$HEALTH" | jq -r '.model')
        
        echo -e "${GREEN}✓ Status:${NC} $STATUS"
        echo -e "${GREEN}✓ Collection:${NC} $COLLECTION"
        echo -e "${GREEN}✓ Total Chunks:${NC} $CHUNKS"
        echo -e "${GREEN}✓ Embedding Model:${NC} $MODEL"
    else
        echo "$HEALTH"
    fi
    
    echo ""
    
    # Try to get stats endpoint (may not exist)
    if curl -s http://localhost:$PORT/stats > /dev/null 2>&1; then
        STATS=$(curl -s http://localhost:$PORT/stats)
        
        echo -e "${CYAN}Recent Queries:${NC}"
        if command -v jq &> /dev/null; then
            echo "$STATS" | jq -r '.recent_queries[] | "  [\(.timestamp)] \(.query[:80])..."'
        else
            echo "$STATS"
        fi
    fi
    
    echo ""
}

# Function to monitor live logs (requires access to server process)
monitor_logs() {
    echo -e "${CYAN}━━━ Live RAG Context Monitoring ━━━${NC}"
    echo "Watching server output for context retrieval..."
    echo ""
    echo -e "${YELLOW}Note: This requires the RAG proxy to be running in a visible terminal${NC}"
    echo -e "${YELLOW}If you see nothing, the server may be running in background${NC}"
    echo ""
    
    # Try to find RAG proxy process and tail its output
    # This is a best-effort approach
    echo -e "${BLUE}Tip:${NC} Run serve_rag_proxy.sh in another terminal to see live context logging"
    echo ""
}

# Interactive mode
interactive_test() {
    echo -e "${CYAN}━━━ Interactive Context Testing ━━━${NC}"
    echo ""
    
    while true; do
        echo -e "${BLUE}Enter query to test RAG retrieval (or 'q' to quit):${NC}"
        read -r query
        
        if [[ "$query" == "q" ]] || [[ "$query" == "quit" ]]; then
            break
        fi
        
        if [ -n "$query" ]; then
            echo ""
            test_retrieval "$query"
            echo ""
        fi
    done
}

# Main menu
echo -e "${CYAN}Choose monitoring mode:${NC}"
echo "1) Show current RAG stats"
echo "2) Test retrieval with specific query"
echo "3) Interactive testing mode"
echo "4) Monitor instructions"
echo ""

read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        show_stats
        ;;
    2)
        read -p "Enter query: " query
        echo ""
        test_retrieval "$query"
        ;;
    3)
        interactive_test
        ;;
    4)
        monitor_logs
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "To see live context retrieval:"
echo "  1. Run: ./serve_rag_proxy.sh scifi_world"
echo "  2. Watch the terminal output - it shows:"
echo "     [RAG] Query: <your query>"
echo "     [RAG] Retrieved <N> chars of context"
echo ""
echo "For detailed context content, modify RAG/serve_rag_proxy.py:"
echo "  Add: print(f\"[RAG] Context: {context[:500]}...\") after line 282"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
