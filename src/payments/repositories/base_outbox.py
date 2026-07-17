import uuid
from abc import ABC, abstractmethod
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from payments.dtos.outbox import OutboxReadSchema
from payments.dtos.payment import PaymentMessageSchema


class BaseOutboxRepository(ABC):
    def __init__(self, session: AsyncSession):
        self.session = session

    @abstractmethod
    async def create(self, payment: PaymentMessageSchema) -> OutboxReadSchema:
        pass

    @abstractmethod
    async def get_new(self) -> List[OutboxReadSchema]:
        pass

    @abstractmethod
    async def update_processed_at(self, outbox_id: uuid.UUID) -> OutboxReadSchema:
        pass
