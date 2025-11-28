#!/usr/bin/env bash
# Comprehensive vLLM Monitor - Performance, tokens, and session tracking for science fiction writing

PORT="${1:-8000}"
SESSION_FILE="/tmp/vllm_session_$(date +%Y%m%d_%H%M%S).log"

# Initialize session tracking variables
LAST_PROMPT_TOKENS=0
LAST_GENERATION_TOKENS=0
LAST_REQUESTS=0
SESSION_START_TIME=$(date +%s)

echo "=== vLLM Comprehensive Monitor for Creative Writing ==="
echo "Usage: ./monitor_vllm.sh [PORT]"
echo "Session log: $SESSION_FILE"
echo "Started: $(date)"
echo "Press Ctrl+C to stop"
echo ""

# Create session log header
echo "# vLLM Session Log - $(date)" > "$SESSION_FILE"
echo "# Time,Session_Seconds,Prompt_Tokens,Generation_Tokens,Total_Tokens,Requests,Words_Est,Model" >> "$SESSION_FILE"

while true; do
    TIME=$(date '+%H:%M:%S')
    SESSION_ELAPSED=$(($(date +%s) - SESSION_START_TIME))
    
    # GPU memory and usage
    GPU_INFO=$(nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits)
    VRAM=$(echo "$GPU_INFO" | awk -F',' '{print $1"/"$2}')
    GPU_UTIL=$(echo "$GPU_INFO" | awk -F',' '{print $3}')
    
    # Server status and model
    if STATUS=$(curl -s http://localhost:$PORT/health 2>/dev/null); then
        STATUS="ONLINE"
        MODEL_INFO=$(curl -s http://localhost:$PORT/v1/models 2>/dev/null | jq -r '.data[0].id' 2>/dev/null || echo "N/A")
        
        # Get Prometheus metrics for comprehensive tracking
        METRICS=$(curl -s http://localhost:$PORT/metrics 2>/dev/null)
        if [ -n "$METRICS" ]; then
            # Extract cumulative counters and convert to integers
            PROMPT_TOKENS=$(echo "$METRICS" | grep "vllm:prompt_tokens_total" | tail -1 | awk '{print int($2)}' 2>/dev/null || echo "0")
            GENERATION_TOKENS=$(echo "$METRICS" | grep "vllm:generation_tokens_total" | tail -1 | awk '{print int($2)}' 2>/dev/null || echo "0")
            REQUESTS=$(echo "$METRICS" | grep "vllm:request_success_total" | tail -1 | awk '{print int($2)}' 2>/dev/null || echo "0")
            
            # Calculate session activity (new tokens since last check)
            NEW_PROMPT=$((PROMPT_TOKENS - LAST_PROMPT_TOKENS))
            NEW_GENERATION=$((GENERATION_TOKENS - LAST_GENERATION_TOKENS))
            NEW_REQUESTS=$((REQUESTS - LAST_REQUESTS))
            
            if [ "$PROMPT_TOKENS" -gt 0 ] || [ "$GENERATION_TOKENS" -gt 0 ]; then
                TOTAL_TOKENS=$((PROMPT_TOKENS + GENERATION_TOKENS))
                WORDS=$((TOTAL_TOKENS * 3 / 4))
                
                # Enhanced display with session activity
                if [ "$NEW_PROMPT" -gt 0 ] || [ "$NEW_GENERATION" -gt 0 ]; then
                    printf "\r[$TIME] GPU: ${GPU_UTIL}%% | VRAM: ${VRAM}MB | $STATUS | Tokens: ${TOTAL_TOKENS} (~${WORDS}w) | +${NEW_PROMPT}p+${NEW_GENERATION}g | Reqs: ${REQUESTS} | ${MODEL_INFO:0:15}"
                    
                    # Log significant activity to session file
                    if [ "$NEW_REQUESTS" -gt 0 ]; then
                        echo "${TIME},${SESSION_ELAPSED},${PROMPT_TOKENS},${GENERATION_TOKENS},${TOTAL_TOKENS},${REQUESTS},${WORDS},${MODEL_INFO}" >> "$SESSION_FILE"
                    fi
                else
                    printf "\r[$TIME] GPU: ${GPU_UTIL}%% | VRAM: ${VRAM}MB | $STATUS | Tokens: ${TOTAL_TOKENS} (~${WORDS}w) | Idle | Reqs: ${REQUESTS} | ${MODEL_INFO:0:15}"
                fi
                
                # Update tracking variables
                LAST_PROMPT_TOKENS=$PROMPT_TOKENS
                LAST_GENERATION_TOKENS=$GENERATION_TOKENS
                LAST_REQUESTS=$REQUESTS
            else
                printf "\r[$TIME] GPU: ${GPU_UTIL}%% | VRAM: ${VRAM}MB | $STATUS | ${MODEL_INFO:0:30} | No activity yet"
            fi
        else
            printf "\r[$TIME] GPU: ${GPU_UTIL}%% | VRAM: ${VRAM}MB | $STATUS | ${MODEL_INFO:0:30} | Metrics N/A"
        fi
    else
        STATUS="OFFLINE"
        printf "\r[$TIME] GPU: ${GPU_UTIL}%% | VRAM: ${VRAM}MB | $STATUS | Server not responding"
    fi
    
    sleep 2
done