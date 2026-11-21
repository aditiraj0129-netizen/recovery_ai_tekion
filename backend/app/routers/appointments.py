"""Appointment endpoints (read-only)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Appointment
from app.schemas.dealership import AppointmentOut, ConsentStatus

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


@router.get("", response_model=list[AppointmentOut])
def list_appointments(
    consent_status: ConsentStatus | None = None,
    ro_id: str | None = None,
    db: Session = Depends(get_db),
):
    query = select(Appointment).order_by(Appointment.scheduled_at, Appointment.ro_id)
    if consent_status:
        query = query.where(Appointment.consent_status == consent_status)
    if ro_id:
        query = query.where(Appointment.ro_id == ro_id)
    return db.scalars(query).all()


@router.get("/{appointment_id}", response_model=AppointmentOut)
def get_appointment(appointment_id: str, db: Session = Depends(get_db)):
    appointment = db.get(Appointment, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail=f"Appointment {appointment_id} not found")
    return appointment
