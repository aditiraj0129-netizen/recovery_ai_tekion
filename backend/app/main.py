"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401  (registers tables on Base)
from app.config import get_settings
from app.database import Base, engine
from app.routers import (
    appointments,
    bays,
    dashboard,
    disruptions,
    health,
    inventory,
    repair_orders,
    technicians,
)
from app.seed import seed_if_empty

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    if settings.auto_seed:
        seed_if_empty(engine, settings.resolved_dataset_path)
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Decision support for dealership service recovery. All data is synthetic.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["GET"],
    allow_headers=["*"],
)
for module in (health, dashboard, repair_orders, technicians, bays, inventory, appointments, disruptions):
    app.include_router(module.router)
