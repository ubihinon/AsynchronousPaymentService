import decimal
import uuid
from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from payments.dtos.payment import PaymentReadSchema


class BasePaymentRepository(ABC):
    def __init__(self, session: AsyncSession):
        self.session = session

    @abstractmethod
    async def create(
        self, price: decimal.Decimal, currency: str,  description: str, meta_data: dict, webhook_url: str,
        idempotency_key: str
    ) -> PaymentReadSchema:
        pass

    @abstractmethod
    async def update(self, payment_id: uuid.UUID) -> PaymentReadSchema | None:
        pass

    @abstractmethod
    async def get_by_idempotency_key(self, idempotency_key: str) -> PaymentReadSchema | None:
        pass
