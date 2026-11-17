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
        limite_conhecido=True,
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
        limite_conhecido=True,
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
]
