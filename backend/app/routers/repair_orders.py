"""Repair order endpoints (read-only)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import RepairOrder
from app.schemas.dealership import RepairOrderOut, RepairOrderStatus

router = APIRouter(prefix="/api/repair-orders", tags=["repair orders"])


def _base_query():
    # selectinload fetches the child rows (parts, skills) in one extra query, not one per order.
    return (
        select(RepairOrder)
        .options(selectinload(RepairOrder.parts), selectinload(RepairOrder.skills))
        .order_by(RepairOrder.ro_id)
    )


@router.get("", response_model=list[RepairOrderOut])
def list_repair_orders(
    status: RepairOrderStatus | None = None,
    assigned_technician_id: str | None = None,
    db: Session = Depends(get_db),
):
    query = _base_query()
    if status:
        query = query.where(RepairOrder.status == status)
    if assigned_technician_id:
        query = query.where(RepairOrder.assigned_technician_id == assigned_technician_id)
    return db.scalars(query).all()


@router.get("/{ro_id}", response_model=RepairOrderOut)
def get_repair_order(ro_id: str, db: Session = Depends(get_db)):
    repair_order = db.scalars(_base_query().where(RepairOrder.ro_id == ro_id)).first()
    if repair_order is None:
        raise HTTPException(status_code=404, detail=f"Repair order {ro_id} not found")
    return repair_order
