import hashlib
import json
import logging
import httpx

from core.settings import settings
from payments.schemas.requests import PaymentCreateRequestSchema


logger = logging.getLogger(__name__)


def hash_request_payload(payload: PaymentCreateRequestSchema) -> str:
    canonical_payload = json.dumps(payload.model_dump(mode='json'), sort_keys=True).encode('utf-8')
    return hashlib.sha256(canonical_payload).hexdigest()


async def send_webhook_with_retry(url: str, payload: dict) -> bool:
    async with httpx.AsyncClient() as client:
        for attempt in range(settings.WEBHOOK_RETRY_ATTEMPTS):
            try:
                response = await client.post(url, json=payload, timeout=settings.WEBHOOK_TIMEOUT_SECONDS)
                response.raise_for_status()
                logger.info(f"Webhook sent successfully to {url}")
                return True
            except Exception as e:
                logger.warning(f"Webhook attempt {attempt + 1} failed: {e}")
                if attempt < settings.WEBHOOK_RETRY_ATTEMPTS - 1:
                    await asyncio.sleep(settings.WEBHOOK_RETRY_DELAY_SECONDS * (2 ** attempt))
        return False
