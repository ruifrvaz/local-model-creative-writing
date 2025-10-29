#!/bin/bash
# Train LoRA adapter for style transfer
# Uses QLoRA by default (memory efficient)

set -euo pipefail

# Change to fine-tuning directory
cd "$(dirname "$0")/.."

# Activate vLLM environment (has PyTorch, CUDA, transformers)
source ~/.venvs/llm/bin/activate

# Configuration
CONFIG="${1:-configs/qlora_style_transfer.yaml}"
RUN_NAME="$(basename "$CONFIG" .yaml)-$(date +%Y%m%d-%H%M%S)"

echo "[SETUP] Training configuration: $CONFIG"
echo "[SETUP] Run name: $RUN_NAME"

# Verify training data exists
if [ ! -f "data/processed/training.jsonl" ]; then
    echo "[ERROR] Training data not found: data/processed/training.jsonl"
    echo "[ERROR] Run scripts/1_prepare_data.py first"
    exit 1
fi

# Count training samples
SAMPLE_COUNT=$(wc -l < data/processed/training.jsonl)
echo "[INFO] Training samples: $SAMPLE_COUNT"

if [ "$SAMPLE_COUNT" -lt 50 ]; then
    echo "[WARN] Low sample count ($SAMPLE_COUNT). Recommend 100+ for good style capture"
fi

# Set memory optimization flags
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export TORCH_CUDNN_V8_API_ENABLED=1

# Optional: Disable Weights & Biases if not configured
export WANDB_DISABLED="${WANDB_DISABLED:-true}"

# Launch training
echo "[START] Beginning training..."
echo "[INFO] Expected time: ~2-4 hours for 500-1000 samples"

python -m axolotl.cli.train "$CONFIG" 2>&1 | tee "logs/training_${RUN_NAME}.log"

EXIT_CODE=${PIPESTATUS[0]}

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "[DONE] Training complete!"
    echo "[INFO] Checkpoints saved to: $(grep 'output_dir:' "$CONFIG" | awk '{print $2}')"
    echo ""
    echo "[NEXT] Merge adapter with base model:"
    echo "  python scripts/3_merge_adapter.py --checkpoint <checkpoint_path> --output merged_models/llama-3.1-8b-your-style"
else
    echo ""
    echo "[ERROR] Training failed with exit code $EXIT_CODE"
    echo "[ERROR] Check logs: logs/training_${RUN_NAME}.log"
    exit $EXIT_CODE
fi
