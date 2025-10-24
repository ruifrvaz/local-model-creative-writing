#!/usr/bin/env bash
set -euo pipefail

################################################################################
# Benchmark 1: Throughput Testing
################################################################################
# Purpose: Measure raw generation speed at different prompt lengths
# Metrics: Tokens/second, latency, time to first token
# Runtime: ~3 minutes
################################################################################

API_URL="http://localhost:8000"
RESULTS_DIR="$(dirname "$0")/results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="$RESULTS_DIR/throughput_${TIMESTAMP}.json"

mkdir -p "$RESULTS_DIR"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "VLLM Throughput Benchmark"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Timestamp: $(date)"
echo "API: $API_URL"
echo "Output: $OUTPUT_FILE"
echo ""

# Check server is running
echo "[TEST] Checking server availability..."
if ! curl -s -f "$API_URL/health" > /dev/null 2>&1; then
    echo "[ERROR] Server not responding at $API_URL"
    echo "Please start the server with: cd ../../ && ./serve_vllm.sh"
    exit 1
fi
echo "[OK] Server is running"
echo ""

# Get model name
MODEL=$(curl -s "$API_URL/v1/models" | jq -r '.data[0].id' 2>/dev/null || echo "unknown")
MAX_MODEL_LEN=$(curl -s "$API_URL/v1/models" | jq -r '.data[0].max_model_len' 2>/dev/null || echo "unknown")
echo "[INFO] Testing model: $MODEL"
echo "[INFO] Server max_model_len: $MAX_MODEL_LEN tokens"
echo ""

# Test configurations: (prompt_tokens, output_tokens, description)
declare -a TESTS=(
    "100:512:Short prompt, medium response"
    "1000:512:Medium prompt, medium response"
    "5000:512:Long prompt, medium response"
    "100:2048:Short prompt, long response"
    "1000:2048:Medium prompt, long response"
)

echo "[RUN] Running throughput tests..."
echo ""

# Initialize JSON output
cat > "$OUTPUT_FILE" << EOF
{
    "benchmark": "throughput",
    "timestamp": "$(date -Iseconds)",
    "model": "$MODEL",
    "max_model_len": $MAX_MODEL_LEN,
    "api_url": "$API_URL",
    "tests": []
}
EOF

PROMPT_SHORT="The starship entered orbit around the alien planet."
PROMPT_MEDIUM=$(python3 -c "print('The interstellar colony ship traversed the void between stars. ' * 50)")
PROMPT_LONG=$(python3 -c "print('In the year 2547, humanity had spread across the galaxy, establishing colonies on distant worlds. ' * 100)")

TEST_NUM=0
for TEST_CONFIG in "${TESTS[@]}"; do
    TEST_NUM=$((TEST_NUM + 1))
    
    PROMPT_SIZE=$(echo "$TEST_CONFIG" | cut -d: -f1)
    OUTPUT_SIZE=$(echo "$TEST_CONFIG" | cut -d: -f2)
    DESCRIPTION=$(echo "$TEST_CONFIG" | cut -d: -f3)
    
    # Select prompt based on size
    if [ "$PROMPT_SIZE" -eq 100 ]; then
        PROMPT="$PROMPT_SHORT"
    elif [ "$PROMPT_SIZE" -eq 1000 ]; then
        PROMPT="$PROMPT_MEDIUM"
    else
        PROMPT="$PROMPT_LONG"
    fi
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "[TEST $TEST_NUM/5] $DESCRIPTION"
    echo "Input: ~$PROMPT_SIZE tokens | Output: $OUTPUT_SIZE tokens"
    echo ""
    
    # Make request and time it
    START_TIME=$(date +%s.%N)
    
    RESPONSE=$(curl -s "$API_URL/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -d @- << REQUEST_EOF
{
    "model": "$MODEL",
    "messages": [{"role": "user", "content": "$PROMPT"}],
    "max_tokens": $OUTPUT_SIZE,
    "temperature": 0.7
}
REQUEST_EOF
    )
    
    END_TIME=$(date +%s.%N)
    TOTAL_TIME=$(echo "$END_TIME - $START_TIME" | bc)
    
    # Parse response
    PROMPT_TOKENS=$(echo "$RESPONSE" | jq -r '.usage.prompt_tokens // 0')
    COMPLETION_TOKENS=$(echo "$RESPONSE" | jq -r '.usage.completion_tokens // 0')
    TOTAL_TOKENS=$(echo "$RESPONSE" | jq -r '.usage.total_tokens // 0')
    
    # Calculate metrics
    if [ "$TOTAL_TIME" != "0" ]; then
        TOKENS_PER_SEC=$(echo "scale=2; $COMPLETION_TOKENS / $TOTAL_TIME" | bc)
        TIME_PER_TOKEN=$(echo "scale=3; $TOTAL_TIME / $COMPLETION_TOKENS * 1000" | bc)
    else
        TOKENS_PER_SEC="N/A"
        TIME_PER_TOKEN="N/A"
    fi
    
    echo "[RESULT] Completion Tokens: $COMPLETION_TOKENS"
    echo "[RESULT] Total Time: ${TOTAL_TIME}s"
    echo "[RESULT] Throughput: $TOKENS_PER_SEC tokens/sec"
    echo "[RESULT] Latency: ${TIME_PER_TOKEN}ms per token"
    echo ""
    
    # Append to JSON (using jq)
    jq --arg desc "$DESCRIPTION" \
       --argjson prompt_tokens "$PROMPT_TOKENS" \
       --argjson completion_tokens "$COMPLETION_TOKENS" \
       --argjson total_time "$TOTAL_TIME" \
       --arg tokens_per_sec "$TOKENS_PER_SEC" \
       --arg time_per_token "$TIME_PER_TOKEN" \
       '.tests += [{
           "description": $desc,
           "prompt_tokens": $prompt_tokens,
           "completion_tokens": $completion_tokens,
           "total_time": $total_time,
           "tokens_per_second": $tokens_per_sec,
           "ms_per_token": $time_per_token
       }]' "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp" && mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[COMPLETE] Throughput Benchmark Complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Calculate average throughput
AVG_THROUGHPUT=$(jq '[.tests[].tokens_per_second | tonumber] | add / length | round' "$OUTPUT_FILE")
echo ""
echo "[SUMMARY] Average Throughput: $AVG_THROUGHPUT tokens/sec"
echo "[INFO] Full results: $OUTPUT_FILE"
echo ""

# Add summary to JSON
jq --argjson avg "$AVG_THROUGHPUT" \
   '.summary = {
       "average_tokens_per_second": $avg,
       "test_count": (.tests | length)
   }' "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp" && mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"

echo "[TIP] View results: cat $OUTPUT_FILE | jq"
echo "[TIP] Compare with other models: jq -s '.' $RESULTS_DIR/throughput_*.json"
echo ""
