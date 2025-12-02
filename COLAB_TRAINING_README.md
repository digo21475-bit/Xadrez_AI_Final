# 🚀 Treinamento Agente02 no Google Colab com GPU

Este arquivo contém tudo que você precisa para treinar o modelo Agente02 no Google Colab usando GPU.

## 📋 Arquivos Disponíveis

### 1. **colab_agente02_training.ipynb** (RECOMENDADO)
- **Notebook completo** para executar no Colab
- Inclui verificação de GPU, instalação de dependências, treinamento e download de resultados
- **Apenas execute célula por célula** na ordem apresentada

### 2. **colab_train_agente02.py**
- Script Python puro (sem Jupyter)
- Pode ser executado diretamente em terminal do Colab
- Útil para automação ou scripts de batch

## 🎯 Como Usar no Colab

### Passo 1: Preparar o Notebook
1. Abra [Google Colab](https://colab.research.google.com/)
2. Clique em **Arquivo > Abrir notebook**
3. Selecione a aba **GitHub**
4. Procure por: `https://github.com/devolopbomfim/Xadrez_AI_Final`
5. Abra o arquivo `colab_agente02_training.ipynb`

### Passo 2: Configurar GPU
1. Vá em **Runtime > Change runtime type**
2. Selecione **GPU** (T4 ou melhor)
3. Clique em **Save**

### Passo 3: Executar Treinamento
Execute as células **na ordem**:

1. ✅ **Verificar GPU** - Confirma que GPU está disponível
2. ✅ **Instalar Dependências** - Instala PyTorch e ferramentas necessárias
3. ✅ **Clonar Repositório** - Baixa o código do projeto
4. ✅ **Configurar Paths** - Prepara diretórios e imports
5. ✅ **Configurar Variáveis** - Define parâmetros de treinamento
6. ✅ **EXECUTAR TREINAMENTO** - Inicia o treino (célula principal)
7. ✅ **Verificar Resultados** - Mostra arquivos gerados
8. ✅ **Download** - Faz download dos modelos
9. ✅ **Limpeza** - Libera memória

## ⚙️ Configuração do Agente02

```
Intermediário (balanceado entre velocidade e qualidade):
├─ Self-Play
│  ├─ Games: 256 (4x Agente01)
│  └─ MCTS Simulations: 512 (4x Agente01)
├─ Treinamento
│  ├─ Iterations: 2000
│  └─ Batch size: 256
├─ Modelo
│  ├─ Channels: 160
│  └─ Blocks: 16
└─ Rewards
   └─ Shaping: ✓ Ativo (30% step + 70% final)
```

## ⏱️ Tempo de Execução

| GPU | Tempo Estimado |
|-----|-----------------|
| T4 (free) | 12-18 horas |
| P100 | 6-8 horas |
| V100 | 3-4 horas |
| A100 | 1-2 horas |

## 💾 Arquivos Gerados

```
models/Agente02/checkpoints/
├─ latest.pt (24 MB)  ← Modelo treinado
└─ replay.pt (500-600 MB)  ← Buffer de replay
```

## 📥 Download dos Resultados

Após o treinamento:

1. A célula **"Download dos Modelos"** mostrará código para fazer download
2. Execute:
   ```python
   from google.colab import files
   files.download('models/Agente02/checkpoints/latest.pt')
   files.download('models/Agente02/checkpoints/replay.pt')
   ```

## 🔧 Troubleshooting

### ❌ GPU não detectada
- ✅ Vá em **Runtime > Change runtime type**
- ✅ Selecione **GPU** e clique **Save**
- ✅ Re-execute a primeira célula

### ❌ Falta de memória
- ✅ Reduza `batch_size` de 256 para 128
- ✅ Reduza `selfplay_sims` de 512 para 256
- ✅ Reduza `num_selfplay` de 256 para 128

### ❌ Timeout / Desconexão
- ℹ️ Colab pode desconectar após 30 min de inatividade
- ✅ Deixe a aba aberta / use [colab-utils](https://github.com/remzi07/colab-keep-alive)
- ✅ Checkpoints são salvos automaticamente

### ❌ ImportError ao clonar repo
- ✅ Execute a célula de clonagem novamente
- ✅ Verifique a conexão de internet
- ✅ Tente clonar manualmente em terminal do Colab

## 📊 Comparação de Versões

| Agente | Status | Jogos | MCTS | Iters | Modelo | Tempo GPU |
|--------|--------|-------|------|-------|--------|-----------|
| **01** | ✅ Completo | 64 | 128 | 500 | 128ch, 12bl | ~4h (CPU) |
| **02** | 🟡 Colab | 256 | 512 | 2000 | 160ch, 16bl | ~12-18h |
| **03** | 🔄 Local | 512 | 1024 | 4000 | 192ch, 20bl | ~40-50h |

## 🎓 Recursos Adicionais

- **PyTorch Documentation**: https://pytorch.org/docs/
- **Google Colab Guide**: https://colab.research.google.com/notebooks/intro.ipynb
- **Projeto Xadrez AI**: https://github.com/devolopbomfim/Xadrez_AI_Final
- **Reward Shaping**: Implementação com material, posição e segurança de rei

## 📞 Suporte

Se encontrar problemas:
1. Verifique a célula de erro
2. Consulte a seção **Troubleshooting**
3. Tente executar células novamente (podem ter sido timeout)
4. Abra uma issue no GitHub do projeto

## ✅ Checklist Antes de Começar

- [ ] Acessou Google Colab
- [ ] Selecionou GPU em Runtime
- [ ] Tem conta Google Drive (para salvar resultados)
- [ ] Verificou conexão de internet
- [ ] Tem 1-2 GB de espaço em Drive para checkpoints

## 🎉 Sucesso!

Após o treinamento, você terá:
- ✅ Modelo Agente02 treinado
- ✅ Buffer de replay com 256 games
- ✅ Checkpoints para continuar treinamento
- ✅ Arquivos prontos para download

Bom treinamento! 🚀
