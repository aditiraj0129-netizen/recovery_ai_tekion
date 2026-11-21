"""Plan and event history tables. Schema only in Milestone 1: nothing writes here yet."""

from datetime import datetime

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Plan(Base):
    __tablename__ = "plans"

    plan_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    version: Mapped[int] = mapped_column(default=1)
    disruption_id: Mapped[str] = mapped_column(ForeignKey("disruptions.disruption_id"))
    parent_plan_id: Mapped[str | None] = mapped_column(ForeignKey("plans.plan_id"))
    affected_ro_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    assignments: Mapped[dict] = mapped_column(JSON, default=dict)
    feasibility: Mapped[str] = mapped_column(String(20), default="unknown")
    promise_protection: Mapped[float | None] = mapped_column(default=None)
    approval_status: Mapped[str] = mapped_column(String(20), default="pending")
    checkpoint_result: Mapped[dict | None] = mapped_column(JSON, default=None)
    created_at: Mapped[datetime]


class PlanEvent(Base):
    """Append-only audit log. idempotency_key makes repeated writes safe."""

    __tablename__ = "plan_events"

    event_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    plan_id: Mapped[str] = mapped_column(ForeignKey("plans.plan_id"))
    event_type: Mapped[str] = mapped_column(String(40))
    idempotency_key: Mapped[str] = mapped_column(String(80), unique=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime]


class UndoEvent(Base):
    """Reversal record pointing at the event it reverses."""

    __tablename__ = "undo_events"

    undo_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    plan_id: Mapped[str] = mapped_column(ForeignKey("plans.plan_id"))
    reverses_event_id: Mapped[str] = mapped_column(
        ForeignKey("plan_events.event_id"), unique=True
    )
    idempotency_key: Mapped[str] = mapped_column(String(80), unique=True)
    created_at: Mapped[datetime]
