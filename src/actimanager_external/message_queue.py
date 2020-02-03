import json

import aio_pika
import structlog

log = structlog.getLogger(__name__)


class MessageQueue:
    def __init__(self, config):
        self._host = config.rabbitmq.host
        self._port = config.rabbitmq.port
        self._username = config.rabbitmq.username
        self._password = config.rabbitmq.password
        self._queue_name = config.rabbitmq.queue_name

        self._queue = None

        self._log = log

    async def connect(self):
        self._connection = await aio_pika.connect_robust(
            (
                f"amqp://{self._username}:{self._password}@"
                f"{self._host}:{self._port}/"
            )
        )

        self._channel = await self._connection.channel()

        self._queue = await self._channel.declare_queue(self._queue_name)

        self._log = log.bind(queue=self._queue.name)

        self._log.debug("queue_declared")

    async def close(self):
        await self._channel.close()
        await self._connection.close()

    def _decode_message(self, message):
        try:
            json_body = message.body.decode("UTF-8")
        except Exception as exc:
            self._log.error("queue_decode_error", error=str(exc))
            return None

        try:
            body = json.loads(json_body)
        except json.JSONDecodeError as exc:
            self._log.error("queue_decode_json_error", error=str(exc))
            return None

        if "hostname" not in body:
            self._log.error("queue_decode_hostname_missing", message=str(body))

        return body

    async def recv(self):
        if not self._queue:
            raise RuntimeError("Message queue not connected")

        self._log.debug("queue_recv_start")

        try:
            message = await self._queue.get(timeout=5)
        except aio_pika.exceptions.QueueEmpty:
            self._log.debug("queue_recv_empty")
            return None

        self._log.debug(
            f"queue_recv_message_received", raw_message_body=str(message.body)
        )

        decoded_message = self._decode_message(message)
        self._log.info(f"queue_recv_message", message=str(decoded_message))

        self._log.debug(f"queue_recv_ack")
        await message.ack()

        self._log.debug(f"queue_recv_end")

        return decoded_message
