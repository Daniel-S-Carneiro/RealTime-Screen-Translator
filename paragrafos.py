"""Junta as linhas lidas pelo OCR em parágrafos, para a tradução respeitar as quebras.

Texto na tela tem dois tipos de quebra de linha:
- a de verdade, entre título, parágrafo, item de menu ou efeito;
- a visual, quando a frase não coube na largura da caixa e continuou embaixo.

Só a primeira deve chegar ao tradutor: cortar uma frase no meio estraga a tradução,
e o texto traduzido tem outro tamanho, então a quebra visual não serviria de qualquer
jeito. As regras usam a posição das caixas do OCR (RapidOCR ou EasyOCR), sempre em
proporção ao tamanho das letras, para valer em qualquer resolução. Duas olham a imagem:
a das abas de uma palavra encostadas, que acha a aba selecionada pelo fundo, e a da barra
de menu lida numa caixa só, que mede o espaço entre as palavras na tinta.

Antes das linhas, o print é dividido em blocos (corte XY): painéis lado a lado, como
uma lista à esquerda e a descrição à direita, são lidos um de cada vez. Sem isso, o
app lia linha a linha da tela inteira e picava a descrição entre os itens. As colunas
de ficha, grade e tabela também viram blocos: a faixa vazia entre elas pode ser
estreita, mas se repete em várias linhas seguidas. Dentro de uma linha, itens lado a
lado (menu, abas, botões) viram linhas separadas. Uma pilha de linhas curtas com cara de
item (menu vertical, lista de características) quebra em cada linha, mesmo quando o
primeiro item é o mais largo. Numa lista em que um item quebrou em duas linhas, as duas
ficam mais perto uma da outra do que os itens entre si: elas são juntadas.

As regras valem para qualquer língua de origem. Em árabe, persa, urdu e uigur as
caixas são espelhadas, para a leitura ir da direita para a esquerda. Em chinês,
japonês e tailandês, que não usam espaço, os pedaços são juntados sem espaço e uma
linha "cabe" mais uma letra, não mais uma palavra.

Nos 90 prints do benchmark (11 jogos), com o RapidOCR e todas as regras até 2026-11-18,
as regras acharam 92% das quebras dos gabaritos, e 91% das quebras que puseram estavam
certas (com o EasyOCR, antes dos blocos e das regras de 2026-11-15: 69% e 78%).
"""

# As regras de montagem dependem umas das outras (linhas, blocos, itens, quebras) e foram
# medidas juntas: ficam num módulo só, mesmo passando de mil linhas.
# pylint: disable=too-many-lines

import math
import re
import statistics
from dataclasses import dataclass, field, replace

import numpy as np

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
ALINHAMENTO = 0.5  # bordas ou centros mais perto que isso (em alturas): caixas alinhadas
DISTANCIA_CABECALHO = 1.5  # cabeçalho de tabela fica até 1,5 altura acima da 1ª linha

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
# Última palavra de uma fala, sozinha na linha de baixo: "llegada.", "quieres.", "want."
# (24/11/2026). Tópico de menu de uma palavra ("duties", "rules") não tem pontuação.
PALAVRA_FINAL = re.compile(r"[.!?…。！？][\"'”’»)\]]*$")
# Frase que termina no fim da linha não quebra o parágrafo se a linha de baixo encosta na
# de cima (proposta do Mistral, 24/11/2026). O vão é o passo menos a altura da linha de
# cima, em alturas de letra. Nos 140 prints, as emendas vão até 0,10 e os avisos, títulos
# e respostas separadas começam em 0,24.
FIM_COLADO = 0.18
FIM_FONTE = 1.4  # alturas tão diferentes (título de fonte grande) quebram mesmo coladas

# Descrição de item centralizada, uma propriedade por linha (Path of Exile, painel do
# Stardew), problema 10 da consulta às IAs (24/11/2026): estrutura do Mistral, prova de
# centralização do Grok, e as travas da vírgula e da linha larga medidas nos 140 prints.
# Propriedade não termina frase; a frase quebrada tem as linhas de dentro "cheias".
DESCRICAO_ESQUERDA = 0.5  # a margem esquerda varia isso em algum par: texto centralizado
DESCRICAO_LARGA = 8.0  # alguma linha do grupo tem essa largura ("POINTS / TO GO" não tem);
# de 6 a 9,7 alturas dá o mesmo resultado nos 140 prints
DESCRICAO_CHEIA = 0.82  # linha "cheia": essa fração da mais larga do grupo
DESCRICAO_VAO = 0.45  # vão entre as caixas (em alturas) que separa itens mesmo cheios
FRASE_FECHADA = re.compile(r"[.!?…。！？؟][\"'”’»)\]]*$")  # fim de frase, talvez com fecho
TITULO_PALAVRAS = 5  # um título tem até 5 palavras

# Margem do "caberia" num painel estreito sem borda visível (o diálogo do Morrowind, o
# tutorial do Qud): a borda do print fica longe e quase toda linha parece acabar cedo.
# As linhas longas vizinhas, com a mesma esquerda, mostram onde o painel acaba.
LINHA_LONGA = 16.0  # em alturas de letra: linha que enche o painel (menu não chega a isso)
VIZINHAS = 2  # linhas olhadas acima e abaixo
MESMA_ESQUERDA = 1.0  # em alturas de letra
ALTURA_PARECIDA = (0.8, 1.25)  # da altura típica: título e nota de rodapé não contam
FOLGA_PRINT = 4.0  # a margem do painel só vale se ficar tão para dentro do print

