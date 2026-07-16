import asyncio
import datetime
import logging
import random

from faststream import FastStream

from core.broker import broker
from core.database import async_session
from core.logger_setup import setup_logging
from payments.constants import PAYMENTS_QUEUE, PaymentStatus
from payments.dtos.payment import PaymentReadSchema


setup_logging()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app = FastStream(broker)


@broker.subscriber(PAYMENTS_QUEUE, retry=3)
async def handle_payment(payload: dict):
    payment_id = payload.get("payment_id")
    webhook_url = payload.get("webhook_url")

    logger.info(f"Processing payment {payment_id}")

    # Emulate processing (2-5 sec)
    await asyncio.sleep(random.uniform(2, 5))

    # Emulate success/failure (90% success)
    success = random.random() < 0.9
    status = PaymentStatus.SUCCEEDED if success else PaymentStatus.FAILED
    #
    # async with async_session() as session:
    #     query = (
    #         update(Payment)
    #         .where(Payment.id == uuid.UUID(payment_id))
    #         .values(status=status, processed_at=datetime.datetime.now(datetime.timezone.utc))
    #     )
    #     await session.execute(query)
    #     await session.commit()
    #
    # # Send Webhook
    # webhook_payload = {
    #     "payment_id": payment_id,
    #     "status": status,
    #     "processed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    # }

    # webhook_success = await send_webhook_with_retry(webhook_url, webhook_payload)
    # if not webhook_success:
    #     logger.error(f"Failed to deliver webhook for payment {payment_id} after retries")


# async def send_webhook_with_retry(url: str, payload: dict):
#     async with httpx.AsyncClient() as client:
#         for attempt in range(settings.WEBHOOK_RETRY_ATTEMPTS):
#             try:
#                 response = await client.post(url, json=payload, timeout=5.0)
#                 response.raise_for_status()
#                 logger.info(f"Webhook sent successfully to {url}")
#                 return True
#             except Exception as e:
#                 logger.warning(f"Webhook attempt {attempt + 1} failed: {e}")
#                 if attempt < settings.WEBHOOK_RETRY_ATTEMPTS - 1:
#                     await asyncio.sleep(settings.WEBHOOK_RETRY_DELAY_SECONDS * (2**attempt))
#         return False

#
# @broker.subscriber(PAYMENTS_QUEUE)
# async def process_order(payment: PaymentReadSchema):
#
#     logger.debug("DEBUG: Получен заказ")
#     logger.info("Получен заказ")
#     breakpoint()
#
#     logger.info(payment.id)
#     logger.info(payment.description)
#     logger.info(payment.webhook_url)
#     logger.info(payment.price)
#
#     logger.info("Обработка завершена")

# import asyncio
# import json
# import os
#
# import aio_pika
#
# RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
# RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
# RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
# RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
# QUEUE_NAME = "my_queue"
#
#
# async def consume_messages():
#     connection = None
#     try:
#         connection = await aio_pika.connect_robust(
#             host=RABBITMQ_HOST,
#             port=RABBITMQ_PORT,
#             login=RABBITMQ_USER,
#             password=RABBITMQ_PASS
#         )
#         async with connection:
#             channel = await connection.channel()
#             await channel.set_qos(prefetch_count=1)
#
#             queue = await channel.declare_queue(QUEUE_NAME, durable=True)
#
#             print(f"[*] Waiting for messages in {QUEUE_NAME}. To exit press CTRL+C")
#
#             async with queue.iterator() as queue_iter:
#                 async for message in queue_iter:
#                     async with message.process():
#                         print(f" [x] Received {message.body.decode()}")
#                         try:
#                             msg_data = json.loads(message.body.decode())
#                             print(f"     Processed message: {msg_data['message']}")
#                         except json.JSONDecodeError:
#                             print(f"     Failed to decode JSON: {message.body.decode()}")
#                         except KeyError:
#                             print(f"     Message missing 'message' key: {message.body.decode()}")
#
#     except aio_pika.exceptions.AMQPConnectionError as e:
#         print(f"[ERROR] Could not connect to RabbitMQ: {e}")
#         print("Retrying connection in 5 seconds...")
#         await asyncio.sleep(5)
#         await consume_messages()  # Retry connection
#     except Exception as e:
#         print(f"[ERROR] An unexpected error occurred: {e}")
#     finally:
#         if connection and not connection.is_closed:
#             await connection.close()
#
#
# if __name__ == "__main__":
#     asyncio.run(consume_messages())
