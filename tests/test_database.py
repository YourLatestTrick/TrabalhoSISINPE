import json

from trabalho_g2_sisinpe.api.services import database


def use_temp_db(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "DATA_DIR", tmp_path)
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.db")
    database.inicializar_banco()


def test_salvar_e_buscar_medicao(monkeypatch, tmp_path):
    use_temp_db(monkeypatch, tmp_path)
    medicao_id = database.salvar_medicao(12.5, 1, 78.0, "CRITICO")
    latest = database.buscar_ultima_medicao()
    assert medicao_id == 1
    assert latest["distance_cm"] == 12.5
    assert latest["water_detected"] == 1
    assert latest["humidity_percent"] == 78.0
    assert latest["risk_level"] == "CRITICO"


def test_criar_alerta_ativo_nao_duplica(monkeypatch, tmp_path):
    use_temp_db(monkeypatch, tmp_path)
    first = database.criar_alerta("WATER_DETECTED", "HIGH", "Água detectada")
    second = database.criar_alerta("WATER_DETECTED", "HIGH", "Água detectada")
    assert first == second
    assert len(database.buscar_alertas()) == 1


def test_resolver_alerta(monkeypatch, tmp_path):
    use_temp_db(monkeypatch, tmp_path)
    alert_id = database.criar_alerta("TEST", "WARNING", "Teste")
    assert database.resolver_alerta(alert_id) is True
    assert database.resolver_alerta(alert_id) is False
    assert database.buscar_alertas()[0]["status"] == "RESOLVED"


def test_evento_guarda_details_json(monkeypatch, tmp_path):
    use_temp_db(monkeypatch, tmp_path)
    database.registrar_evento("TEST", "Evento de teste", {"sensor": "ultrassonico", "distance": 12})
    event = database.buscar_eventos()[0]
    assert event["details"] == {"sensor": "ultrassonico", "distance": 12}
