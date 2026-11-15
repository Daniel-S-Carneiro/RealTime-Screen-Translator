"""Junta as linhas lidas pelo OCR em parágrafos, para a tradução respeitar as quebras.

Texto na tela tem dois tipos de quebra de linha:
- a de verdade, entre título, parágrafo, item de menu ou efeito;
- a visual, quando a frase não coube na largura da caixa e continuou embaixo.

Só a primeira deve chegar ao tradutor: cortar uma frase no meio estraga a tradução,
e o texto traduzido tem outro tamanho, então a quebra visual não serviria de qualquer
jeito. As regras usam só a posição das caixas do EasyOCR, sempre em proporção ao
tamanho das letras, para valer em qualquer resolução.

Antes das linhas, o print é dividido em blocos (corte XY): painéis lado a lado, como
uma lista à esquerda e a descrição à direita, são lidos um de cada vez. Sem isso, o
EasyOCR lia linha a linha da tela inteira e picava a descrição entre os itens.

Nos 90 prints do benchmark (10 jogos, em 2026-11-15), as regras acharam 74% das
quebras dos gabaritos, e 86% das quebras que puseram estavam certas (antes dos
blocos e das regras de 2026-11-15: 69% e 78%).
"""

import math
import re
import statistics
from dataclasses import dataclass, field

# Proporções da altura típica das letras (ou da largura típica de uma letra)
VAO_PARAGRAFO = 0.8  # espaço entre linhas maior que o normal
RECUO = 1.5  # mudança na margem esquerda
FONTE = 1.5  # letra bem maior ou menor: título, nome de quem fala
ESTICADA = 1.4  # letras mais largas que o normal: "Nome ..... Lv.15" numa caixa só
MINIMO_ESTICADA = 8  # em linhas mais curtas, a largura média da letra não é confiável
VAO_COLUNAS = 1.5  # vão entre caixas da mesma linha: "Rótulo ..... valor"
CORTE_COLUNA = 0.8  # vão que separa um rótulo à esquerda de um bloco de texto
CENTRALIZADO = 1.0  # centros de duas linhas mais perto que isso: texto centralizado

# Blocos (corte XY), também em alturas de letra
VAO_BLOCO_HORIZONTAL = 1.0  # faixa vazia que separa blocos de cima e de baixo
VAO_BLOCO_VERTICAL = 3.0  # faixa vazia que separa painéis lado a lado
MINIMO_LINHAS_BLOCO = 2  # rótulos soltos (opções de uma roda de diálogo) não viram painel
FRACAO_VALORES = 0.7  # coluna da direita com tantos valores é tabela, não painel

# Caixas de desenho: barra de vida, coluna de ícones, logotipo
LIXO_ALTURA = 3.0  # muito mais alta que o texto típico...
LIXO_LETRAS = 3  # ...e com quase nada escrito
INCLINACAO_MINIMA = 0.05  # abaixo disso o texto é tratado como reto

MARCADORES = "•-*►▶◆●·"
# Verbete de efeito: "[Shield] Negates part of..." (com minúscula, é só uma frase quebrada)
VERBETE = re.compile(r"\[[^\]]+\]\s*(\w)")
# A linha de cima termina uma frase ou um rótulo
FIM_DE_FRASE = re.compile(r"[.!?:;)\]]$")


def _limites(item) -> tuple:
    """(esquerda, direita, topo, base) de uma caixa do EasyOCR."""
    xs = [ponto[0] for ponto in item[0]]
    ys = [ponto[1] for ponto in item[0]]
    return min(xs), max(xs), min(ys), max(ys)


def _texto(item) -> str:
    return " ".join(str(item[1]).split())


def _altura_caixa(item) -> float:
    _, _, topo, base = _limites(item)
    return base - topo


def _centro_vertical(item) -> float:
    _, _, topo, base = _limites(item)
    return (topo + base) / 2


def _filtrar_lixo(itens: list) -> list:
    """Descarta caixas de desenho lidas como texto.

    Ex.: a coluna de "×" do inventário do Persona virou um "1" de 382 px de altura,
    e a barra de vida virou um "=". Elas juntavam linhas que não tinham nada a ver.
    """
    if len(itens) < 3:
        return itens
    tipica = statistics.median(_altura_caixa(item) for item in itens)
    return [
        item
        for item in itens
        if _altura_caixa(item) <= LIXO_ALTURA * tipica
        or len(_texto(item).replace(" ", "")) > LIXO_LETRAS
    ]


