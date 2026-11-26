"""Motores de tradução que o usuário pode escolher nas configurações.

Cada motor recebe (texto, origem, destino, credenciais) e devolve a tradução, ou
levanta ErroMotor com uma mensagem em português pronta para mostrar ao usuário.
Os motores pagos somam no uso_motores os caracteres que o serviço vai cobrar.

O texto chega com um parágrafo por linha (paragrafos.py). As APIs oficiais recebem
um item por parágrafo no mesmo pedido, e a tradução volta com as mesmas quebras.

Todos os serviços são chamados direto, com tempo limite. As APIs oficiais (Azure, DeepL e
Google Cloud) pela REST: as classes do deep-translator para elas faziam pedidos extras,
usavam um formato de autenticação antigo do DeepL e não tratavam os erros de cota. O
Google grátis pela página móvel do Google Tradutor, a mesma que o deep-translator lia,
mas com tempo limite e com o bloqueio reconhecido (26/11/2026).
"""

import html
import re
from dataclasses import dataclass
from typing import Callable

import requests

import uso_motores
from tradutor_offline import traduzir_offline

TEMPO_LIMITE = 15  # segundos por pedido às APIs

# Por quanto tempo um motor fica de fora depois de cada tipo de recusa
PAUSA_BLOQUEIO = 10 * 60  # Google web pediu CAPTCHA; dobra a cada bloqueio seguido...
PAUSA_BLOQUEIO_MAXIMA = 6 * 60 * 60  # ...até isso
PAUSA_COTA = 60 * 60  # cota grátis do mês esgotada
PAUSA_RAJADA = 60  # pedidos demais em pouco tempo

# Quantos textos cada API aceita num pedido só
MAXIMO_TEXTOS_AZURE = 1000
MAXIMO_TEXTOS_DEEPL = 50
MAXIMO_TEXTOS_GOOGLE_CLOUD = 128

# Google grátis: a página móvel do Google Tradutor, que aceita até 5000 letras por pedido
GOOGLE_WEB = "https://translate.google.com/m"
MAXIMO_LETRAS_GOOGLE_WEB = 5000
_RESULTADO_GOOGLE_WEB = re.compile(
    r'<div[^>]*\bclass="[^"]*\b(?:t0|result-container)\b[^"]*"[^>]*>(.*?)</div>', re.DOTALL
)
_QUEBRA_HTML = re.compile(r"<br\s*/?>", re.IGNORECASE)
_TAG_HTML = re.compile(r"<[^>]+>")
_bloqueios_do_google = {"seguidos": 0}

# Códigos do app (vindos do EasyOCR) que cada serviço escreve de outro jeito
_CODIGOS_GOOGLE = {"ch_sim": "zh-CN", "ch_tra": "zh-TW", "rs_cyrillic": "sr", "rs_latin": "sr"}
_CODIGOS_AZURE = {
    "ch_sim": "zh-Hans",
    "ch_tra": "zh-Hant",
    "rs_cyrillic": "sr-Cyrl",
    "rs_latin": "sr-Latn",
}
# O DeepL exige a variante no destino: PT-BR/PT-PT e EN-US/EN-GB
_CODIGOS_DEEPL = {"pt": "PT-BR", "en": "EN-US", "ch_sim": "ZH-HANS", "ch_tra": "ZH-HANT"}


class ErroMotor(Exception):
    """Falha de um motor. A mensagem já vem pronta para o usuário.

    pausar_segundos > 0 indica bloqueio ou cota: o motor fica de fora por esse tempo.
    """

    def __init__(self, mensagem: str, pausar_segundos: int = 0) -> None:
        super().__init__(mensagem)
        self.pausar_segundos = pausar_segundos


def _chave(credenciais: dict, servico: str) -> str:
    chave = credenciais.get("chave", "").strip()
    if not chave:
        raise ErroMotor(f"chave {servico} não configurada")
    return chave


def _postar(url: str, **kwargs) -> requests.Response:
    try:
        return requests.post(url, timeout=TEMPO_LIMITE, **kwargs)
    except requests.RequestException as e:
        raise ErroMotor("sem conexão com o servidor de tradução") from e


def _paragrafos(texto: str, maximo: int) -> list:
    """Um item por parágrafo. Se passar do máximo da API, o excesso vai junto no último."""
    paragrafos = [linha.strip() for linha in texto.split("\n") if linha.strip()] or [texto]
    if len(paragrafos) > maximo:
        paragrafos = paragrafos[: maximo - 1] + [" ".join(paragrafos[maximo - 1 :])]
    return paragrafos


