import datetime
import decimal
import uuid

from pydantic import BaseModel

from payments.constants import PaymentStatus


class PaymentRequestSchema(BaseModel):
    price: decimal.Decimal
    currency: str
    description: str
    meta_data: dict
    webhook_url: str


class PaymentResponseSchema(BaseModel):
    payment_id: uuid.UUID
    status: PaymentStatus
    created_at: datetime.datetime
