"""Testes da montagem do texto (paragrafos.py + processador_texto.py) em várias línguas.

Cada caso de tests/casos_paragrafos.py vira um teste. Os de limite conhecido são falhas
esperadas: documentam o limite e avisam se um dia passarem a funcionar.
"""

import unittest

from processador_texto import pipeline_processamento
from tests.casos_paragrafos import CASOS


class TestMontagem(unittest.TestCase):
    """Um teste por caso; os nomes dos métodos são gerados a partir dos casos."""


def _criar_teste(caso):
    def teste(self):
        lido = pipeline_processamento(caso.caixas, caso.idioma).split("\n")
        self.assertEqual(lido, caso.esperado, caso.nome)

    teste.__doc__ = caso.nome
    return unittest.expectedFailure(teste) if caso.limite_conhecido else teste


for _numero, _caso in enumerate(CASOS, start=1):
    setattr(TestMontagem, f"test_{_numero:02d}_{_caso.idioma}", _criar_teste(_caso))


if __name__ == "__main__":
    unittest.main()
