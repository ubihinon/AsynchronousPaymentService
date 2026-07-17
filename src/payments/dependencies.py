from typing import Annotated

from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from core.database import get_session
from core.settings import settings
from payments.repositories import OutboxRepository
from payments.repositories.payment import PaymentRepository
from payments.services.payment import PaymentService


async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key")


async def get_payment_service(session: Annotated[AsyncSession, Depends(get_session)]) -> PaymentService:
    return PaymentService(
        session,
        payment_repository=PaymentRepository(session),
        outbox_repository=OutboxRepository(session)
    )
