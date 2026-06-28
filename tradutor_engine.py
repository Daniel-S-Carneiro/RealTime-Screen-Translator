"""Módulo responsável pelo motor de tradução de texto."""

from deep_translator import GoogleTranslator
from deep_translator.exceptions import TranslationNotFound, NotValidPayload


class MotorTradutor:
    """Classe que gerencia o motor de tradução de idiomas usando Google Translator."""

    def __init__(self, origem: str = "en", destino: str = "pt") -> None:
        """Inicializa o tradutor com os idiomas definidos."""
        self.origem = origem
        self.destino = destino

    def traduzir_texto(self, texto: str) -> str:
        """
        Traduz o texto usando a API do Google.

        Args:
            texto (str): O texto a ser traduzido.

        Returns:
            str: O texto traduzido ou mensagem de erro em caso de falha.
        """
        if not texto.strip():
            return ""

        try:
            return GoogleTranslator(source="auto", target=self.destino).translate(texto)
        except (TranslationNotFound, NotValidPayload) as e:
            return f"Erro na tradução: {str(e)}"
        except ConnectionError:
            return "Erro: Falha na conexão com o servidor de tradução."


if __name__ == "__main__":
    # Teste rápido do tradutor isolado
    MOTOR = MotorTradutor(origem="en", destino="pt")

    TEXTO_TESTE = "Hello world! This is a real-time translator project."
    print(f"Texto original: {TEXTO_TESTE}")

    TEXTO_TRADUZIDO = MOTOR.traduzir_texto(TEXTO_TESTE)
    print(f"Texto traduzido: {TEXTO_TRADUZIDO}")
