
"""Serviço de comunicação Serial com o Arduino."""

import os
from serial.tools import list_ports

SERIAL_PORT = os.getenv("SISINPE_SERIAL_PORT", "/dev/ttyACM0")
BAUD_RATE = int(os.getenv("SISINPE_BAUD_RATE", "9600"))

_connection_state = {
    "connected": False,
    "mode": "SIMULATION",
    "port": SERIAL_PORT,
    "message": "Monitor Serial ainda não iniciou."
}


def atualizar_estado_conexao(connected, message=None, port=None):
    global _connection_state

    _connection_state = {
        "connected": bool(connected),
        "mode": "HARDWARE" if connected else "SIMULATION",
        "port": port or SERIAL_PORT,
        "baud_rate": BAUD_RATE,
        "message": message or (
            "Arduino conectado."
            if connected
            else "Arduino desconectado."
        ),
    }

    return dict(_connection_state)


def verificar_disponibilidade():
    """Consulta o estado da conexão e as portas disponíveis."""

    available_ports = [
        item.device for item in list_ports.comports()
    ]

    state = dict(_connection_state)

    state["available_ports"] = available_ports
    state["port_detected"] = state["port"] in available_ports

    if state["connected"] and not state["port_detected"]:
        return atualizar_estado_conexao(
            False,
            "A porta serial não está mais disponível."
        ) | {
            "available_ports": available_ports,
            "port_detected": False
        }

    return state


def interpretar_mensagem(mensagem):
    """
    Interpreta o protocolo:
    DIST:x|WATER:0/1|ATTEMPTS:n|ROTATION:resultado

    Também aceita o protocolo antigo, sem os campos adicionais.
    """

    if not isinstance(mensagem, str):
        raise ValueError("A mensagem Serial deve ser texto.")

    campos = {}

    for parte in mensagem.strip().split("|"):
        if ":" not in parte:
            continue

        chave, valor = parte.split(":", 1)

        campos[chave.strip().upper()] = valor.strip()

    if "DIST" not in campos or "WATER" not in campos:
        raise ValueError(
            "Mensagem fora do protocolo: esperado DIST e WATER."
        )

    try:
        distance = float(campos["DIST"])
        water_value = int(campos["WATER"])
    except ValueError as exc:
        raise ValueError(
            "DIST ou WATER contém valor inválido."
        ) from exc

    if water_value not in (0, 1):
        raise ValueError("WATER deve ser 0 ou 1.")

    attempts_raw = campos.get("ATTEMPTS", "0")

    try:
        attempts = int(attempts_raw)
    except ValueError as exc:
        raise ValueError(
            "ATTEMPTS deve ser um número inteiro."
        ) from exc

    if not 0 <= attempts <= 3:
        raise ValueError(
            "ATTEMPTS deve estar entre 0 e 3."
        )

    rotation_raw = campos.get("ROTATION", "NONE").upper()

    rotation_map = {
        "SUCCESS": True,
        "FAILED": False,
        "NONE": None,
        "NA": None,
    }

    if rotation_raw not in rotation_map:
        raise ValueError(
            "ROTATION deve ser SUCCESS, FAILED ou NONE."
        )

    rotation_success = rotation_map[rotation_raw]

    return {
        "distance_cm": None if distance < 0 else distance,
        "water_detected": bool(water_value),
        "rotation_attempts": attempts,
        "rotation_success": rotation_success,
        "event_code": (
            "TRASH_REMOVAL_REQUIRED"
            if attempts == 3 and rotation_success is False
            else None
        ),
        "raw_message": mensagem.strip(),
        "parsed": True,
    }
