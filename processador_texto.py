"""Módulo responsável pela unificação e limpeza de texto bruto extraído pelo OCR."""

import itertools
import re
from spellchecker import SpellChecker

from paragrafos import montar_paragrafos

# O BERT só é carregado na primeira vez que a correção por IA for usada.
# Ele deixava a abertura do app lenta mesmo com a correção desligada.
_MASK_FILLER = None
_BERT_INDISPONIVEL = False

# Palavras curtas que o OCR costuma grudar na vizinha ("ofthe", "withan", "buffis").
# A divisão por dicionário só corta onde um dos lados é uma delas, para que termos de
# jogo que o dicionário não conhece ("cooldown", "loadout") continuem inteiros.
PALAVRAS_DE_LIGACAO = frozenset(
    "a an the of to in on at by for from with and or is as if all per".split()
)
# No fim da palavra só valem estas: com "in", "on" e "at", "admin" virava "adm in"
LIGACAO_NO_FIM = frozenset("a an the of to and is for with all".split())
ARTIGOS = frozenset({"a", "an", "the"})

# "1 was" -> "I was": verbos que vêm depois de "I" e quase nunca depois de um número
# ("only 1 can trigger" é número, então "can" ficou de fora)
_PRONOME_I = re.compile(
    r"(?<![\w.+\-/\[(])1(?= (?:am|was|wasn't|have|haven't|don't|didn't|think|know|want|"
    r"guess|mean|feel|hope|wonder|believe|never|really|need)\b|'(?:m|ve|ll|d)\b)"
)
# Letras que fontes de jogo fazem o OCR confundir (Morrowind: "chc" = "the", "durics"
# = "duties"; DDLC: "whac" = "what"; Fallout: "Riflc" = "Rifle")
LETRAS_CONFUNDIDAS = {"c": ("e", "t"), "r": ("t",), "l": ("i",)}
# A troca só vale se der palavra comum: palavra curta precisa ser bem comum ("Misc"
# não pode virar "Mist", nem "taur" virar "taut")
FREQUENCIA_MINIMA_CURTA = 1e-5
FREQUENCIA_MINIMA = 5e-7

# Apóstrofo que a fonte apagou ("dont", "Ive", "IM"): só contrações destas palavras,
# para "DPS" não virar "DP'S" nem "Sanas" virar "Sana's"
BASES_CONTRACAO = frozenset(
    "i you we they he she it that there what who here where let don can won isn aren "
    "wasn weren didn doesn haven hasn hadn couldn wouldn shouldn".split()
)
FINS_CONTRACAO = frozenset({"t", "s", "m", "d", "ve", "ll", "re"})

# Quantas palavras o BERT sugere para cada lacuna na correção por contexto
SUGESTOES_BERT = 50


def obter_mask_filler():
    """Carrega o pipeline fill-mask do HuggingFace sob demanda (ou None se falhar)."""
    global _MASK_FILLER, _BERT_INDISPONIVEL  # pylint: disable=global-statement
    if _MASK_FILLER is not None or _BERT_INDISPONIVEL:
        return _MASK_FILLER

    try:
        from transformers import pipeline  # pylint: disable=import-outside-toplevel

        print(
            "Carregando modelo BERT para correção de contexto (isso pode levar alguns segundos)..."
        )
        _MASK_FILLER = pipeline("fill-mask", model="bert-base-uncased")
    except ImportError:
        print(
            "Aviso: Biblioteca 'transformers' não encontrada. Instale com: pip install transformers"
        )
        _BERT_INDISPONIVEL = True
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Aviso: Erro ao carregar o modelo BERT: {e}")
        _BERT_INDISPONIVEL = True
    return _MASK_FILLER