def _mensagem_da_api(resposta: requests.Response) -> str:
    """Tira a mensagem de erro do JSON da resposta (cada API usa um formato)."""
    try:
        dados = resposta.json()
    except ValueError:
        return resposta.text[:200]
    erro = dados.get("error", dados) if isinstance(dados, dict) else dados
    if isinstance(erro, dict):
        return str(erro.get("message", erro))[:200]
    return str(erro)[:200]


def _trechos(texto: str, maximo: int) -> list:
    """As linhas do texto em trechos de até `maximo` letras, sem partir uma linha que caiba."""
    trechos: list = []
    atual = ""
    for linha in texto.split("\n"):
        for inicio in range(0, max(len(linha), 1), maximo):
            pedaco = linha[inicio : inicio + maximo]
            juntos = f"{atual}\n{pedaco}" if atual else pedaco
            if len(juntos) > maximo:
                trechos.append(atual)
                juntos = pedaco
            atual = juntos
    if atual.strip():
        trechos.append(atual)
    return trechos


def _pausa_do_bloqueio(resposta: requests.Response) -> int:
    """Quanto tempo o Google fica de fora depois de um bloqueio.

    O Google mantém o bloqueio enquanto vê pedidos automáticos da rede, então a pausa dobra
    a cada bloqueio seguido (10 min, 20 min, 40 min...), até 6 h. Se ele disser quanto
    esperar (Retry-After), vale o maior dos dois.
    """
    _bloqueios_do_google["seguidos"] += 1
    pausa = PAUSA_BLOQUEIO * 2 ** (_bloqueios_do_google["seguidos"] - 1)
    try:
        pausa = max(pausa, int(resposta.headers.get("Retry-After", "0")))
    except ValueError:
        pass  # Retry-After também pode vir como data; aí vale a pausa dobrada
    return min(pausa, PAUSA_BLOQUEIO_MAXIMA)


def _traduzir_trecho_google_web(trecho: str, alvo: str) -> str:
    try:
        resposta = requests.get(
            GOOGLE_WEB, params={"sl": "auto", "tl": alvo, "q": trecho}, timeout=TEMPO_LIMITE
        )
    except requests.RequestException as e:
        raise ErroMotor("sem conexão com o Google") from e
    # O Google acha automático o tráfego da rede e manda para a página do CAPTCHA
    # (google.com/sorry), às vezes com 429, às vezes com 200. O bloqueio é do IP da rede
    # inteira: outra biblioteca ou outro User-Agent não mudam nada, e o app não tenta
    # passar pelo CAPTCHA.
    if resposta.status_code == 429 or "/sorry/" in resposta.url:
        raise ErroMotor(
            "o Google bloqueou esta rede e pediu um captcha; escolha a Azure grátis ou o modo "
            "offline nas configurações, ou espere",
            _pausa_do_bloqueio(resposta),
        )
    if resposta.status_code != 200:
        raise ErroMotor(f"o Google recusou o pedido (código {resposta.status_code})")
    achado = _RESULTADO_GOOGLE_WEB.search(resposta.text)
    if not achado:
        raise ErroMotor("o Google não devolveu a tradução (a página dele pode ter mudado)")
    _bloqueios_do_google["seguidos"] = 0
    return html.unescape(_TAG_HTML.sub("", _QUEBRA_HTML.sub("\n", achado.group(1)))).strip()


def traduzir_google_web(texto: str, _origem: str, destino: str, _credenciais: dict) -> str:
    """Google Tradutor pela página móvel (grátis, sem chave, sem garantia)."""
    alvo = _CODIGOS_GOOGLE.get(destino, destino)
    return "\n".join(
        _traduzir_trecho_google_web(trecho, alvo)
        for trecho in _trechos(texto, MAXIMO_LETRAS_GOOGLE_WEB)
    )


