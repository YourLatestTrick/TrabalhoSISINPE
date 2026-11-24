from trabalho_g2_sisinpe.api.services import database
from trabalho_g2_sisinpe.api.services.monitoring_service import processar_medicao


def use_temp_db(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "DATA_DIR", tmp_path)
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.db")
    database.inicializar_banco()


def test_medicao_normal_persiste(monkeypatch, tmp_path):
    use_temp_db(monkeypatch, tmp_path)
    result = processar_medicao(25, False, 20.0)
    assert result["risk"]["nivel"] == "NORMAL"
    assert database.buscar_ultima_medicao()["risk_level"] == "NORMAL"


def test_agua_cria_alerta_e_evento(monkeypatch, tmp_path):
    use_temp_db(monkeypatch, tmp_path)
    processar_medicao(25, True, 80.0)
    assert database.buscar_alertas()[0]["alert_type"] == "WATER_DETECTED"
    assert database.buscar_eventos()[0]["event_type"] == "WATER_DETECTED"


def test_falha_de_desobstrucao_cria_alerta_critico(monkeypatch, tmp_path):
    use_temp_db(monkeypatch, tmp_path)
    processar_medicao(12, False, None, 3, False, "TRASH_REMOVAL_REQUIRED")
    alert = database.buscar_alertas()[0]
    assert alert["alert_type"] == "TRASH_REMOVAL_REQUIRED"
    assert alert["severity"] == "CRITICAL"
