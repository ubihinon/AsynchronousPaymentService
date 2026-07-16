from typing import List

from pydantic import TypeAdapter, ValidationError
from sqlalchemy import select

from payments.constants import PAYMENTS_QUEUE
from payments.dtos.outbox import OutboxReadSchema
from payments.dtos.payment import PaymentReadSchema
from payments.models import Outbox
from payments.repositories.base_outbox import BaseOutboxRepository


class OutboxRepository(BaseOutboxRepository):
    async def create(self, payment_schema: PaymentReadSchema) -> OutboxReadSchema:
        outbox_record = Outbox(
            event_type=PAYMENTS_QUEUE,
            aggregate_type="Payment",
            aggregate_id=payment_schema.id,
            payload=payment_schema.model_dump(mode='json')
        )
        self.session.add(outbox_record)
        await self.session.flush()
        return OutboxReadSchema.model_validate(outbox_record)

    async def get_new(self) -> List[OutboxReadSchema]:
        query = select(Outbox).where(
            Outbox.processed_at == None
        )
        result = await self.session.execute(query)
        outbox_records = result.scalars().all()

        try:
            list_adapter = TypeAdapter(List[OutboxReadSchema])
            outbox_records_schemas: List[OutboxReadSchema] = list_adapter.validate_python(outbox_records)
            print("Validation successful!")
            return outbox_records_schemas
        except ValidationError as e:
            print("Validation failed:")
            print(e.json(indent=2))

        return []
