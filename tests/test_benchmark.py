"""Testes das métricas do benchmark que não dependem dos prints."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "benchmark"))
# pylint: disable=wrong-import-position,import-error,no-name-in-module
from benchmark import (  # noqa: E402
    acerto_quebras, cer_sem_ordem, linhas_inteiras, normalizar, taxa_erro_caracteres,
)


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



class TestCerSemOrdem(unittest.TestCase):
    """Letras com as linhas lidas na ordem do gabarito: só a ordem entre linhas sai da conta."""

    GABARITO = "Here is a summary of your character\nStrength 22\nAgility 18"

    def cer(self, lido):
        """O CER de sempre, para comparar."""
        return taxa_erro_caracteres(normalizar(self.GABARITO), normalizar(lido))

    def test_paineis_em_outra_ordem_nao_contam(self):
        """Os mesmos painéis lidos em outra ordem: erro zero, e o CER de sempre não."""
        lido = "Strength 22\nAgility 18\nHere is a summary of your character"
        self.assertGreater(self.cer(lido), 0)
        self.assertEqual(cer_sem_ordem(self.GABARITO, lido), 0)

    def test_letra_trocada_continua_contando(self):
        """Uma letra errada pesa o mesmo nas duas medidas."""
        na_ordem = "Here is a summary of your character\nStrength 22\nAgi1ity 18"
        fora_de_ordem = "Strength 22\nAgi1ity 18\nHere is a summary of your character"
        self.assertAlmostEqual(cer_sem_ordem(self.GABARITO, fora_de_ordem), self.cer(na_ordem))
        self.assertGreater(cer_sem_ordem(self.GABARITO, fora_de_ordem), 0)

    def test_lixo_e_texto_que_falta_continuam_contando(self):
        """Linha de lixo e linha que o OCR não leu continuam sendo erro."""
        self.assertGreater(cer_sem_ordem(self.GABARITO, self.GABARITO + "\nXQZWV KJH"), 0)
        self.assertGreater(cer_sem_ordem(self.GABARITO, "Strength 22\nAgility 18"), 0)

    def test_nunca_passa_do_cer_de_sempre(self):
        """Se reordenar piorar, vale o CER de sempre."""
        for lido in ("Strength 22 Agility 18", "Agility\n18 Strength\n22 Here", "", "x"):
            self.assertLessEqual(cer_sem_ordem(self.GABARITO, lido), self.cer(lido) + 1e-12)


if __name__ == "__main__":
    unittest.main()