def _endireitar(itens: list) -> list:
    """Gira as caixas pela inclinação mediana quando o texto todo está inclinado.

    O EasyOCR devolve os cantos girados para texto inclinado (o título do
    Danganronpa tem inclinação ~0,21); sem endireitar, as palavras de linhas
    diferentes se misturavam. Em texto reto a inclinação é 0 e nada muda.
    """
    inclinacoes = []
    for item in itens:
        pontos = item[0]
        largura = pontos[1][0] - pontos[0][0]
        if largura > 2 * _altura_caixa(item):
            inclinacoes.append((pontos[1][1] - pontos[0][1]) / largura)
    if not inclinacoes or abs(statistics.median(inclinacoes)) < INCLINACAO_MINIMA:
        return itens
    angulo = -math.atan(statistics.median(inclinacoes))
    cos, sen = math.cos(angulo), math.sin(angulo)
    return [
        ([[x * cos - y * sen, x * sen + y * cos] for x, y in item[0]],) + tuple(item[1:])
        for item in itens
    ]


def agrupar_em_linhas(resultados) -> list:
    """Agrupa as caixas do EasyOCR em linhas, de cima para baixo e da esquerda para a direita.

    O EasyOCR devolve as caixas inclinadas no fim da lista, o que jogava trechos
    como "your key:" para o final do texto.
    """
    caixas = []
    for item in resultados:
        _, _, topo, base = _limites(item)
        caixas.append(((topo + base) / 2, base - topo, item))
    caixas.sort(key=lambda caixa: caixa[0])

    linhas = []
    for centro, altura, item in caixas:
        if linhas:
            linha = linhas[-1]
            # Mesma linha quando o centro está a menos de meia altura de texto do centro
            # médio da linha. Medir só pela primeira caixa falhava quando ela era pequena,
            # como o "*" no começo das falas do Undertale.
            media = statistics.mean(linha["centros"])
            if abs(centro - media) < min(altura, linha["altura"]) / 2:
                linha["itens"].append(item)
                linha["centros"].append(centro)
                linha["altura"] = max(linha["altura"], altura)
                continue
        linhas.append({"centros": [centro], "altura": altura, "itens": [item]})

    return [sorted(linha["itens"], key=lambda item: _limites(item)[0]) for linha in linhas]


@dataclass
class Linha:
    """Uma linha de texto na tela: caixas do OCR lado a lado, da esquerda para a direita."""

    itens: list
    esq: float = field(init=False)
    dir: float = field(init=False)
    topo: float = field(init=False)
    base: float = field(init=False)
    altura: float = field(init=False)
    texto: str = field(init=False)

    def __post_init__(self) -> None:
        limites = [_limites(item) for item in self.itens]
        self.esq = limites[0][0]
        self.dir = max(lim[1] for lim in limites)
        self.topo = min(lim[2] for lim in limites)
        self.base = max(lim[3] for lim in limites)
        self.altura = statistics.median(lim[3] - lim[2] for lim in limites)
        self.texto = " ".join(_texto(item) for item in self.itens)

    @property
    def largura_letra(self) -> float:
        """Largura média de um caractere, pela caixa e pelo número de letras."""
        return max((self.dir - self.esq) / max(len(self.texto), 1), 1.0)

    def vaos_internos(self) -> list:
        """Espaço entre cada caixa e a seguinte, na mesma linha."""
        limites = [_limites(item) for item in self.itens]
        return [depois[0] - antes[1] for antes, depois in zip(limites, limites[1:])]


def _linhas(itens: list) -> list:
    return _separar_colunas([Linha(grupo) for grupo in agrupar_em_linhas(itens)])


def _separar_colunas(linhas: list) -> list:
    """Separa um rótulo que fica à esquerda de um bloco de texto.

    Ex.: "Stage Effect    P.DMG -30%. Starting from..." com as linhas de baixo
    começando no mesmo x de "P.DMG": "Stage Effect" é uma coluna à parte.
    """
    resultado = []
    for i, linha in enumerate(linhas):
        vizinhas = [linhas[j].esq for j in (i - 1, i + 1) if 0 <= j < len(linhas)]
        corte = None
        for k, vao in enumerate(linha.vaos_internos(), start=1):
            esquerda = _limites(linha.itens[k])[0]
            alinhada = any(abs(esquerda - x) < linha.altura / 2 for x in vizinhas)
            if vao > CORTE_COLUNA * linha.altura and alinhada:
                corte = k
                break
        if corte is None:
            resultado.append(linha)
        else:
            resultado += [Linha(linha.itens[:corte]), Linha(linha.itens[corte:])]
    return resultado


