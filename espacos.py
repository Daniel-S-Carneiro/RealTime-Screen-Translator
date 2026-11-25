"""O espaço que o reconhecedor engoliu entre duas palavras ("youmight", "Pressto").

O RapidOCR às vezes lê duas palavras sem o espaço entre elas, e a palavra colada não se
traduz. A geometria sozinha não acha esse espaço: o passo entre as letras de uma palavra
chega a 0,68 altura, e o espaço que o OCR acerta desce a 0,43. Quem sabe é o próprio
reconhecedor: o CTC lê a linha em colunas, e numa coluna entre as duas letras o espaço
quase ganhou. A geometria só aponta os candidatos; a probabilidade do espaço decide. Não
usa dicionário, então vale para qualquer língua com espaço entre as palavras.

Proposta do ChatGPT (problema 12 da consulta às IAs, 25/11/2026): candidatos pelo passo
e pela tinta, decisão pelo CTC. Ele pedia a probabilidade da linha inteira com e sem o
espaço (algoritmo forward); aqui vai a versão barata, a margem do espaço na melhor coluna
entre as duas letras, que nos 150 prints deu o mesmo resultado: 13 espaços certos e
nenhum errado (os 4.564 candidatos errados ficaram todos com margem de -2 ou menos), +6
linhas inteiras e nenhuma perdida. As probabilidades são as da leitura principal,
guardadas por GravadorDoReconhecedor: não há segunda chamada ao reconhecedor.
"""

import statistics
from dataclasses import dataclass
from typing import Any, List, Optional, Sequence

import numpy as np

from paragrafos import SEM_ESPACO, _vaos_sem_tinta

CANDIDATO_PASSO = 1.15  # passo entre as letras contra a mediana dos passos da palavra
CANDIDATO_TINTA = 0.20  # ou um vão de tinta dessa largura (em alturas da caixa) na junção
MARGEM_MINIMA = -1.0  # log p(espaço) - log p(melhor classe), na melhor coluna entre as letras
# O limite natural seria 0 (o espaço ganha na coluna): +2 linhas. Com -1, +6, e nenhum dos
# 4.564 candidatos errados passa (o mais alto ficou em -2,0). Escolhido olhando os prints.
TOLERANCIA_TINTA = 2  # px: o vão de tinta conta se o meio da junção cai nele (ou perto)
CAIXA_EM_PE = 1.5  # altura/largura: o RapidOCR gira o recorte e o x das colunas não vale
APOSTROFO_HIFEN = frozenset("'’‘-‐–—")
NAO_SEPARA = frozenset("×/")
SEPARADOR_DECIMAL = frozenset(".,")
BRANCO = 0  # a classe "nenhuma letra" do CTC


@dataclass
class Leitura:
    """O que o reconhecedor viu numa caixa: o texto, as probabilidades de cada coluna e
    quantas colunas cobrem a imagem (o resto é o enchimento do lote)."""

    texto: str
    probs: np.ndarray
    colunas_uteis: float


