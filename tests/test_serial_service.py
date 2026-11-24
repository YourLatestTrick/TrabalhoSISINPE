
import pytest

from trabalho_g2_sisinpe.api.services.serial_service import (
    interpretar_mensagem
)


def test_interpreta_mensagem_com_falha():
    data = interpretar_mensagem(
        "DIST:4.20|WATER:1|ATTEMPTS:3|ROTATION:FAILED"
    )

    assert data["distance_cm"] == 4.2
    assert data["water_detected"] is True
    assert data["rotation_attempts"] == 3
    assert data["rotation_success"] is False

    assert data["event_code"] == "TRASH_REMOVAL_REQUIRED"


def test_aceita_protocolo_antigo():
    data = interpretar_mensagem(
        "DIST:25.00|WATER:0"
    )

    assert data["distance_cm"] == 25.0
    assert data["water_detected"] is False
    assert data["rotation_attempts"] == 0
    assert data["rotation_success"] is None


def test_interpreta_sucesso():
    data = interpretar_mensagem(
        "DIST:8.00|WATER:0|ATTEMPTS:3|ROTATION:SUCCESS"
    )

    assert data["rotation_success"] is True
    assert data["event_code"] is None


@pytest.mark.parametrize(
    "message",
    [
        "",
        "DIST:x|WATER:0",
        "DIST:5|WATER:2",
        "DIST:5|WATER:0|ATTEMPTS:4|ROTATION:FAILED",
        "DIST:5|WATER:0|ROTATION:UNKNOWN",
    ]
)
def test_rejeita_mensagem_invalida(message):
    with pytest.raises(ValueError):
        interpretar_mensagem(message)
