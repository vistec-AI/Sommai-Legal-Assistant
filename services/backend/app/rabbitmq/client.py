from aio_pika import connect_robust, Message, ExchangeType, IncomingMessage
from asyncio import AbstractEventLoop
from pydantic import BaseModel
from app.custom_models.models import ChatJobInQueueMessage

class RabbitMQBroker:
    NO_MESSAGES = 1

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5672,
        username: str = "guest",
        password: str = "guest",
        exchange_name: str = "ex.default",
        queue_name: str = "q.default",
    ):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._exchange_name = exchange_name
        self._queue_name = queue_name
        self._routing_key = queue_name
        self._connection = None
        self._channel = None
        self._exchange = None
        self._queue = None

    async def connect(self, loop: AbstractEventLoop):
        if self._connection is not None and not self._connection.is_closed:
            await self.close()

        self._connection = await connect_robust(
            host=self._host,
            port=self._port,
            login=self._username,
            password=self._password,
            loop=loop,
        )

        # Creating channel
        self._channel = await self._connection.channel()
        # Consumer will take no more than N messages at the same time
        await self._channel.set_qos(prefetch_count=self.NO_MESSAGES)

        # Declaring exchange
        self._exchange = await self._channel.declare_exchange(
            self._exchange_name, ExchangeType.TOPIC, durable=True
        )

        # Declaring queue
        self._queue = await self._channel.declare_queue(self._queue_name, durable=True)

        # Binding queue
        await self._queue.bind(self._exchange, self._routing_key)

    async def consume(self) -> IncomingMessage:
        return await self._queue.get(timeout=30, fail=False)

    async def publish(self, message: ChatJobInQueueMessage):
        await self._exchange.publish(
            Message(
                body=bytes(message.model_dump_json(), encoding="utf-8"),
                content_type="application/json",
            ),
            routing_key=self._routing_key,
        )

    async def close(self):
        await self._connection.close()
