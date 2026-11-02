"""Módulo responsável pela unificação e limpeza de texto bruto extraído pelo OCR."""

import re
from difflib import SequenceMatcher
from spellchecker import SpellChecker

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

    def analisar_confianca(self, resultados_ocr):
        """Extrai o texto bruto e calcula a confiança média do OCR."""
        if not resultados_ocr:
            return "", 0.0

        texto_limpo = []
        confianca_total = 0.0

        for item in resultados_ocr:
            if len(item) >= 3:
                texto = item[1]
                confianca = item[2]
            elif len(item) == 2:
                texto = item[1]
                confianca = 1.0
            else:
                continue

            texto = " ".join(str(texto).split())
            texto_limpo.append(texto)
            confianca_total += float(confianca)

        media_confianca = confianca_total / len(resultados_ocr)
        return " ".join(texto_limpo), media_confianca

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

    def _escolher_correcao(self, erro: str, palavras_bert: list):
        """Escolhe a sugestão do BERT mais parecida com o erro, ou cai no SpellChecker."""
        melhor_palavra_bert = None
        maior_similaridade = 0.0

        # Verifica qual palavra do BERT se parece mais com o erro ortográfico
        for p_bert in palavras_bert:
            sim = SequenceMatcher(None, erro, p_bert).ratio()
            if sim > maior_similaridade:
                maior_similaridade = sim
                melhor_palavra_bert = p_bert

        # Se o BERT sugeriu algo coerente E com similaridade aceitável (>60%)
        if maior_similaridade >= 0.60 and melhor_palavra_bert:
            return melhor_palavra_bert

        # Fallback robusto via SpellChecker
        candidatos = set(self.spell.candidates(erro) or [])
        match_perfeito = candidatos.intersection(set(palavras_bert))
        if match_perfeito:
            return match_perfeito.pop()
        return self.spell.correction(erro)

    def analisar_e_corrigir_ia(self, texto_limpo: str) -> str:
        """Usa SpellChecker e BERT combinados com análise de similaridade."""
        mask_filler = obter_mask_filler()
        if mask_filler is None:
            return texto_limpo

        # Só corrige palavras minúsculas com 3+ letras. Ficam de fora siglas (DMG),
        # abreviações (Lv.5 virava La.5) e nomes próprios (Geralt virava Gerald).
        palavras = [
            p for p in re.findall(r"\b[a-zA-Z]+\b", texto_limpo) if len(p) >= 3 and p.islower()
        ]
        erros = self.spell.unknown(palavras)

        if not erros:
            return texto_limpo

        texto_final = texto_limpo
        for erro in erros:
            padrao = r"\b" + re.escape(erro) + r"\b"
            # TROCA PROTETORA: colchetes viram parênteses só no texto enviado ao BERT,
            # para ele ler com naturalidade. O texto devolvido mantém os originais.
            texto_bert = texto_final.replace("[", "(").replace("]", ")")
            texto_mascarado = re.sub(padrao, "[MASK]", texto_bert, count=1)

            try:
                # Previsão do BERT para a lacuna
                predicoes_bert = mask_filler(texto_mascarado)

                # FILTRO ANTI-SUBWORDS: Descarta tokens de subpalavras do BERT
                palavras_bert = [
                    pred["token_str"].lower()
                    for pred in predicoes_bert
                    if "##" not in pred["token_str"]
                ]
                palavra_escolhida = self._escolher_correcao(erro, palavras_bert)

                if palavra_escolhida and palavra_escolhida != erro:
                    texto_final = re.sub(
                        padrao, palavra_escolhida, texto_final, count=1
                    )
            except Exception:  # pylint: disable=broad-exception-caught
                continue

        return texto_final

    def corrigir_texto(self, texto: str, idioma: str) -> str:
        """Pipeline mestre de correção: Regex -> IA (opcional, só para inglês)."""
        try:
            # 1. Limpeza Bruta
            texto_regex = self.aplicar_regex_limpeza(texto)
            texto_regex = self.separar_palavras_grudadas(texto_regex, idioma)

            # 2. Refinamento de Contexto. O modelo carregado (bert-base-uncased)
            # só conhece inglês, então em outros idiomas ele só atrapalharia.
            if not self.usar_ia or (idioma or "").lower() != "en":
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
    """Pipeline unificado consumido pelo main.py."""
    chave = (usar_ia, pontuacao_agressiva)
    if chave not in _PROCESSADORES:
        _PROCESSADORES[chave] = ProcessadorInteligente(usar_ia, pontuacao_agressiva)
    processador = _PROCESSADORES[chave]
    texto_bruto, _ = processador.analisar_confianca(resultados_ocr)
    return processador.corrigir_texto(texto_bruto, idioma_alvo)
