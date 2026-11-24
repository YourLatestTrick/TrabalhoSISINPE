import sqlite3
import json

from pathlib import Path
from datetime import datetime, timezone


# Caminho do banco de dados
PROJECT_ROOT = Path(__file__).resolve().parents[4]

DATA_DIR = PROJECT_ROOT / "data"

DB_PATH = DATA_DIR / "sisinpe.db"


def conectar():
    """
    Cria uma conexão com o banco SQLite.
    """

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH, timeout=10)

    conn.row_factory = sqlite3.Row

    return conn


def obter_data_atual():
    """
    Retorna a data e hora atual em UTC.
    """

    return datetime.now(timezone.utc).isoformat()


def inicializar_banco():
    """
    Cria as tabelas do sistema caso ainda não existam.
    """

    with conectar() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                distance_cm REAL,

                water_detected INTEGER,

                humidity_percent REAL,

                risk_level TEXT NOT NULL DEFAULT 'NORMAL',

                created_at TEXT NOT NULL
            )
        """)

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

        # Índices para facilitar consultas por data
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
    risk_level="NORMAL"
):
    """
    Salva uma medição dos sensores.
    """

    data = obter_data_atual()

    with conectar() as conn:

        cursor = conn.execute("""
            INSERT INTO measurements (
                distance_cm,
                water_detected,
                humidity_percent,
                risk_level,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            distance_cm,
            water_detected,
            humidity_percent,
            risk_level,
            data
        ))

        return cursor.lastrowid


def criar_alerta(
    alert_type,
    severity,
    description
):
    """
    Cria um alerta.

    Evita duplicar alertas do mesmo tipo
    que ainda estejam ativos.
    """

    data = obter_data_atual()

    with conectar() as conn:

        cursor = conn.execute("""
            SELECT id
            FROM alerts
            WHERE alert_type = ?
              AND status = 'ACTIVE'
            ORDER BY id DESC
            LIMIT 1
        """, (alert_type,))

        alerta_existente = cursor.fetchone()

        if alerta_existente:

            return alerta_existente["id"]

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
            data,
        ))

        return cursor.lastrowid


def registrar_evento(
    event_type,
    description,
    details=None
):
    """
    Registra um evento do sistema.

    Details pode receber um dicionário com
    informações adicionais.
    """

    data = obter_data_atual()

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
            data
        ))

        return cursor.lastrowid


def buscar_ultima_medicao():
    """
    Retorna a medição mais recente.
    """

    with conectar() as conn:

        cursor = conn.execute("""
            SELECT *
            FROM measurements
            ORDER BY id DESC
            LIMIT 1
        """)

        resultado = cursor.fetchone()

        return dict(resultado) if resultado else None


def buscar_medicoes(limite=100):
    """
    Retorna as últimas medições realizadas.
    """

    with conectar() as conn:

        cursor = conn.execute("""
            SELECT *
            FROM measurements
            ORDER BY id DESC
            LIMIT ?
        """, (limite,))

        return [dict(row) for row in cursor.fetchall()]


def buscar_alertas(limite=100):
    """
    Retorna os alertas mais recentes.
    """

    with conectar() as conn:

        cursor = conn.execute("""
            SELECT *
            FROM alerts
            ORDER BY id DESC
            LIMIT ?
        """, (limite,))

        return [dict(row) for row in cursor.fetchall()]


def buscar_eventos(limite=100):
    """
    Retorna os eventos mais recentes.
    """

    with conectar() as conn:

        cursor = conn.execute("""
            SELECT *
            FROM events
            ORDER BY id DESC
            LIMIT ?
        """, (limite,))

        resultados = [dict(row) for row in cursor.fetchall()]

        for evento in resultados:

            if evento["details"]:
                evento["details"] = json.loads(evento["details"])

        return resultados

def buscar_medicoes(limite=100):
    """
    Busca as últimas medições.
    """

    with conectar() as conn:

        cursor = conn.execute("""
            SELECT *
            FROM measurements
            ORDER BY id DESC
            LIMIT ?
        """, (limite,))

        return [dict(row) for row in cursor.fetchall()]


def buscar_alertas(limite=100):
    """
    Busca os alertas mais recentes.
    """

    with conectar() as conn:

        cursor = conn.execute("""
            SELECT *
            FROM alerts
            ORDER BY id DESC
            LIMIT ?
        """, (limite,))

        return [dict(row) for row in cursor.fetchall()]


def buscar_eventos(limite=100):
    """
    Busca os eventos mais recentes.
    """

    with conectar() as conn:

        cursor = conn.execute("""
            SELECT *
            FROM events
            ORDER BY id DESC
            LIMIT ?
        """, (limite,))

        resultados = [dict(row) for row in cursor.fetchall()]

        for evento in resultados:

            if evento["details"]:
                evento["details"] = json.loads(
                    evento["details"]
                )

        return resultados


def resolver_alerta(alerta_id):
    """
    Marca um alerta como resolvido.
    """

    data = obter_data_atual()

    with conectar() as conn:

        cursor = conn.execute("""
            UPDATE alerts
            SET status = 'RESOLVED',
                updated_at = ?
            WHERE id = ?
              AND status = 'ACTIVE'
        """, (data, alerta_id))

        return cursor.rowcount > 0