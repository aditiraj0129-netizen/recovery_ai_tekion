# Recovery AI

> Decision support for dealership service departments: when one part is late, show which customer promises are at risk and how to recover them.

**Status: Milestone 1 in progress (foundation only).** The full README will be written at the end of Milestone 1.

All data in this project is **synthetic and illustrative**. Recovery AI is a proposed specialist layer, not an existing Tekion feature, and has no Tekion ARC integration.

## Implemented so far
- Repository structure
- FastAPI backend scaffold with `GET /api/health`
- SQLAlchemy database models (schema only, no data yet)

## Not implemented yet
Synthetic data generator, read endpoints, dashboard, disruption detection, optimization, simulation, LLM parsing, safe undo.

## Run the backend
```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
uvicorn app.main:app --reload
```
Then open http://127.0.0.1:8000/api/health and http://127.0.0.1:8000/docs.

## Run the tests
```bash
cd backend && source .venv/bin/activate && pytest -v
```
