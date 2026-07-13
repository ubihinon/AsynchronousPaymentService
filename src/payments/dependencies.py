from payments.repositories.payment import PaymentRepository
from payments.services.payment import PaymentService


async def get_payment_service(session) -> PaymentService:
    return PaymentService(PaymentRepository(session))
