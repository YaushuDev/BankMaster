# Archivo: case2.py
# Ubicación: raíz del proyecto
# Descripción: Caso 2 - Responde "adios" a emails que coincidan con las palabras clave

from base_case import BaseCase


class Case(BaseCase):
    def __init__(self):
        super().__init__(
            name="Caso 2",
            description="Responde con 'adios' a emails específicos",
            config_key="caso2",
            response_message="adios",
        )

