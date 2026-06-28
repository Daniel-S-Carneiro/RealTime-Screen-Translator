"""Módulo contendo a interface de configurações para o tradutor."""

import json
from typing import Callable, Any, Optional
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
)
from PySide6.QtCore import Qt
from gerenciador_idiomas import JanelaGerenciarIdiomas

# Dicionário com as 80 línguas suportadas pelo EasyOCR
TODOS_IDIOMAS = {
    "Abaza": "abq",
    "Adyghe": "ady",
    "Afrikaans": "af",
    "Albanian": "sq",
    "Angika": "ang",
    "Arabic": "ar",
    "Assamese": "as",
    "Avar": "ava",
    "Azerbaijani": "az",
    "Belarusian": "be",
    "Bengali": "bn",
    "Bhojpuri": "bho",
    "Bihari": "bh",
    "Bosnian": "bs",
    "Bulgarian": "bg",
    "Chechen": "che",
    "Chinese (simplified)": "ch_sim",
    "Chinese (traditional)": "ch_tra",
    "Croatian": "hr",
    "Czech": "cs",
    "Danish": "da",
    "Dargwa": "dar",
    "Dutch": "nl",
    "English": "en",
    "Estonian": "et",
    "French": "fr",
    "German": "de",
    "Goan Konkani": "gom",
    "Hindi": "hi",
    "Hungarian": "hu",
    "Icelandic": "is",
    "Indonesian": "id",
    "Ingush": "inh",
    "Irish": "ga",
    "Italian": "it",
    "Japanese": "ja",
    "Kabardian": "kbd",
    "Kannada": "kn",
    "Korean": "ko",
    "Kurdish": "ku",
    "Lak": "lbe",
    "Latin": "la",
    "Latvian": "lv",
    "Lezghian": "lez",
    "Lithuanian": "lt",
    "Magahi": "mah",
    "Maithili": "mai",
    "Malay": "ms",
    "Maltese": "mt",
    "Maori": "mi",
    "Marathi": "mr",
    "Mongolian": "mn",
    "Nagpuri": "sck",
    "Nepali": "ne",
    "Newari": "new",
    "Norwegian": "no",
    "Occitan": "oc",
    "Pali": "pi",
    "Persian (Farsi)": "fa",
    "Polish": "pl",
    "Portuguese": "pt",
    "Romanian": "ro",
    "Russian": "ru",
    "Serbian (cyrillic)": "rs_cyrillic",
    "Serbian (latin)": "rs_latin",
    "Slovak": "sk",
    "Slovenian": "sl",
    "Spanish": "es",
    "Swahili": "sw",
    "Swedish": "sv",
    "Tabassaran": "tab",
    "Tagalog": "tl",
    "Tajik": "tjk",
    "Tamil": "ta",
    "Telugu": "te",
    "Thai": "th",
    "Turkish": "tr",
    "Ukrainian": "uk",
    "Urdu": "ur",
    "Uyghur": "ug",
    "Uzbek": "uz",
    "Vietnamese": "vi",
    "Welsh": "cy",
}


