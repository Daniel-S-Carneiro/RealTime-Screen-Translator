"""Quantidades que o detector não marca e ícones lidos como letra.

A) Num inventário ("Medicine   ×   1"), as quantidades ficam numa coluna à direita dos
itens. O detector do OCR não marca o "1" (um traço fino) e quase nunca marca o "×" e o
número juntos: das 8 linhas do inventário do Persona 4, nenhuma saía com "× N". Achada
a coluna de quantidade (2+ caixas só de número ou de "×", cada uma com um item à
esquerda), cada linha da coluna de itens que ficou sem quantidade tem o recorte do campo
relido só pelo reconhecedor. Se a leitura é uma quantidade com a confiança mínima do OCR,
ela entra no texto, no lugar dos pedaços que já estavam na célula.

B) Ícones de interface lidos como letra com confiança alta ("n", "0", "△" na coluna de
ícones do EVE, o "i" do botão de informação). A segunda leitura repete o mesmo texto,
então quem separa é a forma: uma coluna de glifos soltos com letra e não-letra
misturadas (ou alturas muito diferentes), um glifo solto bem maior ou menor que o texto
e sem vizinho do mesmo tamanho, ou um pedaço baixo encostado na borda do print.

Proposta A do Grok e B do Qwen (Problema 6, 18/11/2026), medidas nos 90 prints: as 8
linhas do inventário do Persona e o "Level 6" do Morrowind saem completos e os 5 ícones
do EVE saem do texto, sem piorar outro print. Três ajustes vieram da medição: o item de
cada quantidade é o mais perto à esquerda (pegando o primeiro da linha, os dois painéis
do Morrowind se misturavam e saíam "Class 30" e "Endurance 20"); uma célula com outro
texto não é relida (lia "75" dentro de "-475" no Qud); e a leitura nova passa pelo corte
de confiança do OCR (entrava um "3" com 0,12).

Só procura a quantidade à direita do item: as línguas lidas pelo RapidOCR são todas
escritas da esquerda para a direita.
"""

# pylint: disable=no-member

import re
import statistics
from dataclasses import dataclass

import cv2
import numpy as np

QUANTIDADE = re.compile(r"^(?:\d{1,4}|[xX×✕✖*＊]|[xX×✕✖*＊]\s*\d{1,4})$")

# A) medidas em alturas do texto do print (mediana das caixas com 3+ caracteres)
ALTURA_MINIMA = 0.6  # da caixa de quantidade que forma a coluna
LARGURA_MAXIMA = 2.5
COLUNA = 0.8  # entre os centros x de uma coluna
MESMA_LINHA = 0.5  # entre os centros y
VAO_MINIMO = 1.0  # entre o fim do item e a coluna de quantidade
CAMPO = 1.5  # colunas mais perto que isso formam um campo só (o "×" e o número)
MARGEM = 0.15  # em volta do recorte
TRACO_MINIMO = 0.4  # altura do maior traço de tinta no recorte, para valer a releitura
MAXIMO = 8  # recortes relidos por print
CONFIANCA_MINIMA = 0.7  # a mesma do OCR (ocr_engine.CONFIANCA_MINIMA)
TINTA = 20  # níveis de cinza longe do tom mais comum do recorte
ALTURA_DO_RECONHECEDOR = 48  # px; recortes mais baixos que PEQUENO são ampliados
PEQUENO = 24

# B) medidas em alturas do texto do print
COLUNA_DE_ICONES = 0.5  # entre os centros x
ICONES_MINIMO = 3
ALTURAS_DIFERENTES = 1.5  # maior / menor numa coluna de glifos
GLIFO_SOLTO = (0.6, 1.5)  # fora disso, glifo sem vizinho do mesmo tamanho é ícone
MESMO_TAMANHO = (0.6, 1.6)  # altura do vizinho / altura do glifo
VIZINHO = 3.0  # vão até o vizinho do mesmo tamanho
BORDA = 0.2  # da borda do print
BORDA_ALTURA = 0.7  # pedaço na borda mais baixo que isso...
BORDA_VIZINHO = 2.0  # ...e sem vizinho na linha até essa distância sai


def _limites(item) -> tuple:
    xs = [p[0] for p in item[0]]
    ys = [p[1] for p in item[0]]
    return min(xs), max(xs), min(ys), max(ys)


def _altura(item) -> float:
    _, _, topo, base = _limites(item)
    return base - topo


def _largura(item) -> float:
    esquerda, direita, _, _ = _limites(item)
    return direita - esquerda


def _centro_x(item) -> float:
    esquerda, direita, _, _ = _limites(item)
    return (esquerda + direita) / 2


def _centro_y(item) -> float:
    _, _, topo, base = _limites(item)
    return (topo + base) / 2


def _texto(item) -> str:
    return item[1].strip()


def _glifos(item) -> int:
    return len("".join(item[1].split()))


