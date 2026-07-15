import datetime
import decimal
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict

from payments.constants import CurrencyEnum, PaymentStatus


class PaymentReadSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: uuid.UUID
    price: decimal.Decimal
    currency: CurrencyEnum
    description: str
    meta_data: dict
    status: PaymentStatus
    idempotency_key: str
    request_payload_hash: str
    response_data: dict | None
    webhook_url: str
    created_at: datetime.datetime
    handled_at: Optional[datetime.datetime] = None
