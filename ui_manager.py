# Archivo: ui_manager.py
# Ubicación: raíz del proyecto
# Descripción: Gestiona la estructura y componentes de la interfaz de usuario

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
from email_manager import EmailManager
from config_manager import ConfigManager
from logger import Logger


class UIManager:
    def __init__(self, root):
        """Inicializa la interfaz de usuario del bot"""
        self.root = root
        # Configurar fuente para soportar UTF-8
        default_font = tkfont.nametofont("TkDefaultFont")
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

        # Botón para abrir la configuración de correo con estilo normal
        self.config_button = ttk.Button(
            self.bottom_left_panel,
            text="Configurar Correo",
            command=self.open_email_config_modal
        )
        self.config_button.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # Configurar para que el botón se expanda horizontalmente
        self.bottom_left_panel.columnconfigure(0, weight=1)

    def open_email_config_modal(self):
        """Abre una ventana modal para la configuración de correo"""
        # Cargar configuración actual
        config = self.config_manager.load_config()

        # Crear ventana modal
        modal = tk.Toplevel(self.root)
        modal.title("Configuración de Correo")
        modal.geometry("400x250")
        modal.transient(self.root)  # Hace que la ventana sea modal
        modal.grab_set()  # Previene interacción con la ventana principal
        modal.focus_set()  # Enfoca la ventana modal

        # Centrar la ventana modal en la pantalla
        modal.update_idletasks()
        width = modal.winfo_width()
        height = modal.winfo_height()
        x = (modal.winfo_screenwidth() // 2) - (width // 2)
        y = (modal.winfo_screenheight() // 2) - (height // 2)
        modal.geometry(f"{width}x{height}+{x}+{y}")

        # Frame principal para la configuración
        config_frame = ttk.Frame(modal, padding="10")
        config_frame.pack(fill=tk.BOTH, expand=True)

        # Crear campos para configuración de correo
        ttk.Label(config_frame, text="Proveedor de Correo:").grid(row=0, column=0, sticky="w", padx=5, pady=5)

        # Opciones de proveedores de correo
        provider_var = tk.StringVar(value=config.get('provider', 'Gmail'))
        provider_combo = ttk.Combobox(config_frame, textvariable=provider_var)
        provider_combo['values'] = ('Gmail', 'Outlook', 'Yahoo', 'Otro')
        provider_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(config_frame, text="Usuario (email):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        email_var = tk.StringVar(value=config.get('email', ''))
        email_entry = ttk.Entry(config_frame, textvariable=email_var)
        email_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(config_frame, text="Contraseña:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        password_var = tk.StringVar(value=config.get('password', ''))
        password_entry = ttk.Entry(config_frame, textvariable=password_var, show="*")
        password_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # Frame para botones en la parte inferior
        button_frame = ttk.Frame(config_frame)
        button_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=20)

        # Función para probar la conexión desde la ventana modal
        def test_connection_modal():
            provider = provider_var.get()
            email = email_var.get()
            password = password_var.get()

            if not all([provider, email, password]):
                self.logger.log("Error: Todos los campos son obligatorios", level="ERROR")
                return

            smtp_result = self.email_manager.test_smtp_connection(provider, email, password)
            imap_result = self.email_manager.test_imap_connection(provider, email, password)

            if smtp_result and imap_result:
                self.logger.log(f"Conexión exitosa a {provider} (SMTP e IMAP)", level="INFO")
            else:
                if not smtp_result:
                    self.logger.log(f"Error en la conexión SMTP a {provider}", level="ERROR")
                if not imap_result:
                    self.logger.log(f"Error en la conexión IMAP a {provider}", level="ERROR")

        # Función para guardar la configuración desde la ventana modal
        def save_config_modal():
            new_config = {
                'provider': provider_var.get(),
                'email': email_var.get(),
                'password': password_var.get()
            }

            if not all(new_config.values()):
                self.logger.log("Error: Todos los campos son obligatorios para guardar", level="ERROR")
                return

            if self.config_manager.save_config(new_config):
                self.logger.log("Configuración guardada correctamente", level="INFO")
                modal.destroy()  # Cerrar la ventana modal
            else:
                self.logger.log("Error al guardar la configuración", level="ERROR")

        # Botones de acción - usando el mismo estilo que en la versión original
        test_button = ttk.Button(button_frame, text="Probar Conexión", command=test_connection_modal)
        test_button.grid(row=0, column=0, sticky="ew", padx=5)

        save_button = ttk.Button(button_frame, text="Guardar Datos", command=save_config_modal)
        save_button.grid(row=0, column=1, sticky="ew", padx=5)

        cancel_button = ttk.Button(button_frame, text="Cancelar", command=modal.destroy)
        cancel_button.grid(row=0, column=2, sticky="ew", padx=5)

        # Hacer que los campos y botones se expandan
        config_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

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
            self.logger.log("Configuración cargada correctamente.")