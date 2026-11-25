"""Ícones lidos como símbolo e colados à linha (problema 14, 25/11/2026).

As coordenadas da fila de skills do EVE Online, da opção de diálogo do Disco Elysium e das
falas do Caves of Qud e do The Big Con são as dos prints. Os outros casos são hipotéticos,
desenhados para cada trava: o que é texto ("Extras > Library", "4. - Not now.", "A Route",
"x2 Speed 62", o ">" sem atalho) tem de chegar inteiro.
"""

import unittest

from paragrafos import montar_paragrafos
from tests.casos_paragrafos import caixa


def texto(caixas):
    """Tudo o que a montagem entrega, numa string só."""
    return "\n".join(montar_paragrafos(caixas, "en"))


class TestColunaDeIcones(unittest.TestCase):
    """3+ símbolos iguais, um embaixo do outro, cada um colado a um texto."""

    def test_botoes_mais_da_fila_de_skills(self):
        """Os "+" das duas colunas saem; "34m" e "20m" ficam."""
        linhas = ((584, "Amarr", "Sleeper"), (611, "Caldari", "Takmahl"),
                  (665, "Gallente", "Talocan"))
        caixas = []
        for y, esquerda, direita in linhas:
            caixas += [caixa(123, y, 252, f"{esquerda} Encryption Methods 3d 10h 48m", 21),
                       caixa(386, y, 22, "+", 22),
                       caixa(505, y, 130, f"{direita} Technology", 21),
                       caixa(743, y, 39, "34m", 21), caixa(790, y, 24, "+", 22)]
        caixas += [caixa(119, 706, 74, "Metallurgy", 21), caixa(339, 706, 39, "20m", 21),
                   caixa(386, 706, 22, "+", 22),
                   caixa(507, 706, 189, "Triglavian Encryption Methods", 21),
                   caixa(743, 706, 39, "27m", 21), caixa(791, 706, 22, "+", 22)]
        lido = texto(caixas)
        self.assertNotIn("+", lido)
        for valor in ("34m", "20m", "27m", "Sleeper Technology"):
            self.assertIn(valor, lido)

    def test_dois_botoes_ficam(self):
        """Com 2 linhas só, a coluna pode ser de dois valores iguais: fica."""
        caixas = [caixa(20, 40, 200, "Mining Laser Upgrade", 21), caixa(231, 40, 22, "+", 22),
                  caixa(20, 80, 200, "Shield Booster Mk II", 21), caixa(231, 80, 22, "+", 22)]
        self.assertEqual(texto(caixas).count("+"), 2)

    def test_icone_numerico_antes_do_nome_sai(self):
        """Um "8" de ícone antes de cada um de 3 nomes sai (hipotético)."""
        caixas = []
        for k, nome in enumerate(("Lotus Heart", "Drifting Wind", "Iron Skin")):
            caixas += [caixa(119, 40 + 60 * k, 28, "8", 37), caixa(156, 42 + 60 * k, 150, nome, 32)]
        lido = texto(caixas)
        self.assertNotIn("8", lido)
        self.assertIn("Lotus Heart", lido)

    def test_numero_depois_do_rotulo_fica(self):
        """O mesmo dígito depois do rótulo é valor ("Level 8"), mesmo em 3 linhas."""
        caixas = []
        for k, nome in enumerate(("Level", "Rank", "Tier")):
            caixas += [caixa(20, 40 + 40 * k, 70, nome, 30), caixa(98, 40 + 40 * k, 16, "8", 30)]
        self.assertEqual(texto(caixas).count("8"), 3)

    def test_marcadores_de_lista_ficam(self):
        """O "•" no começo de cada item é marcador, não ícone."""
        caixas = []
        for k, item in enumerate(("Fire resistance", "Cold resistance", "Poison resistance")):
            caixas += [caixa(20, 40 + 40 * k, 14, "•", 30), caixa(40, 40 + 40 * k, 220, item, 30)]
        self.assertEqual(texto(caixas).count("•"), 3)

    def test_artigo_em_caixa_propria_fica(self):
        """EasyOCR, uma caixa por palavra: o "A" de 3 linhas é palavra, não ícone. (Como a
        coluna dos "A" se repete, a regra das colunas estreitas a lê à parte; aqui só
        importa que nenhum "A" sai.)"""
        caixas = []
        for k, resto in enumerate(("Route", "Plan", "Key")):
            caixas += [caixa(20, 40 + 40 * k, 16, "A", 30), caixa(45, 40 + 40 * k, 90, resto, 30)]
        self.assertEqual(texto(caixas).split().count("A"), 3)


