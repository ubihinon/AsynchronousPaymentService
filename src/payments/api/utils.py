import hashlib
import json

from payments.schemas.requests import PaymentCreateRequestSchema


def hash_request_payload(payload: PaymentCreateRequestSchema) -> str:
    canonical_payload = json.dumps(payload.model_dump(mode='json'), sort_keys=True).encode('utf-8')
    return hashlib.sha256(canonical_payload).hexdigest()
