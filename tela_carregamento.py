"""Tela que aparece logo ao abrir o app, enquanto as bibliotecas pesadas carregam.

O OCR, o tradutor e os modelos de leitura levam uns 3 s numa abertura repetida (eram
8 s quando o EasyOCR e o PyTorch carregavam na abertura) e bem mais na primeira depois
de ligar o PC, quando o Windows ainda não tem os arquivos em cache. Antes desta tela,
nada aparecia nesse tempo.

Só usa o Qt: precisa abrir antes de qualquer biblioteca pesada ser importada.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout, QWidget

ESTILO = """
    QFrame#fundo {
        background-color: #1E1E1E;
        border: 1px solid #3A3A3A;
        border-radius: 10px;
    }
    QLabel { color: #E0E0E0; font-family: 'Arial'; }
    QLabel#titulo { color: white; font-size: 17px; font-weight: bold; }
    QLabel#mensagem { font-size: 13px; }
    QLabel#contador { color: #8A8A8A; font-size: 12px; }
    QProgressBar { background-color: #333333; border: none; border-radius: 3px; }
    QProgressBar::chunk { background-color: #0078D7; border-radius: 3px; }
"""


class TelaCarregamento(QWidget):
    """Janela sem borda com o ícone, a etapa atual e uma barra animada."""

    def __init__(self, nome_app: str, icone: QIcon, total_etapas: int) -> None:
        super().__init__(None, Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowTitle(nome_app)
        self.setStyleSheet(ESTILO)
        self.total_etapas = total_etapas

        fundo = QFrame(self)
        fundo.setObjectName("fundo")
        QVBoxLayout(self).addWidget(fundo)
        self.layout().setContentsMargins(0, 0, 0, 0)

        imagem = QLabel()
        imagem.setPixmap(icone.pixmap(56, 56))
        titulo = QLabel(nome_app)
        titulo.setObjectName("titulo")
        self.mensagem = QLabel("Abrindo...")
        self.mensagem.setObjectName("mensagem")
        self.mensagem.setWordWrap(True)
        self.contador = QLabel()
        self.contador.setObjectName("contador")

        # Sem mínimo e máximo, a barra fica em "ocupado" e se anima sozinha: como o
        # carregamento roda em outra thread, ela continua andando o tempo todo
        self.barra = QProgressBar()
        self.barra.setRange(0, 0)
        self.barra.setTextVisible(False)
        self.barra.setFixedHeight(6)

        topo = QHBoxLayout()
        topo.setSpacing(14)
        topo.addWidget(imagem)
        textos = QVBoxLayout()
        textos.addWidget(titulo)
        textos.addWidget(self.mensagem)
        topo.addLayout(textos, stretch=1)

        rodape = QHBoxLayout()
        rodape.addWidget(self.barra, stretch=1)
        rodape.addWidget(self.contador)

        layout = QVBoxLayout(fundo)
        layout.setContentsMargins(20, 18, 20, 16)
        layout.setSpacing(14)
        layout.addLayout(topo)
        layout.addLayout(rodape)

        self.setFixedSize(440, 140)
        tela = QGuiApplication.primaryScreen().availableGeometry()
        self.move(tela.center() - self.rect().center())

    def mostrar_etapa(self, numero: int, texto: str) -> None:
        """Troca a mensagem e o contador ("2 de 3")."""
        self.mensagem.setText(texto)
        self.contador.setText(f"{numero} de {self.total_etapas}")
