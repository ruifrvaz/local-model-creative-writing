#!/usr/bin/env bash
set -euo pipefail
# Usage: ./serve_vllm.sh [MODEL] [PORT] [MAX_SEQS] [CONTEXT_LENGTH] [GPU_MEMORY_UTIL]
# 
# Models optimized for SCIENCE FICTION WRITING & Creative Content:
#   
# Best for Science Fiction Writing (Long Context):
#   meta-llama/Llama-3.1-8B-Instruct (Default - proven stable, 128k context, ~16GB VRAM)
#   Qwen/Qwen2.5-7B-Instruct (Excellent creative writing, 128k context, ~14GB VRAM) 
#   Qwen/Qwen2.5-14B-Instruct (Superior quality, 128k context, ~28GB VRAM)
#   mistralai/Mistral-7B-Instruct-v0.3 (Creative, excellent dialogue, 32k context)
#   
# Creative Writing Specialists (AWQ Quantized for longer context):
#   casperhansen/qwen2.5-14b-instruct-awq (14B quality, 128k context, ~10GB VRAM)
#   casperhansen/llama-3.1-8b-instruct-awq (Great story consistency, 128k, ~6GB VRAM)
#   casperhansen/mixtral-8x7b-instruct-awq (MoE - varied writing styles, 32k, ~24GB VRAM)
#   
# Maximum Context for Long Fiction:
#   hugging-quants/Qwen2.5-32B-Instruct-AWQ (Superior prose, 128k context, ~20GB VRAM)
#   hugging-quants/Llama-3.1-70B-Instruct-AWQ (Best quality, 128k, requires CPU offloading)
#   
# Context Length Recommendations for Creative Writing:
#   Science Fiction Novel:     64k-128k tokens (full chapters)
#   Short Stories:             16k-32k tokens  (complete stories)
#   Character Development:     32k-64k tokens  (detailed backstories)
#   World Building:            64k-128k tokens (extensive lore)
#
# PERFORMANCE NOTE: Context window affects speed significantly!
#   32k window: Fastest (50+ tok/s @ 8k context)
#   64k window: Balanced (23 tok/s @ 8k, 8 tok/s @ 32k)
#   100k window: Slower (24 tok/s @ 8k, 6 tok/s @ 48k)
#   Recommendation: Use smallest window that fits your content
#
#  Model + Context	        VRAM Usage	    Story Length Capacity
#  Llama-3.1-8B @ 128k	    ~30GB	        Full novella chapters (SLOW)
#  Qwen2.5-7B @ 128k	        ~28GB	        Complete story arcs (SLOW)
#  Qwen2.5-14B-AWQ @ 128k	    ~22GB	        Professional-grade prose (SLOW)
#  Llama-3.1-8B @ 64k	        ~24GB	        Long short stories (FAST)
#  Any model @ 32k	        ~16-18GB	    Standard scenes/chapters (FASTEST)
#
MODEL="${1:-meta-llama/Llama-3.1-8B-Instruct}"
# Port for the OpenAI-compatible API.  
PORT="${2:-8000}"
# Scheduler concurrency; 9 is minimum for RTX 5090 with FlashInfer (max_seqs < 9 causes errors)
MAX_SEQS="${3:-9}"
# Context length for creative writing (default: 80k - balanced performance)
# Lower values = faster generation. Use 32k for speed, 64k for balance, 100k+ for very long contexts.
CONTEXT_LENGTH="${4:-80000}"
# GPU memory utilization (0.90-0.98, higher = more context possible)
GPU_MEMORY_UTIL="${5:-0.90}"

echo "[START] Starting vLLM server for SCIENCE FICTION WRITING:"
echo "   Model: $MODEL"
echo "   Port: $PORT"
echo "   GPU: RTX 5090 (32GB VRAM available)"
echo "   GPU Memory Utilization: ${GPU_MEMORY_UTIL} ($(echo "$GPU_MEMORY_UTIL * 32" | bc)GB allocated)"
echo "   FlashInfer: Enabled (proven stable config)"
echo "   Context: $(echo $CONTEXT_LENGTH | awk '{printf "%.0fk", $1/1024}') tokens (optimized for long creative writing)"
echo "   Max concurrent sequences: $MAX_SEQS"
echo "   First run will download model files..."
echo

# Use the venv and stop any previous vLLM instance
echo "[VENV] Activating virtual environment..."
if [ ! -f ~/.venvs/llm/bin/activate ]; then
    echo "[ERROR] ERROR: Virtual environment not found at ~/.venvs/llm/"
    echo "   Please run: ./4_create_venv.sh and ./5_install_torch.sh and ./6_install_llm_stack.sh first"
    exit 1
fi

source ~/.venvs/llm/bin/activate || {
    echo "[ERROR] ERROR: Failed to activate virtual environment"
    echo "   Check if ~/.venvs/llm/bin/activate exists and is readable"
    exit 1
}
echo "[OK] Virtual environment activated"
echo

pkill -f "vllm serve" || true

# Configure FlashInfer backend (proven stable configuration)
export VLLM_ATTENTION_BACKEND=FLASHINFER
export VLLM_USE_XFORMERS=0

# Start vLLM with creative writing optimized settings
exec vllm serve "$MODEL" \
  --dtype bfloat16 \
  --max-model-len "$CONTEXT_LENGTH" \
  --gpu-memory-utilization "$GPU_MEMORY_UTIL" \
  --max-num-seqs "$MAX_SEQS" \
  --tool-call-parser openai \
  --port "$PORT"