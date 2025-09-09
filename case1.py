# Archivo: case1.py
# Ubicación: raíz del proyecto
# Descripción: Caso 1 - Responde "hola" a emails que coincidan con las palabras clave

from base_case import BaseCase


class Case(BaseCase):
    def __init__(self):
        super().__init__(
            name="Caso 1",
            description="Responde con 'hola' a emails específicos",
            config_key="caso1",
            response_message="hola",
        )

