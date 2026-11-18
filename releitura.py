"""Segunda leitura das caixas pequenas: tira o lixo que o OCR lê em letreiros miúdos.

Em letra miúda e borrada (capas de revista numa banca, placas ao longe) o OCR inventa
texto: "SADRKRNIT", "(RNED BEEE". Nos 8 prints de letreiro do benchmark, 65% do erro de
letras era texto a mais, não letra trocada. Lido de novo, o recorte da caixa ampliado,
o lixo muda ("SADRKRNIT" vira "SARIENIT") e perde confiança; o texto real continua igual
("PIEROGI SANDWICH • 3.99"). Quando as duas leituras não concordam e a primeira não é
segura, a caixa sai do texto: melhor não traduzir do que traduzir lixo.

Proposta do Grok (Problema 5, 18/11/2026), medida nos 90 prints: acerto de letras de
95,13% para 95,73%, letreiros de 79,4% para 85,9%, texto a mais nos letreiros de 112 para
33 caracteres, sem piorar outro tipo de tela. Tira também ícones lidos como letra ("D",
"0", "☑ - ×" nas tabelas do EVE).

A releitura usa só o reconhecedor do RapidOCR, numa caixa por vez (cerca de 35 ms cada),
em no máximo 8 caixas por print.
"""

# pylint: disable=no-member

import statistics
import unicodedata

import cv2
import numpy as np

ALTURA_MAXIMA = 32  # px; o reconhecedor recebe a linha com 48 px: abaixo disso ele amplia
FRACAO_DA_TIPICA = 0.6  # e menor que isso da altura típica das caixas do print...
TIPICA_PEQUENA = 24  # ...a não ser num print só de letra miúda: aí toda caixa < 32 px entra
MAXIMO = 8  # caixas relidas por print, as de menor confiança
MARGEM = 0.15  # em volta do recorte, em alturas da caixa
ALTURA_DO_RECONHECEDOR = 48
CONFIANCA_SEGURA = 0.85  # acima disso a leitura original fica, mesmo sem concordância
EDICAO_MAXIMA = 0.25  # diferença entre as leituras, em fração do texto mais longo
GANHO_MINIMO = 0.05  # de confiança, para trocar pela segunda leitura
TINTA = 20  # níveis de cinza longe do tom mais comum da caixa


def _limites(cantos) -> tuple:
    xs = [p[0] for p in cantos]
    ys = [p[1] for p in cantos]
    return min(xs), max(xs), min(ys), max(ys)


def _altura(item) -> float:
    _, _, topo, base = _limites(item[0])
    return base - topo


def _recorte(cinza: np.ndarray, item, margem: float) -> np.ndarray:
    x0, x1, y0, y1 = (int(round(v)) for v in _limites(item[0]))
    m = int(round(margem))
    return cinza[max(0, y0 - m):max(0, y1 + m), max(0, x0 - m):max(0, x1 + m)]


def _normalizar(texto: str) -> str:
    return " ".join(texto.lower().split())


def _edicao(a: str, b: str) -> int:
    linha = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        anterior, linha[0] = linha[0], i
        for j, cb in enumerate(b, 1):
            troca = anterior + (ca != cb)
            anterior, linha[j] = linha[j], min(linha[j] + 1, linha[j - 1] + 1, troca)
    return linha[-1]


def _so_numero(texto: str) -> bool:
    return any(c.isdigit() for c in texto) and all(c.isdigit() or not c.isalnum() for c in texto)


def _escritas(texto: str) -> list:
    """Quantas letras de cada escrita (latina, cirílica...); kana e han contam juntos."""
    baldes = {}
    for c in texto:
        if c.isalpha():
            balde = (unicodedata.name(c, "?").split() or ["?"])[0]
            balde = "CJK" if balde in ("HIRAGANA", "KATAKANA", "CJK") else balde
            baldes[balde] = baldes.get(balde, 0) + 1
    return list(baldes.values())


def _e_lixo(cinza: np.ndarray, item) -> bool:
    """Lixo pela forma, sem dicionário: caixa quase vazia ou chapada, letras de duas
    escritas misturadas, ou mais símbolos que letras."""
    recorte = _recorte(cinza, item, 0).astype(int)
    if recorte.size:
        fundo = int(np.bincount(recorte.ravel(), minlength=256).argmax())
        tinta = float((np.abs(recorte - fundo) >= TINTA).mean())
        if tinta < 0.02 or tinta > 0.85:
            return True
    texto = item[1]
    baldes = _escritas(texto)
    if len(baldes) >= 2 and min(baldes) >= 2:
        return True
    simbolos = sum(1 for c in texto if unicodedata.category(c)[0] in "SC")
    return len(texto) >= 2 and simbolos / len(texto) > 0.5


def _candidatas(caixas: list) -> set:
    """As caixas pequenas de menor confiança (ids)."""
    if not caixas:
        return set()
    tipica = statistics.median(_altura(c) for c in caixas)
    pequenas = [
        c for c in caixas
        if _altura(c) < ALTURA_MAXIMA
        and (_altura(c) < FRACAO_DA_TIPICA * tipica or tipica < TIPICA_PEQUENA)
    ]
    return {id(c) for c in sorted(pequenas, key=lambda c: c[2])[:MAXIMO]}


def _decidir(cinza: np.ndarray, item, ler):
    """A caixa como fica depois da segunda leitura, ou None se ela sai do texto."""
    altura = _altura(item)
    recorte = _recorte(cinza, item, MARGEM * altura)
    if recorte.size == 0:
        return item
    if altura < TIPICA_PEQUENA:
        fator = min((2, 3), key=lambda k: abs(altura * k - ALTURA_DO_RECONHECEDOR))
        recorte = cv2.resize(recorte, None, fx=fator, fy=fator, interpolation=cv2.INTER_LANCZOS4)
    texto, confianca = item[1], item[2]
    novo, nova = ler(recorte)
    a, b = _normalizar(texto), _normalizar(novo)
    if a == b:
        return item
    if _so_numero(texto) and _so_numero(novo) and _edicao(a, b) <= 1:
        return item if confianca >= nova else (item[0], novo, nova)
    if _edicao(a, b) / max(len(a), len(b), 1) <= EDICAO_MAXIMA and nova >= confianca + GANHO_MINIMO:
        return (item[0], novo, nova)
    if confianca >= CONFIANCA_SEGURA and not _e_lixo(cinza, item):
        return item
    return None


def conferir_caixas_pequenas(cinza: np.ndarray, caixas: list, ler) -> list:
    """Relê as caixas pequenas e tira as que não se confirmam.

    caixas: [(cantos, texto, confiança)], já sem as de confiança baixa.
    ler(recorte em cinza) -> (texto, confiança): só o reconhecedor do OCR.
    """
    candidatas = _candidatas(caixas)
    saida = []
    for item in caixas:
        if id(item) in candidatas:
            item = _decidir(cinza, item, ler)
        if item is not None:
            saida.append(item)
    return saida
