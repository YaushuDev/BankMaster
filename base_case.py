# Archivo: base_case.py
# Ubicación: raíz del proyecto
# Descripción: Clase base reutilizable para los casos de respuesta automática

from config_manager import ConfigManager


class BaseCase:
    """Implementa comportamiento común para los casos"""

    def __init__(self, name, description, config_key, response_message):
        self._name = name
        self._description = description
        self._config_key = config_key
        self._response_message = response_message

    # --- Métodos de acceso ---
    def get_name(self):
        return self._name

    def get_description(self):
        return self._description

    def get_search_keywords(self):
        try:
            config = ConfigManager().load_config()
            keyword = config.get('search_params', {}).get(self._config_key, '').strip()
            return [keyword] if keyword else []
        except Exception as e:
            print(f"Error al cargar palabras clave para {self._config_key}: {e}")
            return []

    def get_response_message(self):
        return self._response_message

    def set_response_message(self, message):
        self._response_message = message

    # --- Procesamiento ---
    def process_email(self, email_data, logger):
        try:
            sender = email_data.get('sender', '')
            subject = email_data.get('subject', '')
            logger.log(
                f"Procesando {self._config_key} para email de {sender} con asunto: {subject}",
                level="INFO",
            )
            response = {
                'recipient': sender,
                'subject': f"Re: {subject}",
                'body': self._response_message,
            }
            logger.log(
                f"Respuesta generada para {self._config_key}: '{self._response_message}'",
                level="INFO",
            )
            return response
        except Exception as e:
            logger.log(
                f"Error al procesar email en {self._config_key}: {e}", level="ERROR"
            )
            return None

