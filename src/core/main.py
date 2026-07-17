from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.broker import broker
from core.rabbitmq import payment_retry_3s_queue
from payments.constants import ROUTING_KEY_PAYMENT_RETRY
from core.rabbitmq.events import payment_dlx, payment_exchange, payment_retry_exchange
from core.logger_setup import setup_logging
from payments.api import router as payments_router

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.start()

    retry_exchange = await broker.declare_exchange(payment_retry_exchange)
    retry_queue = await broker.declare_queue(payment_retry_3s_queue)
    await retry_queue.bind(retry_exchange, routing_key=ROUTING_KEY_PAYMENT_RETRY)
    await broker.declare_exchange(payment_exchange)
    await broker.declare_exchange(payment_dlx)

    yield

    await broker.stop()

app = FastAPI(lifespan=lifespan)

app.include_router(payments_router)
