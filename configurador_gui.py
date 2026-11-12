import os
import sys
import configparser
import tkinter as tk
from tkinter import ttk, messagebox
from compartido.toast import Toast
from compartido.gestor_archivos import (
    MODULOS_DISPONIBLES, PLANTILLAS_ATENCION, VARIABLES_PLANTILLAS,
    leer_plantillas_atencion, guardar_plantillas_atencion
)


class ConfiguradorGUI:
    """Interfaz gráfica para configurar el sistema de Marketplace Automático"""

    def __init__(self):
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('--pestana', default=None)
        parser.add_argument('--ejecutar-despues', action='store_true', default=False)
        args, _ = parser.parse_known_args()
        self.pestana_inicial = args.pestana
        self.ejecutar_despues = args.ejecutar_despues

        self.config = configparser.RawConfigParser(delimiters=('=',))

        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.archivo_config = os.path.join(self.base_dir, "config_global.txt")

        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('AutomaPro.ConfiguradorMarketplace')
        except Exception:
            pass

        self.root = tk.Tk()
        self.root.withdraw()

        self.root.title("⚙️ Configurador - Marketplace Automático")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        try:
            base_ico = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
            ico = os.path.join(base_ico, 'iconos', 'settings.ico')
            self.root.iconbitmap(ico)
            # default= hace que las subventanas (Toplevel) hereden el ícono en vez de la pluma de Tkinter
            self.root.iconbitmap(default=ico)
        except Exception:
            pass

        width = 700
        height = 660
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        self._cargar_config()
        self.es_full = self._verificar_licencia_full()
        self._construir_ui()

        self.root.deiconify()

    def _verificar_licencia_full(self):
        """Verifica si la licencia es FULL/MASTER — solo cache, sin llamada de red"""
        try:
            from gestor_licencias import GestorLicencias
            gl = GestorLicencias("Marketplace")
            cache = gl._obtener_cache_local()
            if cache and cache.get('valida'):
                tipo = cache.get('tipo', 'TRIAL')
                return tipo in ['FULL', 'MASTER'] or cache.get('es_developer_permanente', False)
            return False
        except Exception:
            return False

    def _cargar_config(self):
        if os.path.exists(self.archivo_config):
            self.config.read(self.archivo_config, encoding='utf-8')

    def _poner(self, seccion, clave, valor):
        if not self.config.has_section(seccion):
            self.config.add_section(seccion)
        self.config[seccion][clave] = str(valor)

    def _guardar_config(self):
        try:
            self._poner('GENERAL', 'navegador', self.var_navegador.get())

            self._poner('PRODUCTOS', 'cantidad_por_ejecucion', self._numero_valido(self.var_cantidad, 1, 10, 1) if self.es_full else '1')

            self._poner('PUBLICACION', 'ubicacion', self.var_ubicacion.get().strip() or 'Guayaquil')
            self._poner('PUBLICACION', 'tiempo_entre_publicaciones', self._numero_valido(self.var_tiempo_entre, 0, 600, 10))
            self._poner('PUBLICACION', 'max_publicaciones_por_dia', self._numero_valido(self.var_max_dia, 1, 100, 20))
            self._poner('PUBLICACION', 'tiempo_entre_intentos', self._numero_valido(self.var_tiempo_intentos, 1, 30, 3))
            self._poner('PUBLICACION', 'max_intentos_por_publicacion', self._numero_valido(self.var_max_intentos, 1, 10, 3))
            self._poner('PUBLICACION', 'espera_despues_publicar', self._numero_valido(self.var_espera, 1, 30, 5))

            if self.es_full:
                self._poner('EXTRACCION', 'contacto_whatsapp', self.var_contacto_catalogo.get().strip())
                self._poner('EXTRACCION', 'productos_por_extraccion', self._numero_valido(self.var_productos_extraccion, 1, 50, 5))
                self._poner('EXTRACCION', 'auto_scroll', self._numero_valido(self.var_auto_scroll, 0, 30, 5))

                self._poner('ATENCION', 'contacto_vendedor_whatsapp', self.var_contacto_vendedor.get().strip())
                self._poner('ATENCION', 'nombre_vendedor', self.var_nombre_vendedor.get().strip())
                self._poner('ATENCION', 'max_insistencias', self._numero_valido(self.var_max_insistencias, 0, 5, 2))
                self._poner('ATENCION', 'max_conversaciones_por_ejecucion', self._numero_valido(self.var_max_conversaciones, 1, 50, 10))

            self._poner('NAVEGADOR', 'usar_perfil_existente', self.var_usar_perfil.get())
            self._poner('NAVEGADOR', 'maximizar_ventana', self.var_maximizar.get())

            self._poner('LIMITES', 'tiempo_minimo_entre_publicaciones_segundos', self._numero_valido(self.var_tiempo_minimo, 30, 600, 120))
            self._poner('LIMITES', 'permitir_forzar_publicacion_manual', self.var_forzar_manual.get())

            if self.es_full and hasattr(self, '_seq_vars') and hasattr(self, '_seq_orden'):
                activos = [c for c in self._seq_orden if self._seq_vars.get(c, tk.BooleanVar(value=False)).get()]
                self._poner('SECUENCIA', 'modulos_activos', ','.join(activos))

            with open(self.archivo_config, 'w', encoding='utf-8') as f:
                f.write("# ============================================================\n")
                f.write("# CONFIGURACIÓN GLOBAL - MARKETPLACE AUTOMÁTICO\n")
                f.write("# ============================================================\n\n")
                self.config.write(f)

            # Validaciones post-guardado — advertencias opcionales
            revisar = False
            if self.es_full:
                advertencias = []
                secuencia = self.config.get('SECUENCIA', 'modulos_activos', fallback='')
                lista_seq = [m.strip() for m in secuencia.split(',') if m.strip()]

                if 'extraer' in lista_seq and not self.var_contacto_catalogo.get().strip():
                    advertencias.append("• Falta el contacto de WhatsApp dueño del catálogo (pestaña Extractor)")
                if 'atender' in lista_seq and not self.var_contacto_vendedor.get().strip():
                    advertencias.append("• Falta el contacto de WhatsApp del vendedor (pestaña Atención)")

                if advertencias:
                    texto = "Configuración guardada, pero hay items pendientes:\n\n"
                    texto += "\n".join(advertencias)
                    texto += "\n\n¿Deseas revisar la configuración ahora?"
                    revisar = messagebox.askyesno("⚠️ Configuración incompleta", texto)
                else:
                    Toast.exito(self.root, "Configuración guardada correctamente")
            else:
                Toast.exito(self.root, "Configuración guardada correctamente")

            if not revisar:
                if self.ejecutar_despues:
                    import subprocess
                    exe = os.path.join(self.base_dir, "PublicadorMarketplace.exe")
                    if os.path.exists(exe):
                        subprocess.Popen([exe])
                self.root.after(3500, self.root.destroy)

        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al guardar: {e}")

    def _get(self, seccion, clave, defecto=''):
        try:
            valor = self.config[seccion][clave].split('#')[0].strip()
            return valor if valor else defecto
        except Exception:
            return defecto

    def _numero_valido(self, variable, minimo, maximo, defecto):
        try:
            return str(max(minimo, min(maximo, int(variable.get()))))
        except (ValueError, tk.TclError):
            return str(defecto)

    def _seccion(self, parent, texto):
        tk.Label(parent, text=texto, font=("Segoe UI", 10, "bold"), bg="#f0f0f0", fg="#333").pack(anchor='w', padx=20, pady=(12, 2))

    def _ayuda(self, parent, texto):
        tk.Label(parent, text=texto, font=("Segoe UI", 8), fg="gray", bg="#f0f0f0",
                 wraplength=620, justify='left').pack(anchor='w', padx=20)

    def _radio_si_no(self, parent, variable):
        frame = tk.Frame(parent, bg="#f0f0f0")
        frame.pack(anchor='w', padx=20, pady=(0, 12))
        for opcion, label in [('si', 'Sí'), ('no', 'No')]:
            tk.Radiobutton(frame, text=label, variable=variable, value=opcion, bg="#f0f0f0", font=("Segoe UI", 10)).pack(side='left', padx=8)

    def _radio_navegador(self, parent, variable):
        frame = tk.Frame(parent, bg="#f0f0f0")
        frame.pack(anchor='w', padx=20, pady=(0, 12))
        for opcion in ['firefox', 'chrome', 'edge']:
            tk.Radiobutton(frame, text=opcion.capitalize(), variable=variable, value=opcion, bg="#f0f0f0", font=("Segoe UI", 10)).pack(side='left', padx=8)

    def _spinbox(self, parent, variable, desde, hasta, estado='normal'):
        tk.Spinbox(parent, from_=desde, to=hasta, textvariable=variable, width=8, font=("Segoe UI", 10),
                   state=estado).pack(anchor='w', padx=20, pady=(0, 12))

    def _banner_full(self, parent):
        banner = tk.Frame(parent, bg="#fff3cd", pady=6)
        banner.pack(fill='x', padx=20, pady=(8, 0))
        tk.Label(banner, text="🔒 Estas funciones están disponibles en la versión Completa",
                 font=("Segoe UI", 9, "bold"), fg="#856404", bg="#fff3cd").pack()

    def _construir_ui(self):
        header = tk.Frame(self.root, bg="#198754", pady=12)
        header.pack(fill='x')
        tk.Label(header, text="⚙️  Configurador - Marketplace Automático", font=("Segoe UI", 14, "bold"), bg="#198754", fg="white").pack()

        style = ttk.Style()
        style.configure('TNotebook.Tab', font=('Segoe UI', 9))

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        estado_full = 'normal' if self.es_full else 'disabled'

        # ==================== PESTAÑA PUBLICAR ====================
        tab_pub = ttk.Frame(notebook)
        notebook.add(tab_pub, text="▶️ Publicar")

        tk.Label(tab_pub, text="Configuración para publicar tus productos en Facebook Marketplace",
                 font=("Segoe UI", 9), fg="#555", bg="#f0f0f0").pack(anchor='w', padx=20, pady=(10, 0))

        self._seccion(tab_pub, "🌐 Navegador para Facebook y WhatsApp")
        self.var_navegador = tk.StringVar(value=self._get('GENERAL', 'navegador', 'firefox'))
        self._radio_navegador(tab_pub, self.var_navegador)

        self._seccion(tab_pub, "📍 Ciudad de las publicaciones")
        self.var_ubicacion = tk.StringVar(value=self._get('PUBLICACION', 'ubicacion', 'Guayaquil'))
        tk.Entry(tab_pub, textvariable=self.var_ubicacion, width=30, font=("Segoe UI", 10)).pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_pub, "🔢 Productos a publicar por ejecución")
        self.var_cantidad = tk.StringVar(value=self._get('PRODUCTOS', 'cantidad_por_ejecucion', '1') if self.es_full else '1')
        self._spinbox(tab_pub, self.var_cantidad, 1, 10, estado_full)
        if not self.es_full:
            tk.Label(tab_pub, text="🔒 Publicar varios productos por ejecución requiere versión Completa",
                     font=("Segoe UI", 8), bg="#fff3cd", fg="#856404").pack(anchor='w', padx=20, pady=(0, 6))

        self._seccion(tab_pub, "⏳ Espera entre un producto y el siguiente (segundos)")
        self.var_tiempo_entre = tk.StringVar(value=self._get('PUBLICACION', 'tiempo_entre_publicaciones', '10'))
        self._spinbox(tab_pub, self.var_tiempo_entre, 0, 600)

        self._seccion(tab_pub, "📅 Máximo de publicaciones por día")
        self._ayuda(tab_pub, "Recomendado: 10 a 30. Muchas publicaciones seguidas pueden hacer que Facebook te bloquee.")
        self.var_max_dia = tk.StringVar(value=self._get('PUBLICACION', 'max_publicaciones_por_dia', '20'))
        self._spinbox(tab_pub, self.var_max_dia, 1, 100)

        # ==================== PESTAÑA EXTRACTOR ====================
        tab_ext = ttk.Frame(notebook)
        notebook.add(tab_ext, text="🛍️ Extractor")

        tk.Label(tab_ext, text="De dónde se extraen los productos: el catálogo de un contacto de WhatsApp Business",
                 font=("Segoe UI", 9), fg="#555", bg="#f0f0f0").pack(anchor='w', padx=20, pady=(10, 0))
        if not self.es_full:
            self._banner_full(tab_ext)

        self._seccion(tab_ext, "👤 Contacto de WhatsApp dueño del catálogo")
        self._ayuda(tab_ext, "⚠️  Debe ser EXACTAMENTE igual a como aparece en tu WhatsApp")
        self.var_contacto_catalogo = tk.StringVar(value=self._get('EXTRACCION', 'contacto_whatsapp', ''))
        tk.Entry(tab_ext, textvariable=self.var_contacto_catalogo, width=40, font=("Segoe UI", 10),
                 state=estado_full).pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_ext, "📦 Productos a extraer por vez")
        self.var_productos_extraccion = tk.StringVar(value=self._get('EXTRACCION', 'productos_por_extraccion', '5'))
        self._spinbox(tab_ext, self.var_productos_extraccion, 1, 50, estado_full)

        self._seccion(tab_ext, "🖱️ Desplazamientos para cargar el catálogo")
        self._ayuda(tab_ext, "Cuántas veces baja la lista del catálogo para que WhatsApp cargue más productos")
        self.var_auto_scroll = tk.StringVar(value=self._get('EXTRACCION', 'auto_scroll', '5'))
        self._spinbox(tab_ext, self.var_auto_scroll, 0, 30, estado_full)

        # ==================== PESTAÑA ATENCIÓN ====================
        tab_ate = ttk.Frame(notebook)
        notebook.add(tab_ate, text="💬 Atención")

        tk.Label(tab_ate, text="Respuesta automática a las personas que escriben por tus productos en Marketplace",
                 font=("Segoe UI", 9), fg="#555", bg="#f0f0f0").pack(anchor='w', padx=20, pady=(10, 0))
        if not self.es_full:
            self._banner_full(tab_ate)

        self._seccion(tab_ate, "📱 Contacto de WhatsApp del vendedor (a quien se avisa)")
        self._ayuda(tab_ate, "⚠️  Debe ser EXACTAMENTE igual a como aparece en tu WhatsApp")
        self.var_contacto_vendedor = tk.StringVar(value=self._get('ATENCION', 'contacto_vendedor_whatsapp', ''))
        tk.Entry(tab_ate, textvariable=self.var_contacto_vendedor, width=40, font=("Segoe UI", 10),
                 state=estado_full).pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_ate, "🙋 Nombre del vendedor (se le dice al interesado quién lo contactará)")
        self.var_nombre_vendedor = tk.StringVar(value=self._get('ATENCION', 'nombre_vendedor', ''))
        tk.Entry(tab_ate, textvariable=self.var_nombre_vendedor, width=40, font=("Segoe UI", 10),
                 state=estado_full).pack(anchor='w', padx=20, pady=(0, 12))

        fila_numeros = tk.Frame(tab_ate, bg="#f0f0f0")
        fila_numeros.pack(fill='x')
        col_izq = tk.Frame(fila_numeros, bg="#f0f0f0")
        col_izq.pack(side='left', anchor='n')
        col_der = tk.Frame(fila_numeros, bg="#f0f0f0")
        col_der.pack(side='left', anchor='n', padx=(30, 0))

        self._seccion(col_izq, "🔁 Veces que se insiste por el celular")
        self.var_max_insistencias = tk.StringVar(value=self._get('ATENCION', 'max_insistencias', '2'))
        self._spinbox(col_izq, self.var_max_insistencias, 0, 5, estado_full)

        self._seccion(col_der, "💬 Conversaciones por ejecución")
        self.var_max_conversaciones = tk.StringVar(value=self._get('ATENCION', 'max_conversaciones_por_ejecucion', '10'))
        self._spinbox(col_der, self.var_max_conversaciones, 1, 50, estado_full)

        self._seccion(tab_ate, "📝 Mensajes plantilla")
        tk.Button(tab_ate,
            text="📝  Editar mensajes plantilla" if self.es_full else "🔒  Editar mensajes plantilla  —  versión Completa",
            font=("Segoe UI", 10, "bold") if self.es_full else ("Segoe UI", 10),
            bg="#198754" if self.es_full else "#e0e0e0",
            fg="white" if self.es_full else "#9e9e9e",
            command=self._abrir_editor_plantillas if self.es_full else lambda: messagebox.showinfo(
                "🔒 Versión Completa", "Adquiere la versión Completa en automapro.com para atender interesados.")
        ).pack(fill='x', padx=20, ipady=6)

        # ==================== PESTAÑA SECUENCIA ====================
        if self.es_full:
            tab_seq = ttk.Frame(notebook)
            notebook.add(tab_seq, text="⚡ Secuencia")

            tk.Label(tab_seq,
                text="Define qué módulos se ejecutan y en qué orden al usar 'Ejecutar Secuencia'. "
                     "También es el valor inicial de las tareas automáticas nuevas; cada tarea guarda después sus propias acciones.",
                font=("Segoe UI", 9), bg="#f0f0f0", fg="#555", wraplength=560, justify='left'
            ).pack(anchor='w', padx=20, pady=(10, 0))

            banner_seq = tk.Frame(tab_seq, bg="#e3f2fd", pady=6)
            banner_seq.pack(fill='x', padx=20, pady=(8, 0))
            tk.Label(banner_seq,
                text="💡 Usa ↑ ↓ para reordenar. Ejemplo: Extraer → Publicar → Atender.",
                font=("Segoe UI", 8), bg="#e3f2fd", fg="#198754", wraplength=540
            ).pack(padx=10)

            self._seccion(tab_seq, "📋 Módulos a ejecutar (activa/desactiva y ordena)")

            frame_seq = tk.Frame(tab_seq, bg="#f0f0f0")
            frame_seq.pack(fill='x', padx=20, pady=(0, 10))

            seq_guardada = self._get('SECUENCIA', 'modulos_activos', 'publicar')
            seq_activos = set(seq_guardada.split(','))
            seq_lista = [m.strip() for m in seq_guardada.split(',') if m.strip()]
            for clave, _ in MODULOS_DISPONIBLES:
                if clave not in seq_lista:
                    seq_lista.append(clave)

            self._seq_vars = {}
            self._seq_orden = list(seq_lista)
            self._seq_container = tk.Frame(frame_seq, bg="#f0f0f0")
            self._seq_container.pack(fill='x')

            mods_dict = dict(MODULOS_DISPONIBLES)

            def _render_seq():
                for w in self._seq_container.winfo_children():
                    w.destroy()
                for idx, clave in enumerate(self._seq_orden):
                    if clave not in mods_dict:
                        continue
                    label = mods_dict[clave]
                    fila = tk.Frame(self._seq_container, bg="#ffffff", relief='solid', borderwidth=1)
                    fila.pack(fill='x', pady=2)
                    if clave not in self._seq_vars:
                        self._seq_vars[clave] = tk.BooleanVar(value=clave in seq_activos)
                    tk.Checkbutton(fila, text=label, variable=self._seq_vars[clave],
                        font=("Segoe UI", 10), bg="#ffffff", anchor='w').pack(
                        side='left', padx=8, pady=4, fill='x', expand=True)
                    btn_frame = tk.Frame(fila, bg="#ffffff")
                    btn_frame.pack(side='right', padx=4)
                    def _subir(i=idx):
                        if i > 0:
                            self._seq_orden[i], self._seq_orden[i-1] = self._seq_orden[i-1], self._seq_orden[i]
                            _render_seq()
                    def _bajar(i=idx):
                        if i < len(self._seq_orden) - 1:
                            self._seq_orden[i], self._seq_orden[i+1] = self._seq_orden[i+1], self._seq_orden[i]
                            _render_seq()
                    tk.Button(btn_frame, text="↑", font=("Segoe UI", 8), width=2, command=_subir).pack(side='left', padx=1)
                    tk.Button(btn_frame, text="↓", font=("Segoe UI", 8), width=2, command=_bajar).pack(side='left', padx=1)

            self._render_seq = _render_seq
            _render_seq()

        # ==================== PESTAÑA AVANZADO ====================
        tab_adv = ttk.Frame(notebook)
        notebook.add(tab_adv, text="⚙️ Avanzado")

        tk.Label(tab_adv, text="Ajustes del navegador y límites de seguridad para evitar bloqueos",
                 font=("Segoe UI", 9), fg="#555", bg="#f0f0f0").pack(anchor='w', padx=20, pady=(10, 0))

        fila_adv = tk.Frame(tab_adv, bg="#f0f0f0")
        fila_adv.pack(fill='x')
        adv_izq = tk.Frame(fila_adv, bg="#f0f0f0")
        adv_izq.pack(side='left', anchor='n')
        adv_der = tk.Frame(fila_adv, bg="#f0f0f0")
        adv_der.pack(side='left', anchor='n', padx=(30, 0))

        self._seccion(adv_izq, "👤 Usar perfil existente de Facebook")
        self.var_usar_perfil = tk.StringVar(value=self._get('NAVEGADOR', 'usar_perfil_existente', 'si'))
        self._radio_si_no(adv_izq, self.var_usar_perfil)

        self._seccion(adv_der, "🖥️ Maximizar ventana al iniciar")
        self.var_maximizar = tk.StringVar(value=self._get('NAVEGADOR', 'maximizar_ventana', 'si'))
        self._radio_si_no(adv_der, self.var_maximizar)

        self._seccion(adv_izq, "⏱️ Tiempo entre intentos (seg)")
        self.var_tiempo_intentos = tk.StringVar(value=self._get('PUBLICACION', 'tiempo_entre_intentos', '3'))
        self._spinbox(adv_izq, self.var_tiempo_intentos, 1, 30)

        self._seccion(adv_der, "🔄 Máximo de intentos por producto")
        self.var_max_intentos = tk.StringVar(value=self._get('PUBLICACION', 'max_intentos_por_publicacion', '3'))
        self._spinbox(adv_der, self.var_max_intentos, 1, 10)

        self._seccion(adv_izq, "⏳ Espera después de publicar (seg)")
        self.var_espera = tk.StringVar(value=self._get('PUBLICACION', 'espera_despues_publicar', '5'))
        self._spinbox(adv_izq, self.var_espera, 1, 30)

        self._seccion(adv_der, "⏰ Tiempo mínimo entre ejecuciones (seg)")
        self.var_tiempo_minimo = tk.StringVar(value=self._get('LIMITES', 'tiempo_minimo_entre_publicaciones_segundos', '120'))
        self._spinbox(adv_der, self.var_tiempo_minimo, 30, 600)

        self._seccion(tab_adv, "🔓 Permitir forzar publicación manual")
        self._ayuda(tab_adv, "Sí = permite saltarse el tiempo mínimo en ejecución manual")
        self.var_forzar_manual = tk.StringVar(value=self._get('LIMITES', 'permitir_forzar_publicacion_manual', 'si'))
        self._radio_si_no(tab_adv, self.var_forzar_manual)

        # Navegar a pestaña inicial si viene del panel
        if self.pestana_inicial == 'extractor':
            notebook.select(tab_ext)
        elif self.pestana_inicial == 'atencion':
            notebook.select(tab_ate)
        elif self.pestana_inicial == 'secuencia' and self.es_full:
            notebook.select(tab_seq)

        # ==================== BOTONES ====================
        frame_botones = tk.Frame(self.root, bg="#f0f0f0", pady=8)
        frame_botones.pack(fill='x', padx=10)

        tk.Button(frame_botones, text="❌ Cancelar", font=("Segoe UI", 10), bg="#e0e0e0",
                  width=14, command=self.root.destroy).pack(side='right', padx=5)

        tk.Button(frame_botones, text="💾 Guardar", font=("Segoe UI", 10, "bold"),
                  bg="#198754", fg="white", width=14, command=self._guardar_config).pack(side='right', padx=5)

    def _abrir_editor_plantillas(self):
        """Ventana para editar los 4 mensajes plantilla de la atención de interesados"""
        ventana = tk.Toplevel(self.root)
        ventana.withdraw()
        ventana.title("📝 Mensajes plantilla")
        ventana.resizable(False, False)
        ventana.configure(bg="#f0f0f0")
        ventana.transient(self.root)
        ventana.grab_set()

        header = tk.Frame(ventana, bg="#198754", pady=10)
        header.pack(fill='x')
        tk.Label(header, text="📝 Mensajes plantilla", font=("Segoe UI", 13, "bold"),
                 bg="#198754", fg="white").pack()
        tk.Label(header, text=f"Variables: {VARIABLES_PLANTILLAS}", font=("Segoe UI", 8),
                 bg="#198754", fg="white").pack()

        cuerpo = tk.Frame(ventana, bg="#f0f0f0")
        cuerpo.pack(fill='both', expand=True, padx=15, pady=8)

        plantillas = leer_plantillas_atencion()
        cajas = {}
        for clave, titulo in PLANTILLAS_ATENCION:
            tk.Label(cuerpo, text=titulo, font=("Segoe UI", 9, "bold"), bg="#f0f0f0",
                     fg="#333").pack(anchor='w', pady=(6, 2))
            caja = tk.Text(cuerpo, height=4, width=70, font=("Segoe UI", 9), wrap='word')
            caja.insert('1.0', plantillas.get(clave, ''))
            caja.pack(fill='x')
            cajas[clave] = caja

        def cerrar():
            ventana.grab_release()
            ventana.destroy()

        def guardar():
            nuevas = {clave: caja.get('1.0', tk.END).strip() for clave, caja in cajas.items()}
            vacias = [titulo for clave, titulo in PLANTILLAS_ATENCION if not nuevas[clave]]
            if vacias:
                messagebox.showerror("❌ Plantillas", "Ningún mensaje puede quedar vacío:\n\n" + "\n".join(vacias),
                                     parent=ventana)
                return
            if guardar_plantillas_atencion(nuevas):
                cerrar()
                Toast.exito(self.root, "Mensajes plantilla guardados")
            else:
                messagebox.showerror("❌ Plantillas", "No se pudieron guardar los mensajes", parent=ventana)

        frame_btns = tk.Frame(ventana, bg="#f0f0f0", pady=10)
        frame_btns.pack(fill='x', padx=15)
        tk.Button(frame_btns, text="❌ Cancelar", font=("Segoe UI", 10), bg="#e0e0e0", width=14,
                  command=cerrar).pack(side='right', padx=5)
        tk.Button(frame_btns, text="💾 Guardar", font=("Segoe UI", 10, "bold"), bg="#198754", fg="white",
                  width=14, command=guardar).pack(side='right', padx=5)

        ventana.protocol("WM_DELETE_WINDOW", cerrar)
        ventana.update_idletasks()
        ancho, alto = 620, 575
        x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
        y = (ventana.winfo_screenheight() // 2) - (alto // 2)
        ventana.geometry(f'{ancho}x{alto}+{x}+{y}')
        ventana.deiconify()

    def ejecutar(self):
        self.root.mainloop()


def main():
    app = ConfiguradorGUI()
    app.ejecutar()


if __name__ == "__main__":
    main()
