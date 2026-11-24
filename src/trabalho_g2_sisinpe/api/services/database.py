
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "sisinpe.db"


def conectar():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row

    return conn


def obter_data_atual():
    return datetime.now(timezone.utc).isoformat()


def _adicionar_coluna_se_ausente(
    conn,
    tabela,
    coluna,
    definicao
):
    colunas = {
        row[1]
        for row in conn.execute(
            f"PRAGMA table_info({tabela})"
        )
    }

    if coluna not in colunas:
        conn.execute(
            f"ALTER TABLE {tabela} ADD COLUMN {coluna} {definicao}"
        )


def inicializar_banco():
    """Cria tabelas e migra bancos existentes sem apagar medições."""

    with conectar() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                distance_cm REAL,
                water_detected INTEGER,
                humidity_percent REAL,
                risk_level TEXT NOT NULL DEFAULT 'NORMAL',
                created_at TEXT NOT NULL,
                rotation_attempts INTEGER NOT NULL DEFAULT 0,
                rotation_success INTEGER,
                event_code TEXT
            )
        """)

        # Migração não destrutiva.
        _adicionar_coluna_se_ausente(
            conn,
            "measurements",
            "rotation_attempts",
            "INTEGER NOT NULL DEFAULT 0"
        )

        _adicionar_coluna_se_ausente(
            conn,
            "measurements",
            "rotation_success",
            "INTEGER"
        )

        _adicionar_coluna_se_ausente(
            conn,
            "measurements",
            "event_code",
            "TEXT"
        )

        conn.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                created_at TEXT NOT NULL,
                updated_at TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                description TEXT NOT NULL,
                details TEXT,
                created_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_measurements_created_at
            ON measurements(created_at)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_alerts_created_at
            ON alerts(created_at)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_created_at
            ON events(created_at)
        """)

    print(f"Banco de dados inicializado: {DB_PATH}")


def salvar_medicao(
    distance_cm=None,
    water_detected=None,
    humidity_percent=None,
    risk_level="NORMAL",
    rotation_attempts=0,
    rotation_success=None,
    event_code=None
):
    with conectar() as conn:
        cursor = conn.execute("""
            INSERT INTO measurements (
                distance_cm,
                water_detected,
                humidity_percent,
                risk_level,
                created_at,
                rotation_attempts,
                rotation_success,
                event_code
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            distance_cm,
            water_detected,
            humidity_percent,
            risk_level,
            obter_data_atual(),
            rotation_attempts,
            None if rotation_success is None else int(rotation_success),
            event_code
        ))

        return cursor.lastrowid


def criar_alerta(alert_type, severity, description):
    with conectar() as conn:
        existing = conn.execute("""
            SELECT id FROM alerts
            WHERE alert_type = ?
            AND status = 'ACTIVE'
            ORDER BY id DESC LIMIT 1
        """, (alert_type,)).fetchone()

        if existing:
            return existing["id"]

        cursor = conn.execute("""
            INSERT INTO alerts (
                alert_type,
                severity,
                description,
                status,
                created_at
            )
            VALUES (?, ?, ?, 'ACTIVE', ?)
        """, (
            alert_type,
            severity,
            description,
            obter_data_atual()
        ))

        return cursor.lastrowid


def registrar_evento(event_type, description, details=None):
    details_json = (
        json.dumps(details, ensure_ascii=False)
        if details is not None
        else None
    )

    with conectar() as conn:
        cursor = conn.execute("""
            INSERT INTO events (
                event_type,
                description,
                details,
                created_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            event_type,
            description,
            details_json,
            obter_data_atual()
        ))

        return cursor.lastrowid


def _buscar_lista(tabela, limite=100):
    with conectar() as conn:
        rows = conn.execute(
            f"SELECT * FROM {tabela} ORDER BY id DESC LIMIT ?",
            (limite,)
        ).fetchall()

    resultados = [dict(row) for row in rows]

    if tabela == "events":
        for item in resultados:
            if item.get("details"):
                item["details"] = json.loads(item["details"])

    return resultados


def buscar_ultima_medicao():
    with conectar() as conn:
        row = conn.execute("""
            SELECT * FROM measurements
            ORDER BY id DESC LIMIT 1
        """).fetchone()

    if not row:
        return None

    result = dict(row)

    if result.get("rotation_success") is not None:
        result["rotation_success"] = bool(result["rotation_success"])

    if result.get("water_detected") is not None:
        result["water_detected"] = bool(result["water_detected"])

    return result


def buscar_medicoes(limite=100):
    items = _buscar_lista("measurements", limite)

    for item in items:
        if item.get("rotation_success") is not None:
            item["rotation_success"] = bool(item["rotation_success"])

        if item.get("water_detected") is not None:
            item["water_detected"] = bool(item["water_detected"])

    return items


def buscar_alertas(limite=100):
    return _buscar_lista("alerts", limite)


def buscar_eventos(limite=100):
    return _buscar_lista("events", limite)


def resolver_alerta(alerta_id):
    with conectar() as conn:
        cursor = conn.execute("""
            UPDATE alerts
            SET status = 'RESOLVED',
                updated_at = ?
            WHERE id = ?
            AND status = 'ACTIVE'
        """, (
            obter_data_atual(),
            alerta_id
        ))

        return cursor.rowcount > 0

def limpar_alertas_eventos():
    """
    Remove todos os alertas e eventos registrados.
    Preserva o histórico de medições.
    """

    with conectar() as conn:
        cursor_alertas = conn.execute(
            "DELETE FROM alerts"
        )

        cursor_eventos = conn.execute(
            "DELETE FROM events"
        )

        return {
            "alertas_removidos": cursor_alertas.rowcount,
            "eventos_removidos": cursor_eventos.rowcount,
        }