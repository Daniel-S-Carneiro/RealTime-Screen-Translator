"""Preferências que não são segredo: os atalhos e a janela fora da captura (27/11/2026).

Ficam em %APPDATA%\\RealTimeScreenTranslator\\preferencias.json, separadas do config.json,
que guarda o motor e as chaves criptografadas, e do uso.json. Sem o arquivo, com ele
ilegível ou sem uma das chaves, vale o padrão de cada preferência.
"""

import copy
import json
import os

import atalhos
from config_usuario import PASTA_CONFIG

ARQUIVO_PREFERENCIAS = PASTA_CONFIG / "preferencias.json"

PADRAO = {
    "atalhos": dict(atalhos.PADRAO),
    # A janela não aparece nos prints, gravações e transmissões; assim o app lê a tela
    # sem esconder a janela a cada leitura
    "fora_da_captura": True,
}


def carregar() -> dict:
    """As preferências salvas, completadas com o padrão do que faltar ou estiver errado."""
    try:
        dados = json.loads(ARQUIVO_PREFERENCIAS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        dados = {}
    if not isinstance(dados, dict):
        dados = {}
    preferencias = copy.deepcopy(PADRAO)
    salvos = dados.get("atalhos")
    if isinstance(salvos, dict):
        for acao in preferencias["atalhos"]:
            if isinstance(salvos.get(acao), str):
                preferencias["atalhos"][acao] = salvos[acao]
    if isinstance(dados.get("fora_da_captura"), bool):
        preferencias["fora_da_captura"] = dados["fora_da_captura"]
    return preferencias


def salvar(preferencias: dict) -> None:
    """Grava as preferências; um arquivo temporário evita deixar o anterior pela metade."""
    ARQUIVO_PREFERENCIAS.parent.mkdir(parents=True, exist_ok=True)
    temporario = ARQUIVO_PREFERENCIAS.with_suffix(".tmp")
    temporario.write_text(json.dumps(preferencias, ensure_ascii=False, indent=2),
                          encoding="utf-8")
    os.replace(temporario, ARQUIVO_PREFERENCIAS)
