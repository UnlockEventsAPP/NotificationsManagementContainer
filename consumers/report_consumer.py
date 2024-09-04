import json
import os
import pika
from dotenv import load_dotenv
from services.mail_service import MailService
from services.reports_processor import extract_sections, generate_excel
from io import BytesIO
import re

load_dotenv()

class ReportConsumer:
    def __init__(self):
        rabbitmq_url = os.getenv('RABBITMQ_URL')
        if not rabbitmq_url:
            raise ValueError("La variable de entorno RABBITMQ_URL no está definida.")

        print(f"Conectando a RabbitMQ con la URL: {rabbitmq_url}")

        # Conectarse a RabbitMQ usando la URL
        self.connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='report_notifications', durable=True)
        self.mail_service = MailService()

    def extract_emails_from_auth_data(self, auth_data):
        """
        Extrae correos electrónicos de la sección 'Auth Data' del contenido.
        """
        # Concatenar el contenido de la lista en un solo string
        if isinstance(auth_data, list):
            auth_data = "\n".join(auth_data)

        # Usar una expresión regular para encontrar los correos electrónicos
        email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        emails = re.findall(email_pattern, auth_data)
        return emails

    def callback(self, ch, method, properties, body):
        """
        Procesa los mensajes recibidos de la cola report_notifications.
        """
        print(f"Mensaje recibido: {body}")

        # Decodificar el mensaje
        report_data = json.loads(body)
        content = report_data['content']

        # Extraer las secciones del contenido
        accommodation_data, auth_data, events_data = extract_sections(content)

        # Extraer los correos electrónicos de la sección 'Auth Data'
        recipient_emails = self.extract_emails_from_auth_data(auth_data)

        if not recipient_emails:
            print(f"No se encontraron correos electrónicos en el reporte ID: {report_data['report_id']}")
            return

        # Generar el archivo Excel con las tres hojas
        excel_file = BytesIO()  # Utilizar BytesIO para manejar el archivo en memoria
        excel_file = generate_excel(accommodation_data, auth_data, events_data)

        # Verificar que el archivo Excel se generó correctamente
        if not excel_file:
            print(f"Error al generar el archivo Excel para el reporte ID: {report_data['report_id']}")
            return

        # Enviar el correo a cada correo electrónico extraído
        subject = f"Reporte {report_data['report_type'].capitalize()} (ID: {report_data['report_id']})"
        content = f"Adjuntamos el reporte generado con ID {report_data['report_id']}."

        for email in recipient_emails:
            try:
                # Enviar el correo con el archivo adjunto
                self.mail_service.send_email(
                    subject=subject,
                    content=content,
                    to_email=email,
                    files=[(excel_file.getvalue(), 'reporte_generado.xlsx')]
                )
                print(f"Correo enviado a {email} con el reporte ID: {report_data['report_id']}")
            except Exception as e:
                print(f"Error al enviar el correo a {email}: {str(e)}")

    def start_consuming(self):
        """
        Inicia la escucha de mensajes en la cola.
        """
        self.channel.basic_consume(
            queue='report_notifications',
            on_message_callback=self.callback,
            auto_ack=True
        )
        print("Esperando mensajes de reportes...")
        self.channel.start_consuming()
