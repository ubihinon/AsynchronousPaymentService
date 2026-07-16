from abc import ABC, abstractmethod

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from payments.dtos.outbox import OutboxReadSchema


class BaseOutboxRepository(ABC):
    def __init__(self, session: AsyncSession):
        self.session = session

    @abstractmethod
    async def create(self, schema: BaseModel) -> OutboxReadSchema:
        pass
