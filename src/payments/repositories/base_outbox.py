import uuid
from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from payments.dtos.outbox import OutboxReadSchema


class BaseOutboxRepository(ABC):
    def __init__(self, session: AsyncSession):
        self.session = session

    @abstractmethod
    async def create(self, schema: BaseModel) -> OutboxReadSchema:
        pass

    @abstractmethod
    async def get_new(self) -> List[OutboxReadSchema]:
        pass

    @abstractmethod
    async def update_processed_at(self, outbox_id: uuid.UUID) -> OutboxReadSchema:
        pass
