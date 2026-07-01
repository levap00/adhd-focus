import sqlite3
from pathlib import Path

from backend.accounts import DATABASE_PATH


def _connect_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_db() -> sqlite3.Connection:
    return _connect_db(DATABASE_PATH)



def _ensure_column(conn: sqlite3.Connection, table: str, column: str, ddl: str) -> None:
    columns = [row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")



def _init_db() -> None:
    with _connect_db(DATABASE_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                hashed_password TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL DEFAULT ''
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS invite_codes (
                code TEXT PRIMARY KEY,
                used_by_user_id INTEGER,
                created_at TEXT NOT NULL DEFAULT '',
                used_at TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (used_by_user_id) REFERENCES users(id)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                category TEXT DEFAULT 'praca',
                owner_user_id INTEGER,
                FOREIGN KEY (owner_user_id) REFERENCES users(id) ON DELETE CASCADE
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
                due_time TEXT DEFAULT '',
                reminder_offset_minutes INTEGER NOT NULL DEFAULT 0,
                estimated_time INTEGER DEFAULT 0,
                points_weight REAL DEFAULT 1,
                owner_user_id INTEGER NOT NULL,
                FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE,
                FOREIGN KEY (owner_user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS task_subtasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                title TEXT NOT NULL DEFAULT '',
                position INTEGER NOT NULL DEFAULT 0,
                done INTEGER NOT NULL DEFAULT 0,
                estimated_time INTEGER NOT NULL DEFAULT 0,
                points_weight REAL NOT NULL DEFAULT 0,
                done_at TEXT NOT NULL DEFAULT '',
                source_task_id INTEGER,
                source_module_id INTEGER,
                source_due_date TEXT NOT NULL DEFAULT '',
                source_due_time TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_task_subtasks_task_position ON task_subtasks(task_id, position, id)")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS task_shares (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                shared_user_id INTEGER NOT NULL,
                shared_at TEXT NOT NULL DEFAULT '',
                UNIQUE(task_id, shared_user_id),
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (shared_user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_task_shares_user ON task_shares(shared_user_id, task_id)")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS task_reward_claims (
                task_id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                points_weight REAL NOT NULL DEFAULT 0,
                awarded_at TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_task_reward_claims_user ON task_reward_claims(user_id)")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                key TEXT NOT NULL,
                owner_user_id INTEGER NOT NULL,
                content TEXT DEFAULT '',
                updated_at TEXT DEFAULT '',
                UNIQUE(owner_user_id, key),
                FOREIGN KEY (owner_user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS brain_dump_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_user_id INTEGER NOT NULL,
                title TEXT NOT NULL DEFAULT '',
                content TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (owner_user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_brain_dump_notes_owner_updated ON brain_dump_notes(owner_user_id, updated_at DESC, id DESC)")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reward_wallet (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                spent_points REAL NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS monthly_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                due_time TEXT NOT NULL DEFAULT '23:59',
                owner_user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (owner_user_id) REFERENCES users(id) ON DELETE CASCADE
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
            CREATE TABLE IF NOT EXISTS medication_reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                schedule_type TEXT NOT NULL DEFAULT 'daily',
                reminder_time TEXT NOT NULL DEFAULT '08:00',
                active INTEGER NOT NULL DEFAULT 1,
                owner_user_id INTEGER,
                created_at TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (owner_user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS medication_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medication_id INTEGER NOT NULL,
                date_key TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0,
                done_at TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL DEFAULT '',
                UNIQUE(medication_id, date_key),
                FOREIGN KEY (medication_id) REFERENCES medication_reminders(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_medication_states_date ON medication_states(date_key)")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS push_subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_user_id INTEGER NOT NULL,
                endpoint TEXT NOT NULL UNIQUE,
                p256dh TEXT NOT NULL DEFAULT '',
                auth TEXT NOT NULL DEFAULT '',
                content_encoding TEXT NOT NULL DEFAULT 'aes128gcm',
                user_agent TEXT NOT NULL DEFAULT '',
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL DEFAULT '',
                last_success_at TEXT NOT NULL DEFAULT '',
                last_error TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (owner_user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_push_subscriptions_owner_active ON push_subscriptions(owner_user_id, active)")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notification_settings (
                owner_user_id INTEGER PRIMARY KEY,
                enabled INTEGER NOT NULL DEFAULT 1,
                opening_enabled INTEGER NOT NULL DEFAULT 1,
                opening_time TEXT NOT NULL DEFAULT '08:00',
                day_summary_enabled INTEGER NOT NULL DEFAULT 1,
                day_summary_time TEXT NOT NULL DEFAULT '20:30',
                medication_enabled INTEGER NOT NULL DEFAULT 1,
                medication_repeat_minutes INTEGER NOT NULL DEFAULT 5,
                task_reminder_enabled INTEGER NOT NULL DEFAULT 1,
                task_reminder_repeat_minutes INTEGER NOT NULL DEFAULT 120,
                timezone TEXT NOT NULL DEFAULT 'Europe/Warsaw',
                updated_at TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (owner_user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notification_delivery_markers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_user_id INTEGER NOT NULL,
                marker_key TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT '',
                UNIQUE(owner_user_id, marker_key),
                FOREIGN KEY (owner_user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_notification_delivery_markers_owner ON notification_delivery_markers(owner_user_id, marker_key)")

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
                owner_user_id INTEGER NOT NULL,
                note TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (owner_user_id) REFERENCES users(id) ON DELETE CASCADE
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
        _ensure_column(conn, "modules", "owner_user_id", "INTEGER")
        _ensure_column(conn, "brain_dump_notes", "title", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "brain_dump_notes", "content", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "brain_dump_notes", "created_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "brain_dump_notes", "updated_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "tasks", "priority", "TEXT DEFAULT ''")
        _ensure_column(conn, "tasks", "description", "TEXT DEFAULT ''")
        _ensure_column(conn, "tasks", "due_date", "TEXT DEFAULT ''")
        _ensure_column(conn, "tasks", "due_time", "TEXT DEFAULT ''")
        _ensure_column(conn, "tasks", "reminder_offset_minutes", "INTEGER NOT NULL DEFAULT 0")
        _ensure_column(conn, "tasks", "estimated_time", "INTEGER DEFAULT 0")
        _ensure_column(conn, "tasks", "points_weight", "REAL DEFAULT 1")
        _ensure_column(conn, "tasks", "owner_user_id", "INTEGER")
        _ensure_column(conn, "task_subtasks", "title", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "task_subtasks", "position", "INTEGER NOT NULL DEFAULT 0")
        _ensure_column(conn, "task_subtasks", "done", "INTEGER NOT NULL DEFAULT 0")
        _ensure_column(conn, "task_subtasks", "estimated_time", "INTEGER NOT NULL DEFAULT 0")
        _ensure_column(conn, "task_subtasks", "points_weight", "REAL NOT NULL DEFAULT 0")
        _ensure_column(conn, "task_subtasks", "done_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "task_subtasks", "source_task_id", "INTEGER")
        _ensure_column(conn, "task_subtasks", "source_module_id", "INTEGER")
        _ensure_column(conn, "task_subtasks", "source_due_date", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "task_subtasks", "source_due_time", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "task_subtasks", "created_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "task_subtasks", "updated_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "monthly_tasks", "due_day", "INTEGER DEFAULT 0")
        _ensure_column(conn, "monthly_tasks", "due_time", "TEXT NOT NULL DEFAULT '23:59'")
        _ensure_column(conn, "monthly_tasks", "owner_user_id", "INTEGER")
        _ensure_column(conn, "monthly_tasks", "repeat_type", "TEXT NOT NULL DEFAULT 'monthly'")
        _ensure_column(conn, "monthly_tasks", "repeat_weekday", "INTEGER NOT NULL DEFAULT 1")
        _ensure_column(conn, "monthly_tasks", "created_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "monthly_tasks", "updated_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "monthly_task_states", "note", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "monthly_task_states", "updated_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "medication_reminders", "schedule_type", "TEXT NOT NULL DEFAULT 'daily'")
        _ensure_column(conn, "medication_reminders", "reminder_time", "TEXT NOT NULL DEFAULT '08:00'")
        _ensure_column(conn, "medication_reminders", "active", "INTEGER NOT NULL DEFAULT 1")
        _ensure_column(conn, "medication_reminders", "owner_user_id", "INTEGER")
        _ensure_column(conn, "medication_reminders", "created_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "medication_reminders", "updated_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "medication_states", "done", "INTEGER NOT NULL DEFAULT 0")
        _ensure_column(conn, "medication_states", "done_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "medication_states", "updated_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "push_subscriptions", "p256dh", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "push_subscriptions", "auth", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "push_subscriptions", "content_encoding", "TEXT NOT NULL DEFAULT 'aes128gcm'")
        _ensure_column(conn, "push_subscriptions", "user_agent", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "push_subscriptions", "active", "INTEGER NOT NULL DEFAULT 1")
        _ensure_column(conn, "push_subscriptions", "created_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "push_subscriptions", "updated_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "push_subscriptions", "last_success_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "push_subscriptions", "last_error", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "notification_settings", "enabled", "INTEGER NOT NULL DEFAULT 1")
        _ensure_column(conn, "notification_settings", "opening_enabled", "INTEGER NOT NULL DEFAULT 1")
        _ensure_column(conn, "notification_settings", "opening_time", "TEXT NOT NULL DEFAULT '08:00'")
        _ensure_column(conn, "notification_settings", "day_summary_enabled", "INTEGER NOT NULL DEFAULT 1")
        _ensure_column(conn, "notification_settings", "day_summary_time", "TEXT NOT NULL DEFAULT '20:30'")
        _ensure_column(conn, "notification_settings", "medication_enabled", "INTEGER NOT NULL DEFAULT 1")
        _ensure_column(conn, "notification_settings", "medication_repeat_minutes", "INTEGER NOT NULL DEFAULT 5")
        _ensure_column(conn, "notification_settings", "task_reminder_enabled", "INTEGER NOT NULL DEFAULT 1")
        _ensure_column(conn, "notification_settings", "task_reminder_repeat_minutes", "INTEGER NOT NULL DEFAULT 120")
        _ensure_column(conn, "notification_settings", "timezone", "TEXT NOT NULL DEFAULT 'Europe/Warsaw'")
        _ensure_column(conn, "notification_settings", "updated_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "debts", "place", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "debts", "kind", "TEXT NOT NULL DEFAULT 'debt'")
        _ensure_column(conn, "debts", "total_amount", "REAL NOT NULL DEFAULT 0")
        _ensure_column(conn, "debts", "monthly_amount", "REAL NOT NULL DEFAULT 0")
        _ensure_column(conn, "debts", "due_day", "INTEGER NOT NULL DEFAULT 0")
        _ensure_column(conn, "debts", "note", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "debts", "owner_user_id", "INTEGER")
        _ensure_column(conn, "debts", "created_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "debts", "updated_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "debt_payment_states", "done", "INTEGER NOT NULL DEFAULT 0")
        _ensure_column(conn, "debt_payment_states", "updated_at", "TEXT NOT NULL DEFAULT ''")

        conn.execute("UPDATE modules SET category = 'praca' WHERE category IS NULL OR TRIM(category) = ''")
        conn.execute("UPDATE brain_dump_notes SET title = '' WHERE title IS NULL")
        conn.execute("UPDATE brain_dump_notes SET content = '' WHERE content IS NULL")
        conn.execute("UPDATE brain_dump_notes SET created_at = '' WHERE created_at IS NULL")
        conn.execute("UPDATE brain_dump_notes SET updated_at = '' WHERE updated_at IS NULL")
        conn.execute("UPDATE tasks SET priority = '' WHERE priority IS NULL")
        conn.execute("UPDATE tasks SET description = '' WHERE description IS NULL")
        conn.execute("UPDATE tasks SET due_date = '' WHERE due_date IS NULL")
        conn.execute("UPDATE tasks SET due_time = '' WHERE due_time IS NULL")
        conn.execute("UPDATE tasks SET due_time = '' WHERE TRIM(due_date) = ''")
        conn.execute("UPDATE tasks SET reminder_offset_minutes = 0 WHERE reminder_offset_minutes IS NULL OR reminder_offset_minutes < 0")
        conn.execute("UPDATE tasks SET estimated_time = 0 WHERE estimated_time IS NULL")
        conn.execute("UPDATE tasks SET points_weight = 1 WHERE points_weight IS NULL OR points_weight <= 0")
        conn.execute("UPDATE tasks SET status = 'przygotowanie' WHERE status IN ('analiza', 'wstepne')")
        conn.execute("UPDATE task_subtasks SET title = '' WHERE title IS NULL")
        conn.execute("UPDATE task_subtasks SET position = 0 WHERE position IS NULL")
        conn.execute("UPDATE task_subtasks SET done = 0 WHERE done IS NULL")
        conn.execute("UPDATE task_subtasks SET estimated_time = 0 WHERE estimated_time IS NULL OR estimated_time < 0")
        conn.execute("UPDATE task_subtasks SET points_weight = 0 WHERE points_weight IS NULL OR points_weight < 0")
        conn.execute("UPDATE task_subtasks SET done_at = '' WHERE done_at IS NULL")
        conn.execute("UPDATE task_subtasks SET source_due_date = '' WHERE source_due_date IS NULL")
        conn.execute("UPDATE task_subtasks SET source_due_time = '' WHERE source_due_time IS NULL")
        conn.execute("UPDATE task_subtasks SET created_at = '' WHERE created_at IS NULL")
        conn.execute("UPDATE task_subtasks SET updated_at = '' WHERE updated_at IS NULL")
        conn.execute("UPDATE task_subtasks SET done = 1 WHERE done NOT IN (0, 1)")
        conn.execute("UPDATE monthly_tasks SET due_day = 0 WHERE due_day IS NULL")
        conn.execute("UPDATE monthly_tasks SET due_time = '23:59' WHERE due_time IS NULL OR TRIM(due_time) = ''")
        conn.execute("UPDATE monthly_tasks SET repeat_type = 'monthly' WHERE repeat_type IS NULL OR TRIM(repeat_type) = ''")
        conn.execute("UPDATE monthly_tasks SET repeat_type = 'monthly' WHERE repeat_type NOT IN ('monthly', 'weekly')")
        conn.execute("UPDATE monthly_tasks SET repeat_weekday = 1 WHERE repeat_weekday IS NULL")
        conn.execute("UPDATE monthly_tasks SET repeat_weekday = 1 WHERE repeat_weekday < 1 OR repeat_weekday > 7")
        conn.execute("UPDATE monthly_tasks SET created_at = '' WHERE created_at IS NULL")
        conn.execute("UPDATE monthly_tasks SET updated_at = '' WHERE updated_at IS NULL")
        conn.execute("UPDATE monthly_task_states SET note = '' WHERE note IS NULL")
        conn.execute("UPDATE monthly_task_states SET updated_at = '' WHERE updated_at IS NULL")
        conn.execute("UPDATE medication_reminders SET schedule_type = 'daily' WHERE schedule_type IS NULL OR TRIM(schedule_type) = ''")
        conn.execute("UPDATE medication_reminders SET schedule_type = 'weekdays' WHERE schedule_type IN ('weekday', 'workdays', 'workday', 'pon-pt')")
        conn.execute("UPDATE medication_reminders SET schedule_type = 'daily' WHERE schedule_type NOT IN ('daily', 'weekdays')")
        conn.execute("UPDATE medication_reminders SET reminder_time = '08:00' WHERE reminder_time IS NULL OR TRIM(reminder_time) = ''")
        conn.execute("UPDATE medication_reminders SET active = 1 WHERE active IS NULL")
        conn.execute("UPDATE medication_reminders SET active = 1 WHERE active NOT IN (0, 1)")
        conn.execute("UPDATE medication_reminders SET created_at = '' WHERE created_at IS NULL")
        conn.execute("UPDATE medication_reminders SET updated_at = '' WHERE updated_at IS NULL")
        conn.execute("UPDATE medication_states SET date_key = '' WHERE date_key IS NULL")
        conn.execute("UPDATE medication_states SET done = 0 WHERE done IS NULL")
        conn.execute("UPDATE medication_states SET done = 1 WHERE done NOT IN (0, 1)")
        conn.execute("UPDATE medication_states SET done_at = '' WHERE done_at IS NULL")
        conn.execute("UPDATE medication_states SET updated_at = '' WHERE updated_at IS NULL")
        conn.execute("UPDATE push_subscriptions SET p256dh = '' WHERE p256dh IS NULL")
        conn.execute("UPDATE push_subscriptions SET auth = '' WHERE auth IS NULL")
        conn.execute("UPDATE push_subscriptions SET content_encoding = 'aes128gcm' WHERE content_encoding IS NULL OR TRIM(content_encoding) = ''")
        conn.execute("UPDATE push_subscriptions SET user_agent = '' WHERE user_agent IS NULL")
        conn.execute("UPDATE push_subscriptions SET active = 1 WHERE active IS NULL")
        conn.execute("UPDATE push_subscriptions SET active = 1 WHERE active NOT IN (0, 1)")
        conn.execute("UPDATE push_subscriptions SET created_at = '' WHERE created_at IS NULL")
        conn.execute("UPDATE push_subscriptions SET updated_at = '' WHERE updated_at IS NULL")
        conn.execute("UPDATE push_subscriptions SET last_success_at = '' WHERE last_success_at IS NULL")
        conn.execute("UPDATE push_subscriptions SET last_error = '' WHERE last_error IS NULL")
        conn.execute("UPDATE notification_settings SET enabled = 1 WHERE enabled IS NULL")
        conn.execute("UPDATE notification_settings SET enabled = 1 WHERE enabled NOT IN (0, 1)")
        conn.execute("UPDATE notification_settings SET opening_enabled = 1 WHERE opening_enabled IS NULL")
        conn.execute("UPDATE notification_settings SET opening_enabled = 1 WHERE opening_enabled NOT IN (0, 1)")
        conn.execute("UPDATE notification_settings SET opening_time = '08:00' WHERE opening_time IS NULL OR TRIM(opening_time) = ''")
        conn.execute("UPDATE notification_settings SET day_summary_enabled = 1 WHERE day_summary_enabled IS NULL")
        conn.execute("UPDATE notification_settings SET day_summary_enabled = 1 WHERE day_summary_enabled NOT IN (0, 1)")
        conn.execute("UPDATE notification_settings SET day_summary_time = '20:30' WHERE day_summary_time IS NULL OR TRIM(day_summary_time) = ''")
        conn.execute("UPDATE notification_settings SET medication_enabled = 1 WHERE medication_enabled IS NULL")
        conn.execute("UPDATE notification_settings SET medication_enabled = 1 WHERE medication_enabled NOT IN (0, 1)")
        conn.execute("UPDATE notification_settings SET medication_repeat_minutes = 5 WHERE medication_repeat_minutes IS NULL OR medication_repeat_minutes < 1")
        conn.execute("UPDATE notification_settings SET task_reminder_enabled = 1 WHERE task_reminder_enabled IS NULL")
        conn.execute("UPDATE notification_settings SET task_reminder_enabled = 1 WHERE task_reminder_enabled NOT IN (0, 1)")
        conn.execute("UPDATE notification_settings SET task_reminder_repeat_minutes = 120 WHERE task_reminder_repeat_minutes IS NULL OR task_reminder_repeat_minutes < 15")
        conn.execute("UPDATE notification_settings SET timezone = 'Europe/Warsaw' WHERE timezone IS NULL OR TRIM(timezone) = ''")
        conn.execute("UPDATE notification_settings SET updated_at = '' WHERE updated_at IS NULL")
        conn.execute("DELETE FROM notification_delivery_markers WHERE marker_key LIKE 'telegram-%' OR marker_key LIKE 'telegram:%'")
        conn.execute("UPDATE debts SET place = '' WHERE place IS NULL")
        conn.execute("UPDATE debts SET kind = 'debt' WHERE kind IS NULL OR TRIM(kind) = ''")
        conn.execute("UPDATE debts SET kind = 'fixed' WHERE kind IN ('cost', 'fixed_cost', 'koszt')")
        conn.execute("UPDATE debts SET kind = 'debt' WHERE kind NOT IN ('debt', 'fixed')")
        conn.execute("UPDATE debts SET total_amount = 0 WHERE total_amount IS NULL")
        conn.execute("UPDATE debts SET monthly_amount = 0 WHERE monthly_amount IS NULL")
        conn.execute("UPDATE debts SET monthly_amount = total_amount WHERE kind = 'fixed' AND monthly_amount = 0 AND total_amount > 0")
        conn.execute("UPDATE debts SET total_amount = 0 WHERE kind = 'fixed'")
        conn.execute("UPDATE debts SET due_day = 0 WHERE due_day IS NULL")
        conn.execute("UPDATE debts SET note = '' WHERE note IS NULL")
        conn.execute("UPDATE debts SET created_at = '' WHERE created_at IS NULL")
        conn.execute("UPDATE debts SET updated_at = '' WHERE updated_at IS NULL")
        conn.execute("UPDATE debt_payment_states SET done = 0 WHERE done IS NULL")
        conn.execute("UPDATE debt_payment_states SET updated_at = '' WHERE updated_at IS NULL")
        conn.commit()


def init_db() -> None:
    _init_db()


def init_db_for_username(username: str) -> None:
    _init_db()
