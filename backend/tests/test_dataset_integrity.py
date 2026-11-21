"""Integrity tests for the synthetic dataset generator.

These run the generator in memory, so they do not depend on files in data/generated.
Generic checks run for several seeds; hero checks run for every seed too, because the
hero block is fixed by hand.
"""

import csv
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "data"))

from generator.generate_dataset import (  # noqa: E402
    dataset_to_json,
    generate_dataset,
    write_dataset,
)

GENERATED_DIR = REPO_ROOT / "data" / "generated"
SEEDS = [42, 7, 123]


def dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


@pytest.fixture(params=SEEDS, scope="module")
def ds(request):
    return generate_dataset(seed=request.param)


@pytest.fixture(scope="module")
def ds42():
    return generate_dataset(seed=42)


def by_id(rows: list[dict], key: str) -> dict[str, dict]:
    return {row[key]: row for row in rows}


# ------------------------------------------------------------------ counts and labels
def test_counts_match_the_blueprint(ds) -> None:
    assert len(ds["repair_orders"]) == 40
    assert 10 <= len(ds["technicians"]) <= 15
    assert 6 <= len(ds["bays"]) <= 8
    assert 20 <= len(ds["parts"]) <= 30
    assert len(ds["locations"]) == 3
    assert 20 <= len(ds["appointments"]) <= 30
    assert 10 <= len(ds["disruptions"]) <= 20


def test_every_record_is_labelled_synthetic(ds) -> None:
    assert ds["meta"]["is_synthetic"] is True
    assert "synthetic" in ds["meta"]["disclaimer"].lower()
    for table in ("suppliers", "locations", "parts", "inventory", "customers", "vehicles",
                  "technicians", "bays", "repair_orders", "appointments", "disruptions"):
        assert all(row["is_synthetic"] is True for row in ds[table]), table


def test_primary_keys_are_unique(ds) -> None:
    keys = {
        "suppliers": "supplier_id", "locations": "location_id", "parts": "part_id",
        "customers": "customer_id", "vehicles": "vehicle_id", "technicians": "technician_id",
        "bays": "bay_id", "repair_orders": "ro_id", "appointments": "appointment_id",
        "disruptions": "disruption_id",
    }
    for table, key in keys.items():
        ids = [row[key] for row in ds[table]]
        assert len(ids) == len(set(ids)), table
    pairs = [(r["part_id"], r["location_id"]) for r in ds["inventory"]]
    assert len(pairs) == len(set(pairs))


# ------------------------------------------------------------------ references
def test_every_reference_points_to_a_real_entity(ds) -> None:
    parts, locations = by_id(ds["parts"], "part_id"), by_id(ds["locations"], "location_id")
    suppliers = by_id(ds["suppliers"], "supplier_id")
    techs, bays = by_id(ds["technicians"], "technician_id"), by_id(ds["bays"], "bay_id")
    customers, vehicles = by_id(ds["customers"], "customer_id"), by_id(ds["vehicles"], "vehicle_id")
    ros = by_id(ds["repair_orders"], "ro_id")

    for loc in ds["locations"]:
        assert loc["supplier_id"] in suppliers
    for row in ds["inventory"]:
        assert row["part_id"] in parts and row["location_id"] in locations
        assert row["supplier_id"] in suppliers
    for veh in ds["vehicles"]:
        assert veh["customer_id"] in customers
    for ro in ds["repair_orders"]:
        assert ro["vehicle_id"] in vehicles and ro["customer_id"] in customers
        assert vehicles[ro["vehicle_id"]]["customer_id"] == ro["customer_id"]
        assert ro["assigned_technician_id"] in techs and ro["assigned_bay_id"] in bays
        assert all(line["part_id"] in parts for line in ro["required_parts"])
    for apt in ds["appointments"]:
        assert apt["ro_id"] in ros
    for d in ds["disruptions"]:
        assert d["related_part_id"] is None or d["related_part_id"] in parts
        assert d["related_technician_id"] is None or d["related_technician_id"] in techs
        assert d["related_bay_id"] is None or d["related_bay_id"] in bays
        assert d["related_location_id"] is None or d["related_location_id"] in locations


def test_every_part_has_stock_rows_at_every_location(ds) -> None:
    assert len(ds["inventory"]) == len(ds["parts"]) * len(ds["locations"])


