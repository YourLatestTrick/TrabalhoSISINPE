from fastapi.testclient import TestClient
from trabalho_g2_sisinpe.api import app as app_module
from trabalho_g2_sisinpe.api.services import database


def test_api_endpoints(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "DATA_DIR", tmp_path)
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "api-test.db")
    with TestClient(app_module.app) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/").json()["status"] == "online"
        assert client.get("/dashboard").status_code == 200
        response = client.post("/telemetry/simulate", json={
            "distance_cm": 12,
            "water_detected": True,
            "humidity_percent": 75,
            "rotation_attempts": 3,
            "rotation_success": False,
            "event_code": "TRASH_REMOVAL_REQUIRED",
        })
        assert response.status_code == 200
        assert client.get("/telemetry/latest").json()["data"]["risk_level"] == "CRITICO"
        assert client.get("/telemetry/history").json()["total"] == 1
        assert client.get("/alerts").json()["total"] >= 1
        assert client.get("/events").json()["total"] >= 1
        assert client.get("/control/status").status_code == 200
