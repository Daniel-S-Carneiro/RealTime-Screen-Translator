"""Guia da primeira execução: escolher como o app traduz (27/11/2026).

Aparece quando o app abre sem configuração salva, ou com um motor que saiu do app (o
Google Tradutor grátis, até 27/11/2026). Depois que a pessoa escolhe e a configuração é
salva, não aparece mais.
"""

import html
import json
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractButton, QMessageBox, QWidget

from config_usuario import ARQUIVO_CONFIG
from motores_traducao import MOTORES

AZURE = "azure"
OFFLINE = "offline"
OUTRA_CHAVE = "outra_chave"


def motor_salvo() -> Optional[str]:
    """O motor gravado no config.json, ou None se ainda não há configuração."""
    try:
        dados = json.loads(ARQUIVO_CONFIG.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    motor = dados.get("motor") if isinstance(dados, dict) else None
    return motor if isinstance(motor, str) else None


def precisa_do_guia() -> bool:
    """True na primeira execução e quando o motor salvo saiu do app."""
    motor = motor_salvo()
    return motor is None or motor not in MOTORES


def texto_do_guia(motor: Optional[str]) -> str:
    """O texto do guia; avisa da saída do Google grátis a quem o tinha escolhido."""
    aviso = ""
    if motor is not None and motor not in MOTORES:
        aviso = (
            "O Google Tradutor grátis saiu do app: ele não é um serviço oficial, e o Google "
            "bloqueia a rede de quem faz muitos pedidos.\n\n"
        )
    return aviso + (
        "Escolha como o app traduz. Dá para mudar depois, no botão ⚙ da janela.\n\n"
        "• Azure grátis (recomendado): a tradução oficial da Microsoft, com 2 milhões de "
        "caracteres grátis por mês. Pede uma conta na Azure e uma chave, que fica guardada "
        "só no seu PC.\n\n"
        "• Offline: roda no seu PC, sem conta e sem internet depois do primeiro download "
        "(cerca de 80 MB por idioma). A qualidade é menor.\n\n"
        'Se você já tem uma chave do DeepL ou do Google Cloud, escolha "Outra chave".'
    )


def montar_caixa(pai: Optional[QWidget], motor: Optional[str]) -> tuple:
    """A caixa do guia e o dicionário botão -> escolha."""
    caixa = QMessageBox(pai)
    caixa.setWindowTitle("Como traduzir")
    # Em texto puro, o QMessageBox não quebra as linhas longas; em HTML, quebra
    paragrafos = texto_do_guia(motor).split("\n\n")
    caixa.setTextFormat(Qt.TextFormat.RichText)
    caixa.setText("".join(f"<p>{html.escape(p)}</p>" for p in paragrafos))
    azure = caixa.addButton("Usar a Azure grátis", QMessageBox.ButtonRole.AcceptRole)
    botoes: dict[QAbstractButton, str] = {
        azure: AZURE,
        caixa.addButton("Usar o offline", QMessageBox.ButtonRole.ActionRole): OFFLINE,
        caixa.addButton("Outra chave", QMessageBox.ButtonRole.ActionRole): OUTRA_CHAVE,
    }
    caixa.setDefaultButton(azure)
    return caixa, botoes


def perguntar(pai: QWidget) -> Optional[str]:
    """Mostra o guia e devolve AZURE, OFFLINE, OUTRA_CHAVE ou None (fechado sem escolher)."""
    caixa, botoes = montar_caixa(pai, motor_salvo())
    caixa.exec()
    return botoes.get(caixa.clickedButton())
