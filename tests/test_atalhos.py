"""Os atalhos globais e as preferências (27/11/2026).

Nenhum teste registra um atalho no Windows: o user32 é trocado por um falso, que guarda as
chamadas. As preferências vão para um arquivo temporário, nunca para o do usuário.
"""

import ctypes
import json
import tempfile
import unittest
from ctypes import wintypes
from pathlib import Path
from unittest import mock

import atalhos as A
import preferencias as P


class TestInterpretar(unittest.TestCase):
    """Do texto do QKeySequence para o que o RegisterHotKey recebe."""

    def test_padrao(self):
        """Os três atalhos padrão são válidos e diferentes."""
        self.assertEqual(A.interpretar("Ctrl+Alt+T"), (A.MOD_CONTROL | A.MOD_ALT, ord("T")))
        self.assertEqual(A.problemas(A.PADRAO), {})

    def test_teclas_de_funcao_sozinhas(self):
        """Uma tecla de função não precisa de modificador."""
        self.assertEqual(A.interpretar("F9"), (0, 0x78))
        self.assertEqual(A.interpretar("Shift+F1"), (A.MOD_SHIFT, 0x70))

    def test_teclas_com_nome(self):
        """Os nomes do texto portável do Qt viram o código certo."""
        self.assertEqual(A.interpretar("Ctrl+Alt+Ins"), (A.MOD_CONTROL | A.MOD_ALT, 0x2D))
        self.assertEqual(A.interpretar("Meta+PgDown"), (A.MOD_WIN, 0x22))
        self.assertEqual(A.interpretar("Pause"), (0, 0x13))

    def test_letra_sozinha_nao(self):
        """Uma letra ou um número sozinho, ou só com Shift, atrapalharia a digitação."""
        for texto in ("T", "Shift+T", "5", "Space", "Up"):
            with self.subTest(texto=texto), self.assertRaises(A.AtalhoInvalido):
                A.interpretar(texto)

    def test_f12_sozinho_nao(self):
        """O Windows reserva o F12 sozinho; com modificador, pode."""
        with self.assertRaises(A.AtalhoInvalido):
            A.interpretar("F12")
        self.assertEqual(A.interpretar("Ctrl+F12"), (A.MOD_CONTROL, 0x7B))

    def test_textos_invalidos(self):
        """Modificador desconhecido, tecla sem código ou texto quebrado."""
        for texto in ("Hyper+T", "Ctrl+Alt+Ç", "Ctrl+²", "Ctrl+", "", "Ctrl++"):
            with self.subTest(texto=texto), self.assertRaises(A.AtalhoInvalido):
                A.interpretar(texto)


class TestProblemas(unittest.TestCase):
    """O que a tela de configurações recusa antes de salvar."""

    def test_vazio_e_sem_atalho(self):
        """Um campo vazio quer dizer sem atalho, e não é problema."""
        self.assertEqual(A.problemas({"traduzir": "", "mostrar": "Ctrl+Alt+H"}), {})

    def test_repetido(self):
        """A mesma combinação em duas ações, mesmo escrita em outra ordem."""
        encontrados = A.problemas({"traduzir": "Ctrl+Alt+T", "limpar": "Alt+Ctrl+T"})
        self.assertEqual(list(encontrados), ["limpar"])
        self.assertIn("Traduzir a área", encontrados["limpar"])

    def test_invalido(self):
        """O motivo vem junto."""
        self.assertIn("digitação", A.problemas({"traduzir": "T"})["traduzir"])


class User32Falso:
    """Guarda as chamadas e recusa as combinações da lista ocupadas."""

    def __init__(self, ocupadas=()):
        self.ocupadas = set(ocupadas)
        self.registrados = {}
        self.cancelados = []

    def RegisterHotKey(self, hwnd, numero, modificadores, codigo):  # pylint: disable=invalid-name
        """Como o do Windows: 0 quando outro programa já tem a combinação."""
        if (modificadores & ~A.MOD_NOREPEAT, codigo) in self.ocupadas:
            ctypes.set_last_error(A.ERRO_JA_REGISTRADO)
            return 0
        self.registrados[numero] = (hwnd, modificadores, codigo)
        return 1

    def UnregisterHotKey(self, hwnd, numero):  # pylint: disable=invalid-name
        """Registra o cancelamento."""
        self.cancelados.append((hwnd, numero))
        return 1