class JanelaConfiguracao(QWidget):
    """Componente isolado para a interface de configurações."""

    def __init__(
        self,
        callback_salvar: Callable[[Any, Any], None],
        callback_voltar: Callable[[], None],
    ) -> None:
        super().__init__()
        self.callback_salvar = callback_salvar
        self.callback_voltar = callback_voltar

        self.combo_origem: QComboBox = QComboBox()
        self.combo_destino: QComboBox = QComboBox()
        self.janela_extra: Optional[JanelaGerenciarIdiomas] = None

        # Dados Padrão (Top 10)
        self.top_10 = {
            "Inglês": "en",
            "Português": "pt",
            "Espanhol": "es",
            "Chinês": "ch_sim",
            "Hindi": "hi",
            "Árabe": "ar",
            "Francês": "fr",
            "Bengali": "bn",
            "Russo": "ru",
            "Japonês": "ja",
        }

        self.dados: dict = {}
        self.init_ui()

    def init_ui(self) -> None:
        """Inicializa a interface e constrói o layout principal."""
        layout = QVBoxLayout(self)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
            JanelaConfiguracao { 
                background-color: rgb(30, 30, 30); 
                border-radius: 5px; 
                border: 1px solid #555; 
            }
            """)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        label_titulo = QLabel("Configurações do Tradutor")
        label_titulo.setStyleSheet(
            "color: white; font-size: 16px; font-weight: bold; border: none;"
        )
        layout.addWidget(label_titulo)

        # Carregar ou criar JSON
        try:
            with open("idiomas.json", "r", encoding="utf-8") as f:
                self.dados = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.dados = {"mais_usados": self.top_10, "outros": {}}

        # Criação e uso do método _envolver_em_layout
        self.combo_origem = self._criar_combo()
        self.combo_origem.setCurrentText("Inglês")
        layout.addLayout(self._envolver_em_layout("Origem:", self.combo_origem))

        self.combo_destino = self._criar_combo()
        self.combo_destino.setCurrentText("Português")
        layout.addLayout(self._envolver_em_layout("Destino:", self.combo_destino))

        # Botão para adicionar novos idiomas
        btn_add = QPushButton("Adicionar nova língua...")
        getattr(btn_add.clicked, "connect")(self.abrir_gerenciador)
        layout.addWidget(btn_add)

        layout.addStretch()

        # Botões de Voltar e Salvar
        layout_botoes = QHBoxLayout()
        btn_voltar = QPushButton("Voltar")
        getattr(btn_voltar.clicked, "connect")(self.callback_voltar)
        layout_botoes.addWidget(btn_voltar)

        btn_salvar = QPushButton("Salvar")
        getattr(btn_salvar.clicked, "connect")(
            lambda: self.callback_salvar(
                self.combo_origem.currentData(), self.combo_destino.currentData()
            )
        )
        layout_botoes.addWidget(btn_salvar)

        layout.addLayout(layout_botoes)

    def _criar_combo(self) -> QComboBox:
        """Cria e preenche um QComboBox com as línguas do sistema."""
        combo = QComboBox()
        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        # Adiciona top 10
        for nome, cod in self.top_10.items():
            combo.addItem(nome, cod)

        # Adiciona extras do JSON e coloca separador
        outros = self.dados.get("outros", {})
        if outros:
            combo.insertSeparator(combo.count())
            for nome, cod in outros.items():
                combo.addItem(nome, cod)

        return combo

    def abrir_gerenciador(self) -> None:
        """Abre a janela extra para selecionar mais idiomas."""
        self.janela_extra = JanelaGerenciarIdiomas(TODOS_IDIOMAS, self.atualizar_ui)
        self.janela_extra.show()

    def atualizar_ui(self) -> None:
        """Recarrega o JSON e atualiza as opções nos QComboBox dinamicamente."""
        try:
            with open("idiomas.json", "r", encoding="utf-8") as f:
                self.dados = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

        # Salva as seleções atuais para não resetar na cara do usuário
        texto_origem = self.combo_origem.currentText()
        texto_destino = self.combo_destino.currentText()

        # Limpa tudo
        self.combo_origem.clear()
        self.combo_destino.clear()

        # Repopula Top 10
        for nome, cod in self.top_10.items():
            self.combo_origem.addItem(nome, cod)
            self.combo_destino.addItem(nome, cod)

        # Repopula Outros
        outros = self.dados.get("outros", {})
        if outros:
            self.combo_origem.insertSeparator(self.combo_origem.count())
            self.combo_destino.insertSeparator(self.combo_destino.count())
            for nome, cod in outros.items():
                self.combo_origem.addItem(nome, cod)
                self.combo_destino.addItem(nome, cod)

        # Restaura a seleção que o usuário estava vendo
        self.combo_origem.setCurrentText(texto_origem)
        self.combo_destino.setCurrentText(texto_destino)

    def _envolver_em_layout(self, texto: str, combo: QComboBox) -> QHBoxLayout:
        """Envolve um label e um combo em um layout horizontal padronizado."""
        h_layout = QHBoxLayout()
        lbl = QLabel(texto)
        lbl.setStyleSheet("color: #DDD; font-size: 13px; border: none;")
        h_layout.addWidget(lbl)
        h_layout.addWidget(combo)
        return h_layout