# ------------------------------------------------------------------ schedule consistency
def test_assigned_technician_has_required_skills_and_is_present(ds) -> None:
    techs = by_id(ds["technicians"], "technician_id")
    for ro in ds["repair_orders"]:
        tech = techs[ro["assigned_technician_id"]]
        assert set(ro["required_skills"]) <= set(tech["skills"]), ro["ro_id"]
        assert tech["availability"] != "absent", ro["ro_id"]


def test_jobs_sit_inside_shift_and_bay_hours(ds) -> None:
    techs, bays = by_id(ds["technicians"], "technician_id"), by_id(ds["bays"], "bay_id")
    for ro in ds["repair_orders"]:
        start, end = dt(ro["scheduled_start"]), dt(ro["scheduled_end"])
        tech, bay = techs[ro["assigned_technician_id"]], bays[ro["assigned_bay_id"]]
        assert dt(tech["shift_start"]).time() <= start.time(), ro["ro_id"]
        assert end.time() <= dt(tech["shift_end"]).time(), ro["ro_id"]
        assert dt(bay["available_from"]).time() <= start.time(), ro["ro_id"]
        assert end.time() <= dt(bay["available_until"]).time(), ro["ro_id"]
        assert set(ro["required_skills"]) <= set(bay["supported_work"]), ro["ro_id"]


def test_no_technician_or_bay_is_double_booked(ds) -> None:
    for resource in ("assigned_technician_id", "assigned_bay_id"):
        spans = defaultdict(list)
        for ro in ds["repair_orders"]:
            spans[ro[resource]].append((dt(ro["scheduled_start"]), dt(ro["scheduled_end"]), ro["ro_id"]))
        for resource_id, items in spans.items():
            items.sort()
            for (_, prev_end, prev_ro), (next_start, _, next_ro) in zip(items, items[1:]):
                assert prev_end <= next_start, f"{resource_id}: {prev_ro} overlaps {next_ro}"


def test_planned_maintenance_does_not_collide_with_jobs(ds) -> None:
    window = next(d for d in ds["disruptions"] if d["disruption_id"] == "D-011")
    start = dt(window["start_time"])
    from datetime import timedelta
    end = start + timedelta(minutes=window["expected_duration_minutes"])
    for ro in ds["repair_orders"]:
        if ro["assigned_bay_id"] == window["related_bay_id"]:
            assert dt(ro["scheduled_end"]) <= start or dt(ro["scheduled_start"]) >= end


def test_times_and_statuses_are_consistent(ds) -> None:
    now = dt(f"{ds['meta']['scenario_date']}T{ds['meta']['scenario_clock']}:00")
    from datetime import timedelta
    for ro in ds["repair_orders"]:
        start, end = dt(ro["scheduled_start"]), dt(ro["scheduled_end"])
        assert end - start == timedelta(minutes=ro["estimated_duration_minutes"])
        assert dt(ro["created_at"]) <= now
        assert dt(ro["created_at"]) <= start
        assert dt(ro["promised_at"]) >= end, ro["ro_id"]
        assert dt(ro["promised_at"]) >= dt(ro["created_at"])
        expected = "completed" if end <= now else "in_progress" if start <= now else "waiting"
        assert ro["status"] == expected, ro["ro_id"]


def test_bay_and_technician_live_status_match_in_progress_work(ds) -> None:
    working_bays = {r["assigned_bay_id"] for r in ds["repair_orders"] if r["status"] == "in_progress"}
    working_techs = {r["assigned_technician_id"] for r in ds["repair_orders"] if r["status"] == "in_progress"}
    for bay in ds["bays"]:
        assert (bay["status"] == "occupied") == (bay["bay_id"] in working_bays)
    for tech in ds["technicians"]:
        if tech["availability"] != "absent":
            assert (tech["availability"] == "busy") == (tech["technician_id"] in working_techs)


# ------------------------------------------------------------------ appointments
def test_appointments_match_their_repair_orders(ds) -> None:
    ros = by_id(ds["repair_orders"], "ro_id")
    ro_ids = [a["ro_id"] for a in ds["appointments"]]
    assert len(ro_ids) == len(set(ro_ids)), "at most one appointment per RO"
    for apt in ds["appointments"]:
        ro = ros[apt["ro_id"]]
        assert apt["scheduled_at"] == ro["scheduled_start"]
        assert apt["promised_at"] == ro["promised_at"]
        assert apt["consent_status"] in {"pending", "approved", "declined"}


