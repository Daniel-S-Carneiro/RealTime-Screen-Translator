"""Motores de tradução que o usuário pode escolher nas configurações.

Cada motor recebe (texto, origem, destino, credenciais) e devolve a tradução, ou
levanta ErroMotor com uma mensagem em português pronta para mostrar ao usuário.

As APIs oficiais (Azure, DeepL e Google Cloud) são chamadas direto pela REST, com
tempo limite: as classes do deep-translator para elas fazem pedidos extras, usam
um formato de autenticação antigo do DeepL e não tratam os erros de cota.
"""

from dataclasses import dataclass
from typing import Callable

import requests
from deep_translator import GoogleTranslator
from deep_translator.exceptions import (
    LanguageNotSupportedException,
    NotValidPayload,
    RequestError,
    TooManyRequests,
    TranslationNotFound,
)

from tradutor_offline import traduzir_offline

TEMPO_LIMITE = 15  # segundos por pedido às APIs

# Por quanto tempo um motor fica de fora depois de cada tipo de recusa
PAUSA_BLOQUEIO = 10 * 60  # Google web pediu CAPTCHA
PAUSA_COTA = 60 * 60  # cota grátis do mês esgotada
PAUSA_RAJADA = 60  # pedidos demais em pouco tempo

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


def traduzir_google_web(texto: str, _origem: str, destino: str, _credenciais: dict) -> str:
    """Google Tradutor pela página web (grátis, sem chave, sem garantia)."""
    try:
        alvo = _CODIGOS_GOOGLE.get(destino, destino)
        return GoogleTranslator(source="auto", target=alvo).translate(texto)
    except TooManyRequests as e:
        # O Google responde 429 e pede CAPTCHA quando acha o tráfego do IP suspeito.
        # O bloqueio é da rede, não de um clique a mais, e costuma passar sozinho.
        raise ErroMotor("o Google bloqueou temporariamente esta rede", PAUSA_BLOQUEIO) from e
    except LanguageNotSupportedException as e:
        raise ErroMotor(f"o Google não traduz para '{destino}'") from e
    except (TranslationNotFound, NotValidPayload) as e:
        raise ErroMotor(f"tradução não encontrada ({e})") from e
    except RequestError as e:
        raise ErroMotor("o Google recusou o pedido") from e
    except (ConnectionError, requests.RequestException) as e:
        # requests.ConnectionError e Timeout não herdam do ConnectionError do Python
        raise ErroMotor("sem conexão com o Google") from e


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

    resposta = _postar(
        "https://api.cognitive.microsofttranslator.com/translate",
        params={"api-version": "3.0", "to": _CODIGOS_AZURE.get(destino, destino)},
        headers=cabecalhos,
        json=[{"Text": texto}],
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
    return resposta.json()[0]["translations"][0]["text"]


def traduzir_deepl(texto: str, _origem: str, destino: str, credenciais: dict) -> str:
    """DeepL API (v2)."""
    chave = _chave(credenciais, "do DeepL")
    # Chaves do plano grátis terminam em ":fx" e usam outro endereço
    servidor = "api-free.deepl.com" if chave.endswith(":fx") else "api.deepl.com"
    resposta = _postar(
        f"https://{servidor}/v2/translate",
        headers={"Authorization": f"DeepL-Auth-Key {chave}"},
        json={"text": [texto], "target_lang": _CODIGOS_DEEPL.get(destino, destino.upper())},
    )
    if resposta.status_code == 403:
        raise ErroMotor("chave do DeepL inválida")
    if resposta.status_code == 456:
        raise ErroMotor("cota grátis do mês esgotada no DeepL", PAUSA_COTA)
    if resposta.status_code == 429:
        raise ErroMotor("pedidos demais para o DeepL em pouco tempo", PAUSA_RAJADA)
    if not resposta.ok:
        raise ErroMotor(f"o DeepL respondeu {resposta.status_code}: {_mensagem_da_api(resposta)}")
    return resposta.json()["translations"][0]["text"]


def traduzir_google_cloud(texto: str, _origem: str, destino: str, credenciais: dict) -> str:
    """Google Cloud Translation (API Basic v2, a oficial e paga)."""
    resposta = _postar(
        "https://translation.googleapis.com/language/translate/v2",
        headers={"X-goog-api-key": _chave(credenciais, "do Google Cloud")},
        json={"q": texto, "target": _CODIGOS_GOOGLE.get(destino, destino), "format": "text"},
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
    return resposta.json()["data"]["translations"][0]["translatedText"]


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
        ),
        campos=("chave",),
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
