"""Comunicação serial com Arduino e interpretação do protocolo JSON do SISINPE."""
from __future__ import annotations

import json
import os
import threading
import time
from typing import Any

from .monitoring_service import processar_medicao

DEFAULT_BAUD_RATE = 9600

_status: dict[str, Any] = {
    "connected": False,
    "mode": "SIMULATION",
    "port": None,
    "last_message": None,
    "last_error": None,
    "last_received_at": None,
}
_status_lock = threading.Lock()
_stop_event = threading.Event()
_worker: threading.Thread | None = None


def interpretar_mensagem(mensagem: str) -> dict[str, Any]:
    """Interpreta uma linha JSON do Arduino. Também aceita protocolo legado DIST/WATER."""
    line = mensagem.strip()
    if not line:
        raise ValueError("Mensagem serial vazia.")
    if line.startswith("{"):
        data = json.loads(line)
        if not isinstance(data, dict):
            raise ValueError("A mensagem JSON precisa ser um objeto.")
        distance = data.get("distance_cm")
        water = data.get("water_detected", False)
        humidity = data.get("humidity_percent")
        attempts = data.get("rotation_attempts", 0)
        success = data.get("rotation_success")
        event_code = data.get("event_code")
    elif line.startswith("DIST:") and "|WATER:" in line:
        distance_part, water_part = line.split("|", 1)
        raw_distance = distance_part.removeprefix("DIST:").strip()
        distance = float(raw_distance)
        water = water_part.removeprefix("WATER:").strip() == "1"
        humidity, attempts, success, event_code = None, 0, None, None
    else:
        raise ValueError("Formato serial desconhecido.")

    if distance is not None:
        distance = float(distance)
    if humidity is not None:
        humidity = float(humidity)
    attempts = int(attempts)
    if attempts < 0 or attempts > 3:
        raise ValueError("rotation_attempts deve estar entre 0 e 3.")
    if success is not None and not isinstance(success, bool):
        raise ValueError("rotation_success deve ser booleano ou null.")
    if not isinstance(water, bool):
        raise ValueError("water_detected deve ser booleano.")
    return {
        "distance_cm": distance,
        "water_detected": water,
        "humidity_percent": humidity,
        "rotation_attempts": attempts,
        "rotation_success": success,
        "event_code": event_code,
    }


def processar_mensagem_serial(mensagem: str) -> dict[str, Any]:
    dados = interpretar_mensagem(mensagem)
    return processar_medicao(**dados)


def verificar_disponibilidade() -> dict[str, Any]:
    with _status_lock:
        return dict(_status)


def _serial_worker(port: str, baud_rate: int) -> None:
    try:
        import serial  # pyserial é necessário somente no modo hardware
        with serial.Serial(port, baud_rate, timeout=1) as connection:
            time.sleep(2)  # aguarda reset do Arduino após abrir a serial
            with _status_lock:
                _status.update(connected=True, mode="HARDWARE", port=port, last_error=None)
            while not _stop_event.is_set():
                raw = connection.readline()
                if not raw:
                    continue
                message = raw.decode("utf-8", errors="replace").strip()
                if not message:
                    continue
                try:
                    result = processar_mensagem_serial(message)
                    with _status_lock:
                        _status.update(last_message=message, last_received_at=time.time(), last_error=None)
                    print(f"[SERIAL] Medição processada: {result}")
                except (ValueError, json.JSONDecodeError) as exc:
                    with _status_lock:
                        _status.update(last_message=message, last_error=f"Mensagem inválida: {exc}")
                    print(f"[SERIAL] {exc}: {message}")
    except (ImportError, OSError, Exception) as exc:
        with _status_lock:
            _status.update(connected=False, mode="ERROR", port=port, last_error=str(exc))
        print(f"[SERIAL] Não foi possível conectar em {port}: {exc}")
    finally:
        with _status_lock:
            _status.update(connected=False)


def iniciar_monitor_serial(port: str | None = None, baud_rate: int = DEFAULT_BAUD_RATE) -> bool:
    """Inicia leitor serial em thread quando SISINPE_SERIAL_PORT está configurada."""
    global _worker
    port = port or os.getenv("SISINPE_SERIAL_PORT")
    if not port:
        with _status_lock:
            _status.update(connected=False, mode="SIMULATION", port=None, last_error=None)
        print("[SERIAL] Porta não configurada. API em modo de simulação.")
        return False
    if _worker and _worker.is_alive():
        return True
    _stop_event.clear()
    _worker = threading.Thread(target=_serial_worker, args=(port, baud_rate), daemon=True)
    _worker.start()
    return True


def parar_monitor_serial() -> None:
    _stop_event.set()
    if _worker and _worker.is_alive():
        _worker.join(timeout=2)
    with _status_lock:
        _status.update(connected=False)
