"""Pipeline de reconhecimento compartilhado pelo app (main.py) e pelo benchmark.

Tudo o que acontece entre o print e o texto pronto para tradução passa por aqui,
para que o benchmark meça exatamente o que o app executa.
"""

import time
from dataclasses import dataclass, field

import numpy as np

from capturador import MODO_IMAGEM_PADRAO, ProcessadorImagem
from ocr_engine import MotorOCR
from processador_texto import pipeline_processamento


@dataclass
class Reconhecimento:
    """Resultado de uma passada do pipeline."""

    texto: str
    imagem_ocr: np.ndarray
    tempos: dict = field(default_factory=dict)


def reconhecer_texto(  # pylint: disable=too-many-arguments
    imagem: np.ndarray,
    motor_ocr: MotorOCR,
    *,
    idioma: str = "en",
    modo_imagem: str = MODO_IMAGEM_PADRAO,
    usar_ia: bool = False,
    pontuacao_agressiva: bool = False,
) -> Reconhecimento:
    """Imagem BGR capturada -> texto pronto para tradução, com o tempo de cada etapa."""
    inicio = time.perf_counter()
    imagem_ocr = ProcessadorImagem.preparar(imagem, modo_imagem)
    fim_imagem = time.perf_counter()

    resultados_ocr = motor_ocr.extrair_dados_completos(imagem_ocr)
    fim_ocr = time.perf_counter()

    texto = pipeline_processamento(
        resultados_ocr,
        idioma_alvo=idioma,
        usar_ia=usar_ia,
        pontuacao_agressiva=pontuacao_agressiva,
    )
    fim_texto = time.perf_counter()

    tempos = {
        "imagem": fim_imagem - inicio,
        "ocr": fim_ocr - fim_imagem,
        "texto": fim_texto - fim_ocr,
    }
    return Reconhecimento(texto=texto, imagem_ocr=imagem_ocr, tempos=tempos)
