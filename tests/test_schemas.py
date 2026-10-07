from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.models.payment import Currency
from app.schemas.payment import PaymentCreate


def test_payment_create_accepts_valid_payload() -> None:
    payload = PaymentCreate(
        amount=Decimal("199.90"),
        currency=Currency.RUB,
        description="Order #42",
        metadata={"order_id": 42},
        webhook_url="https://example.com/webhooks/payment",
    )
    assert payload.amount == Decimal("199.90")


def test_payment_create_rejects_non_positive_amount() -> None:
    with pytest.raises(ValidationError):
        PaymentCreate(
            amount=Decimal("0"),
            currency=Currency.USD,
            description="Invalid",
            webhook_url="https://example.com/webhooks/payment",
        )
