import asyncio
import datetime
import logging
import random

from faststream import AckPolicy, FastStream
from faststream.rabbit import RabbitMessage

from core.broker import broker
from core.database import async_session
from core.rabbitmq.events import payment_dlx, payment_exchange
from core.logger_setup import setup_logging
from core.rabbitmq.queues import payments_dead_queue, payments_queue
from payments.constants import PaymentStatus
from payments.dtos.payment import PaymentReadSchema
from payments.repositories import OutboxRepository, PaymentRepository
from payments.services.payment import PaymentService
from payments.utils import send_webhook_with_retry

setup_logging()

logger = logging.getLogger(__name__)

app = FastStream(broker)


@broker.subscriber(
    queue=payments_queue,
    exchange=payment_exchange,
    # ack_policy=AckPolicy.NACK_ON_ERROR,
    ack_policy=AckPolicy.REJECT_ON_ERROR,
)
async def handle_payment(payload: PaymentReadSchema, msg: RabbitMessage):
        await asyncio.sleep(3)
        # await msg.reject(
        #     requeue=False
        # )
        raise Exception('TEST Exception !!!!!!!!!!!!!!!!!!!!!!!!!!!123456')
    # try:
        # logger.info(f"Processing payment with id {payload.id}")
        #
        # await asyncio.sleep(random.uniform(2, 5))
        #
        # success = random.random() < 0.1
        # status = PaymentStatus.SUCCEEDED if success else PaymentStatus.FAILED
        #
        # async with async_session() as session:
        #     payment_service = PaymentService(
        #         session,
        #         payment_repository=PaymentRepository(session),
        #         outbox_repository=OutboxRepository(session)
        #     )
        #
        #     payload.status = status
        #     payload.handled_at = datetime.datetime.now(datetime.UTC)
        #
        #     updated_payload = await payment_service.update(payload)
        #     logger.info(f"Processed payment with id {payload.id}")
        #
        # webhook_payload = {
        #     "payment_id": str(payload.id),
        #     "status": status,
        #     "processed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        # }
        #
        # webhook_success = await send_webhook_with_retry(payload.webhook_url, webhook_payload)
        # if not webhook_success:
        #     logger.error(f"Failed to deliver webhook for payment {payload.id} after retries")
    # except Exception:
    #     retries = get_retry_count(msg)
    #     logger.error(f"get_retry_count: {retries}=====================================================")
    #     if retries >= 3:
    #         await broker.publish(
    #             payload,
    #             exchange=payment_dlx,
    #             routing_key="payment.failed",
    #         )
    #         await msg.ack()
    #         return
    #     raise

def get_retry_count(msg: RabbitMessage) -> int:
    logger.info(f"RabbitMessage: {msg}")
    headers = msg.headers or {}
    deaths = headers.get(
        "x-death",
        []
    )

    if not deaths:
        return 0

    return sum(
        death.get("count", 0)
        for death in deaths
    )

#
# @broker.subscriber(
#     queue=payment_retry_10s_queue,
#     exchange=payment_retry_exchange,
# )
# async def retry_handler(payload: PaymentReadSchema):
#     pass


@broker.subscriber(
    queue=payments_dead_queue,
    exchange=payment_dlx,
)
async def process_dead_message(payload: PaymentReadSchema):
    logger.error(f"Processing dead message with id {payload.id}"
        "DEAD LETTER:",
        payload,
    )
