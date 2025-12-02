# Setup and Coverage Testing Guide

## Quick Start (Local Machine)

Execute os comandos abaixo no seu diretório do projeto para instalar dependências e rodar os testes com cobertura:

```bash
# 1) Criar virtualenv (opcional mas recomendado)
python3 -m venv venv
. venv/bin/activate  # ou venv\Scripts\activate no Windows

# 2) Instalar dependências
pip install --upgrade pip
pip install torch torchvision torchaudio numpy
pip install pytest pytest-cov

# 3) Rodar testes com cobertura
pytest -v \
  tests/test_training_device.py \
  tests/test_model_forward.py \
  tests/test_replay_buffer.py \
  tests/test_train_optimized.py \
  tests/test_mcts_and_arena.py \
  tests/test_trainer_and_train_optimized.py \
  --cov=training \
  --cov-report=term-missing \
  --cov-report=html

# 4) Ver relatório HTML
open htmlcov/index.html  # macOS
# ou xdg-open htmlcov/index.html  # Linux
# ou start htmlcov/index.html  # Windows
```

Alternativa: use o script bash
```bash
chmod +x run_coverage.sh
./run_coverage.sh
```

## No Google Colab

```python
# Célula 1 - Instalar dependências
!pip install --upgrade pip
!pip install torch torchvision torchaudio numpy pytest pytest-cov

# Célula 2 - Clonar/navegar para o repo
!git clone https://github.com/devolopbomfim/Xadrez_AI_Final.git || echo 'Repo já existe'
%cd Xadrez_AI_Final

# Célula 3 - Rodar testes
!pytest -v \
  tests/test_training_device.py \
  tests/test_model_forward.py \
  tests/test_replay_buffer.py \
  tests/test_train_optimized.py \
  tests/test_mcts_and_arena.py \
  tests/test_trainer_and_train_optimized.py \
  --cov=training \
  --cov-report=term-missing
```

## O que esperar

A saída conterá:

1. **Lista de testes executados** com PASSED/FAILED
2. **Relatório de cobertura por módulo**:
   - `training/device.py`
   - `training/model.py`
   - `training/replay_buffer.py`
   - `training/trainer.py`
   - `training/train_optimized.py`
   - `training/mcts.py`
   - `training/run_iteration.py`
   - etc.

3. **Percentual total de cobertura** (alvo: ≥95%)

## Depois de executar

Copie e cole aqui:
- A **última linha** do relatório (cobertura total)
- As linhas dos **módulos com <95% cobertura**
- Se houver **testes que falharam**, a saída de erro

Exemplo de saída esperada:
```
tests/test_training_device.py::test_get_device_cpu_monkeypatch PASSED
tests/test_model_forward.py::test_small_model_forward PASSED
...

Name                                Stmts   Miss  Cover   Missing
--------------------------------------------------------------------------
training/__init__.py                    0      0   100%
training/device.py                     10      0   100%
training/model.py                      45      2    95%   67-68
...
--------------------------------------------------------------------------
TOTAL                                 500     20    96%
```

Com isso, posso adicionar testes adicionais focados exatamente nas linhas faltantes.
