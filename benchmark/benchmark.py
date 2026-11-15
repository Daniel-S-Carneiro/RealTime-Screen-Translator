"""Benchmark de OCR: roda o pipeline de produção nas imagens de benchmark/dataset.

Uso (na pasta do projeto):
    env\\Scripts\\python.exe benchmark\\benchmark.py
    env\\Scripts\\python.exe benchmark\\benchmark.py --configs producao
    env\\Scripts\\python.exe benchmark\\benchmark.py --periodo base,2026-11-14
    env\\Scripts\\python.exe benchmark\\benchmark.py --repeticoes 3 --detalhes

As imagens ficam em subpastas: base/ (os exemplos que vão para o git) e uma pasta por
dia de coleta (AAAA-MM-DD). Pastas que começam com "_" (ex.: _fora/) ficam fora do
teste. Cada imagem precisa de um gabarito com o mesmo nome e extensão .txt
(ex.: menu_principal.png + menu_principal.txt). Veja benchmark/README.md.
"""

import argparse
import csv
import difflib
import statistics
import sys
import warnings
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Optional

PASTA_BENCHMARK = Path(__file__).resolve().parent
PASTA_PROJETO = PASTA_BENCHMARK.parent
PASTA_DATASET = PASTA_BENCHMARK / "dataset"
PASTA_RELATORIOS = PASTA_PROJETO / "relatorios" / "benchmark"
# Pastas de dataset/ com esse começo guardam prints que não entram no teste
PREFIXO_FORA = "_"
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
QUEBRA = "¶"  # marca de quebra de parágrafo na comparação das quebras

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


def _fichas(texto: str) -> list:
    """Palavras do texto, com QUEBRA entre um parágrafo (linha) e o seguinte."""
    fichas = []
    for linha in (linha for linha in texto.lower().splitlines() if linha.strip()):
        if fichas:
            fichas.append(QUEBRA)
        fichas.extend(linha.split())
    return fichas


def acerto_quebras(gabarito: str, lido: str) -> tuple:
    """(quebras certas, quebras postas, quebras do gabarito), comparando linha a linha.

    As palavras são alinhadas antes, para um erro de OCR numa palavra não fazer a
    quebra vizinha contar como errada.
    """
    esperado, obtido = _fichas(gabarito), _fichas(lido)
    blocos = difflib.SequenceMatcher(None, esperado, obtido, autojunk=False).get_matching_blocks()
    certas = sum(esperado[b.a : b.a + b.size].count(QUEBRA) for b in blocos)
    return certas, obtido.count(QUEBRA), esperado.count(QUEBRA)


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


def pasta_da_imagem(caminho: Path) -> str:
    """Subpasta de dataset/ onde a imagem está ("base", "2026-11-14"), ou "." na raiz."""
    partes = caminho.relative_to(PASTA_DATASET).parts
    return partes[0] if len(partes) > 1 else "."


def no_periodo(pasta: str, periodos: list) -> bool:
    """Diz se a pasta entra no teste. Sem períodos, entram todas.

    Cada período é o nome de uma pasta ("base", "2026-11-14"), o começo dele
    ("2026-11" pega o mês todo) ou um intervalo com as duas pontas incluídas
    ("2026-11-01..2026-11-14").
    """
    if not periodos:
        return True
    for periodo in periodos:
        if ".." in periodo:
            inicio, fim = periodo.split("..", 1)
            if inicio <= pasta and pasta[: len(fim)] <= fim:
                return True
        elif pasta.startswith(periodo):
            return True
    return False


def carregar_dataset(periodos: Optional[list] = None):
    """Devolve (amostras imagem+gabarito já carregadas, imagens ainda sem gabarito)."""
    amostras, pendentes = [], []
    for caminho in sorted(PASTA_DATASET.rglob("*")):
        if caminho.suffix.lower() not in EXTENSOES_IMAGEM:
            continue
        pasta = pasta_da_imagem(caminho)
        if pasta.startswith(PREFIXO_FORA) or not no_periodo(pasta, periodos or []):
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
    parser.add_argument(
        "--periodo",
        default="",
        help=(
            "Só estas pastas de dataset/, separadas por vírgula: base, 2026-11-14, "
            "2026-11 (o mês todo) ou 2026-11-01..2026-11-14. Padrão: todas"
        ),
    )
    parser.add_argument("--idioma", default="en", help="Idioma do texto das imagens")
    parser.add_argument(
        "--detalhes", action="store_true", help="Mostra as palavras erradas de cada imagem"
    )
    args = parser.parse_args()

    args.configs = [nome.strip() for nome in args.configs.split(",") if nome.strip()]
    args.periodo = [periodo.strip() for periodo in args.periodo.split(",") if periodo.strip()]
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
    cer = taxa_erro_caracteres(normalizar(gabarito), lido)
    wer = taxa_erro_palavras(normalizar(gabarito), lido)
    certas, postas, esperadas = acerto_quebras(gabarito, execucoes[-1].texto)
    tempo_total = sum(tempos.values())

    print(
        f"  {nome:<26} CER {cer:6.2%}  WER {wer:6.2%}  quebras {certas:2}/{esperadas:<2}"
        f" ({postas - certas} a mais)  {tempo_total:5.2f}s"
    )
    if args.detalhes:
        print(f"    {diferencas(normalizar(gabarito), lido)}")

    return {
        "configuracao": nome,
        "cer": round(cer * 100, 2),
        "wer": round(wer * 100, 2),
        "quebras_certas": certas,
        "quebras_postas": postas,
        "quebras_gabarito": esperadas,
        "tempo_imagem": round(tempos["imagem"], 3),
        "tempo_ocr": round(tempos["ocr"], 3),
        "tempo_texto": round(tempos["texto"], 3),
        "tempo_total": round(tempo_total, 3),
        "texto_lido": execucoes[-1].texto,
    }


