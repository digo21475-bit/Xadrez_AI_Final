#!/usr/bin/env python3
"""
Training script para Agente03 - Modelo pesado com reward shaping
Versão agressiva: 512 games, 1024 MCTS simulations
"""
import sys
import os

# Ensure workspace path
sys.path.insert(0, '/home/mike/ProjetosPython/Xadrez_AI_Final')

def train_agente03():
    """Treina o Agente03 com configuração pesada e reward shaping"""
    
    from training.run_heavy import run_heavy
    
    print("=" * 70)
    print("INICIANDO TREINAMENTO: Agente03 (Pesado)")
    print("=" * 70)
    print()
    print("Configuração:")
    print("  - Nome do modelo: Agente03")
    print("  - Self-play games: 512 (pesado)")
    print("  - MCTS simulations: 1024 (pesado)")
    print("  - Training iterations: 4000 (pesado)")
    print("  - Batch size: 512")
    print("  - Reward shaping: ✓ ATIVO")
    print("  - Combinação de rewards: 30% step + 70% final")
    print()
    
    # Configuração pesada para Agente03
    result = run_heavy(
        num_selfplay=512,               # games pesado
        selfplay_sims=1024,             # sims pesado
        trainer_iters=4000,             # iterações pesado
        batch_size=512,
        model_kwargs={
            'channels': 192,            # modelo ainda maior
            'blocks': 20,               # camadas ainda maiores
            'action_size': 20480
        },
        agent_dir='models/Agente03',
        preferred_device=None,          # auto-detect
        use_reward_shaping=True         # ✓ Reward shaping
    )
    
    print()
    print("=" * 70)
    if result == 0:
        print("✓✓✓ TREINAMENTO AGENTE03 CONCLUÍDO COM SUCESSO!")
        print("     Modelo disponível em: models/Agente03/checkpoints/latest.pt")
    else:
        print("✗✗✗ TREINAMENTO AGENTE03 FALHOU")
    print("=" * 70)
    
    return result


if __name__ == '__main__':
    exit_code = train_agente03()
    sys.exit(exit_code)
