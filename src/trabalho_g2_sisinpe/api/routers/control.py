from fastapi import APIRouter

from ..services.risk_service import (
    DISTANCIA_DETECCAO_LIXO_CM,
    MAX_TENTATIVAS_DESOBSTRUCA,
)


router = APIRouter()


@router.get("/control/status")
def obter_status_controle():
    """
    Retorna informações sobre as regras de controle.
    """

    return {
        "system": "SISINPE",
        "automatic_control": True,
        "motor_control": "ARDUINO",
        "max_rotation_attempts": (
            MAX_TENTATIVAS_DESOBSTRUCA
        ),
        "trash_detection_distance_cm": DISTANCIA_DETECCAO_LIXO_CM,
        "ultrasonic_perception_range_cm": 30.0,
        "message": (
            "O controle físico do mecanismo "
            "é realizado pelo Arduino."
        ),
    }