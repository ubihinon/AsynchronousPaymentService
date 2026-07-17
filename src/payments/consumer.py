import asyncio
import datetime
import logging
import random

from faststream import AckPolicy, FastStream
from faststream.rabbit import RabbitMessage

from core.broker import broker
from core.database import async_session
from core.settings import settings
from core.rabbitmq.events import payment_dlx, payment_exchange, payment_retry_exchange
from core.logger_setup import setup_logging
from core.rabbitmq.queues import payment_dead_queue, payments_queue
from payments.constants import PAYMENT_RETRY_ROUTING_KEYS, ROUTING_KEY_PAYMENT_FAILED, PaymentStatus
from payments.dtos.payment import PaymentMessageSchema
from payments.repositories import OutboxRepository, PaymentRepository
from payments.services.payment import PaymentService
from payments.utils import send_webhook_with_retry

setup_logging()

logger = logging.getLogger(__name__)

app = FastStream(broker)


@broker.subscriber(
    queue=payments_queue,
    exchange=payment_exchange,
    ack_policy=AckPolicy.MANUAL,
)
async def handle_payment(payload: PaymentMessageSchema, msg: RabbitMessage):
    try:
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

            await payment_service.update(payload)
            logger.info(f"Processed payment with id {payload.id}")

        webhook_payload = {
            "payment_id": str(payload.id),
            "status": status,
            "processed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

        webhook_success = await send_webhook_with_retry(payload.webhook_url, webhook_payload)
        if not webhook_success:
            logger.error(f"Failed to deliver webhook for payment {payload.id} after retries")

        await msg.ack()

    except Exception as e:
        retries = get_retry_count(msg)
        logger.error(
            f"Payment {payload.id} failed (attempt {retries + 1}/{settings.RABBITMQ_MAX_RETRIES + 1}). Error: {e}"
        )

        if retries >= settings.RABBITMQ_MAX_RETRIES:
            logger.error(f"Payment {payload.id} exceeded max retries, sending to DLQ")
            await broker.publish(
                payload,
                exchange=payment_dlx,
                routing_key=ROUTING_KEY_PAYMENT_FAILED,
                headers={"x-error": str(e), "x-failed-at": datetime.datetime.now().isoformat()}
            )
        else:
            await broker.publish(
                payload,
                exchange=payment_retry_exchange,
                routing_key=PAYMENT_RETRY_ROUTING_KEYS[retries],
                headers={"x-retry-count": retries + 1},
            )
        await msg.ack()


def get_retry_count(msg: RabbitMessage) -> int:
    headers = msg.headers or {}
    return int(headers.get("x-retry-count", 0))


@broker.subscriber(
    queue=payment_dead_queue,
    exchange=payment_dlx,
)
async def process_dead_message(payload: PaymentMessageSchema):
    logger.error(f"Dead letter received for payment {payload.id}: {payload}")

    if payload.status == PaymentStatus.PENDING:
        async with async_session() as session:
            payment_service = PaymentService(
                session,
                payment_repository=PaymentRepository(session),
                outbox_repository=OutboxRepository(session),
            )
            payload.status = PaymentStatus.FAILED
            payload.handled_at = datetime.datetime.now(datetime.UTC)
            await payment_service.update(payload)
