import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.payments import router as payments_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import engine
from app.messaging.broker import broker
from app.messaging.outbox_publisher import run_outbox_publisher
from app.messaging.topology import payments_dead_queue, payments_queue

configure_logging()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await broker.connect()
    await broker.declare_queue(payments_dead_queue)
    await broker.declare_queue(payments_queue)
    stop_event = asyncio.Event()
    publisher_task = asyncio.create_task(run_outbox_publisher(stop_event))
    try:
        yield
    finally:
        stop_event.set()
        await publisher_task
        await broker.close()
        await engine.dispose()


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.include_router(payments_router)


@app.get("/health", include_in_schema=False)
async def health() -> dict[str, str]:
    return {"status": "ok"}
