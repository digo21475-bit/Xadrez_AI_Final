import torch, torchvision
print(torch.__version__)          # deve exibir 2.9.1+rocm6.3
print(torch.cuda.is_available())  # deve ser True
print(torchvision.__version__)    # deve exibir 0.24.1+rocm6.3
