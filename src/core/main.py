import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.broker import broker
from core.logger_setup import setup_logging
from payments.api import router as payments_router
logger = logging.getLogger(__name__)


setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.start()

    yield

    await broker.stop()
# alembic revision --autogenerate -m "add payment"
app = FastAPI(lifespan=lifespan)

app.include_router(payments_router)
