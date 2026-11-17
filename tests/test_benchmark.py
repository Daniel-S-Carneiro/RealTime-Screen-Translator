"""Testes das métricas do benchmark que não dependem dos prints."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "benchmark"))
# pylint: disable=wrong-import-position,import-error,no-name-in-module
from benchmark import acerto_quebras, linhas_inteiras  # noqa: E402


class TestLinhasInteiras(unittest.TestCase):
    """Cada linha do gabarito com 2+ palavras sai inteira, com sobra, partida ou faltando."""

    GABARITO = "Skill Plans\nSkill Catalogue\nStrength 65\nSave Changes"

    def test_tudo_inteiro(self):
        """Cada linha do gabarito sai sozinha numa linha."""
        lido = "Skill Plans\nSkill Catalogue\nStrength 65\nSave Changes"
        self.assertEqual(
            linhas_inteiras(self.GABARITO, lido),
            {"inteira": 4, "com_sobra": 0, "partida": 0, "faltando": 0},
        )

    def test_quebra_perdida_conta_como_sobra(self):
        """Duas linhas do gabarito na mesma linha: as duas têm sobra."""
        lido = "Skill Plans Skill Catalogue\nStrength 65\nSave Changes"
        self.assertEqual(linhas_inteiras(self.GABARITO, lido)["com_sobra"], 2)

    def test_quebra_a_mais_conta_como_partida(self):
        """Uma linha do gabarito cortada em duas."""
        lido = "Skill Plans\nSkill Catalogue\nStrength\n65\nSave Changes"
        self.assertEqual(linhas_inteiras(self.GABARITO, lido)["partida"], 1)

    def test_palavra_nao_lida_conta_como_faltando(self):
        """Uma palavra que o OCR não leu."""
        lido = "Skill Plans\nSkill Catalogue\nStrength 65\nSave"
        self.assertEqual(linhas_inteiras(self.GABARITO, lido)["faltando"], 1)

    def test_linha_de_uma_palavra_nao_conta(self):
        """Linhas de uma palavra só ficam fora da conta."""
        self.assertEqual(sum(linhas_inteiras("Skills\nArmor 2", "Skills\nArmor 2").values()), 1)


class TestQuebras(unittest.TestCase):
    """(quebras certas, quebras postas, quebras do gabarito)."""

    def test_quebras_certas_e_a_mais(self):
        """Uma quebra certa, uma a mais e uma perdida."""
        self.assertEqual(acerto_quebras("a b\nc d\ne f", "a b\nc\nd e f"), (1, 2, 2))


if __name__ == "__main__":
    unittest.main()
