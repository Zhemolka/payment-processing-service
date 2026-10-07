import uuid
from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.outbox import OutboxEvent
from app.models.payment import Payment, PaymentStatus
from app.repositories.payment import PaymentRepository
from app.schemas.payment import PaymentCreate


class PaymentService:
    def __init__(self, repository: PaymentRepository | None = None) -> None:
        self.repository = repository or PaymentRepository()

    async def create_payment(
        self,
        session: AsyncSession,
        data: PaymentCreate,
        idempotency_key: str,
    ) -> tuple[Payment, bool]:
        try:
            async with session.begin():
                existing = await self.repository.get_by_idempotency_key(session, idempotency_key)
                if existing is not None:
                    return existing, False

                payment = Payment(
                    amount=data.amount,
                    currency=data.currency,
                    description=data.description,
                    metadata_=data.metadata,
                    status=PaymentStatus.PENDING,
                    idempotency_key=idempotency_key,
                    webhook_url=str(data.webhook_url),
                )
                session.add(payment)
                await session.flush()

                event_id = uuid.uuid4()
                session.add(
                    OutboxEvent(
                        id=event_id,
                        event_type="payment.created",
                        routing_key="payments.new",
                        payload={
                            "event_id": str(event_id),
                            "payment_id": str(payment.id),
                        },
                        created_at=datetime.now(UTC),
                    )
                )

            return payment, True
        except IntegrityError:
            await session.rollback()
            existing = await self.repository.get_by_idempotency_key(session, idempotency_key)
            if existing is None:
                raise
            return existing, False

    async def get_payment(self, session: AsyncSession, payment_id: uuid.UUID) -> Payment | None:
        return await self.repository.get(session, payment_id)
