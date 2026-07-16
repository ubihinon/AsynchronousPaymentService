import logging

from sqlalchemy.ext.asyncio import AsyncSession

from core.broker import broker
from payments.constants import PAYMENTS_QUEUE
from payments.repositories.base_outbox import BaseOutboxRepository

logger = logging.getLogger(__name__)


class OutboxService:
    def __init__(self, session: AsyncSession, repository: BaseOutboxRepository):
        self.session = session
        self.repository = repository

    async def send_new_events(self):
        try:
            events = await self.repository.get_new()
            for event in events:
                try:
                    await broker.publish(
                        message=event.payload,
                        queue=PAYMENTS_QUEUE,
                    )

                    await self.repository.update_processed_at(event.id)
                    logger.info(f"Published event {event.id} to RabbitMQ")
                except Exception as e:
                    logger.error(f"Failed to publish event {event.id}: {e}")

            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            logger.error(e)
            raise
