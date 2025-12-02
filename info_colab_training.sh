#!/bin/bash
# Script para gerenciar arquivos de treinamento no Colab

echo "📊 ARQUIVOS DE TREINAMENTO NO COLAB"
echo "===================================="
echo ""

# Arquivos disponíveis
echo "✅ PRONTO PARA USAR:"
echo ""
echo "1. colab_agente02_training.ipynb (13 KB)"
echo "   └─ Notebook COMPLETO com GPU"
echo "   └─ Instruções passo a passo"
echo "   └─ Download de resultados integrado"
echo "   └─ RECOMENDADO! ⭐⭐⭐"
echo ""
echo "2. colab_train_agente02.py (4.4 KB)"
echo "   └─ Script Python puro"
echo "   └─ Para uso em terminal do Colab"
echo "   └─ Sem interface Jupyter"
echo ""

# README
echo "📖 DOCUMENTAÇÃO:"
echo ""
echo "3. COLAB_TRAINING_README.md (8.1 KB)"
echo "   └─ Guia completo de uso"
echo "   └─ Troubleshooting"
echo "   └─ Configurações recomendadas"
echo ""

# Como usar
echo "🚀 COMO USAR:"
echo ""
echo "Opção 1 (Recomendada - Notebook):"
echo "  1. Abra Google Colab: https://colab.research.google.com/"
echo "  2. File > Open from GitHub"
echo "  3. Procure: devolopbomfim/Xadrez_AI_Final"
echo "  4. Abra: colab_agente02_training.ipynb"
echo "  5. Runtime > Change runtime type > GPU"
echo "  6. Execute células na ordem"
echo ""
echo "Opção 2 (Script):"
echo "  1. Copie colab_train_agente02.py para Colab"
echo "  2. Execute: python colab_train_agente02.py"
echo ""

# Configuração
echo "⚙️  CONFIGURAÇÃO AGENTE02:"
echo ""
echo "  • Games: 256 (intermediário)"
echo "  • MCTS: 512 (intermediário)"
echo "  • Training iters: 2000"
echo "  • Batch size: 256 (GPU)"
echo "  • Modelo: 160 channels, 16 blocks"
echo "  • Reward shaping: ✓ Ativo"
echo ""

# Tempo
echo "⏱️  TEMPO ESTIMADO (com GPU):"
echo ""
echo "  • T4 (free):  12-18 horas"
echo "  • P100:       6-8 horas"
echo "  • V100:       3-4 horas"
echo "  • A100:       1-2 horas"
echo ""

# Tamanho
echo "💾 TAMANHO DOS ARQUIVOS GERADOS:"
echo ""
echo "  • latest.pt:  ~24 MB (modelo)"
echo "  • replay.pt:  ~500 MB (dados)"
echo "  • Total:      ~524 MB"
echo ""

echo "===================================="
echo "✓ Tudo pronto para treinar! 🎯"
