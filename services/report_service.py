import pika
import json

class ReportService:
    def __init__(self):
        # Conectar a RabbitMQ
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='report_notifications')

    def send_report_content(self, report_data):
        """
        Envía el contenido del reporte a través de RabbitMQ, incluyendo los correos de los destinatarios.
        """
        # Ejemplo de estructura del mensaje a enviar
        message = {
            'accommodation_data': report_data['accommodation_data'],
            'auth_data': report_data['auth_data'],
            'events_data': report_data['events_data'],
            'emails': report_data['emails']  # Lista de correos electrónicos a los que se enviará el reporte
        }

        # Enviar los datos a RabbitMQ
        self.channel.basic_publish(
            exchange='',
            routing_key='report_notifications',
            body=json.dumps(message)
        )
        print("Datos enviados a RabbitMQ con los correos electrónicos")

        # Cerrar la conexión
        self.connection.close()

