# Archivo: case_handler.py
# Ubicación: raíz del proyecto
# Descripción: Manejador principal para cargar y ejecutar casos de respuesta automática

import os
import importlib.util


class CaseHandler:
    def __init__(self):
        """Inicializa el manejador de casos"""
        self.cases = {}
        self.load_cases()

    def load_cases(self):
        """Carga todos los archivos de casos disponibles"""
        try:
            # Obtener todos los archivos case*.py en el directorio actual
            current_dir = os.path.dirname(os.path.abspath(__file__))
            case_files = [f for f in os.listdir(current_dir) if
                          f.startswith('case') and f.endswith('.py') and f != 'case_handler.py']

            for case_file in case_files:
                try:
                    # Extraer el número del caso del nombre del archivo
                    case_name = case_file[:-3]  # Remover .py

                    # Cargar el módulo dinámicamente
                    case_path = os.path.join(current_dir, case_file)
                    spec = importlib.util.spec_from_file_location(case_name, case_path)
                    case_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(case_module)

                    # Verificar que el módulo tenga la clase Case
                    if hasattr(case_module, 'Case'):
                        self.cases[case_name] = case_module.Case()
                        print(f"Caso cargado: {case_name}")
                    else:
                        print(f"Error: {case_file} no tiene la clase Case")

                except Exception as e:
                    print(f"Error al cargar caso {case_file}: {str(e)}")

        except Exception as e:
            print(f"Error al cargar casos: {str(e)}")

    def get_available_cases(self):
        """Obtiene la lista de casos disponibles"""
        return list(self.cases.keys())

    def get_case_info(self, case_name):
        """Obtiene información de un caso específico"""
        if case_name in self.cases:
            case_obj = self.cases[case_name]
            return {
                'name': case_obj.get_name(),
                'description': case_obj.get_description(),
                'search_keywords': case_obj.get_search_keywords()
            }
        return None

    def execute_case(self, case_name, email_data, logger):
        """Ejecuta un caso específico"""
        if case_name in self.cases:
            try:
                case_obj = self.cases[case_name]
                return case_obj.process_email(email_data, logger)
            except Exception as e:
                logger.log(f"Error al ejecutar caso {case_name}: {str(e)}", level="ERROR")
                return False
        else:
            logger.log(f"Caso no encontrado: {case_name}", level="ERROR")
            return False

    def find_matching_case(self, subject, logger):
        """Busca el primer caso que coincida con el asunto del email"""
        for case_name, case_obj in self.cases.items():
            try:
                keywords = case_obj.get_search_keywords()
                for keyword in keywords:
                    if keyword.lower() in subject.lower():
                        logger.log(f"Caso encontrado: {case_name} para palabra clave: {keyword}", level="INFO")
                        return case_name
            except Exception as e:
                logger.log(f"Error al verificar caso {case_name}: {str(e)}", level="ERROR")
                continue

        return None

    def reload_cases(self):
        """Recarga todos los casos disponibles"""
        self.cases.clear()
        self.load_cases()