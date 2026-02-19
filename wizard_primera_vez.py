import os
import tkinter as tk
from tkinter import ttk, messagebox
import configparser
import re
import subprocess
from gestor_licencias import GestorLicencias


class WizardPrimeraVez:
    """Wizard de configuración inicial para primera ejecución"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎉 Bienvenido - Marketplace Automático")
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
            'usar_ejemplos': False
        }
        self.gestor_licencias = GestorLicencias()
        self.licencia_validada = False
        self.tipo_licencia = None

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
            self._paso_mensajes()
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
            text="Esta aplicación publica productos en Facebook Marketplace de forma automática.",
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
                 "• Extracción de catálogo de WhatsApp Business\n"
                 "• Gestión inteligente de productos\n"
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

        # Frame para el entry y el formato
        entry_frame = tk.Frame(frame, bg="#f0f0f0")
        entry_frame.pack(pady=(0, 5))
        
        self.entry_licencia = tk.Entry(
            entry_frame,
            font=("Segoe UI", 12, "bold"),
            width=20,
            justify='center'
        )
        self.entry_licencia.pack()
        self.entry_licencia.focus()
        
        # Label de formato esperado
        self.label_formato = tk.Label(
            frame,
            text="Formato: XXX-XXXXXX-XXXXX",
            font=("Segoe UI", 9),
            bg="#f0f0f0",
            fg="gray"
        )
        self.label_formato.pack(pady=(0, 20))
        
        # Forzar mayúsculas en cada tecla presionada
        def insertar_mayuscula(event):
            if event.char and event.char.isalpha():
                # Insertar la versión en mayúsculas
                pos = self.entry_licencia.index(tk.INSERT)
                self.entry_licencia.insert(pos, event.char.upper())
                return "break"
        
        # Auto-formateo con KeyRelease
        def auto_formateo(event):
            # Obtener contenido actual
            contenido = self.entry_licencia.get().upper()
            
            # Quitar guiones y caracteres no válidos
            solo_alfanum = re.sub(r'[^A-Z0-9]', '', contenido)
            
            # Resetear validación al editar
            if len(solo_alfanum) != 14:
                self.licencia_validada = False
                self.tipo_licencia = None
            
            # LÍMITE ESTRICTO: Cortar en 14 caracteres
            if len(solo_alfanum) > 14:
                solo_alfanum = solo_alfanum[:14]
            
            # Aplicar formato XXX-XXXXXX-XXXXX
            if len(solo_alfanum) <= 3:
                formateado = solo_alfanum
            elif len(solo_alfanum) <= 9:
                formateado = f"{solo_alfanum[:3]}-{solo_alfanum[3:]}"
            else:
                formateado = f"{solo_alfanum[:3]}-{solo_alfanum[3:9]}-{solo_alfanum[9:]}"
            
            # Solo actualizar si cambió
            if formateado != contenido:
                self.entry_licencia.delete(0, tk.END)
                self.entry_licencia.insert(0, formateado)
                # Cursor al final
                self.entry_licencia.icursor(tk.END)
            
            # Verificar licencia cuando tenga 14 caracteres
            if len(solo_alfanum) == 14:
                self._verificar_licencia_tiempo_real(formateado)
            elif len(solo_alfanum) > 0:
                self.label_formato.config(fg="#ffc107", text=f"⚠ Faltan {14 - len(solo_alfanum)} caracteres")
                self.licencia_validada = False
                self.tipo_licencia = None
            else:
                self.label_formato.config(fg="gray", text="Formato: XXX-XXXXXX-XXXXX")
                self.licencia_validada = False
                self.tipo_licencia = None
        
        # Bind para mayúsculas instantáneas
        self.entry_licencia.bind('<Key>', insertar_mayuscula)
        # Bind con KeyRelease para formateo
        self.entry_licencia.bind('<KeyRelease>', auto_formateo)

        tk.Label(
            frame,
            text="Si no tienes código, puedes usar la versión TRIAL\n"
                 "(limitada a 5 mensajes por día)",
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

    def _verificar_licencia_tiempo_real(self, codigo):
        """Verifica la licencia en tiempo real cuando se completa"""
        # Mostrar "Verificando..."
        self.label_formato.config(fg="gray", text="⏳ Verificando...")
        self.root.update()
        
        try:
            # Quitar guiones para validar longitud real
            codigo_limpio = re.sub(r'[^A-Z0-9]', '', codigo)
            
            # FORZAR LÍMITE ESTRICTO
            if len(codigo_limpio) != 14:
                self.label_formato.config(
                    fg="#dc3545",
                    text="❌ FORMATO INCORRECTO"
                )
                self.licencia_validada = False
                self.tipo_licencia = None
                return
            
            # Formatear correctamente
            codigo_formateado = f"{codigo_limpio[:3]}-{codigo_limpio[3:9]}-{codigo_limpio[9:]}"
            
            # Limpiar cache antes de verificar nueva licencia
            # Esto evita que use cache de licencias anteriores
            try:
                import json
                from pathlib import Path
                if os.name == 'nt':
                    base_path = Path(os.environ.get('USERPROFILE', '~'))
                else:
                    base_path = Path.home()
                archivo_config = base_path / '.config' / 'AutomaPro' / 'Marketplace' / 'config.json'
                
                if archivo_config.exists():
                    with open(archivo_config, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    # Eliminar cache de licencia pero mantener código guardado
                    if 'datos_licencia' in config:
                        del config['datos_licencia']
                        with open(archivo_config, 'w', encoding='utf-8') as f:
                            json.dump(config, f, indent=2, ensure_ascii=False)
            except:
                pass  # Si falla, continuar igual
            
            # Verificar contra backend (sin cache)
            resultado = self.gestor_licencias.verificar_licencia(codigo_formateado, mostrar_mensajes=False)
            
            if resultado['valida']:
                if resultado.get('developer_permanente'):
                    # Licencia MASTER - OCULTAR que es MASTER
                    self.label_formato.config(
                        fg="#28a745",
                        text="✅ LICENCIA FULL VÁLIDA"
                    )
                    self.licencia_validada = True
                    self.tipo_licencia = 'MASTER'
                elif resultado.get('tipo') == 'FULL':
                    # Licencia FULL
                    self.label_formato.config(
                        fg="#28a745",
                        text="✅ LICENCIA FULL VÁLIDA"
                    )
                    self.licencia_validada = True
                    self.tipo_licencia = 'FULL'
                elif resultado.get('tipo') == 'TRIAL':
                    # Licencia TRIAL
                    dias = resultado.get('diasRestantes', 0)
                    self.label_formato.config(
                        fg="#ffc107",
                        text=f"✅ LICENCIA TRIAL ({dias} días restantes)"
                    )
                    self.licencia_validada = True
                    self.tipo_licencia = 'TRIAL'
                else:
                    # Tipo desconocido = inválida
                    self.label_formato.config(
                        fg="#dc3545",
                        text="❌ LICENCIA INVÁLIDA"
                    )
                    self.licencia_validada = False
                    self.tipo_licencia = None
            else:
                # Licencia inválida
                self.label_formato.config(
                    fg="#dc3545",
                    text="❌ LICENCIA INVÁLIDA"
                )
                self.licencia_validada = False
                self.tipo_licencia = None
        except Exception as e:
            print(f"Error verificando licencia: {e}")
            self.label_formato.config(
                fg="#dc3545",
                text="❌ Error al verificar"
            )
            self.licencia_validada = False
            self.tipo_licencia = None

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

        self.var_navegador = tk.StringVar(value=self.datos_config.get('navegador', 'firefox'))
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

        self.var_perfil = tk.StringVar(value=self.datos_config.get('usar_perfil', 'si'))
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

    def _paso_mensajes(self):
        """Paso 3: Crear mensajes o usar ejemplos"""
        # Header
        header = tk.Frame(self.root, bg="#198754", pady=15)
        header.pack(fill='x')
        tk.Label(
            header,
            text="Paso 3 de 4: Catálogo",
            font=("Segoe UI", 14, "bold"),
            bg="#198754",
            fg="white"
        ).pack()

        # Contenido
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill='both', expand=True, padx=40, pady=30)

        # Verificar si ya hay mensajes
        mensajes_existentes = len([f for f in os.listdir('mensajes') if f.endswith('.txt')]) if os.path.exists('mensajes') else 0

        if mensajes_existentes > 0:
            tk.Label(
                frame,
                text=f"✅ Ya tienes {mensajes_existentes} mensajes creados",
                font=("Segoe UI", 12, "bold"),
                bg="#f0f0f0",
                fg="#28a745"
            ).pack(pady=(0, 20))
        else:
            tk.Label(
                frame,
                text="La aplicación necesita productos para publicar.",
                font=("Segoe UI", 11),
                bg="#f0f0f0"
            ).pack(pady=(0, 20))

        tk.Label(
            frame,
            text="Opciones:",
            font=("Segoe UI", 10, "bold"),
            bg="#f0f0f0"
        ).pack(anchor='w', pady=(0, 10))

        # Opción 1
        frame_op1 = tk.Frame(frame, bg="white", relief='solid', borderwidth=1)
        frame_op1.pack(fill='x', pady=(0, 15), padx=20)
        
        tk.Label(
            frame_op1,
            text="📦 Extraer catálogo de WhatsApp",
            font=("Segoe UI", 10, "bold"),
            bg="white"
        ).pack(anchor='w', padx=15, pady=(10, 5))
        
        tk.Label(
            frame_op1,
            text="Extrae productos de tu catálogo de WhatsApp Business",
            font=("Segoe UI", 9),
            bg="white",
            fg="gray"
        ).pack(anchor='w', padx=15, pady=(0, 10))
        
        tk.Button(
            frame_op1,
            text="Extraer Catálogo",
            font=("Segoe UI", 9),
            bg="#198754",
            fg="white",
            command=self._abrir_gestor_mensajes
        ).pack(anchor='w', padx=15, pady=(0, 10))

        if mensajes_existentes == 0:
            # Opción 2 - solo si no hay mensajes
            frame_op2 = tk.Frame(frame, bg="white", relief='solid', borderwidth=1)
            frame_op2.pack(fill='x', pady=(0, 15), padx=20)
            
            tk.Label(
                frame_op2,
                text="✅ Ya tengo productos configurados",
                font=("Segoe UI", 10, "bold"),
                bg="white"
            ).pack(anchor='w', padx=15, pady=(10, 5))
            
            tk.Label(
                frame_op2,
                text="Continuar sin extraer (productos ya configurados manualmente)",
                font=("Segoe UI", 9),
                bg="white",
                fg="gray"
            ).pack(anchor='w', padx=15, pady=(0, 10))
            
            tk.Button(
                frame_op2,
                text="Usar Ejemplos",
                font=("Segoe UI", 9),
                bg="#28a745",
                fg="white",
                command=self._usar_ejemplos
            ).pack(anchor='w', padx=15, pady=(0, 10))

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
            command=self._verificar_mensajes
        ).pack(side='right', padx=(10, 40))

    def _paso_finalizar(self):
        """Paso 4: Finalizar configuración"""
        # Ajustar tamaño de ventana según tipo de licencia
        if self.tipo_licencia in ['FULL', 'MASTER']:
            nueva_altura = 720
        else:
            nueva_altura = 500
        
        # Redimensionar y recentrar FORZADO
        nueva_ancho = 600
        
        # Primero cambiar tamaño
        self.root.geometry(f"{nueva_ancho}x{nueva_altura}")
        
        # Forzar actualización para obtener dimensiones reales
        self.root.update_idletasks()
        
        # Calcular posición centrada
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - nueva_ancho) // 2
        y = (screen_height - nueva_altura) // 2
        
        # Aplicar posición centrada
        self.root.geometry(f'{nueva_ancho}x{nueva_altura}+{x}+{y}')
        
        # Forzar actualización visual
        self.root.update()
        
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
        frame.pack(fill='both', expand=True, padx=40, pady=20)

        tk.Label(
            frame,
            text="✅ ¡Configuración completada!",
            font=("Segoe UI", 14, "bold"),
            bg="#f0f0f0",
            fg="#28a745"
        ).pack(pady=(0, 15))

        # Resumen
        resumen_frame = tk.Frame(frame, bg="white", relief='solid', borderwidth=1)
        resumen_frame.pack(fill='x', pady=(0, 15))

        licencia_texto = "TRIAL" if not self.datos_config['codigo_licencia'] else self.datos_config['codigo_licencia']
        productos_count = len([f for f in os.listdir('productos') if f.endswith('.json')]) if os.path.exists('productos') else 0

        items = [
            ("✅ Licencia:", licencia_texto),
            ("✅ Navegador:", self.datos_config['navegador'].capitalize()),
            ("✅ Productos listos:", f"{productos_count} productos")
        ]

        for label, valor in items:
            item_frame = tk.Frame(resumen_frame, bg="white")
            item_frame.pack(fill='x', padx=15, pady=3)
            tk.Label(item_frame, text=label, font=("Segoe UI", 10, "bold"), bg="white", width=20, anchor='w').pack(side='left')
            tk.Label(item_frame, text=valor, font=("Segoe UI", 10), bg="white", anchor='w').pack(side='left')

        # Sección de tareas automáticas (solo FULL/MASTER)
        if self.tipo_licencia in ['FULL', 'MASTER']:
            # Separador
            separator = tk.Frame(frame, bg="#e0e0e0", height=2)
            separator.pack(fill='x', pady=15)
            
            # Título sección
            tk.Label(
                frame,
                text="🗓️ PROGRAMACIÓN AUTOMÁTICA (FULL)",
                font=("Segoe UI", 11, "bold"),
                bg="#f0f0f0",
                fg="#198754"
            ).pack(pady=(0, 8))
            
            tk.Label(
                frame,
                text="¿Quieres que configuremos 4 publicaciones automáticas de productos?",
                font=("Segoe UI", 9),
                bg="#f0f0f0"
            ).pack(pady=(0, 8))
            
            # Frame con horarios propuestos
            horarios_frame = tk.Frame(frame, bg="white", relief='solid', borderwidth=1)
            horarios_frame.pack(fill='x', pady=(0, 10))
            
            tk.Label(
                horarios_frame,
                text="Horarios propuestos:",
                font=("Segoe UI", 9, "bold"),
                bg="white",
                fg="gray"
            ).pack(anchor='w', padx=15, pady=(8, 3))
            
            horarios_texto = [
                "📅 Lunes y Jueves - 09:00 AM",
                "📅 Martes y Viernes - 02:00 PM", 
                "📅 Miércoles - 06:00 PM",
                "📅 Sábado - 11:00 AM"
            ]
            
            for horario in horarios_texto:
                tk.Label(
                    horarios_frame,
                    text=horario,
                    font=("Segoe UI", 9),
                    bg="white",
                    anchor='w'
                ).pack(anchor='w', padx=30, pady=1)
            
            tk.Label(
                horarios_frame,
                text="📦 Solo productos de Marketplace",
                font=("Segoe UI", 8),
                bg="white",
                fg="gray",
                anchor='w'
            ).pack(anchor='w', padx=30, pady=(3, 8))
            
            # Checkbox para activar
            self.var_crear_tareas = tk.BooleanVar(value=True)
            tk.Checkbutton(
                frame,
                text="✓ Sí, crear tareas automáticas",
                variable=self.var_crear_tareas,
                font=("Segoe UI", 10, "bold"),
                bg="#f0f0f0",
                fg="#28a745"
            ).pack(anchor='w', pady=(0, 8))

        tk.Label(
            frame,
            text="¿Quieres hacer la primera publicación ahora mismo?",
            font=("Segoe UI", 10),
            bg="#f0f0f0"
        ).pack(pady=(10, 5))

        # Botones
        frame_btn = tk.Frame(self.root, bg="#f0f0f0", pady=20)
        frame_btn.pack(fill='x', side='bottom')

        tk.Button(
            frame_btn,
            text="❌ Ahora no",
            font=("Segoe UI", 10),
            bg="#e0e0e0",
            width=15,
            command=self._finalizar_sin_publicar
        ).pack(side='left', padx=(40, 10))

        tk.Button(
            frame_btn,
            text="▶️ Publicar Ahora",
            font=("Segoe UI", 10, "bold"),
            bg="#28a745",
            fg="white",
            width=15,
            command=self._publicar_ahora
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
        self.licencia_validada = True
        self.tipo_licencia = 'TRIAL'
        self._siguiente()

    def _validar_licencia(self):
        codigo = self.entry_licencia.get().strip().upper()
        
        # Si está vacío, debe usar TRIAL
        if not codigo:
            messagebox.showwarning(
                "Campo Vacío",
                "Debes ingresar un código de licencia o presionar 'Usar TRIAL'."
            )
            return
        
        # Quitar guiones para validar
        codigo_limpio = re.sub(r'[^A-Z0-9]', '', codigo)
        
        # Validar formato (exactamente 14 caracteres)
        if len(codigo_limpio) != 14:
            messagebox.showerror(
                "Formato Incorrecto",
                f"El código debe tener exactamente 14 caracteres.\n\n"
                f"Formato: XXX-XXXXXX-XXXXX\n"
                f"Tienes: {len(codigo_limpio)} caracteres"
            )
            return
        
        # Validar que la licencia haya sido verificada
        if not self.licencia_validada:
            messagebox.showerror(
                "Licencia Inválida",
                "El código ingresado no es válido.\n\n"
                "Por favor verifica el código o usa TRIAL."
            )
            return
        
        # Formatear correctamente
        codigo = f"{codigo_limpio[:3]}-{codigo_limpio[3:9]}-{codigo_limpio[9:]}"
        self.datos_config['codigo_licencia'] = codigo
        self.gestor_licencias.guardar_codigo_licencia(codigo)
        
        self._siguiente()

    def _guardar_config_basica(self):
        self.datos_config['navegador'] = self.var_navegador.get()
        self.datos_config['usar_perfil'] = self.var_perfil.get()
        self._siguiente()

    def _abrir_gestor_mensajes(self):
        try:
            subprocess.Popen(['python', 'extraer_catalogo_whatsapp.py'])
            messagebox.showinfo("Info", "El extractor de catálogo se abrió en una nueva ventana.\n\nExtrae tus productos y luego presiona 'Siguiente'.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el extractor: {e}")

    def _usar_ejemplos(self):
        """Ya no se usan ejemplos en Marketplace"""
        messagebox.showinfo("Info", "Continúa al siguiente paso.")
        self._verificar_mensajes()

    def _verificar_mensajes(self):
        """Simplemente continúa al siguiente paso para Marketplace"""
        self._crear_config_completa()
        self._siguiente()

    def _crear_config_completa(self):
        """Crea el archivo config_global.txt con la configuración inicial completa"""
        config = configparser.ConfigParser()
        
        config['GENERAL'] = {
            'nombre_proyecto': 'Marketplace Automático',
            'carpeta_productos': 'productos',
            'navegador': self.datos_config['navegador'],
            'modo_debug': 'si'
        }
        
        config['MENSAJES'] = {
            'seleccion': 'aleatoria',
            'historial_evitar_repetir': '5',
            'formato_fecha': 'no',
            'agregar_hashtags': 'no',
            'hashtags': '#Fe,#Biblia,#Reflexión',
            'agregar_firma': 'no',
            'texto_firma': 'Publicado automáticamente'
        }
        
        config['PUBLICACION'] = {
            'tiempo_entre_intentos': '3',
            'max_intentos_por_publicacion': '3',
            'espera_despues_publicar': '5',
            'verificar_publicacion_exitosa': 'si',
            'espera_estabilizacion_modal': '3'
        }
        
        config['NAVEGADOR'] = {
            'usar_perfil_existente': self.datos_config['usar_perfil'],
            'carpeta_perfil_custom': 'perfiles/facebook_publicador',
            'desactivar_notificaciones': 'si',
            'maximizar_ventana': 'si'
        }
        
        config['LIMITES'] = {
            'tiempo_minimo_entre_publicaciones_segundos': '120',
            'permitir_duplicados': 'no',
            'permitir_forzar_publicacion_manual': 'si'
        }
        
        config['PREDICACIONES'] = {
            'activar_predicaciones': 'no',
            'alternar_con_predicaciones': 'no',
            'nombre_grupo_whatsapp': 'Prédicas',
            'mensajes_por_extraccion': '10',
            'agregar_introduccion_predica': 'si',
            'texto_introduccion_predica': '⏰ Vale la pena ver esto',
            'agregar_hashtags_predicaciones': 'no',
            'hashtags_predicaciones': '',
            'tiempo_espera_previsualizacion': '12',
            'usar_estrategia_optimizada_enlaces': 'si'
        }
        
        config['DEBUG'] = {
            'modo_debug': 'detallado'
        }
        
        with open('config_global.txt', 'w', encoding='utf-8') as f:
            f.write("# ============================================================\n")
            f.write("# CONFIGURACIÓN GLOBAL - PUBLICADOR AUTOMÁTICO FACEBOOK\n")
            f.write("# ============================================================\n\n")
            config.write(f)

    def _crear_tareas_predeterminadas(self):
        """Crea las 4 tareas automáticas predeterminadas"""
        try:
            ruta_script = os.path.abspath("publicador_marketplace.py")
            prefijo = "AutomaPro_Marketplace"
            
            # Definir las 4 tareas
            tareas = [
                {
                    'nombre': f"{prefijo}_LunesJueves",
                    'dias': 'MON,THU',
                    'hora': '09:00'
                },
                {
                    'nombre': f"{prefijo}_MartesViernes",
                    'dias': 'TUE,FRI',
                    'hora': '14:00'
                },
                {
                    'nombre': f"{prefijo}_Miercoles",
                    'dias': 'WED',
                    'hora': '18:00'
                },
                {
                    'nombre': f"{prefijo}_Sabado",
                    'dias': 'SAT',
                    'hora': '11:00'
                }
            ]
            
            tareas_creadas = 0
            errores = []
            
            for tarea in tareas:
                comando = [
                    'schtasks',
                    '/Create',
                    '/TN', tarea['nombre'],
                    '/TR', f'python "{ruta_script}"',
                    '/SC', 'WEEKLY',
                    '/D', tarea['dias'],
                    '/ST', tarea['hora'],
                    '/F'
                ]
                
                resultado = subprocess.run(
                    comando,
                    capture_output=True,
                    text=True
                )
                
                if resultado.returncode == 0:
                    tareas_creadas += 1
                else:
                    errores.append(tarea['nombre'])
            
            if tareas_creadas > 0:
                messagebox.showinfo(
                    "✅ Tareas Creadas",
                    f"Se crearon {tareas_creadas} tareas automáticas correctamente.\n\n"
                    f"Puedes verlas y editarlas desde el Panel de Control."
                )
            
            if errores:
                messagebox.showwarning(
                    "⚠️ Advertencia",
                    f"No se pudieron crear {len(errores)} tareas:\n" + "\n".join(errores)
                )
        
        except Exception as e:
            messagebox.showerror("Error", f"Error creando tareas automáticas:\n{e}")

    def _finalizar_sin_publicar(self):
        # Crear tareas automáticas si está activado
        if hasattr(self, 'var_crear_tareas') and self.var_crear_tareas.get():
            self._crear_tareas_predeterminadas()
        
        messagebox.showinfo(
            "✅ Configuración Completada",
            "¡Todo listo!\n\nPuedes ejecutar 'publicador_marketplace.py' cuando quieras publicar.\n\nO usa el gestor de tareas para ver tus publicaciones automáticas."
        )
        self.root.destroy()

    def _publicar_ahora(self):
        try:
            # Crear tareas automáticas si está activado
            if hasattr(self, 'var_crear_tareas') and self.var_crear_tareas.get():
                self._crear_tareas_predeterminadas()
            
            subprocess.Popen(['python', 'publicador_marketplace.py'])
            self._mostrar_notificacion(
                "✅ Publicación Iniciada",
                "El navegador se abrirá en unos segundos..."
            )
            # Cerrar wizard después de 2 segundos para que se vea la notificación
            self.root.after(2000, self.root.destroy)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar la publicación: {e}")

    def _mostrar_notificacion(self, titulo, mensaje, duracion=3000):
        """Muestra notificación Toast que se cierra sola"""
        toast = tk.Toplevel(self.root)
        toast.overrideredirect(True)
        toast.attributes('-topmost', True)
        
        # Posicionar en esquina inferior derecha
        ancho = 350
        alto = 100
        x = toast.winfo_screenwidth() - ancho - 20
        y = toast.winfo_screenheight() - alto - 60
        toast.geometry(f'{ancho}x{alto}+{x}+{y}')
        
        # Frame
        frame = tk.Frame(toast, bg="#28a745", relief='raised', borderwidth=2)
        frame.pack(fill='both', expand=True)
        
        # Título
        tk.Label(
            frame,
            text=titulo,
            font=("Segoe UI", 11, "bold"),
            bg="#28a745",
            fg="white"
        ).pack(pady=(10, 5))
        
        # Mensaje
        tk.Label(
            frame,
            text=mensaje,
            font=("Segoe UI", 9),
            bg="#28a745",
            fg="white",
            wraplength=300
        ).pack(pady=(0, 10))
        
        # Cerrar automáticamente
        toast.after(duracion, toast.destroy)
        
        # Permitir cerrar con clic
        frame.bind('<Button-1>', lambda e: toast.destroy())

    def ejecutar(self):
        self.root.mainloop()


def main():
    wizard = WizardPrimeraVez()
    wizard.ejecutar()


if __name__ == "__main__":
    main()