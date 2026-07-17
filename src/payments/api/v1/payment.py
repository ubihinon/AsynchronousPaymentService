import logging
import uuid
from typing import Annotated

from asyncpg import NumericValueOutOfRangeError
from fastapi import APIRouter, Depends, Header, HTTPException, status

from payments.dependencies import get_payment_service, verify_api_key
from payments.exceptions import IdempotencyKeyException
from payments.schemas.requests import PaymentCreateRequestSchema
from payments.schemas.responses import PaymentGetResponseSchema, PaymentResponseSchema
from payments.services.payment import PaymentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post(
    "", status_code=status.HTTP_202_ACCEPTED,
    response_model=PaymentResponseSchema,
    dependencies=[Depends(verify_api_key)],
)
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
    except NumericValueOutOfRangeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be between less than 99999999.99"
        )
    except Exception as e:
        logger.exception(f"Exception: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


@router.get(
    "/{payment_id}",
    status_code=status.HTTP_200_OK,
    response_model=PaymentGetResponseSchema,
    dependencies=[Depends(verify_api_key)],
)
async def get_payment(
    payment_id: uuid.UUID,
    payment_service: Annotated[PaymentService, Depends(get_payment_service)],
) -> PaymentGetResponseSchema:
    try:
        payment = await payment_service.get(payment_id)
        if payment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
        return PaymentGetResponseSchema.model_validate(payment)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Exception: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )
