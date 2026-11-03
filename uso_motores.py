"""Contador de uso dos motores de tradução pagos e a trava para não gerar cobrança.

O app conta, mês a mês, os caracteres que manda para cada motor com plano grátis
limitado (Azure, DeepL e Google Cloud). Azure e Google Cloud não informam o uso pela
chave de API, então essa conta é a única que o app tem; ela só conhece o uso deste PC.

Com a trava ligada (o padrão), o MotorTradutor deixa de usar um motor com trava de
custo quando o próximo texto passaria do limite grátis do mês, e cai nas reservas.

Fica em %APPDATA%\\RealTimeScreenTranslator\\uso.json, separado do config.json: não
tem nada secreto e muda a cada tradução.
"""

import json
import os
import threading
from datetime import datetime

from config_usuario import PASTA_CONFIG

ARQUIVO_USO = PASTA_CONFIG / "uso.json"

# A tradução roda numa thread e a tela de configurações lê na thread da interface
_TRAVA_ARQUIVO = threading.Lock()


def _mes_atual() -> str:
    return datetime.now().strftime("%Y-%m")


def _ler() -> dict:
    """Lê o arquivo; num mês novo, a contagem começa do zero."""
    try:
        with open(ARQUIVO_USO, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except (FileNotFoundError, json.JSONDecodeError):
        dados = {}
    if dados.get("mes") != _mes_atual():
        dados["mes"] = _mes_atual()
        dados["caracteres"] = {}
    dados.setdefault("caracteres", {})
    dados.setdefault("trava_ligada", True)
    return dados


def _gravar(dados: dict) -> None:
    ARQUIVO_USO.parent.mkdir(parents=True, exist_ok=True)
    temporario = ARQUIVO_USO.with_suffix(".tmp")
    with open(temporario, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=2)
    os.replace(temporario, ARQUIVO_USO)


def registrar(motor: str, caracteres: int) -> None:
    """Soma os caracteres que o serviço vai cobrar por uma tradução."""
    with _TRAVA_ARQUIVO:
        dados = _ler()
        dados["caracteres"][motor] = dados["caracteres"].get(motor, 0) + caracteres
        try:
            _gravar(dados)
        except OSError as erro:
            # Não poder gravar a conta não pode impedir a tradução
            print(f"Aviso: não consegui gravar o uso de {motor}: {erro}")


def usado_no_mes(motor: str) -> int:
    """Caracteres mandados para o motor neste mês, contados por este app."""
    with _TRAVA_ARQUIVO:
        return _ler()["caracteres"].get(motor, 0)


def trava_ligada() -> bool:
    """Se o app deve parar de usar motores pagos ao chegar no limite grátis."""
    with _TRAVA_ARQUIVO:
        return bool(_ler()["trava_ligada"])


def definir_trava(ligada: bool) -> None:
    """Liga ou desliga a trava (chamado ao salvar as configurações)."""
    with _TRAVA_ARQUIVO:
        dados = _ler()
        dados["trava_ligada"] = ligada
        _gravar(dados)
