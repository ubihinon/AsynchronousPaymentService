import datetime
import decimal
import uuid
from typing import Any, Dict, Optional

from sqlalchemy import DateTime, Enum, func, JSON, Numeric, String, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base
from payments.constants import CurrencyEnum, PaymentStatus


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = {"extend_existing": True}

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid7)
    price: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[CurrencyEnum] = mapped_column(Enum(CurrencyEnum), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    meta_data: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING, index=True
    )
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    request_payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    response_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    webhook_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    handled_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
