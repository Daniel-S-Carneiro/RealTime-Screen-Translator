"""A escolha do motor sem o Google Tradutor grátis, as reservas e o guia (27/11/2026).

Nenhum teste chama um serviço de tradução: o traduzir_com do tradutor é trocado por uma
função que responde ou falha como cada caso pede. O config.json do guia é um arquivo
temporário, nunca o do usuário.
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import guia_inicial
import motores_traducao as M
import tradutor_engine as E

COM_DEEPL = {"deepl": {"chave": "chave-de-teste:fx"}}
TODAS = {
    "azure": {"chave": "a", "regiao": "brazilsouth"},
    "deepl": {"chave": "d:fx"},
    "google_cloud": {"chave": "g"},
}


class TestMotorValido(unittest.TestCase):
    """O motor salvo que não existe mais vira um que existe."""

    def test_google_gratis_saiu(self):
        """O Google Tradutor grátis não está mais na lista de motores."""
        self.assertNotIn("google_web", M.MOTORES)

    def test_sem_chave_vai_para_o_offline(self):
        """Quem tinha o Google grátis e nenhuma chave passa a usar o offline."""
        self.assertEqual(M.motor_valido("google_web", {}), "offline")

    def test_com_chave_vai_para_o_pago(self):
        """Com uma chave preenchida, vai para o pago dela."""
        self.assertEqual(M.motor_valido("google_web", COM_DEEPL), "deepl")

    def test_chave_em_branco_nao_conta(self):
        """Um campo de chave só com espaços é o mesmo que não ter chave."""
        self.assertEqual(M.motor_valido("google_web", {"azure": {"chave": "  "}}), "offline")

    def test_motor_que_existe_fica(self):
        """O motor salvo que ainda existe não muda, mesmo sem chave."""
        self.assertEqual(M.motor_valido("azure", {}), "azure")


class TestReservas(unittest.TestCase):
    """A ordem dos motores quando o escolhido falha."""

    def test_pago_com_os_outros_pagos_e_o_offline(self):
        """O escolhido, os outros pagos com chave, na ordem da lista, e o offline."""
        tradutor = E.MotorTradutor(motor="google_cloud", credenciais=TODAS)
        self.assertEqual(tradutor.ordem(), ["google_cloud", "azure", "deepl", "offline"])

    def test_pago_sem_outras_chaves(self):
        """Sem outras chaves, a única reserva é o offline."""
        tradutor = E.MotorTradutor(motor="azure", credenciais={"azure": {"chave": "a"}})
        self.assertEqual(tradutor.ordem(), ["azure", "offline"])

    def test_offline_nao_manda_o_texto_para_fora(self):
        """Quem escolheu o offline fica só com ele, mesmo tendo chaves salvas."""
        tradutor = E.MotorTradutor(motor="offline", credenciais=TODAS)
        self.assertEqual(tradutor.ordem(), ["offline"])

    def test_motor_antigo_no_tradutor(self):
        """O tradutor criado com o Google grátis salvo usa o motor válido."""
        self.assertEqual(E.MotorTradutor(motor="google_web", credenciais={}).motor, "offline")

    def test_reserva_marca_o_nome(self):
        """Quando o escolhido falha, a tradução da reserva vem com o nome dela na frente."""

        def traduzir(motor, *_):
            if motor == "azure":
                raise M.ErroMotor("chave da Azure inválida ou região errada")
            return "Olá"

        tradutor = E.MotorTradutor(motor="azure", credenciais=TODAS)
        with mock.patch.object(E, "traduzir_com", side_effect=traduzir), \
                mock.patch.object(E.uso_motores, "trava_ligada", return_value=False):
            self.assertEqual(tradutor.traduzir_texto("Hello"), "[DeepL] Olá")


class TestGuia(unittest.TestCase):
    """Quando o guia da primeira execução aparece, e o que ele diz."""

    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        self.arquivo = Path(self.pasta.name) / "config.json"
        self.troca = mock.patch.object(guia_inicial, "ARQUIVO_CONFIG", self.arquivo)
        self.troca.start()

    def tearDown(self):
        self.troca.stop()
        self.pasta.cleanup()

    def gravar(self, conteudo: str) -> None:
        """Escreve o config.json temporário."""
        self.arquivo.write_text(conteudo, encoding="utf-8")

    def test_primeira_execucao(self):
        """Sem config.json, o guia aparece."""
        self.assertTrue(guia_inicial.precisa_do_guia())

    def test_google_gratis_salvo(self):
        """Quem tinha o Google grátis salvo vê o guia."""
        self.gravar(json.dumps({"motor": "google_web", "credenciais_protegidas": ""}))
        self.assertTrue(guia_inicial.precisa_do_guia())

    def test_motor_valido_salvo(self):
        """Com um motor que existe salvo, o guia não aparece."""
        self.gravar(json.dumps({"motor": "offline", "credenciais_protegidas": ""}))
        self.assertFalse(guia_inicial.precisa_do_guia())

    def test_config_corrompido(self):
        """Um config.json ilegível conta como primeira execução."""
        self.gravar("{não é json")
        self.assertTrue(guia_inicial.precisa_do_guia())

    def test_texto_avisa_quem_tinha_o_google(self):
        """O aviso da saída do Google grátis só aparece para quem o tinha escolhido."""
        self.assertIn("saiu do app", guia_inicial.texto_do_guia("google_web"))
        self.assertNotIn("saiu do app", guia_inicial.texto_do_guia(None))
        self.assertIn("Azure grátis", guia_inicial.texto_do_guia(None))


if __name__ == "__main__":
    unittest.main()
