import logging

from fastapi import FastAPI

from core.logger_setup import setup_logging
from payments.api import router as payments_router
logger = logging.getLogger(__name__)


setup_logging()

app = FastAPI()

app.include_router(payments_router)
