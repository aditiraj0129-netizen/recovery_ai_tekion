"""Pydantic response models. These define exactly what the API returns."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

RepairOrderStatus = Literal["waiting", "in_progress", "blocked", "completed"]
TechnicianAvailability = Literal["available", "busy", "absent"]
BayStatus = Literal["available", "occupied"]
ConsentStatus = Literal["pending", "approved", "declined"]
DisruptionStatus = Literal["active", "scheduled", "resolved"]
Severity = Literal["low", "medium", "high", "critical"]
StockConfidence = Literal["known", "estimated", "unverified"]


class ORMModel(BaseModel):
    """Base class: lets Pydantic read values straight from SQLAlchemy objects."""

    model_config = ConfigDict(from_attributes=True)


class RepairOrderPartOut(ORMModel):
    part_id: str
    quantity: int


class RepairOrderOut(ORMModel):
    ro_id: str
    vehicle_id: str
    customer_id: str
    # The database stores these as child rows (relationships "parts" and "skills").
    required_parts: list[RepairOrderPartOut] = Field(validation_alias="parts")
    required_skills: list[str] = Field(validation_alias="skills")
    estimated_duration_minutes: int
    status: RepairOrderStatus
    promised_at: datetime
    priority: int
    assigned_technician_id: str | None
    assigned_bay_id: str | None
    scheduled_start: datetime | None
    scheduled_end: datetime | None
    created_at: datetime
    is_waiting_customer: bool
    is_synthetic: bool

    @field_validator("required_skills", mode="before")
    @classmethod
    def _skill_rows_to_names(cls, value):
        return sorted(getattr(item, "skill", item) for item in value)


class TechnicianOut(ORMModel):
    technician_id: str
    name: str
    skills: list[str]
    shift_start: datetime
    shift_end: datetime
    availability: TechnicianAvailability
    efficiency_factor: float
    is_synthetic: bool

    @field_validator("skills", mode="before")
    @classmethod
    def _skill_rows_to_names(cls, value):
        return sorted(getattr(item, "skill", item) for item in value)


class BayOut(ORMModel):
    bay_id: str
    supported_work: list[str]
    available_from: datetime
    available_until: datetime
    status: BayStatus
    is_synthetic: bool


class InventoryOut(BaseModel):
    part_id: str
    part_name: str
    part_type: str
    location_id: str
    location_name: str
    supplier_id: str | None
    quantity_on_hand: int
    reserved_quantity: int
    available_quantity: int  # on hand minus reserved
    expected_arrival: datetime | None
    stock_confidence: StockConfidence
    unit_cost: float
    is_synthetic: bool


class AppointmentOut(ORMModel):
    appointment_id: str
    ro_id: str
    scheduled_at: datetime
    promised_at: datetime
    customer_preference: str | None
    consent_status: ConsentStatus
    is_synthetic: bool


class DisruptionOut(ORMModel):
    disruption_id: str
    disruption_type: str
    affected_resource_type: str
    affected_resource_id: str
    start_time: datetime
    severity: Severity
    expected_duration_minutes: int | None
    status: DisruptionStatus
    related_part_id: str | None
    related_technician_id: str | None
    related_bay_id: str | None
    related_location_id: str | None
    description: str
    details: dict
    is_synthetic: bool


class DashboardResponse(BaseModel):
    scenario_date: str
    scenario_clock: str
    is_synthetic: bool = True
    repair_orders_total: int
    repair_orders_by_status: dict[str, int]
    waiting_customers: int
    technicians_total: int
    technicians_by_availability: dict[str, int]
    bays_total: int
    bays_by_status: dict[str, int]
    appointments_total: int
    appointments_by_consent: dict[str, int]
    disruptions_total: int
    disruptions_by_status: dict[str, int]
    parts_total: int
