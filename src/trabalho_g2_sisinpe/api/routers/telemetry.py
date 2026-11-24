from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..services.database import (
    buscar_ultima_medicao,
    buscar_medicoes,
)

from ..services.monitoring_service import processar_medicao


router = APIRouter()


class MedicaoRequest(BaseModel):
    distance_cm: float | None = None

    water_detected: bool = False

    humidity_percent: float | None = None

    rotation_attempts: int = Field(default=0, ge=0, le=3)

    rotation_success: bool | None = None

    event_code: str | None = None


@router.get("/telemetry/latest")
def obter_ultima_medicao():
    """
    Retorna a última medição registrada.
    """

    medicao = buscar_ultima_medicao()

    return {
        "data": medicao,
    }


@router.get("/telemetry/history")
def obter_historico(limit: int = 100):
    """
    Retorna o histórico de medições.

    O limite máximo é 1000 registros.
    """

    limit = max(1, min(limit, 1000))

    medicoes = buscar_medicoes(limit)

    return {
        "total": len(medicoes),
        "data": medicoes,
    }


@router.post("/telemetry/simulate")
def simular_medicao(medicao: MedicaoRequest):
    """
    Recebe uma medição simulada.

    Endpoint destinado aos testes do backend
    enquanto a comunicação com o Arduino
    ainda não está implementada.
    """

    resultado = processar_medicao(
        distance_cm=medicao.distance_cm,
        water_detected=medicao.water_detected,
        humidity_percent=medicao.humidity_percent,
        rotation_attempts=medicao.rotation_attempts,
        rotation_success=medicao.rotation_success,
        event_code=medicao.event_code,
    )

    return {
        "status": "processed",
        "message": "Medição processada com sucesso.",
        "data": resultado,
    }

@router.post("/telemetry/serial")
def receber_serial(payload: dict):
    """Recebe uma linha bruta do protocolo Serial enviada pelo monitor.py."""

    from ..services.serial_service import interpretar_mensagem

    mensagem = payload.get("message", "")

    try:
        dados = interpretar_mensagem(mensagem)

    except ValueError as exc:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=422,
            detail=str(exc)
        ) from exc

    resultado = processar_medicao(
        distance_cm=dados["distance_cm"],
        water_detected=dados["water_detected"],
        rotation_attempts=dados["rotation_attempts"],
        rotation_success=dados["rotation_success"],
        event_code=dados["event_code"],
    )

    return {
        "status": "processed",
        "data": resultado,
    }