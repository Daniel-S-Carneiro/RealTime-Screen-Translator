"""Gancho de inicialização do PyInstaller (--runtime-hook): roda antes do main.py.

No app instalado, põe a pasta "gpu" (PyTorch com CUDA, baixado depois da instalação)
na frente do sys.path, para o "import torch" usar a placa NVIDIA. Veja aceleracao_gpu.py.
"""

try:
    import aceleracao_gpu

    aceleracao_gpu.ativar_se_instalado()
except Exception:  # pylint: disable=broad-exception-caught
    pass  # qualquer problema aqui só deixa o app na CPU; ele não pode impedir a abertura
