"""O espaço que o reconhecedor engoliu (problema 12, 25/11/2026), com leituras desenhadas.

Cada leitura é uma tabela de probabilidades do CTC feita à mão: uma coluna por letra, com
colunas de "branco" entre elas, e a probabilidade do espaço ajustada na coluna entre duas
letras. Não há modelo nem print nos testes.
"""

import unittest
from types import SimpleNamespace

import numpy as np

from espacos import (
    GravadorDoReconhecedor,
    Leitura,
    espacos_engolidos,
    inserir_espacos,
    leituras_por_caixa,
)

CARACTERES = ["blank"] + list("abcdefghijklmnopqrstuvwxyz'.0123456789") + [" "]
ESPACO = len(CARACTERES) - 1


def leitura(texto, passos, espaco_em=None, margem=-5.0):
    """Leitura de `texto` (sem espaços), com `passos[i]` colunas entre a letra i e a i+1.

    espaco_em: junção (índice da letra de antes) cuja coluna do meio dá ao espaço a
    `margem` dada, em log, contra o branco."""
    colunas = []
    for i, letra in enumerate(texto):
        coluna = np.full(len(CARACTERES), 1e-6)
        coluna[CARACTERES.index(letra)] = 1.0
        colunas.append(coluna)
        if i < len(passos):
            for k in range(passos[i] - 1):
                branco = np.full(len(CARACTERES), 1e-6)
                branco[0] = 1.0
                if i == espaco_em and k == (passos[i] - 1) // 2:
                    branco[ESPACO] = np.exp(margem)
                colunas.append(branco)
    probs = np.array(colunas)
    probs /= probs.sum(axis=1, keepdims=True)
    return Leitura(texto, probs, float(len(colunas)))


def cantos(largura, altura=10.0):
    """Caixa deitada no canto do print, com a largura e a altura dadas."""
    return [[0.0, 0.0], [largura, 0.0], [largura, altura], [0.0, altura]]


class TestEspacoEngolido(unittest.TestCase):
    """Só insere com as duas coisas: um passo fora do normal e o espaço quase escolhido."""

    def test_passo_largo_e_espaco_quase_escolhido(self):
        """"youmight": passo 3x maior entre u e m, e o espaço a -0,5 do branco."""
        lida = leitura("youmight", [2, 2, 6, 2, 2, 2, 2], espaco_em=2, margem=-0.5)
        posicoes = espacos_engolidos(lida, CARACTERES, cantos(len(lida.probs)))
        self.assertEqual(inserir_espacos("youmight", posicoes), "you might")

    def test_espaco_longe_de_ser_escolhido(self):
        """O mesmo passo largo, mas o espaço a -3 do branco: fica como está."""
        lida = leitura("youmight", [2, 2, 6, 2, 2, 2, 2], espaco_em=2, margem=-3.0)
        self.assertEqual(espacos_engolidos(lida, CARACTERES, cantos(len(lida.probs))), [])

    def test_sem_passo_largo_nao_e_candidata(self):
        """Passos iguais e nenhum vão de tinta: o espaço quase escolhido não basta."""
        lida = leitura("youmight", [4, 4, 4, 4, 4, 4, 4], espaco_em=2, margem=-0.5)
        self.assertEqual(espacos_engolidos(lida, CARACTERES, cantos(len(lida.probs))), [])

    def test_numero_decimal_nao_separa(self):
        """"1.8": as junções com o separador decimal são travadas."""
        lida = leitura("x1.8", [2, 6, 2], espaco_em=1, margem=-0.2)
        self.assertEqual(espacos_engolidos(lida, CARACTERES, cantos(len(lida.probs))), [])

    def test_apostrofo_nao_separa(self):
        """"won't": junção com apóstrofo é travada."""
        lida = leitura("won't", [2, 2, 6, 2], espaco_em=2, margem=-0.2)
        self.assertEqual(espacos_engolidos(lida, CARACTERES, cantos(len(lida.probs))), [])

    def test_caixa_em_pe_fica_de_fora(self):
        """Caixa mais alta que larga: o recorte foi girado e as colunas não valem."""
        lida = leitura("youmight", [2, 2, 6, 2, 2, 2, 2], espaco_em=2, margem=-0.5)
        self.assertEqual(espacos_engolidos(lida, CARACTERES, cantos(5.0, altura=40.0)), [])

    def test_texto_que_as_colunas_nao_formam(self):
        """Se as colunas não dão o texto da caixa, nada muda."""
        lida = leitura("youmight", [2, 2, 6, 2, 2, 2, 2], espaco_em=2, margem=-0.5)
        lida.texto = "you might"
        self.assertEqual(espacos_engolidos(lida, CARACTERES, cantos(len(lida.probs))), [])


class FakeReconhecedor:  # pylint: disable=too-few-public-methods
    """Reconhecedor de mentira, que ordena os recortes pela proporção e lê em lotes de 2,
    como o do RapidOCR."""

    def __init__(self):
        self.postprocess_op = _Decodificador()

    def __call__(self, entrada):
        recortes = entrada.img
        ordem = np.argsort(np.array([r.shape[1] / r.shape[0] for r in recortes]))
        textos = [""] * len(recortes)
        for inicio in range(0, len(recortes), 2):
            lote = ordem[inicio:inicio + 2]
            proporcoes = [recortes[i].shape[1] / recortes[i].shape[0] for i in lote]
            preds = np.stack([np.full((4, 3), float(i)) for i in lote])
            self.postprocess_op(
                preds, False, wh_ratio_list=proporcoes, max_wh_ratio=max(proporcoes)
            )
            for i in lote:
                textos[i] = f"caixa {i}"
        return SimpleNamespace(txts=tuple(textos))


class _Decodificador:  # pylint: disable=too-few-public-methods
    character = CARACTERES

    def __call__(self, preds, *args, **kwargs):
        return [], []


class TestGravador(unittest.TestCase):
    """O gravador devolve a leitura de cada recorte na ordem original."""

    def test_ordem_dos_recortes(self):
        """Recortes de proporções 4, 1, 3 e 2 lidos fora de ordem voltam ao lugar."""
        gravador = GravadorDoReconhecedor(FakeReconhecedor())
        recortes = [np.zeros((10, 40)), np.zeros((10, 10)), np.zeros((10, 30)), np.zeros((10, 20))]
        gravador(SimpleNamespace(img=recortes))
        self.assertEqual([int(l.probs[0, 0]) for l in gravador.leituras], [0, 1, 2, 3])
        self.assertEqual(
            [l.texto for l in gravador.leituras], ["caixa 0", "caixa 1", "caixa 2", "caixa 3"]
        )
        # o recorte mais largo do lote ocupa todas as colunas; o outro, a proporção dele
        self.assertAlmostEqual(gravador.leituras[2].colunas_uteis, 4 * 3 / 4)

    def test_leituras_por_caixa_pula_as_vazias(self):
        """O RapidOCR tira as caixas sem texto: a leitura de cada uma é casada pelo texto."""
        leituras = [Leitura(t, np.zeros((1, 1)), 1.0) for t in ("a", "", "b")]
        casadas = leituras_por_caixa(["a", "b"], leituras)
        self.assertEqual([l.texto if l else None for l in casadas], ["a", "b"])


if __name__ == "__main__":
    unittest.main()
