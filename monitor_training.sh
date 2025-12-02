#!/bin/bash
# Monitor Agente02 e Agente03 training progress

echo "📊 MONITORANDO TREINAMENTO - $(date)"
echo "========================================="
echo ""

# Function to monitor an agent
monitor_agent() {
    local agent=$1
    local pid_filter=$2
    
    if ps aux | grep -E "$pid_filter" | grep -v grep > /dev/null 2>&1; then
        PID=$(ps aux | grep -E "$pid_filter" | grep -v grep | awk '{print $2}' | head -1)
        RES_INFO=$(ps aux | grep -E "$pid_filter" | grep -v grep)
        CPU_PCT=$(echo "$RES_INFO" | awk '{print $3}')
        MEM_KB=$(echo "$RES_INFO" | awk '{print $6}')
        MEM_MB=$((MEM_KB / 1024))
        ELAPSED=$(ps -o etime= -p $PID 2>/dev/null | tr -d ' ')
        
        echo "🟢 $agent - RODANDO"
        echo "   PID: $PID | CPU: $CPU_PCT% | RAM: ${MEM_MB} MB | Tempo: $ELAPSED"
        
        # Check checkpoints
        if [ -d "models/$agent/checkpoints" ]; then
            LATEST_SIZE=$(ls -lh "models/$agent/checkpoints/latest.pt" 2>/dev/null | awk '{print $5}')
            REPLAY_SIZE=$(ls -lh "models/$agent/checkpoints/replay.pt" 2>/dev/null | awk '{print $5}')
            if [ ! -z "$LATEST_SIZE" ]; then
                echo "   ✓ latest.pt: $LATEST_SIZE"
            fi
            if [ ! -z "$REPLAY_SIZE" ]; then
                echo "   ✓ replay.pt: $REPLAY_SIZE"
            fi
        fi
    else
        echo "🔴 $agent - NÃO ESTÁ RODANDO"
        
        # Check if completed
        if [ -f "models/$agent/checkpoints/latest.pt" ]; then
            LATEST_SIZE=$(ls -lh "models/$agent/checkpoints/latest.pt" 2>/dev/null | awk '{print $5}')
            REPLAY_SIZE=$(ls -lh "models/$agent/checkpoints/replay.pt" 2>/dev/null | awk '{print $5}')
            echo "   ✓ COMPLETADO"
            echo "   ✓ latest.pt: $LATEST_SIZE"
            echo "   ✓ replay.pt: $REPLAY_SIZE"
        fi
    fi
    echo ""
}

# Monitor each agent
monitor_agent "Agente02" "train_agente02"
monitor_agent "Agente03" "train_agente03"

# Summary
echo "========================================="
echo "📈 Configurações:"
echo ""
echo "Agente01 (Básico - COMPLETO):"
echo "  • 64 games × 128 MCTS × 500 iters"
echo "  • Modelo: 128ch, 12 blocks"
echo ""
echo "Agente02 (Intermediário - TREINANDO):"
echo "  • 256 games × 512 MCTS × 2000 iters"
echo "  • Modelo: 160ch, 16 blocks"
echo "  • ETA: ~24-30 horas"
echo ""
echo "Agente03 (Pesado - TREINANDO):"
echo "  • 512 games × 1024 MCTS × 4000 iters"
echo "  • Modelo: 192ch, 20 blocks"
echo "  • ETA: ~40-50 horas"
echo ""
echo "Todas com reward shaping ativo! ✓"