def traduzir_azure(texto: str, _origem: str, destino: str, credenciais: dict) -> str:
    """Microsoft Azure AI Translator (API v3)."""
    cabecalhos = {
        "Ocp-Apim-Subscription-Key": _chave(credenciais, "da Azure"),
        "Content-Type": "application/json",
    }
    # Recursos regionais exigem a região no cabeçalho; os "global", não.
    # Aceita o nome como o portal mostra: "Brazil South" vira "brazilsouth".
    regiao = credenciais.get("regiao", "").replace(" ", "").lower()
    if regiao and regiao != "global":
        cabecalhos["Ocp-Apim-Subscription-Region"] = regiao

    paragrafos = _paragrafos(texto, MAXIMO_TEXTOS_AZURE)
    resposta = _postar(
        "https://api.cognitive.microsofttranslator.com/translate",
        params={"api-version": "3.0", "to": _CODIGOS_AZURE.get(destino, destino)},
        headers=cabecalhos,
        json=[{"Text": paragrafo} for paragrafo in paragrafos],
    )
    if resposta.status_code == 401:
        raise ErroMotor("chave da Azure inválida ou região errada")
    if resposta.status_code == 403:
        mensagem = _mensagem_da_api(resposta)
        raise ErroMotor(f"a Azure recusou (cota grátis esgotada?): {mensagem}", PAUSA_COTA)
    if resposta.status_code == 429:
        raise ErroMotor("pedidos demais para a Azure em pouco tempo", PAUSA_RAJADA)
    if not resposta.ok:
        raise ErroMotor(f"a Azure respondeu {resposta.status_code}: {_mensagem_da_api(resposta)}")
    traducao = "\n".join(item["translations"][0]["text"] for item in resposta.json())
    # A Azure diz no cabeçalho quantos caracteres vai cobrar por este pedido
    enviados = sum(len(paragrafo) for paragrafo in paragrafos)
    try:
        cobrados = int(resposta.headers.get("X-Metered-Usage", enviados))
    except ValueError:
        cobrados = enviados
    uso_motores.registrar("azure", cobrados)
    return traducao


def _servidor_deepl(chave: str) -> str:
    # Chaves do plano grátis terminam em ":fx" e usam outro endereço
    return "api-free.deepl.com" if chave.endswith(":fx") else "api.deepl.com"


def traduzir_deepl(texto: str, _origem: str, destino: str, credenciais: dict) -> str:
    """DeepL API (v2)."""
    chave = _chave(credenciais, "do DeepL")
    paragrafos = _paragrafos(texto, MAXIMO_TEXTOS_DEEPL)
    resposta = _postar(
        f"https://{_servidor_deepl(chave)}/v2/translate",
        headers={"Authorization": f"DeepL-Auth-Key {chave}"},
        json={"text": paragrafos, "target_lang": _CODIGOS_DEEPL.get(destino, destino.upper())},
    )
    if resposta.status_code == 403:
        raise ErroMotor("chave do DeepL inválida")
    if resposta.status_code == 456:
        raise ErroMotor("cota grátis do mês esgotada no DeepL", PAUSA_COTA)
    if resposta.status_code == 429:
        raise ErroMotor("pedidos demais para o DeepL em pouco tempo", PAUSA_RAJADA)
    if not resposta.ok:
        raise ErroMotor(f"o DeepL respondeu {resposta.status_code}: {_mensagem_da_api(resposta)}")
    traducao = "\n".join(item["text"] for item in resposta.json()["translations"])
    # O DeepL cobra pelo texto de origem
    uso_motores.registrar("deepl", sum(len(paragrafo) for paragrafo in paragrafos))
    return traducao


def consultar_uso_deepl(credenciais: dict) -> tuple:
    """Uso oficial do mês no DeepL: (caracteres usados, limite do plano).

    O DeepL é o único dos motores pagos que informa o uso pela própria chave.
    """
    chave = _chave(credenciais, "do DeepL")
    try:
        resposta = requests.get(
            f"https://{_servidor_deepl(chave)}/v2/usage",
            headers={"Authorization": f"DeepL-Auth-Key {chave}"},
            timeout=TEMPO_LIMITE,
        )
    except requests.RequestException as e:
        raise ErroMotor("sem conexão com o DeepL") from e
    if resposta.status_code == 403:
        raise ErroMotor("chave do DeepL inválida")
    if not resposta.ok:
        raise ErroMotor(f"o DeepL respondeu {resposta.status_code}: {_mensagem_da_api(resposta)}")
    dados = resposta.json()
    return int(dados["character_count"]), int(dados["character_limit"])


def traduzir_google_cloud(texto: str, _origem: str, destino: str, credenciais: dict) -> str:
    """Google Cloud Translation (API Basic v2, a oficial e paga)."""
    paragrafos = _paragrafos(texto, MAXIMO_TEXTOS_GOOGLE_CLOUD)
    resposta = _postar(
        "https://translation.googleapis.com/language/translate/v2",
        headers={"X-goog-api-key": _chave(credenciais, "do Google Cloud")},
        json={
            "q": paragrafos,
            "target": _CODIGOS_GOOGLE.get(destino, destino),
            "format": "text",
        },
    )
    mensagem = _mensagem_da_api(resposta) if not resposta.ok else ""
    if resposta.status_code == 400 and "api key" in mensagem.lower():
        raise ErroMotor("chave do Google Cloud inválida")
    if resposta.status_code == 403:
        raise ErroMotor(
            "o Google Cloud recusou: confira se a Cloud Translation API e o faturamento "
            f"estão ativos no projeto ({mensagem})"
        )
    if resposta.status_code == 429:
        raise ErroMotor("cota do Google Cloud atingida", PAUSA_COTA)
    if not resposta.ok:
        raise ErroMotor(f"o Google Cloud respondeu {resposta.status_code}: {mensagem}")
    traducao = "\n".join(
        item["translatedText"] for item in resposta.json()["data"]["translations"]
    )
    # Conta tudo, até os espaços
    uso_motores.registrar("google_cloud", sum(len(paragrafo) for paragrafo in paragrafos))
    return traducao


