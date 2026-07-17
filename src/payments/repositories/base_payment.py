import decimal
import uuid
from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from payments.dtos.payment import PaymentReadSchema
from payments.models.payment import Payment


class BasePaymentRepository(ABC):
    def __init__(self, session: AsyncSession):
        self.session = session

    @abstractmethod
    async def create(
        self, price: decimal.Decimal, currency: str, description: str, meta_data: dict, webhook_url: str,
        idempotency_key: str, request_payload_hash: str
    ) -> Payment:
        pass

    @abstractmethod
    async def update(self, payment_schema: PaymentReadSchema) -> Payment | None:
        pass

    @abstractmethod
    async def update_response_data(self, payment_id: uuid.UUID, response_data: dict) -> Payment | None:
        pass

    @abstractmethod
    async def get_by_idempotency_key(self, idempotency_key: str) -> Payment | None:
        pass

    @abstractmethod
    async def get(self, payment_id: uuid.UUID) -> Payment | None:
        pass
