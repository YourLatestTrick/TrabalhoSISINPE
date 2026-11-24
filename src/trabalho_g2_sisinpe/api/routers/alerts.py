from fastapi import APIRouter, HTTPException

from ..services.database import (
    buscar_alertas,
    buscar_eventos,
    resolver_alerta,
)


router = APIRouter()


@router.get("/alerts")
def listar_alertas(limit: int = 100):
    """
    Retorna os alertas registrados.
    """

    limit = max(1, min(limit, 1000))

    alertas = buscar_alertas(limit)

    return {
        "total": len(alertas),
        "data": alertas,
    }


@router.patch("/alerts/{alert_id}/resolve")
def resolver(alert_id: int):
    """
    Resolve um alerta.
    """

    resultado = resolver_alerta(alert_id)

    if not resultado:

        raise HTTPException(
            status_code=404,
            detail="Alerta não encontrado.",
        )

    return {
        "status": "resolved",
        "alert_id": alert_id,
        "message": "Alerta resolvido.",
    }


@router.get("/events")
def listar_eventos(limit: int = 100):
    """
    Retorna os eventos do sistema.
    """

    limit = max(1, min(limit, 1000))

    eventos = buscar_eventos(limit)

    return {
        "total": len(eventos),
        "data": eventos,
    }