class TestGlifoLonge(unittest.TestCase):
    """Letra ou símbolo mais baixo que o texto e longe da linha."""

    def test_letra_depois_da_opcao_de_dialogo_sai(self):
        """Disco Elysium: o "A" de 18 px a 131 px (5 alturas) da opção."""
        caixas = [caixa(36, 647, 220, '4. - "I\'ve heard enough."', 26),
                  caixa(387, 651, 17, "A", 18)]
        self.assertEqual(montar_paragrafos(caixas, "en"), ['4. - "I\'ve heard enough."'])

    def test_letra_do_tamanho_do_texto_fica(self):
        """A mesma letra longe, mas da altura do texto, fica (pode ser uma nota: "Rank A")."""
        caixas = [caixa(36, 40, 120, "Final rank", 26), caixa(300, 40, 17, "A", 26)]
        self.assertIn("A", texto(caixas))


class TestPontasDaLinha(unittest.TestCase):
    """O "≡" e o cursor no começo, o enfeite depois do ponto no fim."""

    def test_icone_de_menu(self):
        """EVE Online: o "≡" antes do nome da janela."""
        caixas = [caixa(24, 135, 121, "≡ Overview (General)", 20),
                  caixa(23, 160, 45, "General", 15), caixa(71, 160, 41, "Mining", 15)]
        lido = texto(caixas)
        self.assertIn("Overview (General)", lido)
        self.assertNotIn("≡", lido)

    def test_cursor_antes_do_atalho(self):
        """Caves of Qud: com e sem espaço depois do cursor."""
        for linha in ("> [2] Do you live here?", ">[space] Continue"):
            caixas = [caixa(46, 280, 300, "[1] I am Grug. Who are you?", 20),
                      caixa(46, 322, 222, linha, 20)]
            lido = texto(caixas)
            self.assertNotIn(">", lido, linha)
            self.assertIn(linha.lstrip("> "), lido)

    def test_enfeite_depois_do_ponto(self):
        """The Big Con: "I really gotta quit.*"."""
        caixas = [caixa(618, 40, 189, "ON", 60), caixa(183, 545, 426, "I really gotta quit.*", 40)]
        lido = texto(caixas)
        self.assertIn("I really gotta quit.", lido)
        self.assertNotIn("*", lido)

    def test_texto_com_simbolo_fica(self):
        """O ">" no meio, o ">" sem atalho, o hífen da opção e o "x2" ficam como estão."""
        for linha in ("Extras > Library", "> Obtained Peach Seed x 5.", "4. - Not now.",
                      "x2 Speed 62", "* Fire resistance"):
            caixas = [caixa(20, 40, 300, "Settings and options", 30),
                      caixa(20, 120, 260, linha, 30)]
            self.assertIn(linha, texto(caixas), linha)

    def test_cursor_no_meio_da_linha_fica(self):
        """Caixas separadas: o "> Library" não começa a linha."""
        caixas = [caixa(20, 40, 300, "Settings and options", 30),
                  caixa(20, 120, 80, "Extras", 30), caixa(108, 120, 110, "> Library", 30)]
        self.assertIn("> Library", texto(caixas))


if __name__ == "__main__":
    unittest.main()
