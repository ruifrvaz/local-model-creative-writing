#!/usr/bin/env bash
set -euo pipefail

################################################################################
# Monitor RAG Proxy Server
################################################################################
# Purpose: Watch RAG proxy logs and stats in real-time
#
# Usage: ./monitor_rag_proxy.sh
################################################################################

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "RAG Proxy Monitor"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Monitoring: http://localhost:8001"
echo "Press Ctrl+C to stop"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check proxy health
check_health() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} Checking RAG proxy health..."
    
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        HEALTH=$(curl -s http://localhost:8001/health)
        echo -e "${GREEN}✓${NC} RAG Proxy: Online"
        echo "$HEALTH" | jq '.' 2>/dev/null || echo "$HEALTH"
    else
        echo -e "${YELLOW}✗${NC} RAG Proxy: Offline"
        echo "   Start with: ./serve_rag_proxy.sh"
    fi
    
    echo ""
}

# Function to show recent activity
show_activity() {
    echo -e "${BLUE}Recent RAG Queries:${NC}"
    
    if curl -s http://localhost:8001/stats > /dev/null 2>&1; then
        STATS=$(curl -s http://localhost:8001/stats)
        
        # Extract and display recent queries
        RECENT=$(echo "$STATS" | jq -r '.recent_queries[] | "  [\(.timestamp)] \(.query[:80])..."' 2>/dev/null)
        
        if [ -n "$RECENT" ]; then
            echo "$RECENT"
        else
            echo "  (No queries yet)"
        fi
        
        # Show total count
        TOTAL=$(echo "$STATS" | jq -r '.total_queries' 2>/dev/null)
        echo ""
        echo "  Total queries in session: $TOTAL"
    else
        echo "  (Stats endpoint unavailable)"
    fi
    
    echo ""
}

# Initial check
check_health

# Monitor loop
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Live Monitoring (refreshes every 10 seconds)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

while true; do
    check_health
    show_activity
    sleep 10
done
