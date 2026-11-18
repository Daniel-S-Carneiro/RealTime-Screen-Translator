"""Abas de uma palavra encostadas, separadas pelo fundo da aba selecionada.

As imagens são desenhadas aqui: fundo escuro, um retângulo mais claro atrás da aba
selecionada e traços de "tinta" dentro de cada caixa. Não há print de jogo nos testes.
"""

import unittest

import numpy as np

from processador_texto import pipeline_processamento
from tests.casos_paragrafos import caixa

FUNDO = 30
SELECIONADA = 60
TINTA = 200


def tela(caixas, destacadas=(), largura=700, altura=120):
    """Print em cinza com as caixas; as de índice em 'destacadas' ganham fundo mais claro."""
    img = np.full((altura, largura), FUNDO, dtype=np.uint8)
    for k, (pontos, _texto, _conf) in enumerate(caixas):
        (x0, y0), (x1, y1) = pontos[0], pontos[2]
        if k in destacadas:
            img[max(0, y0 - 4):y1 + 4, max(0, x0 - 6):x1 + 6] = SELECIONADA
        # tinta: duas faixas finas, bem menos que metade da caixa
        meio = (y0 + y1) // 2
        img[meio - 4:meio - 2, x0 + 2:x1 - 2] = TINTA
        img[meio + 2:meio + 4, x0 + 2:x1 - 2] = TINTA
    return img


def montar(caixas, idioma="en", imagem=None):
    """Texto que o app monta, uma linha por parágrafo."""
    return pipeline_processamento(caixas, idioma, imagem=imagem).splitlines()


class TestAbasPeloFundo(unittest.TestCase):
    """A aba selecionada tem fundo próprio; uma frase tem o mesmo fundo em tudo."""

    def test_duas_abas_com_a_primeira_selecionada(self):
        """Abas Browse e Quickbar encostadas, com Browse selecionada."""
        caixas = [caixa(20, 40, 60, "Browse"), caixa(84, 40, 80, "Quickbar")]
        self.assertEqual(montar(caixas, imagem=tela(caixas, {0})), ["Browse", "Quickbar"])

    def test_sem_imagem_fica_como_antes(self):
        """Sem o print, a regra do fundo não roda."""
        caixas = [caixa(20, 40, 60, "Browse"), caixa(84, 40, 80, "Quickbar")]
        self.assertEqual(montar(caixas), ["Browse Quickbar"])

    def test_tres_abas_com_a_do_meio_selecionada(self):
        """A selecionada pode ser qualquer uma da fileira."""
        caixas = [caixa(20, 40, 70, "General"), caixa(94, 40, 60, "Mining"),
                  caixa(160, 40, 64, "WarpTo")]
        self.assertEqual(montar(caixas, imagem=tela(caixas, {1})), ["General", "Mining", "WarpTo"])

    def test_frase_com_fundo_igual_fica_junta(self):
        """Nome de duas palavras lido em duas caixas, mesmo fundo."""
        caixas = [caixa(20, 40, 70, "Black"), caixa(98, 40, 70, "Reach")]
        self.assertEqual(montar(caixas, imagem=tela(caixas)), ["Black Reach"])

    def test_palavra_minuscula_e_de_frase(self):
        """Palavra só minúscula é de frase, mesmo com uma palavra destacada."""
        caixas = [caixa(20, 40, 60, "Open"), caixa(86, 40, 40, "the"), caixa(132, 40, 60, "Gate")]
        self.assertEqual(montar(caixas, imagem=tela(caixas, {2})), ["Open the Gate"])

    def test_pontuacao_e_de_frase(self):
        """Fala em maiúsculas com apóstrofo, uma palavra destacada."""
        caixas = [caixa(20, 40, 60, "IT'S"), caixa(86, 40, 70, "BEEN"),
                  caixa(162, 40, 80, "EIGHT"), caixa(248, 40, 70, "DAYS")]
        self.assertEqual(montar(caixas, imagem=tela(caixas, {2})), ["IT'S BEEN EIGHT DAYS"])

    def test_vao_de_item_continua_na_regra_antiga(self):
        """Com vão de 0,8 altura ou mais, quem decide é a regra de itens, não o fundo."""
        caixas = [caixa(20, 40, 70, "Black"), caixa(120, 40, 70, "Reach")]
        self.assertEqual(montar(caixas, imagem=tela(caixas, {0})), montar(caixas))

    def test_japones_sem_maiuscula(self):
        """Escrita sem maiúscula: decide só o fundo."""
        caixas = [caixa(20, 40, 60, "設定"), caixa(84, 40, 60, "音声")]
        self.assertEqual(montar(caixas, "ja", tela(caixas, {0})), ["設定", "音声"])

    def test_arabe_espelhado(self):
        """Da direita para a esquerda: a aba da direita vem primeiro, e o fundo tem de cair
        na caixa certa mesmo com as caixas espelhadas."""
        caixas = [caixa(300, 40, 60, "الصوت"), caixa(364, 40, 90, "الإعدادات")]
        self.assertEqual(montar(caixas, "ar", tela(caixas, {1})), ["الإعدادات", "الصوت"])

    def test_arabe_com_fundo_igual_fica_junto(self):
        """Árabe sem destaque continua numa linha."""
        caixas = [caixa(300, 40, 60, "الصوت"), caixa(364, 40, 90, "الإعدادات")]
        self.assertEqual(len(montar(caixas, "ar", tela(caixas))), 1)


if __name__ == "__main__":
    unittest.main()
