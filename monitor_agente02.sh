#!/bin/bash
# Monitor Agente02 training progress

echo "📊 MONITORANDO AGENTE02 - $(date)"
echo "================================"

# Check if process is running
if ps aux | grep -E "train_agente02" | grep -v grep > /dev/null 2>&1; then
    echo "✓ Processo rodando"
    
    # Get PID
    PID=$(ps aux | grep -E "train_agente02" | grep -v grep | awk '{print $2}' | head -1)
    
    # Get resource usage
    RES_INFO=$(ps aux | grep -E "train_agente02" | grep -v grep)
    CPU_PCT=$(echo "$RES_INFO" | awk '{print $3}')
    MEM_PCT=$(echo "$RES_INFO" | awk '{print $4}')
    MEM_MB=$(echo "$RES_INFO" | awk '{print $6}')
    
    echo "  PID: $PID"
    echo "  CPU: $CPU_PCT%"
    echo "  Memória: $MEM_MB KB (~${MEM_MB:0:4} MB)"
    
    # Check checkpoint files
    echo ""
    echo "📁 Checkpoints de Agente02:"
    if [ -d models/Agente02/checkpoints ]; then
        ls -lh models/Agente02/checkpoints/ 2>/dev/null | tail -5
    else
        echo "  (Ainda não criado)"
    fi
    
    # Estimate time remaining (rough)
    ELAPSED=$(ps -o etime= -p $PID | tr -d ' ')
    echo ""
    echo "⏱️  Tempo decorrido: $ELAPSED"
    echo "🔄 Monitorar com: tail -f /tmp/agente02.out"
else
    echo "✗ Processo NÃO está rodando"
    
    # Check if there are completed checkpoints
    echo ""
    echo "✓✓ Se treinamento foi concluído:"
    if [ -f "models/Agente02/checkpoints/latest.pt" ]; then
        ls -lh models/Agente02/checkpoints/
        echo "TREINAMENTO COMPLETO!"
    fi
fi

echo ""
echo "Próximas versões:"
echo "  - Agente03: Heavy (512 games, 1024 MCTS)"
echo "  - Agente04: Experimental (com arquitetura diferente)"
