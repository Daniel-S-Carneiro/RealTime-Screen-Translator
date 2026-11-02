"""Configurações do usuário (motor de tradução e chaves de API).

O arquivo fica na pasta do usuário (%APPDATA%\\RealTimeScreenTranslator), fora do
projeto: assim as chaves nunca vão parar no git nem dentro do instalador.
"""

import json
import os
from pathlib import Path

PASTA_CONFIG = Path(os.environ.get("APPDATA", Path.home())) / "RealTimeScreenTranslator"
ARQUIVO_CONFIG = PASTA_CONFIG / "config.json"

CONFIG_PADRAO = {"motor": "google_web", "credenciais": {}}


def carregar_config() -> dict:
    """Lê o config.json; se não existir ou estiver corrompido, devolve o padrão."""
    try:
        with open(ARQUIVO_CONFIG, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except (FileNotFoundError, json.JSONDecodeError):
        dados = {}
    return {
        "motor": dados.get("motor", CONFIG_PADRAO["motor"]),
        "credenciais": dados.get("credenciais", {}),
    }


def salvar_config(motor: str, credenciais: dict) -> None:
    """Grava o motor escolhido e as chaves preenchidas."""
    PASTA_CONFIG.mkdir(parents=True, exist_ok=True)
    with open(ARQUIVO_CONFIG, "w", encoding="utf-8") as arquivo:
        json.dump({"motor": motor, "credenciais": credenciais}, arquivo, indent=2)
