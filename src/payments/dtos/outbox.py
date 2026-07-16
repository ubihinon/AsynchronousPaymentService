import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict


class OutboxReadSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: uuid.UUID
    event_type: str
    aggregate_type: str
    aggregate_id: uuid.UUID
    payload: dict
    created_at: datetime.datetime
    processed_at: Optional[datetime.datetime] = None
