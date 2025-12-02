#!/bin/bash
# Wait for Agente01 training to complete

PID=$(pgrep -f "train_agente01.py")

if [ -z "$PID" ]; then
    echo "❌ Training process not found"
    exit 1
fi

echo "⏳ Aguardando conclusão do treinamento do Agente01..."
echo "   PID: $PID"
echo ""

# Show initial status
ps -p $PID -o etime= 2>/dev/null || echo "Unknown elapsed time"

# Wait for process
wait $PID
EXIT_CODE=$?

echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║         TREINAMENTO AGENTE01 FINALIZADO           ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Treinamento concluído COM SUCESSO!"
else
    echo "❌ Treinamento finalizou com erro (code: $EXIT_CODE)"
fi

echo ""
echo "📁 Arquivos gerados:"
ls -lh models/Agente01/checkpoints/ 2>/dev/null | tail -10

echo ""
echo "💾 Tamanho total:"
du -sh models/Agente01/

echo ""
echo "✅ Você pode começar um novo treinamento (Agente02) agora!"
