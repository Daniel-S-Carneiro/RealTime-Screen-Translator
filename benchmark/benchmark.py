"""Benchmark de OCR: roda o pipeline de produção em todas as imagens de benchmark/dataset.

Uso (na pasta do projeto):
    env\\Scripts\\python.exe benchmark\\benchmark.py
    env\\Scripts\\python.exe benchmark\\benchmark.py --configs producao
    env\\Scripts\\python.exe benchmark\\benchmark.py --repeticoes 3 --detalhes

Cada imagem precisa de um gabarito com o mesmo nome e extensão .txt
(ex.: menu_principal.png + menu_principal.txt). Veja benchmark/README.md.
"""

import argparse
import csv
import difflib
import statistics
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Optional

PASTA_BENCHMARK = Path(__file__).resolve().parent
PASTA_PROJETO = PASTA_BENCHMARK.parent
PASTA_DATASET = PASTA_BENCHMARK / "dataset"
PASTA_RELATORIOS = PASTA_PROJETO / "relatorios" / "benchmark"
sys.path.insert(0, str(PASTA_PROJETO))
warnings.filterwarnings("ignore")

# pylint: disable=wrong-import-position,no-member
import cv2
import numpy as np
from Levenshtein import distance

from capturador import MODO_IMAGEM_PADRAO, MODOS_IMAGEM
from ocr_engine import MotorOCR
from pipeline_ocr import reconhecer_texto

EXTENSOES_IMAGEM = (".png", ".jpg", ".jpeg", ".bmp", ".webp")

# "producao" usa exatamente os padrões do app; as outras mudam uma coisa de cada vez
CONFIGURACOES = {"producao": {}}
for _modo in MODOS_IMAGEM:
    if _modo != MODO_IMAGEM_PADRAO:
        CONFIGURACOES[f"imagem_{_modo}"] = {"modo_imagem": _modo}
CONFIGURACOES["pontuacao_agressiva"] = {"pontuacao_agressiva": True}
CONFIGURACOES["pontuacao_agressiva+bert"] = {"pontuacao_agressiva": True, "usar_ia": True}


def normalizar(texto: str) -> str:
    """Ignora maiúsculas e quebras de linha/espaços repetidos na comparação."""
    return " ".join(texto.lower().split())


def taxa_erro_caracteres(gabarito: str, lido: str) -> float:
    """CER: edições de caractere necessárias / tamanho do gabarito."""
    return distance(gabarito, lido) / max(len(gabarito), 1)


def taxa_erro_palavras(gabarito: str, lido: str) -> float:
    """WER: edições de palavra necessárias / número de palavras do gabarito."""
    palavras_gabarito = gabarito.split()
    return distance(palavras_gabarito, lido.split()) / max(len(palavras_gabarito), 1)


def diferencas(gabarito: str, lido: str) -> str:
    """Mostra só os trechos errados: [-esperado-]{+lido+}."""
    a, b = gabarito.split(), lido.split()
    trechos = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b).get_opcodes():
        if op == "equal":
            continue
        esperado = " ".join(a[i1:i2])
        obtido = " ".join(b[j1:j2])
        trechos.append(f"[-{esperado}-]{{+{obtido}+}}")
    return "  ".join(trechos) if trechos else "(sem diferenças)"


def ler_imagem(caminho: Path) -> Optional[np.ndarray]:
    """Lê a imagem em BGR (None se não abrir).

    Usa imdecode porque o cv2.imread falha no Windows quando o caminho tem acento.
    """
    return cv2.imdecode(np.fromfile(caminho, dtype=np.uint8), cv2.IMREAD_COLOR)


def carregar_dataset():
    """Devolve (amostras imagem+gabarito já carregadas, imagens ainda sem gabarito)."""
    amostras, pendentes = [], []
    for caminho in sorted(PASTA_DATASET.iterdir()):
        if caminho.suffix.lower() not in EXTENSOES_IMAGEM:
            continue
        gabarito = caminho.with_suffix(".txt")
        if not gabarito.exists():
            pendentes.append(caminho)
            continue
        imagem = ler_imagem(caminho)
        if imagem is None:
            print(f"[ERRO] Não consegui abrir {caminho.name}; a imagem ficou de fora.")
            continue
        amostras.append((caminho, imagem, gabarito.read_text(encoding="utf-8")))
    return amostras, pendentes


def ler_argumentos():
    """Lê a linha de comando e valida os nomes das configurações."""
    parser = argparse.ArgumentParser(
        description="Roda o pipeline de OCR de produção nas imagens de benchmark/dataset."
    )
    parser.add_argument(
        "--configs",
        default=",".join(CONFIGURACOES),
        help=f"Lista separada por vírgula. Opções: {', '.join(CONFIGURACOES)}",
    )
    parser.add_argument(
        "--repeticoes", type=int, default=1, help="Execuções por imagem (usa a mediana do tempo)"
    )
    parser.add_argument("--idioma", default="en", help="Idioma do texto das imagens")
    parser.add_argument(
        "--detalhes", action="store_true", help="Mostra as palavras erradas de cada imagem"
    )
    args = parser.parse_args()

    args.configs = [nome.strip() for nome in args.configs.split(",") if nome.strip()]
    desconhecidas = [nome for nome in args.configs if nome not in CONFIGURACOES]
    if desconhecidas:
        parser.error(f"Configuração desconhecida: {', '.join(desconhecidas)}")
    return args


