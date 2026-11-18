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
]
