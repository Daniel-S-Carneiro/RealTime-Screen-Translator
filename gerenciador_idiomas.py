"""Módulo responsável pela interface de gerenciamento e adição de novos idiomas."""

import json
from typing import Dict, Callable
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QCheckBox,
    QScrollArea,
    QPushButton,
)
from PySide6.QtCore import Qt  # Import necessário para o atributo da janela


class JanelaGerenciarIdiomas(QWidget):
    """Janela para pesquisa e seleção de idiomas adicionais suportados."""

    def __init__(
        self, lista_total: Dict[str, str], callback_fechar: Callable[[], None]
    ) -> None:
        super().__init__()
        self.lista_total = lista_total  # Lista com todos os idiomas suportados
        self.callback_fechar = callback_fechar
        self.setWindowTitle("Selecionar Novos Idiomas")

        # 1. A SOLUÇÃO DO CRASH: Impede que fechar esta janela mate o app inteiro
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)
        # Garante que ela se comporte como uma janela independente
        self.setWindowFlag(Qt.WindowType.Window)

        # Tipagem antecipada para evitar alertas do Linter
        self.search_bar: QLineEdit
        self.scroll_area: QScrollArea
        self.container: QWidget
        self.vbox: QVBoxLayout
        self.checkboxes: Dict[str, QCheckBox] = {}

        self.init_ui()

    def init_ui(self) -> None:
        """Inicializa os componentes visuais da janela."""
        layout = QVBoxLayout(self)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Pesquisar idioma...")
        getattr(self.search_bar.textChanged, "connect")(self.filtrar)
        layout.addWidget(self.search_bar)

        self.scroll_area = QScrollArea()
        self.container = QWidget()
        self.vbox = QVBoxLayout(self.container)
        self.vbox.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 2. Verifica quais línguas já estão salvas no JSON para marcá-las
        ja_salvos = {}
        try:
            with open("idiomas.json", "r", encoding="utf-8") as f:
                ja_salvos = json.load(f).get("outros", {})
        except (FileNotFoundError, json.JSONDecodeError):
            pass

        self.checkboxes = {}
        for nome, _ in self.lista_total.items():
            cb = QCheckBox(nome)
            # Se o idioma já estiver no JSON, o checkbox começa marcado
            if nome in ja_salvos:
                cb.setChecked(True)

            self.vbox.addWidget(cb)
            self.checkboxes[nome] = cb

        self.scroll_area.setWidget(self.container)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)

        btn_salvar = QPushButton("Salvar e Voltar")
        getattr(btn_salvar.clicked, "connect")(self.salvar)
        layout.addWidget(btn_salvar)

    def filtrar(self, text: str) -> None:
        """Filtra os checkboxes exibidos com base no texto digitado na pesquisa."""
        for nome, cb in self.checkboxes.items():
            cb.setVisible(text.lower() in nome.lower())

    def salvar(self) -> None:
        """Salva os idiomas selecionados no arquivo json e fecha a janela."""
        selecionados = {
            nome: self.lista_total[nome]
            for nome, cb in self.checkboxes.items()
            if cb.isChecked()
        }

        # 3. Leitura e Gravação Segura
        try:
            with open("idiomas.json", "r", encoding="utf-8") as f:
                dados = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Se o arquivo não existir ou estiver corrompido, cria uma base limpa
            dados = {"mais_usados": {}, "outros": {}}

        dados["outros"] = selecionados

        # Salva o arquivo inteiro do zero (modo "w")
        with open("idiomas.json", "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4)

        # Atualiza a interface principal
        self.callback_fechar()

        # Fecha apenas esta janela
        self.close()

    def closeEvent(self, event) -> None:
        """Sobrescreve o evento de fechar no 'X' para garantir que a UI principal atualize."""
        # Opcional: Se quiser que fechar no 'X' não salve as novas seleções,
        # basta remover a linha self.callback_fechar() daqui de baixo.
        # Mas mantemos para garantir que os combos na tela principal não quebrem.
        self.callback_fechar()
        event.accept()
