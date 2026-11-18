"""Segunda leitura das caixas pequenas (releitura.py), com um leitor de mentira.

O leitor devolve o que o teste manda, então não precisa do modelo do OCR. A imagem é
desenhada: fundo cinza e "tinta" dentro das caixas.
"""

import unittest

import numpy as np

from releitura import MAXIMO, conferir_caixas_pequenas
from tests.casos_paragrafos import caixa


def tela(caixas, vazias=()):
    """Fundo 150 e tinta 60 em faixas dentro de cada caixa (menos nas 'vazias')."""
    img = np.full((600, 1200), 150, dtype=np.uint8)
    for k, (pontos, _texto, _conf) in enumerate(caixas):
        if k in vazias:
            continue
        (x0, y0), (x1, y1) = pontos[0], pontos[2]
        for x in range(int(x0) + 2, int(x1) - 2, 6):
            img[int(y0) + 3:int(y1) - 3, x:x + 3] = 60
    return img


def leitor(respostas):
    """ler(recorte) que devolve as respostas em ordem e conta as chamadas."""
    fila = list(respostas)
    chamadas = []

    def ler(recorte):
        chamadas.append(recorte.shape)
        return fila.pop(0) if fila else ("", 0.0)

    return ler, chamadas


def letreiro(texto, conf, y):
    """Caixa pequena (18 px) num print só de letra miúda."""
    return caixa(40, y, 300, texto, altura=18, conf=conf)


class TestReleitura(unittest.TestCase):
    """O lixo não se confirma na segunda leitura; o texto real se confirma."""

    def test_lixo_que_muda_sai(self):
        """'SADRKRNIT' (0,78) relido como 'SARIENIT' (0,72): sai do texto."""
        caixas = [letreiro("SADRKRNIT", 0.78, 50)]
        ler, _ = leitor([("SARIENIT", 0.72)])
        self.assertEqual(conferir_caixas_pequenas(tela(caixas), caixas, ler), [])

    def test_texto_que_se_confirma_fica(self):
        """Texto real relido igual fica, com a leitura original."""
        caixas = [letreiro("PIEROGI POUCH 2.99", 0.80, 50)]
        ler, _ = leitor([("pierogi pouch 2.99", 0.95)])
        self.assertEqual(conferir_caixas_pequenas(tela(caixas), caixas, ler), caixas)

    def test_leitura_segura_fica_mesmo_diferente(self):
        """Confiança 0,93 e caixa com tinta: fica, mesmo que a releitura mude."""
        caixas = [letreiro("PIEROGI SANDWICH 3.99", 0.93, 50)]
        ler, _ = leitor([("PIEROGISANDWICH * 3.99", 0.80)])
        self.assertEqual(conferir_caixas_pequenas(tela(caixas), caixas, ler), caixas)

    def test_caixa_segura_sem_tinta_sai(self):
        """Confiança alta, mas a caixa não tem tinta: é lixo."""
        caixas = [letreiro("VARIETIES", 0.90, 50)]
        ler, _ = leitor([("ARIES", 0.60)])
        self.assertEqual(conferir_caixas_pequenas(tela(caixas, vazias={0}), caixas, ler), [])

    def test_releitura_melhor_e_parecida_troca(self):
        """Releitura parecida e mais confiante substitui a original."""
        caixas = [letreiro("HOTDOGS 1.99", 0.78, 50)]
        ler, _ = leitor([("HOT DOGS 1.99", 0.90)])
        saida = conferir_caixas_pequenas(tela(caixas), caixas, ler)
        self.assertEqual([t for _, t, _ in saida], ["HOT DOGS 1.99"])

    def test_numero_com_um_digito_diferente_fica(self):
        """Número relido com um dígito diferente não é descartado."""
        caixas = [letreiro("83", 0.71, 50)]
        ler, _ = leitor([("88", 0.94)])
        saida = conferir_caixas_pequenas(tela(caixas), caixas, ler)
        self.assertEqual([t for _, t, _ in saida], ["88"])

    def test_caixa_grande_nao_e_relida(self):
        """Texto do tamanho típico (40 px) não passa pela releitura."""
        caixas = [caixa(40, 50, 600, "This is ordinary dialogue text.", altura=40, conf=0.75)]
        ler, chamadas = leitor([])
        self.assertEqual(conferir_caixas_pequenas(tela(caixas), caixas, ler), caixas)
        self.assertEqual(chamadas, [])

    def test_caixa_pequena_num_print_de_letra_grande(self):
        """Caixa de 28 px num print de letra de 60 px é relida (menor que 0,6 da típica)."""
        caixas = [caixa(40, 50, 600, f"Big line {k}", altura=60, conf=0.99) for k in range(4)]
        caixas[3] = caixa(40, 400, 300, "tiny junk", altura=28, conf=0.80)
        ler, chamadas = leitor([("tny jnk", 0.50)])
        saida = conferir_caixas_pequenas(tela(caixas), caixas, ler)
        self.assertEqual(len(chamadas), 1)
        self.assertNotIn("tiny junk", [t for _, t, _ in saida])

    def test_no_maximo_oito_releituras(self):
        """Num print cheio de letra miúda, só as 8 de menor confiança são relidas."""
        caixas = [letreiro(f"SIGN {k}", 0.75 + k / 100, 20 + 30 * k) for k in range(12)]
        ler, chamadas = leitor([(f"SIGN {k}", 0.9) for k in range(12)])
        conferir_caixas_pequenas(tela(caixas), caixas, ler)
        self.assertEqual(len(chamadas), MAXIMO)


if __name__ == "__main__":
    unittest.main()
