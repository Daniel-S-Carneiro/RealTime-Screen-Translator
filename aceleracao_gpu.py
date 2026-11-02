"""Pacote de aceleração por GPU: o PyTorch com CUDA, baixado depois da instalação.

O instalador traz o PyTorch só de CPU, que funciona em qualquer PC e cabe no limite
de 2 GB do NSIS. Em PCs com placa NVIDIA, o PyTorch com CUDA (cerca de 2,5 GB) é
baixado dos servidores oficiais do PyTorch para a pasta "gpu", ao lado do .exe.

Na abertura do app empacotado, o gancho pyi_gancho_gpu.py chama ativar_se_instalado(),
que põe a pasta "gpu" na frente do sys.path: o "import torch" passa a carregar a versão
com CUDA, e a de CPU embutida fica de reserva. Rodando pelo código, nada disso acontece
e vale o PyTorch instalado no env.
"""

import hashlib
import importlib.metadata
import json
import os
import re
import shutil
import sys
import threading
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

# A mesma variante usada no env de desenvolvimento, testada numa MX350
VARIANTE_CUDA = "cu124"
ENDERECO_PYTORCH = "https://download.pytorch.org/whl"
PACOTES = ("torch", "torchvision")
# Pacote baixado (2,5 GB) + extraído (4,5 GB), com folga
ESPACO_NECESSARIO = 8 * 1024**3
TAMANHO_BLOCO = 1024 * 1024

EMPACOTADO = getattr(sys, "frozen", False)
PASTA_APP = Path(sys.executable).resolve().parent
PASTA_GPU = PASTA_APP / "gpu"
PASTA_NOVA = PASTA_APP / "gpu.novo"
PASTA_DOWNLOAD = PASTA_APP / "gpu.download"
ARQUIVO_VERSAO = PASTA_GPU / "versao.json"

# Recebe (etapa, feito, total); o total é 0 quando ainda não se sabe
Progresso = Callable[[str, int, int], None]


class ErroPacoteGpu(Exception):
    """Falha com uma mensagem pronta para mostrar à pessoa."""


class Cancelado(ErroPacoteGpu):
    """A pessoa cancelou o download."""


@dataclass(frozen=True)
class ArquivoRoda:
    """Um pacote .whl do PyTorch: nome, endereço e o SHA-256 publicado."""

    nome: str
    endereco: str
    sha256: str


def versoes_embutidas() -> dict:
    """Versões do PyTorch embutido no app, sem o sufixo: {"torch": "2.6.0", ...}."""
    return {pacote: importlib.metadata.version(pacote).split("+")[0] for pacote in PACOTES}


def pacote_instalado() -> bool:
    """True se a pasta gpu existe e é da mesma versão do PyTorch embutido."""
    try:
        return json.loads(ARQUIVO_VERSAO.read_text(encoding="utf-8")) == versoes_embutidas()
    except (OSError, ValueError, importlib.metadata.PackageNotFoundError):
        return False


def ativar_se_instalado() -> bool:
    """Põe a pasta gpu na frente do sys.path. Precisa rodar antes do primeiro import torch.

    Depois de uma atualização que troque a versão do PyTorch, o pacote antigo deixa de
    valer e o app volta para a CPU até o novo ser baixado.
    """
    if not EMPACOTADO or not pacote_instalado():
        return False
    sys.path.insert(0, str(PASTA_GPU))
    return True


def tem_placa_nvidia() -> bool:
    """O driver da NVIDIA instala o nvidia-smi.exe na pasta do sistema."""
    sistema = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32"
    return (sistema / "nvidia-smi.exe").exists()


def pode_instalar() -> bool:
    """True quando faz sentido oferecer o download: app instalado, placa NVIDIA e sem pacote."""
    return EMPACOTADO and tem_placa_nvidia() and not pacote_instalado()


def _nome_roda(pacote: str, versao: str) -> str:
    tag = f"cp{sys.version_info.major}{sys.version_info.minor}"
    return f"{pacote}-{versao}+{VARIANTE_CUDA}-{tag}-{tag}-win_amd64.whl"


def listar_rodas(sessao) -> list:
    """Monta o endereço de cada pacote e lê o SHA-256 publicado no índice do PyTorch."""
    rodas = []
    for pacote, versao in versoes_embutidas().items():
        nome = _nome_roda(pacote, versao)
        nome_na_url = nome.replace("+", "%2B")
        indice = sessao.get(f"{ENDERECO_PYTORCH}/{VARIANTE_CUDA}/{pacote}/", timeout=30)
        indice.raise_for_status()
        achado = re.search(re.escape(nome_na_url) + r"#sha256=([0-9a-f]{64})", indice.text)
        if not achado:
            raise ErroPacoteGpu(f"O site do PyTorch não oferece mais o pacote {nome}.")
        endereco = f"{ENDERECO_PYTORCH}/{VARIANTE_CUDA}/{nome_na_url}"
        rodas.append(ArquivoRoda(nome, endereco, achado.group(1)))
    return rodas


