import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status

from payments.dependencies import get_payment_service
from payments.schemas.requests import PaymentRequestSchema, PaymentResponseSchema
from payments.services.payment import PaymentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("")
async def create_payment(
    request_data: PaymentRequestSchema,
    payment_service: Annotated[PaymentService, Depends(get_payment_service)],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key")],
) -> PaymentResponseSchema:
    try:
        payment = await payment_service.create(
            request_data.price,
            request_data.currency,
            request_data.description,
            request_data.meta_data,
            request_data.webhook_url,
            idempotency_key
        )
        return PaymentResponseSchema.model_validate({
            "payment_id": payment.id,
            "status": payment.status,
            "created_at": payment.created_at
        })
    except Exception as e:
        logger.exception(f"Exception: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )
