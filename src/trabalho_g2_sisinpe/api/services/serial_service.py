"""
Serviço de comunicação Serial com o Arduino.

A integração física será implementada após a definição
e validação do protocolo de comunicação do firmware.
"""


def verificar_disponibilidade():
    """
    Retorna o estado da comunicação Serial.
    """

    return {
        "connected": False,
        "mode": "SIMULATION",
        "message": (
            "Comunicação Serial ainda não integrada."
        ),
    }


def interpretar_mensagem(mensagem):
    """
    Preparação para interpretar mensagens do Arduino.

    O protocolo definitivo será implementado
    após verificarmos o firmware.
    """

    return {
        "raw_message": mensagem,
        "parsed": False,
    }