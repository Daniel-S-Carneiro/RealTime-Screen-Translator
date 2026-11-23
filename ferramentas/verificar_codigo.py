"""Confere o código com Pylint e Pyright (o mesmo motor do Pylance).

Uso, a partir da raiz do projeto:
    env/Scripts/python.exe ferramentas/verificar_codigo.py            todo o código do git
    env/Scripts/python.exe ferramentas/verificar_codigo.py a.py b.py  só esses arquivos
    env/Scripts/python.exe ferramentas/verificar_codigo.py --gancho   arquivo editado pelo Claude

laboratorios/ e tudo o que o git ignora ficam de fora.
Saída: 0 = limpo; 1 = há alertas; 2 = alertas devolvidos ao Claude (só com --gancho).
"""

import io
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple, Optional

RAIZ = Path(__file__).resolve().parents[1]
PYTHON = RAIZ / "env" / "Scripts" / "python.exe"
PYRIGHT = RAIZ / "ferramentas" / "node_modules" / "pyright" / "index.js"
INSTALAR_PYRIGHT = "npm ci --prefix ferramentas"
MODELO_PYLINT = "{path}|{line}|{msg_id}|{symbol}|{msg}"
USO_ERRADO_PYLINT = 32
MAXIMO_NO_GANCHO = 30

# Alertas já analisados e sem defeito, em arquivos congelados que não podem ser anotados agora
ALARMES_FALSOS = {
    ("gerenciador_idiomas.py", "E1137"): "é um dicionário; a anotação confunde o Pylint",
}


class Alerta(NamedTuple):
    """Um aviso de uma das ferramentas."""

    arquivo: str
    linha: int
    ferramenta: str
    codigo: str
    mensagem: str

    def __str__(self) -> str:
        return f"{self.arquivo}:{self.linha}: [{self.ferramenta}] {self.codigo}: {self.mensagem}"


class FerramentaIndisponivel(RuntimeError):
    """A verificação não rodou, o que é diferente de não ter achado nada."""


def _rodar(comando: list) -> subprocess.CompletedProcess:
    ambiente = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    try:
        return subprocess.run(
            comando, cwd=RAIZ, env=ambiente, capture_output=True,
            encoding="utf-8", errors="replace", check=False,
        )
    except OSError as erro:
        raise FerramentaIndisponivel(f"não consegui executar {comando[0]}: {erro}") from erro


def _no_escopo(caminho: str) -> Optional[str]:
    """Caminho relativo à raiz se for um .py do projeto que o git não ignora."""
    arquivo = Path(caminho)
    arquivo = (arquivo if arquivo.is_absolute() else RAIZ / arquivo).resolve()
    if arquivo.suffix != ".py" or not arquivo.is_file() or not arquivo.is_relative_to(RAIZ):
        return None
    relativo = arquivo.relative_to(RAIZ).as_posix()
    ignorado = _rodar(["git", "check-ignore", "-q", "--", relativo]).returncode == 0
    return None if ignorado else relativo


def _todo_o_codigo() -> list:
    saida = _rodar(["git", "ls-files", "--cached", "--others", "--exclude-standard", "--", "*.py"])
    return [nome for nome in saida.stdout.splitlines() if (RAIZ / nome).is_file()]


def _pylint(arquivos: list) -> list:
    # benchmark/benchmark.py tem o nome da pasta: junto dos testes, o Pylint erra o import
    grupos = (
        [nome for nome in arquivos if nome.startswith("benchmark/")],
        [nome for nome in arquivos if not nome.startswith("benchmark/")],
    )
    alertas = []
    for grupo in filter(None, grupos):
        saida = _rodar([
            str(PYTHON), "-m", "pylint", "--disable=duplicate-code", "--score=n",
            f"--msg-template={MODELO_PYLINT}", *grupo,
        ])
        if saida.returncode & USO_ERRADO_PYLINT:
            raise FerramentaIndisponivel(f"Pylint falhou: {saida.stderr.strip()[:300]}")
        lidos = [linha.split("|", 4) for linha in saida.stdout.splitlines()]
        novos = [
            Alerta(p[0].replace("\\", "/"), int(p[1]), "Pylint", f"{p[2]} {p[3]}", p[4])
            for p in lidos if len(p) == 5 and p[1].isdigit()
        ]
        if saida.returncode and not novos:
            raise FerramentaIndisponivel(f"Pylint falhou: {saida.stderr.strip()[:300]}")
        alertas += novos
    return alertas


