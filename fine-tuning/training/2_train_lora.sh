#!/bin/bash
# Train LoRA adapter for style transfer
# Uses QLoRA by default (memory efficient)

set -euo pipefail

# Change to fine-tuning directory
cd "$(dirname "$0")/.."

# Activate finetune environment (has PyTorch 2.8.0, Axolotl, training stack)
source ~/.venvs/finetune/bin/activate

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
    echo "[WARN] Low sample count ($SAMPLE_COUNT). Recommend 50-100+ for production"
    echo "[INFO] Running as pipeline test - expect limited style transfer"
fi

# Set memory optimization flags
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export TORCH_CUDNN_V8_API_ENABLED=1

# Optional: Disable Weights & Biases if not configured
export WANDB_DISABLED="${WANDB_DISABLED:-true}"

# Suppress harmless PEFT warnings about saving embedding layers
# (This is expected behavior when lora_modules_to_save includes embed_tokens/lm_head)
export PYTHONWARNINGS="ignore::UserWarning:peft.utils.save_and_load"

# Create logs directory if it doesn't exist
mkdir -p logs

# Launch training
echo "[START] Beginning training..."
echo "[INFO] Expected time: ~30-60 minutes for 14 samples (pipeline test)"
echo "[INFO] This is a PROOF-OF-CONCEPT run with minimal data"
echo ""
echo "[NOTE] Training output will be shown live AND logged to: logs/training_${RUN_NAME}.log"
echo ""

# Run with live output AND logging (tee shows live + saves to file)
python -m axolotl.cli.train "$CONFIG" 2>&1 | tee "logs/training_${RUN_NAME}.log"

EXIT_CODE=${PIPESTATUS[0]}

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "[DONE] Training complete!"
    echo "[INFO] Checkpoints saved to: checkpoints/$(basename "$CONFIG" .yaml)/"
    echo "[INFO] Log file: logs/training_${RUN_NAME}.log"
    echo ""
    echo "[NEXT] Merge adapter with base model:"
    echo "  ./training/3_merge_adapters.sh"
else
    echo ""
    echo "[ERROR] Training failed with exit code $EXIT_CODE"
    echo "[ERROR] Check logs: logs/training_${RUN_NAME}.log"
    exit $EXIT_CODE
fi
