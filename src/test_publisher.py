import asyncio

from core.broker import broker
from payments.constants import PAYMENTS_QUEUE

# project_root = Path(__file__).parent.parent
# sys.path.insert(0, str(project_root / "src"))

async def main():

    await broker.start()

    await broker.publish(
        {
            "description": "Test payment",
            "webhook_url": "https://example.com/webhook",
            "price": 100,
        },
        queue=PAYMENTS_QUEUE,
    )

    print("Message sent")

    await broker.close()

if __name__ == "__main__":
    asyncio.run(main())