class ProcessadorInteligente:
    """Filtra, analisa, unifica e corrige blocos de texto extraídos pelo OCR usando IA."""

    def __init__(self, usar_ia: bool = False, pontuacao_agressiva: bool = False):
        # Desligados por padrão: nos prints reais testados, a regra de ponto e o
        # BERT pioraram o texto ("Press. Enter", "Aerith" -> "Earth").
        self.usar_ia = usar_ia
        self.pontuacao_agressiva = pontuacao_agressiva
        self._spell = None

    @property
    def spell(self) -> SpellChecker:
        """SpellChecker em inglês, criado na primeira vez que for usado."""
        if self._spell is None:
            self._spell = SpellChecker(language="en")
        return self._spell

    def aplicar_regex_limpeza(self, texto: str) -> str:
        """Aplica regex para limpar e padronizar o texto OCR com pontuação inteligente."""

        def consertar_pontuacao(match):
            palavra_anterior = match.group(1)
            proxima_palavra = match.group(2)

            # REGRA 1: Protege siglas (Tudo maiúsculo). Ex: DMG, HP, DEF, ATK
            if proxima_palavra.isupper() and len(proxima_palavra) > 1:
                return f"{palavra_anterior} {proxima_palavra}"

            # REGRA 2: Protege Títulos e Nomes Próprios. Ex: Dream "of" Realms
            preposicoes = {
                "of",
                "the",
                "and",
                "in",
                "for",
                "with",
                "to",
                "by",
                "on",
                "at",
            }
            if palavra_anterior.lower() in preposicoes:
                return f"{palavra_anterior} {proxima_palavra}"

            # REGRA 3: Se não for sigla nem título, deduzimos que o OCR comeu o ponto final.
            return f"{palavra_anterior}. {proxima_palavra}"

        # 1. Limpa espaços duplos
        texto_modificado = re.sub(r"\s+", " ", texto)

        # 2. Cola pontuações soltas na palavra anterior (ex: "HP ." -> "HP.")
        texto_modificado = re.sub(r"\s+([.,;:!?])", r"\1", texto_modificado)
        texto_modificado = texto_modificado.replace("' s", "'s")

        # As regras abaixo foram ajustadas para o teste.png e erram em texto de jogo:
        # "SAMURAI" -> "SAMURA", "Press Enter" -> "Press. Enter".
        if self.pontuacao_agressiva:
            # 3. Limpa falhas visuais do OCR no final de siglas (ex: DMGI -> DMG)
            texto_modificado = re.sub(r"\b([A-Z]{2,})[Il]\b", r"\1", texto_modificado)

            # 4. APLICA A REGRA INTELIGENTE DE PONTUAÇÃO
            texto_modificado = re.sub(
                r"\b([A-Za-zÀ-Ÿ]*[a-zà-ÿ])\s+([A-ZÀ-Ÿ][a-zA-ZÀ-Ÿ]*)",
                consertar_pontuacao,
                texto_modificado,
            )

            # 5. Limpezas finais de resíduos do OCR
            texto_modificado = texto_modificado.replace(" _ ", ". ")
        return texto_modificado.strip()

    def separar_palavras_grudadas(self, texto: str, idioma: str) -> str:
        """Separa palavras que o OCR juntou quando o espaço entre elas era estreito."""
        # Valem para qualquer idioma
        texto = re.sub(r"(?<=\d%)(?=[A-Za-z])", " ", texto)  # 25%own -> 25% own
        texto = re.sub(r"(?<=[a-z]{2})(?=[A-Z][a-z]{2})", " ", texto)  # MartialArt
        texto = re.sub(r"(?<=[A-Za-z\])])([;,:!?])(?=[A-Za-z])", r"\1 ", texto)  # hits;ignores
        texto = re.sub(r"(?<=[a-z])\.(?=[A-Z][a-z])", ". ", texto)  # blood.It

        # As próximas consultam o dicionário, que é só de inglês
        if (idioma or "").lower() != "en":
            return texto
        texto = re.sub(r"\b(\d+)([a-z]{3,})\b", self._separar_numero, texto)  # 2turns
        texto = re.sub(r"\b([A-Z]{2,})([a-z]{2,})\b", self._separar_sigla, texto)  # DMGto
        return re.sub(r"\b[a-z]{3,}\b", self._separar_por_dicionario, texto)  # ofincoming

    def _separar_numero(self, match) -> str:
        """2turns -> 2 turns. Ordinais (5th, 2nd) têm só 2 letras e nem entram aqui."""
        numero, palavra = match.groups()
        return f"{numero} {palavra}" if palavra in self.spell else match.group(0)

    def _separar_sigla(self, match) -> str:
        """DMGto -> DMG to, DMGRed -> DMG Red: fica o corte cuja palavra é mais comum."""
        sigla, resto = match.groups()
        opcoes = []
        if resto in self.spell:
            opcoes.append((self.spell[resto], f"{sigla} {resto}"))
        palavra = sigla[-1] + resto
        if len(sigla) >= 3 and palavra in self.spell:
            opcoes.append((self.spell[palavra], f"{sigla[:-1]} {palavra}"))
        return max(opcoes)[1] if opcoes else match.group(0)

    def _separar_por_dicionario(self, match) -> str:
        """ofincoming -> of incoming. Só mexe em palavras minúsculas que o dicionário
        não conhece; nomes com inicial maiúscula (Azureblade, Bloodburn) ficam de fora."""
        palavra = match.group(0)
        if palavra in self.spell:
            return palavra
        # Entre os cortes válidos, fica o de partes mais comuns
        cortes = [
            (min(self.spell[palavra[:i]], self.spell[palavra[i:]]), f"{palavra[:i]} {palavra[i:]}")
            for i in range(1, len(palavra))
            if self._divisao_valida(palavra[:i], palavra[i:])
        ]
        return max(cortes)[1] if cortes else palavra

    def _divisao_valida(self, esquerda: str, direita: str) -> bool:
        """Aceita o corte só se as duas partes existem e uma delas é palavra de ligação."""
        if esquerda not in self.spell or direita not in self.spell:
            return False
        ligacao_esquerda = esquerda in PALAVRAS_DE_LIGACAO
        ligacao_direita = direita in LIGACAO_NO_FIM
        if ligacao_esquerda and ligacao_direita:
            # "ofthe", "witha"; artigo seguido de outra ligação ("athe") não vale
            return esquerda not in ARTIGOS
        if ligacao_direita:
            # "buffis" -> "buff is"; artigo no fim só depois de ligação, então "mana" fica
            return direita not in ARTIGOS and len(esquerda) >= 3
        if ligacao_esquerda:
            # Em inglês "a" vem antes de consoante e "an" antes de vogal: "aether" fica
            vogal = direita[0] in "aeiou"
            artigo_errado = (esquerda == "a" and vogal) or (esquerda == "an" and not vogal)
            return len(direita) >= 3 and not artigo_errado
        return False

    @staticmethod
    def corrigir_numeros_trocados(texto: str) -> str:
        """Letra que o OCR leu como número (só inglês): "1 was" -> "I was", "g0" -> "go",
        e o contrário dentro de número: "1Omm" -> "10mm", "3Oth" -> "30th"."""
        texto = _PRONOME_I.sub("I", texto)
        texto = re.sub(r"(?<=[A-Za-z])0(?=[a-z]|\b)", "o", texto)
        return re.sub(r"(?<=\b\d)[Oo](?=\d|mm\b|th\b)", "0", texto)

    def corrigir_letras_confundidas(self, texto: str) -> str:
        """Desfaz trocas de letra que fontes de jogo provocam (c/e, c/t, r/t, l/i).

        Só mexe em palavra que o dicionário não conhece, e só aceita a troca que der
        palavra comum. Palavras com apóstrofo e siglas (tudo maiúsculo) ficam de fora.
        """
        return re.sub(r"[A-Za-z]+(?:'[A-Za-z]+)*", self._trocar_letras_confundidas, texto)

    def _trocar_letras_confundidas(self, match) -> str:
        palavra = match.group(0)
        minuscula = palavra.lower()
        if "'" in palavra or len(minuscula) < 3 or minuscula in self.spell:
            return palavra
        if not (palavra.islower() or palavra.istitle()):
            return palavra
        posicoes = [i for i, letra in enumerate(minuscula) if letra in LETRAS_CONFUNDIDAS]
        if not posicoes or len(posicoes) > 6:
            return palavra
        opcoes = [(minuscula[i],) + LETRAS_CONFUNDIDAS[minuscula[i]] for i in posicoes]
        candidatas = set()
        for escolha in itertools.product(*opcoes):
            letras = list(minuscula)
            for i, nova in zip(posicoes, escolha):
                letras[i] = nova
            candidatas.add("".join(letras))
        candidatas = [c for c in candidatas if c != minuscula and c in self.spell]
        if not candidatas:
            return palavra
        nova = max(candidatas, key=self.spell.word_usage_frequency)
        minima = FREQUENCIA_MINIMA_CURTA if len(nova) <= 4 else FREQUENCIA_MINIMA
        if self.spell.word_usage_frequency(nova) < minima:
            return palavra
        return nova.capitalize() if palavra.istitle() else nova

    def corrigir_apostrofo(self, texto: str) -> str:
        """Devolve o apóstrofo que a fonte apagou: "dont" -> "don't", "Ive" -> "I've".

        Só em palavra fora do dicionário que vira uma contração conhecida, então
        "cant" e "wont" (que existem) ficam como estão, e siglas como "DPS" também.
        """
        return re.sub(r"(?<!['\w])[A-Za-z]+(?![\w'])", self._trocar_apostrofo, texto)

    def _trocar_apostrofo(self, match) -> str:
        palavra = match.group(0)
        minuscula = palavra.lower()
        if len(minuscula) < 2 or minuscula in self.spell:
            return palavra
        for corte in (1, 2):
            base, fim = minuscula[:-corte], minuscula[-corte:]
            if base in BASES_CONTRACAO and fim in FINS_CONTRACAO and f"{base}'{fim}" in self.spell:
                return f"{palavra[:-corte]}'{palavra[-corte:]}"
        return palavra

    def analisar_e_corrigir_ia(self, texto: str) -> str:
        """Corrige pelo contexto só quando o dicionário e o BERT concordam.

        Para cada palavra minúscula fora do dicionário, as candidatas são as palavras
        do dicionário a 1 ou 2 letras de distância e as trocas de letra das fontes. O
        BERT lista as palavras que cabem naquele lugar da frase, e a troca só acontece
        se uma candidata estiver entre elas. Sem acordo, a palavra fica como está.

        A versão anterior aceitava a sugestão do dicionário mesmo sem o BERT concordar
        e trocava termos de jogo ("swarmer" -> "warmer", "melee" -> "pelee"). Nos 90
        prints do benchmark (2026-11-15) esta versão melhorou 4 prints e não estragou
        nenhum termo de jogo.
        """
        mask_filler = obter_mask_filler()
        if mask_filler is None:
            return texto

        # Nomes próprios (Geralt virava Gerald), siglas (DMG) e palavras com apóstrofo
        # ficam de fora: só palavras minúsculas com 3+ letras
        for palavra in sorted(set(re.findall(r"(?<!['\w])[a-z]{3,}(?![\w'])", texto))):
            if palavra in self.spell:
                continue
            candidatas = set(self.spell.candidates(palavra) or []) - {palavra}
            trocada = self.corrigir_letras_confundidas(palavra)
            if trocada != palavra:
                candidatas.add(trocada)
            if not candidatas:
                continue

            padrao = r"(?<!['\w])" + re.escape(palavra) + r"(?![\w'])"
            # Colchetes viram parênteses só no texto enviado ao BERT, para ele ler com
            # naturalidade e não confundir com o [MASK]. O texto devolvido mantém os originais.
            mascarado = re.sub(padrao, "[MASK]", texto.replace("[", "(").replace("]", ")"), count=1)
            try:
                sugestoes = mask_filler(mascarado, top_k=SUGESTOES_BERT)
            except Exception:  # pylint: disable=broad-exception-caught
                continue
            escolhida = next(
                (s["token_str"].strip().lower() for s in sugestoes
                 if s["token_str"].strip().lower() in candidatas),
                None,
            )
            if escolhida:
                texto = re.sub(padrao, escolhida, texto, count=1)
        return texto

    def corrigir_texto(self, texto: str, idioma: str) -> str:
        """Pipeline mestre de correção: Regex -> trocas do OCR -> IA (opcional).

        As trocas do OCR e a IA usam dicionário e regras do inglês, então só rodam nele.
        """
        try:
            # 1. Limpeza Bruta
            texto_regex = self.aplicar_regex_limpeza(texto)
            texto_regex = self.separar_palavras_grudadas(texto_regex, idioma)
            if (idioma or "").lower() != "en":
                return texto_regex

            # 2. Trocas de letra que o OCR faz (benchmark de 2026-11-15: CER de 29% para
            # 23% no Morrowind, sem piorar nenhum dos 90 prints)
            texto_regex = self.corrigir_numeros_trocados(texto_regex)
            texto_regex = self.corrigir_letras_confundidas(texto_regex)
            texto_regex = self.corrigir_apostrofo(texto_regex)

            # 3. Refinamento de Contexto (opcional: carregar o BERT leva ~5 s e cada
            # parágrafo com palavra desconhecida custa ~0,4 s). O modelo carregado
            # (bert-base-uncased) só conhece inglês.
            if not self.usar_ia:
                return texto_regex
            return self.analisar_e_corrigir_ia(texto_regex)

        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Erro no processamento de texto: {e}")
            return texto


# Um processador por combinação de opções, para não recriar o SpellChecker a cada tradução
_PROCESSADORES = {}


def pipeline_processamento(
    resultados_ocr,
    idioma_alvo: str,
    usar_ia: bool = False,
    pontuacao_agressiva: bool = False,
) -> str:
    """Pipeline unificado consumido pelo main.py: um parágrafo corrigido por linha.

    idioma_alvo é a língua do texto lido na tela (a de origem da tradução): ela decide
    a direção da leitura e se as correções do inglês rodam.
    """
    chave = (usar_ia, pontuacao_agressiva)
    if chave not in _PROCESSADORES:
        _PROCESSADORES[chave] = ProcessadorInteligente(usar_ia, pontuacao_agressiva)
    processador = _PROCESSADORES[chave]
    corrigidos = (
        processador.corrigir_texto(paragrafo, idioma_alvo)
        for paragrafo in montar_paragrafos(resultados_ocr, idioma_alvo)
    )
    return "\n".join(paragrafo.strip() for paragrafo in corrigidos if paragrafo.strip())
