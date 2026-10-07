import pytest

from app.messaging.retry import retry_delay


def test_exponential_retry_delay() -> None:
    assert retry_delay(1, 1.0) == 1.0
    assert retry_delay(2, 1.0) == 2.0
    assert retry_delay(3, 1.0) == 4.0


def test_retry_delay_rejects_invalid_attempt() -> None:
    with pytest.raises(ValueError):
        retry_delay(0, 1.0)
