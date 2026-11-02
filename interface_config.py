"""Módulo contendo a interface de configurações para o tradutor."""

import json
import threading
from typing import Callable, Any, Optional
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QFrame,
    QLineEdit,
    QPushButton,
    QScrollArea,
)
from PySide6.QtCore import Qt, Signal
from config_usuario import carregar_config, salvar_config
from gerenciador_idiomas import JanelaGerenciarIdiomas
from motores_traducao import MOTORES, ErroMotor, traduzir_com

ROTULOS_CAMPOS = {"chave": "Chave:", "regiao": "Região:"}
FRASE_TESTE = "Welcome, adventurer! Your quest begins now."
ESTILO_TEXTO_AJUDA = "color: #BBB; font-size: 12px; border: none;"

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

    # Leva o resultado do botão "Testar" (feito em outra thread) de volta para a interface
    resultado_teste = Signal(str)

    def __init__(
        self,
        callback_salvar: Callable[[Any, Any, str, dict], None],
        callback_voltar: Callable[[], None],
    ) -> None:
        super().__init__()
        self.callback_salvar = callback_salvar
        self.callback_voltar = callback_voltar

        self.combo_origem: QComboBox = QComboBox()
        self.combo_destino: QComboBox = QComboBox()
        self.janela_extra: Optional[JanelaGerenciarIdiomas] = None

        # Motor de tradução: as chaves de todos os motores ficam aqui até o "Salvar"
        config = carregar_config()
        self.credenciais: dict = config["credenciais"]
        self.combo_motor = QComboBox()
        # Deixa o combo encolher com a janela em vez de forçar rolagem lateral
        self.combo_motor.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        self.combo_motor.setMinimumContentsLength(12)
        for codigo, info in MOTORES.items():
            self.combo_motor.addItem(info.nome, codigo)
        self.combo_motor.setCurrentIndex(max(self.combo_motor.findData(config["motor"]), 0))
        self.label_descricao_motor = QLabel()
        self.label_links_motor = QLabel()
        self.campos_motor: dict[str, tuple] = {}  # campo -> (linha, QLineEdit)
        self.btn_testar = QPushButton("Testar")
        self.label_teste = QLabel()

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
        layout_raiz = QVBoxLayout(self)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
            JanelaConfiguracao {
                background-color: rgb(30, 30, 30);
                border-radius: 5px;
                border: 1px solid #555;
            }
            """)
        layout_raiz.setContentsMargins(10, 10, 10, 10)
        layout_raiz.setSpacing(10)

        # O conteúdo rola: com o motor de tradução, a tela não cabe num overlay pequeno
        conteudo = QWidget()
        conteudo.setObjectName("conteudoConfig")
        layout = QVBoxLayout(conteudo)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        rolagem = QScrollArea()
        rolagem.setWidgetResizable(True)
        rolagem.setFrameShape(QFrame.Shape.NoFrame)
        rolagem.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        rolagem.setStyleSheet(
            "QScrollArea, QWidget#qt_scrollarea_viewport, QWidget#conteudoConfig "
            "{ background: transparent; border: none; }"
        )
        rolagem.setWidget(conteudo)
        layout_raiz.addWidget(rolagem)

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
        self._selecionar_por_texto(self.combo_origem, "Inglês")
        layout.addLayout(self._envolver_em_layout("Origem:", self.combo_origem))

        self.combo_destino = self._criar_combo()
        self._selecionar_por_texto(self.combo_destino, "Português")
        layout.addLayout(self._envolver_em_layout("Destino:", self.combo_destino))

        # Botão para adicionar novos idiomas
        btn_add = QPushButton("Adicionar nova língua...")
        getattr(btn_add.clicked, "connect")(self.abrir_gerenciador)
        layout.addWidget(btn_add)

        self._montar_secao_motor(layout)

        layout.addStretch()

        # Botões de Voltar e Salvar (fora da rolagem, sempre visíveis)
        layout_botoes = QHBoxLayout()
        btn_voltar = QPushButton("Voltar")
        getattr(btn_voltar.clicked, "connect")(self.callback_voltar)
        layout_botoes.addWidget(btn_voltar)

        btn_salvar = QPushButton("Salvar")
        getattr(btn_salvar.clicked, "connect")(self._salvar)
        layout_botoes.addWidget(btn_salvar)

        layout_raiz.addLayout(layout_botoes)

    def _salvar(self) -> None:
        """Grava o motor e as chaves no config do usuário e aplica tudo no app."""
        motor = self.combo_motor.currentData()
        salvar_config(motor, self.credenciais)
        self.callback_salvar(
            self.combo_origem.currentData(),
            self.combo_destino.currentData(),
            motor,
            self.credenciais,
        )

    def _montar_secao_motor(self, layout: QVBoxLayout) -> None:
        """Escolha do motor de tradução, com links de cadastro e campos para a chave."""
        titulo = QLabel("Motor de tradução")
        titulo.setStyleSheet("color: white; font-size: 14px; font-weight: bold; border: none;")
        layout.addWidget(titulo)
        layout.addLayout(self._envolver_em_layout("Motor:", self.combo_motor))

        for rotulo in (self.label_descricao_motor, self.label_links_motor, self.label_teste):
            rotulo.setWordWrap(True)
            rotulo.setStyleSheet(ESTILO_TEXTO_AJUDA)
        self.label_links_motor.setTextFormat(Qt.TextFormat.RichText)
        self.label_links_motor.setOpenExternalLinks(True)
        layout.addWidget(self.label_descricao_motor)
        layout.addWidget(self.label_links_motor)

        for campo, texto in ROTULOS_CAMPOS.items():
            entrada = QLineEdit()
            linha = QWidget()
            layout_linha = QHBoxLayout(linha)
            layout_linha.setContentsMargins(0, 0, 0, 0)
            rotulo = QLabel(texto)
            rotulo.setStyleSheet("color: #DDD; font-size: 13px; border: none;")
            layout_linha.addWidget(rotulo)
            layout_linha.addWidget(entrada)

            if campo == "chave":
                entrada.setEchoMode(QLineEdit.EchoMode.Password)
                entrada.setPlaceholderText("Cole aqui a chave depois do cadastro")
                btn_mostrar = QPushButton("Mostrar")
                btn_mostrar.setCheckable(True)
                getattr(btn_mostrar.toggled, "connect")(
                    lambda visivel, e=entrada: e.setEchoMode(
                        QLineEdit.EchoMode.Normal if visivel else QLineEdit.EchoMode.Password
                    )
                )
                layout_linha.addWidget(btn_mostrar)
            else:
                entrada.setPlaceholderText("Ex.: brazilsouth, eastus ou global")

            getattr(entrada.textEdited, "connect")(
                lambda valor, c=campo: self._guardar_campo(c, valor)
            )
            layout.addWidget(linha)
            self.campos_motor.update({campo: (linha, entrada)})

        layout_teste = QHBoxLayout()
        getattr(self.btn_testar.clicked, "connect")(self.testar_motor)
        layout_teste.addWidget(self.btn_testar)
        layout_teste.addStretch()
        layout.addLayout(layout_teste)
        layout.addWidget(self.label_teste)

        getattr(self.resultado_teste, "connect")(self._mostrar_resultado_teste)
        getattr(self.combo_motor.currentIndexChanged, "connect")(self._atualizar_secao_motor)
        self._atualizar_secao_motor()

    def _atualizar_secao_motor(self) -> None:
        """Mostra a descrição, os links e só os campos que o motor escolhido usa."""
        motor = self.combo_motor.currentData()
        info = MOTORES[motor]
        self.label_descricao_motor.setText(info.descricao)
        self.label_links_motor.setText(
            "  ·  ".join(
                f'<a href="{url}" style="color: #4FC3F7;">{texto}</a>' for texto, url in info.links
            )
        )
        self.label_links_motor.setVisible(bool(info.links))

        valores = self.credenciais.get(motor, {})
        for campo, (linha, entrada) in self.campos_motor.items():
            linha.setVisible(campo in info.campos)
            entrada.setText(valores.get(campo, ""))
        self.label_teste.clear()

    def _guardar_campo(self, campo: str, valor: str) -> None:
        """Guarda o que o usuário digitou na chave/região do motor escolhido."""
        motor = self.combo_motor.currentData()
        self.credenciais.setdefault(motor, {})[campo] = valor.strip()

    def testar_motor(self) -> None:
        """Traduz uma frase curta só com o motor escolhido, sem cair para as reservas."""
        self.btn_testar.setEnabled(False)
        self.label_teste.setText("Testando...")
        threading.Thread(
            target=self._executar_teste,
            args=(
                self.combo_motor.currentData(),
                self.combo_destino.currentData() or "pt",
                dict(self.credenciais),
            ),
            daemon=True,
        ).start()

    def _executar_teste(self, motor: str, destino: str, credenciais: dict) -> None:
        """Roda em outra thread: não mexe em widgets, só emite o resultado."""
        try:
            traducao = traduzir_com(motor, FRASE_TESTE, "en", destino, credenciais)
            self.resultado_teste.emit(f"Funcionou: {traducao}")
        except ErroMotor as erro:
            self.resultado_teste.emit(f"Não funcionou: {erro}")

    def _mostrar_resultado_teste(self, texto: str) -> None:
        self.label_teste.setText(texto)
        self.btn_testar.setEnabled(True)

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
        self._selecionar_por_texto(self.combo_origem, texto_origem)
        self._selecionar_por_texto(self.combo_destino, texto_destino)

    @staticmethod
    def _selecionar_por_texto(combo: QComboBox, texto: str) -> None:
        """Seleciona o item pelo nome.

        Num combo editável, setCurrentText só troca o texto digitado e deixa o item
        selecionado como estava: o currentData() continuava "en" mesmo mostrando
        "Português", e o app salvava o destino errado.
        """
        indice = combo.findText(texto)
        if indice >= 0:
            combo.setCurrentIndex(indice)

    def _envolver_em_layout(self, texto: str, combo: QWidget) -> QHBoxLayout:
        """Envolve um label e um combo em um layout horizontal padronizado."""
        h_layout = QHBoxLayout()
        lbl = QLabel(texto)
        lbl.setStyleSheet("color: #DDD; font-size: 13px; border: none;")
        h_layout.addWidget(lbl)
        h_layout.addWidget(combo)
        return h_layout