# ---------------------------------------------------------------- blocos (corte XY)
def _e_valor(texto: str) -> bool:
    """Valor de tabela: "4 SP", "28 points", "3/56", "17 +5 25" (começa com número)."""
    palavras = texto.split()
    return bool(palavras and re.search(r"\d", palavras[0]))


def _pares_de_valor(itens: list, altura: float) -> set:
    """Pares "Rótulo ....... valor": o valor é a caixa mais próxima à direita, na mesma
    linha, quando ela começa com número e o rótulo não. Devolve (id rótulo, id valor)."""
    limites = [_limites(item) for item in itens]
    pares = set()
    for i, item in enumerate(itens):
        if _e_valor(_texto(item)):
            continue
        esq, dir_, topo, base = limites[i]
        centro = (topo + base) / 2
        vizinhas = [
            j
            for j, (e, _, t, b) in enumerate(limites)
            if j != i and e > dir_ and abs((t + b) / 2 - centro) < altura / 2
        ]
        if vizinhas:
            j = min(vizinhas, key=lambda k: limites[k][0])
            if _e_valor(_texto(itens[j])) and esq < limites[j][0]:
                pares.add((id(item), id(itens[j])))
    return pares


def _vaos(intervalos: list) -> list:
    """Faixas vazias entre os intervalos (ini, fim), de cima para baixo ou da esquerda."""
    intervalos = sorted(intervalos)
    vaos, fim = [], intervalos[0][1]
    for inicio, fim_atual in intervalos[1:]:
        if inicio > fim:
            vaos.append((fim, inicio))
        fim = max(fim, fim_atual)
    return vaos


def _coluna_de_valores(esquerda: list, direita: list, altura: float) -> bool:
    """A direita é a coluna de valores das linhas da esquerda (uma tabela)."""
    linhas = agrupar_em_linhas(direita)
    textos = [" ".join(_texto(item) for item in linha) for linha in linhas]
    if sum(_e_valor(texto) for texto in textos) < FRACAO_VALORES * len(textos):
        return False
    centros = [_centro_vertical(item) for item in esquerda]
    alinhadas = sum(
        any(abs(statistics.mean(_centro_vertical(item) for item in linha) - c) < altura / 2
            for c in centros)
        for linha in linhas
    )
    return alinhadas >= FRACAO_VALORES * len(linhas)


def _pode_separar(esquerda: list, direita: list, altura: float, pares: set) -> bool:
    """Separar em painéis só quando os dois lados são painéis de verdade, não tabela."""
    if min(len(agrupar_em_linhas(esquerda)), len(agrupar_em_linhas(direita))) < MINIMO_LINHAS_BLOCO:
        return False
    if _coluna_de_valores(esquerda, direita, altura):
        return False
    ids_esquerda, ids_direita = {id(i) for i in esquerda}, {id(i) for i in direita}
    separados = sum(a in ids_esquerda and b in ids_direita for a, b in pares)
    return separados < 2


def _blocos(itens: list, altura: float, pares: set) -> list:
    """Corte XY: faixas horizontais vazias e, dentro delas, colunas vazias."""
    if len(itens) < 2:
        return [itens]

    # Faixas horizontais: não mudam a ordem, só deixam achar os painéis dentro delas
    cortes = [
        (inicio + fim) / 2
        for inicio, fim in _vaos([_limites(item)[2:] for item in itens])
        if fim - inicio >= VAO_BLOCO_HORIZONTAL * altura
    ]
    if cortes:
        faixas = {}
        for item in itens:
            faixa = sum(_centro_vertical(item) > corte for corte in cortes)
            faixas.setdefault(faixa, []).append(item)
        return [
            bloco for _, faixa in sorted(faixas.items()) for bloco in _blocos(faixa, altura, pares)
        ]

    # Painéis lado a lado: tenta do maior vão vertical para o menor
    vaos = _vaos([_limites(item)[:2] for item in itens])
    for inicio, fim in sorted(vaos, key=lambda vao: vao[0] - vao[1]):
        if fim - inicio < VAO_BLOCO_VERTICAL * altura:
            break
        corte = (inicio + fim) / 2
        esquerda = [item for item in itens if _limites(item)[1] <= corte]
        direita = [item for item in itens if _limites(item)[0] >= corte]
        if _pode_separar(esquerda, direita, altura, pares):
            return _blocos(esquerda, altura, pares) + _blocos(direita, altura, pares)
    return [itens]


