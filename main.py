"""Módulo principal com overlay arrastável e integrado."""

# 1. Imports da Biblioteca Padrão (Standard Library)
import os
import sys
import tempfile
import traceback
import warnings
from datetime import datetime

from typing import Optional

# 2. Imports de Bibliotecas de Terceiros (Third-Party)
from PIL import ImageGrab
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction  # Removido o import não utilizado (QIcon)
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QScrollArea,
    QSizeGrip,
    QStackedWidget,
    QStyle,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

# 3. Imports Locais do Projeto (Local Application)
from ocr_engine import MotorOCR
from tradutor_engine import MotorTradutor
from capturador import ProcessadorImagem
from interface_config import JanelaConfiguracao

# ==========================================
# CONFIGURAÇÃO DE PRODUÇÃO / AMBIENTE
# ==========================================
DEBUG_MODE = True  # Mude para False para desativar os logs no terminal

# Silencia avisos irritantes do PyTorch rodando na CPU
warnings.filterwarnings("ignore", category=UserWarning, module="torch")


def log_debug(mensagem: str) -> None:
    """Imprime mensagens de log com timestamp apenas se o modo de debug estiver ativado."""
    if DEBUG_MODE:
        agora = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{agora}] {mensagem}")


class OverlayTradutor(QWidget):
    """Janela de overlay arrastável que alterna entre Tradução e Configurações."""

    def __init__(self, motor_ocr: MotorOCR, motor_tradutor: MotorTradutor) -> None:
        super().__init__()
        self.ocr = motor_ocr
        self.tradutor = motor_tradutor
        self.posicao_mouse = None
        self.regiao_alvo = (0, 0, 0, 0)
        self.idioma_atual = "en"

        self.paginas: Optional[QStackedWidget] = None
        self.label_texto: Optional[QLabel] = None
        self.combo_origem: Optional[QComboBox] = None
        self.combo_destino: Optional[QComboBox] = None

        self.widget_config: Optional[JanelaConfiguracao] = None
        self.tray_icon: Optional[QSystemTrayIcon] = None

        self.init_ui()
        self.init_tray_icon()

    def init_ui(self) -> None:
        """Configura a interface gráfica arrastável e empilhada."""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.Window
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        layout_raiz = QVBoxLayout()
        layout_raiz.setContentsMargins(0, 0, 0, 0)
        layout_raiz.setSpacing(0)

        self.paginas = QStackedWidget()
        self.montar_pagina_traducao()
        self.montar_pagina_configuracao()

        layout_raiz.addWidget(self.paginas)
        layout_rodape = QHBoxLayout()
        layout_rodape.addStretch()
        seletor_tamanho = QSizeGrip(self)
        layout_rodape.addWidget(seletor_tamanho)
        layout_raiz.addLayout(layout_rodape)

        self.setLayout(layout_raiz)
        self.setMinimumSize(300, 150)
        self.setGeometry(400, 400, 500, 180)

    def init_tray_icon(self) -> None:
        """Configura o ícone na bandeja do sistema (System Tray) e seu menu."""
        self.tray_icon = QSystemTrayIcon(self)

        icone_padrao = self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.tray_icon.setIcon(icone_padrao)
        self.tray_icon.setToolTip("Tradutor Gameplay")

        tray_menu = QMenu()

        acao_mostrar = QAction("Mostrar / Ocultar Overlay", self)
        # pylint: disable=no-member
        acao_mostrar.triggered.connect(self.alternar_visibilidade)
        tray_menu.addAction(acao_mostrar)

        acao_tela_inteira = QAction("Traduzir Tela Inteira (Em breve)", self)
        # pylint: disable=no-member
        acao_tela_inteira.triggered.connect(self.traduzir_tela_inteira)
        tray_menu.addAction(acao_tela_inteira)

        tray_menu.addSeparator()

        acao_sair = QAction("Encerrar Tradutor", self)
        # pylint: disable=no-member
        acao_sair.triggered.connect(QApplication.quit)
        tray_menu.addAction(acao_sair)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.evento_clique_bandeja)

    def evento_clique_bandeja(self, motivo) -> None:
        """Trata interações com o ícone da bandeja, como duplo clique."""
        if motivo == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.alternar_visibilidade()

    def alternar_visibilidade(self) -> None:
        """Alterna a visibilidade do overlay principal."""
        if self.isVisible():
            self.hide()
            log_debug("[UI] Overlay ocultado na bandeja.")
        else:
            self.show()
            self.activateWindow()
            log_debug("[UI] Overlay exibido.")

    def traduzir_tela_inteira(self) -> None:
        """Método placeholder para a futura funcionalidade de tradução em tela cheia."""
        log_debug("[AÇÃO] Função de tela inteira chamada (Pendente).")

    def ir_para_configuracao(self) -> None:
        """Navega para a página de configurações."""
        if self.paginas:
            self.paginas.setCurrentIndex(1)

    def montar_pagina_traducao(self) -> None:
        """Cria o painel principal de captura de tela e exibição com suporte a scroll."""
        widget_traducao = QWidget()
        layout = QVBoxLayout(widget_traducao)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        barra_controle = QHBoxLayout()
        btn_traduzir = QPushButton("Traduzir Área", widget_traducao)
        # Quebra de linha no CSS para evitar o erro C0301 (Line too long)
        btn_traduzir.setStyleSheet("""
            QPushButton { 
                background-color: #0078D7; color: white; border: none; 
                padding: 4px 10px; border-radius: 3px; font-weight: bold; 
            }
            QPushButton:hover { background-color: #005A9E; }
        """)

        # Uso do decorador de pylint para suprimir avisos de no-member na classe do Qt
        # pylint: disable=no-member
        btn_traduzir.clicked.connect(self.processar_traducao_local)

        btn_limpar = QPushButton("Limpar", widget_traducao)
        btn_limpar.setStyleSheet("""
            QPushButton { 
                background-color: #555555; color: white; border: none; 
                padding: 4px 10px; border-radius: 3px; font-weight: bold; 
            }
            QPushButton:hover { background-color: #333333; }
        """)

        # pylint: disable=no-member
        btn_limpar.clicked.connect(self.resetar_overlay)

        btn_config = QPushButton("⚙️", widget_traducao)
        btn_config.setFixedSize(24, 24)
        btn_config.setStyleSheet("""
            QPushButton { 
                background-color: #444444; color: white; border: none; 
                border-radius: 3px; font-size: 14px; 
            }
            QPushButton:hover { background-color: #666666; }
        """)

        # pylint: disable=no-member
        btn_config.clicked.connect(self.ir_para_configuracao)

        btn_fechar = QPushButton("X", widget_traducao)
        btn_fechar.setFixedSize(24, 24)
        btn_fechar.setStyleSheet("""
            QPushButton { 
                background-color: rgba(200, 0, 0, 180); color: white; 
                border: none; border-radius: 3px; font-weight: bold; 
            }
            QPushButton:hover { background-color: rgba(255, 0, 0, 220); }
        """)

        # pylint: disable=no-member
        btn_fechar.clicked.connect(self.hide)

        barra_controle.addWidget(btn_traduzir)
        barra_controle.addWidget(btn_limpar)
        barra_controle.addWidget(btn_config)
        barra_controle.addStretch()
        barra_controle.addWidget(btn_fechar)
        layout.addLayout(barra_controle)

        self.label_texto = QLabel(
            "Arraste esta janela sobre o texto e clique em 'Traduzir Área'",
            widget_traducao,
        )
        self.label_texto.setStyleSheet("""
            QLabel {
                color: #00FF00; 
                font-size: 16px; 
                font-family: 'Arial'; 
                font-weight: bold;
                background-color: transparent; 
                padding: 5px;
            }
        """)
        self.label_texto.setWordWrap(True)
        self.label_texto.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )

        scroll = QScrollArea(widget_traducao)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { 
                background-color: rgba(0, 0, 0, 220); 
                border: 2px dashed #00FF00; 
                border-radius: 8px; 
            }
            QScrollBar:vertical { width: 10px; background: #222; }
            QScrollBar::handle:vertical { background: #555; border-radius: 5px; }
        """)
        scroll.setWidget(self.label_texto)

        layout.addWidget(scroll)

        if self.paginas is not None:
            self.paginas.addWidget(widget_traducao)

    def voltar_para_traducao(self) -> None:
        """Método seguro para mudar a página."""
        if self.paginas:
            self.paginas.setCurrentIndex(0)

    def montar_pagina_configuracao(self) -> None:
        """Cria o painel de configurações delegando para o arquivo importado."""
        self.widget_config = JanelaConfiguracao(
            callback_salvar=self.salvar_configuracoes,
            callback_voltar=self.voltar_para_traducao,
        )
        if self.paginas:
            self.paginas.addWidget(self.widget_config)

    def salvar_configuracoes(self, novo_origem, novo_destino) -> None:
        """Aplica os novos idiomas selecionados."""
        self.ocr.alterar_idioma(novo_origem)
        self.tradutor.origem = novo_origem
        self.tradutor.destino = novo_destino
        self.idioma_atual = novo_origem
        if self.label_texto:
            self.label_texto.setText(f"Idioma alterado para: {novo_origem}")
        if self.paginas:
            self.paginas.setCurrentIndex(0)

    def mousePressEvent(self, event) -> None:
        """Captura o clique inicial do mouse para arrastar."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.posicao_mouse = event.globalPosition().toPoint()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        """Calcula o deslocamento da janela conforme o mouse arrasta."""
        if self.posicao_mouse is not None:
            deslocamento = event.globalPosition().toPoint() - self.posicao_mouse
            self.move(self.x() + deslocamento.x(), self.y() + deslocamento.y())
            self.posicao_mouse = event.globalPosition().toPoint()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        """Limpa a posição do mouse ao soltar o clique."""
        self.posicao_mouse = None
        super().mouseReleaseEvent(event)

    def resetar_overlay(self) -> None:
        """Reseta o texto para o padrão e força a janela ao tamanho inicial."""
        if self.label_texto is not None:
            log_debug("[AÇÃO] Resetando conteúdo do overlay...")
            self.label_texto.setText(
                "Arraste esta janela sobre o texto e clique em 'Traduzir Área'"
            )
        self.resize(500, 180)

    def processar_traducao_local(self) -> None:
        """Etapa 1: Calcula a geometria com ajuste de bordas úteis e oculta a janela."""
        if self.label_texto is None:
            return

        log_debug("[AÇÃO] Botão 'Traduzir Área' clicado! Ocultando overlay...")

        self.label_texto.setText("Processando...")
        tela = QApplication.screenAt(self.geometry().center())
        fator_dpi = tela.devicePixelRatio() if tela else 1.0

        log_debug(f"[INFO] Fator de escala DPI detectado: {fator_dpi}x")

        geo = self.geometry()
        x_inicial = geo.x() + 5
        y_inicial = geo.y() + 35
        x_final = geo.x() + geo.width() - 5
        y_final = geo.y() + geo.height() - 20

        self.regiao_alvo = (
            int(x_inicial * fator_dpi),
            int(y_inicial * fator_dpi),
            int(x_final * fator_dpi),
            int(y_final * fator_dpi),
        )

        self.setVisible(False)
        QApplication.processEvents()
        QTimer.singleShot(300, self._executar_print_e_ocr)

    def _executar_print_e_ocr(self) -> None:
        """Etapa 2: Executa print, processa imagem com OpenCV e faz o OCR."""
        caminho_bruto = ""
        caminho_processado = ""

        try:
            log_debug(
                f"[PROCESSO] Tirando print da região física real: {self.regiao_alvo}"
            )

            # 1. Definição do diretório (Temp para Produção, Local para Dev)
            if DEBUG_MODE:
                diretorio_base = os.path.dirname(__file__)
            else:
                diretorio_base = tempfile.gettempdir()

            caminho_bruto = os.path.join(diretorio_base, "captura.png")
            caminho_processado = os.path.join(diretorio_base, "processada.png")

            # 2. Captura da imagem bruta
            print_tela = ImageGrab.grab(bbox=self.regiao_alvo)
            print_tela.save(caminho_bruto)

            # 3. Processamento (OpenCV)
            # Passamos explicitamente o caminho_processado para o capturador
            ProcessadorImagem.preparar_para_ocr(caminho_bruto, caminho_processado)

            # 4. Restaura interface para o usuário
            self.setVisible(True)
            self.activateWindow()
            QApplication.processEvents()

            # 5. OCR
            log_debug("[PROCESSO] Enviando imagem processada para o MotorOCR...")
            texto_original = self.ocr.extrair_texto(caminho_processado)
            log_debug(f"[RESULTADO OCR] '{texto_original}'")

            if self.label_texto is not None:
                if not texto_original.strip():
                    self.label_texto.setText("[Nenhum texto detectado]")
                    return

                log_debug("[PROCESSO] Enviando para o Tradutor...")
                texto_traduzido = self.tradutor.traduzir_texto(texto_original)
                log_debug(f"[RESULTADO TRADUÇÃO] '{texto_traduzido}'")

                self.label_texto.setText(texto_traduzido)

        except Exception as e:  # pylint: disable=broad-exception-caught
            log_debug(f"[ERRO CRÍTICO] Pipeline falhou: {str(e)}")
            if DEBUG_MODE:
                traceback.print_exc()
            self.setVisible(True)
            self.activateWindow()
            if self.label_texto:
                self.label_texto.setText(f"Erro: {str(e)}")

        finally:
            # 6. Limpeza de rastros (Executa apenas em Produção)
            if not DEBUG_MODE:
                if os.path.exists(caminho_bruto):
                    os.remove(caminho_bruto)
                if os.path.exists(caminho_processado):
                    os.remove(caminho_processado)
                log_debug("[PROCESSO] Arquivos de imagem temporários excluídos.")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # ATENÇÃO: Isso garante que o app continue rodando mesmo se a janela "X" for fechada
    app.setQuitOnLastWindowClosed(False)

    log_debug("[INÍCIO] Inicializando Motor Tradutor...")
    instancia_tradutor = MotorTradutor(origem="en", destino="pt")

    log_debug("[INÍCIO] Criando instância do MotorOCR...")
    instancia_ocr = MotorOCR(idiomas=["en", "pt"])

    log_debug("[INÍCIO] Abrindo a Janela de Overlay e Bandeja...")
    overlay = OverlayTradutor(
        motor_ocr=instancia_ocr, motor_tradutor=instancia_tradutor
    )
    overlay.show()

    sys.exit(app.exec())
