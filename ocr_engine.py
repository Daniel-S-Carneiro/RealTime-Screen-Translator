"""Motor de OCR do app: RapidOCR para as línguas que ele lê, EasyOCR para as outras.

O RapidOCR roda os modelos PP-OCRv6 small do PaddleOCR no ONNX Runtime, na CPU. Nos 90
prints do benchmark (2026-11-16) ele baixou o CER de 10,24% (EasyOCR) para 7,87% e o
WER de 22,30% para 12,13%, em 1,1 s por print contra 2,9 s do EasyOCR na GPU MX350.
O modelo dele lê inglês, chinês, japonês e as línguas de alfabeto latino da lista
LINGUAS_RAPID. As outras escritas do app (cirílico, árabe, coreano, devanágari,
tailandês...) continuam no EasyOCR, que baixa o modelo de cada uma na primeira vez.

O RapidOCR, o EasyOCR e o PyTorch só são importados quando a língua pede: lendo inglês,
o app abre sem carregar o PyTorch.
"""

# Os motores são importados só quando a língua escolhida precisa deles
# pylint: disable=import-outside-toplevel,no-member

import re
from typing import List, Optional

import cv2
import numpy as np

from paragrafos import agrupar_em_linhas
from quantidades import completar_quantidades, tirar_icones
from releitura import conferir_caixas_pequenas

# Códigos do idiomas.json (os mesmos do EasyOCR) que o modelo PP-OCRv6 small lê
LINGUAS_CJK = frozenset({"ch_sim", "ch_tra", "ja"})
LINGUAS_RAPID = LINGUAS_CJK | frozenset(
    "af az bs cs cy da de en es et fr ga hr hu id is it ku la lt lv mi ms mt nl no oc "
    "pl pt ro rs_latin sk sl sq sv sw tl tr uz vi".split()
)

# Caixas com confiança menor são lixo na maioria (ícones, texto borrado de fundo). O
# corte foi escolhido antes de olhar os prints: com 0,8 o CER cai mais um pouco, mas
# escolher pelo melhor resultado seria ajustar o corte ao próprio dataset.
CONFIANCA_MINIMA = 0.7

# O PP-OCRv6 é multilíngue e lê ícones como caracteres chineses ("口", "三", "然").
# Lendo uma língua de letras latinas, esses caracteres saem do texto.
CJK = re.compile(r"[⺀-鿿가-힯豈-﫿＀-￯]")

# O detector lê o print no tamanho original (até 2016 px no lado maior). O padrão do
# RapidOCR amplia o print até o lado menor ter 736 px: uma legenda de 1249x193 virava
# 4763x736, o que custava tempo e, no benchmark, piorava a leitura (CER 9,30%).
LADO_MAXIMO = 2016


def ordenar_por_linhas(resultados):
    """Põe as caixas do OCR em ordem de leitura: linha a linha, da esquerda para a direita."""
    return [item for linha in agrupar_em_linhas(resultados) for item in linha]


def usa_rapidocr(idiomas: List[str]) -> bool:
    """True se o RapidOCR lê todas as línguas pedidas."""
    return all(idioma in LINGUAS_RAPID for idioma in idiomas)


def criar_rapidocr():
    """RapidOCR com os modelos PP-OCRv6 small, que vêm dentro do pacote rapidocr."""
    from rapidocr import LangDet, LangRec, ModelType, OCRVersion, RapidOCR

    return RapidOCR(
        params={
            "Global.text_score": 0.0,  # o corte de confiança é feito em _ler_rapidocr
            "Global.use_cls": False,  # texto de jogo não vem de cabeça para baixo
            "Global.log_level": "warning",
            "Det.ocr_version": OCRVersion.PPOCRV6,
            "Det.model_type": ModelType.SMALL,
            "Det.lang_type": LangDet.CH,
            "Det.limit_type": "max",
            "Det.limit_side_len": LADO_MAXIMO,
            "Rec.ocr_version": OCRVersion.PPOCRV6,
            "Rec.model_type": ModelType.SMALL,
            "Rec.lang_type": LangRec.CH,
        }
    )


