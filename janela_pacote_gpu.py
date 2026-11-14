"""Janela que baixa e instala o pacote de aceleração por GPU (veja aceleracao_gpu.py).

O instalador abre o app com --instalar-gpu no fim da instalação, e o menu da bandeja
abre esta mesma janela quando a pessoa deixou para depois.
"""

import threading
import time

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)

import aceleracao_gpu

TEXTO_CONVITE = (
    "Encontramos uma placa de vídeo NVIDIA neste PC. Com ela, o app lê a tela mais rápido.\n\n"
    "Para usar a placa, o app precisa baixar o PyTorch com suporte a CUDA (cerca de 2,5 GB) "
    "direto do site oficial do PyTorch. Sem ele, o app funciona normalmente usando só o "
    "processador.\n\n"
    "Se preferir, dá para baixar depois pelo ícone do app na bandeja."
)
TEXTO_BAIXANDO = "Baixando e instalando a aceleração por GPU. Pode usar o PC enquanto isso."
TEXTO_PRONTO = (
    "Pronto! A aceleração por GPU está instalada.\n\n"
    "Ela passa a valer na próxima vez que o app abrir."
)
TEXTO_CANCELADO = (
    "Download cancelado. O que já foi baixado fica guardado, e da próxima vez o "
    "download continua de onde parou."
)


def _gb(quantidade: int) -> str:
    return f"{quantidade / 1e9:.2f}".replace(".", ",")


class JanelaPacoteGpu(QDialog):
    """Convida a baixar o pacote GPU e mostra o progresso do download e da instalação."""

    # (etapa, feito, total), vindo da thread de download
    progresso_mudou = Signal(str, int, int)
    # (situação: "ok", "cancelado" ou "erro"; mensagem)
    terminou = Signal(str, str)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Aceleração por GPU")
        self.setMinimumWidth(480)

        self._cancelar = threading.Event()
        self._executando = False
        self._fechar_ao_terminar = False
        # Para calcular velocidade e tempo restante de cada etapa
        self._etapa_atual = ""
        self._inicio_etapa = 0.0
        self._feito_no_inicio = 0

        self.texto = QLabel(TEXTO_CONVITE)
        self.texto.setWordWrap(True)
        self.etapa = QLabel()
        self.etapa.setWordWrap(True)
        self.barra = QProgressBar()
        self.barra.setRange(0, 1000)  # em milésimos: 2,5 GB não cabe no int do Qt
        self.barra.setTextVisible(False)
        self.detalhe = QLabel()
        for widget in (self.etapa, self.barra, self.detalhe):
            widget.hide()

        self.btn_principal = QPushButton("Baixar agora")
        self.btn_secundario = QPushButton("Agora não")
        self.btn_principal.setDefault(True)
        layout_botoes = QHBoxLayout()
        layout_botoes.addStretch()
        layout_botoes.addWidget(self.btn_secundario)
        layout_botoes.addWidget(self.btn_principal)

        layout = QVBoxLayout(self)
        for widget in (self.texto, self.etapa, self.barra, self.detalhe):
            layout.addWidget(widget)
        layout.addLayout(layout_botoes)

        # pylint: disable=no-member
        self.btn_principal.clicked.connect(self._comecar)
        self.btn_secundario.clicked.connect(self._cancelar_ou_fechar)
        self.progresso_mudou.connect(self._mostrar_progresso)
        self.terminou.connect(self._mostrar_fim)

    def _comecar(self) -> None:
        self._executando = True
        self._cancelar.clear()
        self._etapa_atual = ""
        self.texto.setText(TEXTO_BAIXANDO)
        for widget in (self.etapa, self.barra, self.detalhe):
            widget.show()
        self.barra.setValue(0)
        self.btn_principal.hide()
        self.btn_secundario.setText("Cancelar")
        threading.Thread(target=self._trabalhar, daemon=True).start()

    def _trabalhar(self) -> None:
        """Roda fora da thread da interface; o resultado volta pelo sinal terminou."""
        try:
            aceleracao_gpu.instalar(self.progresso_mudou.emit, self._cancelar)
        except aceleracao_gpu.Cancelado:
            self.terminou.emit("cancelado", TEXTO_CANCELADO)
        except aceleracao_gpu.ErroPacoteGpu as erro:
            self.terminou.emit("erro", str(erro))
        except OSError as erro:
            self.terminou.emit("erro", f"Não foi possível gravar os arquivos do pacote: {erro}")
        else:
            self.terminou.emit("ok", TEXTO_PRONTO)

    def _mostrar_progresso(self, etapa: str, feito: int, total: int) -> None:
        agora = time.monotonic()
        if etapa != self._etapa_atual:
            self._etapa_atual = etapa
            self._inicio_etapa = agora
            self._feito_no_inicio = feito
            self.etapa.setText(etapa)

        if not total:
            self.barra.setRange(0, 0)  # animação de "aguarde"
            self.detalhe.clear()
            return
        self.barra.setRange(0, 1000)
        self.barra.setValue(int(feito * 1000 / total))

        detalhe = f"{_gb(feito)} de {_gb(total)} GB"
        decorrido = agora - self._inicio_etapa
        velocidade = (feito - self._feito_no_inicio) / decorrido if decorrido > 1 else 0
        if velocidade > 0:
            restante = (total - feito) / velocidade
            minutos = "menos de 1 min" if restante < 60 else f"cerca de {round(restante / 60)} min"
            detalhe += f"  ·  {velocidade / 1e6:.1f} MB/s  ·  faltam {minutos}".replace(".", ",")
        self.detalhe.setText(detalhe)

    def _mostrar_fim(self, situacao: str, mensagem: str) -> None:
        self._executando = False
        if self._fechar_ao_terminar:
            super().reject()
            return
        self.texto.setText(mensagem)
        for widget in (self.etapa, self.barra, self.detalhe):
            widget.hide()
        self.btn_secundario.setText("Fechar")
        if situacao == "ok":
            self.btn_principal.hide()
        else:
            self.btn_principal.setText("Tentar de novo")
            self.btn_principal.show()

    def _cancelar_ou_fechar(self) -> None:
        if self._executando:
            self._cancelar.set()
            self.etapa.setText("Cancelando...")
        else:
            self.reject()

    def reject(self) -> None:
        """Esc ou X durante o download: cancela e fecha quando a thread parar."""
        if self._executando:
            self._cancelar.set()
            self._fechar_ao_terminar = True
            self.etapa.setText("Cancelando...")
            return
        super().reject()
