"""Módulo responsável pelo motor de tradução de texto."""

import time
from typing import Optional

import uso_motores
from motores_traducao import (
    MOTORES,
    PAGOS,
    SEM_CHAVE,
    ErroMotor,
    motor_valido,
    tem_chave,
    traduzir_com,
)


class MotorTradutor:
    """Traduz com o motor escolhido nas configurações e usa as reservas se ele falhar.

    As reservas são os outros motores pagos que têm chave (cada um dentro da trava de custo)
    e, por último, o offline. Até 27/11/2026, a primeira reserva era o Google Tradutor
    grátis, que saiu do app.
    """

    def __init__(
        self,
        origem: str = "en",
        destino: str = "pt",
        motor: str = SEM_CHAVE,
        credenciais: Optional[dict] = None,
    ) -> None:
        """Inicializa o tradutor com os idiomas e o motor definidos."""
        self.origem = origem
        self.destino = destino
        self.motor = SEM_CHAVE
        self.credenciais: dict = {}
        # Motor -> até quando (time.monotonic) ele fica de fora depois de bloqueio ou cota
        self._pausado_ate: dict = {}
        self.configurar(motor, credenciais or {})

    def configurar(self, motor: str, credenciais: dict) -> None:
        """Troca o motor e as chaves (chamado ao salvar as configurações)."""
        self.motor = motor_valido(motor, credenciais)
        self.credenciais = credenciais
        # Chave nova merece uma nova chance
        self._pausado_ate.clear()

    def ordem(self) -> list:
        """O motor escolhido, os outros pagos com chave e o offline, nesta ordem.

        Quem escolheu o offline fica só com ele: o texto não sai do PC.
        """
        if self.motor == SEM_CHAVE:
            return [SEM_CHAVE]
        reservas = [m for m in PAGOS if m != self.motor and tem_chave(m, self.credenciais)]
        return [self.motor] + reservas + [SEM_CHAVE]

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
        for motor in self.ordem():
            nome = MOTORES[motor].nome_curto
            if time.monotonic() < self._pausado_ate.get(motor, 0.0):
                motivos.append(f"{nome}: em pausa depois de um bloqueio")
                continue
            if self._passaria_do_limite(motor, texto):
                motivos.append(f"{nome}: limite grátis do mês atingido (trava de custo)")
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

    @staticmethod
    def _passaria_do_limite(motor: str, texto: str) -> bool:
        """True se a trava está ligada e este texto faria o motor passar do limite grátis."""
        info = MOTORES[motor]
        if not info.trava_de_custo or not uso_motores.trava_ligada():
            return False
        return uso_motores.usado_no_mes(motor) + len(texto) > info.limite_gratis


if __name__ == "__main__":
    # Teste rápido do tradutor isolado
    MOTOR = MotorTradutor(origem="en", destino="pt")

    TEXTO_TESTE = "Hello world! This is a real-time translator project."
    print(f"Texto original: {TEXTO_TESTE}")

    TEXTO_TRADUZIDO = MOTOR.traduzir_texto(TEXTO_TESTE)
    print(f"Texto traduzido: {TEXTO_TRADUZIDO}")
