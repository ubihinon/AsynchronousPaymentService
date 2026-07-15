import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status

from payments.api.utils import hash_request_payload
from payments.dependencies import get_payment_service
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
        request_payload_hash = hash_request_payload(request_data)

        existing_payment = await payment_service.get_by_idempotency_key(idempotency_key)
        if existing_payment:
            if existing_payment.request_payload_hash == request_payload_hash:
                if existing_payment.response_data:
                    return PaymentResponseSchema(**existing_payment.response_data)
                return PaymentResponseSchema.model_validate({
                    "payment_id": existing_payment.id,
                    "status": existing_payment.status,
                    "created_at": existing_payment.created_at
                })

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Idempotency key already used with a different request payload"
            )

        payment = await payment_service.create(
            request_data.price,
            request_data.currency,
            request_data.description,
            request_data.meta_data,
            request_data.webhook_url,
            idempotency_key,
            request_payload_hash,
        )

        response_data = PaymentResponseSchema.model_validate({
            "payment_id": payment.id,
            "status": payment.status,
            "created_at": payment.created_at
        })

        await payment_service.update_response_data(payment.id, response_data.model_dump(mode='json'))

        return response_data
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Exception: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


@router.get("/{payment_id}", status_code=status.HTTP_200_OK, response_model=PaymentGetResponseSchema)
async def create_payment(
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
