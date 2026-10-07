def retry_delay(attempt: int, base_delay: float) -> float:
    """Return exponential delay after a failed 1-based attempt."""
    if attempt < 1:
        raise ValueError("attempt must be >= 1")
    return base_delay * (2 ** (attempt - 1))
