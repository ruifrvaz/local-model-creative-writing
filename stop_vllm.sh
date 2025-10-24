#!/usr/bin/env bash
set -euo pipefail

################################################################################
# Stop vLLM Server - Graceful Shutdown with Resource Cleanup
################################################################################
# Purpose: Safely stop the vLLM server and free all associated resources
#
# What this does:
#   1. Identifies running vLLM processes
#   2. Attempts graceful shutdown (SIGTERM) with timeout
#   3. Force kills if graceful shutdown fails (SIGKILL)
#   4. Frees port 8000 if still bound
#   5. Reports cleanup status
#
# Usage: ./stop_vllm.sh [PORT]
#   PORT - Optional server port to free (default: 8000)
#
# Safety features:
#   - Non-destructive checks before killing
#   - Graceful shutdown with 10-second timeout
#   - Force kill only as fallback
#   - Won't fail if nothing is running
################################################################################

PORT="${1:-8000}"
GRACEFUL_TIMEOUT=10

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[STOP] vLLM Server Shutdown"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Port: $PORT"
echo ""

# Check for running vLLM processes
echo "[TEST] Step 1: Checking for running vLLM processes..."
VLLM_PIDS=$(pgrep -f "vllm serve" || true)
PYTHON_VLLM_PIDS=$(pgrep -f "python -m vllm" || true)
UVICORN_PIDS=$(pgrep -f "uvicorn.*vllm" || true)

ALL_PIDS=$(echo "$VLLM_PIDS $PYTHON_VLLM_PIDS $UVICORN_PIDS" | tr ' ' '\n' | sort -u | grep -v '^$' || true)

if [ -z "$ALL_PIDS" ]; then
    echo "[OK] No vLLM processes found running"
else
    echo "[WARN]  Found vLLM processes:"
    for PID in $ALL_PIDS; do
        PROCESS_INFO=$(ps -p $PID -o pid,ppid,etime,cmd --no-headers 2>/dev/null || echo "")
        if [ -n "$PROCESS_INFO" ]; then
            echo "   PID $PROCESS_INFO"
        fi
    done
    echo ""
    
    # Step 2: Attempt graceful shutdown
    echo "[TEST] Step 2: Attempting graceful shutdown (SIGTERM)..."
    for PID in $ALL_PIDS; do
        if ps -p $PID > /dev/null 2>&1; then
            echo "   Sending SIGTERM to PID $PID..."
            kill -TERM $PID 2>/dev/null || true
        fi
    done
    
    # Wait for graceful shutdown
    echo "   Waiting up to ${GRACEFUL_TIMEOUT}s for processes to terminate..."
    WAITED=0
    while [ $WAITED -lt $GRACEFUL_TIMEOUT ]; do
        REMAINING_PIDS=$(ps -p $(echo $ALL_PIDS | tr ' ' ',') -o pid --no-headers 2>/dev/null || true)
        if [ -z "$REMAINING_PIDS" ]; then
            echo "   [OK] All processes terminated gracefully"
            break
        fi
        sleep 1
        WAITED=$((WAITED + 1))
    done
    
    # Step 3: Force kill if still running
    REMAINING_PIDS=$(ps -p $(echo $ALL_PIDS | tr ' ' ',') -o pid --no-headers 2>/dev/null || true)
    if [ -n "$REMAINING_PIDS" ]; then
        echo ""
        echo "[TEST] Step 3: Force killing remaining processes (SIGKILL)..."
        for PID in $REMAINING_PIDS; do
            echo "   Force killing PID $PID..."
            kill -9 $PID 2>/dev/null || true
        done
        sleep 1
        echo "   [OK] Force kill completed"
    fi
fi

echo ""
echo "[TEST] Step 4: Freeing port $PORT..."
# Check if port is in use
PORT_PIDS=$(lsof -ti tcp:$PORT 2>/dev/null || true)
if [ -z "$PORT_PIDS" ]; then
    echo "[OK] Port $PORT is already free"
else
    echo "[WARN]  Port $PORT is still bound to PID(s): $PORT_PIDS"
    echo "   Killing processes on port $PORT..."
    fuser -k ${PORT}/tcp 2>/dev/null || true
    sleep 1
    
    # Verify port is free
    if lsof -ti tcp:$PORT > /dev/null 2>&1; then
        echo "   [WARN]  WARNING: Port $PORT may still be in use"
    else
        echo "   [OK] Port $PORT freed successfully"
    fi
fi

echo ""
echo "[TEST] Step 5: Final verification..."
FINAL_CHECK=$(pgrep -f "vllm serve" || true)
if [ -z "$FINAL_CHECK" ]; then
    echo "[OK] No vLLM processes running"
else
    echo "[WARN]  WARNING: Some vLLM processes may still be running: $FINAL_CHECK"
fi

# Check GPU memory
echo ""
echo "[TEST] Step 6: GPU memory status..."
if command -v nvidia-smi &> /dev/null; then
    GPU_USAGE=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1)
    echo "   GPU Memory Used: ${GPU_USAGE} MiB"
    if [ "$GPU_USAGE" -lt 1000 ]; then
        echo "   [OK] GPU memory mostly freed"
    else
        echo "   [INFO]  Some GPU memory still in use (may include system processes)"
    fi
else
    echo "   [INFO]  nvidia-smi not available, skipping GPU check"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[OK] vLLM server shutdown complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"