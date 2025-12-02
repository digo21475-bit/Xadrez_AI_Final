#!/bin/bash
# Real-time status of Agente01 training

echo "═══════════════════════════════════════════════════════════"
echo "  AGENTE01 TRAINING STATUS"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check process
if pgrep -f "train_agente01.py" > /dev/null; then
    PID=$(pgrep -f "train_agente01.py")
    echo "✅ TRAINNING: PID $PID"
    
    # Elapsed time
    ETIME=$(ps -p $PID -o etime= 2>/dev/null || echo "?")
    echo "   Elapsed: $ETIME"
    
    # CPU and Memory
    ps -p $PID -o %cpu=,%mem= 2>/dev/null | read CPU MEM
    echo "   CPU/Mem: $(ps -p $PID -o %cpu=,%mem= 2>/dev/null)"
else
    echo "❌ NOT RUNNING"
fi

echo ""
echo "📁 DATA:"
echo "   Replay buffer: $(du -h models/Agente01/checkpoints/replay.pt 2>/dev/null | cut -f1)"
echo "   Total size: $(du -sh models/Agente01/ 2>/dev/null | cut -f1)"

echo ""
echo "📊 FILES:"
ls -1 models/Agente01/checkpoints/ 2>/dev/null | while read f; do
    echo "   - $f ($(du -h models/Agente01/checkpoints/$f 2>/dev/null | cut -f1))"
done

echo ""
echo "═══════════════════════════════════════════════════════════"
