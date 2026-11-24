import json
import pytest
from trabalho_g2_sisinpe.api.services.serial_service import interpretar_mensagem


def test_interpreta_json_valido():
    data = interpretar_mensagem(json.dumps({
        "distance_cm": 12.4,
        "water_detected": True,
        "humidity_percent": 55.0,
        "rotation_attempts": 3,
        "rotation_success": False,
        "event_code": "TRASH_REMOVAL_REQUIRED",
    }))
    assert data["distance_cm"] == 12.4
    assert data["water_detected"] is True
    assert data["rotation_attempts"] == 3
    assert data["rotation_success"] is False


def test_interpreta_protocolo_legado():
    data = interpretar_mensagem("DIST:14.20|WATER:1")
    assert data["distance_cm"] == 14.2
    assert data["water_detected"] is True
    assert data["rotation_attempts"] == 0


@pytest.mark.parametrize("message", ["", "texto", "{bad json}", '{"rotation_attempts":4}'])
def test_mensagem_invalida(message):
    with pytest.raises((ValueError, json.JSONDecodeError)):
        interpretar_mensagem(message)
