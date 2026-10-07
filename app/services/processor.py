import uuid
from datetime import UTC, datetime

from app.db.session import async_session_factory
from app.models.payment import PaymentStatus
from app.repositories.payment import PaymentRepository
from app.schemas.payment import WebhookPayload
from app.services.gateway import PaymentGateway
from app.services.webhook import WebhookClient


class PaymentProcessor:
    def __init__(
        self,
        repository: PaymentRepository | None = None,
        gateway: PaymentGateway | None = None,
        webhook_client: WebhookClient | None = None,
    ) -> None:
        self.repository = repository or PaymentRepository()
        self.gateway = gateway or PaymentGateway()
        self.webhook_client = webhook_client or WebhookClient()

    async def process(self, payment_id: uuid.UUID) -> None:
        # Phase 1: process the payment only once. FOR UPDATE prevents duplicate
        # outbox deliveries from executing the gateway concurrently.
        async with async_session_factory() as session:
            async with session.begin():
                payment = await self.repository.get_for_update(session, payment_id)
                if payment is None:
                    raise LookupError(f"Payment {payment_id} not found")

                if payment.status == PaymentStatus.PENDING:
                    result = await self.gateway.process(
                        payment_id=str(payment.id),
                        idempotency_key=payment.idempotency_key,
                        amount=payment.amount,
                        currency=payment.currency,
                    )
                    payment.status = (
                        PaymentStatus.SUCCEEDED if result.succeeded else PaymentStatus.FAILED
                    )
                    payment.processed_at = datetime.now(UTC)

        # Phase 2: deliver the webhook. Keeping a delivery timestamp makes the
        # handler safe when the same RabbitMQ message is delivered again.
        async with async_session_factory() as session:
            async with session.begin():
                payment = await self.repository.get_for_update(session, payment_id)
                if payment is None:
                    raise LookupError(f"Payment {payment_id} not found")

                if payment.webhook_delivered_at is not None:
                    return

                payload = WebhookPayload(
                    payment_id=payment.id,
                    status=payment.status,
                    amount=payment.amount,
                    currency=payment.currency,
                    processed_at=payment.processed_at,
                )
                await self.webhook_client.send(payment.webhook_url, payload)
                payment.webhook_delivered_at = datetime.now(UTC)
