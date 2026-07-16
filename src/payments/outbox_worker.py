import asyncio
import logging

from core.broker import broker
from core.database import async_session
from core.logger_setup import setup_logging
from payments.repositories import OutboxRepository
from payments.services.outbox import OutboxService

setup_logging()

logger = logging.getLogger(__name__)


async def process_outbox():
    await broker.connect()

    logger.info("Outbox worker started")
    while True:
        await asyncio.sleep(1)
        async with async_session() as session:
            outbox_service = OutboxService(session, OutboxRepository(session))
            await outbox_service.send_new_events()

        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(process_outbox())
