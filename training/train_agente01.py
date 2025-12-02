#!/usr/bin/env python3
"""
Training script para Agente01 - Modelo inicial com reward shaping
"""
import sys
import os

# Ensure workspace path
sys.path.insert(0, '/home/mike/ProjetosPython/Xadrez_AI_Final')

def train_agente01():
    """Treina o Agente01 com configuração básica e reward shaping"""
    
    from training.run_heavy import run_heavy
    
    print("=" * 70)
    print("INICIANDO TREINAMENTO: Agente01")
    print("=" * 70)
    print()
    print("Configuração:")
    print("  - Nome do modelo: Agente01")
    print("  - Self-play games: 64 (básico)")
    print("  - MCTS simulations: 128 (básico)")
    print("  - Training iterations: 500 (básico)")
    print("  - Batch size: 128")
    print("  - Reward shaping: ✓ ATIVO")
    print("  - Combinação de rewards: 30% step + 70% final")
    print()
    
    # Configuração básica para Agente01
    result = run_heavy(
        num_selfplay=64,                # games básicos
        selfplay_sims=128,              # sims básico
        trainer_iters=500,              # iterações básico
        batch_size=128,
        model_kwargs={
            'channels': 128,            # modelo médio
            'blocks': 12,               # camadas médias
            'action_size': 20480
        },
        agent_dir='models/Agente01',
        preferred_device=None,          # auto-detect
        use_reward_shaping=True         # ✓ Reward shaping
    )
    
    print()
    print("=" * 70)
    if result == 0:
        print("✓✓✓ TREINAMENTO AGENTE01 CONCLUÍDO COM SUCESSO!")
    else:
        print("✗✗✗ TREINAMENTO AGENTE01 FALHOU")
    print("=" * 70)
    
    return result


if __name__ == '__main__':
    exit_code = train_agente01()
    sys.exit(exit_code)
