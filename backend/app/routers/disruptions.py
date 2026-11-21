"""Disruption endpoints (read-only in this milestone: nothing is injected or fired yet)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Disruption
from app.schemas.dealership import DisruptionOut, DisruptionStatus

router = APIRouter(prefix="/api/disruptions", tags=["disruptions"])


@router.get("", response_model=list[DisruptionOut])
def list_disruptions(status: DisruptionStatus | None = None, db: Session = Depends(get_db)):
    query = select(Disruption).order_by(Disruption.disruption_id)
    if status:
        query = query.where(Disruption.status == status)
    return db.scalars(query).all()


@router.get("/{disruption_id}", response_model=DisruptionOut)
def get_disruption(disruption_id: str, db: Session = Depends(get_db)):
    disruption = db.get(Disruption, disruption_id)
    if disruption is None:
        raise HTTPException(status_code=404, detail=f"Disruption {disruption_id} not found")
    return disruption
