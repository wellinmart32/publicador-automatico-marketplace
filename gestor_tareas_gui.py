import os
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
from datetime import datetime
from gestor_licencias import GestorLicencias


class GestorTareasGUI:
    """Gestor de tareas automáticas - Windows Task Scheduler"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🗓️ Gestor de Tareas Automáticas - Marketplace")
        self.root.geometry("800x600")
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
        
        # Treeview - simplificado
        self.tree = ttk.Treeview(
            frame_lista,
            columns=('nombre', 'estado'),
            show='headings',
            yscrollcommand=scrollbar.set,
            height=15
        )
        
        self.tree.heading('nombre', text='Nombre de Tarea')
        self.tree.heading('estado', text='Estado')
        
        self.tree.column('nombre', width=550)
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
        """Carga las tareas existentes - versión simplificada"""
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
            
            # Parsear CSV (más confiable)
            lineas = resultado.stdout.strip().split('\n')
            
            tareas_encontradas = False
            for linea in lineas[1:]:  # Skip header
                partes = linea.split('","')
                if len(partes) >= 3:
                    nombre = partes[0].replace('"', '').strip()
                    # En español: columna 0=nombre, 1=próxima ejecución, 2=estado
                    estado = partes[2].replace('"', '').strip() if len(partes) > 2 else 'N/A'
                    
                    # Solo nuestras tareas
                    if self.prefijo_tarea in nombre:
                        nombre_corto = nombre.split('\\')[-1]
                        
                        # Traducir estado
                        if 'Ready' in estado or 'Listo' in estado:
                            estado_texto = '✅ Activa'
                        elif 'Disabled' in estado or 'Deshabilitado' in estado:
                            estado_texto = '⏸️ Pausada'
                        elif 'Running' in estado or 'En ejecución' in estado:
                            estado_texto = '▶️ En ejecución'
                        else:
                            estado_texto = estado
                        
                        self.tree.insert('', 'end', values=(nombre_corto, estado_texto))
                        tareas_encontradas = True
            
            if not tareas_encontradas:
                self.tree.insert('', 'end', values=('No hay tareas programadas', ''))
        
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando tareas:\n{e}")

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
        
        # Ventana de edición
        ventana = tk.Toplevel(self.root)
        ventana.title(f"✏️ Editar: {nombre_tarea}")
        ventana.geometry("500x350")
        ventana.configure(bg="#f0f0f0")
        ventana.transient(self.root)
        ventana.grab_set()
        
        # Centrar
        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth() // 2) - (250)
        y = (ventana.winfo_screenheight() // 2) - (175)
        ventana.geometry(f'500x350+{x}+{y}')
        
        # Header
        header = tk.Frame(ventana, bg="#ffc107", pady=15)
        header.pack(fill='x')
        tk.Label(
            header,
            text=f"✏️ Editar Tarea",
            font=("Segoe UI", 14, "bold"),
            bg="#ffc107",
            fg="black"
        ).pack()
        
        # Formulario
        form = tk.Frame(ventana, bg="#f0f0f0")
        form.pack(fill='both', expand=True, padx=30, pady=20)
        
        tk.Label(form, text=f"Tarea: {nombre_tarea}", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(anchor='w', pady=(0, 15))
        
        # Frecuencia
        tk.Label(form, text="Nueva Frecuencia:", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(anchor='w', pady=(0, 5))
        var_frecuencia = tk.StringVar(value="DAILY")
        
        frame_freq = tk.Frame(form, bg="#f0f0f0")
        frame_freq.pack(anchor='w', pady=(0, 15))
        
        tk.Radiobutton(frame_freq, text="Diaria", variable=var_frecuencia, value="DAILY", bg="#f0f0f0").pack(side='left', padx=(0, 15))
        tk.Radiobutton(frame_freq, text="Semanal", variable=var_frecuencia, value="WEEKLY", bg="#f0f0f0").pack(side='left')
        
        # Horario
        tk.Label(form, text="Nuevo Horario (HH:MM):", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(anchor='w', pady=(0, 5))
        
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
            frecuencia = var_frecuencia.get()
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
            
            # Eliminar tarea actual
            nombre_completo = f"{self.prefijo_tarea}_{nombre_tarea}" if not nombre_tarea.startswith(self.prefijo_tarea) else nombre_tarea
            subprocess.run(['schtasks', '/Delete', '/TN', nombre_completo, '/F'], capture_output=True)
            
            # Recrear con nuevos parámetros
            self._crear_tarea_windows(nombre_tarea, frecuencia, horario)
            
            ventana.destroy()
        
        tk.Button(
            frame_btns,
            text="💾 Guardar Cambios",
            font=("Segoe UI", 10, "bold"),
            bg="#28a745",
            fg="white",
            width=15,
            command=guardar
        ).pack(side='right', padx=(10, 30))

    def _nueva_tarea(self):
        """Abre diálogo para crear nueva tarea"""
        ventana = tk.Toplevel(self.root)
        ventana.title("➕ Nueva Tarea Automática")
        ventana.geometry("500x400")
        ventana.configure(bg="#f0f0f0")
        ventana.transient(self.root)
        ventana.grab_set()
        
        # Centrar
        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth() // 2) - (250)
        y = (ventana.winfo_screenheight() // 2) - (200)
        ventana.geometry(f'500x400+{x}+{y}')
        
        # Header
        header = tk.Frame(ventana, bg="#28a745", pady=15)
        header.pack(fill='x')
        tk.Label(
            header,
            text="➕ Configurar Nueva Tarea",
            font=("Segoe UI", 14, "bold"),
            bg="#28a745",
            fg="white"
        ).pack()
        
        # Formulario
        form = tk.Frame(ventana, bg="#f0f0f0")
        form.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Nombre
        tk.Label(form, text="Nombre de la tarea:", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(anchor='w', pady=(0, 5))
        entry_nombre = tk.Entry(form, font=("Segoe UI", 10), width=40)
        entry_nombre.pack(pady=(0, 15))
        entry_nombre.insert(0, f"{self.prefijo_tarea}_{datetime.now().strftime('%Y%m%d_%H%M')}")
        
        # Frecuencia
        tk.Label(form, text="Frecuencia:", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(anchor='w', pady=(0, 5))
        var_frecuencia = tk.StringVar(value="DAILY")
        
        frame_freq = tk.Frame(form, bg="#f0f0f0")
        frame_freq.pack(anchor='w', pady=(0, 15))
        
        tk.Radiobutton(frame_freq, text="Diaria", variable=var_frecuencia, value="DAILY", bg="#f0f0f0").pack(side='left', padx=(0, 15))
        tk.Radiobutton(frame_freq, text="Semanal", variable=var_frecuencia, value="WEEKLY", bg="#f0f0f0").pack(side='left')
        
        # Horario
        tk.Label(form, text="Horario (HH:MM formato 24h):", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(anchor='w', pady=(0, 5))
        
        frame_hora = tk.Frame(form, bg="#f0f0f0")
        frame_hora.pack(anchor='w', pady=(0, 15))
        
        entry_hora = tk.Entry(frame_hora, font=("Segoe UI", 10), width=5)
        entry_hora.pack(side='left')
        entry_hora.insert(0, "09")
        
        tk.Label(frame_hora, text=":", font=("Segoe UI", 10), bg="#f0f0f0").pack(side='left', padx=5)
        
        entry_minuto = tk.Entry(frame_hora, font=("Segoe UI", 10), width=5)
        entry_minuto.pack(side='left')
        entry_minuto.insert(0, "00")
        
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
        
        def crear():
            nombre = entry_nombre.get().strip()
            frecuencia = var_frecuencia.get()
            hora = entry_hora.get().strip()
            minuto = entry_minuto.get().strip()
            
            if not nombre:
                messagebox.showerror("Error", "Debes ingresar un nombre")
                return
            
            if not hora.isdigit() or not minuto.isdigit():
                messagebox.showerror("Error", "Hora y minuto deben ser números")
                return
            
            hora_int = int(hora)
            minuto_int = int(minuto)
            
            if hora_int < 0 or hora_int > 23 or minuto_int < 0 or minuto_int > 59:
                messagebox.showerror("Error", "Horario inválido (00:00 - 23:59)")
                return
            
            horario = f"{hora_int:02d}:{minuto_int:02d}"
            
            # Crear tarea
            self._crear_tarea_windows(nombre, frecuencia, horario)
            ventana.destroy()
        
        tk.Button(
            frame_btns,
            text="✅ Crear Tarea",
            font=("Segoe UI", 10, "bold"),
            bg="#28a745",
            fg="white",
            width=12,
            command=crear
        ).pack(side='right', padx=(10, 30))

    def _crear_tarea_windows(self, nombre, frecuencia, horario):
        """Crea una tarea en el Programador de Tareas de Windows"""
        try:
            # Comando schtasks
            comando = [
                'schtasks',
                '/Create',
                '/TN', nombre,
                '/TR', f'python "{self.ruta_script}"',
                '/SC', frecuencia,
                '/ST', horario,
                '/F'  # Forzar si ya existe
            ]
            
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