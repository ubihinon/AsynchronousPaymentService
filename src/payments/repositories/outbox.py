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
