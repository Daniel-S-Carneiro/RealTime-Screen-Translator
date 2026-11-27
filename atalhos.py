"""Atalhos globais do teclado, que funcionam com o jogo em primeiro plano (27/11/2026).

Usa o RegisterHotKey do Windows, ligado à janela do overlay: o Windows manda a mensagem
WM_HOTKEY para a janela mesmo com outro programa em foco. Enquanto o atalho está
registrado, a combinação não chega aos outros programas; por isso os padrões usam
Ctrl+Alt, pouco usado nos jogos, e uma letra ou um número sozinho não é aceito.

Os atalhos são guardados como o QKeySequence os escreve em texto portável
("Ctrl+Alt+T"), e um texto vazio quer dizer "sem atalho".
"""

import ctypes
import sys
from ctypes import wintypes
from typing import Optional

# Ação -> o nome dela na tela de configurações
ACOES = {
    "traduzir": "Traduzir a área",
    "mostrar": "Mostrar ou esconder a janela",
    "limpar": "Limpar a tradução",
}
PADRAO = {"traduzir": "Ctrl+Alt+T", "mostrar": "Ctrl+Alt+H", "limpar": "Ctrl+Alt+L"}

WM_HOTKEY = 0x0312
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000  # segurar a tecla não repete a ação
ERRO_JA_REGISTRADO = 1409  # ERROR_HOTKEY_ALREADY_REGISTERED

MODIFICADORES = {"ctrl": MOD_CONTROL, "alt": MOD_ALT, "shift": MOD_SHIFT, "meta": MOD_WIN}
# Modificadores que tiram a tecla da digitação (o Shift sozinho só faz a maiúscula)
MODIFICADORES_FORTES = MOD_CONTROL | MOD_ALT | MOD_WIN

VK_F1 = 0x70
VK_F12 = 0x7B
# Teclas com nome, como o QKeySequence as escreve em texto portável -> (código, precisa
# de Ctrl, Alt ou Win). As setas e as teclas de edição sozinhas atrapalhariam o jogo.
TECLAS_COM_NOME = {
    "space": (0x20, True),
    "pgup": (0x21, True),
    "pgdown": (0x22, True),
    "end": (0x23, True),
    "home": (0x24, True),
    "left": (0x25, True),
    "up": (0x26, True),
    "right": (0x27, True),
    "down": (0x28, True),
    "ins": (0x2D, True),
    "del": (0x2E, True),
    "pause": (0x13, False),
    "scrolllock": (0x91, False),
}


class AtalhoInvalido(ValueError):
    """O texto não é um atalho que o app consegue registrar; a mensagem diz o porquê."""


def _codigo_da_tecla(tecla: str) -> tuple:
    """(código virtual da tecla no Windows, se precisa de Ctrl, Alt ou Win)."""
    nome = tecla.lower()
    if len(tecla) == 1 and ("A" <= tecla.upper() <= "Z" or tecla in "0123456789"):
        return ord(tecla.upper()), True
    if nome in TECLAS_COM_NOME:
        return TECLAS_COM_NOME[nome]
    if nome.startswith("f") and nome[1:].isdigit() and 1 <= int(nome[1:]) <= 24:
        return VK_F1 + int(nome[1:]) - 1, False
    raise AtalhoInvalido(f"a tecla {tecla} não pode ser usada em atalho")


def interpretar(texto: str) -> tuple:
    """'Ctrl+Alt+T' -> (modificadores, código da tecla) do RegisterHotKey."""
    partes = [parte.strip() for parte in texto.split("+")]
    if not texto.strip() or any(not parte for parte in partes):
        raise AtalhoInvalido(f"{texto!r} não é um atalho que o app consiga usar")
    *nomes_modificadores, tecla = partes
    modificadores = 0
    for nome in nomes_modificadores:
        if nome.lower() not in MODIFICADORES:
            raise AtalhoInvalido(f"{nome} não é Ctrl, Alt, Shift nem Win")
        modificadores |= MODIFICADORES[nome.lower()]
    codigo, precisa_de_modificador = _codigo_da_tecla(tecla)
    if precisa_de_modificador and not modificadores & MODIFICADORES_FORTES:
        raise AtalhoInvalido(f"{texto} atrapalharia a digitação e o jogo; use com Ctrl ou Alt")
    if codigo == VK_F12 and not modificadores:
        raise AtalhoInvalido("o F12 sozinho é reservado pelo Windows")
    return modificadores, codigo


def problemas(atalhos: dict) -> dict:
    """{ação: motivo} dos atalhos que não dá para usar; os vazios ficam de fora."""
    encontrados = {}
    usados: dict = {}  # (modificadores, código) -> primeira ação que usa
    for acao, texto in atalhos.items():
        if not texto:
            continue
        try:
            combinacao = interpretar(texto)
        except AtalhoInvalido as erro:
            encontrados[acao] = str(erro)
            continue
        if combinacao in usados:
            encontrados[acao] = f"{texto} já é o atalho de {ACOES.get(usados[combinacao], '?')}"
        else:
            usados[combinacao] = acao
    return encontrados


def _user32():
    """O user32 com as assinaturas de que o registro precisa (só existe no Windows)."""
    biblioteca = ctypes.WinDLL("user32", use_last_error=True)
    biblioteca.RegisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.UINT,
                                          wintypes.UINT]
    biblioteca.RegisterHotKey.restype = wintypes.BOOL
    biblioteca.UnregisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int]
    biblioteca.UnregisterHotKey.restype = wintypes.BOOL
    return biblioteca


class RegistroDeAtalhos:
    """Os atalhos registrados numa janela. O id de cada um é a posição da ação, a partir de 1."""

    def __init__(self) -> None:
        self.hwnd = 0
        self.ids: dict = {}  # id do RegisterHotKey -> ação

    def registrar(self, hwnd: int, atalhos: dict) -> dict:
        """Troca os atalhos registrados pelos de agora; devolve {ação: motivo} dos que falharam."""
        self.cancelar()
        if sys.platform != "win32":
            return {}
        user32 = _user32()
        self.hwnd = hwnd
        falhas = {}
        for numero, (acao, texto) in enumerate(atalhos.items(), start=1):
            if not texto:
                continue
            try:
                modificadores, codigo = interpretar(texto)
            except AtalhoInvalido as erro:
                falhas[acao] = str(erro)
                continue
            if user32.RegisterHotKey(hwnd, numero, modificadores | MOD_NOREPEAT, codigo):
                self.ids[numero] = acao
            elif ctypes.get_last_error() == ERRO_JA_REGISTRADO:
                falhas[acao] = f"{texto} já é usado por outro programa"
            else:
                falhas[acao] = f"o Windows recusou o {texto} (erro {ctypes.get_last_error()})"
        return falhas

    def cancelar(self) -> None:
        """Libera os atalhos (a tela de configurações precisa das teclas para gravá-los)."""
        if self.ids and sys.platform == "win32":
            user32 = _user32()
            for numero in self.ids:
                user32.UnregisterHotKey(self.hwnd, numero)
        self.ids = {}

    def acao_da_mensagem(self, tipo: bytes, endereco: int) -> Optional[str]:
        """A ação de uma mensagem do Windows que chegou à janela, ou None se não é atalho."""
        if tipo != b"windows_generic_MSG" or not endereco:
            return None
        mensagem = wintypes.MSG.from_address(endereco)
        if mensagem.message != WM_HOTKEY:
            return None
        return self.ids.get(mensagem.wParam)
