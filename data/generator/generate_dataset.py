"""Reproducible synthetic dealership dataset generator.

Run from the repository root:
    python data/generator/generate_dataset.py --seed 42

Output (data/generated/):
    dealership_dataset.json   single source of truth, all tables, all references valid
    *.csv                     flat views of the blueprint's main tables (derived from the JSON)
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1]
if str(DATA_DIR) not in sys.path:
    sys.path.insert(0, str(DATA_DIR))

from generator import reference_data as ref  # noqa: E402
from generator.common import DEFAULT_SCENARIO_DATE, SCENARIO_CLOCK, iso, ts  # noqa: E402
from generator.hero import (  # noqa: E402
    HERO_APPOINTMENT_PREFERENCES,
    HERO_DIRECT_RO_IDS,
    HERO_INDIRECT_RO_IDS,
    HERO_PART_ID,
    HERO_RO_IDS,
    HERO_TECHNICIAN_ID,
    build_hero,
)

TOTAL_REPAIR_ORDERS = 40
TOTAL_APPOINTMENTS = 28
DEFAULT_SEED = 42
DEFAULT_OUT_DIR = DATA_DIR / "generated"


# --------------------------------------------------------------------------- resources
def build_technicians(rng: random.Random, base: date) -> list[dict]:
    return [
        {
            "technician_id": spec["technician_id"],
            "name": spec["name"],
            "skills": list(spec["skills"]),
            "shift_start": ts(base, spec["shift"][0]),
            "shift_end": ts(base, spec["shift"][1]),
            "availability": "absent" if spec.get("absent") else "available",
            "efficiency_factor": round(0.85 + rng.randrange(0, 31) / 100, 2),
            "is_synthetic": True,
        }
        for spec in ref.TECHNICIANS
    ]


def build_bays(base: date) -> list[dict]:
    return [
        {
            "bay_id": spec["bay_id"],
            "supported_work": list(spec["supported_work"]),
            "available_from": ts(base, spec["hours"][0]),
            "available_until": ts(base, spec["hours"][1]),
            "status": "available",
            "is_synthetic": True,
        }
        for spec in ref.BAYS
    ]


# --------------------------------------------------------------------------- scheduling
def _overlaps(intervals: list[tuple[datetime, datetime]], start: datetime, end: datetime) -> bool:
    return any(start < other_end and other_start < end for other_start, other_end in intervals)


def _initial_busy(base: date, hero_ros: list[dict]) -> dict[str, list[tuple[datetime, datetime]]]:
    busy: dict[str, list[tuple[datetime, datetime]]] = defaultdict(list)
    for ro in hero_ros:
        span = (ro["scheduled_start"], ro["scheduled_end"])
        busy[f"tech:{ro['assigned_technician_id']}"].append(span)
        busy[f"bay:{ro['assigned_bay_id']}"].append(span)
    maint = ref.PLANNED_MAINTENANCE
    start = ts(base, maint["start"])
    busy[f"bay:{maint['bay_id']}"].append((start, start + timedelta(minutes=maint["minutes"])))
    return busy


def _find_slot(rng, base, skills, duration, technicians, bays, busy):
    """Find a (technician, bay, start, end) slot on the scenario day, or None."""
    grid_start = ts(base, "07:30")
    slots = 45  # 15-minute grid, 07:30 to 18:30
    first = rng.randrange(0, 29)
    tech_pool = [
        t for t in technicians
        if t["technician_id"] != HERO_TECHNICIAN_ID
        and t["availability"] != "absent"
        and set(skills) <= set(t["skills"])
    ]
    bay_pool = [b for b in bays if set(skills) <= set(b["supported_work"])]
    rng.shuffle(tech_pool)
    rng.shuffle(bay_pool)
    for step in range(slots):
        start = grid_start + timedelta(minutes=15 * ((first + step) % slots))
        end = start + timedelta(minutes=duration)
        for tech in tech_pool:
            if not (tech["shift_start"] <= start and end <= tech["shift_end"]):
                continue
            if _overlaps(busy[f"tech:{tech['technician_id']}"], start, end):
                continue
            for bay in bay_pool:
                if not (bay["available_from"] <= start and end <= bay["available_until"]):
                    continue
                if _overlaps(busy[f"bay:{bay['bay_id']}"], start, end):
                    continue
                return tech, bay, start, end
    return None


def _status_at(now: datetime, start: datetime, end: datetime) -> str:
    if end <= now:
        return "completed"
    if start <= now:
        return "in_progress"
    return "waiting"


# --------------------------------------------------------------------------- repair orders
def build_random_block(rng, base, now, technicians, bays, hero) -> dict:
    """The 36 non-hero repair orders plus their customers and vehicles."""
    busy = _initial_busy(base, hero["repair_orders"])
    parts_type = {part_id: ptype for part_id, _name, ptype, _cost in ref.PARTS}

    pool = [str(n) for n in range(48201, 48262) if str(n) not in HERO_RO_IDS]
    ro_ids = sorted(rng.sample(pool, TOTAL_REPAIR_ORDERS - len(HERO_RO_IDS)))

    customers, vehicles, repair_orders = [], [], []
    for index, ro_id in enumerate(ro_ids, start=len(hero["customers"]) + 1):
        slot = None
        for _attempt in range(30):  # if a job type has no free slot, try another type
            template = rng.choice(ref.JOB_TEMPLATES)
            duration = rng.choice(template["durations"])
            slot = _find_slot(rng, base, template["skills"], duration, technicians, bays, busy)
            if slot is not None:
                break
        if slot is None:
            raise RuntimeError(f"Could not schedule RO {ro_id}; capacity too tight.")
        tech, bay, start, end = slot
        busy[f"tech:{tech['technician_id']}"].append((start, end))
        busy[f"bay:{bay['bay_id']}"].append((start, end))

        part_count = rng.randint(template["min_parts"], template["max_parts"])
        part_ids = sorted(rng.sample(template["parts"], part_count))
        all_oem = all(parts_type[p] == "OEM" for p in part_ids)

        customer_id, vehicle_id = f"C-{index:04d}", f"VEH-{index:04d}"
        make = rng.choice(sorted(ref.FICTIONAL_MAKES))
        customers.append({
            "customer_id": customer_id,
            "name": f"{rng.choice(ref.FIRST_NAMES)} {rng.choice(ref.LAST_NAMES)}",
            "part_preference": "OEM" if all_oem and rng.random() < 0.3 else None,
            "is_synthetic": True,
        })
        vehicles.append({
            "vehicle_id": vehicle_id,
            "customer_id": customer_id,
            "make": make,
            "model": rng.choice(ref.FICTIONAL_MAKES[make]),
            "year": rng.randint(2012, 2025),
            "is_synthetic": True,
        })

        waiting = rng.random() < 0.3
        created = min(start, now) - timedelta(minutes=rng.randrange(30, 60 * 30, 15))
        repair_orders.append({
            "ro_id": ro_id,
            "vehicle_id": vehicle_id,
            "customer_id": customer_id,
            "required_parts": [{"part_id": p, "quantity": 1} for p in part_ids],
            "required_skills": list(template["skills"]),
            "estimated_duration_minutes": duration,
            "status": _status_at(now, start, end),
            "promised_at": end + timedelta(minutes=rng.choice([30, 45, 60, 90, 120])),
            "priority": 1 if waiting else rng.choice([2, 3, 3, 4]),
            "assigned_technician_id": tech["technician_id"],
            "assigned_bay_id": bay["bay_id"],
            "scheduled_start": start,
            "scheduled_end": end,
            "created_at": created,
            "is_waiting_customer": waiting,
            "is_synthetic": True,
        })
    return {"customers": customers, "vehicles": vehicles, "repair_orders": repair_orders}


# --------------------------------------------------------------------------- inventory
def build_inventory(rng, base, repair_orders) -> list[dict]:
    """One row per part per location. Store A reservations equal real RO demand."""
    demand: dict[str, int] = defaultdict(int)
    for ro in repair_orders:
        if ro["ro_id"] in HERO_DIRECT_RO_IDS or ro["status"] == "completed":
            continue  # pump jobs cannot reserve stock that does not exist
        for line in ro["required_parts"]:
            demand[line["part_id"]] += line["quantity"]

    locations = {loc["location_id"]: loc for loc in ref.LOCATIONS}
    rows = []
    for part_id, _name, part_type, cost in ref.PARTS:
        for location_id, location in locations.items():
            supplier = "SUP-OEM" if part_type == "OEM" else location["supplier_id"]
            arrival = None
            confidence = "known"
            if part_id == HERO_PART_ID:
                if location_id == "LOC-A":  # on order, ETA today 10:30 (will be backordered at 09:40)
                    on_hand, reserved, arrival, confidence = 0, 0, ts(base, "10:30"), "estimated"
                elif location_id == "LOC-B":  # system says 1; physical count is 0 (see D-002)
                    on_hand, reserved, confidence = 1, 0, "unverified"
                else:  # Store C really has one
                    on_hand, reserved = 1, 0
            elif location_id == "LOC-A":
                if part_id == "P-021":  # backordered, see D-004
                    on_hand, reserved, arrival, confidence = 0, 0, ts(base, "09:00", 3), "estimated"
                else:
                    reserved = demand[part_id]
                    on_hand = reserved + rng.randrange(0, 4)
            else:
                on_hand = rng.randrange(0, 5)
                reserved = rng.randrange(0, min(on_hand, 1) + 1)
                confidence = rng.choice(["known", "known", "estimated"])
                if on_hand == 0:
                    arrival = ts(base, "09:00", 1)
            rows.append({
                "part_id": part_id,
                "location_id": location_id,
                "supplier_id": supplier,
                "quantity_on_hand": on_hand,
                "reserved_quantity": reserved,
                "expected_arrival": arrival,
                "stock_confidence": confidence,
                "unit_cost": cost,
                "is_synthetic": True,
            })
    return rows


# --------------------------------------------------------------------------- appointments
def build_appointments(rng, repair_orders) -> list[dict]:
    by_id = {ro["ro_id"]: ro for ro in repair_orders}
    random_ids = sorted(ro_id for ro_id in by_id if ro_id not in HERO_RO_IDS)
    extra = TOTAL_APPOINTMENTS - len(HERO_RO_IDS)
    sampled = rng.sample(random_ids, extra)

    plan: list[tuple[str, str | None, str]] = []  # (ro_id, preference, consent)
    for ro_id in HERO_RO_IDS:
        plan.append((ro_id, HERO_APPOINTMENT_PREFERENCES[ro_id], "pending"))
    for i, ro_id in enumerate(sampled):
        if i < 2:
            plan.append((ro_id, rng.choice(ref.APPOINTMENT_PREFERENCES), "approved"))
        elif i == 2:
            plan.append((ro_id, "Declined a later pickup time", "declined"))
        else:
            plan.append((ro_id, rng.choice(ref.APPOINTMENT_PREFERENCES), "pending"))

    rows = [
        {
            "ro_id": ro_id,
            "scheduled_at": by_id[ro_id]["scheduled_start"],
            "promised_at": by_id[ro_id]["promised_at"],
            "customer_preference": preference,
            "consent_status": consent,
            "is_synthetic": True,
        }
        for ro_id, preference, consent in plan
    ]
    rows.sort(key=lambda r: (r["scheduled_at"], r["ro_id"]))
    for number, row in enumerate(rows, start=1):
        row["appointment_id"] = f"APT-{number:03d}"
    return [{"appointment_id": r["appointment_id"], **{k: v for k, v in r.items() if k != "appointment_id"}} for r in rows]


# --------------------------------------------------------------------------- disruptions
def _disruption(did, dtype, rtype, rid, start, severity, minutes, status, description, details=None,
                part=None, tech=None, bay=None, location=None) -> dict:
    return {
        "disruption_id": did,
        "disruption_type": dtype,
        "affected_resource_type": rtype,
        "affected_resource_id": rid,
        "start_time": start,
        "severity": severity,
        "expected_duration_minutes": minutes,
        "status": status,
        "related_part_id": part,
        "related_technician_id": tech,
        "related_bay_id": bay,
        "related_location_id": location,
        "description": description,
        "details": details or {},
        "is_synthetic": True,
    }


def build_disruptions(base: date, repair_orders: list[dict]) -> list[dict]:
    def pick(statuses: tuple[str, ...]) -> str:
        pool = sorted(
            ro["ro_id"] for ro in repair_orders
            if ro["ro_id"] not in HERO_RO_IDS and ro["status"] in statuses
        )
        fallback = sorted(ro["ro_id"] for ro in repair_orders if ro["ro_id"] not in HERO_RO_IDS)
        return (pool or fallback)[0]

    detected = ts(base, "09:40")
    new_eta = ts(base, "10:00", 1)
    maint = ref.PLANNED_MAINTENANCE
    return [
        # ---- hero disruptions: dormant ("scheduled") until the demo fires them
        _disruption("D-001", "part_backorder", "part", HERO_PART_ID, detected, "high",
                    int((new_eta - detected).total_seconds() // 60), "scheduled",
                    "OEM coolant pump backordered; new ETA tomorrow 10:00.",
                    {"previous_expected_arrival": iso(ts(base, "10:30")),
                     "new_expected_arrival": iso(new_eta), "hero_step": "detect"},
                    part=HERO_PART_ID, location="LOC-A"),
        _disruption("D-002", "incorrect_inventory_count", "inventory", f"{HERO_PART_ID}@LOC-B",
                    ts(base, "10:38"), "high", None, "scheduled",
                    "Store B inventory counter shows 0 on hand; system believed 1.",
                    {"system_quantity": 1, "actual_quantity": 0, "hero_step": "checkpoint_failure"},
                    part=HERO_PART_ID, location="LOC-B"),
        # ---- background disruptions: none touch P-001, T03, BAY-02/03 or Stores B/C
        _disruption("D-003", "technician_absence", "technician", "T11", ts(base, "07:30"), "medium", 600,
                    "active", "Technician T11 absent today (sick leave).", tech="T11"),
        _disruption("D-004", "part_backorder", "part", "P-021", ts(base, "08:15"), "low", 4320,
                    "active", "Thermostat housing backordered; no open repair order needs it.",
                    part="P-021", location="LOC-A"),
        _disruption("D-005", "repair_duration_overrun", "repair_order", pick(("in_progress",)),
                    ts(base, "09:05"), "medium", 45, "active",
                    "In-progress job running longer than estimated.",
                    {"ro_id": pick(("in_progress",)), "overrun_minutes": 45}),
        _disruption("D-006", "bay_unavailable", "bay", "BAY-07", ts(base, "13:00", -1), "low", 120,
                    "resolved", "Lift inspection yesterday afternoon (completed).", bay="BAY-07"),
        _disruption("D-007", "technician_absence", "technician", "T09", ts(base, "08:00", -1), "medium",
                    540, "resolved", "Technician T09 absent yesterday.", tech="T09"),
        _disruption("D-008", "incorrect_inventory_count", "inventory", "P-015@LOC-A",
                    ts(base, "15:20", -1), "low", None, "resolved",
                    "Refrigerant count corrected after cycle count.",
                    {"system_quantity": 3, "actual_quantity": 2}, part="P-015", location="LOC-A"),
        _disruption("D-009", "part_backorder", "part", "P-012", ts(base, "10:00", -2), "medium", 1560,
                    "resolved", "Alternator backorder cleared; stock received.",
                    part="P-012", location="LOC-A"),
        _disruption("D-010", "technician_absence", "technician", "T06", ts(base, "08:00", 1), "low", 540,
                    "scheduled", "Technician T06 approved leave tomorrow.", tech="T06"),
        _disruption("D-011", "bay_unavailable", "bay", maint["bay_id"], ts(base, maint["start"]), "low",
                    maint["minutes"], "scheduled", "Planned maintenance on BAY-05.", bay=maint["bay_id"]),
        _disruption("D-012", "repair_duration_overrun", "repair_order", pick(("completed", "in_progress")),
                    ts(base, "08:20"), "low", 30, "resolved", "Earlier job overran, now finished.",
                    {"ro_id": pick(("completed", "in_progress")), "overrun_minutes": 30}),
        _disruption("D-013", "part_backorder", "part", "P-014", ts(base, "13:00"), "medium", 2880,
                    "scheduled", "A/C compressor supplier delay expected this afternoon.",
                    part="P-014", location="LOC-A"),
        _disruption("D-014", "incorrect_inventory_count", "inventory", "P-005@LOC-A",
                    ts(base, "11:30"), "low", None, "scheduled",
                    "Cycle count may reveal an oil filter discrepancy.",
                    {"system_quantity": 4, "actual_quantity": 3}, part="P-005", location="LOC-A"),
    ]


# --------------------------------------------------------------------------- assembly
def generate_dataset(seed: int = DEFAULT_SEED, scenario_date: str = DEFAULT_SCENARIO_DATE) -> dict:
    """Build the full dataset in memory. Same seed in, same dataset out."""
    rng = random.Random(seed)
    base = date.fromisoformat(scenario_date)
    now = ts(base, SCENARIO_CLOCK)

    technicians = build_technicians(rng, base)
    bays = build_bays(base)
    hero = build_hero(base)
    block = build_random_block(rng, base, now, technicians, bays, hero)

    repair_orders = sorted(hero["repair_orders"] + block["repair_orders"], key=lambda r: r["ro_id"])
    customers = hero["customers"] + block["customers"]
    vehicles = hero["vehicles"] + block["vehicles"]

    # Live status of resources at the scenario clock.
    working_techs = {r["assigned_technician_id"] for r in repair_orders if r["status"] == "in_progress"}
    working_bays = {r["assigned_bay_id"] for r in repair_orders if r["status"] == "in_progress"}
    for tech in technicians:
        if tech["availability"] != "absent":
            tech["availability"] = "busy" if tech["technician_id"] in working_techs else "available"
    for bay in bays:
        bay["status"] = "occupied" if bay["bay_id"] in working_bays else "available"

    inventory = build_inventory(rng, base, repair_orders)
    appointments = build_appointments(rng, repair_orders)
    disruptions = build_disruptions(base, repair_orders)

    parts = [
        {"part_id": pid, "part_name": name, "part_type": ptype, "unit_cost": cost, "is_synthetic": True}
        for pid, name, ptype, cost in ref.PARTS
    ]
    suppliers = [{**s, "is_synthetic": True} for s in ref.SUPPLIERS]
    locations = [{**loc, "is_synthetic": True} for loc in ref.LOCATIONS]

    tables = {
        "suppliers": suppliers, "locations": locations, "parts": parts, "inventory": inventory,
        "customers": customers, "vehicles": vehicles, "technicians": technicians, "bays": bays,
        "repair_orders": repair_orders, "appointments": appointments, "disruptions": disruptions,
    }
    meta = {
        "dataset_name": "Recovery AI synthetic dealership dataset",
        "schema_version": "1.0",
        "is_synthetic": True,
        "disclaimer": ref.SYNTHETIC_NOTE,
        "seed": seed,
        "scenario_date": scenario_date,
        "scenario_clock": SCENARIO_CLOCK,
        "snapshot_note": "State of the dealership immediately before the 09:40 hero disruption is applied.",
        "hero_scenario": {
            "disruption_id": "D-001",
            "detected_at": iso(ts(base, "09:40")),
            "part_id": HERO_PART_ID,
            "direct_ro_ids": list(HERO_DIRECT_RO_IDS),
            "indirect_ro_ids": list(HERO_INDIRECT_RO_IDS),
            "shared_technician_id": HERO_TECHNICIAN_ID,
            "plan_v1_source_location": "LOC-B",
            "plan_v2_source_location": "LOC-C",
            "checkpoint_failure_disruption_id": "D-002",
        },
        "counts": {name: len(rows) for name, rows in tables.items()},
    }
    return _jsonable({"meta": meta, **tables})


def _jsonable(value):
    if isinstance(value, datetime):
        return iso(value)
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    return value


# --------------------------------------------------------------------------- writers
def dataset_to_json(dataset: dict) -> str:
    return json.dumps(dataset, indent=2, ensure_ascii=True) + "\n"


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_dataset(dataset: dict, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "dealership_dataset.json"
    json_path.write_text(dataset_to_json(dataset), encoding="utf-8")

    def flat(rows: list[dict], list_fields: dict[str, str]) -> list[dict]:
        out = []
        for row in rows:
            copy = dict(row)
            for field, mode in list_fields.items():
                if mode == "ids":
                    copy[field] = "|".join(item["part_id"] for item in row[field])
                else:
                    copy[field] = "|".join(row[field])
            out.append(copy)
        return out

    parts = {p["part_id"]: p for p in dataset["parts"]}
    inventory_rows = [
        {"part_id": r["part_id"], "part_name": parts[r["part_id"]]["part_name"],
         "part_type": parts[r["part_id"]]["part_type"], **{k: v for k, v in r.items() if k != "part_id"}}
        for r in dataset["inventory"]
    ]
    disruption_rows = [{**d, "details": json.dumps(d["details"], sort_keys=True)} for d in dataset["disruptions"]]

    specs = [
        ("repair_orders.csv", flat(dataset["repair_orders"], {"required_parts": "ids", "required_skills": "join"})),
        ("parts_inventory.csv", inventory_rows),
        ("technicians.csv", flat(dataset["technicians"], {"skills": "join"})),
        ("bays.csv", flat(dataset["bays"], {"supported_work": "join"})),
        ("appointments.csv", dataset["appointments"]),
        ("disruptions.csv", disruption_rows),
    ]
    paths = [json_path]
    for filename, rows in specs:
        path = out_dir / filename
        _write_csv(path, list(rows[0].keys()), rows)
        paths.append(path)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the Recovery AI synthetic dataset.")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--scenario-date", default=DEFAULT_SCENARIO_DATE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()

    dataset = generate_dataset(args.seed, args.scenario_date)
    paths = write_dataset(dataset, args.out)
    print(f"Generated synthetic dataset (seed={args.seed}) in {args.out}")
    for name, count in dataset["meta"]["counts"].items():
        print(f"  {name:<14}{count:>4}")
    print(f"  files written: {len(paths)}")


if __name__ == "__main__":
    main()
