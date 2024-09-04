import aio_pika
from config import settings

async def get_rabbitmq_connection():

    try:
        # Conexión a RabbitMQ usando la URL configurada en settings
        connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        return connection
    except Exception as e:
        print(f"Error al conectarse a RabbitMQ: {e}")
        raise
