import os
import sys
import tkinter as tk
from tkinter import messagebox
import subprocess
from gestor_licencias import GestorLicencias
from gestor_registro import GestorRegistro
from compartido.gestor_archivos import migrar_tareas_antiguas
from compartido.toast import Toast


class PanelControl:
    """Panel de control principal - Marketplace Automático"""

    def __init__(self):
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('AutomaPro.PanelControlMarketplace')
        except Exception:
            pass

        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title("🛍️ Marketplace Automático - Panel de Control")
        self.root.geometry("700x680")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        try:
            base_ico = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
            ico = os.path.join(base_ico, 'iconos', 'dashboard.ico')
            self.root.iconbitmap(ico)
            # default= hace que las subventanas (Toplevel) hereden el ícono en vez de la pluma de Tkinter
            self.root.iconbitmap(default=ico)
        except Exception:
            pass

        self.gestor_licencias = GestorLicencias()
        self.licencia = self._verificar_licencia()

        # Ruta base del ejecutable
        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

        if not self.licencia:
            self.root.destroy()
            return

        self._construir_ui()

        # Centrar después de construir la UI completa
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        self.root.deiconify()

        self._verificar_actualizacion()
        self._migrar_tareas_en_segundo_plano()

    def _migrar_tareas_en_segundo_plano(self):
        """Convierte en silencio las tareas automáticas antiguas al formato con --tarea"""
        import threading
        def migrar():
            try:
                migradas = migrar_tareas_antiguas()
            except Exception as e:
                print(f"⚠️  Error actualizando tareas automáticas: {e}")
                return
            if migradas:
                self.root.after(0, lambda: self._toast("🔄 Tareas automáticas actualizadas",
                                                       f"{migradas} tarea(s) convertida(s) al formato nuevo"))
        threading.Thread(target=migrar, daemon=True).start()

    def _exe(self, nombre):
        """Retorna ruta al .exe en la misma carpeta del ejecutable"""
        if getattr(sys, 'frozen', False):
            base = os.path.dirname(sys.executable)
        else:
            base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, nombre)

    def _verificar_licencia(self):
        """Verifica licencia — usa caché si no hay código guardado (caso TRIAL)"""
        codigo = self.gestor_licencias.obtener_codigo_guardado()

        if not codigo:
            # Sin código — lanzar wizard automáticamente
            import subprocess
            if getattr(sys, 'frozen', False):
                wizard = os.path.join(os.path.dirname(sys.executable), "WizardMarketplace.exe")
            else:
                wizard = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wizard_primera_vez.py")
            if os.path.exists(wizard):
                subprocess.Popen([wizard] if wizard.endswith('.exe') else [sys.executable, wizard])
            else:
                messagebox.showwarning("Sin Licencia", "No hay licencia configurada.\n\nEjecuta el Wizard de primera vez.")
            return None

        resultado = self.gestor_licencias.verificar_licencia(codigo, mostrar_mensajes=False)

        if not resultado['valida']:
            messagebox.showerror("Licencia Inválida", "Tu licencia no es válida o ha expirado.")
            return None

        # Verificar expiración para licencias TRIAL
        tipo = resultado.get('tipo', 'TRIAL')
        if tipo == 'TRIAL':
            dias = resultado.get('diasRestantes', 0)
            if dias is not None and dias <= 0:
                messagebox.showwarning(
                    "⏰ Período de Prueba Expirado",
                    "Tu período de prueba ha terminado.\n\n"
                    "Adquiere la versión Completa para seguir usando todas las funciones.\n\n"
                    "Visita: automapro-frontend.vercel.app"
                )
                self._abrir_upgrade()
                return None

        return resultado

    def _verificar_actualizacion(self):
        """Verifica si hay una versión nueva disponible en segundo plano"""
        import threading
        def consultar():
            try:
                import sys, os
                base = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
                with open(os.path.join(base, 'version.txt'), 'r') as f:
                    version_local = f.read().strip()
            except Exception:
                version_local = "1.0.0"
            resultado = self.gestor_licencias.verificar_actualizacion(version_local)
            if resultado.get('hay_actualizacion'):
                version_nueva = resultado.get('version_nueva')
                ruta_archivo = resultado.get('ruta_archivo', '')
                self.root.after(0, lambda: self._mostrar_ventana_actualizacion(version_local, version_nueva, ruta_archivo))
        threading.Thread(target=consultar, daemon=True).start()

    def _mostrar_ventana_actualizacion(self, version_local, version_nueva, ruta_archivo):
        """Muestra ventana modal de actualización disponible"""
        import tkinter as tk
        from tkinter import ttk
        import urllib.request
        import subprocess
        import tempfile
        import os
        import threading

        ventana = tk.Toplevel(self.root)
        ventana.title("Actualización Disponible")
        ventana.resizable(False, False)
        ventana.configure(bg="#f0f0f0")
        ventana.grab_set()

        # Centrar ventana
        ventana.withdraw()
        ventana.update_idletasks()
        w, h = 420, 280
        x = (ventana.winfo_screenwidth() // 2) - (w // 2)
        y = (ventana.winfo_screenheight() // 2) - (h // 2)
        ventana.geometry(f"{w}x{h}+{x}+{y}")
        ventana.deiconify()

        # Header
        header = tk.Frame(ventana, bg="#198754", pady=15)
        header.pack(fill='x')
        tk.Label(
            header,
            text="🔄  Actualización Disponible",
            font=("Segoe UI", 13, "bold"),
            bg="#198754",
            fg="white"
        ).pack()

        # Cuerpo
        cuerpo = tk.Frame(ventana, bg="#f0f0f0", padx=30, pady=15)
        cuerpo.pack(fill='both', expand=True)

        tk.Label(cuerpo, text=f"Versión actual:      {version_local}", font=("Segoe UI", 10), bg="#f0f0f0", anchor='w').pack(fill='x')
        tk.Label(cuerpo, text=f"Nueva versión:       {version_nueva}", font=("Segoe UI", 10, "bold"), bg="#f0f0f0", fg="#198754", anchor='w').pack(fill='x', pady=(0, 10))
        tk.Label(
            cuerpo,
            text="Hay una nueva versión disponible.\nHaz clic en Actualizar para instalarla automáticamente.",
            font=("Segoe UI", 9),
            bg="#f0f0f0",
            fg="#555555",
            justify='left'
        ).pack(fill='x')

        # Barra de progreso (oculta inicialmente)
        progreso_frame = tk.Frame(ventana, bg="#f0f0f0", padx=30)
        progreso_frame.pack(fill='x')
        label_progreso = tk.Label(progreso_frame, text="", font=("Segoe UI", 9), bg="#f0f0f0", fg="#555555")
        label_progreso.pack(anchor='w')
        barra = ttk.Progressbar(progreso_frame, mode='indeterminate', length=360)

        # Botones
        frame_btns = tk.Frame(ventana, bg="#f0f0f0", pady=10)
        frame_btns.pack(fill='x', padx=30)

        def recordar_despues():
            ventana.grab_release()
            ventana.destroy()

        def actualizar_ahora():
            if not ruta_archivo:
                recordar_despues()
                return

            btn_actualizar.config(state='disabled')
            btn_despues.config(state='disabled')
            label_progreso.config(text="Descargando actualización...")
            barra.pack(fill='x', pady=5)
            barra.start(10)
            ventana.update()

            def descargar_e_instalar():
                try:
                    tmp = tempfile.mktemp(suffix=".exe")
                    urllib.request.urlretrieve(ruta_archivo, tmp)

                    self.root.after(0, lambda: label_progreso.config(text="Instalando..."))
                    self.root.after(500, lambda: _ejecutar_instalador(tmp))
                except Exception as e:
                    self.root.after(0, lambda: label_progreso.config(text=f"Error: {e}"))
                    self.root.after(0, lambda: barra.stop())

            def _ejecutar_instalador(ruta_tmp):
                barra.stop()
                ventana.grab_release()
                ventana.destroy()
                self.root.destroy()
                subprocess.Popen([ruta_tmp, '/SILENT'])

            threading.Thread(target=descargar_e_instalar, daemon=True).start()

        btn_despues = tk.Button(
            frame_btns,
            text="Recordar después",
            font=("Segoe UI", 10),
            bg="#e0e0e0",
            width=16,
            command=recordar_despues
        )
        btn_despues.pack(side='left')

        btn_actualizar = tk.Button(
            frame_btns,
            text="Actualizar ahora",
            font=("Segoe UI", 10, "bold"),
            bg="#198754",
            fg="white",
            width=16,
            command=actualizar_ahora
        )
        btn_actualizar.pack(side='right')

    def _construir_ui(self):
        """Construye la interfaz del panel"""
        tipo_licencia = self.licencia.get('tipo', 'TRIAL')
        es_full = tipo_licencia in ['FULL', 'MASTER'] or self.licencia.get('developer_permanente')

        # ==================== HEADER ====================
        header = tk.Frame(self.root, bg="#198754", pady=15)
        header.pack(fill='x')

        # Leer versión desde version.txt
        try:
            ruta_version = os.path.join(self.base_dir, 'version.txt')
            with open(ruta_version, 'r', encoding='utf-8') as f:
                version = f.read().strip()
        except Exception:
            version = '1.0.0'

        tk.Label(
            header,
            text="🛍️ Marketplace Automático",
            font=("Segoe UI", 20, "bold"),
            bg="#198754",
            fg="white"
        ).pack()

        tk.Label(
            header,
            text=f"v{version}",
            font=("Segoe UI", 9),
            bg="#198754",
            fg="#c8e6d4"
        ).pack()

        # Badge de licencia
        if self.licencia.get('developer_permanente'):
            texto_lic = "👑 LICENCIA MAESTRA"
            color_lic = "#6f42c1"
        elif tipo_licencia == "FULL":
            texto_lic = "✅ LICENCIA COMPLETA"
            color_lic = "#28a745"
        else:
            dias = self.licencia.get('diasRestantes', 0)
            texto_lic = f"⚠️  PRUEBA — {dias} días restantes"
            color_lic = "#e65100"

        tk.Label(
            header,
            text=texto_lic,
            font=("Segoe UI", 10, "bold"),
            bg=color_lic,
            fg="white",
            padx=15,
            pady=4
        ).pack(pady=(8, 0))

        # Banner upgrade (solo TRIAL)
        if not es_full:
            banner = tk.Frame(self.root, bg="#fff3cd", pady=8)
            banner.pack(fill='x')
            tk.Label(
                banner,
                text="🔓 Desbloquea catálogo de WhatsApp, atención de interesados y tareas automáticas",
                font=("Segoe UI", 9),
                bg="#fff3cd",
                fg="#856404"
            ).pack(side='left', padx=(15, 10))
            tk.Button(
                banner,
                text="⬆️ Comprar versión Completa",
                font=("Segoe UI", 9, "bold"),
                bg="#ffc107",
                fg="#212529",
                cursor="hand2",
                relief='flat',
                padx=10,
                command=self._abrir_upgrade
            ).pack(side='right', padx=(0, 15))

        # ==================== GRID PRINCIPAL ====================
        container = tk.Frame(self.root, bg="#f0f0f0")
        container.pack(fill='both', expand=True, padx=25, pady=15)

        grid = tk.Frame(container, bg="#f0f0f0")
        grid.pack(fill='both', expand=True)

        self._botones_grid = []  # Para bloquear/desbloquear todos juntos

        # Fila 0
        self._boton(grid, "⚡\nAcciones", "Publicar y automatizar",
                    self._abrir_acciones, row=0, col=0, color="#e65100")
        self._boton(grid, "⚙️\nConfigurador", "Ajustar configuración",
                    self._abrir_configurador, row=0, col=1, en_hilo=True)

        # Fila 1
        if es_full:
            self._boton(grid, "🛍️\nProductos", "Crear y editar productos",
                        self._abrir_gestor_articulos, row=1, col=0, en_hilo=True)
        else:
            self._boton(grid, "🛍️\nProductos", "Ver tus productos",
                        self._abrir_carpeta_productos, row=1, col=0)
        self._boton(grid, "📊\nEstadísticas", "Ver historial",
                    self._ver_estadisticas, row=1, col=1)

        # Fila 2
        if es_full:
            self._boton(grid, "🗓️\nTareas Automáticas", "Programar publicaciones",
                        self._gestionar_tareas, row=2, col=0, color="#28a745", en_hilo=True)
        else:
            self._boton(grid, "🔒\nTareas Automáticas", "Solo versión Completa",
                        self._mostrar_mensaje_upgrade, row=2, col=0, color="#9e9e9e")

        self._boton(grid, "❓\nAyuda", "Cómo usar el sistema",
                    self._mostrar_ayuda, row=2, col=1)

        # Fila 3
        self._boton(grid, "❌\nSalir", "Cerrar panel",
                    self.root.destroy, row=3, col=0, color="#dc3545")

    def _bloquear_grid(self):
        """Bloquea todos los botones del grid"""
        self.root.config(cursor="wait")
        for frame, widgets in self._botones_grid:
            frame.config(cursor="", bg="#e0e0e0")
            for w in widgets:
                w.config(bg="#e0e0e0")
                w.unbind('<Button-1>')
                w.unbind('<Enter>')
                w.unbind('<Leave>')
            frame.unbind('<Button-1>')
            frame.unbind('<Enter>')
            frame.unbind('<Leave>')

    def _desbloquear_grid(self):
        """Restaura todos los botones del grid"""
        self.root.config(cursor="")
        for frame, widgets in self._botones_grid:
            frame.config(cursor="hand2", bg="white")
            cmd = frame._cmd
            en_hilo = frame._en_hilo
            for w in widgets:
                w.config(bg="white")
                accion = (lambda c=cmd: self._lanzar_en_hilo(c)) if en_hilo else cmd
                w.bind('<Button-1>', lambda e, a=accion: a())
                w.bind('<Enter>', lambda e, f=frame: f.config(bg="#f8f9fa"))
                w.bind('<Leave>', lambda e, f=frame: f.config(bg="white"))
            accion = (lambda c=cmd: self._lanzar_en_hilo(c)) if en_hilo else cmd
            frame.bind('<Button-1>', lambda e, a=accion: a())
            frame.bind('<Enter>', lambda e, f=frame: f.config(bg="#f8f9fa"))
            frame.bind('<Leave>', lambda e, f=frame: f.config(bg="white"))

    def _lanzar_accion(self, cmd):
        """Para acciones que abren ventanas: bloquea grid brevemente para evitar doble clic"""
        self._bloquear_grid()
        self.root.after(300, self._desbloquear_grid)
        cmd()

    def _lanzar_subprocess(self, cmd):
        """Para subprocesos externos: bloquea grid, espera cierre del proceso, desbloquea"""
        self._bloquear_grid()
        import threading
        def _hilo():
            try:
                cmd()
            finally:
                pass  # El cmd maneja su propio desbloqueo
        threading.Thread(target=_hilo, daemon=True).start()

    def _lanzar_en_hilo(self, cmd):
        """Para subprocesos: bloquea grid, corre en hilo, desbloquea al terminar"""
        self._bloquear_grid()
        import threading
        def _hilo():
            try:
                cmd()
            finally:
                self.root.after(0, self._desbloquear_grid)
        threading.Thread(target=_hilo, daemon=True).start()

    def _centrar_ventana(self, ventana, ancho, alto):
        """Centra una ventana en pantalla antes de mostrarla"""
        x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
        y = (ventana.winfo_screenheight() // 2) - (alto // 2)
        ventana.geometry(f'{ancho}x{alto}+{x}+{y}')

    def _boton(self, parent, texto, subtexto, comando, row, col, color="#198754", en_hilo=False):
        """Crea un botón estilizado en el grid"""
        frame = tk.Frame(parent, bg="white", relief='solid', borderwidth=1, cursor="hand2")
        frame.grid(row=row, column=col, padx=8, pady=8, sticky='nsew')
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        frame._cmd = comando
        frame._en_hilo = en_hilo

        lbl1 = tk.Label(frame, text=texto, font=("Segoe UI", 13, "bold"), bg="white", fg=color)
        lbl1.pack(expand=True, pady=(12, 3))

        lbl2 = tk.Label(frame, text=subtexto, font=("Segoe UI", 8), bg="white", fg="gray")
        lbl2.pack(expand=True, pady=(0, 12))

        if en_hilo:
            accion = lambda c=comando: self._lanzar_en_hilo(c)
        else:
            accion = lambda c=comando: self._lanzar_accion(c)
        for w in [frame, lbl1, lbl2]:
            w.bind('<Button-1>', lambda e, a=accion: a())
            w.bind('<Enter>', lambda e, f=frame: f.config(bg="#f8f9fa"))
            w.bind('<Leave>', lambda e, f=frame: f.config(bg="white"))

        self._botones_grid.append((frame, [lbl1, lbl2]))

    # ==================== VENTANA ACCIONES ====================

    def _abrir_acciones(self):
        """Abre ventana de acciones disponibles según licencia"""
        tipo_licencia = self.licencia.get('tipo', 'TRIAL')
        es_full = tipo_licencia in ['FULL', 'MASTER'] or self.licencia.get('developer_permanente')

        ventana = tk.Toplevel(self.root)
        ventana.withdraw()
        ventana.title("⚡ Acciones")
        ventana.resizable(False, False)
        ventana.configure(bg="#f0f0f0")
        ventana.transient(self.root)
        ventana.grab_set()

        # Header
        header = tk.Frame(ventana, bg="#e65100", pady=12)
        header.pack(fill='x')
        tk.Label(
            header,
            text="⚡ Acciones",
            font=("Segoe UI", 14, "bold"),
            bg="#e65100",
            fg="white"
        ).pack()
        tk.Label(
            header,
            text="Selecciona qué deseas ejecutar",
            font=("Segoe UI", 9),
            bg="#e65100",
            fg="white"
        ).pack()

        frame = tk.Frame(ventana, bg="#f0f0f0")
        frame.pack(fill='both', expand=True, padx=20, pady=15)

        # Acción 1 — siempre disponible
        tk.Button(
            frame,
            text="▶️  Publicar Productos en Marketplace",
            font=("Segoe UI", 11, "bold"),
            bg="#198754",
            fg="white",
            activebackground="#146c43",
            cursor="hand2",
            anchor='w',
            padx=15,
            pady=8,
            command=lambda: [ventana.destroy(), self._publicar_productos()]
        ).pack(fill='x', pady=(0, 8))

        # Acción 2 — Extraer Catálogo de WhatsApp
        tk.Button(
            frame,
            text="🛍️  Extraer Catálogo de WhatsApp" if es_full else "🔒  Extraer Catálogo de WhatsApp  —  versión Completa",
            font=("Segoe UI", 11, "bold") if es_full else ("Segoe UI", 11),
            bg="#25D366" if es_full else "#e0e0e0",
            fg="white" if es_full else "#9e9e9e",
            cursor="hand2",
            anchor='w',
            padx=15,
            pady=8,
            command=lambda: [ventana.destroy(), self._extraer_catalogo()] if es_full else self._mostrar_mensaje_upgrade()
        ).pack(fill='x', pady=(0, 8))

        # Acción 3 — Atender Interesados en Messenger
        tk.Button(
            frame,
            text="💬  Atender Interesados en Messenger" if es_full else "🔒  Atender Interesados en Messenger  —  versión Completa",
            font=("Segoe UI", 11, "bold") if es_full else ("Segoe UI", 11),
            bg="#0866ff" if es_full else "#e0e0e0",
            fg="white" if es_full else "#9e9e9e",
            cursor="hand2",
            anchor='w',
            padx=15,
            pady=8,
            command=lambda: [ventana.destroy(), self._atender_interesados()] if es_full else self._mostrar_mensaje_upgrade()
        ).pack(fill='x', pady=(0, 8))

        # Acción 4 — Ejecutar Secuencia Configurada
        if es_full:
            tk.Button(
                frame,
                text="⚡  Ejecutar Secuencia Configurada",
                font=("Segoe UI", 11, "bold"),
                bg="#e65100",
                fg="white",
                activebackground="#bf360c",
                cursor="hand2",
                anchor='w',
                padx=15,
                pady=8,
                command=lambda: [ventana.destroy(), self._ejecutar_secuencia()]
            ).pack(fill='x', pady=(0, 8))
        else:
            tk.Button(
                frame,
                text="🔒  Ejecutar Secuencia Configurada  —  versión Completa",
                font=("Segoe UI", 11),
                bg="#e0e0e0",
                fg="#9e9e9e",
                cursor="hand2",
                anchor='w',
                padx=15,
                pady=8,
                command=self._mostrar_mensaje_upgrade
            ).pack(fill='x', pady=(0, 8))

        tk.Button(
            frame,
            text="Cerrar",
            font=("Segoe UI", 10),
            bg="#6c757d",
            fg="white",
            width=12,
            command=ventana.destroy
        ).pack(pady=15)

        self._centrar_ventana(ventana, 500, 430)
        ventana.deiconify()

    # ==================== ACCIONES ====================

    def _ejecutar_secuencia(self):
        """Ejecuta los módulos en el orden configurado en Secuencia"""
        import configparser
        cfg = configparser.ConfigParser()
        cfg.read(os.path.join(self.base_dir, "config_global.txt"), encoding='utf-8')
        modulos = cfg.get('SECUENCIA', 'modulos_activos', fallback='').strip()

        if not modulos:
            respuesta = messagebox.askyesno(
                "⚙️ Secuencia no configurada",
                "No has configurado la secuencia de módulos.\n\n"
                "¿Deseas ir al Configurador para definirla ahora?"
            )
            if respuesta:
                self._abrir_configurador(pestana='secuencia')
                return
            # Si dice No → ejecutar con módulo por defecto (publicar)
            modulos = 'publicar'

        lista = [m.strip() for m in modulos.split(',') if m.strip()]

        # Validar configuración antes de ejecutar
        problema = self._problema_configuracion(lista)
        if problema:
            texto, pestana = problema
            if messagebox.askyesno("⚠️ Configuración incompleta",
                                   f"{texto}.\n\n¿Deseas ir al Configurador para completarlo ahora?"):
                self._abrir_configurador(pestana=pestana)
            return

        try:
            exe = self._exe("PublicadorMarketplace.exe")
            if os.path.exists(exe):
                subprocess.Popen([exe, "--secuencia"]).wait()
            else:
                subprocess.Popen([sys.executable, "publicar_marketplace.py", "--secuencia"]).wait()
            self._toast("⚡ Secuencia completada", "Todos los módulos ejecutados")
        except Exception as e:
            messagebox.showerror("❌ Error en secuencia", f"Error ejecutando la secuencia:\n{e}")

    def _problema_configuracion(self, modulos):
        """(texto, pestaña del configurador) del primer dato que falta para los módulos, o None"""
        from compartido.gestor_archivos import leer_config_global
        config = leer_config_global()
        if 'extraer' in modulos and not config['contacto_whatsapp']:
            return "Falta el contacto de WhatsApp dueño del catálogo", 'extractor'
        if 'atender' in modulos and not config['contacto_vendedor_whatsapp']:
            return "Falta el contacto de WhatsApp del vendedor al que se avisa de cada interesado", 'atencion'
        return None

    def _lanzar_modulo(self, modulo, titulo_toast, mensaje_toast):
        """Ejecuta un módulo del publicador en su propia consola"""
        problema = self._problema_configuracion([modulo])
        if problema:
            texto, pestana = problema
            if messagebox.askokcancel("⚠️ Configuración incompleta",
                                      f"{texto}.\n\n¿Deseas abrir el Configurador para completarlo ahora?"):
                self._abrir_configurador(pestana=pestana)
            return
        try:
            exe = self._exe("PublicadorMarketplace.exe")
            if os.path.exists(exe):
                subprocess.Popen([exe, "--modulo", modulo])
            else:
                subprocess.Popen([sys.executable, "publicar_marketplace.py", "--modulo", modulo])
            self._toast(titulo_toast, mensaje_toast)
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo iniciar el módulo:\n{e}")

    def _publicar_productos(self):
        self._lanzar_modulo("publicar", "🚀 Publicación iniciada", "El navegador se abrirá en unos segundos...")

    def _extraer_catalogo(self):
        self._lanzar_modulo("extraer", "🛍️ Extrayendo catálogo", "Abriendo WhatsApp Web...")

    def _atender_interesados(self):
        self._lanzar_modulo("atender", "💬 Atendiendo interesados", "Revisando la bandeja de Marketplace...")

    def _abrir_configurador(self, pestaña=None, pestana=None):
        """Abre el configurador — bloquea el grid mientras está abierto"""
        try:
            exe = self._exe("ConfiguradorMarketplace.exe")
            pestana_final = pestaña or pestana
            args = [exe] if os.path.exists(exe) else [sys.executable, "configurador_gui.py"]
            if pestana_final:
                args.append(f"--pestana={pestana_final}")
            subprocess.run(args)
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo abrir el configurador:\n{e}")

    def _abrir_carpeta_productos(self):
        """TRIAL: abre la carpeta de productos en el explorador e informa sobre el gestor"""
        import subprocess as sp
        from compartido.gestor_archivos import leer_config_global
        carpeta = os.path.join(self.base_dir, leer_config_global()['carpeta_productos'])
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)
        sp.Popen(f'explorer "{carpeta}"')
        self._toast(
            "🛍️ Tus Productos",
            "Carpeta abierta — version Completa incluye editor visual",
            duracion=5000
        )

    def _abrir_gestor_articulos(self):
        try:
            exe = self._exe("GestorArticulos.exe")
            if os.path.exists(exe):
                subprocess.run([exe])
            else:
                subprocess.run([sys.executable, "gestor_articulos_gui.py"])
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo abrir el gestor:\n{e}")

    def _gestionar_tareas(self):
        try:
            exe = self._exe("GestorTareasMarketplace.exe")
            if os.path.exists(exe):
                subprocess.run([exe])
            else:
                subprocess.run([sys.executable, "gestor_tareas_gui.py"])
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo abrir el gestor de tareas:\n{e}")

    def _abrir_upgrade(self):
        """Abre la página de compra con el código de licencia del usuario"""
        import webbrowser
        from dialogos_licencia import ID_APP_WEB
        try:
            codigo = self.gestor_licencias.obtener_codigo_guardado()
            url = f"https://automapro-frontend.vercel.app/cliente/comprar?codigo={codigo}&app={ID_APP_WEB}"
            webbrowser.open(url)
        except Exception:
            webbrowser.open("https://automapro-frontend.vercel.app/catalogo")

    def _mostrar_mensaje_upgrade(self):
        """Muestra mensaje cuando el usuario intenta acceder a función premium"""
        messagebox.showinfo(
            "🔒 Función Premium",
            "Esta función está disponible solo en la versión Completa.\n\n"
            "Adquiérela en automapro.com para desbloquear:\n"
            "• Extraer Catálogo de WhatsApp\n"
            "• Atender Interesados en Messenger\n"
            "• Editor visual de productos\n"
            "• Tareas Automáticas"
        )

    def _ver_estadisticas(self):
        """Muestra ventana de estadísticas"""
        try:
            gestor = GestorRegistro()
            stats = gestor.obtener_estadisticas()
            fecha_ultima = stats.get('ultima_publicacion') or 'Nunca'

            ventana = tk.Toplevel(self.root)
            ventana.withdraw()
            ventana.title("📊 Estadísticas")
            ventana.resizable(False, False)
            ventana.configure(bg="#f0f0f0")
            ventana.transient(self.root)
            ventana.grab_set()

            header = tk.Frame(ventana, bg="#198754", pady=12)
            header.pack(fill='x')
            tk.Label(header, text="📊 Estadísticas del Sistema",
                     font=("Segoe UI", 13, "bold"), bg="#198754", fg="white").pack()

            frame = tk.Frame(ventana, bg="white", padx=25, pady=15)
            frame.pack(fill='both', expand=True, padx=15, pady=15)

            items = [
                ("📈 Total publicaciones:", str(stats.get('total_publicaciones', 0))),
                ("✅ Exitosas:", str(stats.get('publicaciones_exitosas', 0))),
                ("❌ Fallidas:", str(stats.get('publicaciones_fallidas', 0))),
                ("📅 Publicados hoy:", str(stats.get('publicaciones_hoy', 0))),
                ("🎯 Tasa de éxito:", f"{stats.get('tasa_exito', 0):.1f}%"),
                ("⏱️ Tiempo promedio:", f"{stats.get('tiempo_promedio', 0):.1f}s"),
                ("🛍️ Productos extraídos:", str(stats.get('productos_extraidos', 0))),
                ("📅 Última publicación:", fecha_ultima),
            ]

            for label, valor in items:
                row = tk.Frame(frame, bg="white")
                row.pack(fill='x', pady=5)
                tk.Label(row, text=label, font=("Segoe UI", 10, "bold"),
                         bg="white", anchor='w', width=25).pack(side='left')
                tk.Label(row, text=valor, font=("Segoe UI", 10),
                         bg="white", anchor='w').pack(side='left')

            tk.Button(
                ventana,
                text="Cerrar",
                font=("Segoe UI", 10),
                bg="#6c757d",
                fg="white",
                width=12,
                command=ventana.destroy
            ).pack(pady=15)

            self._centrar_ventana(ventana, 470, 440)
            ventana.deiconify()

        except Exception as e:
            messagebox.showerror("❌ Error", f"Error mostrando estadísticas:\n{e}")

    def _mostrar_ayuda(self):
        ventana = tk.Toplevel(self.root)
        ventana.withdraw()
        ventana.title("❓ Centro de Ayuda")
        ventana.resizable(False, False)
        ventana.configure(bg="#f0f0f0")
        ventana.transient(self.root)
        ventana.grab_set()

        TEMAS = [
            ("▶️  Publicar Productos",
             "▶️ PUBLICAR PRODUCTOS EN MARKETPLACE\n\n"
             "Publica automáticamente tus productos en Facebook Marketplace.\n\n"
             "¿Qué hace?\n"
             "• Abre el navegador configurado con tu sesión de Facebook guardada\n"
             "• Toma los productos de la carpeta 'ArticulosMarketplace' en orden de rotación\n"
             "• Salta los productos sin título, precio o imágenes\n"
             "• Sube las imágenes (hasta 10) y llena título, precio, categoría, estado,\n"
             "  ubicación y descripción\n"
             "• Publica la cantidad configurada (1 por defecto)\n"
             "• Respeta el límite diario de publicaciones para evitar bloqueos\n"
             "• Registra cada publicación en las Estadísticas"),

            ("🛍️  Extraer Catálogo",
             "🛍️ EXTRAER CATÁLOGO DE WHATSAPP\n\n"
             "Llena tus productos automáticamente desde un catálogo de WhatsApp Business.\n\n"
             "¿Qué hace?\n"
             "• Abre WhatsApp Web (la primera vez debes escanear el código QR)\n"
             "• Busca el contacto configurado y abre su catálogo\n"
             "• Extrae título, precio, descripción e imágenes de cada producto\n"
             "• Continúa donde se quedó la extracción anterior\n\n"
             "Antes de usarlo:\n"
             "• Configura el contacto dueño del catálogo en Configurador → Extractor"),

            ("💬  Atender Interesados",
             "💬 ATENDER INTERESADOS EN MESSENGER\n\n"
             "Responde a las personas que escriben por tus productos de Marketplace.\n\n"
             "¿Qué hace?\n"
             "• Revisa solo la bandeja de Marketplace (no tus chats personales)\n"
             "• Atiende solo los chats de productos publicados por la app\n"
             "• Pide el número de celular al interesado con un mensaje plantilla\n"
             "• Si responde otra cosa, vuelve a pedirlo (hasta el máximo configurado)\n"
             "• Cuando lo envía, le confirma que será contactado\n"
             "• Avisa al vendedor por WhatsApp con el nombre, celular y producto\n"
             "• Nunca escribe dos veces lo mismo a la misma persona\n\n"
             "Antes de usarlo:\n"
             "• Configura el contacto del vendedor en Configurador → Atención"),

            ("⚡  Ejecutar Secuencia",
             "⚡ EJECUTAR SECUENCIA\n\n"
             "Ejecuta varios módulos seguidos, en el orden definido en\n"
             "Configurador → Secuencia.\n\n"
             "Ejemplo: Extraer catálogo → Publicar productos → Atender interesados"),

            ("🗓️  Tareas Automáticas",
             "🗓️ TAREAS AUTOMÁTICAS\n\n"
             "Programa el sistema para que trabaje solo, a la hora y los días que elijas.\n\n"
             "• Cada tarea tiene sus propias acciones (publicar, extraer, atender)\n"
             "• Cada tarea puede publicar su propia cantidad de productos\n"
             "• Lo que pasa en cada ejecución queda en 'registro_tareas.log'\n"
             "• Requiere la versión Completa"),

            ("⚙️  Configurador",
             "⚙️ CONFIGURADOR\n\n"
             "Ajusta el sistema sin tocar archivos:\n"
             "• Navegador y perfil de Facebook\n"
             "• Cantidad de productos por ejecución y límite diario\n"
             "• Contacto del catálogo de WhatsApp\n"
             "• Mensajes plantilla y vendedor para atender interesados\n"
             "• Orden de la secuencia"),

            ("🛍️  Gestor de Productos",
             "🛍️ GESTOR DE PRODUCTOS\n\n"
             "Crea y edita tus productos sin abrir carpetas:\n"
             "• Título, precio, categoría, estado, ubicación y descripción\n"
             "• Imágenes de cada producto\n"
             "• Indica qué productos están listos para publicar"),

            ("📊  Estadísticas",
             "📊 ESTADÍSTICAS\n\n"
             "Resumen del historial de publicaciones en Marketplace.\n\n"
             "¿Qué muestra?\n"
             "• Total de publicaciones, exitosas y fallidas\n"
             "• Publicados hoy, tasa de éxito y tiempo promedio\n"
             "• Productos extraídos del catálogo\n"
             "• Fecha de la última publicación\n\n"
             "Los datos se guardan en 'registro_publicaciones.json'."),

            ("🔄  Actualizaciones",
             "🔄 ACTUALIZACIONES\n\n"
             "El sistema revisa si hay una versión nueva:\n"
             "• Al abrir el Panel de Control\n"
             "• Al terminar una Tarea Automática (como máximo un aviso por día)\n\n"
             "En el aviso puedes elegir:\n"
             "• Actualizar ahora → descarga e instala la versión nueva\n"
             "• Más tarde → se vuelve a avisar otro día\n"
             "  (si nadie responde en 30 segundos, se elige Más tarde)\n\n"
             "Al actualizar se conserva todo lo tuyo:\n"
             "• Productos e imágenes\n"
             "• Tareas automáticas y su configuración\n"
             "• Configuración, conversaciones atendidas e historial"),
        ]

        header = tk.Frame(ventana, bg="#198754", pady=12)
        header.pack(fill='x')
        tk.Label(header, text="❓ Centro de Ayuda",
                 font=("Segoe UI", 14, "bold"), bg="#198754", fg="white").pack()
        tk.Label(header, text="Selecciona una opción para ver su explicación",
                 font=("Segoe UI", 9), bg="#198754", fg="white").pack()

        cuerpo = tk.Frame(ventana, bg="#f0f0f0")
        cuerpo.pack(fill='both', expand=True, padx=15, pady=12)

        panel_izq = tk.Frame(cuerpo, bg="#f0f0f0", width=245)
        panel_izq.pack(side='left', fill='y', padx=(0, 10))
        panel_izq.pack_propagate(False)

        tk.Label(panel_izq, text="Opciones", font=("Segoe UI", 9, "bold"),
                 bg="#f0f0f0", fg="#555").pack(anchor='w', pady=(0, 5))

        panel_der = tk.Frame(cuerpo, bg="white", relief='solid', borderwidth=1)
        panel_der.pack(side='left', fill='both', expand=True)

        texto_detalle = tk.Text(panel_der, font=("Segoe UI", 10), bg="white",
                                fg="#333", wrap='word', relief='flat',
                                padx=15, pady=12, state='disabled', cursor="arrow")
        scroll = tk.Scrollbar(panel_der, command=texto_detalle.yview)
        texto_detalle.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        texto_detalle.pack(fill='both', expand=True)

        botones = []

        def seleccionar(idx):
            for i, btn in enumerate(botones):
                btn.config(bg="#198754" if i == idx else "white",
                           fg="white" if i == idx else "#333")
            texto_detalle.config(state='normal')
            texto_detalle.delete('1.0', tk.END)
            texto_detalle.insert(tk.END, TEMAS[idx][1])
            texto_detalle.config(state='disabled')

        for i, (nombre, _) in enumerate(TEMAS):
            btn = tk.Button(panel_izq, text=nombre, font=("Segoe UI", 9),
                            bg="white", fg="#333", anchor='w', padx=8, pady=5,
                            relief='solid', borderwidth=1, cursor="hand2",
                            command=lambda idx=i: seleccionar(idx))
            btn.pack(fill='x', pady=2)
            botones.append(btn)

        seleccionar(0)

        tk.Button(ventana, text="Cerrar", font=("Segoe UI", 10),
                  bg="#6c757d", fg="white", width=12,
                  command=lambda: [ventana.grab_release(), ventana.destroy()]
                  ).pack(pady=10)

        ventana.protocol("WM_DELETE_WINDOW",
                         lambda: [ventana.grab_release(), ventana.destroy()])
        self._centrar_ventana(ventana, 860, 640)
        ventana.deiconify()

    def _toast(self, titulo, mensaje, duracion=3000, color="#28a745"):
        """Delega al sistema centralizado de toasts"""
        from compartido.toast import Toast
        if color == Toast.COLOR_ERROR or color == "#dc3545":
            Toast.error(self.root, f"{titulo}\n{mensaje}", duracion)
        elif color == Toast.COLOR_ADVERTENCIA or color == "#e65100":
            Toast.advertencia(self.root, f"{titulo}\n{mensaje}", duracion)
        elif color == Toast.COLOR_INFO or color == "#1a73e8":
            Toast.info(self.root, f"{titulo}\n{mensaje}", duracion)
        else:
            Toast.exito(self.root, f"{titulo}\n{mensaje}", duracion)

    def ejecutar(self):
        self.root.mainloop()


def _verificar_wizard_completado():
    """Si no hay licencia configurada, lanza el wizard y termina"""
    import subprocess
    gestor = GestorLicencias("Marketplace")
    if not os.path.exists(gestor.archivo_config):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
            wizard = os.path.join(base_dir, "WizardMarketplace.exe")
        else:
            wizard = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wizard_primera_vez.py")

        if os.path.exists(wizard):
            subprocess.Popen([wizard] if wizard.endswith('.exe') else [sys.executable, wizard])
        else:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showwarning(
                "Configuración requerida",
                "Por favor ejecuta WizardMarketplace.exe para configurar el sistema."
            )
            root.destroy()
        return False
    return True


def main():
    if not _verificar_wizard_completado():
        return
    panel = PanelControl()
    panel.ejecutar()


if __name__ == "__main__":
    main()