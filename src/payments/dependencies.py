from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from payments.repositories import OutboxRepository
from payments.repositories.payment import PaymentRepository
from payments.services.payment import PaymentService


async def get_payment_service(session: Annotated[AsyncSession, Depends(get_session)]) -> PaymentService:
    return PaymentService(
        session,
        payment_repository=PaymentRepository(session),
        outbox_repository=OutboxRepository(session)
    )
