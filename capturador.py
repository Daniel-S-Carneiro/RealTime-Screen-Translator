"""Módulo para processamento de imagem usando OpenCV com foco em OCR."""

# pylint: disable=no-member

import cv2
import numpy as np

# "cinza" teve o menor erro médio e o menor tempo nas imagens de benchmark/dataset
# (nov/2026: CER 0,78% contra 1,41% do "binarizado", que foi 2 a 4x mais lento).
# "binarizado" é o pipeline campeão dos laboratórios, mantido para comparação.
MODOS_IMAGEM = ("original", "cinza", "binarizado")
MODO_IMAGEM_PADRAO = "cinza"


class ProcessadorImagem:
    """Classe responsável por preparar imagens para o motor de OCR."""

    @staticmethod
    def preparar(img: np.ndarray, modo: str = MODO_IMAGEM_PADRAO) -> np.ndarray:
        """Recebe a imagem BGR capturada e devolve a versão que vai para o OCR."""
        if modo not in MODOS_IMAGEM:
            raise ValueError(f"Modo de imagem desconhecido: {modo}")

        if modo == "original":
            return img
        if modo == "binarizado":
            return ProcessadorImagem.binarizar(img)

        if len(img.shape) == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img

    @staticmethod
    def binarizar(img: np.ndarray) -> np.ndarray:
        """
        Pipeline vencedor dos laboratórios (Pipeline #1), feito para o teste.png.
        Fluxo 100% OpenCV: Aumentar(CV) ->
        Ruido_Ini(CV) -> Cor(CV) -> Binarizar Dinâmico(CV) -> Ruido_Fim(CV)
        Atenção: em prints reais ele trocou "14%" por "74%" e "turn" por "tum".
        """
        # 1. Aumentar(CV) - Upscaling 200% via Interpolação Vizinho
        # Mais Próximo (Rápido e mantém bordas duras)
        img = cv2.resize(img, (0, 0), fx=2, fy=2, interpolation=cv2.INTER_NEAREST)

        # 2. Ruido_Ini(CV) - Suavização via Median Blur (Remove artefatos menores sem borrar bordas)
        img = cv2.medianBlur(img, 3)

        # 3. Cor(CV) - Extração de um único canal de cor (Canal Verde) para focar no brilho
        if len(img.shape) == 3:
            img = img[:, :, 1]

        # 4. Binarizar Dinâmico(CV) - Analisa o fundo antes de aplicar o Otsu
        # Como o texto ocupa menos espaço que o fundo, a média de brilho revela a cor predominante.
        # Media > 127 = Fundo claro | Media < 127 = Fundo escuro
        if np.mean(img) > 127:
            # Fundo já é claro: Binarização normal (mantém fundo branco, texto preto)
            _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            # Fundo é escuro: Binarização invertida
            # (transforma fundo escuro em branco e texto em preto)
            _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # 5. Ruido_Fim(CV) - Morfologia Open para limpar ruído "sal e pimenta" após binarizar
        kernel = np.ones((2, 2), np.uint8)
        return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
