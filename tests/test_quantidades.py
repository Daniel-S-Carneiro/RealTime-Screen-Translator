"""Quantidades sem caixa e ícones lidos como letra (quantidades.py), com um leitor de mentira.

O leitor devolve o que o teste manda, então não precisa do modelo do OCR. A imagem é
desenhada: fundo cinza e "tinta" em faixas dentro das caixas e nos retângulos pedidos (o
que está no print mas o detector não marcou).
"""

import unittest

import numpy as np

from quantidades import MAXIMO, completar_quantidades, tirar_icones
from tests.casos_paragrafos import caixa


def tela(caixas, tinta=(), largura=1200, altura=900):
    """Fundo 150; tinta 60 nas caixas e nos retângulos (x0, y0, x1, y1) de 'tinta'."""
    img = np.full((altura, largura), 150, dtype=np.uint8)
    retangulos = [(p[0][0], p[0][1], p[2][0], p[2][1]) for p, _t, _c in caixas] + list(tinta)
    for x0, y0, x1, y1 in retangulos:
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


def textos_na_linha(caixas, y, x_minimo):
    """Textos das caixas à direita de x_minimo cujo centro cai na linha y (+-20 px)."""
    return sorted(
        (c[0][0][0], c[1]) for c in caixas
        if c[0][0][0] >= x_minimo and abs((c[0][0][1] + c[0][2][1]) / 2 - y) <= 20
    )


# Inventário como o do Persona 4: itens com letra de 50 px, o "×" em x 700 e o número em
# x 800. O detector marcou só alguns pedaços; a tinta das 8 linhas está no print.
ITENS = ["Medicine", "Soul Drop", "Vanish Ball", "Peach Seed", "Life Stone",
         "Revival Bead", "Chest Key", "Velvet Key"]
MARCADO = {1: ["X"], 2: ["X"], 3: ["6"], 4: ["3"], 5: ["X", "4"], 7: ["X"]}


def inventario():
    """As caixas que o detector marcou e o print com a tinta de todas as quantidades."""
    caixas = []
    tinta = []
    for k, nome in enumerate(ITENS):
        y = 20 + 63 * k
        caixas.append(caixa(100, y, 300, nome, altura=50, conf=1.0))
        for texto in MARCADO.get(k, []):
            x = 700 if texto == "X" else 800
            caixas.append(caixa(x, y + 5, 40, texto, altura=40, conf=0.95))
        tinta += [(700, y + 5, 740, y + 45), (800, y + 5, 840, y + 45)]
    return caixas, tela(caixas, tinta)


