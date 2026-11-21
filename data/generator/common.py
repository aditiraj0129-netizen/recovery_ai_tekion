"""Small time helpers shared by the generator modules."""

from datetime import date, datetime, timedelta

DEFAULT_SCENARIO_DATE = "2026-03-10"
SCENARIO_CLOCK = "09:40"


def ts(base: date, hhmm: str, day_offset: int = 0) -> datetime:
    """Build a naive datetime on `base` (+ day_offset days) at HH:MM."""
    hour, minute = (int(part) for part in hhmm.split(":"))
    return datetime(base.year, base.month, base.day, hour, minute) + timedelta(
        days=day_offset
    )


def iso(value: datetime | None) -> str | None:
    return value.isoformat(timespec="seconds") if value is not None else None
