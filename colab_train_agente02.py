#!/usr/bin/env python3
"""
Training script para Agente02 no Google Colab com GPU
Versão otimizada para execução em Colab
"""
import sys
import os

# Ensure workspace path for Colab
COLAB_WORKSPACE = '/content/Xadrez_AI_Final'
if os.path.exists(COLAB_WORKSPACE):
    sys.path.insert(0, COLAB_WORKSPACE)
else:
    sys.path.insert(0, '/home/mike/ProjetosPython/Xadrez_AI_Final')


def setup_colab():
    """Setup inicial para executar no Colab"""
    try:
        import google.colab
        IN_COLAB = True
        print("✓ Executando no Google Colab!")
    except ImportError:
        IN_COLAB = False
        print("⚠ Não está no Colab, continuando localmente...")
    
    return IN_COLAB


def check_gpu():
    """Verifica disponibilidade de GPU"""
    import torch
    
    if torch.cuda.is_available():
        print(f"✓ GPU disponível: {torch.cuda.get_device_name(0)}")
        print(f"  Memória: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        return True
    else:
        print("⚠ GPU não disponível, usando CPU")
        return False


def train_agente02_colab():
    """Treina o Agente02 no Colab com GPU"""
    
    import torch
    from training.run_heavy import run_heavy
    
    print("=" * 80)
    print("AGENTE02 - TREINAMENTO NO GOOGLE COLAB COM GPU")
    print("=" * 80)
    print()
    
    # Setup Colab
    in_colab = setup_colab()
    has_gpu = check_gpu()
    
    print()
    print("Configuração do Treinamento:")
    print("  - Nome do modelo: Agente02")
    print("  - Self-play games: 256 (intermediário)")
    print("  - MCTS simulations: 512 (intermediário)")
    print("  - Training iterations: 2000 (intermediário)")
    print("  - Batch size: 256 (otimizado para GPU)")
    print("  - Dispositivo: GPU (CUDA)" if has_gpu else "  - Dispositivo: CPU")
    print("  - Reward shaping: ✓ ATIVO")
    print("  - Combinação de rewards: 30% step + 70% final")
    print()
    print("=" * 80)
    print("Iniciando treinamento...")
    print("=" * 80)
    print()
    
    # Configuração intermediária para Agente02 - otimizada para GPU
    result = run_heavy(
        num_selfplay=256,               # games intermediário
        selfplay_sims=512,              # sims intermediário
        trainer_iters=2000,             # iterações intermediário
        batch_size=256,                 # batch maior para GPU
        model_kwargs={
            'channels': 160,            # modelo maior
            'blocks': 16,               # camadas maiores
            'action_size': 20480
        },
        agent_dir='models/Agente02',
        preferred_device='cuda' if has_gpu else 'cpu',  # Usar GPU se disponível
        use_reward_shaping=True         # ✓ Reward shaping
    )
    
    print()
    print("=" * 80)
    if result == 0:
        print("✓✓✓ TREINAMENTO AGENTE02 CONCLUÍDO COM SUCESSO!")
        print()
        print("📊 Resultados:")
        print(f"   Modelo salvo em: models/Agente02/checkpoints/latest.pt")
        print(f"   Replay buffer em: models/Agente02/checkpoints/replay.pt")
        print()
        
        # Print file sizes
        import os
        latest_path = 'models/Agente02/checkpoints/latest.pt'
        replay_path = 'models/Agente02/checkpoints/replay.pt'
        
        if os.path.exists(latest_path):
            size_mb = os.path.getsize(latest_path) / (1024**2)
            print(f"   ✓ latest.pt: {size_mb:.1f} MB")
        
        if os.path.exists(replay_path):
            size_mb = os.path.getsize(replay_path) / (1024**2)
            print(f"   ✓ replay.pt: {size_mb:.1f} MB")
        
        print()
        print("✓ Próximos passos:")
        print("  1. Fazer download dos modelos do Colab")
        print("  2. Testar Agente02 localmente")
        print("  3. Comparar com Agente01")
        print("  4. Consideraro treinar Agente03 (Heavy)")
    else:
        print("✗✗✗ TREINAMENTO AGENTE02 FALHOU")
        print("   Status de erro:", result)
    print("=" * 80)
    
    return result


if __name__ == '__main__':
    # Para Colab: ensure imports and setup
    print("Inicializando ambiente...")
    print()
    
    try:
        exit_code = train_agente02_colab()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Erro durante treinamento: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
