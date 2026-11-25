"""Barra de menu com itens de uma ou duas palavras, lida numa caixa só, cortada pelos
espaços entre as palavras do reconhecedor (problema 11, 25/11/2026).

As caixas são desenhadas aqui, com o 4º elemento que o RapidOCR entrega: as palavras e o x
de cada uma. Os espaços estão em alturas da caixa; os de "New Game" e "Act 1" são os
medidos no Butterfly Soup e no Katawa Shoujo, com o ruído do reconhecedor ("Load Game"
leu 0,09). Os outros casos são hipotéticos, desenhados para cada trava.
"""

import unittest
from types import SimpleNamespace

from ocr_engine import _palavras_do_texto, _palavras_por_caixa
from paragrafos import montar_paragrafos
from tests.casos_paragrafos import caixa

LETRA = 14  # largura de uma letra, em px


def barra(palavras, espacos, x=40, y=40, altura=60):
    """Caixa de uma linha com as palavras do reconhecedor; espacos em alturas da caixa."""
    lidas, inicio = [], x
    for k, palavra in enumerate(palavras):
        fim = inicio + LETRA * len(palavra)
        lidas.append((palavra, float(inicio), float(fim)))
        if k < len(espacos):
            inicio = fim + espacos[k] * altura
    largura = int(lidas[-1][2] - x) + 10
    return caixa(x - 5, y, largura, " ".join(palavras), altura) + (tuple(lidas),)


class TestMenuPelasPalavras(unittest.TestCase):
    """Corta só a barra: espaços em dois grupos, 3+ grandes e regulares, itens curtos."""

    def test_menu_do_titulo_com_itens_de_duas_palavras(self):
        """Menu do título do Butterfly Soup: cada item numa linha, "New Game" inteiro."""
        item = barra("New Game Load Game Settings About Quit".split(),
                     [0.25, 0.75, 0.09, 0.75, 0.75, 0.74])
        self.assertEqual(montar_paragrafos([item], "en"),
                         ["New Game", "Load Game", "Settings", "About", "Quit"])

    def test_abas_com_numero(self):
        """Abas do Katawa Shoujo: "Act 1" fica junto no espaço pequeno."""
        item = barra("Act 1 Emi Hanako Lilly Rin Shizune".split(),
                     [0.17, 0.62, 0.48, 0.65, 0.62, 0.79])
        self.assertEqual(montar_paragrafos([item], "en"),
                         ["Act 1", "Emi", "Hanako", "Lilly", "Rin", "Shizune"])

    def test_sem_as_palavras_fica_como_antes(self):
        """Caixa sem as palavras do reconhecedor (EasyOCR): a barra continua numa linha."""
        item = barra("New Game Load Game Settings About Quit".split(),
                     [0.25, 0.75, 0.09, 0.75, 0.75, 0.74])[:3]
        self.assertEqual(montar_paragrafos([item], "en"),
                         ["New Game Load Game Settings About Quit"])

    def test_item_com_minuscula_nao_corta(self):
        """Pedaço que começa com minúscula é frase, não item."""
        # Fonte de largura fixa: os espaços de uma frase alternam (Caves of Qud)
        item = barra("Total skill points per level".split(), [0.15, 0.5, 0.5, 0.5])
        self.assertEqual(montar_paragrafos([item], "en"), ["Total skill points per level"])

    def test_tres_itens_nao_cortam(self):
        """Um espaço grande só (três pedaços ou menos) não é barra."""
        # Um espaço grande no meio de pequenos: título ("Become Investor Enjoy Privileges")
        item = barra("Become Investor Enjoy Privileges".split(), [0.16, 0.47, 0.16])
        self.assertEqual(montar_paragrafos([item], "en"), ["Become Investor Enjoy Privileges"])

    def test_espacos_grandes_irregulares_nao_cortam(self):
        """Espaços grandes com mais de 2x de diferença entre si não são de uma barra."""
        item = barra("Open Map Quest Log Inventory Help".split(), [0.15, 0.5, 0.15, 0.5, 1.2])
        self.assertEqual(montar_paragrafos([item], "en"),
                         ["Open Map Quest Log Inventory Help"])

    def test_item_com_virgula_nao_corta(self):
        """Lista de frase separada por vírgula fica junta."""
        item = barra("Red, Green, Blue, Yellow".split(), [0.6, 0.6, 0.6])
        self.assertEqual(montar_paragrafos([item], "en"), ["Red, Green, Blue, Yellow"])

    def test_item_de_tres_palavras_nao_corta(self):
        """Item de três palavras: a regra desiste, em vez de cortar o item ao meio."""
        item = barra("New Game Plus Load Game Quit Now".split(),
                     [0.2, 0.2, 0.7, 0.2, 0.7, 0.7])
        self.assertEqual(montar_paragrafos([item], "en"), ["New Game Plus Load Game Quit Now"])


class TestPalavrasDoRapidOCR(unittest.TestCase):
    """As palavras do RapidOCR casam com a caixa pelo texto, não pela posição na lista."""

    @staticmethod
    def palavra(texto, x0, x1):
        """Uma palavra como o RapidOCR entrega: (texto, confiança, 4 cantos)."""
        return (texto, 0.99, [[x0, 0], [x1, 0], [x1, 10], [x0, 10]])

    def test_caixa_sem_palavras_nao_desalinha_as_outras(self):
        """A lista do RapidOCR pula a caixa sem palavras; as seguintes continuam certas."""
        new_game = (self.palavra("New", 0, 30), self.palavra("Game", 35, 70))
        load = (self.palavra("Load", 0, 30),)
        saida = SimpleNamespace(txts=("New Game", "OK", "Load"), word_results=(new_game, load))
        self.assertEqual(_palavras_por_caixa(saida), [new_game, None, load])

    def test_palavras_viram_texto_e_x(self):
        """Cada palavra vira (texto, x inicial, x final)."""
        palavras = (self.palavra("New", 2, 30), self.palavra("Game", 35, 70))
        self.assertEqual(_palavras_do_texto(palavras, "New Game"),
                         (("New", 2.0, 30.0), ("Game", 35.0, 70.0)))

    def test_texto_limpo_diferente_descarta_as_palavras(self):
        """Se as palavras não formam o texto limpo da caixa, ficam de fora."""
        # A limpeza do app tirou um caractere chinês lido no lugar de um ícone
        palavras = (self.palavra("口", 0, 10), self.palavra("Sword", 15, 60))
        self.assertIsNone(_palavras_do_texto(palavras, "Sword"))


if __name__ == "__main__":
    unittest.main()
