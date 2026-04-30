import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "tasks.db"



def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn



def _ensure_column(conn: sqlite3.Connection, table: str, column: str, ddl: str) -> None:
    columns = [row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")



def init_db() -> None:
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                category TEXT DEFAULT 'praca'
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                module_id INTEGER,
                status TEXT DEFAULT 'oczekujace',
                priority TEXT DEFAULT '',
                description TEXT DEFAULT '',
                due_date TEXT DEFAULT '',
                estimated_time INTEGER DEFAULT 0,
                FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                key TEXT PRIMARY KEY,
                content TEXT DEFAULT '',
                updated_at TEXT DEFAULT ''
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS monthly_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL DEFAULT ''
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS monthly_task_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                monthly_task_id INTEGER NOT NULL,
                month_key TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0,
                note TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL DEFAULT '',
                UNIQUE(monthly_task_id, month_key),
                FOREIGN KEY (monthly_task_id) REFERENCES monthly_tasks(id) ON DELETE CASCADE
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS debts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                place TEXT NOT NULL DEFAULT '',
                kind TEXT NOT NULL DEFAULT 'debt',
                total_amount REAL NOT NULL DEFAULT 0,
                monthly_amount REAL NOT NULL DEFAULT 0,
                due_day INTEGER NOT NULL DEFAULT 0,
                note TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL DEFAULT ''
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS debt_payment_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                debt_id INTEGER NOT NULL,
                month_key TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL DEFAULT '',
                UNIQUE(debt_id, month_key),
                FOREIGN KEY (debt_id) REFERENCES debts(id) ON DELETE CASCADE
            )
            """
        )

        _ensure_column(conn, "modules", "category", "TEXT DEFAULT 'praca'")
        _ensure_column(conn, "tasks", "priority", "TEXT DEFAULT ''")
        _ensure_column(conn, "tasks", "description", "TEXT DEFAULT ''")
        _ensure_column(conn, "tasks", "due_date", "TEXT DEFAULT ''")
        _ensure_column(conn, "tasks", "estimated_time", "INTEGER DEFAULT 0")
        _ensure_column(conn, "monthly_tasks", "due_day", "INTEGER DEFAULT 0")
        _ensure_column(conn, "monthly_tasks", "created_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "monthly_tasks", "updated_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "monthly_task_states", "note", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "monthly_task_states", "updated_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "debts", "place", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "debts", "kind", "TEXT NOT NULL DEFAULT 'debt'")
        _ensure_column(conn, "debts", "total_amount", "REAL NOT NULL DEFAULT 0")
        _ensure_column(conn, "debts", "monthly_amount", "REAL NOT NULL DEFAULT 0")
        _ensure_column(conn, "debts", "due_day", "INTEGER NOT NULL DEFAULT 0")
        _ensure_column(conn, "debts", "note", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "debts", "created_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "debts", "updated_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "debt_payment_states", "done", "INTEGER NOT NULL DEFAULT 0")
        _ensure_column(conn, "debt_payment_states", "updated_at", "TEXT NOT NULL DEFAULT ''")

        conn.execute("UPDATE modules SET category = 'praca' WHERE category IS NULL OR TRIM(category) = ''")
        conn.execute("UPDATE tasks SET priority = '' WHERE priority IS NULL")
        conn.execute("UPDATE tasks SET description = '' WHERE description IS NULL")
        conn.execute("UPDATE tasks SET due_date = '' WHERE due_date IS NULL")
        conn.execute("UPDATE tasks SET estimated_time = 0 WHERE estimated_time IS NULL")
        conn.execute("UPDATE tasks SET status = 'przygotowanie' WHERE status IN ('analiza', 'wstepne')")
        conn.execute("UPDATE monthly_tasks SET due_day = 0 WHERE due_day IS NULL")
        conn.execute("UPDATE monthly_tasks SET created_at = '' WHERE created_at IS NULL")
        conn.execute("UPDATE monthly_tasks SET updated_at = '' WHERE updated_at IS NULL")
        conn.execute("UPDATE monthly_task_states SET note = '' WHERE note IS NULL")
        conn.execute("UPDATE monthly_task_states SET updated_at = '' WHERE updated_at IS NULL")
        conn.execute("UPDATE debts SET place = '' WHERE place IS NULL")
        conn.execute("UPDATE debts SET kind = 'debt' WHERE kind IS NULL OR TRIM(kind) = ''")
        conn.execute("UPDATE debts SET kind = 'fixed' WHERE kind IN ('cost', 'fixed_cost', 'koszt')")
        conn.execute("UPDATE debts SET kind = 'debt' WHERE kind NOT IN ('debt', 'fixed')")
        conn.execute("UPDATE debts SET total_amount = 0 WHERE total_amount IS NULL")
        conn.execute("UPDATE debts SET monthly_amount = 0 WHERE monthly_amount IS NULL")
        conn.execute("UPDATE debts SET due_day = 0 WHERE due_day IS NULL")
        conn.execute("UPDATE debts SET note = '' WHERE note IS NULL")
        conn.execute("UPDATE debts SET created_at = '' WHERE created_at IS NULL")
        conn.execute("UPDATE debts SET updated_at = '' WHERE updated_at IS NULL")
        conn.execute("UPDATE debt_payment_states SET done = 0 WHERE done IS NULL")
        conn.execute("UPDATE debt_payment_states SET updated_at = '' WHERE updated_at IS NULL")

        conn.commit()
