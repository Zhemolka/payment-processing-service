import asyncio
import random
from dataclasses import dataclass
from decimal import Decimal

from app.models.payment import Currency


@dataclass(slots=True, frozen=True)
class GatewayResult:
    succeeded: bool


class PaymentGateway:
    async def process(
        self,
        *,
        payment_id: str,
        idempotency_key: str,
        amount: Decimal,
        currency: Currency,
    ) -> GatewayResult:
        # payment_id/idempotency_key are intentionally part of the gateway contract.
        # A real provider should receive one of them as its own idempotency key.
        del payment_id, idempotency_key, amount, currency
        await asyncio.sleep(random.uniform(2, 5))
        return GatewayResult(succeeded=random.random() < 0.9)
