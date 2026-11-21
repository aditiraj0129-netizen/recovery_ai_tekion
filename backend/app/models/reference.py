"""Reference data: suppliers, locations, parts, inventory, customers, vehicles."""

from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    supplier_type: Mapped[str] = mapped_column(String(30))  # oem | dealer_store
    is_synthetic: Mapped[bool] = mapped_column(default=True)


class Location(Base):
    """A store or warehouse that can hold stock (Store A is the home dealership)."""

    __tablename__ = "locations"

    location_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    supplier_id: Mapped[str | None] = mapped_column(ForeignKey("suppliers.supplier_id"))
    is_home: Mapped[bool] = mapped_column(default=False)
    transfer_time_minutes: Mapped[int] = mapped_column(default=0)
    transfer_cost: Mapped[float] = mapped_column(default=0.0)
    is_synthetic: Mapped[bool] = mapped_column(default=True)


class Part(Base):
    """Part catalog: one row per unique part."""

    __tablename__ = "parts"

    part_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    part_name: Mapped[str] = mapped_column(String(150))
    part_type: Mapped[str] = mapped_column(String(20), default="OEM")  # OEM | aftermarket
    unit_cost: Mapped[float] = mapped_column(default=0.0)
    is_synthetic: Mapped[bool] = mapped_column(default=True)


class InventoryItem(Base):
    """Stock of one part at one location (composite primary key)."""

    __tablename__ = "inventory"
    __table_args__ = (
        CheckConstraint("quantity_on_hand >= 0", name="ck_inv_qty_non_negative"),
        CheckConstraint("reserved_quantity >= 0", name="ck_inv_reserved_non_negative"),
        CheckConstraint(
            "reserved_quantity <= quantity_on_hand", name="ck_inv_reserved_le_on_hand"
        ),
    )

    part_id: Mapped[str] = mapped_column(ForeignKey("parts.part_id"), primary_key=True)
    location_id: Mapped[str] = mapped_column(
        ForeignKey("locations.location_id"), primary_key=True
    )
    supplier_id: Mapped[str | None] = mapped_column(ForeignKey("suppliers.supplier_id"))
    quantity_on_hand: Mapped[int] = mapped_column(default=0)
    reserved_quantity: Mapped[int] = mapped_column(default=0)
    expected_arrival: Mapped[datetime | None] = mapped_column(default=None)
    stock_confidence: Mapped[str] = mapped_column(String(20), default="known")
    unit_cost: Mapped[float] = mapped_column(default=0.0)
    is_synthetic: Mapped[bool] = mapped_column(default=True)

    part: Mapped[Part] = relationship()
    location: Mapped[Location] = relationship()


class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    part_preference: Mapped[str | None] = mapped_column(String(50), default=None)
    is_synthetic: Mapped[bool] = mapped_column(default=True)


class Vehicle(Base):
    __tablename__ = "vehicles"

    vehicle_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.customer_id"))
    make: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(50))
    year: Mapped[int]
    is_synthetic: Mapped[bool] = mapped_column(default=True)
