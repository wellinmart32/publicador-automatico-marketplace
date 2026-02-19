import os
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
from gestor_licencias import GestorLicencias
from gestor_registro import GestorRegistro


class PanelControl:
    """Panel de control principal - Marketplace Automático"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🛒 Marketplace Automático - Panel de Control")
        self.root.geometry("700x600")
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

        # Verificar licencia
        self.gestor_licencias = GestorLicencias("Marketplace")
        self.licencia = self._verificar_licencia()
        
        if not self.licencia:
            messagebox.showerror("Error", "No se pudo verificar la licencia")
            self.root.destroy()
            return

        self._construir_ui()

    def _verificar_licencia(self):
        """Verifica la licencia al inicio"""
        codigo = self.gestor_licencias.obtener_codigo_guardado()
        
        if not codigo:
            messagebox.showwarning(
                "Sin Licencia",
                "No hay código de licencia configurado.\n\nEjecuta el Wizard de primera vez."
            )
            return None
        
        resultado = self.gestor_licencias.verificar_licencia(codigo, mostrar_mensajes=False)
        
        if not resultado['valida']:
            messagebox.showerror(
                "Licencia Inválida",
                "Tu licencia no es válida o ha expirado."
            )
            return None
        
        return resultado

    def _construir_ui(self):
        """Construye la interfaz del panel"""
        
        # Header
        header = tk.Frame(self.root, bg="#198754", pady=20)
        header.pack(fill='x')
        
        tk.Label(
            header,
            text="🛒 Marketplace Automático",
            font=("Segoe UI", 20, "bold"),
            bg="#198754",
            fg="white"
        ).pack()
        
        # Subtítulo con tipo de licencia
        tipo_licencia = self.licencia.get('tipo', 'TRIAL')
        color_badge = "#28a745" if tipo_licencia == "FULL" else "#ffc107"
        
        if self.licencia.get('developer_permanente'):
            texto_licencia = "👑 LICENCIA DEVELOPER"
        elif tipo_licencia == "FULL":
            texto_licencia = "✅ LICENCIA FULL"
        else:
            dias = self.licencia.get('diasRestantes', 0)
            texto_licencia = f"⚠️ TRIAL - {dias} días restantes"
        
        tk.Label(
            header,
            text=texto_licencia,
            font=("Segoe UI", 10, "bold"),
            bg=color_badge,
            fg="white",
            padx=15,
            pady=5
        ).pack(pady=(10, 0))

        # Contenedor principal
        container = tk.Frame(self.root, bg="#f0f0f0")
        container.pack(fill='both', expand=True, padx=30, pady=20)

        # Botón principal: PUBLICAR PRODUCTO
        btn_publicar = tk.Button(
            container,
            text="▶️  PUBLICAR PRODUCTO",
            font=("Segoe UI", 16, "bold"),
            bg="#198754",
            fg="white",
            activebackground="#146c43",
            activeforeground="white",
            cursor="hand2",
            height=2,
            command=self._publicar_ahora
        )
        btn_publicar.pack(fill='x', pady=(0, 20))

        # Grid de opciones
        grid_frame = tk.Frame(container, bg="#f0f0f0")
        grid_frame.pack(fill='both', expand=True)

        # Fila 1
        self._crear_boton_opcion(
            grid_frame,
            "⚙️\nConfigurador",
            "Ajustar configuración",
            self._abrir_configurador,
            row=0, col=0
        )
        
        self._crear_boton_opcion(
            grid_frame,
            "📦\nGestor Artículos",
            "Crear/editar productos",
            self._abrir_gestor_articulos,
            row=0, col=1
        )

        # Fila 2
        self._crear_boton_opcion(
            grid_frame,
            "📱\nExtractor WhatsApp",
            "Importar catálogo",
            self._abrir_extractor,
            row=1, col=0,
            color="#25D366"
        )
        
        self._crear_boton_opcion(
            grid_frame,
            "📊\nEstadísticas",
            "Ver historial",
            self._ver_estadisticas,
            row=1, col=1
        )

        # Fila 3
        # Gestión de tareas (solo FULL)
        if tipo_licencia == "FULL" or self.licencia.get('developer_permanente'):
            self._crear_boton_opcion(
                grid_frame,
                "🗓️\nTareas Auto",
                "Programar publicaciones",
                self._gestionar_tareas,
                row=2, col=0,
                color="#28a745"
            )
        else:
            self._crear_boton_opcion(
                grid_frame,
                "🔒\nTareas Auto",
                "Solo versión FULL",
                lambda: messagebox.showinfo("Premium", "Esta función requiere licencia FULL"),
                row=2, col=0,
                color="#6c757d"
            )
        
        self._crear_boton_opcion(
            grid_frame,
            "❌\nSalir",
            "Cerrar panel",
            self.root.destroy,
            row=2, col=1,
            color="#dc3545"
        )

    def _crear_boton_opcion(self, parent, texto, subtexto, comando, row, col, color="#198754"):
        """Crea un botón de opción estilizado"""
        frame = tk.Frame(parent, bg="white", relief='solid', borderwidth=1, cursor="hand2")
        frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        # Configurar grid
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        # Label principal
        lbl_texto = tk.Label(
            frame,
            text=texto,
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg=color
        )
        lbl_texto.pack(expand=True, pady=(15, 5))
        
        # Subtexto
        lbl_sub = tk.Label(
            frame,
            text=subtexto,
            font=("Segoe UI", 8),
            bg="white",
            fg="gray"
        )
        lbl_sub.pack(expand=True, pady=(0, 15))
        
        # Hacer todo clickeable
        for widget in [frame, lbl_texto, lbl_sub]:
            widget.bind('<Button-1>', lambda e: comando())
            widget.bind('<Enter>', lambda e: frame.config(bg="#f8f9fa"))
            widget.bind('<Leave>', lambda e: frame.config(bg="white"))

    def _publicar_ahora(self):
        """Ejecuta publicación inmediata"""
        try:
            subprocess.Popen(['python', 'automatizador_marketplace.py'])
            self._mostrar_notificacion(
                "✅ Publicación Iniciada",
                "El navegador se abrirá en unos segundos...",
                duracion=3000,
                color="#28a745"
            )
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo iniciar la publicación:\n{e}")

    def _abrir_configurador(self):
        """Abre el configurador GUI"""
        try:
            subprocess.Popen(['python', 'configurador_gui.py'])
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo abrir el configurador:\n{e}")

    def _abrir_gestor_articulos(self):
        """Abre el gestor de artículos"""
        try:
            subprocess.Popen(['python', 'gestor_articulos_gui.py'])
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo abrir el gestor:\n{e}")

    def _abrir_extractor(self):
        """Abre el extractor de WhatsApp"""
        try:
            subprocess.Popen(['python', 'extractor_whatsapp.py'])
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo abrir el extractor:\n{e}")

    def _ver_estadisticas(self):
        """Muestra ventana de estadísticas básicas"""
        try:
            # Contar artículos
            carpeta = "ArticulosMarketplace"
            total_articulos = 0
            if os.path.exists(carpeta):
                total_articulos = len([d for d in os.listdir(carpeta) 
                                      if os.path.isdir(os.path.join(carpeta, d)) 
                                      and d.startswith("Articulo_")])
            
            # Crear ventana
            ventana = tk.Toplevel(self.root)
            ventana.title("📊 Estadísticas")
            ventana.geometry("400x250")
            ventana.configure(bg="#f0f0f0")
            
            # Centrar
            ventana.update_idletasks()
            x = (ventana.winfo_screenwidth() // 2) - (200)
            y = (ventana.winfo_screenheight() // 2) - (125)
            ventana.geometry(f'400x250+{x}+{y}')
            
            # Header
            header = tk.Frame(ventana, bg="#198754", pady=15)
            header.pack(fill='x')
            tk.Label(
                header,
                text="📊 Estadísticas Básicas",
                font=("Segoe UI", 14, "bold"),
                bg="#198754",
                fg="white"
            ).pack()
            
            # Contenido
            frame = tk.Frame(ventana, bg="white", padx=30, pady=20)
            frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            tk.Label(
                frame,
                text=f"📦 Artículos totales: {total_articulos}",
                font=("Segoe UI", 12),
                bg="white"
            ).pack(pady=10)
            
            tk.Label(
                frame,
                text="💡 Estadísticas detalladas próximamente",
                font=("Segoe UI", 9),
                bg="white",
                fg="gray"
            ).pack(pady=10)
            
            # Botón cerrar
            tk.Button(
                ventana,
                text="Cerrar",
                font=("Segoe UI", 10),
                bg="#6c757d",
                fg="white",
                command=ventana.destroy
            ).pack(pady=(0, 20))
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error mostrando estadísticas:\n{e}")

    def _gestionar_tareas(self):
        """Gestión de tareas automáticas"""
        try:
            subprocess.Popen(['python', 'gestor_tareas_gui.py'])
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo abrir el gestor de tareas:\n{e}")

    def _mostrar_notificacion(self, titulo, mensaje, duracion=3000, color="#198754"):
        """Muestra notificación Toast que se cierra sola"""
        # Crear ventana toast
        toast = tk.Toplevel(self.root)
        toast.overrideredirect(True)  # Sin bordes
        toast.attributes('-topmost', True)  # Siempre encima
        
        # Posicionar en esquina inferior derecha
        ancho = 350
        alto = 100
        x = toast.winfo_screenwidth() - ancho - 20
        y = toast.winfo_screenheight() - alto - 60
        toast.geometry(f'{ancho}x{alto}+{x}+{y}')
        
        # Frame con sombra
        frame = tk.Frame(toast, bg=color, relief='raised', borderwidth=2)
        frame.pack(fill='both', expand=True)
        
        # Título
        tk.Label(
            frame,
            text=titulo,
            font=("Segoe UI", 11, "bold"),
            bg=color,
            fg="white"
        ).pack(pady=(10, 5))
        
        # Mensaje
        tk.Label(
            frame,
            text=mensaje,
            font=("Segoe UI", 9),
            bg=color,
            fg="white",
            wraplength=300
        ).pack(pady=(0, 10))
        
        # Cerrar automáticamente
        toast.after(duracion, toast.destroy)
        
        # Permitir cerrar con clic
        frame.bind('<Button-1>', lambda e: toast.destroy())

    def ejecutar(self):
        """Inicia el panel de control"""
        self.root.mainloop()


def main():
    panel = PanelControl()
    panel.ejecutar()


if __name__ == "__main__":
    main()