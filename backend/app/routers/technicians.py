"""Technician endpoints (read-only)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Technician
from app.schemas.dealership import TechnicianAvailability, TechnicianOut

router = APIRouter(prefix="/api/technicians", tags=["technicians"])


def _base_query():
    return select(Technician).options(selectinload(Technician.skills)).order_by(Technician.technician_id)


@router.get("", response_model=list[TechnicianOut])
def list_technicians(availability: TechnicianAvailability | None = None, db: Session = Depends(get_db)):
    query = _base_query()
    if availability:
        query = query.where(Technician.availability == availability)
    return db.scalars(query).all()


@router.get("/{technician_id}", response_model=TechnicianOut)
def get_technician(technician_id: str, db: Session = Depends(get_db)):
    technician = db.scalars(_base_query().where(Technician.technician_id == technician_id)).first()
    if technician is None:
        raise HTTPException(status_code=404, detail=f"Technician {technician_id} not found")
    return technician
