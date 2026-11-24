import os
import time

import httpx
import serial

from trabalho_g2_sisinpe.api.services.serial_service import (
    BAUD_RATE,
    SERIAL_PORT,
    interpretar_mensagem,
)

API_URL = os.getenv(
    "SISINPE_API_URL",
    "http://127.0.0.1:8000"
)

SERIAL_PORT = os.getenv(
    "SISINPE_SERIAL_PORT",
    SERIAL_PORT
)

import threading

parar_monitor = threading.Event()
_thread_monitor = None


def flood_alert(water):
    return {
        "event": "flood_alert",
        "water": water,
    }


def trash_alert(distance):
    return {
        "event": "trash_needs_pickup",
        "distance_cm": distance,
    }


def enviar_estado_conexao(client, connected, message):
    try:
        client.post(
            f"{API_URL}/serial/status",
            json={
                "connected": connected,
                "message": message,
                "port": SERIAL_PORT,
            },
            timeout=3.0,
        )

    except httpx.HTTPError as exc:
        print(
            f"Não foi possível atualizar o status Serial na API: {exc}"
        )


def monitor_system():
    print(
        f"Conectando ao Arduino em {SERIAL_PORT} "
        f"({BAUD_RATE} baud)"
    )

    flood_alerted = False
    trash_alerted = False

    with httpx.Client() as client:
        connection = None

        try:
            connection = serial.Serial(
                SERIAL_PORT,
                BAUD_RATE,
                timeout=1
            )

            time.sleep(2)

            enviar_estado_conexao(
                client,
                True,
                "Arduino conectado e monitorando."
            )

            print("Arduino conectado. Monitoramento iniciado.")

            while not parar_monitor.is_set():
                raw = connection.readline()

                if not raw:
                    continue

                line = raw.decode(
                    "utf-8",
                    errors="ignore"
                ).strip()

                if not line:
                    continue

                print(line)

                try:
                    dados = interpretar_mensagem(line)

                except ValueError:
                    # Ignora mensagens que não pertencem ao protocolo.
                    continue

                try:
                    response = client.post(
                        f"{API_URL}/telemetry/serial",
                        json={"message": line},
                        timeout=3.0,
                    )

                    response.raise_for_status()

                    print(
                        "API:",
                        response.json().get("status", "received")
                    )

                except httpx.HTTPError as exc:
                    print(
                        f"Falha ao enviar telemetria para a API: {exc}"
                    )

                water = dados["water_detected"]
                distance = dados["distance_cm"]

                # Alerta de água.
                if water and not flood_alerted:
                    flood_alerted = True
                    print(flood_alert(water))

                elif not water:
                    flood_alerted = False

                # Alerta de lixo.
                if (
                    distance is not None
                    and 0 < distance <= 5.0
                    and not trash_alerted
                ):
                    trash_alerted = True
                    print(trash_alert(distance))

                elif distance is None or distance > 5.0:
                    trash_alerted = False

        except serial.SerialException as exc:
            enviar_estado_conexao(
                client,
                False,
                f"Falha na porta serial: {exc}"
            )

            print(f"Falha na porta serial: {exc}")

        except KeyboardInterrupt:
            print("Monitoramento interrompido.")

        finally:
            if connection is not None and connection.is_open:
                connection.close()

            enviar_estado_conexao(
                client,
                False,
                "Monitoramento Serial encerrado."
            )

def iniciar_monitor():
    global _thread_monitor
    if _thread_monitor is not None and _thread_monitor.is_alive():
        return _thread_monitor

    parar_monitor.clear()
    _thread_monitor = threading.Thread(
        target=monitor_system,
        name="sisinpe-monitor",
        daemon=True,
    )
    _thread_monitor.start()
    return _thread_monitor


def parar_monitor():
    parar_monitor.set()


if __name__ == "__main__":
    monitor_system()
