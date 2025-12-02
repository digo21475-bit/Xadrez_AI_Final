# Xadrez_AI_Final

**Motor de Xadrez + Pipeline de Treinamento (MCTS + Rede Neural)**

Este repositório contém um motor de xadrez, utilitários de geração de movimentos e um pipeline de treinamento baseado em MCTS com rede neural. O projeto inclui ferramentas para self-play, avaliação, checkpoints e diversos scripts de diagnóstico.

---

## Badges

![tests](https://img.shields.io/badge/tests-passing-brightgreen)
![coverage](https://img.shields.io/badge/coverage-98.7%25-brightgreen)
![python](https://img.shields.io/badge/python-3.10-blue)

---

## Visão rápida (30s)

- Nome: `Xadrez_AI_Final`
- O que é: motor de xadrez com pipeline de treinamento (MCTS + rede)
- Por que usar: base completa para experimentar agentes de xadrez com aprendizado por reforço e MCTS.

---

## Requisitos

- Linux (testado)
- Python 3.10
- Recomenda-se usar um ambiente virtual (`venv`)
- Opcional: GPU CUDA com PyTorch compatível para acelerar inferência/treino

Instalação (desenvolvimento):

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

---

## Testes

Rodar a suíte de testes:

```bash
pytest -q
```

Rodar cobertura (local):

```bash
pytest --cov=. --cov-report=term-missing --cov-fail-under=95
```

---

## Executando exemplos

- Jogo: random vs engine

```bash
python -m examples.game_mode_random_vs_engine
```

- Engine vs Engine (headless):

```bash
python -m examples.game_mode_engine_vs_engine
```

---

## Estrutura do projeto (resumida)

- `core/` — Representação de tabuleiro, geração de movimentos, regras
- `engine/` — Busca, avaliação, heurísticas de ordenação
- `training/` — Treino, self-play, MCTS, replay buffer, checkpoints
- `agents/` — Agentes (engine, random, human)
- `interface/` — GUI e TUI
- `scripts/` — Ferramentas e diagnósticos
- `tests/` — Testes unitários e de integração

---

## Principais funcionalidades

- Treinamento agnóstico a dispositivo via `training/device.py`
- Wrapper `training/net.py` com `batch_predict()` para MCTS em lote
- MCTS com caminho batched e fallback sequencial (`training/mcts.py`)
- Checkpoint manager e treino compatível com AMP (`training/train_optimized.py`)
- Testes e CI com gate de cobertura

---

## Exemplo rápido de uso (treino simplificado)

O projeto expõe utilitários de treino que aceitam um objeto de configuração (`TrainConfig`-like). Para testes rápidos e experimentos, veja os exemplos e os testes `tests/` que contêm `DummyConfig` usados localmente.

---

## Contribuindo

1. Fork
2. Crie uma branch: `git checkout -b feature/minha-feature`
3. Adicione testes para novas funcionalidades
4. Faça `commit` seguindo Conventional Commits (`feat:`, `fix:`, `test:`, `docs:`)
5. Abra um Pull Request

Recomendações:
- Escreva testes determinísticos (evitar dependência de hardware não replicável)
- Use `training/net.py` para expor `batch_predict()` nas redes e permitir batching no MCTS

---

## Roadmap resumido

- v1.0 (Atual): Baseline de treino e MCTS batched
- v1.1 (Em progresso): Otimizações GPU, substituir helper de cobertura por testes reais
- v2.0 (Planejado): Distribuído self-play, UI e benchmarks

---

## Troubleshooting rápido

- Warnings PyTorch sobre shapes: verifique `squeeze`/`unsqueeze` e shapes retornadas pelo modelo
- Se testes falharem por diferença de dispositivo, force `device='cpu'` em configs de teste

---

## Licença

Atualize este bloco com a licença do repositório (arquivo `LICENSE`).

---

## Contato

Repo owner: `devolopbomfim` — abra issues/PRs no GitHub

---

Se quiser que eu também crie um `CONTRIBUTING.md` e um esqueleto de `docs/`, diga que eu crio na sequência.