# Listas de "rótulo valor" ("Endurance 41" / "Personality 30" / "Luck 40", "Born: ..." /
# "Total Net Worth:"): a lista encosta na borda direita do print, o "caberia" nunca acha
# espaço e nenhuma regra quebra. O sinal é a repetição: linhas curtas seguidas, cada uma
# terminando em número ou com ":" de rótulo. Uma só ("...founded in 1990", "...magic:")
# acontece em prosa.
CAMPO_LARGURA = 16.0  # em alturas de letra: mais longa que isso é frase, não campo
CAMPO_PALAVRAS = 8
CAMPOS_SEGUIDOS = 3  # linhas da lista, no mínimo
CAMPO_VAO = 0.8  # vão vertical máximo entre dois campos, em alturas de letra
CAMPO_SOBREPOSICAO = 0.4  # da largura do mais curto: os dois estão na mesma coluna
DOIS_PONTOS = ":："

# Menu vertical em que o primeiro item é o mais largo ("New game" / "Continue" / "Options"
# / "Quit"): num print só do menu, a margem do "caberia" é o fim do próprio "New game", e a
# regra de menu pede uma palavra por linha. Num parágrafo, as linhas que não são a última
# enchem a medida; numa pilha de itens, alguma delas acaba bem antes da mais larga.
MENU_MINIMO = 3  # linhas na pilha (duas não se distinguem de uma frase quebrada)
MENU_VAO = 0.8  # vão máximo entre as linhas, em alturas de letra (o mesmo da quebra)
MENU_VAO_REGULAR = 0.5  # maior vão menos o menor
MENU_ALINHADA = 1.0  # bordas a até isso estão alinhadas (as duas alinhadas: justificado)
MENU_CENTRO = 0.5  # centros alinhados: menu centralizado
MENU_LARGURA = 16.0  # linha mais larga que isso é texto corrido (como LINHA_LONGA)
MENU_CURTA = 0.85  # alguma linha que não é a última tem menos que isso da mais larga
MENU_PALAVRAS = 5  # por item; em escrita sem espaço, 1 palavra a cada 4 letras
FIM_DE_ITEM = ".!?。！？؟"  # mas "Load game..." é item de menu
FIM_NO_MEIO = re.compile(r"[.!?;][\s\"]|[。！？；](?=.)")  # frase que acaba no meio da linha
VIRGULA_NO_MEIO = re.compile(r",\s+\S|[，、](?=.)")  # oração no meio da linha ("1,409" não)

# Lista em que um item quebrou em duas linhas (tópicos do diálogo do Morrowind: "Disappearance
# of th" / "Dwarves"; arma do Fallout: "Mercenary's Grenade" / "Rifle"). As duas linhas do
# item ficam coladas (caixas sobrepostas; passo de 15 e 18 px contra 22 a 26 entre itens) e
# a de baixo é a sobra, mais curta. Os itens podem começar com minúscula ("duties"), o que a
# regra do menu veta. A prosa não tem esse degrau no passo: os pares de uma frase quebrada
# ficam a 0,9-1,1 da mediana do bloco.
TOPICO_SOBREPOSICAO = 0.1  # as caixas das duas linhas do item se sobrepõem tanto (em alturas)
TOPICO_BORDA = 0.5  # a sobra começa na mesma borda (em alturas)
TOPICO_SOBRA = 0.85  # e tem até isso da largura da linha de cima
TOPICO_PASSO = 0.85  # passo dentro do item, contra a mediana dos passos entre itens
TOPICO_PASSO_FRACO = 0.75  # um item quebrado só, sem caixas sobrepostas: passo ainda menor
TOPICO_PASSO_REGULAR = 0.5  # maior passo entre itens menos o menor (em alturas)
TOPICOS_QUEBRADOS = 2  # itens em duas linhas para dispensar a regra do menu
TOPICOS_INTEIROS = 3  # passos entre itens, no mínimo
TOPICO_CURTAS = 2  # linhas antes da última bem mais curtas que a mais larga (MENU_CURTA)

# Itens de lista e parágrafos seguidos costumam ter um vão maior que o das linhas de um
# mesmo parágrafo. Nos 140 prints (24/11/2026), nenhuma emenda de linha do gabarito tem
# passo acima de 1,21 do típico do bloco, nas duas leituras. Platô de 1,3 a 1,4: com 1,25
# aparece a primeira quebra errada (Caves of Qud, EasyOCR); com 1,45 os ganhos somem.
PASSO_GRANDE = 1.35  # passo (topo a topo) contra o típico do bloco: quebra
PASSO_MESMA_FILEIRA = 0.5  # passo menor que isso (em alturas) é da mesma fileira, não conta

# Abas de uma palavra encostadas ("Browse | Quickbar", "General | Mining | WarpTo"): o vão
# é o de um espaço e o texto não as distingue de uma frase lida palavra a palavra. A aba
# selecionada tem fundo próprio, medido pelo tom mais comum dentro da caixa (a tinta das
# letras é minoria). No EVE: 53 contra 24, 58 contra 22.
ABAS_MAXIMO = 5  # caixas numa fileira de abas; mais que isso é frase
ABA_FUNDO = 25  # níveis de cinza (0-255) entre o fundo da aba selecionada e o das outras
ABAS_FUNDO_IGUAL = 8  # as outras abas têm o mesmo fundo, com essa folga
PONTUACAO_DE_FRASE = frozenset("',.!?…;:’")

# Barra de menu que o OCR lê numa caixa só ("History Skip Auto Save Load Settings" no Doki
# Doki). Os itens ficam à distância de uma palavra, mas maior que a da fala do mesmo print
# (0,31 a 0,45 altura contra 0,18). Um limite fixo não serve: a fala de cinco jogos tem
# espaço maior que o da barra. O espaço é medido na tinta, dentro da caixa.
BARRA_PALAVRAS = 6  # itens de uma palavra só, no mínimo
BARRA_LETRAS = 3  # letras em cada item ("OK" não passa)
BARRA_ESPACO = 1.5  # o MENOR espaço da barra contra a mediana do espaço da fala
BARRA_AMOSTRA = 5  # espaços de fala medidos no print, no mínimo
BARRA_ALTURA_FALA = (0.5, 2.0)  # altura da fala que serve de referência, contra a da barra
PONTUACAO_DE_FALA = frozenset("',.!?…;’")
# Tinta = pixel a 20 níveis ou mais do tom mais comum da caixa, para os dois lados: pega o
# item apagado e o item claro, que o Otsu jogava no fundo e transformava num "buraco"
TINTA = 20
TINTA_COLUNA = 3  # pixels de tinta para uma coluna contar
ESPACO_CONFIAVEL = 0.08  # um "espaço" menor que isso é fresta de letra: a medida falhou


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


