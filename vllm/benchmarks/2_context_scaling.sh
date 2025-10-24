#!/usr/bin/env bash
set -euo pipefail

################################################################################
# Benchmark 2: Context Scaling Test
################################################################################
# Purpose: Measure performance degradation with increasing context lengths
# Metrics: Speed vs context size, memory usage patterns
# Runtime: ~5 minutes
# Key Hypothesis:
# "Does my 48k token story generate slower than a 1k token prompt?"
################################################################################

API_URL="http://localhost:8000"
RESULTS_DIR="$(dirname "$0")/results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="$RESULTS_DIR/context_scaling_${TIMESTAMP}.json"

mkdir -p "$RESULTS_DIR"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "VLLM Context Scaling Benchmark"
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

# Get model name and max context
MODEL=$(curl -s "$API_URL/v1/models" | jq -r '.data[0].id' 2>/dev/null || echo "unknown")
MAX_MODEL_LEN=$(curl -s "$API_URL/v1/models" | jq -r '.data[0].max_model_len' 2>/dev/null || echo "unknown")
echo "[INFO] Testing model: $MODEL"
echo "[INFO] Server max_model_len: $MAX_MODEL_LEN tokens"
echo ""

# Test context lengths (tokens)
declare -a CONTEXT_SIZES=(
    "1000"
    "4000"
    "8000"
    "16000"
    "32000"
    "48000"
    "60000"
)

echo "[RUN] Testing context scaling..."
echo "[INFO] This tests how generation speed changes with context length"
echo ""

# Initialize JSON output
cat > "$OUTPUT_FILE" << EOF
{
    "benchmark": "context_scaling",
    "timestamp": "$(date -Iseconds)",
    "model": "$MODEL",
    "max_model_len": $MAX_MODEL_LEN,
    "api_url": "$API_URL",
    "tests": []
}
EOF

# Base story chunk (repeated to create long contexts)
STORY_CHUNK="In the depths of space, the colony ship Artemis drifted through the void. Captain Sarah Chen reviewed the mission logs, her eyes scanning the holographic displays that floated before her. The ship's AI, named Athena, monitored thousands of hibernating colonists while maintaining course toward the distant star system designated as New Hope. "

TEST_NUM=0
for CONTEXT_SIZE in "${CONTEXT_SIZES[@]}"; do
    TEST_NUM=$((TEST_NUM + 1))
    
    # Calculate repetitions needed (approximately 10 tokens per chunk)
    REPETITIONS=$((CONTEXT_SIZE / 50))
    
    # Build context by repeating story (no character limit for proper testing)
    CONTEXT=$(python3 -c "chunk = '''$STORY_CHUNK'''; print(chunk * $REPETITIONS)")
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "[TEST $TEST_NUM/7] Context Size: ~${CONTEXT_SIZE} tokens"
    echo ""
    
    # Add GPU memory check before request
    if command -v nvidia-smi &> /dev/null; then
        MEMORY_BEFORE=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
    else
        MEMORY_BEFORE="N/A"
    fi
    
    # Make request and time it
    START_TIME=$(date +%s.%N)
    
    RESPONSE=$(curl -s "$API_URL/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -d @- << REQUEST_EOF
{
    "model": "$MODEL",
    "messages": [
        {"role": "user", "content": "$CONTEXT"},
        {"role": "user", "content": "Continue this story with 500 more words."}
    ],
    "max_tokens": 500,
    "temperature": 0.7
}
REQUEST_EOF
    )
    
    END_TIME=$(date +%s.%N)
    TOTAL_TIME=$(echo "$END_TIME - $START_TIME" | bc)
    
    # Check GPU memory after request
    if command -v nvidia-smi &> /dev/null; then
        MEMORY_AFTER=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
        MEMORY_DELTA=$((MEMORY_AFTER - MEMORY_BEFORE))
    else
        MEMORY_AFTER="N/A"
        MEMORY_DELTA="N/A"
    fi
    
    # Parse response
    PROMPT_TOKENS=$(echo "$RESPONSE" | jq -r '.usage.prompt_tokens // 0')
    COMPLETION_TOKENS=$(echo "$RESPONSE" | jq -r '.usage.completion_tokens // 0')
    
    # Calculate metrics
    if [ "$TOTAL_TIME" != "0" ] && [ "$COMPLETION_TOKENS" != "0" ]; then
        TOKENS_PER_SEC=$(echo "scale=2; $COMPLETION_TOKENS / $TOTAL_TIME" | bc)
        TIME_PER_TOKEN=$(echo "scale=3; $TOTAL_TIME / $COMPLETION_TOKENS * 1000" | bc)
    else
        TOKENS_PER_SEC="0"
        TIME_PER_TOKEN="0"
    fi
    
    echo "[RESULT] Actual Prompt Tokens: $PROMPT_TOKENS"
    echo "[RESULT] Completion Tokens: $COMPLETION_TOKENS"
    echo "[RESULT] Total Time: ${TOTAL_TIME}s"
    echo "[RESULT] Throughput: $TOKENS_PER_SEC tokens/sec"
    echo "[RESULT] VRAM Usage: ${MEMORY_AFTER}MB (Δ ${MEMORY_DELTA}MB)"
    echo ""
    
    # Append to JSON
    jq --argjson context_size "$CONTEXT_SIZE" \
       --argjson prompt_tokens "$PROMPT_TOKENS" \
       --argjson completion_tokens "$COMPLETION_TOKENS" \
       --argjson total_time "$TOTAL_TIME" \
       --arg tokens_per_sec "$TOKENS_PER_SEC" \
       --arg memory_mb "$MEMORY_AFTER" \
       '.tests += [{
           "target_context_size": $context_size,
           "actual_prompt_tokens": $prompt_tokens,
           "completion_tokens": $completion_tokens,
           "total_time": $total_time,
           "tokens_per_second": $tokens_per_sec,
           "vram_mb": $memory_mb
       }]' "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp" && mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"
    
    # Sleep to allow memory to stabilize
    sleep 2
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[COMPLETE] Context Scaling Benchmark Complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Calculate scaling factor (speed drop from smallest to largest)
FIRST_SPEED=$(jq -r '.tests[0].tokens_per_second' "$OUTPUT_FILE")
LAST_SPEED=$(jq -r '.tests[-1].tokens_per_second' "$OUTPUT_FILE")

if [ "$FIRST_SPEED" != "0" ] && [ "$FIRST_SPEED" != "null" ]; then
    SPEED_DEGRADATION=$(echo "scale=2; ($FIRST_SPEED - $LAST_SPEED) / $FIRST_SPEED * 100" | bc)
else
    SPEED_DEGRADATION="N/A"
fi

echo "[SUMMARY] Performance Degradation: ${SPEED_DEGRADATION}%"
echo "[SUMMARY] Speed at 1k context: $FIRST_SPEED tok/s"
echo "[SUMMARY] Speed at max context: $LAST_SPEED tok/s"
echo "[INFO] Full results: $OUTPUT_FILE"
echo ""

# Add summary to JSON
jq --arg degradation "$SPEED_DEGRADATION" \
   --arg first_speed "$FIRST_SPEED" \
   --arg last_speed "$LAST_SPEED" \
   '.summary = {
       "performance_degradation_percent": $degradation,
       "speed_at_min_context": $first_speed,
       "speed_at_max_context": $last_speed
   }' "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp" && mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"

echo "[TIP] View results: cat $OUTPUT_FILE | jq"
echo "[TIP] Plot degradation curve with your favorite tool"
echo ""
