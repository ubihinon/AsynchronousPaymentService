from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.broker import broker
from core.rabbitmq import payment_retry_queue_1, payment_retry_queue_2, payment_retry_queue_3
from payments.constants import PAYMENT_RETRY_ROUTING_KEYS
from core.rabbitmq.events import payment_dlx, payment_exchange, payment_retry_exchange
from core.logger_setup import setup_logging
from payments.api import router as payments_router

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.start()

    retry_exchange = await broker.declare_exchange(payment_retry_exchange)
    for queue_obj, routing_key in zip(
        [payment_retry_queue_1, payment_retry_queue_2, payment_retry_queue_3],
        PAYMENT_RETRY_ROUTING_KEYS,
    ):
        retry_queue = await broker.declare_queue(queue_obj)
        await retry_queue.bind(retry_exchange, routing_key=routing_key)

    await broker.declare_exchange(payment_exchange)
    await broker.declare_exchange(payment_dlx)

    yield

    await broker.stop()

app = FastAPI(lifespan=lifespan)

app.include_router(payments_router)
