#!/usr/bin/env bash
set -euo pipefail

################################################################################
# Benchmark 9: Model Comparison Suite
################################################################################
# Purpose: Compare multiple models side-by-side for science fiction writing
# Metrics: All benchmarks across different models
# Runtime: ~30 minutes per model
################################################################################

RESULTS_DIR="$(dirname "$0")/results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
COMPARISON_FILE="$RESULTS_DIR/model_comparison_${TIMESTAMP}.md"

mkdir -p "$RESULTS_DIR"

# Models to compare (optimized for science fiction writing)
declare -a MODELS=(
    "meta-llama/Llama-3.1-8B-Instruct"
    "casperhansen/llama-3.1-8b-instruct-awq"
    "Qwen/Qwen2.5-7B-Instruct"
)

# Context lengths to test for each model
declare -A CONTEXT_LENGTHS=(
    ["meta-llama/Llama-3.1-8B-Instruct"]="64000"
    ["casperhansen/llama-3.1-8b-instruct-awq"]="128000"
    ["Qwen/Qwen2.5-7B-Instruct"]="64000"
)

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "VLLM Model Comparison Benchmark"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Timestamp: $(date)"
echo "Models to compare: ${#MODELS[@]}"
echo "Output: $COMPARISON_FILE"
echo ""

for MODEL in "${MODELS[@]}"; do
    echo "  - $MODEL"
done
echo ""

# Initialize comparison report
cat > "$COMPARISON_FILE" << 'EOF'
# VLLM Model Comparison Report

**Generated:** $(date)
**Purpose:** Compare models for science fiction writing performance

---

## Executive Summary

| Model | Overall Score | Speed | Quality | Coherence | Memory |
|-------|---------------|-------|---------|-----------|--------|
EOF