class MotorOCR:
    """Lê o texto de uma imagem e devolve as caixas no formato do EasyOCR:
    [(4 cantos [[x, y], ...], texto, confiança)], em ordem de leitura."""

    def __init__(self, idiomas: Optional[List[str]] = None) -> None:
        self.idiomas_atuais = idiomas if idiomas else ["en", "pt"]
        self.rapidocr = None
        self.easyocr = None
        self.nome = ""
        self._carregar()

    def _carregar(self) -> None:
        if usa_rapidocr(self.idiomas_atuais):
            self.nome = "RapidOCR (PP-OCRv6 small, CPU)"
            if self.rapidocr is None:
                print(f"Inicializando {self.nome}...")
                self.rapidocr = criar_rapidocr()
            return

        import easyocr
        import torch

        # Detecção automática de Hardware (Nvidia GPU vs CPU)
        usar_gpu = torch.cuda.is_available()
        self.nome = f"EasyOCR ({'NVIDIA GPU' if usar_gpu else 'CPU'})"
        print(f"Inicializando {self.nome}: {self.idiomas_atuais}...")
        self.easyocr = easyocr.Reader(
            self.idiomas_atuais, gpu=usar_gpu, recog_network="standard"
        )

    def alterar_idioma(self, novo_idioma: str) -> None:
        """Altera dinamicamente o idioma."""
        if novo_idioma in self.idiomas_atuais:
            return

        print(f"Carregando a leitura de texto para: {novo_idioma}")
        self.idiomas_atuais = [novo_idioma]
        self._carregar()

    def extrair_texto(self, caminho_imagem: str) -> str:
        """Lê uma imagem e retorna o texto bruto, com as caixas separadas por espaço."""
        imagem = cv2.imread(caminho_imagem)
        if imagem is None:
            return "Erro: Imagem não encontrada."
        return " ".join(texto for _, texto, _ in self.extrair_dados_completos(imagem))

    def extrair_dados_completos(self, imagem):
        """Retorna a lista completa de resultados do OCR, já em ordem de leitura.

        Aceita o caminho de um arquivo ou a imagem como array numpy (cinza ou BGR).
        """
        if usa_rapidocr(self.idiomas_atuais):
            if isinstance(imagem, str):
                imagem = cv2.imread(imagem)
            return ordenar_por_linhas(self._ler_rapidocr(imagem))

        resultados = self.easyocr.readtext(
            imagem,
            decoder="greedy",  # <-- Mais rápido que beamsearch e não engole letras duplas
            batch_size=1,  # <-- Processamento único
            adjust_contrast=0.0,  # <-- Desativado: valores testados nos laboratórios
            contrast_ths=0.1,
            paragraph=False,  # <-- Mantemos False para o paragrafos.py cuidar da junção
        )
        return ordenar_por_linhas(resultados)

    def _ler_rapidocr(self, imagem: np.ndarray) -> list:
        if imagem.ndim == 2:
            cinza = imagem
            imagem = cv2.cvtColor(imagem, cv2.COLOR_GRAY2BGR)
        else:
            cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
        # use_det e use_rec sempre explícitos: o RapidOCR guarda o modo da última chamada,
        # e a releitura (_reler) chama só o reconhecedor
        saida = self.rapidocr(imagem, use_det=True, use_cls=False, use_rec=True)
        if getattr(saida, "boxes", None) is None or saida.txts is None:
            return []

        latina = not any(idioma in LINGUAS_CJK for idioma in self.idiomas_atuais)
        resultados = []
        for caixa, texto, confianca in zip(saida.boxes, saida.txts, saida.scores):
            if confianca < CONFIANCA_MINIMA:
                continue
            texto = self._limpar(str(texto), latina)
            if texto:
                cantos = [[float(x), float(y)] for x, y in caixa]
                resultados.append((cantos, texto, float(confianca)))
        def reler(recorte):
            return self._reler(recorte, latina)

        # Letreiros miúdos: o lixo que o OCR inventa não se confirma numa segunda leitura
        resultados = conferir_caixas_pequenas(cinza, resultados, reler)
        # Inventários: o "1" e o "×" que o detector não marcou; depois, ícones lidos como letra
        resultados, protegidas = completar_quantidades(cinza, resultados, reler)
        return tirar_icones(resultados, cinza.shape[1], protegidas)

    @staticmethod
    def _limpar(texto: str, latina: bool) -> str:
        if latina:
            texto = CJK.sub(" ", texto)
        return " ".join(texto.split())

    def _reler(self, recorte: np.ndarray, latina: bool) -> tuple:
        """Só o reconhecedor, num recorte em cinza: (texto, confiança)."""
        saida = self.rapidocr(
            cv2.cvtColor(recorte, cv2.COLOR_GRAY2BGR), use_det=False, use_cls=False, use_rec=True
        )
        if not saida.txts:
            return "", 0.0
        return self._limpar(str(saida.txts[0]), latina), float(saida.scores[0])


if __name__ == "__main__":
    MOTOR = MotorOCR(idiomas=["en"])
    print("Motor OCR pronto para uso.")
