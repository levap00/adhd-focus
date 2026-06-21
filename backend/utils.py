import re
from datetime import datetime, timezone
from typing import Optional

STATUS_ALIASES = {
    "analiza": "przygotowanie",
    "wstepne": "przygotowanie",
}
ALLOWED_STATUSES = {"oczekujace", "przygotowanie", "todo", "gotowe"}


def normalize_module_category(raw: Optional[str]) -> str:
    value = (raw or "praca").strip().lower()
    return "prywatne" if value.startswith("pryw") else "praca"


def normalize_priority(raw: Optional[str]) -> str:
    value = (raw or "").strip().upper()
    return value if value in {"P1", "P2", "P3"} else ""


def normalize_status(raw: Optional[str]) -> str:
    value = (raw or "oczekujace").strip().lower()
    value = STATUS_ALIASES.get(value, value)
    return value if value in ALLOWED_STATUSES else "oczekujace"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_month_key(raw: Optional[str]) -> str:
    value = (raw or "").strip()
    if value:
        try:
            datetime.strptime(value, "%Y-%m")
            return value
        except ValueError:
            pass
    return datetime.now(timezone.utc).strftime("%Y-%m")


def normalize_due_date(raw: Optional[str]) -> str:
    value = (raw or "").strip()
    if not value:
        return ""
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return value
    return ""


def normalize_due_time(raw: Optional[str], default: str = "23:59") -> str:
    fallback = (default or "").strip()
    value = (raw or "").strip() or fallback
    if not value:
        return ""
    if re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", value):
        return value
    if re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d", value):
        return value[:5]
    if re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", fallback):
        return fallback
    return ""


def parse_non_negative_int(raw, default: int = 0) -> int:
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return default
    return max(0, value)


def parse_non_negative_float(raw, default: float = 0.0) -> float:
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return default
    return round(max(0.0, value), 2)
