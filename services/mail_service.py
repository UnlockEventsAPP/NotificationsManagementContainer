import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

class MailService:
    def __init__(self):
        # Cargar las credenciales de Gmail desde las variables de entorno
        self.gmail_user = os.getenv('GMAIL_USER')
        self.gmail_password = os.getenv('GMAIL_PASSWORD')

    def send_email(self, subject, content, to_email, files=None):
        """
        Envía un correo electrónico utilizando el servidor SMTP de Gmail.

        :param subject: El asunto del correo.
        :param content: El cuerpo del correo en HTML.
        :param to_email: El destinatario del correo.
        :param files: Lista de archivos adjuntos en el formato [(bytes_data, filename)].
        """
        try:
            # Crear el mensaje de correo electrónico
            msg = MIMEMultipart()
            msg['From'] = self.gmail_user
            msg['To'] = to_email
            msg['Subject'] = subject

            # Adjuntar el contenido del correo en HTML
            msg.attach(MIMEText(content, 'html'))

            # Adjuntar archivos si los hay
            if files:
                for file_data, file_name in files:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(file_data)
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename={file_name}')
                    msg.attach(part)

            # Conectar al servidor SMTP de Gmail
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()  # Iniciar la conexión segura (TLS)
            server.login(self.gmail_user, self.gmail_password)

            # Enviar el correo
            server.sendmail(self.gmail_user, to_email, msg.as_string())
            server.quit()

            print(f"Correo enviado a {to_email}")
        except Exception as e:
            print(f"Error al enviar el correo: {str(e)}")
