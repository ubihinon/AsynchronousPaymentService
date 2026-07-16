import asyncio
import datetime
import logging
import random

from faststream import FastStream

from core.broker import broker
from core.database import async_session
from core.logger_setup import setup_logging
from payments.constants import PAYMENTS_QUEUE, PaymentStatus
from payments.dtos.payment import PaymentReadSchema
from payments.repositories import OutboxRepository, PaymentRepository
from payments.services.payment import PaymentService
from payments.utils import send_webhook_with_retry

setup_logging()

logger = logging.getLogger(__name__)

app = FastStream(broker)


@broker.subscriber(PAYMENTS_QUEUE)
async def handle_payment(payload: PaymentReadSchema):
    logger.info(f"Processing payment with id {payload.id}")

    await asyncio.sleep(random.uniform(2, 5))

    success = random.random() < 0.9
    status = PaymentStatus.SUCCEEDED if success else PaymentStatus.FAILED

    async with async_session() as session:
        payment_service = PaymentService(
            session,
            payment_repository=PaymentRepository(session),
            outbox_repository=OutboxRepository(session)
        )

        payload.status = status
        payload.handled_at = datetime.datetime.now(datetime.UTC)

        updated_payload = await payment_service.update(payload)
        logger.info(f"Processed payment with id {payload.id}")
        logger.info(f"UPDATED PAYLOAD: {updated_payload}")

    webhook_payload = {
        "payment_id": payload.id,
        "status": status,
        "processed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }

    webhook_success = await send_webhook_with_retry(payload.webhook_url, webhook_payload)
    if not webhook_success:
        logger.error(f"Failed to deliver webhook for payment {payload.id} after retries")
