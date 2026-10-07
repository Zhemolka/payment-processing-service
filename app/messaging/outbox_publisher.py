import asyncio
import logging
from datetime import UTC, datetime

from app.core.config import settings
from app.db.session import async_session_factory
from app.messaging.broker import broker
from app.repositories.outbox import OutboxRepository

logger = logging.getLogger(__name__)
repository = OutboxRepository()


async def publish_outbox_once() -> int:
    processed = 0
    async with async_session_factory() as session:
        async with session.begin():
            events = await repository.get_unpublished_for_update(
                session, limit=settings.outbox_batch_size
            )
            for event in events:
                try:
                    await broker.publish(
                        event.payload,
                        queue=event.routing_key,
                        persist=True,
                        message_id=str(event.id),
                        message_type=event.event_type,
                    )
                except Exception as exc:
                    event.attempts += 1
                    event.last_error = str(exc)[:2000]
                    logger.exception("outbox_publish_failed event_id=%s", event.id)
                else:
                    event.attempts += 1
                    event.last_error = None
                    event.published_at = datetime.now(UTC)
                    processed += 1
                    logger.info("outbox_published event_id=%s", event.id)
    return processed


async def run_outbox_publisher(stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        try:
            published = await publish_outbox_once()
        except Exception:
            logger.exception("outbox_loop_failed")
            published = 0

        if published == 0:
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=settings.outbox_poll_interval)
            except TimeoutError:
                pass
