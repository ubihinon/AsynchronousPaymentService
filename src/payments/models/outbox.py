import datetime
import uuid
from typing import Any, Dict, Optional

from sqlalchemy import DateTime, func, JSON, String, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base


class Outbox(Base):
    __tablename__ = "outbox"
    __table_args__ = {"extend_existing": True}

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid7)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    aggregate_type: Mapped[str] = mapped_column(String(50), nullable=False)
    aggregate_id: Mapped[uuid.UUID] = mapped_column(UUID, nullable=False)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    processed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