class GravadorDoReconhecedor:
    """Envolve o reconhecedor do RapidOCR para guardar as probabilidades de cada caixa.

    O RapidOCR ordena os recortes pela proporção, lê em lotes e descarta as
    probabilidades depois de escolher as letras. O gravador pega cada lote antes do
    descarte e guarda as leituras na ordem dos recortes. O resto passa direto.
    """

    def __init__(self, reconhecedor: Any) -> None:
        self._reconhecedor = reconhecedor
        self._decodificador = reconhecedor.postprocess_op
        self._lotes: List[tuple] = []
        self.leituras: List[Leitura] = []
        reconhecedor.postprocess_op = self._decodificar

    def __getattr__(self, nome: str) -> Any:
        return getattr(self._reconhecedor, nome)

    @property
    def caracteres(self) -> List[str]:
        """As classes do reconhecedor (a 0 é o branco do CTC)."""
        return self._decodificador.character

    def _decodificar(self, preds, *args, **kwargs):
        self._lotes.append((preds, kwargs.get("wh_ratio_list"), kwargs.get("max_wh_ratio")))
        return self._decodificador(preds, *args, **kwargs)

    def __call__(self, entrada):
        self._lotes = []
        saida = self._reconhecedor(entrada)
        recortes = [entrada.img] if isinstance(entrada.img, np.ndarray) else list(entrada.img)
        # a mesma ordem do reconhecedor: os recortes ordenados pela proporção
        ordem = np.argsort(np.array([r.shape[1] / float(r.shape[0]) for r in recortes]))
        leituras: List[Optional[Leitura]] = [None] * len(recortes)
        posicao = 0
        for preds, proporcoes, maxima in self._lotes:
            for linha in range(preds.shape[0]):
                indice = int(ordem[posicao])
                proporcao = proporcoes[linha] if proporcoes else 1.0
                uteis = preds.shape[1] * proporcao / (maxima or proporcao)
                leituras[indice] = Leitura(str(saida.txts[indice]), preds[linha], uteis)
                posicao += 1
        self.leituras = [leitura for leitura in leituras if leitura is not None]
        return saida


def leituras_por_caixa(textos: Sequence, leituras: List[Leitura]) -> List[Optional[Leitura]]:
    """A leitura de cada caixa final, casada pelo texto (o RapidOCR tira as vazias)."""
    saida, proxima = [], 0
    for texto in textos:
        while proxima < len(leituras) and leituras[proxima].texto != str(texto):
            proxima += 1
        if proxima < len(leituras):
            saida.append(leituras[proxima])
            proxima += 1
        else:
            saida.append(None)
    return saida


def _emissoes(probs: np.ndarray) -> list:
    """(classe, coluna) de cada caractere que o decodificador guloso escolheu."""
    saida, anterior = [], -1
    for coluna, classe in enumerate(probs.argmax(axis=1)):
        if classe not in (anterior, BRANCO):
            saida.append((int(classe), coluna))
        anterior = classe
    return saida


def _travada(texto: str, posicao: int) -> bool:
    """Junções que nunca recebem espaço: apóstrofo, hífen, número com número, ×, /,
    separador decimal e escrita sem espaço. posicao é o índice da letra de depois."""
    antes, depois = texto[posicao - 1], texto[posicao]
    if {antes, depois} & (APOSTROFO_HIFEN | NAO_SEPARA):
        return True
    if SEM_ESPACO.match(antes) or SEM_ESPACO.match(depois):
        return True
    if antes.isdigit() and depois.isdigit():
        return True
    return any(  # o "." de "1.8", a "," de "300,000"
        texto[j] in SEPARADOR_DECIMAL and 0 < j < len(texto) - 1
        and texto[j - 1].isdigit() and texto[j + 1].isdigit()
        for j in (posicao - 1, posicao)
    )


def _letras(leitura: Leitura, caracteres: List[str], espaco: int, cantos) -> Optional[list]:
    """Cada caractere do texto, na ordem: None num espaço, senão (posição no texto, coluna
    do CTC, centro x no print). None se as colunas não formam o texto da caixa."""
    emissoes = _emissoes(leitura.probs)
    if "".join(caracteres[c] for c, _ in emissoes) != leitura.texto:
        return None
    xs = [p[0] for p in cantos]
    largura = max(xs) - min(xs)
    saida, posicao = [], 0
    for classe, coluna in emissoes:
        if classe == espaco:
            saida.append(None)
        else:
            centro = min(xs) + (coluna + 0.5) * largura / leitura.colunas_uteis
            saida.append((posicao, coluna, centro))
        posicao += len(caracteres[classe])
    return saida


def _trechos(letras: list) -> list:
    """Letras seguidas sem espaço entre elas."""
    saida, atual = [], []
    for letra in letras:
        if letra is None:
            if atual:
                saida.append(atual)
            atual = []
        else:
            atual.append(letra)
    if atual:
        saida.append(atual)
    return saida


