from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from app import models
from app.database import make_engine
from app.seed import count_rows, load_dataset, reset_database, seed_database, seed_if_empty


def test_row_counts_match_the_dataset(db_engine, dataset) -> None:
    with Session(db_engine) as session:
        counts = count_rows(session)
    for table, count in counts.items():
        assert count == len(dataset[table]), table


def test_nested_lists_become_child_rows(db_engine) -> None:
    with Session(db_engine) as session:
        ro = session.get(models.RepairOrder, "48213")
        assert [(p.part_id, p.quantity) for p in ro.parts] == [("P-001", 1)]
        assert [s.skill for s in ro.skills] == ["cooling_system"]
        t03 = session.get(models.Technician, "T03")
        assert sorted(s.skill for s in t03.skills) == ["cooling_system", "diagnostics", "engine"]


def test_timestamps_are_stored_as_datetimes(db_engine) -> None:
    with Session(db_engine) as session:
        ro = session.get(models.RepairOrder, "48213")
        assert ro.promised_at == datetime(2026, 3, 10, 17, 0)
        pump_a = session.get(models.InventoryItem, ("P-001", "LOC-A"))
        assert pump_a.expected_arrival == datetime(2026, 3, 10, 10, 30)


def test_loaded_data_has_no_foreign_key_violations(db_engine) -> None:
    with db_engine.connect() as conn:
        assert conn.execute(text("PRAGMA foreign_key_check")).fetchall() == []


def test_seed_database_replaces_rather_than_duplicates(tmp_path, dataset) -> None:
    engine = make_engine(f"sqlite:///{tmp_path}/reseed.db")
    first = seed_database(engine, dataset)
    second = seed_database(engine, dataset)
    assert first == second
    assert second["repair_orders"] == 40
    engine.dispose()


def test_seed_if_empty_seeds_once_and_tolerates_a_missing_file(tmp_path, dataset) -> None:
    from generator.generate_dataset import dataset_to_json

    path = tmp_path / "dataset.json"
    path.write_text(dataset_to_json(dataset), encoding="utf-8")
    engine = make_engine(f"sqlite:///{tmp_path}/once.db")
    assert seed_if_empty(engine, path) is True
    assert seed_if_empty(engine, path) is False  # already has data

    empty = make_engine(f"sqlite:///{tmp_path}/missing.db")
    assert seed_if_empty(empty, tmp_path / "nope.json") is False
    with Session(empty) as session:
        assert count_rows(session)["repair_orders"] == 0
    engine.dispose()
    empty.dispose()


def test_load_dataset_is_importable_for_reuse() -> None:
    assert callable(load_dataset) and callable(reset_database)
