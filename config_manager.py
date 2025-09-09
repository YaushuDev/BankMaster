# Archivo: config_manager.py
# Ubicación: raíz del proyecto
# Descripción: Gestiona la configuración y almacenamiento en JSON con soporte para casos dinámicos

import json
import os


class ConfigManager:
    def __init__(self, config_file="config.json"):
        """Inicializa el gestor de configuración"""
        self.config_file = config_file

    def load_config(self):
        """Carga la configuración desde el archivo JSON"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as file:
                    return json.load(file)
            else:
                return {}
        except Exception as e:
            print(f"Error al cargar la configuración: {str(e)}")
            return {}

    def save_config(self, config):
        """Guarda la configuración en el archivo JSON"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as file:
                json.dump(config, file, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al guardar la configuración: {str(e)}")
            return False

    def get_value(self, key, default=None):
        """Obtiene un valor específico de la configuración"""
        config = self.load_config()
        return config.get(key, default)

    def set_value(self, key, value):
        """Establece un valor específico en la configuración"""
        config = self.load_config()
        config[key] = value
        return self.save_config(config)

    def get_email_config(self):
        """Obtiene la configuración de correo electrónico"""
        config = self.load_config()
        return {
            'provider': config.get('provider', ''),
            'email': config.get('email', ''),
            'password': config.get('password', '')
        }

    def set_email_config(self, provider, email, password):
        """Establece la configuración de correo electrónico"""
        config = self.load_config()
        config['provider'] = provider
        config['email'] = email
        config['password'] = password
        return self.save_config(config)

    def get_search_params(self):
        """Obtiene todos los parámetros de búsqueda"""
        config = self.load_config()
        return config.get('search_params', {})

    def set_search_params(self, search_params):
        """Establece todos los parámetros de búsqueda"""
        config = self.load_config()
        config['search_params'] = search_params
        return self.save_config(config)

    def get_case_keyword(self, case_name):
        """Obtiene la palabra clave para un caso específico"""
        search_params = self.get_search_params()
        return search_params.get(case_name, '')

    def set_case_keyword(self, case_name, keyword):
        """Establece la palabra clave para un caso específico"""
        config = self.load_config()
        if 'search_params' not in config:
            config['search_params'] = {}

        if keyword.strip():
            config['search_params'][case_name] = keyword.strip()
        else:
            # Si la palabra clave está vacía, eliminar la entrada
            if case_name in config['search_params']:
                del config['search_params'][case_name]

        return self.save_config(config)

    def remove_case_keyword(self, case_name):
        """Elimina la palabra clave de un caso específico"""
        config = self.load_config()
        if 'search_params' in config and case_name in config['search_params']:
            del config['search_params'][case_name]
            return self.save_config(config)
        return True

    def get_all_case_keywords(self):
        """Obtiene todas las palabras clave configuradas con sus casos"""
        search_params = self.get_search_params()
        return [(case_name, keyword) for case_name, keyword in search_params.items() if keyword.strip()]

    def has_email_config(self):
        """Verifica si existe configuración completa de correo"""
        email_config = self.get_email_config()
        return all([email_config['provider'], email_config['email'], email_config['password']])

    def has_search_params(self):
        """Verifica si existen parámetros de búsqueda configurados"""
        search_params = self.get_search_params()
        return bool(search_params)

    def validate_config(self):
        """Valida la configuración completa"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }

        # Validar configuración de correo
        if not self.has_email_config():
            validation_result['valid'] = False
            validation_result['errors'].append("Configuración de correo incompleta")

        # Validar parámetros de búsqueda
        if not self.has_search_params():
            validation_result['warnings'].append("No hay parámetros de búsqueda configurados")

        # Verificar integridad del archivo de configuración
        try:
            config = self.load_config()
            if not isinstance(config, dict):
                validation_result['valid'] = False
                validation_result['errors'].append("Archivo de configuración corrupto")
        except Exception as e:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Error al validar configuración: {str(e)}")

        return validation_result

    def reset_config(self):
        """Resetea la configuración a valores por defecto"""
        default_config = {
            'provider': '',
            'email': '',
            'password': '',
            'search_params': {}
        }
        return self.save_config(default_config)

    def backup_config(self, backup_file=None):
        """Crea una copia de seguridad de la configuración"""
        if backup_file is None:
            backup_file = f"{self.config_file}.backup"

        try:
            config = self.load_config()
            with open(backup_file, 'w', encoding='utf-8') as file:
                json.dump(config, file, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al crear copia de seguridad: {str(e)}")
            return False

    def restore_config(self, backup_file=None):
        """Restaura la configuración desde una copia de seguridad"""
        if backup_file is None:
            backup_file = f"{self.config_file}.backup"

        try:
            if os.path.exists(backup_file):
                with open(backup_file, 'r', encoding='utf-8') as file:
                    config = json.load(file)
                return self.save_config(config)
            else:
                print(f"Archivo de copia de seguridad no encontrado: {backup_file}")
                return False
        except Exception as e:
            print(f"Error al restaurar configuración: {str(e)}")
            return False