def _pyright(arquivos: list) -> list:
    if not PYRIGHT.is_file():
        raise FerramentaIndisponivel(f"Pyright não instalado. Rode: {INSTALAR_PYRIGHT}")
    saida = _rodar(["node", str(PYRIGHT), "--outputjson", "--pythonpath", str(PYTHON), *arquivos])
    try:
        diagnosticos = json.loads(saida.stdout)["generalDiagnostics"]
    except (ValueError, KeyError) as erro:
        raise FerramentaIndisponivel(f"Pyright falhou: {saida.stderr.strip()[:300]}") from erro
    return [
        Alerta(
            Path(item["file"]).resolve().relative_to(RAIZ).as_posix(),
            item["range"]["start"]["line"] + 1,
            "Pyright",
            item.get("rule", item["severity"]),
            " ".join(item["message"].replace("\xa0", " ").split()),
        )
        for item in diagnosticos if item["severity"] in ("error", "warning")
    ]


def conferir(arquivos: list) -> tuple:
    """(alertas a analisar, quantos alarmes falsos conhecidos ficaram de fora)."""
    todos = _pylint(arquivos) + _pyright(arquivos)
    alertas = sorted(a for a in todos if (a.arquivo, a.codigo.split()[0]) not in ALARMES_FALSOS)
    return alertas, len(todos) - len(alertas)


def _gancho() -> int:
    """Depois de uma edição: só fala com o Claude se houver algo a analisar."""
    dados = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    caminho = dados.get("tool_input", {}).get("file_path", "")
    arquivo = _no_escopo(caminho) if caminho else None
    if arquivo is None:
        return 0
    try:
        alertas, _ = conferir([arquivo])
    except FerramentaIndisponivel as erro:
        print(f"A verificação NÃO rodou em {arquivo}: {erro}", file=sys.stderr)
        return 2
    if not alertas:
        return 0
    print(
        f"Pylint/Pyright: {len(alertas)} alerta(s) em {arquivo}. Classifique cada um: real, "
        "corrigir; falso, ajustar a anotação sem mudar o comportamento. Em .py congelado, "
        "só relatar ao usuário (docs/referencia-validacao.md).",
        file=sys.stderr,
    )
    for alerta in alertas[:MAXIMO_NO_GANCHO]:
        print(alerta, file=sys.stderr)
    if len(alertas) > MAXIMO_NO_GANCHO:
        print(f"... e mais {len(alertas) - MAXIMO_NO_GANCHO}", file=sys.stderr)
    return 2


def _manual(pedidos: list) -> int:
    arquivos = [nome for nome in map(_no_escopo, pedidos) if nome] if pedidos else _todo_o_codigo()
    if not arquivos:
        print("Nenhum arquivo do projeto para conferir.")
        return 0
    try:
        alertas, conhecidos = conferir(arquivos)
    except FerramentaIndisponivel as erro:
        print(f"A verificação NÃO rodou: {erro}")
        return 1
    for alerta in alertas:
        print(alerta)
    print(f"{len(arquivos)} arquivo(s), {len(alertas)} alerta(s), "
          f"{conhecidos} alarme(s) falso(s) já analisado(s).")
    return 1 if alertas else 0


def main() -> int:
    """Escolhe o modo pelos argumentos."""
    for fluxo in (sys.stdout, sys.stderr):
        if isinstance(fluxo, io.TextIOWrapper):
            fluxo.reconfigure(encoding="utf-8")
    argumentos = sys.argv[1:]
    return _gancho() if argumentos == ["--gancho"] else _manual(argumentos)


if __name__ == "__main__":
    sys.exit(main())
