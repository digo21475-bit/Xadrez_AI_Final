#!/bin/bash
# Monitor Agente01 training progress
# Usage: ./monitor_agente01.sh

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║          AGENTE01 TRAINING MONITOR                                ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

while true; do
    echo "[$(date '+%H:%M:%S')] Status check..."
    
    # Check if training process is running
    if pgrep -f "train_agente01.py" > /dev/null; then
        echo "✓ Training process is RUNNING"
        
        # Check replay buffer size
        if [ -f "models/Agente01/checkpoints/replay.pt" ]; then
            size=$(du -h "models/Agente01/checkpoints/replay.pt" | cut -f1)
            echo "  Replay buffer size: $size"
        fi
        
        # Check for model checkpoints
        ckpt_count=$(ls -1 models/Agente01/checkpoints/*.pt 2>/dev/null | wc -l)
        echo "  Checkpoint files: $ckpt_count"
        
        # Last modified files
        echo "  Last 3 modified files:"
        ls -1t models/Agente01/checkpoints/ 2>/dev/null | head -3 | while read f; do
            echo "    - $f"
        done
    else
        echo "✗ Training process is NOT RUNNING"
        echo ""
        echo "Check status:"
        echo "  tail training_agente01.log"
        echo "  ls -lh models/Agente01/checkpoints/"
        break
    fi
    
    echo ""
    echo "Next check in 30 seconds... (Ctrl+C to exit)"
    sleep 30
done
