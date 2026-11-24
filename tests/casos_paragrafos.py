"""Casos de montagem do texto em várias línguas, com caixas de OCR simuladas.

Cada caso imita o que o OCR devolve (caixas com posição e texto) e diz quais parágrafos o
app deveria montar. Não há texto de jogo aqui: os casos foram escritos para os testes.

Os casos com limite_conhecido=True ainda falham e ficam como registro do limite.
"""

from dataclasses import dataclass

ALTURA = 30


def caixa(x, y, largura, texto, altura=ALTURA, conf=0.9):  # pylint: disable=too-many-arguments,too-many-positional-arguments
    """Caixa no formato do OCR: (4 cantos, texto, confiança)."""
    return ([[x, y], [x + largura, y], [x + largura, y + altura], [x, y + altura]], texto, conf)


@dataclass(frozen=True)
class Caso:
    """Um caso de teste: caixas lidas numa língua e os parágrafos esperados."""

    nome: str
    idioma: str
    caixas: list
    esperado: list
    limite_conhecido: bool = False

def coluna(itens, x=20, passo=40, dentro=24):
    """Lista alinhada à esquerda em x, com 14 px por letra. Um item em tupla quebrou em duas
    linhas: entre elas o passo é `dentro` (caixas sobrepostas); entre os itens, `passo`."""
    caixas, y = [], 0
    for item in itens:
        partes = item if isinstance(item, tuple) else (item,)
        for k, parte in enumerate(partes):
            caixas.append(caixa(x, y, 14 * len(parte), parte))
            y += dentro if k < len(partes) - 1 else passo
    return caixas


# Geometria da lista de tópicos do diálogo do Morrowind (x, topo, largura, altura), com
# outros nomes: dois tópicos quebram em duas linhas e alguns começam com minúscula
TOPICOS = [
    (1170, 122, 105, 22, "Training"),
    (1170, 146, 149, 23, "Lost caravan of the"),
    (1170, 164, 71, 20, "Traders"),
    (1170, 186, 52, 22, "errands"),
    (1170, 211, 118, 22, "join the Fighters"),
    (1170, 226, 47, 22, "Guild"),
    (1170, 250, 99, 23, "Fighters Guild"),
    (1170, 275, 110, 22, "Promotions"),
    (1170, 298, 43, 23, "orders"),
    (1170, 324, 79, 20, "Northmoor"),
]
TOPICOS_ESPERADOS = [
    "Training", "Lost caravan of the Traders", "errands", "join the Fighters Guild",
    "Fighters Guild", "Promotions", "orders", "Northmoor",
]


def topicos(por_palavra=False):
    """A lista de tópicos numa caixa por linha (RapidOCR) ou por palavra (EasyOCR)."""
    if not por_palavra:
        return [caixa(x, y, w, t, altura=a) for x, y, w, a, t in TOPICOS]
    caixas = []
    for x, y, _, a, texto in TOPICOS:
        for palavra in texto.split():
            caixas.append(caixa(x, y, 9 * len(palavra), palavra, altura=a))
            x += 9 * (len(palavra) + 1)
    return caixas