class TestQuantidades(unittest.TestCase):
    """O "×" e o número que o detector não marcou entram pela releitura da célula."""

    def test_inventario_completo(self):
        """As 7 linhas sem quantidade inteira são relidas; a completa (X 4) fica igual."""
        caixas, img = inventario()
        lidas = ["×1", "X5", "×1", "×6", "×3", "×1", "× 1"]
        ler, chamadas = leitor([(t, 0.9) for t in lidas])
        saida, protegidas = completar_quantidades(img, caixas, ler)
        self.assertEqual(len(chamadas), 7)
        esperado = iter(lidas)
        for k in range(len(ITENS)):
            linha = textos_na_linha(saida, 20 + 63 * k + 25, 600)
            if k == 5:
                self.assertEqual([t for _, t in linha], ["X", "4"])
            else:
                self.assertEqual([t for _, t in linha], [next(esperado)])
        # nenhuma caixa de quantidade sai como ícone
        self.assertEqual(tirar_icones(saida, img.shape[1], protegidas), saida)

    def test_leitura_fraca_nao_entra(self):
        """Releitura fraca não muda nada, e o "X" baixo da coluna não sai como ícone."""
        caixas, img = inventario()
        baixo = next(k for k, c in enumerate(caixas) if c[1] == "X" and c[0][0][1] == 151)
        caixas[baixo] = caixa(700, 157, 40, "X", altura=28, conf=0.95)  # 0,56 da letra
        ler, _ = leitor([("×1", 0.5)] * 7)
        saida, protegidas = completar_quantidades(img, caixas, ler)
        self.assertEqual(saida, caixas)
        self.assertEqual(tirar_icones(saida, img.shape[1], protegidas), saida)
        self.assertNotIn(caixas[baixo], tirar_icones(saida, img.shape[1]))

    def test_leitura_que_nao_e_quantidade_nao_entra(self):
        """Uma palavra lida na célula não entra."""
        caixas, img = inventario()
        ler, _ = leitor([("Key", 0.95)] * 7)
        saida, _ = completar_quantidades(img, caixas, ler)
        self.assertEqual(saida, caixas)

    def test_celula_com_outro_texto_nao_e_relida(self):
        """Como no Qud: "Reputation: 0" em coluna, e uma linha com "-475" na célula."""
        caixas = []
        for k, valor in enumerate(["0", "0", "-475", "0"]):
            y = 100 + 120 * k
            caixas.append(caixa(678, y, 110, "Reputation:", altura=20, conf=1.0))
            x = 800 if valor == "-475" else 828
            caixas.append(caixa(x, y, 50 if valor == "-475" else 16, valor, altura=20, conf=1.0))
        ler, chamadas = leitor([("75", 0.99)])
        saida, _ = completar_quantidades(tela(caixas), caixas, ler)
        self.assertEqual(chamadas, [])
        self.assertEqual(saida, caixas)

    def test_texto_no_campo_de_duas_colunas_fica(self):
        """Uma linha com uma palavra no lugar do "× N" não é relida nem perde a palavra."""
        caixas, _ = inventario()
        y = 20 + 63 * len(ITENS)
        caixas += [caixa(100, y, 300, "Old Map", altura=50, conf=1.0),
                   caixa(690, y + 5, 160, "Key item", altura=40, conf=1.0)]
        img = tela(caixas, [(700, 25 + 63 * k, 840, 65 + 63 * k) for k in range(len(ITENS))])
        ler, _ = leitor([("×1", 0.9)] * 10)
        saida, _ = completar_quantidades(img, caixas, ler)
        self.assertEqual([t for _, t in textos_na_linha(saida, y + 25, 600)], ["Key item"])

    def test_sem_coluna_de_quantidade_nada_e_relido(self):
        """Um número solto ao lado de um item não forma coluna."""
        caixas = [caixa(100, 20, 300, "Medicine", altura=50), caixa(800, 25, 40, "6", altura=40),
                  caixa(100, 83, 300, "Soul Drop", altura=50)]
        ler, chamadas = leitor([("×1", 0.9)])
        saida, _ = completar_quantidades(tela(caixas, [(800, 88, 840, 128)]), caixas, ler)
        self.assertEqual(chamadas, [])
        self.assertEqual(saida, caixas)

    def test_dois_paineis_nao_se_misturam(self):
        """Como no Morrowind: o campo da direita só relê as linhas do painel da direita.

        A linha "Class" é do painel da esquerda; a tinta na altura dela, no campo da
        direita, é de outra coisa e não pode virar a quantidade dela.
        """
        caixas = []
        paineis = [("Strength", "Destruction"), ("Intelligence", "Light Armor"),
                   ("Willpower", "Long Blade")]
        for k, (esq, dir_) in enumerate(paineis):
            y = 100 + 30 * k
            caixas += [caixa(30, y, 80, esq, altura=25), caixa(220, y, 25, "65", altura=25),
                       caixa(260, y, 90, dir_, altura=25), caixa(455, y, 25, "41", altura=25)]
        caixas.append(caixa(30, 220, 50, "Class", altura=25))
        ler, chamadas = leitor([("30", 0.99)])
        saida, _ = completar_quantidades(tela(caixas, [(455, 222, 480, 245)]), caixas, ler)
        self.assertEqual(chamadas, [])
        self.assertEqual(saida, caixas)

    def test_no_maximo_oito_releituras(self):
        """Numa lista longa sem quantidades, só 8 células são relidas."""
        caixas = []
        tinta = []
        for k in range(14):
            y = 20 + 63 * k
            caixas.append(caixa(100, y, 300, f"Item number {k}", altura=50))
            if k < 2:
                caixas += [caixa(700, y + 5, 40, "X", altura=40),
                           caixa(800, y + 5, 40, "5", altura=40)]
            tinta += [(700, y + 5, 740, y + 45), (800, y + 5, 840, y + 45)]
        ler, chamadas = leitor([("×1", 0.9)] * 20)
        completar_quantidades(tela(caixas, tinta, altura=1000), caixas, ler)
        self.assertEqual(len(chamadas), MAXIMO)


