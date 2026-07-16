import asyncio
import logging

from faststream.rabbit import RabbitBroker

from core.database import async_session
from core.settings import settings
from payments.repositories import OutboxRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def process_outbox():
    broker = RabbitBroker(settings.RABBITMQ_URL)
    await broker.connect()

    logger.info("Outbox worker started")
    while True:
        logger.info("Outbox worker started")
        await asyncio.sleep(1)
        async with async_session() as session:
            outbox_repository = OutboxRepository(session)
            # Select unprocessed events
            # stmt = select(Outbox).where(Outbox.processed == False).limit(10)
            # result = await session.execute(stmt)
            # events = result.scalars().all()
            outbox = await outbox_repository.get_new()
            print()
            # for event in events:
            #     try:
            #         # Publish to RabbitMQ
            #         await broker.publish(
            #             message=event.payload,
            #             queue="payments.new",
            #         )
            #
            #         # Mark as processed
            #         event.processed = True
            #         logger.info(f"Published event {event.id} to RabbitMQ")
            #     except Exception as e:
            #         logger.error(f"Failed to publish event {event.id}: {e}")

            await session.commit()

        await asyncio.sleep(1)  # Polling interval


if __name__ == "__main__":
    asyncio.run(process_outbox())
