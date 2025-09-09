# Archivo: email_manager.py
# Ubicación: raíz del proyecto
# Descripción: Gestiona las operaciones de correo electrónico (SMTP e IMAP) con sistema modular de casos

import smtplib
import imaplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header, decode_header
import email
import base64
from datetime import datetime, date
import email.utils
from case_handler import CaseHandler


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

        # Inicializar el manejador de casos
        self.case_handler = CaseHandler()

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

    def check_and_process_emails(self, provider, email_addr, password, search_titles, logger):
        """Función principal que revisa emails y procesa los que coinciden usando el sistema modular"""
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
                imap.select('INBOX')

                # Buscar emails del día de hoy no leídos
                today = date.today().strftime("%d-%b-%Y")
                status, messages = imap.search(None, f'UNSEEN SINCE "{today}"')

                # Obtener la lista de IDs de mensajes
                message_ids = messages[0].split()

                if not message_ids:
                    return  # No hay emails nuevos del día de hoy

                logger.log(f"Encontrados {len(message_ids)} emails no leídos del día de hoy", level="INFO")

                # Procesar cada email
                for msg_id in message_ids:
                    try:
                        # Obtener solo las cabeceras del email SIN marcarlo como leído
                        status, header_data = imap.fetch(msg_id, '(BODY.PEEK[HEADER])')

                        if status != 'OK' or not header_data:
                            logger.log(f"No se pudieron obtener las cabeceras del email {msg_id}", level="WARNING")
                            continue

                        # Parsear solo las cabeceras
                        raw_headers = header_data[0][1]
                        headers = email.message_from_bytes(raw_headers, policy=email.policy.default)

                        # Obtener y decodificar el subject del email
                        subject = self._decode_header_value(headers.get('Subject', ''))
                        sender = headers.get('From', '')

                        logger.log(f"Revisando email: '{subject}' de {sender}", level="INFO")

                        # Buscar caso coincidente usando el sistema modular
                        matching_case = self.case_handler.find_matching_case(subject, logger)

                        if matching_case:
                            logger.log(f"Email encontrado para caso: {matching_case}", level="INFO")

                            # Marcar como leído
                            status, result = self._mark_as_read(imap, msg_id)
                            if status:
                                logger.log(f"Email marcado como leído: {result}", level="INFO")

                                # Preparar datos del email para el caso
                                email_data = {
                                    'sender': sender,
                                    'subject': subject,
                                    'msg_id': msg_id.decode() if isinstance(msg_id, bytes) else str(msg_id)
                                }

                                # Ejecutar el caso correspondiente
                                response_data = self.case_handler.execute_case(matching_case, email_data, logger)

                                if response_data:
                                    # Enviar respuesta automática
                                    if self._send_case_reply(provider, email_addr, password, response_data, logger):
                                        logger.log(f"Respuesta automática enviada usando {matching_case}", level="INFO")
                                    else:
                                        logger.log(f"Error al enviar respuesta automática", level="ERROR")
                                else:
                                    logger.log(f"Error al procesar {matching_case}", level="ERROR")
                            else:
                                logger.log(f"Error al marcar email como leído: {result}", level="ERROR")
                        else:
                            logger.log(f"Email no coincide con ningún caso: '{subject}'", level="INFO")

                    except Exception as e:
                        logger.log(f"Error al procesar email individual: {str(e)}", level="ERROR")

        except Exception as e:
            logger.log(f"Error en check_and_process_emails: {str(e)}", level="ERROR")

    def _send_case_reply(self, provider, email_addr, password, response_data, logger):
        """Envía una respuesta automática usando los datos del caso"""
        try:
            recipient = response_data.get('recipient', '')
            subject = response_data.get('subject', '')
            body = response_data.get('body', '')

            # Extraer solo la dirección de email del remitente
            if '<' in recipient and '>' in recipient:
                recipient = recipient.split('<')[1].split('>')[0].strip()

            # Enviar la respuesta
            return self.send_email(provider, email_addr, password, recipient, subject, body)

        except Exception as e:
            logger.log(f"Error al enviar respuesta del caso: {str(e)}", level="ERROR")
            return False

    def _decode_header_value(self, header_value):
        """Decodifica un valor de cabecera que puede estar codificado"""
        if not header_value:
            return ""

        try:
            decoded_parts = decode_header(header_value)
            decoded_text = ""

            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    if encoding:
                        decoded_text += part.decode(encoding)
                    else:
                        decoded_text += part.decode('utf-8', errors='ignore')
                else:
                    decoded_text += part

            return decoded_text
        except Exception as e:
            print(f"Error al decodificar cabecera: {str(e)}")
            return str(header_value)

    def _mark_as_read(self, imap_connection, msg_id):
        """Marca un email específico como leído"""
        try:
            # Añadir la flag \Seen al mensaje para marcarlo como leído
            status, result = imap_connection.store(msg_id, '+FLAGS', '\\Seen')
            if status != 'OK':
                return False, f"Estado no OK: {status}"

            # Verificar el resultado
            if not result or not result[0]:
                return False, "Resultado vacío"

            return True, "Email marcado correctamente como leído"
        except Exception as e:
            return False, f"Error al marcar email como leído: {str(e)}"

    def _is_today(self, email_date_str):
        """Verifica si un email es del día de hoy"""
        try:
            # Parsear la fecha del email
            email_date = email.utils.parsedate_to_datetime(email_date_str)
            today = datetime.now().date()

            # Comparar solo la fecha (sin hora)
            return email_date.date() == today

        except Exception as e:
            print(f"Error al verificar fecha del email: {str(e)}")
            return False

    def _sanitize_string(self, text):
        """Sanitiza un string para evitar problemas de codificación"""
        if not isinstance(text, str):
            return str(text)

        # Eliminar caracteres no imprimibles y espacios no separables
        text = ''.join(c for c in text if c.isprintable() and ord(c) != 0xA0)
        return text

    def reload_cases(self):
        """Recarga todos los casos disponibles"""
        self.case_handler.reload_cases()

    def get_available_cases(self):
        """Obtiene los casos disponibles"""
        return self.case_handler.get_available_cases()

    def get_case_info(self, case_name):
        """Obtiene información de un caso específico"""
        return self.case_handler.get_case_info(case_name)