def _vaos(cinza, cantos, altura: float) -> list:
    """Vãos sem tinta da caixa: (largura em alturas, x inicial, x final) no print."""
    xs = [p[0] for p in cantos]
    ys = [p[1] for p in cantos]
    x0, y0 = int(max(0, min(xs))), int(max(0, min(ys)))
    recorte = cinza[y0:int(max(ys)), x0:int(max(xs))]
    if recorte.size == 0:
        return []
    return [((b - a) / altura, x0 + a, x0 + b) for a, b in _vaos_sem_tinta(recorte)]


def espacos_engolidos(leitura: Leitura, caracteres: List[str], cantos, cinza=None) -> List[int]:
    """Posições do texto (o índice do caractere de depois) em que falta um espaço.

    cantos é a caixa no print; cinza, o print em tons de cinza, para o vão de tinta.
    """
    altura = _altura_deitada(cantos)
    if " " not in caracteres or leitura.colunas_uteis <= 0 or altura <= 0:
        return []
    espaco = caracteres.index(" ")
    letras = _letras(leitura, caracteres, espaco, cantos)
    if letras is None:
        return []
    vaos = _vaos(cinza, cantos, altura) if cinza is not None else []
    log_probs = np.log(np.maximum(leitura.probs, 1e-12))
    return [
        b[0]
        for trecho in _trechos(letras)
        for a, b in _candidatas(trecho, leitura.texto, altura, vaos)
        if _margem(log_probs, espaco, a[1], b[1]) > MARGEM_MINIMA
    ]


def _altura_deitada(cantos) -> float:
    """Altura da caixa, ou 0 se ela está em pé (o RapidOCR gira o recorte e o x das
    colunas não vale mais)."""
    xs = [p[0] for p in cantos]
    ys = [p[1] for p in cantos]
    altura = max(ys) - min(ys)
    return 0.0 if altura > CAIXA_EM_PE * (max(xs) - min(xs)) else altura


def _margem(log_probs: np.ndarray, espaco: int, coluna_a: int, coluna_b: int) -> float:
    """Quanto o espaço chegou perto de ganhar nas colunas entre duas letras: o maior
    log p(espaço) - log p(melhor classe). Letras em colunas vizinhas: olha as duas."""
    if coluna_b - coluna_a > 1:
        colunas = range(coluna_a + 1, coluna_b)
    else:
        colunas = range(coluna_a, coluna_b + 1)
    return max(float(log_probs[c, espaco] - log_probs[c].max()) for c in colunas)


def _candidatas(trecho: list, texto: str, altura: float, vaos: list) -> list:
    """Os pares de letras seguidas de um trecho em que o espaço pode ter sumido: o passo
    1,15 vez a mediana do trecho, ou um vão de tinta de 0,20 altura, fora das travas."""
    passos = [(b[2] - a[2]) / altura for a, b in zip(trecho, trecho[1:])]
    if not passos:
        return []
    mediana = statistics.median(passos)
    saida = []
    for passo, (a, b) in zip(passos, zip(trecho, trecho[1:])):
        if _travada(texto, b[0]):
            continue
        if _candidata(passo, mediana, _tinta(vaos, (a[2] + b[2]) / 2)):
            saida.append((a, b))
    return saida


def _tinta(vaos: list, meio: float) -> float:
    """A largura do vão de tinta no meio da junção (0 se não há)."""
    larguras = [w for w, x0, x1 in vaos
                if x0 - TOLERANCIA_TINTA <= meio <= x1 + TOLERANCIA_TINTA]
    return max(larguras, default=0.0)


def _candidata(passo: float, mediana: float, tinta: float) -> bool:
    return (mediana > 0 and passo / mediana >= CANDIDATO_PASSO) or tinta >= CANDIDATO_TINTA


def inserir_espacos(texto: str, posicoes: List[int]) -> str:
    """O texto com um espaço antes de cada posição."""
    for posicao in sorted(set(posicoes), reverse=True):
        texto = texto[:posicao] + " " + texto[posicao:]
    return texto
