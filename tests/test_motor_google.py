"""Google Tradutor grátis (motores_traducao.traduzir_google_web), com respostas simuladas.

Nenhum teste acessa a rede: o requests.get é trocado por respostas montadas aqui. Os
casos de bloqueio reproduzem o diagnóstico de 26/11/2026, em que o Google respondeu 429 e
mandou para a página do CAPTCHA (google.com/sorry).
"""

import unittest
from dataclasses import dataclass, field
from unittest import mock

import requests

import motores_traducao as M

SORRY = "https://www.google.com/sorry/index?continue=https://translate.google.com/m"
PAGINA = "https://translate.google.com/m?sl=auto&tl=pt&q=Hello"


@dataclass
class Resposta:
    """O pedaço de requests.Response que o motor usa."""

    status_code: int = 200
    url: str = PAGINA
    text: str = ""
    headers: dict = field(default_factory=dict)


def pagina_com(traducao: str, classe: str = "result-container") -> Resposta:
    """A página móvel do Google Tradutor com a tradução no lugar de sempre."""
    return Resposta(text=f'<html><body><div class="{classe}">{traducao}</div></body></html>')


def traduzir(texto: str = "Hello", destino: str = "pt") -> str:
    """Chama o motor como o app chama: origem automática, sem credenciais."""
    return M.traduzir_google_web(texto, "en", destino, {})


def simular(resposta):
    """Troca o requests.get do motor por uma resposta (ou uma lista delas, ou um erro)."""
    if isinstance(resposta, (list, Exception)):
        return mock.patch.object(M.requests, "get", side_effect=resposta)
    return mock.patch.object(M.requests, "get", return_value=resposta)


class TestGoogleWeb(unittest.TestCase):
    """O pedido, a leitura da página e o bloqueio."""

    def setUp(self):
        M._bloqueios_do_google["seguidos"] = 0  # pylint: disable=protected-access

    def bloqueio(self, resposta) -> M.ErroMotor:
        """O ErroMotor que o motor levanta com essa resposta."""
        with simular(resposta):
            with self.assertRaises(M.ErroMotor) as erro:
                traduzir()
        return erro.exception

    def test_traducao_da_pagina(self):
        """Lê a tradução, desfaz o HTML e manda o pedido com tempo limite."""
        with simular(pagina_com("Olá &amp; adeus")) as get:
            self.assertEqual(traduzir(), "Olá & adeus")
        self.assertEqual(get.call_args.kwargs["params"], {"sl": "auto", "tl": "pt", "q": "Hello"})
        self.assertEqual(get.call_args.kwargs["timeout"], M.TEMPO_LIMITE)

    def test_classe_t0_e_quebra_de_linha(self):
        """A outra classe da página e o <br> virando quebra de linha."""
        with simular(pagina_com("Um<br>Dois", "t0")):
            self.assertEqual(traduzir("One\nTwo"), "Um\nDois")

    def test_codigo_do_chines(self):
        """O código do app (ch_sim) vira o do Google (zh-CN)."""
        with simular(pagina_com("你好")) as get:
            traduzir(destino="ch_sim")
        self.assertEqual(get.call_args.kwargs["params"]["tl"], "zh-CN")

    def test_bloqueio_429_na_pagina_do_captcha(self):
        """O caso do diagnóstico de 26/11: 429 e a página google.com/sorry."""
        erro = self.bloqueio(Resposta(429, SORRY))
        self.assertIn("bloqueou esta rede", str(erro))
        self.assertEqual(erro.pausar_segundos, M.PAUSA_BLOQUEIO)

    def test_bloqueio_disfarcado_de_200(self):
        """A página do CAPTCHA com 200; antes, virava 'tradução não encontrada'."""
        erro = self.bloqueio(Resposta(200, SORRY, "<html></html>"))
        self.assertIn("bloqueou esta rede", str(erro))

    def test_pausa_dobra_a_cada_bloqueio_e_zera_depois_de_traduzir(self):
        """10, 20 e 40 minutos; depois de uma tradução, volta a 10."""
        pausas = [self.bloqueio(Resposta(429, SORRY)).pausar_segundos for _ in range(3)]
        self.assertEqual(pausas, [M.PAUSA_BLOQUEIO, 2 * M.PAUSA_BLOQUEIO, 4 * M.PAUSA_BLOQUEIO])
        with simular(pagina_com("Olá")):
            traduzir()
        self.assertEqual(self.bloqueio(Resposta(429, SORRY)).pausar_segundos, M.PAUSA_BLOQUEIO)

    def test_retry_after_e_teto_de_6_horas(self):
        """O tempo que o Google pedir, até 6 h; uma data no lugar dos segundos é ignorada."""
        casos = (("3600", 3600), ("100000", M.PAUSA_BLOQUEIO_MAXIMA), ("amanhã", M.PAUSA_BLOQUEIO))
        for valor, esperado in casos:
            M._bloqueios_do_google["seguidos"] = 0  # pylint: disable=protected-access
            erro = self.bloqueio(Resposta(429, SORRY, headers={"Retry-After": valor}))
            self.assertEqual(erro.pausar_segundos, esperado, valor)

    def test_pagina_sem_traducao(self):
        """A página mudou: o erro diz isso e o motor não entra em pausa."""
        erro = self.bloqueio(Resposta(text="<html></html>"))
        self.assertIn("não devolveu a tradução", str(erro))
        self.assertEqual(erro.pausar_segundos, 0)

    def test_outro_codigo_de_erro(self):
        """Um código que não é bloqueio aparece na mensagem."""
        self.assertIn("código 400", str(self.bloqueio(Resposta(400))))

    def test_sem_conexao_e_tempo_esgotado(self):
        """Falha de rede e tempo esgotado viram a mesma mensagem."""
        for excecao in (requests.ConnectionError(), requests.Timeout()):
            self.assertIn("sem conexão", str(self.bloqueio(excecao)))

    def test_texto_longo_vai_em_mais_de_um_pedido(self):
        """Duas linhas de 3000 letras passam do limite de 5000 e vão em dois pedidos."""
        linha = "a" * 3000
        with simular([pagina_com("um"), pagina_com("dois")]) as get:
            self.assertEqual(traduzir(f"{linha}\n{linha}"), "um\ndois")
        self.assertEqual(get.call_count, 2)


class TestTrechos(unittest.TestCase):
    """O texto em pedaços de até 5000 letras, sem partir uma linha que caiba."""

    def test_junta_linhas_ate_o_maximo(self):
        """Linhas seguidas vão juntas enquanto couberem."""
        trechos = M._trechos("a\nb\nc", 3)  # pylint: disable=protected-access
        self.assertEqual(trechos, ["a\nb", "c"])

    def test_linha_maior_que_o_maximo_e_cortada(self):
        """Uma linha sozinha maior que o máximo é cortada em pedaços."""
        trechos = M._trechos("x" * 12, 5)  # pylint: disable=protected-access
        self.assertEqual(trechos, ["xxxxx", "xxxxx", "xx"])

    def test_linhas_vazias_no_meio_ficam(self):
        """A linha vazia entre parágrafos continua no trecho."""
        trechos = M._trechos("a\n\nb", 10)  # pylint: disable=protected-access
        self.assertEqual(trechos, ["a\n\nb"])


if __name__ == "__main__":
    unittest.main()
