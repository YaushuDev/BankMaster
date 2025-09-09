# Archivo: case2.py
# Ubicación: raíz del proyecto
# Descripción: Caso 2 - Responde "adios" a emails que coincidan con las palabras clave

class Case:
    def __init__(self):
        """Inicializa el caso 2"""
        self.name = "Caso 2"
        self.description = "Responde con 'adios' a emails específicos"
        self.search_keywords = []
        self.response_message = "adios"

    def get_name(self):
        """Obtiene el nombre del caso"""
        return self.name

    def get_description(self):
        """Obtiene la descripción del caso"""
        return self.description

    def get_search_keywords(self):
        """Obtiene las palabras clave de búsqueda desde la configuración"""
        try:
            from config_manager import ConfigManager
            config_manager = ConfigManager()
            config = config_manager.load_config()
            search_params = config.get('search_params', {})
            keyword = search_params.get('caso2', '').strip()

            if keyword:
                return [keyword]
            else:
                return []
        except Exception as e:
            print(f"Error al cargar palabras clave para caso2: {str(e)}")
            return []

    def process_email(self, email_data, logger):
        """Procesa el email y genera la respuesta automática"""
        try:
            # Extraer información del email
            sender = email_data.get('sender', '')
            subject = email_data.get('subject', '')

            logger.log(f"Procesando caso2 para email de {sender} con asunto: {subject}", level="INFO")

            # Generar respuesta
            response_data = {
                'recipient': sender,
                'subject': f"Re: {subject}",
                'body': self.response_message
            }

            logger.log(f"Respuesta generada para caso2: '{self.response_message}'", level="INFO")

            return response_data

        except Exception as e:
            logger.log(f"Error al procesar email en caso2: {str(e)}", level="ERROR")
            return None

    def get_response_message(self):
        """Obtiene el mensaje de respuesta"""
        return self.response_message

    def set_response_message(self, message):
        """Establece un nuevo mensaje de respuesta"""
        self.response_message = message