def _conferir_sha256(caminho: Path, esperado: str, progresso: Progresso, cancelar) -> None:
    total = caminho.stat().st_size
    resumo = hashlib.sha256()
    feito = 0
    with open(caminho, "rb") as arquivo:
        while bloco := arquivo.read(TAMANHO_BLOCO):
            if cancelar.is_set():
                raise Cancelado("Download cancelado.")
            resumo.update(bloco)
            feito += len(bloco)
            progresso(f"Conferindo {caminho.name}", feito, total)
    if resumo.hexdigest() != esperado:
        caminho.unlink()
        raise ErroPacoteGpu("O arquivo baixado veio corrompido. Tente de novo.")


def _baixar(sessao, roda: ArquivoRoda, progresso: Progresso, cancelar) -> Path:
    """Baixa a roda; se um download anterior parou no meio, continua de onde parou."""
    destino = PASTA_DOWNLOAD / roda.nome
    feito = destino.stat().st_size if destino.exists() else 0
    cabecalhos = {"Range": f"bytes={feito}-"} if feito else {}
    with sessao.get(roda.endereco, headers=cabecalhos, stream=True, timeout=30) as resposta:
        if resposta.status_code != 416:  # 416: o arquivo já estava completo
            resposta.raise_for_status()
            if resposta.status_code != 206:  # o servidor ignorou o Range: recomeça
                feito = 0
            total = feito + int(resposta.headers.get("Content-Length", 0))
            with open(destino, "ab" if feito else "wb") as saida:
                for bloco in resposta.iter_content(TAMANHO_BLOCO):
                    if cancelar.is_set():
                        raise Cancelado("Download cancelado.")
                    saida.write(bloco)
                    feito += len(bloco)
                    progresso(f"Baixando {roda.nome}", feito, total)
    _conferir_sha256(destino, roda.sha256, progresso, cancelar)
    return destino


def _extrair(arquivos: list, progresso: Progresso, cancelar) -> None:
    """Extrai as rodas numa pasta nova e só no fim troca pela pasta gpu.

    Assim uma extração interrompida nunca deixa uma pasta gpu pela metade, que o
    gancho de inicialização tentaria usar.
    """
    shutil.rmtree(PASTA_NOVA, ignore_errors=True)
    for arquivo in arquivos:
        with zipfile.ZipFile(arquivo) as roda:
            membros = roda.infolist()
            total = sum(membro.file_size for membro in membros)
            feito = 0
            for membro in membros:
                if cancelar.is_set():
                    raise Cancelado("Instalação cancelada.")
                roda.extract(membro, PASTA_NOVA)
                feito += membro.file_size
                progresso(f"Instalando {arquivo.name}", feito, total)
    (PASTA_NOVA / "versao.json").write_text(json.dumps(versoes_embutidas()), encoding="utf-8")
    shutil.rmtree(PASTA_GPU, ignore_errors=True)
    PASTA_NOVA.rename(PASTA_GPU)


def instalar(progresso: Progresso, cancelar: threading.Event) -> None:
    """Baixa, confere e instala o PyTorch com CUDA na pasta gpu."""
    # Importado aqui para o gancho de inicialização, que importa este módulo, continuar leve
    import requests  # pylint: disable=import-outside-toplevel

    if shutil.disk_usage(PASTA_APP).free < ESPACO_NECESSARIO:
        raise ErroPacoteGpu("Espaço insuficiente: são necessários 8 GB livres no disco do app.")
    PASTA_DOWNLOAD.mkdir(exist_ok=True)
    try:
        with requests.Session() as sessao:
            progresso("Consultando o site do PyTorch", 0, 0)
            arquivos = [_baixar(sessao, roda, progresso, cancelar) for roda in listar_rodas(sessao)]
    except requests.RequestException as erro:
        raise ErroPacoteGpu(
            "Não foi possível baixar o pacote. Confira a internet e tente de novo; "
            f"o download continua de onde parou. ({erro})"
        ) from erro
    _extrair(arquivos, progresso, cancelar)
    shutil.rmtree(PASTA_DOWNLOAD, ignore_errors=True)
