"""Junta as linhas lidas pelo OCR em parágrafos, para a tradução respeitar as quebras.

Texto na tela tem dois tipos de quebra de linha:
- a de verdade, entre título, parágrafo, item de menu ou efeito;
- a visual, quando a frase não coube na largura da caixa e continuou embaixo.

Só a primeira deve chegar ao tradutor: cortar uma frase no meio estraga a tradução,
e o texto traduzido tem outro tamanho, então a quebra visual não serviria de qualquer
jeito. As regras usam só a posição das caixas do OCR (RapidOCR ou EasyOCR), sempre em
proporção ao tamanho das letras, para valer em qualquer resolução.

Antes das linhas, o print é dividido em blocos (corte XY): painéis lado a lado, como
uma lista à esquerda e a descrição à direita, são lidos um de cada vez. Sem isso, o
app lia linha a linha da tela inteira e picava a descrição entre os itens. As colunas
de ficha, grade e tabela também viram blocos: a faixa vazia entre elas pode ser
estreita, mas se repete em várias linhas seguidas. Dentro de uma linha, itens lado a
lado (menu, abas, botões) viram linhas separadas.

As regras valem para qualquer língua de origem. Em árabe, persa, urdu e uigur as
caixas são espelhadas, para a leitura ir da direita para a esquerda. Em chinês,
japonês e tailandês, que não usam espaço, os pedaços são juntados sem espaço e uma
linha "cabe" mais uma letra, não mais uma palavra.

Nos 90 prints do benchmark (11 jogos), com o RapidOCR, as colunas estreitas, os itens
lado a lado e as regras de aviso e título (2026-11-17), as regras acharam 88% das quebras
dos gabaritos, e 89% das quebras que puseram estavam certas (com o EasyOCR, antes dos
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

# Colunas de ficha, grade e tabela: a faixa vazia entre elas pode ser estreita (na ficha
# do Morrowind, os números da esquerda encostam na coluna da direita: 0,2 altura), mas
# se repete em várias linhas seguidas, o que não acontece num parágrafo.
VAO_COLUNA_ESTREITA = 0.2  # faixa mínima, em alturas de letra
APOIO_COLUNA = 3  # linhas com texto dos dois lados da faixa
# Campos de um mesmo registro têm tipos diferentes ("12 km | Jita | Stargate"): quando um
# lado tem número em quase todas as linhas e o outro em quase nenhuma, a linha é lida inteira
DIFERENCA_TIPOS = 0.8

# Itens lado a lado na mesma linha: menus ("FIGHT ACT ITEM MERCY"), abas, botões. O vão
# não serve para achá-los (rótulo e valor têm vãos ainda maiores); o conteúdo serve.
# Mas o vão precisa ser maior que um espaço entre palavras: com uma caixa por palavra,
# uma fala em maiúsculas viraria uma palavra por linha.
VAO_ITENS = 0.8  # em alturas de letra
MINIMO_ITENS = 3  # caixas curtas numa linha para ela ser uma fila de itens
PALAVRAS_ITEM = 3  # um item de menu, aba ou botão tem até 3 palavras

# Caixas de desenho: barra de vida, coluna de ícones, logotipo
LIXO_ALTURA = 3.0  # muito mais alta que o texto típico...
LIXO_LETRAS = 3  # ...e com quase nada escrito
INCLINACAO_MINIMA = 0.05  # abaixo disso o texto é tratado como reto

# Línguas escritas da direita para a esquerda (códigos do EasyOCR)
IDIOMAS_DA_DIREITA = frozenset({"ar", "fa", "ur", "ug"})
# Escritas sem espaço entre palavras: chinês, japonês (kana), tailandês e a pontuação
# de largura cheia. O coreano usa espaço e fica de fora.
SEM_ESPACO = re.compile(r"[฀-๿　-ヿ㐀-鿿豈-﫿＀-￯]")
MENU_SEM_ESPACO = 8  # nessas escritas, opção de menu tem até 8 letras

# Começo de item ou entrada; ":" é o "::" do registro de mensagens do Caves of Qud
MARCADORES = "•-*►▶◆●·:"
# Verbete de efeito: "[Shield] Negates part of..." (com minúscula, é só uma frase quebrada)
VERBETE = re.compile(r"\[[^\]]+\]\s*(\w)")
# A linha de cima termina uma frase ou um rótulo
FIM_DE_FRASE = re.compile(r"[.!?:;)\]]$")
# A linha de cima termina uma sentença
FIM_DE_SENTENCA = re.compile(r"[.!?]$")
TITULO_PALAVRAS = 5  # um título tem até 5 palavras


def _limites(item) -> tuple:
    """(esquerda, direita, topo, base) de uma caixa do EasyOCR."""
    xs = [ponto[0] for ponto in item[0]]
    ys = [ponto[1] for ponto in item[0]]
    return min(xs), max(xs), min(ys), max(ys)


def _texto(item) -> str:
    return " ".join(str(item[1]).split())


def _juntar(partes: list) -> str:
    """Junta pedaços de texto com espaço, menos entre dois pedaços de escrita sem espaço
    ("この城の" + "地下に" vira "この城の地下に", e não "この城の 地下に")."""
    texto = ""
    for parte in partes:
        if texto and parte and not (SEM_ESPACO.match(texto[-1]) and SEM_ESPACO.match(parte[0])):
            texto += " "
        texto += parte
    return texto


def _espelhar(item) -> tuple:
    """Espelha a caixa na horizontal, para ler escrita da direita para a esquerda com as
    mesmas regras: o começo da linha (à direita) vira a esquerda. A ordem dos cantos é
    refeita para o canto de cima à esquerda continuar sendo o primeiro."""
    p0, p1, p2, p3 = [(-x, y) for x, y in item[0]]
    return ([list(p1), list(p0), list(p3), list(p2)],) + tuple(item[1:])


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
    # Só texto ASCII pode ser descartado: em chinês ou japonês, três letras grandes
    # são uma palavra inteira, como o título "第一章"
    return [
        item
        for item in itens
        if _altura_caixa(item) <= LIXO_ALTURA * tipica
        or len(_texto(item).replace(" ", "")) > LIXO_LETRAS
        or not _texto(item).isascii()
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
    """Uma linha de texto na tela: caixas do OCR lado a lado, da esquerda para a direita.

    item_novo marca um item de menu, aba ou botão separado do item à esquerda: ele
    sempre começa um parágrafo.
    """

    itens: list
    item_novo: bool = False
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
        self.texto = _juntar([_texto(item) for item in self.itens])

    @property
    def largura_letra(self) -> float:
        """Largura média de um caractere, pela caixa e pelo número de letras."""
        return max((self.dir - self.esq) / max(len(self.texto), 1), 1.0)

    def vaos_internos(self) -> list:
        """Espaço entre cada caixa e a seguinte, na mesma linha."""
        limites = [_limites(item) for item in self.itens]
        return [depois[0] - antes[1] for antes, depois in zip(limites, limites[1:])]


def _linhas(itens: list) -> list:
    linhas = _separar_colunas([Linha(grupo) for grupo in agrupar_em_linhas(itens)])
    return [parte for linha in linhas for parte in _separar_itens(linha)]


def _e_item(texto: str) -> bool:
    """Texto de item de menu, aba ou botão: curto, sem número no começo, primeira letra
    maiúscula e sem pontuação de frase no fim. Escritas sem maiúscula ficam de fora."""
    letra = next((c for c in texto if c.isalpha()), "")
    return (
        len(texto.split()) <= PALAVRAS_ITEM
        and not _e_valor(texto)
        and letra.isupper()
        and texto[-1:] not in ",;:—-"
    )


def _em_maiusculas(texto: str) -> bool:
    return texto.isupper() and not _e_valor(texto)


def _mesma_aba(esquerda: str, direita: str, total: int) -> bool:
    """Duas abas com uma palavra em comum na ponta: "Skill Plans" | "Skill Catalogue",
    "Certified Plans" | "Personal Plans"."""
    palavras_esq = esquerda.lower().split()
    palavras_dir = direita.lower().split()
    return (
        total == 2
        and _e_item(esquerda) and _e_item(direita)
        and not esquerda.isupper() and not direita.isupper()
        and min(len(palavras_esq), len(palavras_dir)) >= 2
        and (palavras_esq[0] == palavras_dir[0] or palavras_esq[-1] == palavras_dir[-1])
    )


def _separar_itens(linha: Linha) -> list:
    """Separa itens lado a lado da mesma linha: cada item vira uma linha.

    Uma fila de MINIMO_ITENS caixas que são todas itens (menu, abas) é separada inteira.
    Fora isso, separa duas caixas vizinhas em maiúsculas ("FIGHT" | "ACT") ou duas abas
    com a mesma primeira palavra. Nos dois casos, só com vão maior que um espaço.
    """
    textos = [_texto(item) for item in linha.itens]
    vaos_ok = [vao >= VAO_ITENS * linha.altura for vao in linha.vaos_internos()]
    if len(textos) >= MINIMO_ITENS and all(vaos_ok) and all(_e_item(t) for t in textos):
        grupos = [[item] for item in linha.itens]
    else:
        grupos = [[linha.itens[0]]]
        for k, item in enumerate(linha.itens[1:]):
            esquerda, direita = textos[k], textos[k + 1]
            if vaos_ok[k] and (
                (_em_maiusculas(esquerda) and _em_maiusculas(direita))
                or _mesma_aba(esquerda, direita, len(textos))
            ):
                grupos.append([item])
            else:
                grupos[-1].append(item)
    if len(grupos) == 1:
        return [linha]
    return [Linha(grupo, item_novo=k > 0) for k, grupo in enumerate(grupos)]


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


def _parece_coluna(itens: list, corte: float) -> bool:
    """Uma faixa estreita no x = corte separa colunas de verdade?

    Precisa de APOIO_COLUNA linhas com texto dos dois lados. Não é coluna quando, na
    maioria dessas linhas, a direita continua a frase da esquerda (um parágrafo lido
    palavra a palavra, com os vãos alinhados por acaso), nem quando os dois lados têm
    tipos diferentes, como os campos de uma tabela de registros.
    """
    lados = []
    for linha in agrupar_em_linhas(itens):
        esquerda = [item for item in linha if _limites(item)[1] <= corte]
        direita = [item for item in linha if _limites(item)[0] >= corte]
        if esquerda and direita:
            lados.append((_texto(esquerda[-1]), _texto(direita[0]), esquerda, direita))
    if len(lados) < APOIO_COLUNA:
        return False

    continua = sum(
        inicio[:1].islower() and not FIM_DE_FRASE.search(fim) for fim, inicio, _, _ in lados
    )
    if continua > len(lados) / 2:
        return False

    def com_numero(caixas: list) -> float:
        return any(re.search(r"\d", _texto(item)) for item in caixas)

    numeros_esquerda = sum(com_numero(esquerda) for _, _, esquerda, _ in lados) / len(lados)
    numeros_direita = sum(com_numero(direita) for _, _, _, direita in lados) / len(lados)
    return abs(numeros_esquerda - numeros_direita) <= DIFERENCA_TIPOS


def _separar_por_titulo(itens: list, altura: float, pares: set) -> list:
    """Colunas que um título ou uma linha cheia atravessa.

    Na ficha do Morrowind, o nome do personagem em cima ("OHM") cruza a faixa entre as
    colunas. A faixa é procurada só nas linhas de duas caixas ou mais; se apenas linhas
    de uma caixa a atravessam, cada uma vira um bloco à parte, e o resto é cortado de novo.
    """
    linhas = agrupar_em_linhas(itens)
    com_colunas = [item for linha in linhas if len(linha) >= 2 for item in linha]
    if len(com_colunas) < 2:
        return [itens]
    vaos = _vaos([_limites(item)[:2] for item in com_colunas])
    for inicio, fim in sorted(vaos, key=lambda vao: vao[0] - vao[1]):
        if fim - inicio < VAO_COLUNA_ESTREITA * altura:
            break
        corte = (inicio + fim) / 2
        cruzam = {
            k for k, linha in enumerate(linhas)
            if any(_limites(item)[0] < corte < _limites(item)[1] for item in linha)
        }
        if not cruzam or any(len(linhas[k]) > 1 for k in cruzam):
            continue
        if not _parece_coluna(itens, corte):
            continue
        resto = [item for k, linha in enumerate(linhas) if k not in cruzam for item in linha]
        if not _pode_separar(*_lados(resto, corte), altura, pares):
            continue
        partes = _cortar_nas_linhas(linhas, cruzam)
        return [bloco for parte in partes for bloco in _blocos(parte, altura, pares)]
    return [itens]


def _lados(itens: list, corte: float) -> tuple:
    """As caixas inteiras à esquerda e as inteiras à direita do x = corte."""
    return (
        [item for item in itens if _limites(item)[1] <= corte],
        [item for item in itens if _limites(item)[0] >= corte],
    )


def _cortar_nas_linhas(linhas: list, separadoras: set) -> list:
    """Divide as linhas em partes; cada linha separadora vira uma parte sozinha."""
    partes, atual = [], []
    for k, linha in enumerate(linhas):
        if k in separadoras:
            partes += [atual, list(linha)] if atual else [list(linha)]
            atual = []
        else:
            atual += linha
    return partes + [atual] if atual else partes


def _blocos(itens: list, altura: float, pares: set) -> list:
    """Corte XY: faixas horizontais vazias e, dentro delas, colunas vazias.

    Painéis separados por uma faixa larga (VAO_BLOCO_VERTICAL) são cortados direto.
    Faixas estreitas só cortam colunas de ficha, grade ou tabela (_parece_coluna).
    """
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
        if fim - inicio < VAO_COLUNA_ESTREITA * altura:
            break
        corte = (inicio + fim) / 2
        if fim - inicio < VAO_BLOCO_VERTICAL * altura and not _parece_coluna(itens, corte):
            continue
        esquerda, direita = _lados(itens, corte)
        if _pode_separar(esquerda, direita, altura, pares):
            return _blocos(esquerda, altura, pares) + _blocos(direita, altura, pares)
    return _separar_por_titulo(itens, altura, pares)


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


def _parece_titulo(texto: str) -> bool:
    """Linha curta com cara de título: até TITULO_PALAVRAS palavras, sem pontuação no
    fim, e todas as palavras começando com maiúscula. "Surrender to" (fala quebrada) e
    "Der Kapitän der Flotte" (alemão, que põe maiúscula em todo substantivo) não são
    títulos; escritas sem maiúscula ficam de fora."""
    palavras = texto.split()
    iniciais = [next((c for c in p if c.isalpha()), "") for p in palavras]
    iniciais = [c for c in iniciais if c]
    return (
        1 <= len(palavras) <= TITULO_PALAVRAS
        and not FIM_DE_FRASE.search(texto)
        and texto[-1:] not in ",;-"
        and bool(iniciais)
        and all(c.isupper() for c in iniciais)
    )


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
    """Menu de uma palavra por linha: "Skill / Item / Equip / Persona".

    Em escrita sem espaço e sem maiúscula ("はじめから / つづきから / 設定"), valem
    duas linhas curtas, a de cima sem vírgula no fim: fala quebrada tem linha comprida.
    """
    if SEM_ESPACO.match(anterior.texto) and SEM_ESPACO.match(seguinte.texto):
        return (
            max(len(anterior.texto), len(seguinte.texto)) <= MENU_SEM_ESPACO
            and anterior.texto[-1] not in "、，,"
        )
    return (
        len(anterior.texto.split()) == 1
        and len(seguinte.texto.split()) == 1
        and seguinte.texto[:1].isupper()
        and not anterior.texto.endswith(",")
    )


def _comeca_paragrafo(
    anterior: Linha, seguinte: Linha, margem_dir: float, altura: float, letra: float
) -> bool:
    if seguinte.item_novo:
        return True
    # Sentença terminada e a de baixo não continua com minúscula: avisos seguidos
    # ("...increased to 66." / "Item does not have enough charge.")
    if FIM_DE_SENTENCA.search(anterior.texto) and not seguinte.texto[:1].islower():
        return True
    # Título em cima e texto começando com minúscula embaixo ("Wood Technique Chant" /
    # "swept by the wind..."): sem isto, a regra da minúscula juntava os dois
    if seguinte.texto[:1].islower() and _parece_titulo(anterior.texto):
        return True
    vao = seguinte.topo - anterior.base > VAO_PARAGRAFO * altura
    razao_fonte = seguinte.altura / max(anterior.altura, 1.0)
    outra_fonte = not 1 / FONTE <= razao_fonte <= FONTE
    if _continua_frase(anterior, seguinte):
        return vao or outra_fonte

    # A primeira palavra da seguinte caberia no fim da anterior: a anterior acabou ali.
    # A margem é a do print inteiro: medir por bloco juntou itens curtos de menu.
    # Em escrita sem espaço, a linha quebra em qualquer letra: basta caber uma.
    primeira = seguinte.texto[:1] if SEM_ESPACO.match(seguinte.texto) else seguinte.texto.split()[0]
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


def montar_paragrafos(resultados, idioma: str = "") -> list:
    """Resultados do EasyOCR -> lista de parágrafos (cada um já numa linha só).

    idioma é o código do texto lido (o do EasyOCR); em árabe, persa, urdu e uigur
    a leitura vai da direita para a esquerda.
    """
    itens = [item for item in resultados if len(item) >= 2 and _texto(item)]
    if (idioma or "").lower() in IDIOMAS_DA_DIREITA:
        itens = [_espelhar(item) for item in itens]
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
        paragrafos += [_juntar(partes) for partes in atuais]
    return paragrafos
