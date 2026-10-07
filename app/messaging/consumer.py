import asyncio
import logging

from faststream import FastStream
from faststream.exceptions import RejectMessage

from app.core.config import settings
from app.core.logging import configure_logging
from app.messaging.broker import broker
from app.messaging.retry import retry_delay
from app.messaging.topology import payments_queue
from app.schemas.events import PaymentCreatedEvent
from app.services.processor import PaymentProcessor

configure_logging()
logger = logging.getLogger(__name__)
app = FastStream(broker)
processor = PaymentProcessor()


@broker.subscriber(payments_queue)
async def process_payment(event: PaymentCreatedEvent) -> None:
    for attempt in range(1, settings.processing_max_attempts + 1):
        try:
            await processor.process(event.payment_id)
            logger.info(
                "payment_processed payment_id=%s event_id=%s attempt=%s",
                event.payment_id,
                event.event_id,
                attempt,
            )
            return
        except Exception as exc:
            logger.exception(
                "payment_processing_failed payment_id=%s event_id=%s attempt=%s/%s",
                event.payment_id,
                event.event_id,
                attempt,
                settings.processing_max_attempts,
            )
            if attempt >= settings.processing_max_attempts:
                logger.error("sending_to_dlq payment_id=%s error=%r", event.payment_id, exc)
                raise RejectMessage from exc

            await asyncio.sleep(retry_delay(attempt, settings.processing_retry_base_delay))
