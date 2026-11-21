"""The fixed hero scenario: four repair orders exposed by one backordered OEM pump.

Everything here is hand-specified (no randomness) and matches the blueprint:

    Direct:    RO 48213 (promise today 17:00), RO 48240 (promise tomorrow 12:00)
    Indirect:  RO 48220 (target 15:00), RO 48231 (target 16:00); both on technician T03

T03 is the only technician with the cooling_system skill, so T03 is the only person who
can install the pump. If the pump job slides, T03's later jobs (48220, 48231) slide too.
The dataset is a snapshot immediately BEFORE the 09:40 disruption is applied.
"""

from datetime import date, timedelta

from generator.common import ts

HERO_PART_ID = "P-001"
HERO_TECHNICIAN_ID = "T03"
HERO_DIRECT_RO_IDS = ("48213", "48240")
HERO_INDIRECT_RO_IDS = ("48220", "48231")
HERO_RO_IDS = HERO_DIRECT_RO_IDS + HERO_INDIRECT_RO_IDS

# Standing customer constraints on the hero appointments (consent is still pending).
HERO_APPOINTMENT_PREFERENCES = {
    "48213": "Waiting on site",
    "48240": "OEM parts only",
    "48220": None,
    "48231": None,
}


def _repair_order(
    ro_id: str, vehicle_id: str, customer_id: str, part_ids: list[str],
    skills: list[str], minutes: int, bay_id: str, start, promised, created,
    priority: int, waiting_customer: bool,
) -> dict:
    return {
        "ro_id": ro_id,
        "vehicle_id": vehicle_id,
        "customer_id": customer_id,
        "required_parts": [{"part_id": p, "quantity": 1} for p in part_ids],
        "required_skills": skills,
        "estimated_duration_minutes": minutes,
        "status": "waiting",
        "promised_at": promised,
        "priority": priority,
        "assigned_technician_id": HERO_TECHNICIAN_ID,
        "assigned_bay_id": bay_id,
        "scheduled_start": start,
        "scheduled_end": start + timedelta(minutes=minutes),
        "created_at": created,
        "is_waiting_customer": waiting_customer,
        "is_synthetic": True,
    }


def build_hero(base: date) -> dict:
    customers = [
        {"customer_id": "C-0001", "name": "Jordan Ellis", "part_preference": None, "is_synthetic": True},
        {"customer_id": "C-0002", "name": "Sam Whitaker", "part_preference": "OEM", "is_synthetic": True},
        {"customer_id": "C-0003", "name": "Nadia Rahman", "part_preference": None, "is_synthetic": True},
        {"customer_id": "C-0004", "name": "Chris Donovan", "part_preference": None, "is_synthetic": True},
    ]
    vehicles = [
        {"vehicle_id": "VEH-0001", "customer_id": "C-0001", "make": "Arden", "model": "Sedan S", "year": 2021, "is_synthetic": True},
        {"vehicle_id": "VEH-0002", "customer_id": "C-0002", "make": "Brava", "model": "Wagon W", "year": 2019, "is_synthetic": True},
        {"vehicle_id": "VEH-0003", "customer_id": "C-0003", "make": "Calix", "model": "Coupe C", "year": 2022, "is_synthetic": True},
        {"vehicle_id": "VEH-0004", "customer_id": "C-0004", "make": "Dorian", "model": "SUV V", "year": 2020, "is_synthetic": True},
    ]
    repair_orders = [
        # Direct: waiting customer, needs the pump, planned 11:00-13:00 once the pump arrives (10:30).
        _repair_order("48213", "VEH-0001", "C-0001", [HERO_PART_ID], ["cooling_system"], 120,
                      "BAY-02", ts(base, "11:00"), ts(base, "17:00"), ts(base, "16:30", -1), 1, True),
        # Direct: same pump, tomorrow. Customer is OEM-only. Promise tomorrow 12:00.
        _repair_order("48240", "VEH-0002", "C-0002", [HERO_PART_ID], ["cooling_system"], 120,
                      "BAY-02", ts(base, "09:30", 1), ts(base, "12:00", 1), ts(base, "11:00", -1), 2, False),
        # Indirect: T03 works on it after the pump job. Target 15:00.
        _repair_order("48220", "VEH-0003", "C-0003", ["P-009"], ["engine"], 90,
                      "BAY-03", ts(base, "13:00"), ts(base, "15:00"), ts(base, "15:00", -1), 2, False),
        # Indirect: follows 48220. Target 16:00.
        _repair_order("48231", "VEH-0004", "C-0004", ["P-016"], ["diagnostics"], 60,
                      "BAY-03", ts(base, "14:30"), ts(base, "16:00"), ts(base, "08:10"), 2, False),
    ]
    return {"customers": customers, "vehicles": vehicles, "repair_orders": repair_orders}
