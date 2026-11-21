# Recovery AI

> Decision support for dealership service departments: when one part is late, show which customer promises are at risk and how to recover them.

**Status: Milestone 1 in progress (foundation only).** The full README will be written at the end of Milestone 1.

All data in this project is **synthetic and illustrative**. Recovery AI is a proposed specialist layer, not an existing Tekion feature, and has no Tekion ARC integration.

## Implemented so far
- Repository structure
- FastAPI backend scaffold with `GET /api/health`
- SQLAlchemy database models (17 tables)
- Reproducible synthetic dataset generator (seeded) with the fixed hero scenario
- Dataset integrity tests

## Not implemented yet
Loading the dataset into SQLite, read endpoints, dashboard, disruption detection, optimization, simulation, LLM parsing, safe undo.

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
python -m uvicorn app.main:app --reload
```
Then open http://127.0.0.1:8000/api/health and http://127.0.0.1:8000/docs.

## Run the tests
```bash
cd backend && source .venv/bin/activate && python -m pytest -v
```
