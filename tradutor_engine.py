"""Módulo responsável pelo motor de tradução de texto."""

import time
from typing import Optional

from motores_traducao import MOTORES, ErroMotor, traduzir_com

# Se o motor escolhido falhar, tenta estes, nesta ordem
RESERVAS = ("google_web", "offline")


class MotorTradutor:
    """Traduz com o motor escolhido nas configurações e usa as reservas se ele falhar."""

    def __init__(
        self,
        origem: str = "en",
        destino: str = "pt",
        motor: str = "google_web",
        credenciais: Optional[dict] = None,
    ) -> None:
        """Inicializa o tradutor com os idiomas e o motor definidos."""
        self.origem = origem
        self.destino = destino
        self.motor = "google_web"
        self.credenciais: dict = {}
        # Motor -> até quando (time.monotonic) ele fica de fora depois de bloqueio ou cota
        self._pausado_ate: dict = {}
        self.configurar(motor, credenciais or {})

    def configurar(self, motor: str, credenciais: dict) -> None:
        """Troca o motor e as chaves (chamado ao salvar as configurações)."""
        self.motor = motor if motor in MOTORES else "google_web"
        self.credenciais = credenciais
        # Chave nova merece uma nova chance
        self._pausado_ate.clear()

    def traduzir_texto(self, texto: str) -> str:
        """
        Traduz o texto com o motor escolhido; se ele falhar, com as reservas.

        Args:
            texto (str): O texto a ser traduzido.

        Returns:
            str: O texto traduzido ou mensagem de erro em caso de falha.
        """
        if not texto.strip():
            return ""

        motivos = []
        for motor in [self.motor] + [m for m in RESERVAS if m != self.motor]:
            nome = MOTORES[motor].nome_curto
            if time.monotonic() < self._pausado_ate.get(motor, 0.0):
                motivos.append(f"{nome}: em pausa depois de um bloqueio")
                continue
            try:
                traducao = traduzir_com(motor, texto, self.origem, self.destino, self.credenciais)
            except ErroMotor as erro:
                if erro.pausar_segundos:
                    self._pausado_ate[motor] = time.monotonic() + erro.pausar_segundos
                print(f"Tradutor {nome} falhou: {erro}")
                motivos.append(f"{nome}: {erro}")
                continue
            # Marca quando a tradução veio de uma reserva: a qualidade pode ser outra
            return traducao if motor == self.motor else f"[{nome}] {traducao}"

        return "Erro: nenhum tradutor funcionou (" + "; ".join(motivos) + ")."


if __name__ == "__main__":
    # Teste rápido do tradutor isolado
    MOTOR = MotorTradutor(origem="en", destino="pt")

    TEXTO_TESTE = "Hello world! This is a real-time translator project."
    print(f"Texto original: {TEXTO_TESTE}")

    TEXTO_TRADUZIDO = MOTOR.traduzir_texto(TEXTO_TESTE)
    print(f"Texto traduzido: {TEXTO_TRADUZIDO}")
