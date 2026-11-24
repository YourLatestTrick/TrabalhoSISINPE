"""
Serviço central de monitoramento do SISINPE.
"""

from .database import (
    salvar_medicao,
    criar_alerta,
    registrar_evento,
)

from .risk_service import classificar_risco


def processar_medicao(
    distance_cm=None,
    water_detected=False,
    humidity_percent=None,
    rotation_attempts=0,
    rotation_success=None,
    event_code=None,
):
    """
    Processa uma leitura dos sensores.

    Recebe:
        distance_cm: distância do ultrassônico.
        water_detected: presença de água.
        humidity_percent: umidade, se disponível.
        rotation_attempts: tentativas realizadas pelo Arduino.
        rotation_success: resultado da desobstrução.
        event_code: evento informado pelo hardware.

    """

    risco = classificar_risco(
        distance_cm=distance_cm,
        water_detected=water_detected,
    )

    # Salva a medição
    # Salva a medição
    measurement_id = salvar_medicao(
        distance_cm=distance_cm,
        water_detected=water_detected,
        humidity_percent=humidity_percent,
        risk_level=risco["nivel"],
        rotation_attempts=rotation_attempts,
        rotation_success=rotation_success,
        event_code=event_code,
    )

    # Evento de detecção de lixo
    if risco["lixo_detectado"] is True:

        registrar_evento(
            event_type="TRASH_DETECTED",
            description="Possível lixo detectado pelo ultrassônico.",
            details={
                "distance_cm": distance_cm,
                "measurement_id": measurement_id,
            },
        )

    # Evento de detecção de água
    if water_detected:

        registrar_evento(
            event_type="WATER_DETECTED",
            description="Sensor de umidade detectou água.",
            details={
                "measurement_id": measurement_id,
            },
        )

        criar_alerta(
            alert_type="WATER_DETECTED",
            severity="HIGH",
            description=(
                "Água detectada na galeria pluvial."
            ),
        )

    # Evento de falha na desobstrução
    if (
        rotation_attempts >= 3
        and rotation_success is False
    ):

        registrar_evento(
            event_type="TRASH_REMOVAL_REQUIRED",
            description=(
                "O mecanismo não conseguiu desobstruir "
                "a boca de lobo após três tentativas."
            ),
            details={
                "rotation_attempts": rotation_attempts,
                "distance_cm": distance_cm,
                "measurement_id": measurement_id,
                "event_code": event_code,
            },
        )

        criar_alerta(
            alert_type="TRASH_REMOVAL_REQUIRED",
            severity="CRITICAL",
            description=(
                "Lixo permanece obstruindo a boca de lobo. "
                "Remoção manual necessária."
            ),
        )

    # Falha de leitura
    if risco["nivel"] == "INDETERMINADO":

        registrar_evento(
            event_type="SENSOR_ERROR",
            description=risco["descricao"],
            details={
                "distance_cm": distance_cm,
                "measurement_id": measurement_id,
            },
        )

        criar_alerta(
            alert_type="SENSOR_ERROR",
            severity="WARNING",
            description=risco["descricao"],
        )

    # Retorno do processamento
    return {
        "measurement_id": measurement_id,
        "distance_cm": distance_cm,
        "water_detected": bool(water_detected),
        "humidity_percent": humidity_percent,
        "rotation_attempts": rotation_attempts,
        "rotation_success": rotation_success,
        "event_code": event_code,
        "risk": risco,
    }