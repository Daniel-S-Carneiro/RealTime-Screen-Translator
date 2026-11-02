"""Configurações do usuário (motor de tradução e chaves de API).

O arquivo fica na pasta do usuário (%APPDATA%\\RealTimeScreenTranslator), fora do
projeto: assim as chaves nunca vão parar no git nem dentro do instalador.

As chaves são gravadas criptografadas com o DPAPI do Windows, que usa uma chave
ligada à conta do Windows: só a mesma conta, no mesmo PC, consegue abrir. Um
config.json copiado para outro lugar não revela as chaves.
"""

import base64
import ctypes
import json
import os
from ctypes import wintypes
from pathlib import Path

PASTA_CONFIG = Path(os.environ.get("APPDATA", Path.home())) / "RealTimeScreenTranslator"
ARQUIVO_CONFIG = PASTA_CONFIG / "config.json"

CONFIG_PADRAO = {"motor": "google_web", "credenciais": {}}

# Impede o Windows de abrir uma janela pedindo confirmação ao criptografar
CRYPTPROTECT_UI_FORBIDDEN = 0x1


class _BlobDados(ctypes.Structure):  # pylint: disable=too-few-public-methods
    """DATA_BLOB da API do Windows: um bloco de bytes e o tamanho dele."""

    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]


def _chamar_dpapi(funcao, dados: bytes) -> bytes:
    """Passa os bytes por CryptProtectData ou CryptUnprotectData (mesma assinatura)."""
    buffer = ctypes.create_string_buffer(dados, len(dados))
    entrada = _BlobDados(len(dados), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_char)))
    saida = _BlobDados()
    # Os None são a descrição, a entropia extra, um campo reservado e o aviso na tela
    sucesso = funcao(
        ctypes.byref(entrada),
        None,
        None,
        None,
        None,
        CRYPTPROTECT_UI_FORBIDDEN,
        ctypes.byref(saida),
    )
    if not sucesso:
        raise ctypes.WinError()
    try:
        return ctypes.string_at(saida.pbData, saida.cbData)
    finally:
        ctypes.windll.kernel32.LocalFree(saida.pbData)


def criptografar(dados: bytes) -> bytes:
    """Criptografa com a chave da conta do Windows (DPAPI)."""
    return _chamar_dpapi(ctypes.windll.crypt32.CryptProtectData, dados)


def descriptografar(dados: bytes) -> bytes:
    """Desfaz o criptografar(); falha (OSError) em outra conta ou em outro PC."""
    return _chamar_dpapi(ctypes.windll.crypt32.CryptUnprotectData, dados)


def _ler_credenciais(protegidas: str) -> dict:
    """Abre as chaves gravadas pelo salvar_config()."""
    if not protegidas:
        return {}
    try:
        return json.loads(descriptografar(base64.b64decode(protegidas)).decode("utf-8"))
    except (OSError, ValueError):
        # Arquivo vindo de outro PC ou de outra conta do Windows: as chaves precisam
        # ser coladas de novo. O arquivo só é sobrescrito quando a pessoa salvar.
        print("Aviso: não consegui abrir as chaves salvas; cole-as de novo nas configurações.")
        return {}


def carregar_config() -> dict:
    """Lê o config.json; se não existir ou estiver corrompido, devolve o padrão.

    Um config.json do formato antigo, com as chaves em texto puro, é regravado
    criptografado na primeira leitura.
    """
    try:
        with open(ARQUIVO_CONFIG, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except (FileNotFoundError, json.JSONDecodeError):
        dados = {}
    motor = dados.get("motor", CONFIG_PADRAO["motor"])

    if "credenciais" in dados:
        credenciais = dados["credenciais"]
        try:
            salvar_config(motor, credenciais)
        except OSError:
            pass  # sem permissão de escrita: tenta de novo na próxima abertura
    else:
        credenciais = _ler_credenciais(dados.get("credenciais_protegidas", ""))
    return {"motor": motor, "credenciais": credenciais}


def salvar_config(motor: str, credenciais: dict) -> None:
    """Grava o motor escolhido e as chaves preenchidas, criptografadas."""
    protegidas = criptografar(json.dumps(credenciais).encode("utf-8"))
    conteudo = {
        "motor": motor,
        "credenciais_protegidas": base64.b64encode(protegidas).decode("ascii"),
    }
    PASTA_CONFIG.mkdir(parents=True, exist_ok=True)
    # Grava num arquivo temporário e troca no fim: se algo falhar no meio, o
    # config.json anterior continua inteiro e as chaves não se perdem.
    temporario = ARQUIVO_CONFIG.with_suffix(".tmp")
    with open(temporario, "w", encoding="utf-8") as arquivo:
        json.dump(conteudo, arquivo, indent=2)
    os.replace(temporario, ARQUIVO_CONFIG)
