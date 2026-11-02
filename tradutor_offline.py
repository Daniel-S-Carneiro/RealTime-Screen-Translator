"""Tradutor offline (Argos Translate), usado como reserva quando o Google falha.

Os modelos ficam em ~/.local/share/argos-translate e são baixados uma única vez,
na primeira tradução de cada par de idiomas (cerca de 100 MB cada). Depois disso,
a tradução roda no próprio computador, sem internet e sem limite de uso.
"""

# O argostranslate é importado só quando a reserva é usada: ele carrega spaCy,
# Stanza e CTranslate2, o que deixaria a abertura do app bem mais lenta.
# pylint: disable=import-outside-toplevel

import threading

# Códigos do app (EasyOCR/Google) que o Argos escreve de outro jeito
_CODIGOS_ARGOS = {"ch_sim": "zh", "zh-cn": "zh", "ch_tra": "zt", "zh-tw": "zt"}
# No Argos, "pb" é o português do Brasil e "pt" é o de Portugal
_PREFERENCIAS_DESTINO = {"pt": ["pb", "pt"]}

# Baixar/instalar o mesmo modelo duas vezes ao mesmo tempo corromperia a pasta
_trava = threading.Lock()


def _codigo_argos(codigo: str) -> str:
    codigo = codigo.lower()
    return _CODIGOS_ARGOS.get(codigo, codigo.split("-")[0])


def _obter_traducao(origem: str, destino: str):
    """Tradução instalada de origem para destino (direta ou via outro idioma), ou None."""
    from argostranslate import translate

    idioma_origem = translate.get_language_from_code(origem)
    idioma_destino = translate.get_language_from_code(destino)
    if idioma_origem is None or idioma_destino is None:
        return None
    return idioma_origem.get_translation(idioma_destino)


def _instalar(origem: str, destino: str) -> bool:
    """Baixa o modelo do par; se ele não existir, baixa o caminho passando pelo inglês."""
    from argostranslate import package

    package.update_package_index()
    disponiveis = {(p.from_code, p.to_code) for p in package.get_available_packages()}
    if (origem, destino) in disponiveis:
        pares = [(origem, destino)]
    elif (origem, "en") in disponiveis and ("en", destino) in disponiveis:
        pares = [(origem, "en"), ("en", destino)]
    else:
        return False

    for de, para in pares:
        if _obter_traducao(de, para) is None:
            print(f"Baixando modelo offline {de} -> {para} (só na primeira vez)...")
            package.install_package_for_language_pair(de, para)
    return True


def traduzir_offline(texto: str, origem: str, destino: str) -> str:
    """Traduz no próprio computador. Na primeira vez de cada par, precisa de internet."""
    origem = _codigo_argos(origem)
    destino = _codigo_argos(destino)
    candidatos = _PREFERENCIAS_DESTINO.get(destino, [destino])

    with _trava:
        for alvo in candidatos:
            traducao = _obter_traducao(origem, alvo)
            if traducao is not None:
                return traducao.translate(texto)

        for alvo in candidatos:
            if _instalar(origem, alvo):
                traducao = _obter_traducao(origem, alvo)
                if traducao is not None:
                    return traducao.translate(texto)

    raise ValueError(f"não há modelo offline de '{origem}' para '{destino}'")
