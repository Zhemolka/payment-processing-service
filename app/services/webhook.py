import httpx

from app.core.config import settings
from app.schemas.payment import WebhookPayload


class WebhookClient:
    async def send(self, url: str, payload: WebhookPayload) -> None:
        async with httpx.AsyncClient(timeout=settings.webhook_timeout) as client:
            response = await client.post(
                url,
                json=payload.model_dump(mode="json"),
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
