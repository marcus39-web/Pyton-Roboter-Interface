import os
from dataclasses import dataclass

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
except ModuleNotFoundError:
    mysql = None
    MySQLError = Exception


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(64) NOT NULL UNIQUE,
    name VARCHAR(128) NOT NULL,
    description TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS samples (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    source VARCHAR(128) NOT NULL,
    distance_cm INT NOT NULL,
    safe_distance_cm INT NOT NULL,
    raw_payload JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS predictions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sample_id BIGINT NOT NULL,
    category_id INT NOT NULL,
    decision_text VARCHAR(128) NOT NULL,
    command_text VARCHAR(128) NOT NULL,
    confidence DECIMAL(5,4) NOT NULL DEFAULT 1.0,
    model_version VARCHAR(64) NOT NULL DEFAULT 'rule-v1',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_predictions_sample FOREIGN KEY (sample_id) REFERENCES samples(id) ON DELETE CASCADE,
    CONSTRAINT fk_predictions_category FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS feedback (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    prediction_id BIGINT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    corrected_category_id INT NULL,
    note TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_feedback_prediction FOREIGN KEY (prediction_id) REFERENCES predictions(id) ON DELETE CASCADE,
    CONSTRAINT fk_feedback_category FOREIGN KEY (corrected_category_id) REFERENCES categories(id)
);
"""


@dataclass
class CategorizationDatabase:
    host: str = "127.0.0.1"
    port: int = 3306
    user: str = "root"
    password: str = ""
    database: str = "brainbot_ai"
    enabled: bool = False

    @classmethod
    def from_env(cls) -> "CategorizationDatabase":
        enabled_raw = os.getenv("APP_USE_MYSQL", "0").strip().lower()
        enabled = enabled_raw in ("1", "true", "yes", "on")

        return cls(
            host=os.getenv("MYSQL_HOST", "127.0.0.1"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=os.getenv("MYSQL_DATABASE", "brainbot_ai"),
            enabled=enabled,
        )

    def _connect(self):
        if mysql is None:
            raise RuntimeError("mysql-connector-python ist nicht installiert")

        return mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            autocommit=False,
        )

    def initialize(self) -> tuple[bool, str]:
        if not self.enabled:
            return False, "MySQL deaktiviert (APP_USE_MYSQL=0)"

        try:
            connection = self._connect()
            cursor = connection.cursor()
            for statement in [segment.strip() for segment in SCHEMA_SQL.split(";") if segment.strip()]:
                cursor.execute(statement)

            cursor.execute(
                """
                INSERT INTO categories (code, name, description)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE name = VALUES(name), description = VALUES(description)
                """,
                ("OBSTACLE", "Hindernis", "Abstand unter Sicherheitsgrenze"),
            )
            cursor.execute(
                """
                INSERT INTO categories (code, name, description)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE name = VALUES(name), description = VALUES(description)
                """,
                ("CLEAR", "Freie Strecke", "Abstand über Sicherheitsgrenze"),
            )

            connection.commit()
            cursor.close()
            connection.close()
            return True, "MySQL-Schema initialisiert"
        except (MySQLError, RuntimeError, OSError, ValueError) as error:
            return False, f"MySQL-Init fehlgeschlagen: {error}"

    def _resolve_or_create_category(self, cursor, decision: str) -> int:
        code = decision.strip().upper() or "UNKNOWN"
        cursor.execute("SELECT id FROM categories WHERE code = %s", (code,))
        row = cursor.fetchone()
        if row:
            return int(row[0])

        cursor.execute(
            "INSERT INTO categories (code, name, description) VALUES (%s, %s, %s)",
            (code, code.title(), "Automatisch angelegt durch Laufzeitdaten"),
        )
        return int(cursor.lastrowid)

    def log_decision(
        self,
        distance_cm: int,
        safe_distance_cm: int,
        decision: str,
        command: str,
        source: str = "main.py",
        room_name: str = "",
    ) -> tuple[bool, str]:
        if not self.enabled:
            return False, "MySQL deaktiviert"

        try:
            connection = self._connect()
            cursor = connection.cursor()

            category_id = self._resolve_or_create_category(cursor, decision)

            cursor.execute(
                """
                INSERT INTO samples (source, distance_cm, safe_distance_cm, raw_payload)
                VALUES (%s, %s, %s, JSON_OBJECT('decision', %s, 'command', %s, 'room_name', %s))
                """,
                (source, int(distance_cm), int(safe_distance_cm), decision, command, room_name),
            )
            sample_id = int(cursor.lastrowid)

            cursor.execute(
                """
                INSERT INTO predictions (sample_id, category_id, decision_text, command_text, confidence, model_version)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (sample_id, category_id, decision, command, 1.0, "rule-v1"),
            )

            connection.commit()
            cursor.close()
            connection.close()
            return True, "Entscheidung in MySQL gespeichert"
        except (MySQLError, RuntimeError, OSError, ValueError) as error:
            return False, f"MySQL-Log fehlgeschlagen: {error}"

    def fetch_recent_predictions(self, limit: int = 500) -> tuple[bool, list[dict], str]:
        if not self.enabled:
            return False, [], "MySQL deaktiviert"

        try:
            connection = self._connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT
                    p.created_at,
                    p.decision_text AS decision,
                    p.command_text AS command,
                    p.confidence,
                    s.distance_cm,
                    s.safe_distance_cm,
                    COALESCE(JSON_UNQUOTE(JSON_EXTRACT(s.raw_payload, '$.room_name')), '') AS room_name
                FROM predictions p
                INNER JOIN samples s ON p.sample_id = s.id
                ORDER BY p.created_at DESC
                LIMIT %s
                """,
                (int(limit),),
            )
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            return True, rows, "ok"
        except (MySQLError, RuntimeError, OSError, ValueError) as error:
            return False, [], f"MySQL-Abfrage fehlgeschlagen: {error}"
