
import pytest

from fastapi.testclient import TestClient

from trabalho_g2_sisinpe.api.app import app
from trabalho_g2_sisinpe.api.services import database


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATA_DIR", tmp_path)

    monkeypatch.setattr(
        database,
        "DB_PATH",
        tmp_path / "test_sisinpe.db"
    )

    with TestClient(app) as test_client:
        yield test_client


def test_health_and_serial_status(client):
    assert client.get("/health").status_code == 200

    response = client.get("/serial/status")

    assert response.status_code == 200
    assert "connected" in response.json()


def test_recebe_mensagem_serial(client):
    response = client.post(
        "/telemetry/serial",
        json={
            "message": (
                "DIST:4.00|WATER:0|"
                "ATTEMPTS:3|ROTATION:FAILED"
            )
        }
    )

    assert response.status_code == 200

    data = response.json()["data"]

    assert data["rotation_attempts"] == 3
    assert data["rotation_success"] is False

    assert data["event_code"] == "TRASH_REMOVAL_REQUIRED"

    latest = client.get(
        "/telemetry/latest"
    ).json()["data"]

    assert latest["rotation_attempts"] == 3
    assert latest["rotation_success"] is False

    assert latest["event_code"] == "TRASH_REMOVAL_REQUIRED"

    alerts = client.get("/alerts").json()["data"]

    assert any(
        item["alert_type"] == "TRASH_REMOVAL_REQUIRED"
        for item in alerts
    )


def test_rejeita_mensagem_serial_invalida(client):
    response = client.post(
        "/telemetry/serial",
        json={
            "message": "mensagem invalida"
        }
    )

    assert response.status_code == 422