@dataclass(frozen=True)
class Vizinhanca:
    """O que as linhas de cima e de baixo dizem das caixas, olhando o print inteiro (o
    corte XY pode pôr um cabeçalho num bloco e a tabela dele em outro).

    cabecalho: caixas de uma linha de cabeçalho de tabela, alinhada com a de baixo.
    alinhada: caixas alinhadas com alguma caixa da linha de cima ou da de baixo.
    """

    cabecalho: frozenset = frozenset()
    alinhada: frozenset = frozenset()
    comeca_item: frozenset = frozenset()  # pedaços de uma barra de menu cortada (_separar_barras)


def _alinhadas(item, linha: Linha, altura: float) -> bool:
    """A caixa se alinha (borda esquerda, direita ou centro) com alguma caixa da linha."""
    esq, dir_, _, _ = _limites(item)
    for outro in linha.itens:
        esq2, dir2, _, _ = _limites(outro)
        distancia = min(abs(esq - esq2), abs(dir_ - dir2), abs(esq + dir_ - esq2 - dir2) / 2)
        if distancia < ALINHAMENTO * altura:
            return True
    return False


def _vizinhanca(itens: list) -> Vizinhanca:
    linhas = _separar_colunas([Linha(grupo) for grupo in agrupar_em_linhas(itens)])
    cabecalho, alinhada = set(), set()
    for k, linha in enumerate(linhas):
        vizinhas = [linhas[j] for j in (k - 1, k + 1) if 0 <= j < len(linhas)]
        for item in linha.itens:
            if any(_alinhadas(item, vizinha, linha.altura) for vizinha in vizinhas):
                alinhada.add(id(item))
        abaixo = linhas[k + 1] if k + 1 < len(linhas) else None
        if (
            abaixo is not None
            and abaixo.topo - linha.base <= DISTANCIA_CABECALHO * linha.altura
            and sum(_alinhadas(item, abaixo, linha.altura) for item in linha.itens) >= 2
        ):
            cabecalho.update(id(item) for item in linha.itens)
    return Vizinhanca(frozenset(cabecalho), frozenset(alinhada))


@dataclass(frozen=True)
class Fundo:
    """O print em tons de cinza, nas coordenadas das caixas.

    Em escrita da direita para a esquerda as caixas são espelhadas (x vira -x): aí a
    imagem também é espelhada e deslocada, para cada caixa cair no mesmo lugar.
    """

    cinza: np.ndarray
    deslocamento: float = 0.0

    def tom_dominante(self, item):
        """Tom de cinza mais comum dentro da caixa: o fundo, porque a tinta é minoria."""
        esq, dir_, topo, base = _limites(item)
        altura, largura = self.cinza.shape
        x0 = max(0, int(round(esq + self.deslocamento)))
        x1 = min(largura, int(round(dir_ + self.deslocamento)))
        y0, y1 = max(0, int(round(topo))), min(altura, int(round(base)))
        if x1 <= x0 or y1 <= y0:
            return None
        return int(np.bincount(self.cinza[y0:y1, x0:x1].ravel(), minlength=256).argmax())

    def espacos(self, item):
        """Espaços entre as palavras da caixa, medidos na tinta: (larguras em alturas da
        caixa, x do meio de cada espaço) ou None se a medida não for confiável.

        Os (palavras - 1) maiores vãos sem tinta, entre a primeira e a última letra, são os
        espaços. Linhas com tinta em 70% da largura (sublinhado) não contam.
        """
        espacos = len(_texto(item).split()) - 1
        esq, dir_, topo, base = _limites(item)
        x0 = max(0, int(round(esq + self.deslocamento)))
        x1 = min(self.cinza.shape[1], int(round(dir_ + self.deslocamento)))
        y0, y1 = max(0, int(round(topo))), min(self.cinza.shape[0], int(round(base)))
        if espacos < 1 or x1 - x0 < 4 or y1 - y0 < 2:
            return None
        vaos = _vaos_sem_tinta(self.cinza[y0:y1, x0:x1])
        if len(vaos) < espacos:
            return None
        vaos = sorted(sorted(vaos, key=lambda v: v[1] - v[0], reverse=True)[:espacos])
        larguras = [(b - a) / (y1 - y0) for a, b in vaos]
        if min(larguras) < ESPACO_CONFIAVEL:
            return None
        return larguras, [x0 + (a + b) / 2 - self.deslocamento for a, b in vaos]


def _vaos_sem_tinta(recorte: np.ndarray) -> list:
    """Faixas de colunas sem tinta entre letras: [(início, fim)], sem as das pontas."""
    recorte = recorte.astype(int)
    fundo = int(np.bincount(recorte.ravel(), minlength=256).argmax())
    tinta = np.abs(recorte - fundo) >= TINTA
    tinta[tinta.mean(axis=1) >= 0.7, :] = False
    vaos, inicio = [], None
    for x, tem in enumerate(tinta.sum(axis=0) >= TINTA_COLUNA):
        if not tem and inicio is None:
            inicio = x
        elif tem and inicio is not None:
            if inicio > 0:
                vaos.append((inicio, x))
            inicio = None
    return vaos


def _fundo(imagem, espelhada: bool):
    """Fundo a partir do print em cinza (uint8, 2 dimensões); sem print, None."""
    if imagem is None or getattr(imagem, "ndim", 0) != 2:
        return None
    cinza = np.asarray(imagem, dtype=np.uint8)
    if espelhada:
        return Fundo(cinza[:, ::-1], cinza.shape[1] - 1)
    return Fundo(cinza)