# ---------------------------------------------------------------- parágrafos
def _comeca_com_marcador(texto: str) -> bool:
    verbete = VERBETE.match(texto)
    return texto[:1] in MARCADORES or bool(verbete and verbete.group(1).isupper())


def _item_solto(linha: Linha, altura: float, letra: float) -> bool:
    """Linha que é um item sozinho: nome com o nível na direita, rótulo e valor."""
    esticada = len(linha.texto) >= MINIMO_ESTICADA and linha.largura_letra > ESTICADA * letra
    return esticada or max(linha.vaos_internos(), default=0) > VAO_COLUNAS * altura


def _recuou(anterior: Linha, seguinte: Linha, altura: float) -> bool:
    """Mudou a margem esquerda, a não ser em texto centralizado (legendas, cartazes)."""
    if abs(seguinte.esq - anterior.esq) <= RECUO * altura:
        return False
    centro_anterior = (anterior.esq + anterior.dir) / 2
    centro_seguinte = (seguinte.esq + seguinte.dir) / 2
    return abs(centro_anterior - centro_seguinte) >= CENTRALIZADO * altura


def _continua_frase(anterior: Linha, seguinte: Linha) -> bool:
    """A linha de baixo começa com minúscula e a de cima não fechou a frase.

    Ex.: "Sensei! Mind your / health, okay?". Linha de uma palavra só ("duties",
    "rules") é tópico de menu, não continuação.
    """
    return (
        seguinte.texto[:1].islower()
        and not FIM_DE_FRASE.search(anterior.texto)
        and len(seguinte.texto.split()) >= 2
    )


def _menu_de_palavras(anterior: Linha, seguinte: Linha) -> bool:
    """Menu de uma palavra por linha: "Skill / Item / Equip / Persona"."""
    return (
        len(anterior.texto.split()) == 1
        and len(seguinte.texto.split()) == 1
        and seguinte.texto[:1].isupper()
        and not anterior.texto.endswith(",")
    )


def _comeca_paragrafo(
    anterior: Linha, seguinte: Linha, margem_dir: float, altura: float, letra: float
) -> bool:
    vao = seguinte.topo - anterior.base > VAO_PARAGRAFO * altura
    razao_fonte = seguinte.altura / max(anterior.altura, 1.0)
    outra_fonte = not 1 / FONTE <= razao_fonte <= FONTE
    if _continua_frase(anterior, seguinte):
        return vao or outra_fonte

    # A primeira palavra da seguinte caberia no fim da anterior: a anterior acabou ali.
    # A margem é a do print inteiro: medir por bloco juntou itens curtos de menu.
    primeira = seguinte.texto.split()[0]
    cabia = margem_dir - anterior.dir > (len(primeira) + 1) * seguinte.largura_letra
    return (
        vao
        or cabia
        or outra_fonte
        or _recuou(anterior, seguinte, altura)
        or _item_solto(anterior, altura, letra)
        or _item_solto(seguinte, altura, letra)
        or _comeca_com_marcador(seguinte.texto)
        or _menu_de_palavras(anterior, seguinte)
    )


def montar_paragrafos(resultados) -> list:
    """Resultados do EasyOCR -> lista de parágrafos (cada um já numa linha só)."""
    itens = [item for item in resultados if len(item) >= 2 and _texto(item)]
    itens = _endireitar(_filtrar_lixo(itens))
    todas = _linhas(itens)
    if not todas:
        return []

    # Medidas típicas do print, para as regras valerem em qualquer resolução
    altura = statistics.median(linha.altura for linha in todas)
    letra = statistics.median(linha.largura_letra for linha in todas)
    margem_dir = max(linha.dir for linha in todas)

    paragrafos = []
    for bloco in _blocos(itens, altura, _pares_de_valor(itens, altura)):
        linhas = _linhas(bloco)
        atuais = [[linhas[0].texto]]
        for anterior, seguinte in zip(linhas, linhas[1:]):
            if _comeca_paragrafo(anterior, seguinte, margem_dir, altura, letra):
                atuais.append([seguinte.texto])
            else:
                atuais[-1].append(seguinte.texto)
        paragrafos += [" ".join(partes) for partes in atuais]
    return paragrafos
