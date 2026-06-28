# pylint: disable=no-member
"""Módulo para captura e processamento de imagem usando OpenCV."""

import cv2


class ProcessadorImagem:
    """Classe responsável por preparar imagens para o motor de OCR."""

    @staticmethod
    def preparar_para_ocr(
        caminho_entrada: str, caminho_saida: str = "processada.png"
    ) -> str:
        """Aplica filtros para melhorar a precisão do OCR."""
        # Carrega a imagem
        img = cv2.imread(caminho_entrada)
        if img is None:
            return caminho_entrada

        # 1. Escala de cinza
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 2. Upscaling: Aumenta o tamanho em 2x
        img_grande = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        # 3. Binarização adaptativa
        processada = cv2.adaptiveThreshold(
            img_grande, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        cv2.imwrite(caminho_saida, processada)
        return caminho_saida
