import datetime
import decimal
import uuid

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
    webhook_url: str
    created_at: datetime.datetime
    handled_at: datetime.datetime
