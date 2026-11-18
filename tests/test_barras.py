"""Barra de menu que o OCR lê numa caixa só, separada pelo espaço medido na tinta.

As telas são desenhadas aqui: cada palavra é um bloco de "tinta" no meio da caixa, com o
espaço entre palavras escolhido em alturas da caixa. Não há print de jogo nos testes.
"""

import unittest

import numpy as np

from processador_texto import pipeline_processamento
from tests.casos_paragrafos import caixa

FUNDO = 150
TINTA = 70
LARGURA_LETRA = 9
TRACO = 5  # cada letra é um traço vertical de 5 px, com 4 px até a próxima


def escrever(img, x, y, altura, palavras, espaco):  # pylint: disable=too-many-arguments,too-many-positional-arguments
    """Desenha as palavras e devolve a caixa do OCR que cobre a linha. espaco é o espaço
    entre palavras em alturas da caixa (um número, ou um por espaço)."""
    espacos = espaco if isinstance(espaco, list) else [espaco] * (len(palavras) - 1)
    inicio = x
    meio = y + altura // 2
    for k, palavra in enumerate(palavras):
        for letra in range(len(palavra)):
            img[meio - altura // 5:meio + altura // 5, x + letra * LARGURA_LETRA:
                x + letra * LARGURA_LETRA + TRACO] = TINTA
        x += LARGURA_LETRA * len(palavra) - (LARGURA_LETRA - TRACO)
        if k < len(palavras) - 1:
            x += int(round(espacos[k] * altura))
    return caixa(inicio, y, x - inicio, " ".join(palavras), altura)


def tela(linhas, largura=1200, altura=400):
    """linhas: [(x, y, altura, texto, espaço em alturas)]. Devolve (imagem, caixas)."""
    img = np.full((altura, largura), FUNDO, dtype=np.uint8)
    caixas = [escrever(img, x, y, alt, txt.split(), espaco) for x, y, alt, txt, espaco in linhas]
    return img, caixas


FALA = [
    (40, 20, 45, "she might be an airhead but sometimes it is weird", 0.18),
    (40, 75, 45, "she knows exactly what she is doing here", 0.17),
]
BARRA = "History Skip Auto Save Load Settings"


def montar(img, caixas):
    """Texto que o app monta, uma linha por parágrafo."""
    return pipeline_processamento(caixas, "en", imagem=img).splitlines()


class TestBarraDeMenu(unittest.TestCase):
    """Cada item vira uma linha só quando o espaço da barra passa bem do espaço da fala."""

    def test_barra_com_fala_no_print(self):
        """Barra com espaço de 0,4 altura e fala com 0,18: cada item numa linha."""
        img, caixas = tela(FALA + [(300, 200, 30, BARRA, 0.40)])
        saida = montar(img, caixas)
        for item in BARRA.split():
            self.assertIn(item, saida)

    def test_sem_imagem_fica_como_antes(self):
        """Sem o print, a barra continua numa linha."""
        _img, caixas = tela(FALA + [(300, 200, 30, BARRA, 0.40)])
        self.assertIn(BARRA, pipeline_processamento(caixas, "en").splitlines())

    def test_titulo_com_espaco_da_fala_fica_junto(self):
        """Título de 6 palavras com o mesmo espaço da fala: uma linha."""
        titulo = "The Legend Of Seven Golden Swords"
        img, caixas = tela(FALA + [(300, 200, 30, titulo, 0.18)])
        self.assertIn(titulo, montar(img, caixas))

    def test_sem_fala_no_print_nao_corta(self):
        """Sem fala para comparar, não há referência: a barra fica junta."""
        img, caixas = tela([(300, 200, 30, BARRA, 0.40)])
        self.assertIn(BARRA, montar(img, caixas))

    def test_fala_de_espaco_largo_nao_deixa_cortar(self):
        """Num jogo de fonte larga (fala a 0,6), um espaço de 0,4 não é grande."""
        fala_larga = [(x, y, alt, texto, 0.6) for x, y, alt, texto, _ in FALA]
        img, caixas = tela(fala_larga + [(300, 200, 30, BARRA, 0.40)])
        self.assertIn(BARRA, montar(img, caixas))

    def test_item_de_duas_letras_nao_passa(self):
        """Barra com "OK": fica junta (itens de 3 letras ou mais)."""
        barra = "History Skip Auto Save Load OK"
        img, caixas = tela(FALA + [(300, 200, 30, barra, 0.40)])
        self.assertIn(barra, montar(img, caixas))

    def test_um_espaco_grande_no_meio_nao_corta(self):
        """Slogan com um espaço grande e os outros normais: decide o menor espaço."""
        slogan = "Daily Earnings How Enviable Limit Rewards"
        img, caixas = tela(FALA + [(300, 200, 30, slogan, [0.18, 0.5, 0.18, 0.5, 0.18])])
        self.assertIn(slogan, montar(img, caixas))


if __name__ == "__main__":
    unittest.main()
