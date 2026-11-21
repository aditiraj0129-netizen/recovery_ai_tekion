"""Service bay endpoints (read-only)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Bay
from app.schemas.dealership import BayOut, BayStatus

router = APIRouter(prefix="/api/bays", tags=["bays"])


@router.get("", response_model=list[BayOut])
def list_bays(status: BayStatus | None = None, db: Session = Depends(get_db)):
    query = select(Bay).order_by(Bay.bay_id)
    if status:
        query = query.where(Bay.status == status)
    return db.scalars(query).all()


@router.get("/{bay_id}", response_model=BayOut)
def get_bay(bay_id: str, db: Session = Depends(get_db)):
    bay = db.get(Bay, bay_id)
    if bay is None:
        raise HTTPException(status_code=404, detail=f"Bay {bay_id} not found")
    return bay