def _palavra_de_aba(texto: str) -> bool:
    """Uma palavra com 2+ letras, sem pontuação de frase e que não é só minúscula ("been",
    "der"). Escritas sem maiúscula (árabe, japonês) passam: aí decide o fundo."""
    return (
        " " not in texto
        and sum(c.isalpha() for c in texto) >= 2
        and not any(c in PONTUACAO_DE_FRASE for c in texto)
        and not (any(c.islower() for c in texto) and not any(c.isupper() for c in texto))
    )


def _abas_pelo_fundo(itens: list, fundo) -> bool:
    """Fileira de abas de uma palavra encostadas: só uma caixa tem fundo próprio.

    Uma frase lida palavra a palavra tem o mesmo fundo em todas as caixas. Não há veto de
    tabela: a barra de abas fica sempre em cima de uma lista, e o cabeçalho de uma tabela
    tem o mesmo fundo nas colunas.
    """
    if fundo is None or not 2 <= len(itens) <= ABAS_MAXIMO:
        return False
    if not all(_palavra_de_aba(_texto(item).strip()) for item in itens):
        return False
    altura = statistics.median(_altura_caixa(item) for item in itens)
    limites = [_limites(item) for item in itens]
    vaos = [depois[0] - antes[1] for antes, depois in zip(limites, limites[1:])]
    if not all(0 < vao < VAO_ITENS * altura for vao in vaos):
        return False
    tons = [fundo.tom_dominante(item) for item in itens]
    if None in tons:
        return False
    for k, tom in enumerate(tons):
        outros = tons[:k] + tons[k + 1:]
        if (
            all(abs(tom - outro) >= ABA_FUNDO for outro in outros)
            and max(outros) - min(outros) <= ABAS_FUNDO_IGUAL
        ):
            return True
    return False


def _so_minuscula(palavra: str) -> bool:
    return any(c.islower() for c in palavra) and not any(c.isupper() for c in palavra)


def _e_fala(texto: str) -> bool:
    """Texto de frase: alguma palavra só minúscula ou pontuação de frase."""
    return any(_so_minuscula(p) for p in texto.split()) or any(
        c in PONTUACAO_DE_FALA for c in texto
    )


def _espaco_da_fala(item, itens: list, fundo: Fundo):
    """(mediana, p90) do espaço entre palavras da fala do print, em caixas de altura
    comparável à desta (a fala do Doki Doki tem letra 1,4 a 1,6 vez maior que a barra)."""
    altura = _altura_caixa(item)
    espacos = []
    for outro in itens:
        if outro is item or not _e_fala(_texto(outro)):
            continue
        if not BARRA_ALTURA_FALA[0] <= _altura_caixa(outro) / altura <= BARRA_ALTURA_FALA[1]:
            continue
        medida = fundo.espacos(outro)
        if medida:
            espacos += medida[0]
    if len(espacos) < BARRA_AMOSTRA:
        return None
    return statistics.median(espacos), statistics.quantiles(espacos, n=10, method="inclusive")[8]


def _barra_de_menu(item, itens: list, fundo: Fundo) -> list:
    """x dos cortes de uma barra de menu lida numa caixa só; [] se não for barra.

    A linha inteira decide: 6+ palavras de 3+ letras, nenhuma só minúscula e sem
    pontuação, e o MENOR espaço entre elas 1,5 vez maior que o espaço típico da fala do
    mesmo print (e acima do p90 dela). Numa frase, um espaço grande fica no meio de
    espaços normais; na barra, todos são grandes. Proposta do Grok (2ª rodada, 18/11/2026).
    """
    palavras = _texto(item).split()
    if len(palavras) < BARRA_PALAVRAS or not all(
        p.isalpha() and len(p) >= BARRA_LETRAS and not _so_minuscula(p) for p in palavras
    ):
        return []
    medida = fundo.espacos(item)
    if medida is None:
        return []
    referencia = _espaco_da_fala(item, itens, fundo)
    if referencia is None:
        return []
    menor = min(medida[0])
    if menor >= BARRA_ESPACO * referencia[0] and menor > referencia[1]:
        return medida[1]
    return []


def _separar_barras(itens: list, fundo) -> tuple:
    """Corta cada barra de menu numa caixa por palavra. Devolve as caixas e os ids dos
    pedaços que começam um item novo (todos menos o primeiro de cada barra)."""
    if fundo is None:
        return itens, frozenset()
    saida, novos = [], set()
    for item in itens:
        cortes = _barra_de_menu(item, itens, fundo)
        if not cortes:
            saida.append(item)
            continue
        esq, dir_, topo, base = _limites(item)
        xs = [esq] + list(cortes) + [dir_]
        for k, palavra in enumerate(_texto(item).split()):
            pontos = [[xs[k], topo], [xs[k + 1], topo], [xs[k + 1], base], [xs[k], base]]
            pedaco = (pontos, palavra) + tuple(item[2:])
            if k > 0:
                novos.add(id(pedaco))
            saida.append(pedaco)
    return saida, frozenset(novos)


def _cortar_nos_itens(parte: Linha, comeca: frozenset) -> list:
    """Separa a linha antes de cada pedaço de barra de menu que começa um item."""
    if not any(id(item) in comeca for item in parte.itens[1:]):
        return [parte]
    grupos = [[parte.itens[0]]]
    for item in parte.itens[1:]:
        if id(item) in comeca:
            grupos.append([item])
        else:
            grupos[-1].append(item)
    return [Linha(grupo, item_novo=parte.item_novo or k > 0) for k, grupo in enumerate(grupos)]


def _linhas(itens: list, vizinhanca: Vizinhanca = Vizinhanca(), fundo=None) -> list:
    linhas = _separar_colunas([Linha(grupo) for grupo in agrupar_em_linhas(itens)])
    return [parte for linha in linhas for parte in _separar_itens(linha, vizinhanca, fundo)]


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


