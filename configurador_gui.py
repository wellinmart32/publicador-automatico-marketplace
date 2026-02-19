import os
import configparser
import tkinter as tk
from tkinter import ttk, messagebox


class ConfiguradorGUI:
    """Interfaz gráfica para configurar el sistema de Marketplace"""

    def __init__(self):
        self.archivo_config = "config_global.txt"
        self.config = configparser.ConfigParser()

        self.root = tk.Tk()
        self.root.title("⚙️ Configurador - Marketplace")
        self.root.geometry("600x520")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        # Ocultar ventana mientras se configura
        self.root.withdraw()
        
        # Centrar ventana correctamente
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Mostrar ventana ya centrada
        self.root.deiconify()

        self._cargar_config()
        self._construir_ui()

    def _cargar_config(self):
        if os.path.exists(self.archivo_config):
            self.config.read(self.archivo_config, encoding='utf-8')

    def _get(self, seccion, clave, defecto=''):
        try:
            return self.config[seccion][clave].split('#')[0].strip()
        except:
            return defecto

    def _guardar_config(self):
        try:
            # General
            self.config['GENERAL']['cantidad_productos'] = self.var_cantidad.get()
            self.config['GENERAL']['modo'] = self.var_modo.get()

            # Publicación
            self.config['PUBLICACION']['auto_publicar'] = self.var_auto_publicar.get()
            self.config['PUBLICACION']['tiempo_entre_publicaciones'] = self.var_tiempo_pub.get()
            self.config['PUBLICACION']['max_publicaciones_por_dia'] = self.var_max_dia.get()
            self.config['PUBLICACION']['publicar_todos'] = self.var_publicar_todos.get()

            # WhatsApp / Extracción
            self.config['EXTRACCION']['contacto_whatsapp'] = self.var_contacto.get()
            self.config['EXTRACCION']['auto_scroll'] = self.var_scroll.get()
            self.config['EXTRACCION']['productos_por_extraccion'] = self.var_productos_extraccion.get()

            # Seguridad
            self.config['SEGURIDAD']['confirmacion_borrado'] = self.var_confirmacion.get()
            self.config['SEGURIDAD']['backup_antes_borrar'] = self.var_backup.get()

            with open(self.archivo_config, 'w', encoding='utf-8') as f:
                f.write("# ============================================================\n")
                f.write("# CONFIGURACIÓN GLOBAL DEL SISTEMA - MARKETPLACE\n")
                f.write("# ============================================================\n\n")
                self.config.write(f)

            messagebox.showinfo("✅ Éxito", "Configuración guardada correctamente")
            self.root.destroy()

        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al guardar: {e}")

    def _seccion(self, parent, texto):
        tk.Label(
            parent,
            text=texto,
            font=("Segoe UI", 10, "bold"),
            bg="#f0f0f0",
            fg="#333"
        ).pack(anchor='w', padx=20, pady=(12, 2))

    def _construir_ui(self):

        # Header
        header = tk.Frame(self.root, bg="#198754", pady=12)
        header.pack(fill='x')
        tk.Label(
            header,
            text="⚙️  Configurador - Marketplace",
            font=("Segoe UI", 14, "bold"),
            bg="#198754",
            fg="white"
        ).pack()

        # Notebook
        style = ttk.Style()
        style.configure('TNotebook.Tab', font=('Segoe UI', 9))

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # ==================== PESTAÑA GENERAL ====================
        tab_general = ttk.Frame(notebook)
        notebook.add(tab_general, text="⚙️ General")

        self._seccion(tab_general, "📦 Cantidad de productos (carpetas Articulo_X)")
        self.var_cantidad = tk.StringVar(value=self._get('GENERAL', 'cantidad_productos', '5'))
        tk.Spinbox(tab_general, from_=1, to=50, textvariable=self.var_cantidad, width=8, font=("Segoe UI", 10)).pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_general, "🎯 Modo de operación")
        tk.Label(tab_general, text="completo = extrae y publica | solo_extraer | solo_publicar",
                 font=("Segoe UI", 8), fg="gray", bg="#f0f0f0").pack(anchor='w', padx=20)
        self.var_modo = tk.StringVar(value=self._get('GENERAL', 'modo', 'completo'))
        frame_modo = tk.Frame(tab_general, bg="#f0f0f0")
        frame_modo.pack(anchor='w', padx=20, pady=(4, 12))
        for opcion in ['completo', 'solo_extraer', 'solo_publicar']:
            tk.Radiobutton(
                frame_modo, text=opcion,
                variable=self.var_modo, value=opcion,
                bg="#f0f0f0", font=("Segoe UI", 10)
            ).pack(side='left', padx=8)

        # ==================== PESTAÑA PUBLICACIÓN ====================
        tab_pub = ttk.Frame(notebook)
        notebook.add(tab_pub, text="🚀 Publicación")

        self._seccion(tab_pub, "🤖 Publicar automáticamente después de extraer")
        self.var_auto_publicar = tk.StringVar(value=self._get('PUBLICACION', 'auto_publicar', 'si'))
        frame_ap = tk.Frame(tab_pub, bg="#f0f0f0")
        frame_ap.pack(anchor='w', padx=20, pady=(0, 12))
        for opcion, label in [('si', 'Sí'), ('no', 'No')]:
            tk.Radiobutton(
                frame_ap, text=label,
                variable=self.var_auto_publicar, value=opcion,
                bg="#f0f0f0", font=("Segoe UI", 10)
            ).pack(side='left', padx=8)

        self._seccion(tab_pub, "⏱️ Tiempo entre publicaciones (segundos)")
        tk.Label(tab_pub, text="Recomendado: 10-30 segundos para evitar detección de spam",
                 font=("Segoe UI", 8), fg="gray", bg="#f0f0f0").pack(anchor='w', padx=20)
        self.var_tiempo_pub = tk.StringVar(value=self._get('PUBLICACION', 'tiempo_entre_publicaciones', '10'))
        tk.Spinbox(tab_pub, from_=5, to=300, textvariable=self.var_tiempo_pub, width=8, font=("Segoe UI", 10)).pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_pub, "📈 Máximo de publicaciones por día")
        tk.Label(tab_pub, text="Recomendado: 10-30 para evitar bloqueo de Facebook",
                 font=("Segoe UI", 8), fg="gray", bg="#f0f0f0").pack(anchor='w', padx=20)
        self.var_max_dia = tk.StringVar(value=self._get('PUBLICACION', 'max_publicaciones_por_dia', '20'))
        tk.Spinbox(tab_pub, from_=1, to=100, textvariable=self.var_max_dia, width=8, font=("Segoe UI", 10)).pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_pub, "📋 Publicar todos los productos disponibles")
        tk.Label(tab_pub, text="si = publica todos | no = solo publica el siguiente",
                 font=("Segoe UI", 8), fg="gray", bg="#f0f0f0").pack(anchor='w', padx=20)
        self.var_publicar_todos = tk.StringVar(value=self._get('PUBLICACION', 'publicar_todos', 'si'))
        frame_pt = tk.Frame(tab_pub, bg="#f0f0f0")
        frame_pt.pack(anchor='w', padx=20, pady=(0, 12))
        for opcion, label in [('si', 'Sí'), ('no', 'No')]:
            tk.Radiobutton(
                frame_pt, text=label,
                variable=self.var_publicar_todos, value=opcion,
                bg="#f0f0f0", font=("Segoe UI", 10)
            ).pack(side='left', padx=8)

        # ==================== PESTAÑA WHATSAPP ====================
        tab_wa = ttk.Frame(notebook)
        notebook.add(tab_wa, text="📱 WhatsApp")

        self._seccion(tab_wa, "👤 Nombre del contacto en WhatsApp Business")
        tk.Label(tab_wa, text="⚠️  Debe ser EXACTAMENTE igual a como aparece en WhatsApp",
                 font=("Segoe UI", 8), fg="gray", bg="#f0f0f0").pack(anchor='w', padx=20)
        self.var_contacto = tk.StringVar(value=self._get('EXTRACCION', 'contacto_whatsapp', 'Trabajo John'))
        tk.Entry(tab_wa, textvariable=self.var_contacto, width=40, font=("Segoe UI", 10)).pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_wa, "📜 Auto scroll (veces que hace scroll en catálogo)")
        self.var_scroll = tk.StringVar(value=self._get('EXTRACCION', 'auto_scroll', '5'))
        tk.Spinbox(tab_wa, from_=1, to=20, textvariable=self.var_scroll, width=8, font=("Segoe UI", 10)).pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_wa, "📦 Productos a extraer por vez")
        self.var_productos_extraccion = tk.StringVar(value=self._get('EXTRACCION', 'productos_por_extraccion', '5'))
        tk.Spinbox(tab_wa, from_=1, to=50, textvariable=self.var_productos_extraccion, width=8, font=("Segoe UI", 10)).pack(anchor='w', padx=20, pady=(0, 12))

        # ==================== PESTAÑA SEGURIDAD ====================
        tab_seg = ttk.Frame(notebook)
        notebook.add(tab_seg, text="🔒 Seguridad")

        self._seccion(tab_seg, "⏱️ Confirmación antes de borrar carpetas")
        tk.Label(tab_seg, text="si = countdown de 5-10s | no = borra inmediatamente",
                 font=("Segoe UI", 8), fg="gray", bg="#f0f0f0").pack(anchor='w', padx=20)
        self.var_confirmacion = tk.StringVar(value=self._get('SEGURIDAD', 'confirmacion_borrado', 'si'))
        frame_conf = tk.Frame(tab_seg, bg="#f0f0f0")
        frame_conf.pack(anchor='w', padx=20, pady=(0, 12))
        for opcion, label in [('si', 'Sí'), ('no', 'No')]:
            tk.Radiobutton(
                frame_conf, text=label,
                variable=self.var_confirmacion, value=opcion,
                bg="#f0f0f0", font=("Segoe UI", 10)
            ).pack(side='left', padx=8)

        self._seccion(tab_seg, "💾 Crear backup antes de borrar carpetas")
        tk.Label(tab_seg, text="si = guarda backup en 'backups/' | no = borra directo",
                 font=("Segoe UI", 8), fg="gray", bg="#f0f0f0").pack(anchor='w', padx=20)
        self.var_backup = tk.StringVar(value=self._get('SEGURIDAD', 'backup_antes_borrar', 'si'))
        frame_bk = tk.Frame(tab_seg, bg="#f0f0f0")
        frame_bk.pack(anchor='w', padx=20, pady=(0, 12))
        for opcion, label in [('si', 'Sí'), ('no', 'No')]:
            tk.Radiobutton(
                frame_bk, text=label,
                variable=self.var_backup, value=opcion,
                bg="#f0f0f0", font=("Segoe UI", 10)
            ).pack(side='left', padx=8)

        # ==================== BOTONES ====================
        frame_botones = tk.Frame(self.root, bg="#f0f0f0", pady=8)
        frame_botones.pack(fill='x', padx=10)

        tk.Button(
            frame_botones,
            text="❌ Cancelar",
            font=("Segoe UI", 10),
            bg="#e0e0e0",
            width=14,
            command=self.root.destroy
        ).pack(side='right', padx=5)

        tk.Button(
            frame_botones,
            text="💾 Guardar",
            font=("Segoe UI", 10, "bold"),
            bg="#198754",
            fg="white",
            width=14,
            command=self._guardar_config
        ).pack(side='right', padx=5)

    def ejecutar(self):
        self.root.mainloop()


def main():
    app = ConfiguradorGUI()
    app.ejecutar()


if __name__ == "__main__":
    main()