# Function to run benchmarks for a model
run_model_benchmarks() {
    local MODEL="$1"
    local CONTEXT_LENGTH="${CONTEXT_LENGTHS[$MODEL]}"
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Testing Model: $MODEL"
    echo "Context Length: $CONTEXT_LENGTH tokens"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Stop any running server
    echo "[SETUP] Stopping existing server..."
    ../stop_vllm.sh || true
    sleep 3
    
    # Start server with this model
    echo "[SETUP] Starting server with $MODEL..."
    ../serve_vllm.sh "$MODEL" 8000 9 "$CONTEXT_LENGTH" > /tmp/vllm_benchmark.log 2>&1 &
    SERVER_PID=$!
    
    # Wait for server to be ready
    echo "[SETUP] Waiting for server to initialize..."
    MAX_WAIT=300  # 5 minutes
    WAITED=0
    while [ $WAITED -lt $MAX_WAIT ]; do
        if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
            echo "[OK] Server is ready"
            break
        fi
        sleep 5
        WAITED=$((WAITED + 5))
        echo -n "."
    done
    echo ""
    
    if [ $WAITED -ge $MAX_WAIT ]; then
        echo "[ERROR] Server failed to start within $MAX_WAIT seconds"
        kill $SERVER_PID 2>/dev/null || true
        return 1
    fi
    
    sleep 5  # Extra stabilization time
    
    # Run benchmarks
    echo ""
    echo "[RUN] Running throughput benchmark..."
    ./1_throughput.sh
    THROUGHPUT_FILE=$(ls -t "$RESULTS_DIR"/throughput_*.json 2>/dev/null | head -1)
    
    echo ""
    echo "[RUN] Running creative quality benchmark..."
    python3 ./3_creative_quality.py
    QUALITY_FILE=$(ls -t "$RESULTS_DIR"/creative_quality_*.json 2>/dev/null | head -1)
    
    echo ""
    echo "[RUN] Running long context coherence benchmark..."
    python3 ./4_long_context_coherence.py
    COHERENCE_FILE=$(ls -t "$RESULTS_DIR"/long_context_coherence_*.json 2>/dev/null | head -1)
    
    # Extract key metrics
    if [ -f "$THROUGHPUT_FILE" ]; then
        AVG_SPEED=$(jq -r '.summary.average_tokens_per_second // 0' "$THROUGHPUT_FILE")
    else
        AVG_SPEED="N/A"
    fi
    
    if [ -f "$QUALITY_FILE" ]; then
        QUALITY_SCORE=$(jq -r '.summary.average_overall_score // 0' "$QUALITY_FILE")
    else
        QUALITY_SCORE="N/A"
    fi
    
    if [ -f "$COHERENCE_FILE" ]; then
        COHERENCE_SCORE=$(jq -r '.summary.overall_coherence_score // 0' "$COHERENCE_FILE")
    else
        COHERENCE_SCORE="N/A"
    fi
    
    # Get memory usage
    if command -v nvidia-smi &> /dev/null; then
        MEMORY_USAGE=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
    else
        MEMORY_USAGE="N/A"
    fi
    
    # Calculate overall score (weighted average)
    if [ "$AVG_SPEED" != "N/A" ] && [ "$QUALITY_SCORE" != "N/A" ] && [ "$COHERENCE_SCORE" != "N/A" ]; then
        OVERALL=$(echo "scale=1; ($QUALITY_SCORE * 0.4) + ($COHERENCE_SCORE * 0.4) + ($AVG_SPEED / 40 * 20)" | bc)
    else
        OVERALL="N/A"
    fi
    
    echo ""
    echo "[SUMMARY] Model: $MODEL"
    echo "  Overall Score: $OVERALL/100"
    echo "  Speed: $AVG_SPEED tok/s"
    echo "  Quality: $QUALITY_SCORE/100"
    echo "  Coherence: $COHERENCE_SCORE/100"
    echo "  Memory: ${MEMORY_USAGE}MB"
    echo ""
    
    # Add to comparison report
    echo "| $MODEL | $OVERALL | $AVG_SPEED | $QUALITY_SCORE | $COHERENCE_SCORE | ${MEMORY_USAGE}MB |" >> "$COMPARISON_FILE"
    
    # Stop server
    echo "[CLEANUP] Stopping server..."
    ../stop_vllm.sh || kill $SERVER_PID 2>/dev/null || true
    sleep 5
    
    # Store results for detailed section
    cat >> "$COMPARISON_FILE" << DETAIL_EOF

---

## Detailed Results: $MODEL

### Configuration
- **Context Length:** $CONTEXT_LENGTH tokens
- **VRAM Usage:** ${MEMORY_USAGE}MB

### Performance Metrics
- **Throughput:** $AVG_SPEED tokens/second
- **Creative Quality:** $QUALITY_SCORE/100
- **Long Context Coherence:** $COHERENCE_SCORE/100
- **Overall Score:** $OVERALL/100

### Score Breakdown
EOF
    
    if [ -f "$QUALITY_FILE" ]; then
        cat >> "$COMPARISON_FILE" << QUALITY_EOF
#### Creative Quality Scores
- Vocabulary: $(jq -r '.summary.average_vocabulary_score' "$QUALITY_FILE")/100
- Structure: $(jq -r '.summary.average_structure_score' "$QUALITY_FILE")/100
- Creativity: $(jq -r '.summary.average_creativity_score' "$QUALITY_FILE")/100

QUALITY_EOF
    fi
    
    if [ -f "$COHERENCE_FILE" ]; then
        cat >> "$COMPARISON_FILE" << COHERENCE_EOF
#### Coherence Metrics
- Elena Consistency: $(jq -r '.summary.character_coherence.elena_consistency * 100' "$COHERENCE_FILE")%
- Marcus Consistency: $(jq -r '.summary.character_coherence.marcus_consistency * 100' "$COHERENCE_FILE")%
- Story Length: $(jq -r '.summary.total_words_generated' "$COHERENCE_FILE") words

COHERENCE_EOF
    fi
}

# Run benchmarks for each model
for MODEL in "${MODELS[@]}"; do
    run_model_benchmarks "$MODEL"
    echo ""
    echo "Completed: $MODEL"
    echo ""
done

# Add recommendations section
cat >> "$COMPARISON_FILE" << 'EOF'

---

## Recommendations

### For Science Fiction Novel Writing
**Best Overall:** Model with highest coherence score (most important for long-form fiction)

### For Speed-Critical Applications
**Best Performance:** Model with highest tokens/second

### For Memory-Constrained Systems
**Most Efficient:** AWQ models (lower VRAM, longer context possible)

### For Maximum Quality
**Best Writing:** Model with highest creative quality score

---

## Testing Methodology

1. **Throughput Test:** 5 different prompt/response length combinations
2. **Creative Quality:** 5 writing scenarios (character, world-building, dialogue, etc.)
3. **Long Context Coherence:** Multi-stage story development (3000+ tokens)

**Scoring:**
- Overall Score = (Quality × 0.4) + (Coherence × 0.4) + (Speed/40 × 20)
- Emphasizes writing quality and continuity over raw speed

---

Generated with VLLM benchmarking suite
EOF

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[COMPLETE] Model Comparison Complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "[INFO] Comparison report: $COMPARISON_FILE"
echo ""
echo "[TIP] View report: cat $COMPARISON_FILE"
echo "[TIP] Choose the model with the best overall score for your use case"
echo ""
