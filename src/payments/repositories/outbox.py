import datetime
import logging
import uuid
from typing import List

from pydantic import TypeAdapter, ValidationError
from sqlalchemy import select

from core.settings import settings
from payments.constants import ROUTING_KEY_PAYMENT_CREATED
from payments.dtos.outbox import OutboxReadSchema
from payments.dtos.payment import PaymentReadSchema
from payments.models import Outbox
from payments.repositories.base_outbox import BaseOutboxRepository

logger = logging.getLogger(__name__)


class OutboxRepository(BaseOutboxRepository):
    async def create(self, payment_schema: PaymentReadSchema) -> OutboxReadSchema:
        outbox_record = Outbox(
            event_type=ROUTING_KEY_PAYMENT_CREATED,
            aggregate_type="Payment",
            aggregate_id=payment_schema.id,
            payload=payment_schema.model_dump(mode="json")
        )
        self.session.add(outbox_record)
        await self.session.flush()

        logger.info(f"Created outbox record with id {outbox_record.id}")

        return OutboxReadSchema.model_validate(outbox_record)

    async def get_new(self) -> List[OutboxReadSchema]:
        query = select(Outbox).where(
            Outbox.processed_at == None
        ).limit(settings.OUTBOX_LIMIT)
        result = await self.session.execute(query)
        outbox_records = result.scalars().all()

        try:
            list_adapter = TypeAdapter(List[OutboxReadSchema])
            outbox_records_schemas: List[OutboxReadSchema] = list_adapter.validate_python(outbox_records)

            logger.info(f"Found {len(outbox_records_schemas)} outbox records")

            return outbox_records_schemas
        except ValidationError as e:
            logger.error(e.json(indent=2))

        return []

    async def update_processed_at(self, outbox_id: uuid.UUID) -> OutboxReadSchema | None:
        query = select(Outbox).where(Outbox.id == outbox_id)
        result = await self.session.execute(query)
        outbox_record = result.scalar_one_or_none()

        if outbox_record is None:
            return None

        outbox_record.processed_at = datetime.datetime.now(datetime.timezone.utc)
        await self.session.flush()
        await self.session.refresh(outbox_record)

        logger.info(f"Updated outbox record with id {outbox_id}")

        return OutboxReadSchema.model_validate(outbox_record)
