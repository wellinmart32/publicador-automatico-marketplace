import os
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
from datetime import datetime, timedelta
from gestor_licencias import GestorLicencias


class GestorTareasGUI:
    """Gestor de tareas automáticas - Windows Task Scheduler"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🗓️ Gestor de Tareas Automáticas - Marketplace")
        self.root.geometry("1000x600")
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

        # Verificar licencia FULL
        self.gestor_licencias = GestorLicencias("Marketplace")
        if not self._verificar_licencia_full():
            messagebox.showerror(
                "Licencia Requerida",
                "Esta función requiere licencia FULL.\n\nActualiza tu licencia para acceder."
            )
            self.root.destroy()
            return

        self.ruta_script = os.path.abspath("automatizador_marketplace.py")
        self.prefijo_tarea = "AutomaPro_Marketplace"
        
        # Mapeo de días
        self.dias_map = {
            'L': 'MON', 'M': 'TUE', 'X': 'WED', 
            'J': 'THU', 'V': 'FRI', 'S': 'SAT', 'D': 'SUN'
        }
        self.dias_map_inverso = {v: k for k, v in self.dias_map.items()}
        
        self._construir_ui()
        self._cargar_tareas()

    def _verificar_licencia_full(self):
        """Verifica que tenga licencia FULL o MASTER"""
        codigo = self.gestor_licencias.obtener_codigo_guardado()
        if not codigo:
            return False
        
        resultado = self.gestor_licencias.verificar_licencia(codigo, mostrar_mensajes=False)
        
        return (resultado.get('valida') and 
                (resultado.get('tipo') == 'FULL' or resultado.get('developer_permanente')))

    def _construir_ui(self):
        """Construye la interfaz"""
        
        # Header
        header = tk.Frame(self.root, bg="#198754", pady=20)
        header.pack(fill='x')
        
        tk.Label(
            header,
            text="🗓️ Gestor de Tareas Automáticas",
            font=("Segoe UI", 18, "bold"),
            bg="#198754",
            fg="white"
        ).pack()
        
        tk.Label(
            header,
            text="Programa publicaciones automáticas en Windows",
            font=("Segoe UI", 10),
            bg="#198754",
            fg="white"
        ).pack()

        # Contenedor principal
        container = tk.Frame(self.root, bg="#f0f0f0")
        container.pack(fill='both', expand=True, padx=20, pady=20)

        # Frame superior: Botones de acción
        frame_acciones = tk.Frame(container, bg="#f0f0f0")
        frame_acciones.pack(fill='x', pady=(0, 15))
        
        tk.Button(
            frame_acciones,
            text="➕ Nueva Tarea",
            font=("Segoe UI", 10, "bold"),
            bg="#28a745",
            fg="white",
            command=self._nueva_tarea,
            width=13
        ).pack(side='left', padx=(0, 10))
        
        tk.Button(
            frame_acciones,
            text="✏️ Editar",
            font=("Segoe UI", 10),
            bg="#ffc107",
            fg="black",
            command=self._editar_tarea,
            width=10
        ).pack(side='left', padx=(0, 10))
        
        tk.Button(
            frame_acciones,
            text="🔄 Actualizar",
            font=("Segoe UI", 10),
            bg="#17a2b8",
            fg="white",
            command=self._cargar_tareas,
            width=10
        ).pack(side='left', padx=(0, 10))
        
        tk.Button(
            frame_acciones,
            text="🗑️ Eliminar",
            font=("Segoe UI", 10),
            bg="#dc3545",
            fg="white",
            command=self._eliminar_tarea,
            width=12
        ).pack(side='left')

        # Lista de tareas (Treeview)
        frame_lista = tk.Frame(container, bg="white")
        frame_lista.pack(fill='both', expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_lista)
        scrollbar.pack(side='right', fill='y')
        
        # Treeview con 4 columnas
        self.tree = ttk.Treeview(
            frame_lista,
            columns=('nombre', 'dias', 'proxima', 'estado'),
            show='headings',
            yscrollcommand=scrollbar.set,
            height=15
        )
        
        self.tree.heading('nombre', text='Nombre de Tarea')
        self.tree.heading('dias', text='Días')
        self.tree.heading('proxima', text='Próxima Ejecución')
        self.tree.heading('estado', text='Estado')
        
        self.tree.column('nombre', width=350)
        self.tree.column('dias', width=100)
        self.tree.column('proxima', width=250)
        self.tree.column('estado', width=150)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.tree.yview)

        # Info footer
        footer = tk.Frame(self.root, bg="#e9ecef", pady=10)
        footer.pack(fill='x', side='bottom')
        
        tk.Label(
            footer,
            text="💡 Doble clic en una tarea para ver detalles completos",
            font=("Segoe UI", 9),
            bg="#e9ecef",
            fg="gray"
        ).pack()
        
        # Bind doble clic
        self.tree.bind('<Double-Button-1>', lambda e: self._ver_detalles())

    def _cargar_tareas(self):
        """Carga las tareas existentes"""
        # Limpiar tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            # Obtener lista de tareas con nuestro prefijo
            resultado = subprocess.run(
                ['schtasks', '/Query', '/FO', 'CSV'],
                capture_output=True,
                text=True,
                encoding='cp1252'
            )
            
            if resultado.returncode != 0:
                messagebox.showerror("Error", "No se pudo acceder al Programador de Tareas")
                return
            
            # Parsear CSV
            lineas = resultado.stdout.strip().split('\n')
            
            tareas_encontradas = False
            for linea in lineas[1:]:  # Skip header
                partes = linea.split('","')
                if len(partes) >= 3:
                    nombre = partes[0].replace('"', '').strip()
                    proxima = partes[1].replace('"', '').strip() if len(partes) > 1 else 'N/A'
                    estado = partes[2].replace('"', '').strip() if len(partes) > 2 else 'N/A'
                    
                    # Solo nuestras tareas
                    if self.prefijo_tarea in nombre:
                        nombre_corto = nombre.split('\\')[-1]
                        
                        # Obtener días de la tarea
                        detalles = self._obtener_detalles_tarea(nombre_corto)
                        dias_texto = self._extraer_dias_cortos(detalles) if detalles else 'N/A'
                        
                        # Traducir estado
                        if 'Ready' in estado or 'Listo' in estado:
                            estado_texto = '✅ Activa'
                        elif 'Disabled' in estado or 'Deshabilitado' in estado:
                            estado_texto = '⏸️ Pausada'
                        elif 'Running' in estado or 'En ejecución' in estado:
                            estado_texto = '▶️ En ejecución'
                        else:
                            estado_texto = estado
                        
                        self.tree.insert('', 'end', values=(nombre_corto, dias_texto, proxima, estado_texto))
                        tareas_encontradas = True
            
            if not tareas_encontradas:
                self.tree.insert('', 'end', values=('No hay tareas programadas', '', '', ''))
        
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando tareas:\n{e}")

    def _extraer_dias_cortos(self, detalles):
        """Extrae los días en formato corto (LMXJVSD) de los detalles de la tarea"""
        if not detalles:
            return 'N/A'
        
        frecuencia = detalles.get('frecuencia', '').lower()
        dias_completos = detalles.get('dias', 'N/A')
        
        if 'daily' in frecuencia or 'diaria' in frecuencia:
            return 'Diario'
        
        # Mapear días en inglés a español abreviado
        dias_map_eng = {
            'mon': 'L', 'tue': 'M', 'wed': 'X', 'thu': 'J',
            'fri': 'V', 'sat': 'S', 'sun': 'D'
        }
        
        if dias_completos and dias_completos != 'N/A':
            dias_lower = dias_completos.lower()
            dias_cortos = []
            for eng, esp in dias_map_eng.items():
                if eng in dias_lower:
                    dias_cortos.append(esp)
            return ''.join(dias_cortos) if dias_cortos else dias_completos
        
        return 'Semanal'

    def _obtener_detalles_tarea(self, nombre_tarea):
        """Obtiene detalles específicos de una tarea"""
        try:
            # Construir nombre completo
            nombre_completo = f"{self.prefijo_tarea}_{nombre_tarea}" if not nombre_tarea.startswith(self.prefijo_tarea) else nombre_tarea
            
            resultado = subprocess.run(
                ['schtasks', '/Query', '/TN', nombre_completo, '/FO', 'LIST', '/V'],
                capture_output=True,
                text=True,
                encoding='cp1252'
            )
            
            if resultado.returncode != 0:
                return None
            
            detalles = {}
            for linea in resultado.stdout.split('\n'):
                linea = linea.strip()
                if ':' in linea:
                    partes = linea.split(':', 1)
                    clave = partes[0].strip()
                    valor = partes[1].strip() if len(partes) > 1 else ''
                    
                    # Mapear campos importantes
                    if 'Hora de inicio' in clave or 'Start Time' in clave:
                        detalles['horario'] = valor
                    elif 'Tipo de programación' in clave or 'Schedule Type' in clave:
                        detalles['frecuencia'] = valor
                    elif 'Estado' in clave or 'Status' in clave:
                        detalles['estado'] = valor
                    elif 'Días' in clave or 'Days' in clave:
                        detalles['dias'] = valor
            
            return detalles
        
        except Exception as e:
            print(f"Error obteniendo detalles: {e}")
            return None

    def _ver_detalles(self):
        """Muestra ventana con detalles completos de la tarea"""
        seleccion = self.tree.selection()
        if not seleccion:
            return
        
        item = self.tree.item(seleccion[0])
        nombre_tarea = item['values'][0]
        
        if nombre_tarea == 'No hay tareas programadas':
            return
        
        detalles = self._obtener_detalles_tarea(nombre_tarea)
        
        if not detalles:
            messagebox.showerror("Error", "No se pudieron obtener los detalles de la tarea")
            return
        
        # Crear ventana de detalles
        ventana = tk.Toplevel(self.root)
        ventana.title(f"📋 Detalles: {nombre_tarea}")
        ventana.geometry("500x300")
        ventana.configure(bg="#f0f0f0")
        ventana.transient(self.root)
        
        # Centrar
        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth() // 2) - (250)
        y = (ventana.winfo_screenheight() // 2) - (150)
        ventana.geometry(f'500x300+{x}+{y}')
        
        # Header
        header = tk.Frame(ventana, bg="#17a2b8", pady=15)
        header.pack(fill='x')
        tk.Label(
            header,
            text=f"📋 {nombre_tarea}",
            font=("Segoe UI", 14, "bold"),
            bg="#17a2b8",
            fg="white"
        ).pack()
        
        # Contenido
        frame = tk.Frame(ventana, bg="white", padx=30, pady=20)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        items = [
            ("⏰ Horario:", detalles.get('horario', 'N/A')),
            ("🔄 Frecuencia:", detalles.get('frecuencia', 'N/A')),
            ("📅 Días:", detalles.get('dias', 'N/A')),
            ("✅ Estado:", detalles.get('estado', 'N/A'))
        ]
        
        for label, valor in items:
            item_frame = tk.Frame(frame, bg="white")
            item_frame.pack(fill='x', pady=8)
            
            tk.Label(
                item_frame,
                text=label,
                font=("Segoe UI", 10, "bold"),
                bg="white",
                anchor='w',
                width=15
            ).pack(side='left')
            
            tk.Label(
                item_frame,
                text=valor,
                font=("Segoe UI", 10),
                bg="white",
                anchor='w'
            ).pack(side='left')
        
        # Botón cerrar
        tk.Button(
            ventana,
            text="Cerrar",
            font=("Segoe UI", 10),
            bg="#6c757d",
            fg="white",
            command=ventana.destroy,
            width=15
        ).pack(pady=(0, 20))

    def _editar_tarea(self):
        """Abre diálogo para editar tarea seleccionada"""
        seleccion = self.tree.selection()
        
        if not seleccion:
            messagebox.showwarning("Aviso", "Selecciona una tarea para editar")
            return
        
        item = self.tree.item(seleccion[0])
        nombre_tarea = item['values'][0]
        
        if nombre_tarea == 'No hay tareas programadas':
            return
        
        # Obtener detalles actuales
        detalles = self._obtener_detalles_tarea(nombre_tarea)
        
        if not detalles:
            messagebox.showerror("Error", "No se pudieron obtener los detalles de la tarea")
            return
        
        # Extraer hora actual
        horario_actual = detalles.get('horario', '09:00:00')
        try:
            hora_parts = horario_actual.split(':')
            hora_inicial = hora_parts[0]
            minuto_inicial = hora_parts[1]
        except:
            hora_inicial = '09'
            minuto_inicial = '00'
        
        # Extraer frecuencia y días
        frecuencia_actual = detalles.get('frecuencia', '').lower()
        dias_actuales = detalles.get('dias', '')
        
        es_diaria = 'daily' in frecuencia_actual or 'diaria' in frecuencia_actual
        
        # Ventana de edición
        self._mostrar_formulario_tarea(
            titulo=f"✏️ Editar: {nombre_tarea}",
            color_header="#ffc107",
            nombre_tarea=nombre_tarea,
            hora_inicial=hora_inicial,
            minuto_inicial=minuto_inicial,
            es_diaria=es_diaria,
            dias_iniciales=dias_actuales,
            es_edicion=True
        )

    def _nueva_tarea(self):
        """Abre diálogo para crear nueva tarea"""
        nombre_auto = f"{self.prefijo_tarea}_{datetime.now().strftime('%Y%m%d_%H%M')}"
        
        self._mostrar_formulario_tarea(
            titulo="➕ Nueva Tarea Automática",
            color_header="#28a745",
            nombre_tarea=nombre_auto,
            hora_inicial="09",
            minuto_inicial="00",
            es_diaria=True,
            dias_iniciales="",
            es_edicion=False
        )

    def _mostrar_formulario_tarea(self, titulo, color_header, nombre_tarea, hora_inicial, minuto_inicial, es_diaria, dias_iniciales, es_edicion):
        """Muestra formulario unificado para crear/editar tareas"""
        ventana = tk.Toplevel(self.root)
        ventana.title(titulo)
        ventana.geometry("550x500")
        ventana.configure(bg="#f0f0f0")
        ventana.transient(self.root)
        ventana.grab_set()
        
        # Centrar
        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth() // 2) - (275)
        y = (ventana.winfo_screenheight() // 2) - (250)
        ventana.geometry(f'550x500+{x}+{y}')
        
        # Header
        header = tk.Frame(ventana, bg=color_header, pady=15)
        header.pack(fill='x')
        tk.Label(
            header,
            text=titulo,
            font=("Segoe UI", 14, "bold"),
            bg=color_header,
            fg="white" if color_header != "#ffc107" else "black"
        ).pack()
        
        # Formulario
        form = tk.Frame(ventana, bg="#f0f0f0")
        form.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Nombre (solo lectura si es edición)
        tk.Label(form, text="Nombre de la tarea:", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(anchor='w', pady=(0, 5))
        
        if es_edicion:
            tk.Label(form, text=nombre_tarea, font=("Segoe UI", 10), bg="#f0f0f0", fg="gray").pack(anchor='w', pady=(0, 15))
            entry_nombre = None
        else:
            entry_nombre = tk.Entry(form, font=("Segoe UI", 10), width=50)
            entry_nombre.pack(anchor='w', pady=(0, 15))
            entry_nombre.insert(0, nombre_tarea)
        
        # Frecuencia
        tk.Label(form, text="Frecuencia:", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(anchor='w', pady=(0, 5))
        var_frecuencia = tk.StringVar(value="DAILY" if es_diaria else "WEEKLY")
        
        frame_freq = tk.Frame(form, bg="#f0f0f0")
        frame_freq.pack(anchor='w', pady=(0, 15))
        
        def cambio_frecuencia():
            if var_frecuencia.get() == "DAILY":
                frame_dias.pack_forget()
            else:
                frame_dias.pack(after=frame_freq, anchor='w', pady=(0, 15))
        
        tk.Radiobutton(frame_freq, text="Diaria", variable=var_frecuencia, value="DAILY", bg="#f0f0f0", command=cambio_frecuencia).pack(side='left', padx=(0, 15))
        tk.Radiobutton(frame_freq, text="Semanal", variable=var_frecuencia, value="WEEKLY", bg="#f0f0f0", command=cambio_frecuencia).pack(side='left')
        
        # Días de la semana (solo para semanal)
        tk.Label(form, text="Días de la semana:", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(anchor='w', pady=(0, 5))
        
        frame_dias = tk.Frame(form, bg="#f0f0f0")
        if not es_diaria:
            frame_dias.pack(anchor='w', pady=(0, 15))
        
        dias_vars = {}
        dias_labels = [('L', 'Lunes'), ('M', 'Martes'), ('X', 'Miércoles'), ('J', 'Jueves'), 
                      ('V', 'Viernes'), ('S', 'Sábado'), ('D', 'Domingo')]
        
        # Parsear días iniciales
        dias_seleccionados = []
        if dias_iniciales:
            dias_lower = dias_iniciales.lower()
            for eng_day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
                if eng_day in dias_lower:
                    dias_seleccionados.append(self.dias_map_inverso[eng_day.upper()])
        
        for corto, completo in dias_labels:
            var = tk.BooleanVar(value=corto in dias_seleccionados)
            dias_vars[corto] = var
            tk.Checkbutton(frame_dias, text=completo, variable=var, bg="#f0f0f0").pack(anchor='w')
        
        # Horario
        tk.Label(form, text="Horario (HH:MM formato 24h):", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(anchor='w', pady=(10, 5))
        
        frame_hora = tk.Frame(form, bg="#f0f0f0")
        frame_hora.pack(anchor='w', pady=(0, 15))
        
        entry_hora = tk.Entry(frame_hora, font=("Segoe UI", 10), width=5)
        entry_hora.pack(side='left')
        entry_hora.insert(0, hora_inicial)
        
        tk.Label(frame_hora, text=":", font=("Segoe UI", 10), bg="#f0f0f0").pack(side='left', padx=5)
        
        entry_minuto = tk.Entry(frame_hora, font=("Segoe UI", 10), width=5)
        entry_minuto.pack(side='left')
        entry_minuto.insert(0, minuto_inicial)
        
        # Botones
        frame_btns = tk.Frame(ventana, bg="#f0f0f0", pady=15)
        frame_btns.pack(fill='x', side='bottom')
        
        tk.Button(
            frame_btns,
            text="Cancelar",
            font=("Segoe UI", 10),
            bg="#6c757d",
            fg="white",
            width=12,
            command=ventana.destroy
        ).pack(side='left', padx=(30, 10))
        
        def guardar():
            # Obtener nombre
            if es_edicion:
                nombre = nombre_tarea
            else:
                nombre = entry_nombre.get().strip()
                if not nombre:
                    messagebox.showerror("Error", "Debes ingresar un nombre")
                    return
            
            # Obtener frecuencia
            frecuencia = var_frecuencia.get()
            
            # Validar días si es semanal
            dias_selec = []
            if frecuencia == "WEEKLY":
                for corto, var in dias_vars.items():
                    if var.get():
                        dias_selec.append(self.dias_map[corto])
                
                if not dias_selec:
                    messagebox.showerror("Error", "Debes seleccionar al menos un día para tarea semanal")
                    return
            
            # Obtener hora/minuto
            hora = entry_hora.get().strip()
            minuto = entry_minuto.get().strip()
            
            if not hora.isdigit() or not minuto.isdigit():
                messagebox.showerror("Error", "Hora y minuto deben ser números")
                return
            
            hora_int = int(hora)
            minuto_int = int(minuto)
            
            if hora_int < 0 or hora_int > 23 or minuto_int < 0 or minuto_int > 59:
                messagebox.showerror("Error", "Horario inválido (00:00 - 23:59)")
                return
            
            horario = f"{hora_int:02d}:{minuto_int:02d}"
            
            # Validar que no sea en el pasado
            ahora = datetime.now()
            hora_tarea = datetime.now().replace(hour=hora_int, minute=minuto_int, second=0, microsecond=0)
            
            if frecuencia == "DAILY" and hora_tarea <= ahora:
                # Si es hoy y ya pasó, programar para mañana
                messagebox.showinfo(
                    "Información",
                    f"La hora {horario} ya pasó hoy.\nLa tarea se programará para mañana a las {horario}."
                )
            elif frecuencia == "WEEKLY":
                # Verificar que al menos uno de los días seleccionados sea futuro
                dias_semana_eng = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
                dia_actual = dias_semana_eng[ahora.weekday()]
                
                # Si el día de hoy está seleccionado y la hora ya pasó, advertir
                if dia_actual in dias_selec and hora_tarea <= ahora:
                    messagebox.showinfo(
                        "Información",
                        f"El horario de hoy ({horario}) ya pasó.\nLa tarea se ejecutará en los próximos días seleccionados."
                    )
            
            # Si es edición, eliminar tarea actual primero
            if es_edicion:
                nombre_completo = f"{self.prefijo_tarea}_{nombre}" if not nombre.startswith(self.prefijo_tarea) else nombre
                subprocess.run(['schtasks', '/Delete', '/TN', nombre_completo, '/F'], capture_output=True)
            
            # Crear tarea
            self._crear_tarea_windows(nombre, frecuencia, horario, dias_selec if frecuencia == "WEEKLY" else None)
            
            ventana.destroy()
        
        texto_boton = "💾 Guardar Cambios" if es_edicion else "✅ Crear Tarea"
        tk.Button(
            frame_btns,
            text=texto_boton,
            font=("Segoe UI", 10, "bold"),
            bg="#28a745",
            fg="white",
            width=15,
            command=guardar
        ).pack(side='right', padx=(10, 30))

    def _crear_tarea_windows(self, nombre, frecuencia, horario, dias=None):
        """Crea una tarea en el Programador de Tareas de Windows"""
        try:
            # Comando base
            comando = [
                'schtasks',
                '/Create',
                '/TN', nombre,
                '/TR', f'python "{self.ruta_script}"',
                '/SC', frecuencia,
                '/ST', horario
            ]
            
            # Agregar días si es semanal
            if frecuencia == 'WEEKLY' and dias:
                comando.extend(['/D', ','.join(dias)])
            
            # Forzar si ya existe
            comando.append('/F')
            
            resultado = subprocess.run(
                comando,
                capture_output=True,
                text=True
            )
            
            if resultado.returncode == 0:
                messagebox.showinfo("✅ Éxito", f"Tarea '{nombre}' creada correctamente")
                self._cargar_tareas()
            else:
                messagebox.showerror("❌ Error", f"No se pudo crear la tarea:\n{resultado.stderr}")
        
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error creando tarea:\n{e}")

    def _eliminar_tarea(self):
        """Elimina la tarea seleccionada"""
        seleccion = self.tree.selection()
        
        if not seleccion:
            messagebox.showwarning("Aviso", "Selecciona una tarea para eliminar")
            return
        
        item = self.tree.item(seleccion[0])
        nombre_tarea = item['values'][0]
        
        if nombre_tarea == 'No hay tareas programadas':
            return
        
        respuesta = messagebox.askyesno(
            "Confirmar",
            f"¿Eliminar la tarea '{nombre_tarea}'?"
        )
        
        if not respuesta:
            return
        
        try:
            # Construir nombre completo
            nombre_completo = f"{self.prefijo_tarea}_{nombre_tarea}" if not nombre_tarea.startswith(self.prefijo_tarea) else nombre_tarea
            
            resultado = subprocess.run(
                ['schtasks', '/Delete', '/TN', nombre_completo, '/F'],
                capture_output=True,
                text=True
            )
            
            if resultado.returncode == 0:
                messagebox.showinfo("✅ Éxito", f"Tarea eliminada correctamente")
                self._cargar_tareas()
            else:
                messagebox.showerror("❌ Error", f"No se pudo eliminar la tarea")
        
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error eliminando tarea:\n{e}")

    def ejecutar(self):
        """Inicia la interfaz"""
        self.root.mainloop()


def main():
    gestor = GestorTareasGUI()
    gestor.ejecutar()


if __name__ == "__main__":
    main()