def test_customer_oem_preference_is_respected_by_parts(ds) -> None:
    parts, customers = by_id(ds["parts"], "part_id"), by_id(ds["customers"], "customer_id")
    for ro in ds["repair_orders"]:
        if customers[ro["customer_id"]]["part_preference"] == "OEM":
            assert all(parts[line["part_id"]]["part_type"] == "OEM" for line in ro["required_parts"])


# ------------------------------------------------------------------ inventory
def test_stock_quantities_are_logically_consistent(ds) -> None:
    for row in ds["inventory"]:
        assert row["quantity_on_hand"] >= 0 and row["reserved_quantity"] >= 0
        assert row["reserved_quantity"] <= row["quantity_on_hand"]
        assert row["stock_confidence"] in {"known", "estimated", "unverified"}
        if row["quantity_on_hand"] == 0 and row["location_id"] != "LOC-A":
            assert row["expected_arrival"] is not None


def test_store_a_reservations_equal_open_repair_order_demand(ds) -> None:
    demand: dict[str, int] = defaultdict(int)
    for ro in ds["repair_orders"]:
        if ro["ro_id"] in ("48213", "48240") or ro["status"] == "completed":
            continue
        for line in ro["required_parts"]:
            demand[line["part_id"]] += line["quantity"]
    for row in ds["inventory"]:
        if row["location_id"] == "LOC-A" and row["part_id"] not in ("P-001",):
            assert row["reserved_quantity"] == demand[row["part_id"]], row["part_id"]


# ------------------------------------------------------------------ hero scenario
def test_hero_repair_orders_have_the_blueprint_commitments(ds) -> None:
    ros = by_id(ds["repair_orders"], "ro_id")
    date = ds["meta"]["scenario_date"]
    tomorrow = "2026-03-11" if date == "2026-03-10" else None
    assert ros["48213"]["promised_at"] == f"{date}T17:00:00"
    assert ros["48213"]["is_waiting_customer"] is True
    assert ros["48240"]["promised_at"] == f"{tomorrow}T12:00:00"
    assert ros["48220"]["promised_at"] == f"{date}T15:00:00"
    assert ros["48231"]["promised_at"] == f"{date}T16:00:00"
    for direct in ("48213", "48240"):
        assert [l["part_id"] for l in ros[direct]["required_parts"]] == ["P-001"]
    for indirect in ("48220", "48231"):
        assert all(l["part_id"] != "P-001" for l in ros[indirect]["required_parts"])
        assert ros[indirect]["assigned_technician_id"] == "T03"


def test_t03_is_the_only_technician_who_can_install_the_pump(ds) -> None:
    capable = [t["technician_id"] for t in ds["technicians"] if "cooling_system" in t["skills"]]
    assert capable == ["T03"]
    ros = by_id(ds["repair_orders"], "ro_id")
    assert ros["48213"]["assigned_technician_id"] == "T03"
    assert ros["48213"]["scheduled_end"] <= ros["48220"]["scheduled_start"] <= ros["48231"]["scheduled_start"]


def test_only_the_two_pump_jobs_need_the_pump(ds) -> None:
    needing = sorted(r["ro_id"] for r in ds["repair_orders"]
                     if any(l["part_id"] == "P-001" for l in r["required_parts"]))
    assert needing == ["48213", "48240"]


def test_pump_stock_supports_plan_v1_failure_and_plan_v2(ds) -> None:
    stock = {r["location_id"]: r for r in ds["inventory"] if r["part_id"] == "P-001"}
    assert stock["LOC-A"]["quantity_on_hand"] == 0 and stock["LOC-A"]["expected_arrival"]
    # Store B: system believes 1, confidence unverified (D-002 reveals the true count of 0)
    assert stock["LOC-B"]["quantity_on_hand"] == 1 and stock["LOC-B"]["stock_confidence"] == "unverified"
    # Store C: genuinely has one, verified, longer transfer than B
    assert stock["LOC-C"]["quantity_on_hand"] == 1 and stock["LOC-C"]["stock_confidence"] == "known"
    locations = by_id(ds["locations"], "location_id")
    assert locations["LOC-B"]["transfer_time_minutes"] < locations["LOC-C"]["transfer_time_minutes"]


