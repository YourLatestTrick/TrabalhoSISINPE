from fastapi import APIRouter
from ..services.risk_service import (
    MAX_TENTATIVAS_DESOBSTRUCA,
    DISTANCIA_DETECCAO_LIXO_CM,
    DISTANCIA_MAXIMA_PERCEPCAO_CM,
)
from ..services.serial_service import verificar_disponibilidade

router = APIRouter()


@router.get("/control/status")
def obter_status_controle():
    return {
        "system": "SISINPE",
        "automatic_control": True,
        "motor_control": "ARDUINO",
        "max_rotation_attempts": MAX_TENTATIVAS_DESOBSTRUCA,
        "trash_detection_distance_cm": DISTANCIA_DETECCAO_LIXO_CM,
        "ultrasonic_perception_range_cm": DISTANCIA_MAXIMA_PERCEPCAO_CM,
        "serial": verificar_disponibilidade(),
        "message": "O controle físico do mecanismo é realizado pelo Arduino.",
    }
