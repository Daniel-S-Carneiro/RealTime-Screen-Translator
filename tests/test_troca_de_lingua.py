"""Troca de língua do motor de OCR quando o carregamento falha, sem carregar modelo nenhum."""

import unittest
from unittest import mock

from ocr_engine import MotorOCR


def motor_em_ingles():
    """Um motor em inglês, sem criar o RapidOCR de verdade."""
    with mock.patch("ocr_engine.criar_rapidocr", return_value=object()):
        return MotorOCR(idiomas=["en"])


class TestTrocaDeLingua(unittest.TestCase):
    """Se a língua nova não carregar, a anterior continua valendo."""

    def test_falha_mantem_a_lingua_e_o_nome(self):
        """O erro sobe para a tela, e o motor continua como estava."""
        motor = motor_em_ingles()
        nome = motor.nome
        with mock.patch.object(motor, "_carregar", side_effect=OSError("sem internet")):
            with self.assertRaises(OSError):
                motor.alterar_idioma("ru")
        self.assertEqual(motor.idiomas_atuais, ["en"])
        self.assertEqual(motor.nome, nome)

    def test_depois_da_falha_tenta_carregar_de_novo(self):
        """Antes, a 2ª tentativa achava que já estava na língua e não carregava."""
        motor = motor_em_ingles()
        with mock.patch.object(motor, "_carregar", side_effect=OSError("sem internet")):
            with self.assertRaises(OSError):
                motor.alterar_idioma("ru")
        with mock.patch.object(motor, "_carregar") as carregar:
            motor.alterar_idioma("ru")
        carregar.assert_called_once()
        self.assertEqual(motor.idiomas_atuais, ["ru"])

    def test_mesma_lingua_nao_recarrega(self):
        """Salvar a língua atual não carrega nada."""
        motor = motor_em_ingles()
        with mock.patch.object(motor, "_carregar") as carregar:
            motor.alterar_idioma("en")
        carregar.assert_not_called()

    def test_caminho_inexistente_da_erro_claro(self):
        """Um arquivo que não existe não vira AttributeError lá dentro da leitura."""
        motor = motor_em_ingles()
        with self.assertRaises(FileNotFoundError):
            motor.extrair_dados_completos("arquivo_que_nao_existe.png")


if __name__ == "__main__":
    unittest.main()
