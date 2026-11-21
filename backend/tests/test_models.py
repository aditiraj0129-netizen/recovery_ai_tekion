from datetime import datetime

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models
from app.database import Base, make_engine

EXPECTED_TABLES = {
    "suppliers", "locations", "parts", "inventory", "customers", "vehicles",
    "technicians", "technician_skills", "bays", "repair_orders",
    "repair_order_parts", "repair_order_skills", "appointments", "disruptions",
    "plans", "plan_events", "undo_events",
}


@pytest.fixture()
def db(tmp_path):
    engine = make_engine(f"sqlite:///{tmp_path}/test.db")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


def test_all_expected_tables_are_created(db: Session) -> None:
    assert set(inspect(db.get_bind()).get_table_names()) == EXPECTED_TABLES


def test_inventory_rejects_reserved_above_on_hand(db: Session) -> None:
    db.add(models.Part(part_id="P-1", part_name="Pump"))
    db.add(models.Location(location_id="L-A", name="Store A"))
    db.commit()
    db.add(models.InventoryItem(part_id="P-1", location_id="L-A",
                                quantity_on_hand=1, reserved_quantity=2))
    with pytest.raises(IntegrityError):
        db.commit()


def test_foreign_keys_are_enforced(db: Session) -> None:
    now = datetime(2026, 3, 10, 9, 0)
    db.add(models.RepairOrder(ro_id="RO-1", vehicle_id="missing", customer_id="missing",
                              estimated_duration_minutes=60, status="waiting",
                              promised_at=now, created_at=now))
    with pytest.raises(IntegrityError):
        db.commit()