class TestRegistro(unittest.TestCase):
    """O registro dos atalhos na janela e a leitura das mensagens."""

    def setUp(self):
        self.user32 = User32Falso(ocupadas={(A.MOD_CONTROL | A.MOD_ALT, ord("H"))})
        self.troca = mock.patch.object(A, "_user32", return_value=self.user32)
        self.troca.start()
        self.plataforma = mock.patch.object(A.sys, "platform", "win32")
        self.plataforma.start()

    def tearDown(self):
        self.troca.stop()
        self.plataforma.stop()

    def test_registra_sem_repetir_e_avisa_o_ocupado(self):
        """Cada atalho vai com o MOD_NOREPEAT; o ocupado volta como falha."""
        registro = A.RegistroDeAtalhos()
        falhas = registro.registrar(1234, A.PADRAO)
        self.assertEqual(list(falhas), ["mostrar"])
        self.assertIn("outro programa", falhas["mostrar"])
        self.assertEqual(registro.ids, {1: "traduzir", 3: "limpar"})
        for _, modificadores, _ in self.user32.registrados.values():
            self.assertTrue(modificadores & A.MOD_NOREPEAT)

    def test_sem_atalho_nao_registra(self):
        """O campo vazio não chega ao Windows."""
        registro = A.RegistroDeAtalhos()
        self.assertEqual(registro.registrar(1, {"traduzir": "", "limpar": "F8"}), {})
        self.assertEqual(registro.ids, {2: "limpar"})

    def test_registrar_de_novo_cancela_os_anteriores(self):
        """Ao voltar das configurações, os atalhos antigos saem antes dos novos."""
        registro = A.RegistroDeAtalhos()
        registro.registrar(1234, {"traduzir": "F8"})
        registro.registrar(1234, {"traduzir": "F9"})
        self.assertEqual(self.user32.cancelados, [(1234, 1)])
        registro.cancelar()
        self.assertEqual(registro.ids, {})

    def test_mensagem_do_atalho(self):
        """O WM_HOTKEY com o id registrado vira a ação; as outras mensagens, não."""
        registro = A.RegistroDeAtalhos()
        registro.registrar(1234, A.PADRAO)
        mensagem = wintypes.MSG()
        mensagem.message = A.WM_HOTKEY
        mensagem.wParam = 3
        endereco = ctypes.addressof(mensagem)
        self.assertEqual(registro.acao_da_mensagem(b"windows_generic_MSG", endereco), "limpar")
        mensagem.wParam = 2  # o "mostrar", que não registrou
        self.assertIsNone(registro.acao_da_mensagem(b"windows_generic_MSG", endereco))
        mensagem.message = 0x0100  # WM_KEYDOWN
        self.assertIsNone(registro.acao_da_mensagem(b"windows_generic_MSG", endereco))
        self.assertIsNone(registro.acao_da_mensagem(b"windows_dispatcher_MSG", endereco))


class TestPreferencias(unittest.TestCase):
    """O preferencias.json: o padrão completa o que falta ou está errado."""

    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        self.arquivo = Path(self.pasta.name) / "preferencias.json"
        self.troca = mock.patch.object(P, "ARQUIVO_PREFERENCIAS", self.arquivo)
        self.troca.start()

    def tearDown(self):
        self.troca.stop()
        self.pasta.cleanup()

    def test_sem_arquivo(self):
        """Na primeira execução, valem os padrões, com a janela fora da captura."""
        self.assertEqual(P.carregar(), P.PADRAO)
        self.assertTrue(P.carregar()["fora_da_captura"])

    def test_ida_e_volta(self):
        """O que é salvo volta igual, inclusive um atalho tirado."""
        prefs = P.carregar()
        prefs["atalhos"]["limpar"] = ""
        prefs["fora_da_captura"] = False
        P.salvar(prefs)
        self.assertEqual(P.carregar(), prefs)

    def test_arquivo_ilegivel(self):
        """Um arquivo quebrado dá o padrão, sem erro."""
        self.arquivo.write_text("{não é json", encoding="utf-8")
        self.assertEqual(P.carregar(), P.PADRAO)

    def test_parcial_e_tipos_errados(self):
        """A ação que falta (de uma versão anterior) recebe o padrão; o tipo errado é ignorado."""
        self.arquivo.write_text(json.dumps({
            "atalhos": {"traduzir": "F8", "mostrar": 5},
            "fora_da_captura": "sim",
            "outra": 1,
        }), encoding="utf-8")
        prefs = P.carregar()
        self.assertEqual(prefs["atalhos"], {**A.PADRAO, "traduzir": "F8"})
        self.assertTrue(prefs["fora_da_captura"])
        self.assertNotIn("outra", prefs)

    def test_padrao_nao_muda(self):
        """Mexer no que o carregar devolve não altera o padrão."""
        P.carregar()["atalhos"]["traduzir"] = "F1"
        self.assertEqual(P.PADRAO["atalhos"]["traduzir"], "Ctrl+Alt+T")


if __name__ == "__main__":
    unittest.main()
