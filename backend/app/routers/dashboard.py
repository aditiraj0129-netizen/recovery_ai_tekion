"""Dashboard summary: plain counts only. No risk scoring or recovery logic exists yet."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import Appointment, Bay, Disruption, Part, RepairOrder, Technician
from app.schemas.dealership import DashboardResponse

router = APIRouter(prefix="/api", tags=["dashboard"])


def _counts_by(db: Session, column) -> dict[str, int]:
    rows = db.execute(select(column, func.count()).group_by(column).order_by(column)).all()
    return {str(value): count for value, count in rows}


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db)) -> DashboardResponse:
    settings = get_settings()
    by_status = _counts_by(db, RepairOrder.status)
    by_availability = _counts_by(db, Technician.availability)
    by_bay_status = _counts_by(db, Bay.status)
    by_consent = _counts_by(db, Appointment.consent_status)
    by_disruption = _counts_by(db, Disruption.status)
    return DashboardResponse(
        scenario_date=settings.scenario_date,
        scenario_clock=settings.scenario_clock,
        repair_orders_total=sum(by_status.values()),
        repair_orders_by_status=by_status,
        waiting_customers=db.scalar(
            select(func.count()).select_from(RepairOrder).where(RepairOrder.is_waiting_customer.is_(True))
        ) or 0,
        technicians_total=sum(by_availability.values()),
        technicians_by_availability=by_availability,
        bays_total=sum(by_bay_status.values()),
        bays_by_status=by_bay_status,
        appointments_total=sum(by_consent.values()),
        appointments_by_consent=by_consent,
        disruptions_total=sum(by_disruption.values()),
        disruptions_by_status=by_disruption,
        parts_total=db.scalar(select(func.count()).select_from(Part)) or 0,
    )
