"""Load the generated synthetic dataset into the database.

Run manually (from backend/, venv active):  python -m app.seed
The API also calls seed_if_empty() on startup, so a fresh checkout just works.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from app import models
from app.config import get_settings
from app.database import Base

logger = logging.getLogger(__name__)

# JSON stores timestamps as ISO strings; the database wants datetime objects.
DATETIME_FIELDS: dict[str, tuple[str, ...]] = {
    "inventory": ("expected_arrival",),
    "technicians": ("shift_start", "shift_end"),
    "bays": ("available_from", "available_until"),
    "repair_orders": ("promised_at", "scheduled_start", "scheduled_end", "created_at"),
    "appointments": ("scheduled_at", "promised_at"),
    "disruptions": ("start_time",),
}

# Tables with no nested lists. Order matters: parents before children.
SIMPLE_TABLES = [
    ("suppliers", models.Supplier),
    ("locations", models.Location),
    ("parts", models.Part),
    ("customers", models.Customer),
    ("vehicles", models.Vehicle),
]

TABLE_MODELS = {
    "suppliers": models.Supplier,
    "locations": models.Location,
    "parts": models.Part,
    "inventory": models.InventoryItem,
    "customers": models.Customer,
    "vehicles": models.Vehicle,
    "technicians": models.Technician,
    "bays": models.Bay,
    "repair_orders": models.RepairOrder,
    "appointments": models.Appointment,
    "disruptions": models.Disruption,
}


def _prepare(table: str, row: dict) -> dict:
    data = dict(row)
    for field in DATETIME_FIELDS.get(table, ()):
        if data.get(field) is not None:
            data[field] = datetime.fromisoformat(data[field])
    return data


def load_dataset_file(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def reset_database(engine: Engine) -> None:
    """Drop and recreate every table (used for a clean re-seed)."""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def load_dataset(session: Session, dataset: dict) -> None:
    """Insert one dataset into an empty database. The caller commits."""
    # Flush after every table: SQLAlchemy only orders inserts by relationship(), not by plain
    # foreign-key columns, so we insert parents explicitly before their children.
    for table, model in SIMPLE_TABLES:
        session.add_all(model(**_prepare(table, row)) for row in dataset[table])
        session.flush()

    for row in dataset["technicians"]:
        data = _prepare("technicians", row)
        skills = data.pop("skills")
        session.add(models.Technician(**data, skills=[models.TechnicianSkill(skill=s) for s in skills]))
    session.flush()
    session.add_all(models.Bay(**_prepare("bays", row)) for row in dataset["bays"])
    session.flush()

    session.add_all(models.InventoryItem(**_prepare("inventory", row)) for row in dataset["inventory"])
    session.flush()
    for row in dataset["repair_orders"]:
        data = _prepare("repair_orders", row)
        parts, skills = data.pop("required_parts"), data.pop("required_skills")
        session.add(models.RepairOrder(
            **data,
            parts=[models.RepairOrderPart(part_id=p["part_id"], quantity=p["quantity"]) for p in parts],
            skills=[models.RepairOrderSkill(skill=s) for s in skills],
        ))
    session.flush()

    session.add_all(models.Appointment(**_prepare("appointments", row)) for row in dataset["appointments"])
    session.add_all(models.Disruption(**_prepare("disruptions", row)) for row in dataset["disruptions"])
    session.flush()


def count_rows(session: Session) -> dict[str, int]:
    return {
        table: session.scalar(select(func.count()).select_from(model)) or 0
        for table, model in TABLE_MODELS.items()
    }


def seed_database(engine: Engine, dataset: dict) -> dict[str, int]:
    """Wipe the database and load `dataset`. Returns row counts per table."""
    reset_database(engine)
    with Session(engine) as session:
        load_dataset(session, dataset)
        session.commit()
        return count_rows(session)


def seed_if_empty(engine: Engine, path: Path) -> bool:
    """Create tables and load the dataset only if there are no repair orders yet."""
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        if (session.scalar(select(func.count()).select_from(models.RepairOrder)) or 0) > 0:
            return False
        if not path.exists():
            logger.warning("Dataset file not found at %s; database left empty. "
                           "Run: python data/generator/generate_dataset.py", path)
            return False
        load_dataset(session, load_dataset_file(path))
        session.commit()
    logger.info("Seeded database from %s", path)
    return True


def main() -> None:
    from app.database import engine

    settings = get_settings()
    path = settings.resolved_dataset_path
    if not path.exists():
        raise SystemExit(f"Dataset not found: {path}\nRun: python data/generator/generate_dataset.py")
    counts = seed_database(engine, load_dataset_file(path))
    print(f"Seeded {settings.database_url} from {path}")
    for table, count in counts.items():
        print(f"  {table:<14}{count:>4}")


if __name__ == "__main__":
    main()
