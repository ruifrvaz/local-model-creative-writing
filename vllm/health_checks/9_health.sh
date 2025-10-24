#!/usr/bin/env bash
set -euo pipefail

################################################################################
# Step 9: Health Check - Validate vLLM Server API Endpoints
################################################################################
# Purpose: Verify that the vLLM server is running and responding correctly
#          to OpenAI-compatible API requests.
#
# What this tests:
#   1. /v1/models endpoint - Lists available models
#   2. /v1/chat/completions endpoint - Validates inference pipeline
#
# Usage: ./9_health.sh [PORT]
#   PORT - Optional server port (default: 8000)
#
# Note: Automatically detects the loaded model from the server
#
# Success criteria:
#   - Server responds to HTTP requests
#   - Model is loaded and available
#   - Chat completion generates coherent response
#   - All JSON responses are well-formed
################################################################################

PORT="${1:-8000}"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[HEALTH] vLLM Server Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Server: http://localhost:$PORT"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Test 1: Check if server is responding
echo "[TEST] Test 1: Checking server availability..."
if ! curl -s --max-time 5 http://localhost:$PORT/health > /dev/null 2>&1; then
    echo "[ERROR] ERROR: Server is not responding on port $PORT"
    echo "   Try: ps aux | grep vllm"
    exit 1
fi
echo "[OK] Server is responding"
echo ""

# Test 2: List loaded models via the OpenAI-compatible endpoint
echo "[TEST] Test 2: Listing available models (/v1/models)..."
MODELS_RESPONSE=$(curl -s http://localhost:$PORT/v1/models)
echo "$MODELS_RESPONSE" | jq .

# Auto-detect the loaded model
MODEL=$(echo "$MODELS_RESPONSE" | jq -r '.data[0].id' 2>/dev/null)
if [ -z "$MODEL" ] || [ "$MODEL" = "null" ]; then
    echo "[ERROR] Could not detect model from server"
    exit 1
fi

echo "[OK] Detected model: $MODEL"
echo ""

# Test 3: Simple chat to validate inference path end-to-end
echo "[TEST] Test 3: Testing chat completion inference (/v1/chat/completions)..."
echo "   Using model: $MODEL"
echo "   Prompt: 'Say hello in 6 words'"
echo ""

CHAT_RESPONSE=$(curl -s http://localhost:$PORT/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "{
    \"model\":\"$MODEL\",
    \"messages\":[{\"role\":\"user\",\"content\":\"Say hello in 6 words\"}],
    \"temperature\":0.2,
    \"max_tokens\":50
  }")

echo "$CHAT_RESPONSE" | jq .

# Extract and display key metrics
RESPONSE_TEXT=$(echo "$CHAT_RESPONSE" | jq -r '.choices[0].message.content')
PROMPT_TOKENS=$(echo "$CHAT_RESPONSE" | jq -r '.usage.prompt_tokens')
COMPLETION_TOKENS=$(echo "$CHAT_RESPONSE" | jq -r '.usage.completion_tokens')
TOTAL_TOKENS=$(echo "$CHAT_RESPONSE" | jq -r '.usage.total_tokens')
FINISH_REASON=$(echo "$CHAT_RESPONSE" | jq -r '.choices[0].finish_reason')

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[METRICS] Response Metrics:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[MSG] Response: $RESPONSE_TEXT"
echo "[STATS] Tokens: $PROMPT_TOKENS prompt + $COMPLETION_TOKENS completion = $TOTAL_TOKENS total"
echo "[END] Finish reason: $FINISH_REASON"

if [ "$FINISH_REASON" = "stop" ]; then
    echo "[OK] Response completed naturally"
else
    echo "[WARN]  Response finished with reason: $FINISH_REASON"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[OK] All health checks passed!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"