def medir(imagem, gabarito: str, motor: MotorOCR, nome: str, args) -> dict:
    """Roda uma configuração numa imagem e devolve a linha do relatório."""
    execucoes = [
        reconhecer_texto(imagem, motor, idioma=args.idioma, **CONFIGURACOES[nome])
        for _ in range(max(args.repeticoes, 1))
    ]
    lido = normalizar(execucoes[-1].texto)
    tempos = {
        etapa: statistics.median(e.tempos[etapa] for e in execucoes)
        for etapa in execucoes[-1].tempos
    }
    cer = taxa_erro_caracteres(gabarito, lido)
    wer = taxa_erro_palavras(gabarito, lido)
    tempo_total = sum(tempos.values())

    print(f"  {nome:<26} CER {cer:6.2%}  WER {wer:6.2%}  {tempo_total:5.2f}s")
    if args.detalhes:
        print(f"    {diferencas(gabarito, lido)}")

    return {
        "configuracao": nome,
        "cer": round(cer * 100, 2),
        "wer": round(wer * 100, 2),
        "tempo_imagem": round(tempos["imagem"], 3),
        "tempo_ocr": round(tempos["ocr"], 3),
        "tempo_texto": round(tempos["texto"], 3),
        "tempo_total": round(tempo_total, 3),
        "texto_lido": execucoes[-1].texto,
    }


def imprimir_resumo(linhas: list, args, total_imagens: int, use_gpu: bool) -> None:
    """Média de cada configuração e a imagem em que ela mais errou."""
    print(f"\nRESUMO ({total_imagens} imagens, idioma {args.idioma}, GPU: {use_gpu})")
    print(
        f"  {'configuração':<26} {'CER médio':>9} {'WER médio':>9} {'tempo médio':>11}"
        "  pior imagem"
    )
    for nome in args.configs:
        medidas = [linha for linha in linhas if linha["configuracao"] == nome]
        pior = max(medidas, key=lambda linha: linha["cer"])
        print(
            f"  {nome:<26} {statistics.mean(m['cer'] for m in medidas):8.2f}%"
            f" {statistics.mean(m['wer'] for m in medidas):8.2f}%"
            f" {statistics.mean(m['tempo_total'] for m in medidas):10.2f}s"
            f"  {pior['imagem']} ({pior['cer']:.2f}%)"
        )


def salvar_csv(linhas: list) -> None:
    """Grava o relatório em relatorios/benchmark/."""
    PASTA_RELATORIOS.mkdir(parents=True, exist_ok=True)
    caminho_csv = PASTA_RELATORIOS / datetime.now().strftime("benchmark_%Y%m%d_%H%M%S.csv")
    with open(caminho_csv, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(linhas[0]))
        escritor.writeheader()
        escritor.writerows(linhas)
    print(f"\nRelatório salvo em {caminho_csv.relative_to(PASTA_PROJETO)}")


def main() -> None:
    """Roda cada configuração em cada imagem e salva o relatório CSV."""
    args = ler_argumentos()

    amostras, pendentes = carregar_dataset()
    for caminho in pendentes:
        rascunho = caminho.with_name(caminho.stem + ".rascunho.txt")
        dica = f" (corrija {rascunho.name} e renomeie para .txt)" if rascunho.exists() else ""
        print(f"[PENDENTE] {caminho.name} sem gabarito{dica}")
    if not amostras:
        print(f"Nenhuma imagem com gabarito em {PASTA_DATASET}")
        return
    if len(amostras) < 15:
        print(f"[AVISO] Só {len(amostras)} imagens: diferenças pequenas ainda podem ser acaso.")

    motor = MotorOCR(idiomas=["en", "pt"])
    # Aquecimento: a primeira chamada na GPU (e a carga do BERT) é bem mais lenta que as outras
    imagem_aquecimento = amostras[0][1]
    for nome in args.configs:
        reconhecer_texto(imagem_aquecimento, motor, idioma=args.idioma, **CONFIGURACOES[nome])

    linhas = []
    for caminho, imagem, gabarito in amostras:
        print(f"\n{caminho.name}  ({imagem.shape[1]}x{imagem.shape[0]})")
        for nome in args.configs:
            linha = medir(imagem, normalizar(gabarito), motor, nome, args)
            linhas.append({"imagem": caminho.name, **linha})

    imprimir_resumo(linhas, args, len(amostras), motor.use_gpu)
    salvar_csv(linhas)


if __name__ == "__main__":
    main()