CASOS = [
    Caso(
        "português: fala quebrada em duas linhas, com o nome em cima",
        "pt",
        [
            caixa(20, 0, 110, "Joana"),
            caixa(20, 45, 880, "O que você está fazendo aqui? Eu pensei que"),
            caixa(20, 85, 600, "tinha te dito para ficar em casa."),
        ],
        ["Joana", "O que você está fazendo aqui? Eu pensei que tinha te dito para ficar em casa."],
    ),
    Caso(
        "espanhol: menu de uma opção por linha (o 1º item é o mais largo)",
        "es",
        [
            caixa(20, 0, 260, "Nueva partida"),
            caixa(20, 40, 190, "Continuar"),
            caixa(20, 80, 180, "Opciones"),
            caixa(20, 120, 100, "Salir"),
        ],
        ["Nueva partida", "Continuar", "Opciones", "Salir"],
    ),
    Caso(
        "inglês: o mesmo menu (o 1º item é o mais largo)",
        "en",
        [
            caixa(20, 0, 200, "New game"),
            caixa(20, 40, 180, "Continue"),
            caixa(20, 80, 160, "Options"),
            caixa(20, 120, 80, "Quit"),
        ],
        ["New game", "Continue", "Options", "Quit"],
    ),
    Caso(
        "japonês: fala comprida quebrada em três linhas (não é menu)",
        "ja",
        [
            caixa(20, 0, 880, "この村には古い言い伝えがあって、"),
            caixa(20, 40, 880, "夜になると森の奥から不思議な"),
            caixa(20, 80, 300, "歌が聞こえる。"),
        ],
        ["この村には古い言い伝えがあって、夜になると森の奥から不思議な歌が聞こえる。"],
    ),
    Caso(
        "alemão: frase continua numa linha que começa com substantivo",
        "de",
        [
            caixa(20, 0, 880, "Du musst zuerst mit dem freundlichen alten"),
            caixa(20, 40, 520, "Händler im Dorf sprechen."),
        ],
        ["Du musst zuerst mit dem freundlichen alten Händler im Dorf sprechen."],
    ),
    Caso(
        "russo: frase continua com minúscula",
        "ru",
        [
            caixa(20, 0, 640, "Ты должен поговорить с"),
            caixa(20, 40, 700, "торговцем в деревне, он знает дорогу."),
        ],
        ["Ты должен поговорить с торговцем в деревне, он знает дорогу."],
    ),
    Caso(
        "japonês: fala de duas linhas sem espaço e nome em cima",
        "ja",
        [
            caixa(20, 0, 70, "王様"),
            caixa(20, 45, 880, "勇者よ、よくぞ来た。この城の地下に"),
            caixa(20, 85, 560, "魔王が眠っている。"),
        ],
        ["王様", "勇者よ、よくぞ来た。この城の地下に魔王が眠っている。"],
    ),
    Caso(
        "japonês: título grande de 3 letras acima da fala",
        "ja",
        [
            caixa(300, 0, 360, "第一章", altura=120),
            caixa(20, 160, 880, "勇者よ、よくぞ来た。この城の地下に"),
            caixa(20, 200, 560, "魔王が眠っている。"),
        ],
        ["第一章", "勇者よ、よくぞ来た。この城の地下に魔王が眠っている。"],
    ),
    Caso(
        "japonês: menu de opções curtas",
        "ja",
        [caixa(20, 0, 300, "はじめから"), caixa(20, 40, 240, "つづきから"), caixa(20, 80, 120, "設定")],
        ["はじめから", "つづきから", "設定"],
    ),
    Caso(
        "chinês: linha que o OCR dividiu em duas caixas",
        "ch_sim",
        [caixa(20, 0, 300, "你好，旅行者。"), caixa(330, 0, 300, "欢迎来到村庄。")],
        ["你好，旅行者。欢迎来到村庄。"],
    ),
    Caso(
        "árabe: uma linha em três caixas (lê da direita para a esquerda)",
        "ar",
        [caixa(600, 0, 200, "مرحبا"), caixa(400, 0, 180, "أيها"), caixa(150, 0, 230, "المسافر")],
        ["مرحبا أيها المسافر"],
    ),
    Caso(
        "árabe: frase quebrada em duas linhas alinhadas à direita",
        "ar",
        [
            caixa(100, 0, 700, "يجب عليك أن تتحدث مع التاجر"),
            caixa(450, 40, 350, "في القرية قبل الرحيل."),
        ],
        ["يجب عليك أن تتحدث مع التاجر في القرية قبل الرحيل."],
    ),
    Caso(
        "árabe: lista à direita e descrição à esquerda (painéis)",
        "ar",
        [
            caixa(700, 0, 120, "سيف"),
            caixa(700, 40, 120, "درع"),
            caixa(700, 80, 120, "خوذة"),
            caixa(100, 10, 400, "سيف حاد يقطع"),
            caixa(100, 50, 400, "كل شيء تقريبا."),
        ],
        ["سيف", "درع", "خوذة", "سيف حاد يقطع كل شيء تقريبا."],
    ),
    Caso(
        "português: correções do inglês NÃO podem rodar",
        "pt",
        [caixa(20, 0, 600, "Ive dont chc 1 was cicizen")],
        ["Ive dont chc 1 was cicizen"],
    ),
    Caso(
        "inglês: as mesmas palavras SÃO corrigidas",
        "en",
        [caixa(20, 0, 600, "Ive dont chc 1 was cicizen")],
        ["I've don't the I was citizen"],
    ),
    Caso(
        "inglês: menu de botões na mesma linha (itens lado a lado)",
        "en",
        [caixa(20, 0, 90, "FIGHT"), caixa(200, 0, 60, "ACT"), caixa(350, 0, 80, "ITEM"),
         caixa(520, 0, 100, "MERCY")],
        ["FIGHT", "ACT", "ITEM", "MERCY"],
    ),
    Caso(
        "japonês: fala que o OCR dividiu em 3 caixas (NÃO são itens)",
        "ja",
        [caixa(20, 0, 150, "この城の"), caixa(200, 0, 120, "地下には"), caixa(360, 0, 200, "宝があるらしい。")],
        ["この城の地下には宝があるらしい。"],
    ),
    Caso(
        "alemão: linha só com substantivos e a de baixo com minúscula (NÃO é título)",
        "de",
        [
            caixa(20, 0, 520, "Der Kapitän der Flotte"),
            caixa(20, 40, 760, "sah das brennende Schiff am Horizont."),
        ],
        ["Der Kapitän der Flotte sah das brennende Schiff am Horizont."],
    ),
    Caso(
        "português: avisos curtos seguidos, cada um com ponto final",
        "pt",
        [
            caixa(20, 0, 640, "Sua habilidade subiu para 66."),
            caixa(20, 40, 560, "O item não tem carga suficiente."),
        ],
        ["Sua habilidade subiu para 66.", "O item não tem carga suficiente."],
    ),
    Caso(
        "inglês: frase que termina no fim da linha, no meio de um parágrafo (linhas coladas)",
        "en",
        [
            caixa(20, 0, 880, "My parents are here. It's been a few days since I've last seen"),
            caixa(20, 32, 890, "them. Is this supposed to be some kind of special occasion?"),
            caixa(20, 64, 240, "It's not a party."),
        ],
        [
            "My parents are here. It's been a few days since I've last seen them. Is this "
            "supposed to be some kind of special occasion? It's not a party."
        ],
    ),
    Caso(
        "inglês: título de letra grande colado ao subtítulo (alturas 1,45x) continua quebrando",
        "en",
        [
            caixa(20, 0, 700, "A Next Generation Legend!", altura=58),
            caixa(20, 45, 700, "Stand Tall, Galactic Hero!", altura=40),
        ],
        ["A Next Generation Legend!", "Stand Tall, Galactic Hero!"],
    ),
    Caso(
        "inglês: HUD alternando rótulo e valor",
        "en",
        [caixa(20, 0, 50, "HP"), caixa(80, 0, 110, "140/140"), caixa(210, 0, 40, "DT"),
         caixa(260, 0, 50, "0.0"), caixa(330, 0, 70, "Caps"), caixa(410, 0, 40, "27")],
        ["HP 140/140", "DT 0.0", "Caps 27"],
    ),
    Caso(
        "português: dois botões sozinhos numa linha",
        "pt",
        [
            caixa(20, 0, 700, "Deseja salvar as alterações antes de sair?"),
            caixa(120, 60, 230, "Salvar tudo"),
            caixa(420, 60, 160, "Cancelar"),
        ],
        ["Deseja salvar as alterações antes de sair?", "Salvar tudo", "Cancelar"],
    ),
    Caso(
        "russo: fala em maiúsculas, uma caixa por palavra (NÃO são itens)",
        "ru",
        [caixa(20, 0, 80, "ЭТО"), caixa(108, 0, 120, "БЫЛО"), caixa(236, 0, 100, "ДАВНО")],
        ["ЭТО БЫЛО ДАВНО"],
    ),
    Caso(
        "português: painel estreito sem borda, frase quebrada depois de ':' com maiúscula",
        "pt",
        [
            caixa(1150, 0, 150, "Tópicos"),
            caixa(20, 80, 620, "A guilda aceita apenas candidatos de mente afiada e"),
            caixa(20, 120, 600, "vontade firme. Todos devem dominar as quatro escolas:"),
            caixa(20, 160, 610, "Fogo, Água, Terra e Ar. Também devem conhecer as artes"),
            caixa(20, 200, 340, "da alquimia e dos encantamentos."),
        ],
        [
            "Tópicos",
            "A guilda aceita apenas candidatos de mente afiada e vontade firme. Todos devem "
            "dominar as quatro escolas: Fogo, Água, Terra e Ar. Também devem conhecer as artes "
            "da alquimia e dos encantamentos.",
        ],
    ),
    Caso(
        "inglês: painel estreito, linha curta sem ponto e frase nova (quebra mantida)",
        "en",
        [
            caixa(1150, 0, 150, "Topics"),
            caixa(20, 80, 620, "Welcome to the guild hall, where every new member must"),
            caixa(20, 120, 600, "sign the old ledger before taking any of the contracts"),
            caixa(20, 160, 260, "posted on the board"),
            caixa(20, 200, 610, "Ask the clerk at the front desk if you need any help with"),
            caixa(20, 240, 250, "your first contract."),
        ],
        [
            "Topics",
            "Welcome to the guild hall, where every new member must sign the old ledger before "
            "taking any of the contracts posted on the board",
            "Ask the clerk at the front desk if you need any help with your first contract.",
        ],
    ),
    Caso(
        "português: lista de atributos 'rótulo número', uma linha por atributo",
        "pt",
        [
            caixa(20, 0, 200, "Força 72"),
            caixa(20, 35, 220, "Agilidade 41"),
            caixa(20, 70, 260, "Inteligência 30"),
            caixa(20, 105, 160, "Sorte 40"),
        ],
        ["Força 72", "Agilidade 41", "Inteligência 30", "Sorte 40"],
    ),
    Caso(
        "português: perfil com rótulos de dois pontos, um deles sem valor",
        "pt",
        [
            caixa(20, 0, 330, "Nascido: 13/01/2022"),
            caixa(20, 35, 240, "Patrimônio:"),
            caixa(20, 70, 300, "Reputação: 0.0"),
            caixa(20, 105, 330, "Base: Kisogo 1.0"),
        ],
        ["Nascido: 13/01/2022", "Patrimônio:", "Reputação: 0.0", "Base: Kisogo 1.0"],
    ),
    Caso(
        "inglês: prosa com um ano no fim de 3 linhas, continuando em minúscula (NÃO é lista)",
        "en",
        [
            caixa(20, 0, 520, "The building was founded in 1990"),
            caixa(20, 40, 400, "and expanded in 2005"),
            caixa(20, 80, 420, "before closing in 2010."),
        ],
        ["The building was founded in 1990 and expanded in 2005 before closing in 2010."],
    ),
    Caso(
        "alemão: linha que termina em número e substantivo maiúsculo embaixo (NÃO é lista)",
        "de",
        [
            caixa(20, 0, 900, "Die Wachen berichten, dass die Karawane im Morgengrauen mit 40"),
            caixa(20, 40, 880, "Soldaten und 12 Wagen die Stadt verlassen hat."),
        ],
        [
            "Die Wachen berichten, dass die Karawane im Morgengrauen mit 40 Soldaten und 12 Wagen "
            "die Stadt verlassen hat."
        ],
    ),
    Caso(
        "alemão: prosa estreita com 3 linhas seguidas terminando em número",
        "de",
        [
            caixa(20, 0, 470, "Die Stadt hatte im Jahr 1990 rund 5000"),
            caixa(20, 40, 460, "Einwohner und wuchs bis 2005 auf 8000"),
            caixa(20, 80, 450, "Einwohner, und 2010 waren es 9000"),
            caixa(20, 120, 300, "Einwohner in der Stadt."),
        ],
        [
            "Die Stadt hatte im Jahr 1990 rund 5000 Einwohner und wuchs bis 2005 auf 8000 "
            "Einwohner, und 2010 waren es 9000 Einwohner in der Stadt."
        ],
        limite_conhecido=True,
    ),
    # Problema 7 (18/11/2026): menus em que o 1º item é o mais largo, e prosa estreita que
    # a regra do menu não pode quebrar (casos escritos para o teste, não de print real)
    Caso(
        "inglês: menu centralizado, o 1º item é o mais largo",
        "en",
        [
            caixa(100, 0, 200, "New game"),
            caixa(110, 40, 180, "Continue"),
            caixa(120, 80, 160, "Options"),
            caixa(160, 120, 80, "Quit"),
        ],
        ["New game", "Continue", "Options", "Quit"],
    ),
    Caso(
        "inglês: menu com os dois primeiros itens da mesma largura",
        "en",
        [
            caixa(20, 0, 220, "Save game"),
            caixa(20, 40, 220, "Load game"),
            caixa(20, 80, 160, "Options"),
            caixa(20, 120, 80, "Quit"),
        ],
        ["Save game", "Load game", "Options", "Quit"],
    ),
    Caso(
        "inglês: menu com reticências no item mais largo",
        "en",
        [
            caixa(20, 0, 200, "New game"),
            caixa(20, 40, 230, "Load game..."),
            caixa(20, 80, 160, "Options"),
            caixa(20, 120, 80, "Quit"),
        ],
        ["New game", "Load game...", "Options", "Quit"],
    ),
    Caso(
        "inglês: inventário sem números",
        "en",
        [
            caixa(20, 0, 210, "Iron Sword"),
            caixa(20, 40, 260, "Leather Armor"),
            caixa(20, 80, 250, "Health Potion"),
            caixa(20, 120, 80, "Rope"),
        ],
        ["Iron Sword", "Leather Armor", "Health Potion", "Rope"],
    ),
    Caso(
        "inglês: menu num print com texto mais à direita",
        "en",
        [
            caixa(20, 0, 200, "New game"),
            caixa(20, 40, 180, "Continue"),
            caixa(20, 80, 160, "Options"),
            caixa(20, 120, 80, "Quit"),
            caixa(900, 300, 120, "v1.0.3"),
        ],
        ["New game", "Continue", "Options", "Quit", "v1.0.3"],
    ),
    Caso(
        "inglês: balão estreito de 4 linhas, só a última curta (NÃO é menu)",
        "en",
        [
            caixa(20, 0, 440, "The old lighthouse has"),
            caixa(20, 40, 400, "been dark for twenty"),
            caixa(20, 80, 410, "years, but tonight it"),
            caixa(20, 120, 260, "shines again."),
        ],
        ["The old lighthouse has been dark for twenty years, but tonight it shines again."],
    ),
    Caso(
        "inglês: balão estreito com linhas curtas começando com nome (NÃO é menu)",
        "en",
        [
            caixa(20, 0, 330, "I met Sarah and"),
            caixa(20, 40, 260, "Tom at the"),
            caixa(20, 80, 330, "Riverside Mill last"),
            caixa(20, 120, 140, "night."),
        ],
        ["I met Sarah and Tom at the Riverside Mill last night."],
    ),
    Caso(
        "alemão: fala estreita, linhas começando com substantivo (NÃO é menu)",
        "de",
        [
            caixa(20, 0, 315, "Der Wächter sagt, das"),
            caixa(20, 40, 270, "Tor bleibt bis zum"),
            caixa(20, 80, 375, "Morgengrauen geschlossen."),
        ],
        ["Der Wächter sagt, das Tor bleibt bis zum Morgengrauen geschlossen."],
    ),
    Caso(
        "alemão: fala estreita sem ponto no fim, linhas começando com substantivo (NÃO é menu)",
        "de",
        [
            caixa(20, 0, 315, "Der Wächter sagt, die"),
            caixa(20, 40, 195, "Brücke bleibt"),
            caixa(20, 80, 375, "Nachtwächtern vorbehalten"),
        ],
        ["Der Wächter sagt, die Brücke bleibt Nachtwächtern vorbehalten"],
    ),
    Caso(
        "inglês: ficha de atributos empilhada",
        "en",
        [
            caixa(20, 0, 200, "Strength 72"),
            caixa(20, 40, 230, "Intelligence 42"),
            caixa(20, 80, 190, "Willpower 40"),
            caixa(20, 120, 120, "Luck 40"),
        ],
        ["Strength 72", "Intelligence 42", "Willpower 40", "Luck 40"],
    ),
    Caso(
        "inglês: menu de só 2 itens, o 1º mais largo (duas linhas não bastam para ver o menu)",
        "en",
        [
            caixa(20, 0, 200, "New game"),
            caixa(20, 40, 180, "Continue"),
        ],
        ["New game", "Continue"],
        limite_conhecido=True,
    ),
    Caso(
        "japonês: fala estreita de 3 linhas (a regra de menu sem espaço corta as curtas)",
        "ja",
        [
            caixa(20, 0, 300, "夜になると森の奥から"),
            caixa(20, 40, 240, "不思議な歌が"),
            caixa(20, 80, 270, "聞こえてくる。"),
        ],
        ["夜になると森の奥から不思議な歌が聞こえてくる。"],
        limite_conhecido=True,
    ),
    # Problema 8 (19/11/2026): listas em que um item quebrou em duas linhas, com o passo
    # menor dentro do item, e prosa estreita com passos curtos que não pode virar lista
    Caso(
        "inglês: tópicos com minúscula e dois tópicos em duas linhas (caixas sobrepostas)",
        "en",
        topicos(),
        TOPICOS_ESPERADOS,
    ),
    Caso(
        "inglês: os mesmos tópicos, uma caixa por palavra",
        "en",
        topicos(por_palavra=True),
        TOPICOS_ESPERADOS,
    ),
    Caso(
        "inglês: menu com um item em duas linhas (passo menor dentro do item)",
        "en",
        coluna(["Apprentices", ("Disappearance of the", "Traders"), "Northmoor", "Promotions"]),
        ["Apprentices", "Disappearance of the Traders", "Northmoor", "Promotions"],
    ),
    Caso(
        "inglês: lista cujo 1º item quebra em duas linhas",
        "en",
        coluna([("Lost caravan of the", "Traders"), "Training", "Northmoor", "Promotions",
                ("Return the stolen", "amulet"), "Ranks"]),
        ["Lost caravan of the Traders", "Training", "Northmoor", "Promotions",
         "Return the stolen amulet", "Ranks"],
    ),
    Caso(
        "inglês: lista em que todo item quebra em duas linhas",
        "en",
        coluna([("Lost caravan of the", "Traders"), ("Return the stolen", "amulet"),
                ("Find the missing", "courier"), ("Clear the old", "mine")]),
        ["Lost caravan of the Traders", "Return the stolen amulet", "Find the missing courier",
         "Clear the old mine"],
    ),
    Caso(
        "árabe: lista alinhada à direita com um item em duas linhas",
        "ar",
        [
            caixa(502, 0, 98, "البداية"),
            caixa(376, 40, 224, "قصة الملك القديم"),
            caixa(516, 64, 84, "والجبل"),
            caixa(488, 104, 112, "الخيارات"),
            caixa(488, 144, 112, "المساعدة"),
            caixa(516, 184, 84, "الخروج"),
        ],
        ["البداية", "قصة الملك القديم والجبل", "الخيارات", "المساعدة", "الخروج"],
    ),
    Caso(
        "alemão: fala estreita de 6 linhas sem ponto, com um passo curto (NÃO é lista)",
        "de",
        [
            caixa(20, 0, 280, "Der alte Wächter sagt"),
            caixa(20, 40, 252, "dass die Brücke im"),
            caixa(20, 80, 196, "Winter nur den"),
            caixa(20, 108, 224, "Händlern aus dem"),
            caixa(20, 148, 224, "Norden und ihren"),
            caixa(20, 188, 252, "Wagen offen bleibt"),
        ],
        [
            "Der alte Wächter sagt dass die Brücke im Winter nur den Händlern aus dem Norden "
            "und ihren Wagen offen bleibt"
        ],
    ),
    Caso(
        "alemão: a mesma fala com dois passos curtos (NÃO é lista)",
        "de",
        [
            caixa(20, 0, 280, "Der alte Wächter sagt"),
            caixa(20, 26, 252, "dass die Brücke im"),
            caixa(20, 66, 196, "Winter nur den"),
            caixa(20, 106, 224, "Händlern aus dem"),
            caixa(20, 132, 224, "Norden und ihren"),
            caixa(20, 172, 252, "Wagen offen bleibt"),
        ],
        [
            "Der alte Wächter sagt dass die Brücke im Winter nur den Händlern aus dem Norden "
            "und ihren Wagen offen bleibt"
        ],
    ),
    Caso(
        "inglês: fala estreita com o desenho de uma lista de tópicos, mas com ponto (NÃO é lista)",
        "en",
        [
            caixa(20, 0, 308, "Everyone in the harbor"),
            caixa(20, 24, 126, "remembers"),
            caixa(20, 64, 182, "unfortunately"),
            caixa(20, 104, 224, "the storm of the"),
            caixa(20, 128, 84, "winter"),
            caixa(20, 168, 182, "when the lamp"),
            caixa(20, 208, 126, "went out."),
        ],
        [
            "Everyone in the harbor remembers unfortunately the storm of the winter when the "
            "lamp went out."
        ],
    ),
    Caso(
        "inglês: menu de itens com larguras parecidas (nenhuma linha bem mais curta)",
        "en",
        [
            caixa(20, 0, 260, "Health Potion"),
            caixa(20, 40, 230, "Mana Potion"),
            caixa(20, 80, 230, "Antidote"),
            caixa(20, 120, 120, "Elixir"),
        ],
        ["Health Potion", "Mana Potion", "Antidote", "Elixir"],
        limite_conhecido=True,
    ),
    Caso(
        "inglês: itens com minúscula e o mesmo passo (iguais a uma frase quebrada)",
        "en",
        coluna(["Training", "errands", "join the Guild", "orders", "Northmoor"]),
        ["Training", "errands", "join the Guild", "orders", "Northmoor"],
        limite_conhecido=True,
    ),
    Caso(
        "inglês: falas seguidas e uma nota entre elas, com um vão um pouco maior (1,44)",
        "en",
        [
            caixa(20, 0, 880, 'YOU - "Was I singing this?" (Show her the empty case'),
            caixa(20, 32, 870, "of the record with the smallest church in the whole"),
            caixa(20, 64, 870, "town on the cover, the one you found by the door.)"),
            caixa(20, 110, 380, "+5 XP: gained experience."),
            caixa(20, 156, 880, 'KLAASJE - "Yes! There was a church in there. A very'),
            caixa(20, 188, 870, "small church, the smallest and saddest church in"),
            caixa(20, 220, 400, 'the whole world."'),
        ],
        [
            'YOU - "Was I singing this?" (Show her the empty case of the record with the '
            'smallest church in the whole town on the cover, the one you found by the door.)',
            "+5 XP: gained experience.",
            'KLAASJE - "Yes! There was a church in there. A very small church, the smallest '
            'and saddest church in the whole world."',
        ],
    ),
    Caso(
        "inglês: duas listas de itens com um vão um pouco maior entre elas (1,56)",
        "en",
        coluna(["ACE'S HIGH", "LONESOME ROAD", "GUILLAUME LE MILLION OF THE NORTHERN HILLS"],
               passo=32)
        + [caixa(20, 114 + 32 * k, 14 * len(texto), texto)
           for k, texto in enumerate(["REVACHOLIAN NATIONHOOD", "HOBOCOP", "INEXPLICABLE AGENDA"])],
        ["ACE'S HIGH", "LONESOME ROAD", "GUILLAUME LE MILLION OF THE NORTHERN HILLS",
         "REVACHOLIAN NATIONHOOD", "HOBOCOP", "INEXPLICABLE AGENDA"],
    ),
    Caso(
        "espanhol: fala com a última palavra sozinha na linha, caixa mais estreita que a tela",
        "es",
        [
            caixa(40, 0, 14 * 27, "Yo soy Robin, la carpintera"),
            caixa(40, 40, 14 * 29, "local. El alcalde Lewis me ha"),
            caixa(40, 80, 14 * 30, "pedido que te enseñe el camino"),
            caixa(40, 120, 14 * 27, "a tu nuevo hogar. Te espera"),
            caixa(40, 160, 14 * 31, "allí, arreglándolo todo para tu"),
            caixa(40, 200, 14 * 8, "llegada."),
            caixa(900, 260, 14 * 5, "Robin"),
        ],
        [
            "Yo soy Robin, la carpintera local. El alcalde Lewis me ha pedido que te enseñe el "
            "camino a tu nuevo hogar. Te espera allí, arreglándolo todo para tu llegada.",
            "Robin",
        ],
    ),
    Caso(
        "inglês: parágrafo com uma linha um pouco mais afastada (1,19 do passo) não quebra",
        "en",
        [
            caixa(20, 0, 880, "The road to the harbor was longer than anyone had"),
            caixa(20, 32, 870, "expected, and by the time the lights of the town"),
            caixa(20, 70, 880, "appeared over the hill the rain had already begun"),
            caixa(20, 102, 500, "to soak through their coats."),
        ],
        [
            "The road to the harbor was longer than anyone had expected, and by the time the "
            "lights of the town appeared over the hill the rain had already begun to soak "
            "through their coats."
        ],
    ),
]
