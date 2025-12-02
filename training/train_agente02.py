#!/usr/bin/env python3
"""
Training script para Agente02 - Modelo intermediário com reward shaping
Versão mais agressiva: 256 games, 512 MCTS simulations
"""
import sys
import os

# Ensure workspace path
sys.path.insert(0, '/home/mike/ProjetosPython/Xadrez_AI_Final')

def train_agente02():
    """Treina o Agente02 com configuração intermediária e reward shaping"""
    
    from training.run_heavy import run_heavy
    
    print("=" * 70)
    print("INICIANDO TREINAMENTO: Agente02 (Intermediário)")
    print("=" * 70)
    print()
    print("Configuração:")
    print("  - Nome do modelo: Agente02")
    print("  - Self-play games: 256 (intermediário)")
    print("  - MCTS simulations: 512 (intermediário)")
    print("  - Training iterations: 2000 (intermediário)")
    print("  - Batch size: 256")
    print("  - Reward shaping: ✓ ATIVO")
    print("  - Combinação de rewards: 30% step + 70% final")
    print()
    
    # Configuração intermediária para Agente02
    result = run_heavy(
        num_selfplay=256,               # games intermediário
        selfplay_sims=512,              # sims intermediário
        trainer_iters=2000,             # iterações intermediário
        batch_size=256,
        model_kwargs={
            'channels': 160,            # modelo maior
            'blocks': 16,               # camadas maiores
            'action_size': 20480
        },
        agent_dir='models/Agente02',
        preferred_device=None,          # auto-detect
        use_reward_shaping=True         # ✓ Reward shaping
    )
    
    print()
    print("=" * 70)
    if result == 0:
        print("✓✓✓ TREINAMENTO AGENTE02 CONCLUÍDO COM SUCESSO!")
        print("     Modelo disponível em: models/Agente02/checkpoints/latest.pt")
    else:
        print("✗✗✗ TREINAMENTO AGENTE02 FALHOU")
    print("=" * 70)
    
    return result


if __name__ == '__main__':
    exit_code = train_agente02()
    sys.exit(exit_code)