def _rotulo_hud(texto: str) -> bool:
    letra = next((c for c in texto if c.isalpha()), "")
    return not _e_valor(texto) and letra.isupper() and len(texto.split()) <= 2


def _e_hud(textos: list) -> bool:
    """Linha inteira alternando rótulo e valor: "HP | 140/140 | DT | 0.0 | Caps | 27"."""
    return (
        len(textos) >= 4
        and len(textos) % 2 == 0
        and all(_rotulo_hud(t) for t in textos[0::2])
        and all(_e_valor(t) for t in textos[1::2])
    )


def _separar_itens(linha: Linha, vizinhanca: Vizinhanca = Vizinhanca(), fundo=None) -> list:
    """Itens lado a lado da mesma linha viram linhas: pelo texto e pela posição
    (_separar_itens_pelo_texto) e, com o print, abas encostadas pelo fundo e pedaços de
    barra de menu (_separar_barras)."""
    saida = []
    for parte in _separar_itens_pelo_texto(linha, vizinhanca):
        if fundo is not None and _abas_pelo_fundo(parte.itens, fundo):
            saida += [
                Linha([item], item_novo=parte.item_novo or k > 0)
                for k, item in enumerate(parte.itens)
            ]
        else:
            saida += _cortar_nos_itens(parte, vizinhanca.comeca_item)
    return saida


def _separar_itens_pelo_texto(linha: Linha, vizinhanca: Vizinhanca = Vizinhanca()) -> list:
    """Separa itens lado a lado da mesma linha: cada item vira uma linha.

    - HUD: rótulo e valor alternados viram um par por linha ("HP 140/140" | "DT 0.0").
    - Fila de MINIMO_ITENS caixas que são todas itens (menu, abas): cada uma vira uma
      linha. Precisa de vão maior que um espaço, a não ser que o OCR tenha agrupado
      palavras numa das caixas ("Home Station"): aí caixas separadas são itens separados,
      mesmo encostadas, desde que a linha não seja o cabeçalho de uma tabela.
    - Duas caixas vizinhas em maiúsculas ("FIGHT" | "ACT"), duas abas com uma palavra em
      comum na ponta, ou dois itens numa linha que não se alinha com as de cima e de
      baixo ("Save Changes" | "Cancel"), sempre com vão maior que um espaço.
    """
    textos = [_texto(item) for item in linha.itens]
    if _e_hud(textos):
        grupos = [linha.itens[k:k + 2] for k in range(0, len(textos), 2)]
        return [Linha(grupo, item_novo=k > 0) for k, grupo in enumerate(grupos)]

    vaos_ok = [vao >= VAO_ITENS * linha.altura for vao in linha.vaos_internos()]
    agrupou = any(len(t.split()) >= 2 for t in textos) and not any(
        id(item) in vizinhanca.cabecalho for item in linha.itens
    )
    fila = len(textos) >= MINIMO_ITENS and all(_e_item(t) for t in textos)
    if fila and (all(vaos_ok) or agrupou):
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
        if (
            len(grupos) == 1 and len(textos) == 2 and vaos_ok[0]
            and all(_e_item(t) and sum(c.isalpha() for c in t) >= 2 for t in textos)
            and not any(id(item) in vizinhanca.alinhada for item in linha.itens)
        ):
            grupos = [[linha.itens[0]], [linha.itens[1]]]
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


