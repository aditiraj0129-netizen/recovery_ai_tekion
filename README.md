# Recovery AI

> Decision support for dealership service departments: when one part is late, show which customer promises are at risk and how to recover them.

**Status: Milestone 1 in progress (foundation only).** The full README will be written at the end of Milestone 1.

All data in this project is **synthetic and illustrative**. Recovery AI is a proposed specialist layer, not an existing Tekion feature, and has no Tekion ARC integration.

## Implemented so far
- Repository structure
- FastAPI backend with SQLAlchemy models (17 tables) and Pydantic response models
- Reproducible synthetic dataset generator (seeded) with the fixed hero scenario
- Loader that seeds SQLite from the generated dataset (automatic on first start)
- Read-only API endpoints (see below)
- Dataset integrity, seeding and API tests
- Read-only dashboard (React, Vite, TypeScript, Tailwind) showing repair orders, technicians, bays, parts inventory, appointments and disruptions

## Not implemented yet
Disruption detection, impact analysis, optimization, simulation, LLM parsing, safe undo.
The hero disruptions (D-001, D-002) exist in the data as dormant `scheduled` records; nothing fires them yet.

## Generate the synthetic dataset
From the repository root (any Python 3.12 environment works; the generator uses only the standard library):
```bash
python data/generator/generate_dataset.py --seed 42
```
This writes `data/generated/dealership_dataset.json` (single source of truth) and six CSV views.
The same seed always produces byte-identical files. See [docs/dataset.md](docs/dataset.md).

## Run the backend
```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
python -m uvicorn app.main:app --reload --port 8001
```
On first start the API creates `backend/recovery_ai.db` and loads the dataset into it.
To reset the database to the generated dataset at any time: `python -m app.seed`.
Then open http://127.0.0.1:8001/docs (interactive API documentation).

## Run the frontend
Needs Node.js 20 or newer. Start the backend first (above, port 8001), then in a second terminal:
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173. The dev server forwards every `/api/...` request to the backend on
port 8001, so no CORS setup is needed. To use a different backend address, copy
`frontend/.env.example` to `frontend/.env.local` and edit `VITE_API_TARGET`.

The dashboard has six tabs: Overview, Repair orders, Technicians & bays, Parts inventory,
Appointments and Disruptions. It only reads data; it never changes anything. If the backend is
not running it shows an error with a "Try again" button.

Production build check: `npm run build` (type-checks, then bundles into `frontend/dist`).

## API endpoints (all read-only, all `GET`)
| Endpoint | Purpose | Filters |
|---|---|---|
| `/api/health` | Service and database check | |
| `/api/dashboard` | Counts by status for the dashboard | |
| `/api/repair-orders`, `/api/repair-orders/{ro_id}` | Repair orders with parts and skills | `status`, `assigned_technician_id` |
| `/api/technicians`, `/api/technicians/{id}` | Technicians, skills, shifts | `availability` |
| `/api/bays`, `/api/bays/{id}` | Service bays | `status` |
| `/api/inventory` | Stock per part per location | `part_id`, `location_id` |
| `/api/appointments`, `/api/appointments/{id}` | Appointments and consent status | `consent_status`, `ro_id` |
| `/api/disruptions`, `/api/disruptions/{id}` | Seeded disruptions | `status` |

Unknown IDs return `404`; invalid filter values return `422`.

## Run the tests
```bash
cd backend && source .venv/bin/activate && python -m pytest -v
```
Tests use a throwaway database, so they never touch `backend/recovery_ai.db`.
