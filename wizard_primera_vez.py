import os
import tkinter as tk
from tkinter import ttk, messagebox
import configparser
from gestor_licencias import GestorLicencias


class WizardPrimeraVez:
    """Wizard de configuración inicial para primera ejecución"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎉 Bienvenido - Marketplace")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")
        
        # Centrar ventana
        self.root.withdraw()
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        self.root.deiconify()

        self.paso_actual = 0
        self.datos_config = {
            'codigo_licencia': '',
            'navegador': 'firefox',
            'usar_perfil': 'si',
            'contacto_whatsapp': ''
        }
        self.gestor_licencias = GestorLicencias("Marketplace")

        self._mostrar_paso()

    def _limpiar_ventana(self):
        """Limpia todos los widgets de la ventana"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def _mostrar_paso(self):
        """Muestra el paso actual del wizard"""
        self._limpiar_ventana()

        if self.paso_actual == 0:
            self._paso_bienvenida()
        elif self.paso_actual == 1:
            self._paso_licencia()
        elif self.paso_actual == 2:
            self._paso_configuracion()
        elif self.paso_actual == 3:
            self._paso_whatsapp()
        elif self.paso_actual == 4:
            self._paso_finalizar()

    def _paso_bienvenida(self):
        """Paso 0: Pantalla de bienvenida"""
        # Header
        header = tk.Frame(self.root, bg="#198754", pady=20)
        header.pack(fill='x')
        tk.Label(
            header,
            text="🎉 Bienvenido a Marketplace Automático",
            font=("Segoe UI", 16, "bold"),
            bg="#198754",
            fg="white"
        ).pack()

        # Contenido
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill='both', expand=True, padx=40, pady=30)

        tk.Label(
            frame,
            text="Esta aplicación publica productos en\nFacebook Marketplace de forma automática.",
            font=("Segoe UI", 12),
            bg="#f0f0f0",
            justify='center'
        ).pack(pady=(0, 20))

        tk.Label(
            frame,
            text="Vamos a configurarla juntos paso a paso\n(solo esta vez).",
            font=("Segoe UI", 11),
            bg="#f0f0f0",
            fg="gray",
            justify='center'
        ).pack(pady=(0, 30))

        tk.Label(
            frame,
            text="✨ Características:\n\n"
                 "• Publicación automática en Marketplace\n"
                 "• Extracción de catálogos WhatsApp Business\n"
                 "• Gestión visual de artículos\n"
                 "• Programación de tareas (versión FULL)",
            font=("Segoe UI", 10),
            bg="#f0f0f0",
            justify='left'
        ).pack(pady=(0, 30))

        # Botones
        frame_btn = tk.Frame(self.root, bg="#f0f0f0", pady=20)
        frame_btn.pack(fill='x', side='bottom')

        tk.Button(
            frame_btn,
            text="▶️  Comenzar",
            font=("Segoe UI", 11, "bold"),
            bg="#198754",
            fg="white",
            width=20,
            command=self._siguiente
        ).pack()

    def _paso_licencia(self):
        """Paso 1: Activar licencia"""
        # Header
        header = tk.Frame(self.root, bg="#198754", pady=15)
        header.pack(fill='x')
        tk.Label(
            header,
            text="Paso 1 de 4: Activar Licencia",
            font=("Segoe UI", 14, "bold"),
            bg="#198754",
            fg="white"
        ).pack()

        # Contenido
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill='both', expand=True, padx=40, pady=30)

        tk.Label(
            frame,
            text="Ingresa tu código de licencia:",
            font=("Segoe UI", 11, "bold"),
            bg="#f0f0f0"
        ).pack(anchor='w', pady=(0, 10))

        self.entry_licencia = tk.Entry(
            frame,
            font=("Segoe UI", 12),
            width=35
        )
        self.entry_licencia.pack(pady=(0, 20))
        self.entry_licencia.focus()
        
        # Auto-mayúsculas mientras escribe
        def auto_mayusculas(event):
            contenido = self.entry_licencia.get()
            mayus = contenido.upper()
            if contenido != mayus:
                pos = self.entry_licencia.index(tk.INSERT)
                self.entry_licencia.delete(0, tk.END)
                self.entry_licencia.insert(0, mayus)
                self.entry_licencia.icursor(pos)
        
        self.entry_licencia.bind('<KeyRelease>', auto_mayusculas)

        tk.Label(
            frame,
            text="Si no tienes código, puedes usar la versión TRIAL\n"
                 "(limitada a 3 productos por día)",
            font=("Segoe UI", 9),
            bg="#f0f0f0",
            fg="gray",
            justify='center'
        ).pack(pady=(0, 30))

        # Botones
        frame_btn = tk.Frame(self.root, bg="#f0f0f0", pady=20)
        frame_btn.pack(fill='x', side='bottom')

        tk.Button(
            frame_btn,
            text="◀️ Atrás",
            font=("Segoe UI", 10),
            bg="#e0e0e0",
            width=12,
            command=self._anterior
        ).pack(side='left', padx=(40, 10))

        tk.Button(
            frame_btn,
            text="Usar TRIAL",
            font=("Segoe UI", 10),
            bg="#ffc107",
            width=12,
            command=self._usar_trial
        ).pack(side='left', padx=10)

        tk.Button(
            frame_btn,
            text="Siguiente ▶️",
            font=("Segoe UI", 10, "bold"),
            bg="#198754",
            fg="white",
            width=12,
            command=self._validar_licencia
        ).pack(side='right', padx=(10, 40))

    def _paso_configuracion(self):
        """Paso 2: Configuración básica"""
        # Header
        header = tk.Frame(self.root, bg="#198754", pady=15)
        header.pack(fill='x')
        tk.Label(
            header,
            text="Paso 2 de 4: Configuración",
            font=("Segoe UI", 14, "bold"),
            bg="#198754",
            fg="white"
        ).pack()

        # Contenido
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill='both', expand=True, padx=40, pady=30)

        tk.Label(
            frame,
            text="Navegador:",
            font=("Segoe UI", 11, "bold"),
            bg="#f0f0f0"
        ).pack(anchor='w', pady=(0, 5))

        self.var_navegador = tk.StringVar(value="firefox")
        frame_nav = tk.Frame(frame, bg="#f0f0f0")
        frame_nav.pack(anchor='w', pady=(0, 20))
        
        tk.Radiobutton(
            frame_nav, text="Firefox",
            variable=self.var_navegador, value="firefox",
            bg="#f0f0f0", font=("Segoe UI", 10)
        ).pack(side='left', padx=(0, 20))
        
        tk.Radiobutton(
            frame_nav, text="Chrome",
            variable=self.var_navegador, value="chrome",
            bg="#f0f0f0", font=("Segoe UI", 10)
        ).pack(side='left')

        tk.Label(
            frame,
            text="Usar tu sesión de Facebook guardada:",
            font=("Segoe UI", 11, "bold"),
            bg="#f0f0f0"
        ).pack(anchor='w', pady=(20, 5))

        tk.Label(
            frame,
            text="(Recomendado: Sí - para no tener que iniciar sesión cada vez)",
            font=("Segoe UI", 9),
            bg="#f0f0f0",
            fg="gray"
        ).pack(anchor='w', pady=(0, 5))

        self.var_perfil = tk.StringVar(value="si")
        frame_perfil = tk.Frame(frame, bg="#f0f0f0")
        frame_perfil.pack(anchor='w', pady=(0, 20))
        
        tk.Radiobutton(
            frame_perfil, text="Sí",
            variable=self.var_perfil, value="si",
            bg="#f0f0f0", font=("Segoe UI", 10)
        ).pack(side='left', padx=(0, 20))
        
        tk.Radiobutton(
            frame_perfil, text="No",
            variable=self.var_perfil, value="no",
            bg="#f0f0f0", font=("Segoe UI", 10)
        ).pack(side='left')

        # Botones
        frame_btn = tk.Frame(self.root, bg="#f0f0f0", pady=20)
        frame_btn.pack(fill='x', side='bottom')

        tk.Button(
            frame_btn,
            text="◀️ Atrás",
            font=("Segoe UI", 10),
            bg="#e0e0e0",
            width=12,
            command=self._anterior
        ).pack(side='left', padx=(40, 10))

        tk.Button(
            frame_btn,
            text="Siguiente ▶️",
            font=("Segoe UI", 10, "bold"),
            bg="#198754",
            fg="white",
            width=12,
            command=self._guardar_config_basica
        ).pack(side='right', padx=(10, 40))

    def _paso_whatsapp(self):
        """Paso 3: Configuración de WhatsApp (opcional)"""
        # Header
        header = tk.Frame(self.root, bg="#198754", pady=15)
        header.pack(fill='x')
        tk.Label(
            header,
            text="Paso 3 de 4: WhatsApp (Opcional)",
            font=("Segoe UI", 14, "bold"),
            bg="#198754",
            fg="white"
        ).pack()

        # Contenido
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill='both', expand=True, padx=40, pady=30)

        tk.Label(
            frame,
            text="Puedes extraer productos automáticamente\ndesde un catálogo de WhatsApp Business.",
            font=("Segoe UI", 11),
            bg="#f0f0f0",
            justify='center'
        ).pack(pady=(0, 20))

        tk.Label(
            frame,
            text="Nombre del contacto en WhatsApp:",
            font=("Segoe UI", 10, "bold"),
            bg="#f0f0f0"
        ).pack(anchor='w', pady=(0, 5))

        tk.Label(
            frame,
            text="(Ejemplo: 'Trabajo John' - déjalo en blanco para configurar después)",
            font=("Segoe UI", 9),
            bg="#f0f0f0",
            fg="gray"
        ).pack(anchor='w', pady=(0, 10))

        self.entry_contacto = tk.Entry(
            frame,
            font=("Segoe UI", 11),
            width=40
        )
        self.entry_contacto.pack(pady=(0, 20))
        self.entry_contacto.insert(0, "Trabajo John")

        tk.Label(
            frame,
            text="💡 También puedes crear artículos manualmente\nusando el Gestor de Artículos",
            font=("Segoe UI", 9),
            bg="#f0f0f0",
            fg="gray",
            justify='center'
        ).pack(pady=(0, 10))

        # Botones
        frame_btn = tk.Frame(self.root, bg="#f0f0f0", pady=20)
        frame_btn.pack(fill='x', side='bottom')

        tk.Button(
            frame_btn,
            text="◀️ Atrás",
            font=("Segoe UI", 10),
            bg="#e0e0e0",
            width=12,
            command=self._anterior
        ).pack(side='left', padx=(40, 10))

        tk.Button(
            frame_btn,
            text="Siguiente ▶️",
            font=("Segoe UI", 10, "bold"),
            bg="#198754",
            fg="white",
            width=12,
            command=self._guardar_whatsapp
        ).pack(side='right', padx=(10, 40))

    def _paso_finalizar(self):
        """Paso 4: Finalizar configuración"""
        # Header
        header = tk.Frame(self.root, bg="#28a745", pady=15)
        header.pack(fill='x')
        tk.Label(
            header,
            text="Paso 4 de 4: ¡Listo!",
            font=("Segoe UI", 14, "bold"),
            bg="#28a745",
            fg="white"
        ).pack()

        # Contenido
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill='both', expand=True, padx=40, pady=30)

        tk.Label(
            frame,
            text="✅ ¡Configuración completada!",
            font=("Segoe UI", 14, "bold"),
            bg="#f0f0f0",
            fg="#28a745"
        ).pack(pady=(0, 20))

        # Resumen
        resumen_frame = tk.Frame(frame, bg="white", relief='solid', borderwidth=1)
        resumen_frame.pack(fill='x', pady=(0, 20))

        licencia_texto = "TRIAL" if not self.datos_config['codigo_licencia'] else self.datos_config['codigo_licencia'][:20] + "..."
        articulos_count = self._contar_articulos()
        contacto = self.datos_config['contacto_whatsapp'] or "(Configurar después)"

        items = [
            ("✅ Licencia:", licencia_texto),
            ("✅ Navegador:", self.datos_config['navegador'].capitalize()),
            ("✅ Contacto WhatsApp:", contacto),
            ("✅ Artículos:", f"{articulos_count} artículos")
        ]

        for label, valor in items:
            item_frame = tk.Frame(resumen_frame, bg="white")
            item_frame.pack(fill='x', padx=15, pady=5)
            tk.Label(item_frame, text=label, font=("Segoe UI", 10, "bold"), bg="white", width=22, anchor='w').pack(side='left')
            tk.Label(item_frame, text=valor, font=("Segoe UI", 10), bg="white", anchor='w').pack(side='left')

        tk.Label(
            frame,
            text="Usa el Gestor de Artículos para crear tus productos",
            font=("Segoe UI", 10),
            bg="#f0f0f0",
            fg="gray"
        ).pack(pady=(20, 10))

        # Botones
        frame_btn = tk.Frame(self.root, bg="#f0f0f0", pady=20)
        frame_btn.pack(fill='x', side='bottom')

        tk.Button(
            frame_btn,
            text="📦 Abrir Gestor",
            font=("Segoe UI", 10),
            bg="#198754",
            fg="white",
            width=15,
            command=self._abrir_gestor
        ).pack(side='left', padx=(40, 10))

        tk.Button(
            frame_btn,
            text="✅ Finalizar",
            font=("Segoe UI", 10, "bold"),
            bg="#28a745",
            fg="white",
            width=15,
            command=self._finalizar
        ).pack(side='right', padx=(10, 40))

    # Funciones auxiliares
    def _siguiente(self):
        self.paso_actual += 1
        self._mostrar_paso()

    def _anterior(self):
        self.paso_actual -= 1
        self._mostrar_paso()

    def _usar_trial(self):
        self.datos_config['codigo_licencia'] = ''
        self._siguiente()

    def _validar_licencia(self):
        codigo = self.entry_licencia.get().strip().upper()
        
        # Formatear: quitar guiones, convertir mayúsculas, agregar guiones
        if codigo:
            # Quitar guiones existentes
            codigo_limpio = codigo.replace('-', '')
            
            # Si tiene el formato correcto de cantidad de caracteres, formatear
            # Formato esperado: LIC-MASTER-WELLI (3-6-5 caracteres)
            if len(codigo_limpio) >= 10:
                codigo = f"{codigo_limpio[:3]}-{codigo_limpio[3:9]}-{codigo_limpio[9:]}"
            
            self.datos_config['codigo_licencia'] = codigo
            self.gestor_licencias.guardar_codigo_licencia(codigo)
        
        self._siguiente()

    def _guardar_config_basica(self):
        self.datos_config['navegador'] = self.var_navegador.get()
        self.datos_config['usar_perfil'] = self.var_perfil.get()
        self._siguiente()

    def _guardar_whatsapp(self):
        self.datos_config['contacto_whatsapp'] = self.entry_contacto.get().strip()
        self._crear_config_completa()
        self._siguiente()

    def _contar_articulos(self):
        """Cuenta los artículos existentes"""
        try:
            carpeta = "ArticulosMarketplace"
            if not os.path.exists(carpeta):
                return 0
            return len([d for d in os.listdir(carpeta) 
                       if os.path.isdir(os.path.join(carpeta, d)) 
                       and d.startswith("Articulo_")])
        except:
            return 0

    def _crear_config_completa(self):
        """Crea el archivo config_global.txt con la configuración inicial completa"""
        config = configparser.ConfigParser()
        
        config['GENERAL'] = {
            'cantidad_productos': '5',
            'modo': 'completo'
        }
        
        config['EXTRACCION'] = {
            'contacto_whatsapp': self.datos_config['contacto_whatsapp'],
            'auto_scroll': '5',
            'productos_por_extraccion': '5'
        }
        
        config['PUBLICACION'] = {
            'auto_publicar': 'si',
            'tiempo_entre_publicaciones': '10',
            'max_publicaciones_por_dia': '10',
            'publicar_todos': 'si'
        }
        
        config['SEGURIDAD'] = {
            'confirmacion_borrado': 'si',
            'backup_antes_borrar': 'si'
        }
        
        config['NAVEGADOR'] = {
            'navegador': self.datos_config['navegador'],
            'usar_perfil_existente': self.datos_config['usar_perfil'],
            'carpeta_perfil_custom': 'perfil_bot_marketplace',
            'desactivar_notificaciones': 'si',
            'maximizar_ventana': 'si'
        }
        
        with open('config_global.txt', 'w', encoding='utf-8') as f:
            f.write("# ============================================================\n")
            f.write("# CONFIGURACIÓN GLOBAL DEL SISTEMA - MARKETPLACE\n")
            f.write("# ============================================================\n\n")
            config.write(f)

    def _abrir_gestor(self):
        """Abre el gestor de artículos"""
        try:
            import subprocess
            subprocess.Popen(['python', 'gestor_articulos_gui.py'])
            messagebox.showinfo(
                "✅ Gestor Abierto",
                "El Gestor de Artículos se abrió en una nueva ventana.\n\nCrea tus productos y luego cierra esta ventana."
            )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el gestor: {e}")
        self.root.destroy()

    def _finalizar(self):
        """Finaliza sin abrir el gestor"""
        messagebox.showinfo(
            "✅ Configuración Completada",
            "¡Todo listo!\n\nPuedes ejecutar 'Marketplace' cuando quieras publicar.\n\nO usa 'Panel de Control' para gestionar tu aplicación."
        )
        self.root.destroy()

    def ejecutar(self):
        self.root.mainloop()


def main():
    wizard = WizardPrimeraVez()
    wizard.ejecutar()


if __name__ == "__main__":
    main()