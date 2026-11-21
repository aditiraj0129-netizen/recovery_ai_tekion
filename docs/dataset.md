# Synthetic dataset

All records are **synthetic and illustrative**. No real dealership, customer, supplier or Tekion data is used.

## How it is built
`data/generator/generate_dataset.py` creates one dataset in two layers:

1. **Fixed hero block** (`hero.py`, no randomness): the four hero repair orders, their customers and vehicles.
2. **Seeded random block** (`random.Random(seed)`): the other 36 repair orders, scheduled so that skills, shifts, bays and parts are all consistent, plus inventory, appointments and customers.

Static reference data (locations, parts, technicians, bays, job templates) lives in `reference_data.py`.

The dataset is a snapshot of the dealership at **2026-03-10, immediately before the 09:40 hero disruption is applied**.

## Size (seed 42)
| Entity | Count |
|---|---|
| Repair orders | 40 |
| Technicians | 12 (T11 absent today) |
| Service bays | 7 |
| Parts (catalog) | 24 |
| Locations | 3 (Store A home, Store B, Store C) |
| Inventory rows | 72 (every part at every location) |
| Appointments | 28 (12 repair orders are walk-ins with no appointment) |
| Disruptions | 14 |

## Key rules the tests enforce
- Every foreign key points to a real entity.
- Assigned technician has every skill the job needs, the job is inside their shift, and the bay supports the work.
- No technician or bay is double-booked.
- `reserved_quantity <= quantity_on_hand`; Store A reservations equal open repair-order demand.
- Promise time is not before the scheduled end; statuses agree with the 09:40 clock.
- Same seed gives byte-identical output.

## Hero scenario in the data
| Item | Seeded as |
|---|---|
| RO 48213 | Waiting customer, needs pump P-001, T03 in BAY-02 11:00-13:00, promise today 17:00 |
| RO 48240 | Needs pump, T03 in BAY-02 tomorrow 09:30-11:30, promise tomorrow 12:00, appointment consent `pending`, customer prefers OEM |
| RO 48220 | T03 in BAY-03 13:00-14:30, target 15:00 |
| RO 48231 | T03 in BAY-03 14:30-15:30, target 16:00 |
| Pump at Store A | 0 on hand, order ETA today 10:30 (disruption D-001 moves it to tomorrow 10:00) |
| Pump at Store B | System says 1, `unverified`. Disruption D-002 (10:38) holds the true count of 0 |
| Pump at Store C | 1 on hand, `known`, longer transfer time than Store B |
| T03 | The only technician with `cooling_system`, so slipping the pump job pushes 48220 and 48231 |

D-001 and D-002 are seeded with status `scheduled`: they are dormant until a later milestone fires them.

## Output files (`data/generated/`)
`dealership_dataset.json` is the source of truth. The CSVs (`repair_orders`, `parts_inventory`, `technicians`, `bays`, `appointments`, `disruptions`) are flat views of it; list fields are joined with `|`.

## Plan and event history
The `plans`, `plan_events` and `undo_events` tables exist in the database schema but are empty. They are populated from Milestone 6 onward.
