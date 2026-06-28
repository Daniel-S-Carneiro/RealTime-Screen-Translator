"""Módulo responsável pelo motor de OCR usando EasyOCR."""

import os
from typing import List, Optional
import easyocr


class MotorOCR:
    """Motor de OCR para extrair texto de imagens usando EasyOCR."""

    def __init__(self, idiomas: Optional[List[str]] = None) -> None:
        self.idiomas_atuais = idiomas if idiomas else ["en", "pt"]

        print(f"Inicializando EasyOCR: {self.idiomas_atuais}...")
        self.reader = easyocr.Reader(self.idiomas_atuais, gpu=False)

    def extrair_texto(self, caminho_imagem: str) -> str:
        """Lê uma imagem local e retorna o texto consolidado em uma string."""
        if not os.path.exists(caminho_imagem):
            return "Erro: Imagem não encontrada."

        try:
            # paragraph=True agrupa blocos de texto logicamente
            resultados = self.reader.readtext(caminho_imagem, paragraph=True)

            texto_extraido = []
            for item in resultados:
                if isinstance(item, (list, tuple)) and len(item) > 1:
                    texto_extraido.append(str(item[1]))

            # Consolidação do texto
            texto_bruto = " ".join(texto_extraido).strip()

            # CAMADA DE LIMPEZA INTELIGENTE:
            # Corrige artefatos comuns gerados por fontes estilizadas em jogos
            texto_limpo = texto_bruto.replace("; ", ", ")
            texto_limpo = texto_limpo.replace("claimlit", "claim it")

            return texto_limpo

        except (RuntimeError, TypeError, ValueError) as e:
            return f"Erro processamento OCR: {str(e)}"

    def alterar_idioma(self, novo_idioma: str) -> None:
        """Altera dinamicamente o idioma."""
        if novo_idioma in self.idiomas_atuais:
            return

        print(f"Baixando/Carregando novo modelo para: {novo_idioma}")
        self.idiomas_atuais = [novo_idioma]
        self.reader = easyocr.Reader(self.idiomas_atuais, gpu=False)


if __name__ == "__main__":
    MOTOR = MotorOCR(idiomas=["en"])
    print("Motor OCR pronto para uso.")
