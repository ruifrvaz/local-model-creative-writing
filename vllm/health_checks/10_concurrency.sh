#!/usr/bin/env bash
set -euo pipefail

################################################################################
# Step 10: Concurrency Test - Validate Parallel Request Handling
################################################################################
# Purpose: Test the vLLM server's ability to handle multiple simultaneous
#          requests and measure throughput under concurrent load.
#
# What this tests:
#   - Server's request batching capabilities
#   - KV cache sharing efficiency
#   - Concurrent request scheduling
#   - Overall system stability under load
#
# Usage: ./10_concurrency.sh [PORT] [NUM_REQUESTS]
#   PORT - Optional server port (default: 8000)
#   NUM_REQUESTS - Number of parallel requests (default: 4)
#
# Technical context:
#   Our configuration supports max concurrency of 3.36x for 32k token contexts.
#   With 4 parallel requests, vLLM will batch and schedule them efficiently
#   using continuous batching and prefix caching.
#
# Success criteria:
#   - All requests complete successfully
#   - No timeout or connection errors
#   - Total time should be significantly less than sequential execution
#
# Model detection:
#   Automatically detects the loaded model from the server.
################################################################################

PORT="${1:-8000}"
NUM_REQUESTS="${2:-4}"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[ASYNC] vLLM Concurrency Test"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Server: http://localhost:$PORT"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Auto-detect the loaded model
echo "[INFO] Detecting loaded model from server..."
MODELS_RESPONSE=$(curl -s http://localhost:$PORT/v1/models)
MODEL=$(echo "$MODELS_RESPONSE" | jq -r '.data[0].id' 2>/dev/null)

if [ -z "$MODEL" ] || [ "$MODEL" = "null" ]; then
    echo "[ERROR] Could not detect model from server"
    echo "[ERROR] Server may not be running on port $PORT"
    exit 1
fi

echo "[OK] Detected model: $MODEL"
echo "Parallel requests: $NUM_REQUESTS"
echo ""

echo "[METRICS] Starting $NUM_REQUESTS parallel requests..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Track start time
START_TIME=$(date +%s.%N)

# Fire parallel requests using xargs for process parallelism
# Each request sends a simple "ping N" message and reports success
SUCCESS_COUNT=0
RESULTS=$(seq 1 $NUM_REQUESTS | xargs -I{} -P$NUM_REQUESTS bash -c '
  START=$(date +%s.%N)
  RESPONSE=$(curl -s --max-time 30 http://localhost:'"$PORT"'/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d "{
      \"model\":\"'"$MODEL"'\",
      \"messages\":[{\"role\":\"user\",\"content\":\"Respond with just: pong {}\"}],
      \"temperature\":0,
      \"max_tokens\":10
    }")
  
  END=$(date +%s.%N)
  DURATION=$(echo "$END - $START" | bc)
  
  if [ $? -eq 0 ] && echo "$RESPONSE" | jq -e ".choices[0].message.content" > /dev/null 2>&1; then
    CONTENT=$(echo "$RESPONSE" | jq -r ".choices[0].message.content")
    echo "[OK] Request {}: OK (${DURATION}s) - Response: $CONTENT"
    exit 0
  else
    echo "[ERROR] Request {}: FAILED (${DURATION}s)"
    exit 1
  fi
' || echo "[ERROR] Request failed")

# Count successes
SUCCESS_COUNT=$(echo "$RESULTS" | grep -c "[OK]" || echo "0")

# Track end time
END_TIME=$(date +%s.%N)
TOTAL_DURATION=$(echo "$END_TIME - $START_TIME" | bc)

echo "$RESULTS"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[METRICS] Concurrency Test Results:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[OK] Successful requests: $SUCCESS_COUNT / $NUM_REQUESTS"
echo "[TIME]  Total time: ${TOTAL_DURATION}s"

if [ "$SUCCESS_COUNT" -eq "$NUM_REQUESTS" ]; then
  AVG_TIME=$(echo "scale=3; $TOTAL_DURATION / $NUM_REQUESTS" | bc)
  echo "[STATS] Average time per request: ${AVG_TIME}s"
  echo "[START] Throughput: $(echo "scale=2; $NUM_REQUESTS / $TOTAL_DURATION" | bc) requests/second"
  echo ""
  echo "[OK] Concurrency test PASSED - Server handled all parallel requests successfully!"
else
  FAILED=$((NUM_REQUESTS - SUCCESS_COUNT))
  echo "[ERROR] Failed requests: $FAILED"
  echo ""
  echo "[ERROR] Concurrency test FAILED - Some requests did not complete successfully"
  exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"