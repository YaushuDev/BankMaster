# Archivo: ui_manager.py
# Ubicación: raíz del proyecto
# Descripción: Gestiona la estructura y componentes de la interfaz de usuario

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont  # Importación correcta del módulo font
from email_manager import EmailManager
from config_manager import ConfigManager
from logger import Logger


class UIManager:
    def __init__(self, root):
        """Inicializa la interfaz de usuario del bot"""
        self.root = root
        # Configurar fuente para soportar UTF-8
        default_font = tkfont.nametofont("TkDefaultFont")  # Usando tkfont en lugar de tk.font
        default_font.configure(family="Arial", size=10)
        self.root.option_add("*Font", default_font)

        self.email_manager = EmailManager()
        self.config_manager = ConfigManager()
        self.logger = Logger()

        # Configurar el marco principal
        self.setup_main_frame()

        # Configurar los tres paneles
        self.setup_top_panel()
        self.setup_bottom_left_panel()
        self.setup_bottom_right_panel()

        # Iniciar componentes
        self.initialize_components()

    def setup_main_frame(self):
        """Configura el marco principal de la aplicación"""
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Configurar el peso de las filas y columnas
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=2)  # Panel superior más grande
        self.main_frame.rowconfigure(1, weight=1)  # Paneles inferiores

    def setup_top_panel(self):
        """Configura el panel superior principal"""
        self.top_panel = ttk.LabelFrame(self.main_frame, text="Panel Principal")
        self.top_panel.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

    def setup_bottom_left_panel(self):
        """Configura el panel inferior izquierdo para configuración de correo"""
        self.bottom_left_panel = ttk.LabelFrame(self.main_frame, text="Configuración de Correo")
        self.bottom_left_panel.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Crear campos para configuración de correo
        ttk.Label(self.bottom_left_panel, text="Proveedor de Correo:").grid(row=0, column=0, sticky="w", padx=5, pady=5)

        # Opciones de proveedores de correo
        self.provider_var = tk.StringVar()
        self.provider_combo = ttk.Combobox(self.bottom_left_panel, textvariable=self.provider_var)
        self.provider_combo['values'] = ('Gmail', 'Outlook', 'Yahoo', 'Otro')
        self.provider_combo.current(0)  # Por defecto selecciona Gmail
        self.provider_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(self.bottom_left_panel, text="Usuario (email):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(self.bottom_left_panel, textvariable=self.email_var)
        self.email_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(self.bottom_left_panel, text="Contraseña:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(self.bottom_left_panel, textvariable=self.password_var, show="*")
        self.password_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # Botones de acción
        self.test_button = ttk.Button(self.bottom_left_panel, text="Probar Conexión", command=self.test_connection)
        self.test_button.grid(row=3, column=0, sticky="ew", padx=5, pady=(15, 5))

        self.save_button = ttk.Button(self.bottom_left_panel, text="Guardar Datos", command=self.save_config)
        self.save_button.grid(row=3, column=1, sticky="ew", padx=5, pady=(15, 5))

        # Hacer que los campos se expandan
        self.bottom_left_panel.columnconfigure(1, weight=1)

    def setup_bottom_right_panel(self):
        """Configura el panel inferior derecho para logs"""
        self.bottom_right_panel = ttk.LabelFrame(self.main_frame, text="Log del Sistema")
        self.bottom_right_panel.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        # Área de texto para mostrar logs con scroll
        self.log_text = tk.Text(self.bottom_right_panel, wrap=tk.WORD, height=10, width=40)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Barra de desplazamiento para el área de texto
        scrollbar = ttk.Scrollbar(self.bottom_right_panel, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

        # Configurar el logger para usar este widget
        self.logger.set_text_widget(self.log_text)

    def initialize_components(self):
        """Inicializa componentes adicionales y carga la configuración"""
        # Cargar configuración si existe
        config = self.config_manager.load_config()
        if config:
            self.provider_var.set(config.get('provider', 'Gmail'))
            self.email_var.set(config.get('email', ''))
            self.password_var.set(config.get('password', ''))

            self.logger.log("Configuración cargada correctamente.")

    def test_connection(self):
        """Prueba la conexión de correo con los datos proporcionados"""
        # Obtener los valores de los campos
        provider = self.provider_var.get()
        email = self.email_var.get()
        password = self.password_var.get()

        # Validar que los campos estén completos
        if not all([provider, email, password]):
            self.logger.log("Error: Todos los campos son obligatorios", level="ERROR")
            return

        # Probar la conexión SMTP e IMAP
        smtp_result = self.email_manager.test_smtp_connection(provider, email, password)
        imap_result = self.email_manager.test_imap_connection(provider, email, password)

        # Registrar resultados
        if smtp_result and imap_result:
            self.logger.log(f"Conexión exitosa a {provider} (SMTP e IMAP)", level="INFO")
        else:
            if not smtp_result:
                self.logger.log(f"Error en la conexión SMTP a {provider}", level="ERROR")
            if not imap_result:
                self.logger.log(f"Error en la conexión IMAP a {provider}", level="ERROR")

    def save_config(self):
        """Guarda la configuración en un archivo JSON"""
        # Obtener los valores de los campos
        config = {
            'provider': self.provider_var.get(),
            'email': self.email_var.get(),
            'password': self.password_var.get()
        }

        # Validar que los campos estén completos
        if not all(config.values()):
            self.logger.log("Error: Todos los campos son obligatorios para guardar", level="ERROR")
            return

        # Guardar la configuración
        if self.config_manager.save_config(config):
            self.logger.log("Configuración guardada correctamente", level="INFO")
        else:
            self.logger.log("Error al guardar la configuración", level="ERROR")