"""Parts inventory endpoint (read-only). One row per part per location."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import InventoryItem
from app.schemas.dealership import InventoryOut

router = APIRouter(prefix="/api/inventory", tags=["inventory"])


def _to_out(item: InventoryItem) -> InventoryOut:
    return InventoryOut(
        part_id=item.part_id,
        part_name=item.part.part_name,
        part_type=item.part.part_type,
        location_id=item.location_id,
        location_name=item.location.name,
        supplier_id=item.supplier_id,
        quantity_on_hand=item.quantity_on_hand,
        reserved_quantity=item.reserved_quantity,
        available_quantity=item.quantity_on_hand - item.reserved_quantity,
        expected_arrival=item.expected_arrival,
        stock_confidence=item.stock_confidence,
        unit_cost=item.unit_cost,
        is_synthetic=item.is_synthetic,
    )


@router.get("", response_model=list[InventoryOut])
def list_inventory(part_id: str | None = None, location_id: str | None = None, db: Session = Depends(get_db)):
    query = (
        select(InventoryItem)
        .options(joinedload(InventoryItem.part), joinedload(InventoryItem.location))
        .order_by(InventoryItem.part_id, InventoryItem.location_id)
    )
    if part_id:
        query = query.where(InventoryItem.part_id == part_id)
    if location_id:
        query = query.where(InventoryItem.location_id == location_id)
    return [_to_out(item) for item in db.scalars(query).all()]
