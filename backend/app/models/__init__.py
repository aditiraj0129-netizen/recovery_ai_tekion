"""Importing this package registers every table on Base.metadata."""

from app.models.history import Plan, PlanEvent, UndoEvent
from app.models.operations import (
    Appointment,
    Bay,
    Disruption,
    RepairOrder,
    RepairOrderPart,
    RepairOrderSkill,
    Technician,
    TechnicianSkill,
)
from app.models.reference import (
    Customer,
    InventoryItem,
    Location,
    Part,
    Supplier,
    Vehicle,
)

__all__ = [
    "Appointment", "Bay", "Customer", "Disruption", "InventoryItem", "Location",
    "Part", "Plan", "PlanEvent", "RepairOrder", "RepairOrderPart",
    "RepairOrderSkill", "Supplier", "Technician", "TechnicianSkill", "UndoEvent",
    "Vehicle",
]