def _altura_do_texto(caixas: list) -> float:
    """Mediana da altura das caixas com 3+ caracteres (ou de todas, se não houver)."""
    longas = [_altura(c) for c in caixas if len(_texto(c)) >= 3]
    if longas:
        return statistics.median(longas)
    return statistics.median(_altura(c) for c in caixas) if caixas else 0.0


def _mesma_linha(a, b, h: float) -> bool:
    return abs(_centro_y(a) - _centro_y(b)) <= MESMA_LINHA * h


def _vao(a, b) -> float:
    """Distância horizontal entre duas caixas (negativa se elas se cruzam)."""
    return min(abs(_limites(a)[0] - _limites(b)[1]), abs(_limites(b)[0] - _limites(a)[1]))


def _colunas(caixas: list, tolerancia: float) -> list:
    """Agrupa pelo centro x, em cadeia."""
    colunas = []
    for caixa in sorted(caixas, key=_centro_x):
        if colunas and _centro_x(caixa) - _centro_x(colunas[-1][-1]) < tolerancia:
            colunas[-1].append(caixa)
        else:
            colunas.append([caixa])
    return colunas


def _recortar(cinza: np.ndarray, x0: float, x1: float, y0: float, y1: float) -> np.ndarray:
    alto, largo = cinza.shape[:2]
    return cinza[max(0, int(y0)):min(alto, int(y1)), max(0, int(x0)):min(largo, int(x1))]


def _tem_traco(recorte: np.ndarray, minimo: float) -> bool:
    """Se há um traço de tinta com pelo menos essa altura no recorte."""
    if recorte.size == 0:
        return False
    fundo = int(np.bincount(recorte.ravel(), minlength=256).argmax())
    tinta = (np.abs(recorte.astype(int) - fundo) >= TINTA).astype(np.uint8)
    total, _, medidas, _ = cv2.connectedComponentsWithStats(tinta, connectivity=8)
    return any(medidas[i, cv2.CC_STAT_HEIGHT] >= minimo for i in range(1, total))


def _ampliar(recorte: np.ndarray) -> np.ndarray:
    if 0 < recorte.shape[0] < PEQUENO:
        fator = min((2, 3), key=lambda k: abs(recorte.shape[0] * k - ALTURA_DO_RECONHECEDOR))
        return cv2.resize(recorte, None, fx=fator, fy=fator, interpolation=cv2.INTER_LANCZOS4)
    return recorte


def _itens(caixas: list) -> list:
    return [c for c in caixas if len(_texto(c)) >= 3 and not QUANTIDADE.match(_texto(c))]


@dataclass
class _Campo:
    """Um campo de quantidade: uma coluna ou duas juntas (o "×" e o número)."""

    inicio: float
    fim: float
    pares: list  # os itens com quantidade, um por caixa de quantidade
    colunas: int = 1

    def celula(self, caixas: list, item, h: float) -> list:
        """As caixas que já estão no campo, na linha do item."""
        x0, x1 = self.inicio - MARGEM * h, self.fim + MARGEM * h
        return [
            c for c in caixas
            if c is not item and _mesma_linha(c, item, h)
            and _limites(c)[1] > x0 and _limites(c)[0] < x1
        ]

    def cantos(self, item, margem: float) -> list:
        """O retângulo do campo na linha do item (com margem, para o recorte)."""
        _, _, topo, base = _limites(item)
        x0, x1, y0, y1 = self.inicio - margem, self.fim + margem, topo - margem, base + margem
        return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]

    def recorte(self, cinza: np.ndarray, item, h: float) -> np.ndarray:
        """O campo na linha do item, com margem, recortado do print."""
        (x0, y0), _, (x1, y1), _ = self.cantos(item, MARGEM * h)
        return _recortar(cinza, x0, x1, y0, y1)

    def linhas(self, itens: list, h: float) -> list:
        """Os itens da mesma coluna dos que têm quantidade, de cima para baixo."""
        esquerda = statistics.median(_limites(p)[0] for p in self.pares)
        return sorted(
            (i for i in itens
             if abs(_limites(i)[0] - esquerda) <= h and _limites(i)[1] < self.inicio),
            key=_centro_y,
        )


def _colunas_de_quantidade(caixas: list, h: float) -> list:
    """Colunas de 2+ quantidades, cada uma com o item mais perto à esquerda, longe dele."""
    quantidades = [
        c for c in caixas
        if QUANTIDADE.match(_texto(c)) and _largura(c) <= LARGURA_MAXIMA * h
        and _altura(c) >= ALTURA_MINIMA * h
    ]
    itens = _itens(caixas)
    colunas = []
    for coluna in _colunas(quantidades, COLUNA * h):
        inicio = min(_limites(c)[0] for c in coluna)
        pares = []
        for quantidade in coluna:
            antes = [i for i in itens
                     if _mesma_linha(i, quantidade, h) and _limites(i)[1] < inicio]
            if antes:
                pares.append(max(antes, key=lambda i: _limites(i)[1]))
        if len(pares) >= 2 and inicio - max(_limites(p)[1] for p in pares) >= VAO_MINIMO * h:
            colunas.append(_Campo(inicio, max(_limites(c)[1] for c in coluna), pares))
    return sorted(colunas, key=lambda c: c.inicio)