def test_hero_disruptions_are_seeded_and_dormant(ds) -> None:
    d = by_id(ds["disruptions"], "disruption_id")
    date = ds["meta"]["scenario_date"]
    assert d["D-001"]["disruption_type"] == "part_backorder"
    assert d["D-001"]["start_time"] == f"{date}T09:40:00" and d["D-001"]["status"] == "scheduled"
    assert d["D-001"]["related_part_id"] == "P-001"
    assert d["D-001"]["details"]["new_expected_arrival"] == "2026-03-11T10:00:00"
    assert d["D-002"]["disruption_type"] == "incorrect_inventory_count"
    assert d["D-002"]["start_time"] == f"{date}T10:38:00" and d["D-002"]["status"] == "scheduled"
    assert d["D-002"]["related_location_id"] == "LOC-B"
    assert d["D-002"]["details"] == {"system_quantity": 1, "actual_quantity": 0, "hero_step": "checkpoint_failure"}


def test_background_disruptions_do_not_touch_hero_resources(ds) -> None:
    for d in ds["disruptions"]:
        if d["disruption_id"] in ("D-001", "D-002"):
            continue
        assert d["related_part_id"] != "P-001", d["disruption_id"]
        assert d["related_technician_id"] != "T03", d["disruption_id"]
        assert d["related_bay_id"] not in ("BAY-02", "BAY-03"), d["disruption_id"]
        assert d["related_location_id"] not in ("LOC-B", "LOC-C"), d["disruption_id"]
        if d["affected_resource_type"] == "repair_order":
            assert d["affected_resource_id"] not in ("48213", "48240", "48220", "48231")


def test_hero_appointment_for_ro_48240_awaits_consent(ds) -> None:
    apt = next(a for a in ds["appointments"] if a["ro_id"] == "48240")
    assert apt["consent_status"] == "pending"
    assert apt["customer_preference"] == "OEM parts only"
    customer = by_id(ds["customers"], "customer_id")["C-0002"]
    assert customer["part_preference"] == "OEM"


def test_hero_meta_lists_the_four_repair_orders(ds) -> None:
    hero = ds["meta"]["hero_scenario"]
    assert hero["direct_ro_ids"] == ["48213", "48240"]
    assert hero["indirect_ro_ids"] == ["48220", "48231"]


# ------------------------------------------------------------------ reproducibility and files
def test_same_seed_gives_identical_output() -> None:
    assert dataset_to_json(generate_dataset(seed=42)) == dataset_to_json(generate_dataset(seed=42))


def test_different_seed_changes_the_random_block_but_not_the_hero_block() -> None:
    a, b = generate_dataset(seed=42), generate_dataset(seed=7)
    assert dataset_to_json(a) != dataset_to_json(b)
    hero_a = [r for r in a["repair_orders"] if r["ro_id"] in ("48213", "48240", "48220", "48231")]
    hero_b = [r for r in b["repair_orders"] if r["ro_id"] in ("48213", "48240", "48220", "48231")]
    assert hero_a == hero_b


def test_written_files_match_the_in_memory_dataset(tmp_path, ds42) -> None:
    paths = write_dataset(ds42, tmp_path)
    assert {p.name for p in paths} == {
        "dealership_dataset.json", "repair_orders.csv", "parts_inventory.csv",
        "technicians.csv", "bays.csv", "appointments.csv", "disruptions.csv",
    }
    for filename, table in [("repair_orders.csv", "repair_orders"), ("parts_inventory.csv", "inventory"),
                            ("technicians.csv", "technicians"), ("bays.csv", "bays"),
                            ("appointments.csv", "appointments"), ("disruptions.csv", "disruptions")]:
        with (tmp_path / filename).open(newline="", encoding="utf-8") as handle:
            assert len(list(csv.DictReader(handle))) == len(ds42[table]), filename


def test_committed_dataset_file_is_up_to_date_for_seed_42(ds42) -> None:
    committed = GENERATED_DIR / "dealership_dataset.json"
    if not committed.exists():
        pytest.skip("data/generated/dealership_dataset.json not generated yet")
    assert committed.read_text(encoding="utf-8") == dataset_to_json(ds42), (
        "Committed dataset is stale. Re-run: python data/generator/generate_dataset.py --seed 42"
    )
