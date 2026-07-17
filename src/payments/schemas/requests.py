import decimal

from pydantic import BaseModel


class PaymentCreateRequestSchema(BaseModel):
    price: decimal.Decimal
    currency: str
    description: str
    meta_data: dict
    webhook_url: str
