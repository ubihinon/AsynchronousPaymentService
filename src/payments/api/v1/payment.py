import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from payments.api.utils import hash_request_payload
from payments.dependencies import get_payment_service
from payments.exceptions import IdempotencyKeyException
from payments.schemas.requests import PaymentCreateRequestSchema
from payments.schemas.responses import PaymentGetResponseSchema, PaymentResponseSchema
from payments.services.payment import PaymentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("", status_code=status.HTTP_202_ACCEPTED, response_model=PaymentResponseSchema)
async def create_payment(
    request_data: PaymentCreateRequestSchema,
    payment_service: Annotated[PaymentService, Depends(get_payment_service)],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key")]
) -> PaymentResponseSchema:
    try:
        payment, is_new = await payment_service.create(
            request_data,
            idempotency_key
        )

        if not is_new and payment.response_data:
            return PaymentResponseSchema.model_validate(payment.response_data)

        return PaymentResponseSchema.model_validate({
            "payment_id": payment.id,
            "status": payment.status,
            "created_at": payment.created_at
        })
    except IdempotencyKeyException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message
        )
    except Exception as e:
        logger.exception(f"Exception: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


@router.get("/{payment_id}", status_code=status.HTTP_200_OK, response_model=PaymentGetResponseSchema)
async def get_payment(
    payment_id: uuid.UUID,
    payment_service: Annotated[PaymentService, Depends(get_payment_service)],
) -> PaymentGetResponseSchema:
    try:
        payment = await payment_service.get(payment_id)
        return PaymentGetResponseSchema.model_validate(payment)
    except Exception as e:
        logger.exception(f"Exception: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )
