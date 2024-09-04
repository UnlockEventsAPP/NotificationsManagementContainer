import aio_pika
from utils.rabbitmq_connection import get_rabbitmq_connection


class BaseConsumer:
    queue_name = None

    async def consume(self):

        if not self.queue_name:
            raise ValueError("Debe definir `queue_name` en la clase hija.")

        # Obtener la conexión a RabbitMQ
        connection = await get_rabbitmq_connection()

        async with connection:
            channel = await connection.channel()

            # Declarar la cola
            queue = await channel.declare_queue(self.queue_name, durable=True)

            # Iniciar el consumo de mensajes
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    await self.process_message(message)

    async def process_message(self, message: aio_pika.IncomingMessage):

        raise NotImplementedError("Debe implementar `process_message` en la clase hija.")