def linhas_de_texto(passo, largura, altura):
    """Quatro linhas de texto comum, uma embaixo da outra."""
    return [caixa(60, 100 + passo * k, largura, f"Some line of text {k}", altura=altura)
            for k in range(4)]


class TestIcones(unittest.TestCase):
    """Ícones lidos como letra saem pela forma; texto e números reais ficam."""

    def test_coluna_de_icones_misturados_sai(self):
        """Como no EVE: "n", "0", "0", "△" numa coluna, ao lado dos dados da tabela."""
        caixas = []
        for k, (icone, h) in enumerate([("n", 11), ("0", 19), ("0", 19), ("△", 13)]):
            y = 100 + 30 * k
            caixas += [caixa(25, y + (18 - h) / 2, 17, icone, altura=h),
                       caixa(60, y, 200, f"Station Alpha {k}", altura=18),
                       caixa(300, y, 60, "12 km", altura=18)]
        saida = tirar_icones(caixas, 435)
        self.assertEqual([t for _, t, _ in saida],
                         [t for _, t, _ in caixas if len(t) > 1])

    def test_coluna_de_numeros_fica(self):
        """Como no Qud: "Reputation: 0" três vezes; o 0 é valor, não ícone."""
        caixas = []
        for k in range(3):
            caixas += [caixa(678, 100 + 120 * k, 110, "Reputation:", altura=20),
                       caixa(828, 100 + 120 * k, 16, "0", altura=19)]
        self.assertEqual(tirar_icones(caixas, 1657), caixas)

    def test_glifo_solto_grande_sai(self):
        """O "i" do botão de informação: 1,7 vez a altura do texto e sem vizinho."""
        texto = linhas_de_texto(30, 250, 18)
        icone = caixa(380, 20, 15, "i", altura=31)
        self.assertEqual(tirar_icones(texto + [icone], 435), texto)

    def test_letra_solta_do_tamanho_do_texto_fica(self):
        """Uma letra sozinha na altura do texto (uma opção "A", uma nota) fica."""
        texto = linhas_de_texto(30, 250, 18)
        letra = caixa(380, 20, 14, "A", altura=18)
        self.assertEqual(tirar_icones(texto + [letra], 435), texto + [letra])

    def test_pedaco_na_borda_sai(self):
        """Pedaço baixo encostado na borda direita, sem vizinho na linha."""
        texto = linhas_de_texto(40, 600, 20)
        pedaco = caixa(1637, 300, 19, "po", altura=13)
        self.assertEqual(tirar_icones(texto + [pedaco], 1657), texto)

    def test_pedaco_na_borda_com_vizinho_fica(self):
        """Na borda, mas com texto ao lado na mesma linha: é o fim de uma linha cortada."""
        texto = linhas_de_texto(40, 600, 20)
        fim = [caixa(1500, 300, 120, "and then", altura=20), caixa(1637, 303, 19, "po", altura=13)]
        self.assertEqual(tirar_icones(texto + fim, 1657), texto + fim)


if __name__ == "__main__":
    unittest.main()
