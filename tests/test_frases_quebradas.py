"""Frase ou rótulo quebrado de propósito em linhas curtas e coladas (problema 15, 25/11/2026).

As coordenadas do formulário do Stardew Valley, do letreiro e da anotação do The Big Con, da
lista do Pip-Boy, da dica do Disco Elysium e do objetivo da missão do Immortal Clan são as
dos prints. As linhas de contexto (os outros itens da lista, a linha de baixo da missão) e
os casos que têm de continuar separados são desenhados para cada trava. Cada teste tem,
longe, uma linha larga (CONTEXTO): nos prints, o letreiro e o formulário são bem mais
estreitos que a tela, e é por isso que o "caberia" os separava.
"""

import unittest

from paragrafos import montar_paragrafos
from tests.casos_paragrafos import caixa


def linha(esq, topo, dir_, base, texto):
    """Caixa pelas bordas, como nos dados da pergunta (x início-fim, y topo-base)."""
    return caixa(esq, topo, dir_ - esq, texto, base - topo)


CONTEXTO = linha(40, 900, 1200, 934, "Press any key to continue")


def montar(caixas, idioma="en"):
    """Os parágrafos sem o da linha de contexto."""
    return [p for p in montar_paragrafos(caixas + [CONTEXTO], idioma)
            if p != "Press any key to continue"]


class TestJunta(unittest.TestCase):
    """O que o gabarito junta."""

    def test_rotulos_do_formulario(self):
        """Stardew Valley, em espanhol: a palavra minúscula sobreposta continua o rótulo;
        "Tu cosa" começa outro rótulo, mesmo encostado em "la granja"."""
        caixas = [linha(244, 117, 382, 151, "Nombre de"), linha(244, 147, 364, 180, "la granja"),
                  linha(252, 180, 359, 214, "Tu cosa"), linha(252, 210, 358, 240, "favorita"),
                  linha(257, 253, 385, 286, "Tu animal"), linha(256, 281, 377, 315, "preferido"),
                  linha(261, 408, 371, 443, "Color de"), linha(259, 438, 323, 471, "pelo:")]
        self.assertEqual(montar(caixas, "es"),
                         ["Nombre de la granja", "Tu cosa favorita", "Tu animal preferido",
                          "Color de pelo:"])

    def test_letreiro_centralizado(self):
        """The Big Con: três linhas curtas, centralizadas e sobrepostas."""
        caixas = [linha(827, 404, 951, 446, "REWIND"), linha(852, 437, 920, 470, "FOR"),
                  linha(805, 461, 945, 508, "HUMANKIND!")]
        self.assertEqual(montar(caixas), ["REWIND FOR HUMANKIND!"])

    def test_item_que_quebrou_na_lista(self):
        """Fallout New Vegas: só "Mercenary's Grenade / Rifle" tem o passo curto. No print
        inteiro, o app separava o par e só a regra nova o juntou; aqui, com a lista sozinha,
        a regra dos itens em duas linhas também o junta. O teste garante que os outros
        itens continuam separados."""
        caixas = [linha(164, 324, 344, 363, "Laser Pistol"),
                  linha(194, 373, 442, 413, "Mercenary's Grenade"),
                  linha(194, 409, 266, 445, "Rifle"),
                  linha(196, 456, 481, 498, "Sturdy Caravan Shotgun"),
                  linha(196, 507, 430, 545, "Hunting Revolver"),
                  linha(196, 556, 380, 594, "Varmint Rifle")]
        paragrafos = montar(caixas)
        self.assertIn("Mercenary's Grenade Rifle", paragrafos)
        self.assertIn("Sturdy Caravan Shotgun", paragrafos)
        self.assertIn("Laser Pistol", paragrafos)

    def test_cauda_em_maiusculas(self):
        """Disco Elysium: a dica longa, com aspas, e a cauda curta embaixo."""
        caixas = [linha(466, 344, 716, 361, 'TAP "Q" OR "L" TO SEAMLESSLY SWITCH'),
                  linha(465, 362, 602, 379, "LANGUAGES IN GAME")]
        self.assertEqual(montar(caixas),
                         ['TAP "Q" OR "L" TO SEAMLESSLY SWITCH LANGUAGES IN GAME'])

    def test_objetivo_com_quantidade(self):
        """Immortal Clan: o objetivo da missão não coube na caixa, e a quantidade, que
        começa com "x" minúsculo, continua o item (releitura dos gabaritos, 26/11)."""
        caixas = [caixa(39, 100, 177, "Harvest Magic Paper", 31),
                  caixa(38, 126, 213, "x300,000(152K/300K)", 31),
                  caixa(39, 300, 600, "Achieve the daily goal to unlock the chapter reward", 31)]
        self.assertIn("Harvest Magic Paper x300,000(152K/300K)", montar(caixas))


class TestSepara(unittest.TestCase):
    """O que tem de continuar separado, mesmo colado."""

    def test_atributo_com_multiplicador(self):
        """Morrowind, desenhado colado: "x2 Willpower 40" começa com minúscula, mas tem
        mais de uma palavra; é outro atributo, não o fim da linha de cima."""
        caixas = [caixa(40, 100, 150, "Intelligence 42", 30),
                  caixa(40, 126, 160, "x2 Willpower 40", 30),
                  caixa(40, 300, 600, "Affects your ability to dodge and hit targets", 30)]
        paragrafos = montar(caixas)
        self.assertIn("Intelligence 42", paragrafos)
        self.assertIn("x2 Willpower 40", paragrafos)

    def test_topicos_de_uma_palavra(self):
        """Morrowind: tópico minúsculo embaixo de outro tópico de uma palavra."""
        caixas = [caixa(20, 40, 100, "Dwarves", 30), caixa(20, 66, 80, "duties", 30),
                  caixa(20, 92, 70, "rules", 30),
                  caixa(20, 200, 600, "Hmm... Duties, you say? Ask me about the rules.", 30)]
        paragrafos = montar(caixas)
        for topico in ("Dwarves", "duties", "rules"):
            self.assertIn(topico, paragrafos)

    def test_menu_centralizado_com_respiro(self):
        """Três opções centralizadas, curtas, com vão positivo: menu, não letreiro."""
        caixas = [caixa(70, 40, 100, "NEW GAME", 30), caixa(85, 74, 70, "LOAD", 30),
                  caixa(60, 108, 120, "SETTINGS", 30)]
        self.assertEqual(montar(caixas), ["NEW GAME", "LOAD", "SETTINGS"])

    def test_item_de_lista_so_encostado(self):
        """Disco Elysium: tarefas da mesma lista, encostadas (-0,08), cada uma um item."""
        caixas = [caixa(20, 40, 260, "Interview the Union boss", 30),
                  caixa(20, 68, 230, "Perform field autopsy", 30),
                  caixa(20, 96, 280, "Read your ledger and name the case", 30)]
        paragrafos = montar(caixas)
        self.assertIn("Perform field autopsy", paragrafos)


if __name__ == "__main__":
    unittest.main()
