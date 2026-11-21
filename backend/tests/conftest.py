"""Shared fixtures: a throwaway SQLite database seeded from the generator (seed 42)."""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "data"))

from generator.generate_dataset import generate_dataset  # noqa: E402

from app.database import get_db, make_engine  # noqa: E402
from app.main import app  # noqa: E402
from app.seed import load_dataset, reset_database  # noqa: E402


@pytest.fixture(scope="session")
def dataset() -> dict:
    return generate_dataset(seed=42)


@pytest.fixture()
def db_engine(tmp_path, dataset):
    engine = make_engine(f"sqlite:///{tmp_path}/test_api.db")
    reset_database(engine)
    with Session(engine) as session:
        load_dataset(session, dataset)
        session.commit()
    yield engine
    engine.dispose()


@pytest.fixture()
def client(db_engine):
    """A test client wired to the throwaway database (startup events are not run)."""
    testing_session = sessionmaker(bind=db_engine, autoflush=False, expire_on_commit=False)

    def override_get_db():
        session = testing_session()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