def _medias(medidas: list) -> str:
    """CER, WER, quebras e tempo de um grupo de medições, já formatados para o resumo.

    Quebras achadas: das quebras dos gabaritos, quantas o pipeline pôs.
    Quebras certas: das quebras que o pipeline pôs, quantas estão nos gabaritos.
    """
    certas = sum(m["quebras_certas"] for m in medidas)
    achadas = certas / max(sum(m["quebras_gabarito"] for m in medidas), 1)
    acertadas = certas / max(sum(m["quebras_postas"] for m in medidas), 1)
    return (
        f"{statistics.mean(m['cer'] for m in medidas):8.2f}%"
        f" {statistics.mean(m['wer'] for m in medidas):8.2f}%"
        f" {achadas:15.0%} {acertadas:6.0%}"
        f" {statistics.mean(m['tempo_total'] for m in medidas):10.2f}s"
    )


def imprimir_resumo(linhas: list, args, total_imagens: int, use_gpu: bool) -> None:
    """Média de cada configuração e a imagem em que ela mais errou; depois, por pasta."""
    print(f"\nRESUMO ({total_imagens} imagens, idioma {args.idioma}, GPU: {use_gpu})")
    cabecalho = (
        f"{'CER médio':>9} {'WER médio':>9} {'quebras achadas':>15} {'certas':>6}"
        f" {'tempo médio':>11}"
    )
    print(f"  {'configuração':<26} {cabecalho}  pior imagem")
    for nome in args.configs:
        medidas = [linha for linha in linhas if linha["configuracao"] == nome]
        pior = max(medidas, key=lambda linha: linha["cer"])
        print(f"  {nome:<26} {_medias(medidas)}  {pior['imagem']} ({pior['cer']:.2f}%)")

    # Uma pasta por dia de coleta: dá para ver se um período (ou um jogo) foi pior
    pastas = sorted({linha["pasta"] for linha in linhas})
    if len(pastas) < 2:
        return
    print(f"\nPOR PASTA\n  {'pasta':<26} {cabecalho}  imagens")
    for nome in args.configs:
        if len(args.configs) > 1:
            print(f"  [{nome}]")
        for pasta in pastas:
            medidas = [l for l in linhas if l["configuracao"] == nome and l["pasta"] == pasta]
            print(f"  {pasta:<26} {_medias(medidas)}  {len(medidas):7}")


def salvar_csv(linhas: list) -> None:
    """Grava o relatório em relatorios/benchmark/."""
    PASTA_RELATORIOS.mkdir(parents=True, exist_ok=True)
    caminho_csv = PASTA_RELATORIOS / datetime.now().strftime("benchmark_%Y%m%d_%H%M%S.csv")
    with open(caminho_csv, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(linhas[0]))
        escritor.writeheader()
        escritor.writerows(linhas)
    print(f"\nRelatório salvo em {caminho_csv.relative_to(PASTA_PROJETO)}")


def apresentar_dataset(amostras: list, pendentes: list, periodo: list) -> bool:
    """Lista as imagens pendentes e as pastas que entram no teste. False se não há o que medir."""
    for caminho in pendentes:
        rascunho = caminho.with_name(caminho.stem + ".rascunho.txt")
        dica = f" (corrija {rascunho.name} e renomeie para .txt)" if rascunho.exists() else ""
        print(f"[PENDENTE] {caminho.relative_to(PASTA_DATASET)} sem gabarito{dica}")
    if not amostras:
        filtro = f" no período {','.join(periodo)}" if periodo else ""
        print(f"Nenhuma imagem com gabarito em {PASTA_DATASET}{filtro}")
        return False
    contagem = Counter(pasta_da_imagem(caminho) for caminho, _, _ in amostras)
    print("Pastas: " + ", ".join(f"{pasta} ({total})" for pasta, total in contagem.items()))
    if len(amostras) < 15:
        print(f"[AVISO] Só {len(amostras)} imagens: diferenças pequenas ainda podem ser acaso.")
    return True


def main() -> None:
    """Roda cada configuração em cada imagem e salva o relatório CSV."""
    args = ler_argumentos()

    amostras, pendentes = carregar_dataset(args.periodo)
    if not apresentar_dataset(amostras, pendentes, args.periodo):
        return

    motor = MotorOCR(idiomas=["en", "pt"])
    # Aquecimento: a primeira chamada na GPU (e a carga do BERT) é bem mais lenta que as outras
    imagem_aquecimento = amostras[0][1]
    for nome in args.configs:
        reconhecer_texto(imagem_aquecimento, motor, idioma=args.idioma, **CONFIGURACOES[nome])

    linhas = []
    for caminho, imagem, gabarito in amostras:
        imagem_relativa = caminho.relative_to(PASTA_DATASET).as_posix()
        print(f"\n{imagem_relativa}  ({imagem.shape[1]}x{imagem.shape[0]})")
        for nome in args.configs:
            linha = medir(imagem, gabarito, motor, nome, args)
            linhas.append({"imagem": imagem_relativa, "pasta": pasta_da_imagem(caminho), **linha})

    imprimir_resumo(linhas, args, len(amostras), motor.use_gpu)
    salvar_csv(linhas)


if __name__ == "__main__":
    main()