def traduzir_argos(texto: str, origem: str, destino: str, _credenciais: dict) -> str:
    """Argos Translate, no próprio computador."""
    try:
        return traduzir_offline(texto, origem, destino)
    except Exception as e:  # pylint: disable=broad-exception-caught
        raise ErroMotor(f"o tradutor offline falhou ({e})") from e


@dataclass(frozen=True)
class InfoMotor:
    """O que a tela de configurações mostra sobre cada motor."""

    nome: str
    nome_curto: str
    descricao: str
    traduzir: Callable[[str, str, str, dict], str]
    links: tuple = ()  # pares (texto, url)
    campos: tuple = ()  # "chave" e/ou "regiao"
    limite_gratis: int = 0  # caracteres grátis por mês; 0 = motor sem limite contado
    # True quando passar do limite grátis pode gerar cobrança (o DeepL Free só recusa)
    trava_de_custo: bool = False


# A ordem aqui é a ordem da lista na tela de configurações
MOTORES = {
    "google_web": InfoMotor(
        nome="Google Tradutor (grátis, sem cadastro)",
        nome_curto="Google",
        descricao=(
            "Não precisa de conta. Pode ser bloqueado por um tempo quando o Google "
            "acha que recebeu pedidos demais da sua rede."
        ),
        traduzir=traduzir_google_web,
    ),
    "azure": InfoMotor(
        nome="Microsoft Azure Translator",
        nome_curto="Azure",
        descricao=(
            "Plano Free (F0): 2 milhões de caracteres por mês. A conta Azure pede cartão "
            "para verificação. A região é a escolhida ao criar o recurso Translator "
            "(ex.: brazilsouth, eastus ou global)."
        ),
        traduzir=traduzir_azure,
        links=(
            ("Criar conta", "https://azure.microsoft.com/free/"),
            (
                "Criar o recurso Translator",
                "https://portal.azure.com/#create/Microsoft.CognitiveServicesTextTranslation",
            ),
            (
                "Passo a passo",
                "https://learn.microsoft.com/azure/ai-services/translator/"
                "create-translator-resource",
            ),
        ),
        campos=("chave", "regiao"),
        limite_gratis=2_000_000,
        trava_de_custo=True,
    ),
    "deepl": InfoMotor(
        nome="DeepL",
        nome_curto="DeepL",
        descricao=(
            "Plano API Free: 500 mil caracteres por mês. Pede cartão só para verificação. "
            'As chaves do plano grátis terminam em ":fx".'
        ),
        traduzir=traduzir_deepl,
        links=(
            ("Criar conta (API Free)", "https://www.deepl.com/pro-api"),
            ("Pegar a chave", "https://www.deepl.com/your-account/keys"),
        ),
        campos=("chave",),
        limite_gratis=500_000,
    ),
    "google_cloud": InfoMotor(
        nome="Google Cloud Translation",
        nome_curto="Google Cloud",
        descricao=(
            "500 mil caracteres por mês grátis (crédito mensal de US$ 10). Exige "
            "faturamento ativo com cartão: configure um alerta de orçamento."
        ),
        traduzir=traduzir_google_cloud,
        links=(
            ("Criar projeto", "https://console.cloud.google.com/projectcreate"),
            (
                "Ativar a API",
                "https://console.cloud.google.com/apis/library/translate.googleapis.com",
            ),
            ("Criar a chave", "https://console.cloud.google.com/apis/credentials"),
            (
                "Limitar o uso por dia",
                "https://console.cloud.google.com/apis/api/translate.googleapis.com/quotas",
            ),
        ),
        campos=("chave",),
        limite_gratis=500_000,
        trava_de_custo=True,
    ),
    "offline": InfoMotor(
        nome="Offline (Argos Translate)",
        nome_curto="Offline",
        descricao=(
            "Roda no seu PC, sem limite e sem internet. A primeira tradução de cada "
            "idioma baixa cerca de 80 MB. Qualidade menor que as outras opções."
        ),
        traduzir=traduzir_argos,
    ),
}


def traduzir_com(motor: str, texto: str, origem: str, destino: str, credenciais: dict) -> str:
    """Traduz só com o motor pedido, sem reservas. credenciais é o dict de todos os motores."""
    return MOTORES[motor].traduzir(texto, origem, destino, credenciais.get(motor, {}))
