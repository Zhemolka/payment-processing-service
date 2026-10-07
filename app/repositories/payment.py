import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment


class PaymentRepository:
    async def get(self, session: AsyncSession, payment_id: uuid.UUID) -> Payment | None:
        return await session.get(Payment, payment_id)

    async def get_for_update(
        self, session: AsyncSession, payment_id: uuid.UUID
    ) -> Payment | None:
        result = await session.execute(
            select(Payment).where(Payment.id == payment_id).with_for_update()
        )
        return result.scalar_one_or_none()

    async def get_by_idempotency_key(
        self, session: AsyncSession, idempotency_key: str
    ) -> Payment | None:
        result = await session.execute(
            select(Payment).where(Payment.idempotency_key == idempotency_key)
        )
        return result.scalar_one_or_none()
