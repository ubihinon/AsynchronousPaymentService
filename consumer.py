import asyncio
import json
import os

import aio_pika

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
QUEUE_NAME = "my_queue"


async def consume_messages():
    connection = None
    try:
        connection = await aio_pika.connect_robust(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            login=RABBITMQ_USER,
            password=RABBITMQ_PASS
        )
        async with connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=1)

            queue = await channel.declare_queue(QUEUE_NAME, durable=True)

            print(f"[*] Waiting for messages in {QUEUE_NAME}. To exit press CTRL+C")

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        print(f" [x] Received {message.body.decode()}")
                        try:
                            msg_data = json.loads(message.body.decode())
                            print(f"     Processed message: {msg_data['message']}")
                        except json.JSONDecodeError:
                            print(f"     Failed to decode JSON: {message.body.decode()}")
                        except KeyError:
                            print(f"     Message missing 'message' key: {message.body.decode()}")

    except aio_pika.exceptions.AMQPConnectionError as e:
        print(f"[ERROR] Could not connect to RabbitMQ: {e}")
        print("Retrying connection in 5 seconds...")
        await asyncio.sleep(5)
        await consume_messages()  # Retry connection
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
    finally:
        if connection and not connection.is_closed:
            await connection.close()


if __name__ == "__main__":
    asyncio.run(consume_messages())