def _campos(caixas: list, h: float) -> list:
    """Campos de quantidade: colunas perto uma da outra viram um campo só."""
    campos = []
    for coluna in _colunas_de_quantidade(caixas, h):
        if campos and coluna.inicio - campos[-1].fim < CAMPO * h:
            campos[-1].fim = max(campos[-1].fim, coluna.fim)
            campos[-1].pares += coluna.pares
            campos[-1].colunas += 1
        else:
            campos.append(coluna)
    return campos


def completar_quantidades(cinza: np.ndarray, caixas: list, ler) -> tuple:
    """Relê a célula de quantidade das linhas que ficaram sem ela.

    caixas: [(cantos, texto, confiança)]; ler(recorte em cinza) -> (texto, confiança).
    Devolve (caixas, ids das caixas dos campos de quantidade), para tirar_icones não
    tirar um "X" de quantidade.
    """
    saida = list(caixas)
    protegidas = set()
    h = _altura_do_texto(caixas)
    if not h:
        return saida, protegidas
    itens = _itens(caixas)
    relidos = 0
    for campo in _campos(caixas, h):
        for item in campo.linhas(itens, h):
            celula = campo.celula(saida, item, h)
            if any(not QUANTIDADE.match(_texto(c)) for c in celula):
                continue  # a célula tem outro texto ("Reputation: -475")
            protegidas.update(id(c) for c in celula)  # mesmo se a releitura falhar
            if len(celula) >= campo.colunas:
                continue
            recorte = campo.recorte(cinza, item, h)
            if relidos >= MAXIMO or not _tem_traco(recorte, TRACO_MINIMO * h):
                continue
            texto, confianca = ler(_ampliar(recorte))
            relidos += 1
            if confianca < CONFIANCA_MINIMA or not QUANTIDADE.match(texto.strip()):
                continue
            saida = [c for c in saida if all(c is not v for v in celula)]
            saida.append((campo.cantos(item, 0), texto.strip(), float(confianca)))
            protegidas.add(id(saida[-1]))
    return saida, protegidas


def _coluna_de_icones(candidatas: list, h: float) -> set:
    """Colunas de glifos soltos com letra e não-letra misturadas ou alturas diferentes."""
    icones = set()
    curtas = [c for c in candidatas if _glifos(c) <= 2]
    for coluna in _colunas(curtas, COLUNA_DE_ICONES * h):
        if len(coluna) < ICONES_MINIMO:
            continue
        com_letra = [any(ch.isalpha() for ch in _texto(c)) for c in coluna]
        alturas = [_altura(c) for c in coluna]
        misturada = any(com_letra) and not all(com_letra)
        if misturada or max(alturas) / max(min(alturas), 1) >= ALTURAS_DIFERENTES:
            icones.update(id(c) for c in coluna)
    return icones


def _glifo_solto(caixa, caixas: list, h: float) -> bool:
    """Um glifo (não dígito) fora da altura do texto, sem vizinho do mesmo tamanho."""
    texto = _texto(caixa)
    if _glifos(caixa) != 1 or texto.isdigit():
        return False
    if GLIFO_SOLTO[0] * h <= _altura(caixa) <= GLIFO_SOLTO[1] * h:
        return False
    return not any(
        o is not caixa and _mesma_linha(o, caixa, h)
        and MESMO_TAMANHO[0] <= _altura(o) / max(_altura(caixa), 1) <= MESMO_TAMANHO[1]
        and _vao(o, caixa) <= VIZINHO * h
        for o in caixas
    )


def _pedaco_na_borda(caixa, caixas: list, h: float, largura: int) -> bool:
    """Até 2 glifos, baixo, encostado na borda do print e sem vizinho na linha."""
    if _glifos(caixa) > 2 or _altura(caixa) > BORDA_ALTURA * h:
        return False
    esquerda, direita, _, _ = _limites(caixa)
    if esquerda > BORDA * h and direita < largura - BORDA * h:
        return False
    return not any(
        o is not caixa and _mesma_linha(o, caixa, h) and _vao(o, caixa) <= BORDA_VIZINHO * h
        for o in caixas
    )


def tirar_icones(caixas: list, largura: int, protegidas=frozenset()) -> list:
    """Tira os ícones lidos como letra. largura: do print, em px."""
    h = _altura_do_texto(caixas)
    if not h:
        return list(caixas)
    candidatas = [c for c in caixas if id(c) not in protegidas]
    icones = _coluna_de_icones(candidatas, h)
    icones.update(
        id(c) for c in candidatas
        if _glifo_solto(c, caixas, h) or _pedaco_na_borda(c, caixas, h, largura)
    )
    return [c for c in caixas if id(c) not in icones]
