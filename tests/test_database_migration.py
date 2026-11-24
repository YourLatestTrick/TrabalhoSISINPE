
import sqlite3

from trabalho_g2_sisinpe.api.services import database


def test_migracao_adiciona_colunas_sem_apagar_medicoes(
    tmp_path,
    monkeypatch
):
    db_path = tmp_path / "legacy.db"

    monkeypatch.setattr(
        database,
        "DATA_DIR",
        tmp_path
    )

    monkeypatch.setattr(
        database,
        "DB_PATH",
        db_path
    )

    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                distance_cm REAL,
                water_detected INTEGER,
                humidity_percent REAL,
                risk_level TEXT NOT NULL DEFAULT 'NORMAL',
                created_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            INSERT INTO measurements (
                distance_cm,
                water_detected,
                risk_level,
                created_at
            )
            VALUES (
                4.0,
                0,
                'OBSTRUCAO',
                '2026-11-24T00:00:00+00:00'
            )
        """)

    database.inicializar_banco()

    latest = database.buscar_ultima_medicao()

    assert latest["id"] == 1
    assert latest["distance_cm"] == 4.0

    assert latest["rotation_attempts"] == 0
    assert latest["rotation_success"] is None

    assert "event_code" in latest
