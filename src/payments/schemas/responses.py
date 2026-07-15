import datetime
import decimal
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict

from payments.constants import CurrencyEnum, PaymentStatus


class PaymentResponseSchema(BaseModel):
    payment_id: uuid.UUID
    status: PaymentStatus
    created_at: datetime.datetime


class PaymentGetResponseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: uuid.UUID
    price: decimal.Decimal
    currency: CurrencyEnum
    description: str
    meta_data: dict
    status: PaymentStatus
    created_at: datetime.datetime
    handled_at: Optional[datetime.datetime] = None
