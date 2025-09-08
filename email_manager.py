# Archivo: email_manager.py
# Ubicación: raíz del proyecto
# Descripción: Gestiona las operaciones de correo electrónico (SMTP e IMAP)

import smtplib
import imaplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import email
import base64


class EmailManager:
    def __init__(self):
        """Inicializa el gestor de correo electrónico"""
        # Definir configuraciones predeterminadas para proveedores comunes
        self.provider_configs = {
            'Gmail': {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'imap_server': 'imap.gmail.com',
                'imap_port': 993
            },
            'Outlook': {
                'smtp_server': 'smtp-mail.outlook.com',
                'smtp_port': 587,
                'imap_server': 'outlook.office365.com',
                'imap_port': 993
            },
            'Yahoo': {
                'smtp_server': 'smtp.mail.yahoo.com',
                'smtp_port': 587,
                'imap_server': 'imap.mail.yahoo.com',
                'imap_port': 993
            },
            'Otro': {
                'smtp_server': '',
                'smtp_port': 587,
                'imap_server': '',
                'imap_port': 993
            }
        }

    def get_provider_config(self, provider):
        """Obtiene la configuración para un proveedor específico"""
        return self.provider_configs.get(provider, self.provider_configs['Otro'])

    def test_smtp_connection(self, provider, email_addr, password):
        """Prueba la conexión SMTP con los parámetros proporcionados"""
        try:
            # Obtener configuración del proveedor
            config = self.get_provider_config(provider)
            server = config['smtp_server']
            port = config['smtp_port']

            # Asegurarse de que las credenciales sean strings y eliminar caracteres problemáticos
            # Para evitar problemas con caracteres especiales
            email_addr = self._sanitize_string(email_addr)
            password = self._sanitize_string(password)

            # Crear un contexto SSL
            context = ssl.create_default_context()

            # Conectar al servidor SMTP
            smtp = smtplib.SMTP(server, port)
            smtp.ehlo()
            smtp.starttls(context=context)
            smtp.ehlo()

            # Iniciar sesión con las credenciales
            smtp.login(email_addr, password)

            # Cerrar la conexión
            smtp.quit()

            return True

        except Exception as e:
            print(f"Error en la conexión SMTP: {str(e)}")
            return False

    def test_imap_connection(self, provider, email_addr, password):
        """Prueba la conexión IMAP con los parámetros proporcionados"""
        try:
            # Obtener configuración del proveedor
            config = self.get_provider_config(provider)
            server = config['imap_server']
            port = config['imap_port']

            # Asegurarse de que las credenciales sean strings y eliminar caracteres problemáticos
            email_addr = self._sanitize_string(email_addr)
            password = self._sanitize_string(password)

            # Crear un contexto SSL
            context = ssl.create_default_context()

            # Conectar al servidor IMAP
            imap = imaplib.IMAP4_SSL(server, port, ssl_context=context)

            # Iniciar sesión con las credenciales
            imap.login(email_addr, password)

            # Cerrar la conexión
            imap.logout()

            return True

        except Exception as e:
            print(f"Error en la conexión IMAP: {str(e)}")
            return False

    def send_email(self, provider, email_addr, password, to, subject, body):
        """Envía un correo electrónico a través de SMTP"""
        try:
            # Obtener configuración del proveedor
            config = self.get_provider_config(provider)
            server = config['smtp_server']
            port = config['smtp_port']

            # Sanitizar credenciales
            email_addr = self._sanitize_string(email_addr)
            password = self._sanitize_string(password)

            # Crear un mensaje MIME
            msg = MIMEMultipart()
            msg['From'] = email_addr
            msg['To'] = to
            msg['Subject'] = Header(subject, 'utf-8')

            # Adjuntar el cuerpo del mensaje con codificación UTF-8
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            # Crear un contexto SSL
            context = ssl.create_default_context()

            # Conectar al servidor SMTP
            with smtplib.SMTP(server, port) as smtp:
                smtp.ehlo()
                smtp.starttls(context=context)
                smtp.ehlo()

                # Iniciar sesión y enviar el correo
                smtp.login(email_addr, password)
                smtp.send_message(msg)

            return True

        except Exception as e:
            print(f"Error al enviar correo: {str(e)}")
            return False

    def read_emails(self, provider, email_addr, password, mailbox='INBOX', limit=10):
        """Lee correos de un buzón IMAP específico"""
        try:
            # Obtener configuración del proveedor
            config = self.get_provider_config(provider)
            server = config['imap_server']
            port = config['imap_port']

            # Sanitizar credenciales
            email_addr = self._sanitize_string(email_addr)
            password = self._sanitize_string(password)

            # Crear un contexto SSL
            context = ssl.create_default_context()

            # Conectar al servidor IMAP
            with imaplib.IMAP4_SSL(server, port, ssl_context=context) as imap:
                # Iniciar sesión
                imap.login(email_addr, password)

                # Seleccionar el buzón de correo
                imap.select(mailbox)

                # Buscar todos los correos no leídos
                status, messages = imap.search(None, 'UNSEEN')

                # Obtener la lista de IDs de mensajes
                message_ids = messages[0].split()

                # Limitar la cantidad de correos a procesar
                if limit > 0:
                    message_ids = message_ids[:limit]

                emails = []

                # Leer cada correo con codificación UTF-8
                for msg_id in message_ids:
                    status, data = imap.fetch(msg_id, '(RFC822)')
                    raw_email = data[0][1]
                    # Usar UTF-8 para decodificar el correo
                    email_message = email.message_from_bytes(raw_email, policy=email.policy.default)
                    emails.append(email_message)

                return emails

        except Exception as e:
            print(f"Error al leer correos: {str(e)}")
            return []

    def _sanitize_string(self, text):
        """Sanitiza un string para evitar problemas de codificación"""
        if not isinstance(text, str):
            return str(text)

        # Eliminar caracteres no imprimibles y espacios no separables
        text = ''.join(c for c in text if c.isprintable() and ord(c) != 0xA0)
        return text