def _lados(itens: list, corte: float) -> tuple[list, list]:
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
    "rules") é tópico de menu, não continuação, a não ser que termine a frase
    ("...para tu / llegada.").
    """
    palavras = seguinte.texto.split()
    return (
        seguinte.texto[:1].islower()
        and not FIM_DE_FRASE.search(anterior.texto)
        and (len(palavras) >= 2 or bool(PALAVRA_FINAL.search(seguinte.texto)))
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


def _linhas_coladas(anterior: Linha, seguinte: Linha, altura: float) -> bool:
    """A de baixo encosta na de cima, com letra do mesmo tamanho: linhas de um parágrafo.

    Avisos, títulos e respostas separadas têm um respiro entre as caixas.
    """
    vao = (seguinte.topo - anterior.topo - anterior.altura) / altura
    menor = max(min(anterior.altura, seguinte.altura), 1.0)
    return vao < FIM_COLADO and max(anterior.altura, seguinte.altura) / menor < FIM_FONTE


def _comeca_paragrafo(
    anterior: Linha, seguinte: Linha, margem_dir: float, altura: float, letra: float
) -> bool:
    if seguinte.item_novo:
        return True
    # Sentença terminada e a de baixo não continua com minúscula: avisos seguidos
    # ("...increased to 66." / "Item does not have enough charge."), a não ser que as
    # linhas estejam coladas, como num parágrafo ("...special occasion?" / "It's not...")
    if (
        FIM_DE_SENTENCA.search(anterior.texto)
        and not seguinte.texto[:1].islower()
        and not _linhas_coladas(anterior, seguinte, altura)
    ):
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
    # A margem é a do print ou a do painel (_margem_local); a do bloco juntou itens de menu.
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


def _margem_local(linhas: list, indice: int, margem_dir: float, altura: float) -> float:
    """Margem do "caberia" para linhas[indice]: a do painel ou, sem evidência, a do print.

    O painel acaba onde terminam as linhas longas vizinhas que começam no mesmo x.
    Menu não tem linha longa e tabela vai até a borda do print: nos dois fica a margem do
    print. Usar o fim da linha mais longa do bloco todo juntava itens de menu.
    """
    atual = linhas[indice]
    fins = [
        linha.dir
        for linha in linhas[max(0, indice - VIZINHAS) : indice + VIZINHAS + 1]
        if ALTURA_PARECIDA[0] * altura <= linha.altura <= ALTURA_PARECIDA[1] * altura
        and abs(linha.esq - atual.esq) <= MESMA_ESQUERDA * altura
        and linha.dir - linha.esq >= LINHA_LONGA * altura
    ]
    if not fins:
        return margem_dir
    painel = max(fins) + altura
    return painel if margem_dir - painel >= FOLGA_PRINT * altura else margem_dir


def _termina_em_numero(texto: str) -> bool:
    """O último pedaço é um valor: "41", "0.0", "16:29", "1,409,640", "0.0 ?", "75%"."""
    resto = texto.rstrip().rstrip("?!.%)]").rstrip()
    if not resto:
        return False
    ultimo = resto.split()[-1]
    return any(c.isdigit() for c in ultimo) and not any(c.isalpha() for c in ultimo)


def _tem_rotulo(texto: str) -> bool:
    """Tem ":" de rótulo ("Total Net Worth:"), com letra logo antes; "16:29" não conta."""
    return any(c in DOIS_PONTOS and i > 0 and texto[i - 1].isalpha() for i, c in enumerate(texto))


def _e_campo(linha: Linha, altura: float) -> bool:
    """Linha curta de ficha: "Endurance 41", "Security Status: 0.0", "Total Net Worth:"."""
    return (
        linha.dir - linha.esq < CAMPO_LARGURA * altura
        and len(linha.texto.split()) <= CAMPO_PALAVRAS
        and (_termina_em_numero(linha.texto) or _tem_rotulo(linha.texto))
    )


def _empilhadas(cima: Linha, baixo: Linha, altura: float) -> bool:
    """Uma logo abaixo da outra, na mesma coluna (sem exigir o mesmo x: "x2 Speed 62")."""
    sobreposicao = min(cima.dir, baixo.dir) - max(cima.esq, baixo.esq)
    menor = min(cima.dir - cima.esq, baixo.dir - baixo.esq)
    return (
        baixo.topo - cima.base <= CAMPO_VAO * altura
        and sobreposicao >= CAMPO_SOBREPOSICAO * menor
    )


def _quebras_de_lista(linhas: list, altura: float) -> set:
    """Índices i em que linhas[i + 1] é um campo novo de uma lista "rótulo valor".

    Vale só para CAMPOS_SEGUIDOS linhas ou mais, curtas e empilhadas. Antes de uma linha
    que começa com minúscula não quebra: é continuação ("...in 1990" / "and later...").
    """
    quebras = set()
    trecho = []
    for indice, linha in enumerate(linhas + [None]):
        campo = linha is not None and _e_campo(linha, altura)
        if linha is not None and campo and trecho and _empilhadas(
            linhas[trecho[-1]], linha, altura
        ):
            trecho.append(indice)
            continue
        if len(trecho) >= CAMPOS_SEGUIDOS:
            quebras.update(i for i in trecho[:-1] if not linhas[i + 1].texto[:1].islower())
        trecho = [indice] if campo else []
    return quebras


def _pilhas(linhas: list, altura: float) -> list:
    """Trechos (início, fim) de MENU_MINIMO+ linhas seguidas com vãos pequenos e regulares."""
    trechos = []
    inicio = 0
    while inicio < len(linhas):
        fim = inicio
        vaos = []
        while fim + 1 < len(linhas):
            vao = linhas[fim + 1].topo - linhas[fim].base
            irregular = max(vaos + [vao]) - min(vaos + [vao]) > MENU_VAO_REGULAR * altura
            if vao > MENU_VAO * altura or irregular:
                break
            vaos.append(vao)
            fim += 1
        if fim - inicio + 1 >= MENU_MINIMO:
            trechos.append((inicio, fim))
        inicio = fim + 1 if fim > inicio else inicio + 1
    return trechos


def _palavras(texto: str) -> int:
    if SEM_ESPACO.match(texto):
        return (len(texto) + 3) // 4
    return len(texto.split())


def _parece_item(texto: str) -> bool:
    """Sem cara de frase: não começa com minúscula, não termina nem para no meio de uma
    frase (ponto, vírgula), até MENU_PALAVRAS palavras. Reticências são de item de menu."""
    termina = texto[-1:] in FIM_DE_ITEM and not texto.endswith(("...", "…"))
    return not (
        texto[:1].islower()
        or termina
        or FIM_NO_MEIO.search(texto)
        or VIRGULA_NO_MEIO.search(texto)
        or _palavras(texto) > MENU_PALAVRAS
    )


def _e_menu(pilha: list, altura: float) -> bool:
    """Uma borda alinhada e a outra não (ou centralizado), linhas curtas, itens sem cara de
    frase e alguma linha antes da última bem mais curta que a mais larga."""
    def amplitude(valores):
        return max(valores) - min(valores)

    esquerda = amplitude([l.esq for l in pilha]) <= MENU_ALINHADA * altura
    direita = amplitude([l.dir for l in pilha]) <= MENU_ALINHADA * altura
    centro = amplitude([(l.esq + l.dir) / 2 for l in pilha]) <= MENU_CENTRO * altura
    larguras = [l.dir - l.esq for l in pilha]
    return (
        (esquerda != direita or (centro and not esquerda))
        and max(larguras) < MENU_LARGURA * altura
        and all(_parece_item(l.texto) for l in pilha)
        and any(w < MENU_CURTA * max(larguras) for w in larguras[:-1])
    )


def _grupos_por_centro(linhas: list, altura: float) -> list:
    """Sequências de índices seguidos com os centros a até CENTRALIZADO alturas."""
    grupos, atual = [], [0]
    for indice in range(1, len(linhas)):
        anterior, linha = linhas[indice - 1], linhas[indice]
        distancia = abs((linha.esq + linha.dir) - (anterior.esq + anterior.dir)) / 2
        if distancia <= CENTRALIZADO * altura:
            atual.append(indice)
        else:
            grupos.append(atual)
            atual = [indice]
    grupos.append(atual)
    return grupos


def _quebras_centralizadas(linhas: list, altura: float) -> set:
    """Quebra entre as propriedades de uma descrição de item centralizada.

    "ATTACK, MELEE, STRIKE, PHYSICAL" / "LEVEL: 1" (Path of Exile, em versalete, sem a pista
    da minúscula) saíam numa linha só. Não quebra quando a de cima termina frase (aí vale a
    regra do fim de frase), a de baixo continua com minúscula, a de cima acaba em vírgula,
    nem quando as duas são cheias ou a de baixo fecha a frase de uma de cima cheia:
    "PERFORMS TWO FAST STRIKES WITH A MELEE" / "WEAPON." fica junto.
    """
    quebras = set()
    for grupo in _grupos_por_centro(linhas, altura):
        larguras = [linhas[i].dir - linhas[i].esq for i in grupo]
        centralizado = any(
            abs(linhas[i].esq - linhas[j].esq) > DESCRICAO_ESQUERDA * altura
            for i, j in zip(grupo, grupo[1:])
        )
        if len(grupo) < 2 or not centralizado or max(larguras) < DESCRICAO_LARGA * altura:
            continue
        cheia = DESCRICAO_CHEIA * max(larguras)
        for indice in grupo[:-1]:
            anterior, seguinte = linhas[indice], linhas[indice + 1]
            if (
                FRASE_FECHADA.search(anterior.texto.rstrip())
                or seguinte.texto.lstrip()[:1].islower()
                or anterior.texto.rstrip().endswith((",", "，", "、"))
            ):
                continue
            if (seguinte.topo - anterior.topo - anterior.altura) / altura >= DESCRICAO_VAO:
                quebras.add(indice)
                continue
            fecha = (
                seguinte.dir - seguinte.esq >= cheia
                or FRASE_FECHADA.search(seguinte.texto.rstrip()) is not None
            )
            if anterior.dir - anterior.esq >= cheia and fecha:
                continue
            quebras.add(indice)
    return quebras


def _quebras_por_passo(linhas: list, altura: float) -> set:
    """Quebra onde o passo vertical é bem maior que o típico do bloco.

    "Sell Items" / "Goodbye" do Path of Exile, a fala do Disco Elysium e o "+5 XP" embaixo
    dela: o vão entre os itens é maior que o das linhas de cada um.
    """
    passos = [b.topo - a.topo for a, b in zip(linhas, linhas[1:])]
    entre_fileiras = [passo for passo in passos if passo >= PASSO_MESMA_FILEIRA * altura]
    if len(entre_fileiras) < 2:
        return set()
    tipico = statistics.median(entre_fileiras)
    return {indice for indice, passo in enumerate(passos) if passo >= PASSO_GRANDE * tipico}


def _quebras_de_menu(linhas: list, altura: float) -> set:
    """Índices i em que linhas[i + 1] é outro item de um menu vertical.

    Proposta do Grok (Problema 7, 18/11/2026), com as travas medidas: fim de frase ou
    vírgula no meio da linha e até 5 palavras (uma manchete em maiúsculas e uma linha de
    10 palavras do EasyOCR viravam menu) e reticências como item.
    """
    quebras = set()
    for inicio, fim in _pilhas(linhas, altura):
        if _e_menu(linhas[inicio : fim + 1], altura):
            quebras.update(range(inicio, fim))
    return quebras


def _pilhas_por_vao(linhas: list, altura: float) -> list:
    """Trechos (início, fim) de linhas seguidas com vão de até MENU_VAO, sem exigir que os
    vãos sejam regulares: dentro de um item quebrado o vão é negativo."""
    trechos = []
    inicio = 0
    while inicio < len(linhas):
        fim = inicio
        while (fim + 1 < len(linhas)
               and linhas[fim + 1].topo - linhas[fim].base <= MENU_VAO * altura):
            fim += 1
        if fim > inicio:
            trechos.append((inicio, fim))
        inicio = fim + 1
    return trechos


def _sobra_de_item(cima: Linha, baixo: Linha, altura: float) -> bool:
    """A de baixo começa na mesma borda e é mais curta: o resto de um item que quebrou."""
    return (
        abs(baixo.esq - cima.esq) <= TOPICO_BORDA * altura
        and baixo.dir - baixo.esq <= TOPICO_SOBRA * (cima.dir - cima.esq)
    )


def _parece_topico(texto: str) -> bool:
    """Como _parece_item, mas aceita minúscula no começo ("duties", "rules") e não aceita
    reticências: sem o veto da minúscula, a pontuação é a proteção da prosa."""
    return not (
        texto[-1:] in FIM_DE_ITEM
        or texto.endswith("…")
        or FIM_NO_MEIO.search(texto)
        or VIRGULA_NO_MEIO.search(texto)
        or (not SEM_ESPACO.match(texto) and len(texto.split()) > MENU_PALAVRAS)
    )


def _topicos(pilha: list, altura: float) -> set:
    """Pares (k, k + 1) da pilha que são um item em duas linhas, se a pilha é uma lista com
    TOPICOS_QUEBRADOS itens assim (caixas sobrepostas) e passos regulares entre os outros.

    Proposta do Grok (Problema 8, 19/11/2026). Fica de fora a coluna larga, com fim de frase
    ou vírgula no meio, com linhas de mais de MENU_PALAVRAS palavras ou sem linhas curtas.
    """
    def amplitude(valores):
        return max(valores) - min(valores)

    colados = {
        k
        for k, (cima, baixo) in enumerate(zip(pilha, pilha[1:]))
        if cima.base - baixo.topo >= TOPICO_SOBREPOSICAO * altura
        and _sobra_de_item(cima, baixo, altura)
    }
    passos = [baixo.topo - cima.topo for cima, baixo in zip(pilha, pilha[1:])]
    entre = [passo for k, passo in enumerate(passos) if k not in colados]
    if len(colados) < TOPICOS_QUEBRADOS or len(entre) < TOPICOS_INTEIROS:
        return set()
    dentro = max(passos[k] for k in colados)
    larguras = [linha.dir - linha.esq for linha in pilha]
    lista = (
        dentro <= TOPICO_PASSO * statistics.median(entre)
        and dentro < min(entre)
        and amplitude(entre) <= TOPICO_PASSO_REGULAR * altura
        and amplitude([linha.esq for linha in pilha]) <= MENU_ALINHADA * altura
        and max(larguras) < MENU_LARGURA * altura
        and sum(1 for w in larguras[:-1] if w < MENU_CURTA * max(larguras)) >= TOPICO_CURTAS
        and all(_parece_topico(linha.texto) for linha in pilha)
    )
    return colados if lista else set()


def _menu_com_item_quebrado(pilha: list, altura: float) -> tuple:
    """Menu em que um item quebrou em duas linhas ("Mercenary's Grenade" / "Rifle"): junta
    as linhas coladas e devolve (quebras, juntas) se a regra do menu confirmar nos itens.

    É o "modo fraco" do ChatGPT (Problema 8): um par colado só não prova que a pilha é uma
    lista, então a regra do menu decide, com o veto da minúscula.
    """
    passos = [baixo.topo - cima.topo for cima, baixo in zip(pilha, pilha[1:])]
    mediana = statistics.median(passos)
    colados = {
        k
        for k, (cima, baixo) in enumerate(zip(pilha, pilha[1:]))
        if passos[k] <= TOPICO_PASSO * mediana
        and (cima.base - baixo.topo >= TOPICO_SOBREPOSICAO * altura
             or passos[k] <= TOPICO_PASSO_FRACO * mediana)
        and _sobra_de_item(cima, baixo, altura)
    }
    if not colados:
        return set(), set()
    itens, primeiras = [], []  # linha lógica de cada item e a 1ª linha dele na pilha
    for k, linha in enumerate(pilha):
        if k - 1 in colados:
            itens[-1] = Linha(itens[-1].itens + linha.itens)
        else:
            itens.append(linha)
            primeiras.append(k)
    primeiras.append(len(pilha))
    quebras, juntas = set(), set()
    for inicio, fim in _pilhas(itens, altura):
        if not _e_menu(itens[inicio : fim + 1], altura):
            continue
        for item in range(inicio, fim + 1):
            ultima = primeiras[item + 1] - 1
            juntas.update(range(primeiras[item], ultima))
            if item < fim:
                quebras.add(ultima)
    return quebras, juntas


def _itens_quebrados(linhas: list, altura: float) -> tuple:
    """(quebras, juntas): índices i em que linhas[i + 1] começa outro item de uma lista, ou
    continua o item de cima, que quebrou em duas linhas. As junções valem mais que as outras
    regras (o "caberia" e a minúscula separavam o item)."""
    quebras, juntas = set(), set()
    for inicio, fim in _pilhas_por_vao(linhas, altura):
        pilha = linhas[inicio : fim + 1]
        colados = _topicos(pilha, altura)
        if colados:
            juntas.update(inicio + k for k in colados)
            quebras.update(inicio + k for k in range(len(pilha) - 1) if k not in colados)
            continue
        if len(pilha) > MENU_MINIMO:
            de_menu, coladas = _menu_com_item_quebrado(pilha, altura)
            quebras.update(inicio + k for k in de_menu)
            juntas.update(inicio + k for k in coladas)
    return quebras, juntas


def _paragrafos_do_bloco(linhas: list, margem_dir: float, altura: float, letra: float) -> list:
    """Junta as linhas de um bloco em parágrafos."""
    de_itens, juntas = _itens_quebrados(linhas, altura)
    de_lista = (
        _quebras_de_lista(linhas, altura)
        | _quebras_de_menu(linhas, altura)
        | de_itens
        | _quebras_por_passo(linhas, altura)
        | _quebras_centralizadas(linhas, altura)
    )
    atuais = [[linhas[0].texto]]
    for indice, (anterior, seguinte) in enumerate(zip(linhas, linhas[1:])):
        if indice in juntas:
            atuais[-1].append(seguinte.texto)
            continue
        margem = _margem_local(linhas, indice, margem_dir, altura)
        if indice in de_lista or _comeca_paragrafo(anterior, seguinte, margem, altura, letra):
            atuais.append([seguinte.texto])
        else:
            atuais[-1].append(seguinte.texto)
    return [_juntar(partes) for partes in atuais]


def montar_paragrafos(resultados, idioma: str = "", imagem=None) -> list:
    """Resultados do OCR -> lista de parágrafos (cada um já numa linha só).

    idioma é o código do texto lido; em árabe, persa, urdu e uigur a leitura vai da
    direita para a esquerda. imagem é o print em tons de cinza, nas coordenadas das
    caixas (opcional): sem ele, as abas encostadas e as barras de menu lidas numa caixa só
    não são separadas.
    """
    itens = [item for item in resultados if len(item) >= 2 and _texto(item)]
    espelhada = (idioma or "").lower() in IDIOMAS_DA_DIREITA
    if espelhada:
        itens = [_espelhar(item) for item in itens]
    filtrados = _filtrar_lixo(itens)
    itens = _endireitar(filtrados)
    # Caixas giradas não batem mais com a imagem: aí as regras da imagem ficam de fora
    fundo = _fundo(imagem, espelhada) if itens is filtrados else None
    itens, pedacos = _separar_barras(itens, fundo)
    vizinhanca = replace(_vizinhanca(itens), comeca_item=pedacos)
    todas = _linhas(itens, vizinhanca, fundo)
    if not todas:
        return []

    # Medidas típicas do print, para as regras valerem em qualquer resolução
    altura = statistics.median(linha.altura for linha in todas)
    letra = statistics.median(linha.largura_letra for linha in todas)
    margem_dir = max(linha.dir for linha in todas)

    paragrafos = []
    for bloco in _blocos(itens, altura, _pares_de_valor(itens, altura)):
        paragrafos += _paragrafos_do_bloco(
            _linhas(bloco, vizinhanca, fundo), margem_dir, altura, letra
        )
    return paragrafos
