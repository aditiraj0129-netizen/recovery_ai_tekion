"""Operational data: technicians, bays, repair orders, appointments, disruptions."""

from datetime import datetime

from sqlalchemy import JSON, CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Technician(Base):
    __tablename__ = "technicians"

    technician_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    shift_start: Mapped[datetime]
    shift_end: Mapped[datetime]
    availability: Mapped[str] = mapped_column(String(20), default="available")
    efficiency_factor: Mapped[float] = mapped_column(default=1.0)
    is_synthetic: Mapped[bool] = mapped_column(default=True)

    skills: Mapped[list["TechnicianSkill"]] = relationship(cascade="all, delete-orphan")


class TechnicianSkill(Base):
    __tablename__ = "technician_skills"

    technician_id: Mapped[str] = mapped_column(
        ForeignKey("technicians.technician_id"), primary_key=True
    )
    skill: Mapped[str] = mapped_column(String(50), primary_key=True)


class Bay(Base):
    __tablename__ = "bays"

    bay_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    supported_work: Mapped[list[str]] = mapped_column(JSON, default=list)
    available_from: Mapped[datetime]
    available_until: Mapped[datetime]
    status: Mapped[str] = mapped_column(String(20), default="available")
    is_synthetic: Mapped[bool] = mapped_column(default=True)


class RepairOrder(Base):
    __tablename__ = "repair_orders"
    __table_args__ = (
        CheckConstraint("promised_at >= created_at", name="ck_ro_promise_after_created"),
    )

    ro_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    vehicle_id: Mapped[str] = mapped_column(ForeignKey("vehicles.vehicle_id"))
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.customer_id"))
    estimated_duration_minutes: Mapped[int]
    status: Mapped[str] = mapped_column(String(20))  # waiting|in_progress|blocked|completed
    promised_at: Mapped[datetime]
    priority: Mapped[int] = mapped_column(default=3)
    assigned_technician_id: Mapped[str | None] = mapped_column(
        ForeignKey("technicians.technician_id")
    )
    assigned_bay_id: Mapped[str | None] = mapped_column(ForeignKey("bays.bay_id"))
    scheduled_start: Mapped[datetime | None] = mapped_column(default=None)
    scheduled_end: Mapped[datetime | None] = mapped_column(default=None)
    created_at: Mapped[datetime]
    is_waiting_customer: Mapped[bool] = mapped_column(default=False)
    is_synthetic: Mapped[bool] = mapped_column(default=True)

    parts: Mapped[list["RepairOrderPart"]] = relationship(cascade="all, delete-orphan")
    skills: Mapped[list["RepairOrderSkill"]] = relationship(cascade="all, delete-orphan")


class RepairOrderPart(Base):
    __tablename__ = "repair_order_parts"

    ro_id: Mapped[str] = mapped_column(ForeignKey("repair_orders.ro_id"), primary_key=True)
    part_id: Mapped[str] = mapped_column(ForeignKey("parts.part_id"), primary_key=True)
    quantity: Mapped[int] = mapped_column(default=1)


class RepairOrderSkill(Base):
    __tablename__ = "repair_order_skills"

    ro_id: Mapped[str] = mapped_column(ForeignKey("repair_orders.ro_id"), primary_key=True)
    skill: Mapped[str] = mapped_column(String(50), primary_key=True)


class Appointment(Base):
    """At most one appointment per RO; walk-in ROs have none."""

    __tablename__ = "appointments"

    appointment_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    ro_id: Mapped[str] = mapped_column(ForeignKey("repair_orders.ro_id"), unique=True)
    scheduled_at: Mapped[datetime]
    promised_at: Mapped[datetime]
    customer_preference: Mapped[str | None] = mapped_column(String(200), default=None)
    consent_status: Mapped[str] = mapped_column(String(20), default="pending")
    is_synthetic: Mapped[bool] = mapped_column(default=True)


class Disruption(Base):
    __tablename__ = "disruptions"

    disruption_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    disruption_type: Mapped[str] = mapped_column(String(40))
    affected_resource_type: Mapped[str] = mapped_column(String(20))  # part|technician|bay|inventory
    affected_resource_id: Mapped[str] = mapped_column(String(40))
    start_time: Mapped[datetime]
    severity: Mapped[str] = mapped_column(String(20))  # low|medium|high|critical
    expected_duration_minutes: Mapped[int | None] = mapped_column(default=None)
    status: Mapped[str] = mapped_column(String(20), default="active")  # active|scheduled|resolved
    related_part_id: Mapped[str | None] = mapped_column(ForeignKey("parts.part_id"))
    related_technician_id: Mapped[str | None] = mapped_column(
        ForeignKey("technicians.technician_id")
    )
    related_bay_id: Mapped[str | None] = mapped_column(ForeignKey("bays.bay_id"))
    related_location_id: Mapped[str | None] = mapped_column(
        ForeignKey("locations.location_id")
    )
    description: Mapped[str] = mapped_column(String(300), default="")
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    is_synthetic: Mapped[bool] = mapped_column(default=True)
