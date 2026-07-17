import asyncio
import datetime
import logging
import random

from faststream import AckPolicy, FastStream
from faststream.rabbit import RabbitMessage

from core.broker import broker
from core.database import async_session
from core.rabbitmq.events import payment_dlx, payment_exchange, payment_retry_exchange
from core.logger_setup import setup_logging
from core.rabbitmq.queues import payment_retry_10s_queue, payments_dead_queue, payments_queue
from payments.constants import PAYMENTS_QUEUE, PaymentStatus
from payments.dtos.payment import PaymentReadSchema
from payments.repositories import OutboxRepository, PaymentRepository
from payments.services.payment import PaymentService
from payments.utils import send_webhook_with_retry

setup_logging()

logger = logging.getLogger(__name__)

app = FastStream(broker)

MAX_RETRIES = 3


@app.after_startup
async def declare_retry_infrastructure():
    retry_exchange = await broker.declare_exchange(payment_retry_exchange)
    retry_queue = await broker.declare_queue(payment_retry_10s_queue)
    await retry_queue.bind(retry_exchange, routing_key="payment.events.retry.3s")


@broker.subscriber(
    queue=payments_queue,
    exchange=payment_exchange,
    ack_policy=AckPolicy.MANUAL,
)
async def handle_payment(payload: PaymentReadSchema, msg: RabbitMessage):
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
        logger.error(f"Payment {payload.id} failed (attempt {retries + 1}/{MAX_RETRIES + 1}). Error: {e}")

        if retries >= MAX_RETRIES:
            logger.error(f"Payment {payload.id} exceeded max retries, sending to DLQ")
            await broker.publish(
                payload,
                exchange=payment_dlx,
                routing_key="payment.failed",
                headers={"x-error": str(e), "x-failed-at": datetime.datetime.now().isoformat()}
            )
            await msg.ack()
        else:
            await msg.nack(requeue=False)


def get_retry_count(msg: RabbitMessage) -> int:
    headers = msg.headers or {}
    deaths = headers.get("x-death", [])
    for death in deaths:
        if death.get("queue") == PAYMENTS_QUEUE:
            return death.get("count", 0)
    return 0


@broker.subscriber(
    queue=payments_dead_queue,
    exchange=payment_dlx,
)
async def process_dead_message(payload: PaymentReadSchema):
    logger.error(f"Dead letter received for payment {payload.id}: {payload}")
