"""Ponto de entrada: mostra a tela de carregamento e abre o overlay quando tudo estiver pronto.

Fica leve de propósito (só o Qt). O OCR, o tradutor e os modelos carregam numa
thread, e a tela de carregamento continua respondendo e animada enquanto isso.
"""

# Os módulos pesados são importados dentro das funções, depois da tela aparecer
# pylint: disable=import-outside-toplevel

import ctypes
import os
import sys
import threading
import traceback

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from tela_carregamento import TelaCarregamento

NOME_APP = "RealTime Screen Translator"
DIRETORIO_PROJETO = os.path.dirname(os.path.abspath(__file__))
# Ícone da janela, da barra de tarefas e da bandeja (o .ico tem do 16 ao 256 px)
ICONE_APP = os.path.join(DIRETORIO_PROJETO, "assets", "icone.ico")
TOTAL_ETAPAS = 3


class Carregador(QObject):
    """Carrega as bibliotecas e os motores numa thread e avisa a interface de cada etapa."""

    etapa = Signal(int, str)
    pronto = Signal(object, object)  # (MotorOCR, MotorTradutor)
    falhou = Signal(str)

    def iniciar(self) -> None:
        """Começa o carregamento em segundo plano."""
        threading.Thread(target=self._carregar, daemon=True).start()

    def _carregar(self) -> None:
        try:
            self.etapa.emit(1, "Carregando as bibliotecas de leitura e tradução...")
            from config_usuario import carregar_config
            from ocr_engine import MotorOCR
            from tradutor_engine import MotorTradutor

            # O overlay também é importado aqui, fora da thread da interface
            from janela_overlay import log_debug

            log_debug("[INÍCIO] Inicializando Motor Tradutor...")
            config = carregar_config()
            tradutor = MotorTradutor(
                origem="en",
                destino="pt",
                motor=config["motor"],
                credenciais=config["credenciais"],
            )

            # Os modelos do RapidOCR vêm dentro do app: não há download na 1ª abertura
            self.etapa.emit(2, "Preparando a leitura de texto...")
            log_debug("[INÍCIO] Criando instância do MotorOCR...")
            ocr = MotorOCR(idiomas=["en", "pt"])
        except Exception:  # pylint: disable=broad-exception-caught
            self.falhou.emit(traceback.format_exc())
            return
        self.pronto.emit(ocr, tradutor)


class Abertura(QObject):
    """Mostra a tela de carregamento e troca pelo overlay quando o Carregador terminar.

    Os sinais do Carregador vêm de outra thread; como este objeto vive na thread da
    interface, o Qt entrega cada um aqui na hora certa.
    """

    def __init__(self, app: QApplication) -> None:
        super().__init__()
        self.app = app
        self.tela = TelaCarregamento(NOME_APP, app.windowIcon(), TOTAL_ETAPAS)
        self.overlay = None
        self.carregador = Carregador()
        # pylint: disable=no-member
        self.carregador.etapa.connect(self.tela.mostrar_etapa)
        self.carregador.pronto.connect(self.abrir_overlay)
        self.carregador.falhou.connect(self.mostrar_erro)

    def iniciar(self) -> None:
        """Mostra a tela e começa a carregar."""
        self.tela.show()
        self.carregador.iniciar()

    def abrir_overlay(self, ocr, tradutor) -> None:
        """Tudo carregado: cria o overlay (na thread da interface) e fecha a tela."""
        self.tela.mostrar_etapa(3, "Abrindo a janela...")
        from janela_overlay import OverlayTradutor, log_debug

        log_debug("[INÍCIO] Abrindo a Janela de Overlay e Bandeja...")
        self.overlay = OverlayTradutor(motor_ocr=ocr, motor_tradutor=tradutor)
        self.overlay.show()
        self.tela.close()

    def mostrar_erro(self, detalhes: str) -> None:
        """Sem isto, um erro no carregamento fechava o app instalado sem aviso nenhum."""
        print(detalhes, file=sys.stderr)
        self.tela.close()
        QMessageBox.critical(
            None, NOME_APP, "Não foi possível abrir o app.\n\n" + detalhes.strip().splitlines()[-1]
        )
        self.app.quit()


def instalar_gpu() -> None:
    """O instalador e o menu da bandeja abrem o app com --instalar-gpu para baixar o pacote GPU."""
    import aceleracao_gpu
    from janela_pacote_gpu import JanelaPacoteGpu

    if aceleracao_gpu.pode_instalar():
        JanelaPacoteGpu().exec()


def main() -> None:
    """Abre a tela de carregamento, carrega tudo em segundo plano e então mostra o overlay."""
    # Sem um ID próprio, o Windows agrupa o app com o python.exe na barra de tarefas
    # e mostra o ícone do Python no lugar do nosso
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("RealTimeScreenTranslator")

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(ICONE_APP))

    if "--instalar-gpu" in sys.argv:
        instalar_gpu()
        sys.exit(0)

    # ATENÇÃO: Isso garante que o app continue rodando mesmo se a janela "X" for fechada
    app.setQuitOnLastWindowClosed(False)

    abertura = Abertura(app)
    abertura.iniciar()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
