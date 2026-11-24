from fastapi import APIRouter
from pydantic import BaseModel

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

    rotation_attempts: int = 0

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