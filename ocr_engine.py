"""Módulo responsável pelo motor de OCR usando EasyOCR."""

import os
from typing import List, Optional
import easyocr
import torch


def ordenar_por_linhas(resultados):
    """Ordena as caixas do EasyOCR em ordem de leitura: linha a linha, da esquerda para a direita.

    O EasyOCR devolve as caixas inclinadas no fim da lista, o que jogava trechos
    como "your key:" para o final do texto.
    """
    if len(resultados) < 2:
        return resultados

    caixas = []
    for item in resultados:
        xs = [ponto[0] for ponto in item[0]]
        ys = [ponto[1] for ponto in item[0]]
        caixas.append(((min(ys) + max(ys)) / 2, max(ys) - min(ys), min(xs), item))
    caixas.sort(key=lambda caixa: caixa[0])

    linhas = []
    for centro, altura, esquerda, item in caixas:
        if linhas:
            linha = linhas[-1]
            # Mesma linha quando os centros verticais estão a menos de meia altura de texto
            if abs(centro - linha["centro"]) < min(altura, linha["altura"]) / 2:
                linha["itens"].append((esquerda, item))
                continue
        linhas.append({"centro": centro, "altura": altura, "itens": [(esquerda, item)]})

    return [
        item
        for linha in linhas
        for _, item in sorted(linha["itens"], key=lambda par: par[0])
    ]


class MotorOCR:
    """Motor de OCR para extrair texto de imagens usando EasyOCR."""

    def __init__(self, idiomas: Optional[List[str]] = None) -> None:
        self.idiomas_atuais = idiomas if idiomas else ["en", "pt"]

        # Detecção automática de Hardware (Nvidia GPU vs CPU)
        self.use_gpu = torch.cuda.is_available()
        hardware_nome = "NVIDIA GPU" if self.use_gpu else "CPU"

        print(f"Inicializando EasyOCR ({hardware_nome}): {self.idiomas_atuais}...")
        self.reader = easyocr.Reader(
            self.idiomas_atuais, gpu=self.use_gpu, recog_network="standard"
        )

    def extrair_texto(self, caminho_imagem: str) -> str:
        """Lê uma imagem e retorna o texto bruto."""
        if not os.path.exists(caminho_imagem):
            return "Erro: Imagem não encontrada."

        try:
            # Mantive esse método para retrocompatibilidade, se você ainda usar em algum lugar.
            # O main.py usa o extrair_dados_completos
            resultados = self.reader.readtext(
                caminho_imagem,
                paragraph=True,
                decoder="greedy",
                adjust_contrast=0.0,
            )

            texto_extraido = [
                str(item[1])
                for item in resultados
                if isinstance(item, (list, tuple)) and len(item) > 1
            ]

            return " ".join(texto_extraido).strip()

        except (RuntimeError, TypeError, ValueError) as e:
            return f"Erro processamento OCR: {str(e)}"

    def alterar_idioma(self, novo_idioma: str) -> None:
        """Altera dinamicamente o idioma."""
        if novo_idioma in self.idiomas_atuais:
            return

        print(f"Baixando/Carregando novo modelo para: {novo_idioma}")
        self.idiomas_atuais = [novo_idioma]
        self.reader = easyocr.Reader(
            self.idiomas_atuais, gpu=self.use_gpu, recog_network="standard"
        )

    def extrair_dados_completos(self, imagem):
        """Retorna a lista completa de resultados do EasyOCR, já em ordem de leitura.

        Aceita o caminho de um arquivo ou a imagem como array numpy.
        """
        resultados = self.reader.readtext(
            imagem,
            decoder="greedy",  # <-- Mais rápido que beamsearch e não engole letras duplas
            batch_size=1,  # <-- Processamento único
            adjust_contrast=0.0,  # <-- Desativado: valores testados nos laboratórios
            contrast_ths=0.1,
            paragraph=False,  # <-- Mantemos False para o processador_texto.py cuidar da junção
        )
        return ordenar_por_linhas(resultados)


if __name__ == "__main__":
    MOTOR = MotorOCR(idiomas=["en"])
    print("Motor OCR pronto para uso.")
