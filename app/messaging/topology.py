from faststream.rabbit import RabbitQueue

PAYMENTS_QUEUE_NAME = "payments.new"
PAYMENTS_DLQ_NAME = "payments.dead"

payments_queue = RabbitQueue(
    PAYMENTS_QUEUE_NAME,
    durable=True,
    arguments={
        "x-dead-letter-exchange": "",
        "x-dead-letter-routing-key": PAYMENTS_DLQ_NAME,
    },
)

payments_dead_queue = RabbitQueue(PAYMENTS_DLQ_NAME, durable=True)
