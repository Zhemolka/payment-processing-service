# Test assignment checklist

| Requirement | Implementation |
|---|---|
| Payment model | `app/models/payment.py` |
| Outbox model | `app/models/outbox.py` |
| Alembic migrations | `alembic/versions/0001_initial.py` |
| `POST /api/v1/payments` | `app/api/routes/payments.py` |
| `GET /api/v1/payments/{payment_id}` | `app/api/routes/payments.py` |
| `X-API-Key` auth | `app/api/deps.py` |
| `Idempotency-Key` | unique DB constraint + `app/services/payment_service.py` |
| Atomic payment + outbox insert | `app/services/payment_service.py` |
| Outbox publisher | `app/messaging/outbox_publisher.py` |
| RabbitMQ `payments.new` | `app/messaging/topology.py` |
| One consumer handler | `app/messaging/consumer.py` |
| Gateway emulation 2–5 sec, 90/10 | `app/services/gateway.py` |
| Payment status update | `app/services/processor.py` |
| Webhook | `app/services/webhook.py` + `app/services/processor.py` |
| 3 retries + exponential backoff | `app/messaging/consumer.py` + `app/messaging/retry.py` |
| Dead Letter Queue | `payments.dead`, configured in `app/messaging/topology.py` |
| Async SQLAlchemy 2.0 | `app/db/session.py` + repositories |
| FastAPI + Pydantic v2 | `app/main.py`, `app/schemas/` |
| FastStream | `app/messaging/` |
| Docker Compose | `docker-compose.yml` |
| Documentation | `README.md` |
| Basic tests | `tests/` |
| CI | `.github/workflows/ci.yml` |
