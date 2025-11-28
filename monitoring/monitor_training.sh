#!/usr/bin/env bash
# Monitor QLoRA training progress in real-time
# Shows: GPU usage, training logs, checkpoint status

set -euo pipefail

################################################################################
# Training Monitor
################################################################################
# Purpose: Real-time monitoring of fine-tuning progress
#
# What it displays:
#   - GPU utilization and VRAM usage
#   - System RAM usage
#   - Latest training log entries (loss, epoch progress)
#   - Checkpoint directory status
#   - Process status
#
# Usage: ./monitor_training.sh [log_file]
#   If no log file specified, finds most recent training_*.log
################################################################################

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Find log file
if [ -n "${1:-}" ]; then
    LOG_FILE="$1"
else
    LOG_FILE=$(ls -t fine-tuning/logs/training_*.log 2>/dev/null | head -1)
fi

if [ -z "$LOG_FILE" ] || [ ! -f "$LOG_FILE" ]; then
    echo -e "${RED}[ERROR] No training log file found${NC}"
    echo "Usage: $0 [log_file_path]"
    exit 1
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Training Monitor${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "Log file: ${GREEN}$LOG_FILE${NC}"
echo -e "Press ${YELLOW}Ctrl+C${NC} to exit"
echo ""

# Monitoring loop
while true; do
    clear
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}GPU Status${NC} ($(date '+%Y-%m-%d %H:%M:%S'))"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # GPU metrics
    if command -v nvidia-smi &> /dev/null; then
        nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw \
            --format=csv,noheader,nounits | \
            awk -F', ' '{printf "GPU Util: %3s%%  |  VRAM: %5s/%5s MB  |  Temp: %3s°C  |  Power: %6s W\n", $1, $2, $3, $4, $5}'
    else
        echo -e "${RED}nvidia-smi not found${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}System Memory${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # System RAM
    free -h | grep "Mem:" | awk '{printf "RAM: %s / %s used  |  Available: %s\n", $3, $2, $7}'
    
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Training Process${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Check if training process is running
    if pgrep -f "axolotl.cli.train" > /dev/null; then
        PID=$(pgrep -f "axolotl.cli.train" | head -1)
        ELAPSED=$(ps -p "$PID" -o etime= 2>/dev/null | xargs)
        echo -e "Status: ${GREEN}RUNNING${NC}  |  PID: $PID  |  Elapsed: $ELAPSED"
    else
        echo -e "Status: ${RED}NOT RUNNING${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Latest Training Logs${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Extract relevant training information
    if [ -f "$LOG_FILE" ]; then
        # Show last 15 lines, filter for training progress
        tail -n 30 "$LOG_FILE" | grep -E "(epoch|loss|step|Loading|Training|Saving|ERROR|WARNING)" | tail -n 15 || echo "Waiting for training output..."
    else
        echo -e "${RED}Log file not found: $LOG_FILE${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Checkpoints${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # List checkpoints
    CHECKPOINT_DIR="fine-tuning/checkpoints/qlora-style-pipeline-test"
    if [ -d "$CHECKPOINT_DIR" ]; then
        echo "Directory: $CHECKPOINT_DIR"
        # Count checkpoint folders
        CHECKPOINT_COUNT=$(find "$CHECKPOINT_DIR" -maxdepth 1 -type d -name "checkpoint-*" 2>/dev/null | wc -l)
        if [ "$CHECKPOINT_COUNT" -gt 0 ]; then
            echo -e "${GREEN}Checkpoints saved: $CHECKPOINT_COUNT${NC}"
            # Show latest checkpoint with size
            LATEST=$(ls -td "$CHECKPOINT_DIR"/checkpoint-* 2>/dev/null | head -1)
            if [ -n "$LATEST" ]; then
                SIZE=$(du -sh "$LATEST" 2>/dev/null | cut -f1)
                echo "Latest: $(basename "$LATEST") ($SIZE)"
            fi
        else
            echo -e "${YELLOW}No checkpoints yet${NC}"
        fi
    else
        echo -e "${YELLOW}Checkpoint directory not created yet${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "Refreshing in 5 seconds... (Ctrl+C to exit)"
    
    sleep 5
done
