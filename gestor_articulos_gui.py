import os
import sys
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from compartido.gestor_archivos import (
    leer_config_global, leer_datos_articulo, guardar_datos_articulo, numeros_articulos,
    articulo_listo_para_publicar, crear_carpeta_articulo, _carpeta_productos,
    ESTADOS_ARTICULO, CATEGORIAS_ARTICULO, EXTENSIONES_IMAGEN
)


class GestorArticulosGUI:
    """Interfaz gráfica para gestionar artículos de Marketplace"""

    def __init__(self):
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('AutomaPro.GestorArticulos')
        except Exception:
            pass

        # Ruta siempre relativa al ejecutable, no al directorio de trabajo
        self.carpeta_base = _carpeta_productos()
        self.ubicacion_defecto = leer_config_global()['ubicacion']

        self.root = tk.Tk()
        self.root.withdraw()

        self.root.title("🛍️ Gestor de Productos - Marketplace")
        self.root.minsize(900, 700)
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f0f0")

        try:
            base_ico = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
            ico = os.path.join(base_ico, 'iconos', 'edit.ico')
            self.root.iconbitmap(ico)
            # default= hace que las subventanas y los diálogos hereden el ícono en vez de la pluma de Tkinter
            self.root.iconbitmap(default=ico)
        except Exception:
            pass

        width = 900
        height = 700
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        self.root.deiconify()

        self.articulo_actual = None
        self.numeros_lista = []

        self._construir_ui()
        self._cargar_articulos()

    def _construir_ui(self):

        # Header
        header = tk.Frame(self.root, bg="#198754", pady=12)
        header.pack(fill='x')
        tk.Label(
            header,
            text="🛍️ Gestor de Productos - Marketplace",
            font=("Segoe UI", 14, "bold"),
            bg="#198754",
            fg="white"
        ).pack()

        # Panel principal
        panel = tk.Frame(self.root, bg="#f0f0f0")
        panel.pack(fill='both', expand=True, padx=10, pady=10)

        # ==================== PANEL IZQUIERDO ====================
        panel_izq = tk.Frame(panel, bg="#f0f0f0", width=200)
        panel_izq.pack(side='left', fill='y', padx=(0, 5))
        panel_izq.pack_propagate(False)

        tk.Label(
            panel_izq,
            text="📂 Artículos",
            font=("Segoe UI", 10, "bold"),
            bg="#f0f0f0"
        ).pack(anchor='w', pady=(0, 5))

        self.lbl_contador = tk.Label(
            panel_izq,
            text="0 artículos",
            font=("Segoe UI", 8),
            fg="gray",
            bg="#f0f0f0"
        )
        self.lbl_contador.pack(anchor='w', pady=(0, 5))

        # Lista
        frame_lista = tk.Frame(panel_izq, bg="#f0f0f0")
        frame_lista.pack(fill='both', expand=True)

        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side='right', fill='y')

        self.lista = tk.Listbox(
            frame_lista,
            yscrollcommand=scrollbar.set,
            font=("Segoe UI", 9),
            selectmode='single',
            bg="white",
            relief='solid',
            borderwidth=1
        )
        self.lista.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.lista.yview)

        self.lista.bind('<<ListboxSelect>>', self._on_seleccionar)

        # Botones
        frame_btn_lista = tk.Frame(panel_izq, bg="#f0f0f0")
        frame_btn_lista.pack(fill='x', pady=(5, 0))

        tk.Button(
            frame_btn_lista,
            text="➕ Nuevo",
            font=("Segoe UI", 9, "bold"),
            bg="#198754",
            fg="white",
            command=self._nuevo_articulo
        ).pack(side='left', expand=True, fill='x', padx=(0, 2))

        tk.Button(
            frame_btn_lista,
            text="🗑️ Eliminar",
            font=("Segoe UI", 9),
            bg="#dc3545",
            fg="white",
            command=self._eliminar_articulo
        ).pack(side='left', expand=True, fill='x', padx=(2, 0))

        # ==================== PANEL DERECHO ====================
        panel_der = tk.Frame(panel, bg="#f0f0f0")
        panel_der.pack(side='left', fill='both', expand=True)

        # Nombre artículo
        self.lbl_articulo = tk.Label(
            panel_der,
            text="(ninguno seleccionado)",
            font=("Segoe UI", 12, "bold"),
            fg="gray",
            bg="#f0f0f0"
        )
        self.lbl_articulo.pack(anchor='w', pady=(0, 8))

        # Notebook (pestañas)
        self.notebook = ttk.Notebook(panel_der)
        self.notebook.pack(fill='both', expand=True)

        # PESTAÑA DATOS
        tab_datos = ttk.Frame(self.notebook)
        self.notebook.add(tab_datos, text="📝 Datos del artículo")

        # Scroll para formulario (sin scrollbar visible si no es necesario)
        canvas = tk.Canvas(tab_datos, bg="#f0f0f0", highlightthickness=0)
        scrollbar_form = tk.Scrollbar(tab_datos, orient="vertical", command=canvas.yview)
        frame_form = tk.Frame(canvas, bg="#f0f0f0")

        def actualizar_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Solo mostrar scrollbar si el contenido es mayor que el canvas
            if frame_form.winfo_reqheight() > canvas.winfo_height():
                scrollbar_form.pack(side="right", fill="y")
            else:
                scrollbar_form.pack_forget()

        frame_form.bind("<Configure>", actualizar_scroll)

        canvas.create_window((0, 0), window=frame_form, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_form.set)

        canvas.pack(side="left", fill="both", expand=True)

        # ==================== CAMPOS DEL FORMULARIO ====================
        self.vars = {}

        # Título
        tk.Label(
            frame_form,
            text="Título",
            font=("Segoe UI", 9, "bold"),
            bg="#f0f0f0"
        ).pack(anchor='w', padx=15, pady=(8, 2))
        
        self.vars['titulo'] = tk.StringVar()
        tk.Entry(
            frame_form,
            textvariable=self.vars['titulo'],
            font=("Segoe UI", 10),
            width=50
        ).pack(anchor='w', padx=15)

        # Precio (solo números, decimales opcionales)
        tk.Label(
            frame_form,
            text="Precio (USD)",
            font=("Segoe UI", 9, "bold"),
            bg="#f0f0f0"
        ).pack(anchor='w', padx=15, pady=(8, 2))
        
        self.vars['precio'] = tk.StringVar()
        entry_precio = tk.Entry(
            frame_form,
            textvariable=self.vars['precio'],
            font=("Segoe UI", 10),
            width=50
        )
        entry_precio.pack(anchor='w', padx=15)
        
        # Validación de precio
        def validar_precio(texto):
            if texto == "":
                return True
            # Solo números y un punto decimal
            if texto.replace('.', '', 1).isdigit():
                return True
            return False
        
        vcmd_precio = (self.root.register(validar_precio), '%P')
        entry_precio.config(validate='key', validatecommand=vcmd_precio)

        # Categoría
        tk.Label(
            frame_form,
            text="Categoría",
            font=("Segoe UI", 9, "bold"),
            bg="#f0f0f0"
        ).pack(anchor='w', padx=15, pady=(8, 2))
        
        self.vars['categoria'] = tk.StringVar()
        ttk.Combobox(
            frame_form,
            textvariable=self.vars['categoria'],
            values=CATEGORIAS_ARTICULO,
            font=("Segoe UI", 10),
            width=48
        ).pack(anchor='w', padx=15)

        # Estado
        tk.Label(
            frame_form,
            text="Estado",
            font=("Segoe UI", 9, "bold"),
            bg="#f0f0f0"
        ).pack(anchor='w', padx=15, pady=(8, 2))
        
        self.vars['estado'] = tk.StringVar(value=ESTADOS_ARTICULO[0])
        ttk.Combobox(
            frame_form,
            textvariable=self.vars['estado'],
            values=ESTADOS_ARTICULO,
            font=("Segoe UI", 10),
            width=48,
            state='readonly'
        ).pack(anchor='w', padx=15)

        # Ubicación (Combobox con ciudades de Ecuador)
        tk.Label(
            frame_form,
            text="Ubicación",
            font=("Segoe UI", 9, "bold"),
            bg="#f0f0f0"
        ).pack(anchor='w', padx=15, pady=(8, 2))
        
        self.vars['ubicacion'] = tk.StringVar()
        ciudades_ecuador = [
            "Quito", "Guayaquil", "Cuenca", "Santo Domingo", "Machala",
            "Manta", "Portoviejo", "Loja", "Ambato", "Esmeraldas",
            "Quevedo", "Riobamba", "Ibarra", "Milagro", "Latacunga"
        ]
        if self.ubicacion_defecto not in ciudades_ecuador:
            ciudades_ecuador.append(self.ubicacion_defecto)
        combo_ubicacion = ttk.Combobox(
            frame_form,
            textvariable=self.vars['ubicacion'],
            values=sorted(ciudades_ecuador),
            font=("Segoe UI", 10),
            width=48,
            state='readonly'
        )
        combo_ubicacion.pack(anchor='w', padx=15)
        combo_ubicacion.set(self.ubicacion_defecto)  # Por defecto, la ciudad del Configurador

        # Encuentro público
        tk.Label(
            frame_form,
            text="Encuentro en lugar público",
            font=("Segoe UI", 9, "bold"),
            bg="#f0f0f0"
        ).pack(anchor='w', padx=15, pady=(8, 2))
        
        self.vars['encuentro_publico'] = tk.StringVar(value="Si")
        frame_encuentro = tk.Frame(frame_form, bg="#f0f0f0")
        frame_encuentro.pack(anchor='w', padx=15)
        for opcion, label in [('Si', 'Sí'), ('No', 'No')]:
            tk.Radiobutton(
                frame_encuentro, text=label,
                variable=self.vars['encuentro_publico'], value=opcion,
                bg="#f0f0f0", font=("Segoe UI", 10)
            ).pack(side='left', padx=(0, 10))

        # Etiquetas
        tk.Label(
            frame_form,
            text="Etiquetas (separadas por comas)",
            font=("Segoe UI", 9, "bold"),
            bg="#f0f0f0"
        ).pack(anchor='w', padx=15, pady=(8, 2))
        
        self.vars['etiquetas'] = tk.StringVar()
        tk.Entry(
            frame_form,
            textvariable=self.vars['etiquetas'],
            font=("Segoe UI", 10),
            width=50
        ).pack(anchor='w', padx=15)

        # SKU
        tk.Label(
            frame_form,
            text="SKU (código de producto)",
            font=("Segoe UI", 9, "bold"),
            bg="#f0f0f0"
        ).pack(anchor='w', padx=15, pady=(8, 2))
        
        self.vars['sku'] = tk.StringVar()
        tk.Entry(
            frame_form,
            textvariable=self.vars['sku'],
            font=("Segoe UI", 10),
            width=50
        ).pack(anchor='w', padx=15)

        # Descripción (textarea con scrollbar)
        tk.Label(
            frame_form,
            text="Descripción",
            font=("Segoe UI", 9, "bold"),
            bg="#f0f0f0"
        ).pack(anchor='w', padx=15, pady=(8, 2))

        frame_desc = tk.Frame(frame_form, bg="#f0f0f0")
        frame_desc.pack(anchor='w', padx=15, pady=(0, 12))

        scrollbar_desc = tk.Scrollbar(frame_desc)
        scrollbar_desc.pack(side='right', fill='y')

        self.texto_desc = tk.Text(
            frame_desc,
            font=("Segoe UI", 10),
            wrap='word',
            height=12,
            width=50,
            yscrollcommand=scrollbar_desc.set
        )
        self.texto_desc.pack(side='left')
        scrollbar_desc.config(command=self.texto_desc.yview)

        # PESTAÑA IMÁGENES
        tab_img = ttk.Frame(self.notebook)
        self.notebook.add(tab_img, text="🖼️ Imágenes")

        tk.Label(
            tab_img,
            text="Imágenes del artículo",
            font=("Segoe UI", 10, "bold"),
            bg="#f0f0f0"
        ).pack(anchor='w', padx=15, pady=(8, 0))
        tk.Label(
            tab_img,
            text="Hasta 10 imágenes; se suben en orden alfabético. Un producto sin imágenes no se publica.",
            font=("Segoe UI", 8),
            fg="gray",
            bg="#f0f0f0"
        ).pack(anchor='w', padx=15, pady=(0, 4))

        # Lista de imágenes
        frame_imgs = tk.Frame(tab_img, bg="#f0f0f0")
        frame_imgs.pack(fill='both', expand=True, padx=15, pady=(0, 8))

        scrollbar_imgs = tk.Scrollbar(frame_imgs)
        scrollbar_imgs.pack(side='right', fill='y')

        self.lista_imagenes = tk.Listbox(
            frame_imgs,
            yscrollcommand=scrollbar_imgs.set,
            font=("Segoe UI", 9),
            height=10,
            bg="white"
        )
        self.lista_imagenes.pack(side='left', fill='both', expand=True)
        scrollbar_imgs.config(command=self.lista_imagenes.yview)

        # Botones de imágenes
        frame_btn_imgs = tk.Frame(tab_img, bg="#f0f0f0")
        frame_btn_imgs.pack(fill='x', padx=15, pady=(0, 8))

        tk.Button(
            frame_btn_imgs,
            text="➕ Agregar imagen",
            font=("Segoe UI", 9),
            bg="#198754",
            fg="white",
            command=self._agregar_imagen
        ).pack(side='left', padx=(0, 5))

        tk.Button(
            frame_btn_imgs,
            text="🗑️ Eliminar imagen",
            font=("Segoe UI", 9),
            bg="#dc3545",
            fg="white",
            command=self._eliminar_imagen
        ).pack(side='left')

        # Botón guardar
        tk.Button(
            panel_der,
            text="💾 Guardar artículo",
            font=("Segoe UI", 10, "bold"),
            bg="#198754",
            fg="white",
            command=self._guardar_articulo
        ).pack(anchor='e', pady=(8, 0))

    def _cargar_articulos(self):
        """Carga la lista de artículos, marcando los que están listos para publicar"""
        self.lista.delete(0, tk.END)
        os.makedirs(self.carpeta_base, exist_ok=True)

        self.numeros_lista = numeros_articulos()
        listos = 0
        for numero in self.numeros_lista:
            datos = leer_datos_articulo(numero, avisar=False) or {}
            listo = articulo_listo_para_publicar(numero)
            listos += 1 if listo else 0
            titulo = datos.get('titulo', '')
            texto = f"{'✅' if listo else '⚠️'} Articulo_{numero}" + (f" · {titulo[:22]}" if titulo else "")
            self.lista.insert(tk.END, texto)

        self.lbl_contador.config(text=f"{len(self.numeros_lista)} artículos · {listos} listos para publicar")

    def _nombre_seleccionado(self):
        """Carpeta (Articulo_N) del elemento seleccionado en la lista, o None"""
        seleccion = self.lista.curselection()
        if not seleccion:
            return None
        return f"Articulo_{self.numeros_lista[seleccion[0]]}"

    def _numero_actual(self):
        return int(self.articulo_actual.split('_')[1])

    def _seleccionar_en_lista(self, nombre):
        for i, numero in enumerate(self.numeros_lista):
            if f"Articulo_{numero}" == nombre:
                self.lista.selection_clear(0, tk.END)
                self.lista.selection_set(i)
                self.lista.see(i)
                break

    def _on_seleccionar(self, event):
        """Al seleccionar un artículo lo muestra en el editor"""
        nombre = self._nombre_seleccionado()
        if not nombre:
            return

        self.articulo_actual = nombre
        self.lbl_articulo.config(text=nombre, fg="#198754")

        # Limpiar campos y poner los valores por defecto
        for var in self.vars.values():
            var.set("")
        self.vars['estado'].set(ESTADOS_ARTICULO[0])
        self.vars['ubicacion'].set(self.ubicacion_defecto)
        self.vars['encuentro_publico'].set("Si")
        self.texto_desc.delete('1.0', tk.END)

        try:
            datos = leer_datos_articulo(self._numero_actual(), avisar=False) or {}
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al leer datos: {e}")
            datos = {}

        for clave, var in self.vars.items():
            if datos.get(clave):
                var.set(datos[clave])
        if datos.get('descripcion'):
            self.texto_desc.insert('1.0', datos['descripcion'])

        self._cargar_imagenes()

    def _cargar_imagenes(self):
        """Carga la lista de imágenes del artículo actual"""
        self.lista_imagenes.delete(0, tk.END)

        if not self.articulo_actual:
            return

        carpeta_imgs = os.path.join(self.carpeta_base, self.articulo_actual, "imagenes")

        if os.path.exists(carpeta_imgs):
            imagenes = [f for f in os.listdir(carpeta_imgs) if f.lower().endswith(EXTENSIONES_IMAGEN)]
            for img in sorted(imagenes):
                self.lista_imagenes.insert(tk.END, img)

    def _guardar_articulo(self):
        """Guarda los datos del artículo en datos.txt"""
        if not self.articulo_actual:
            messagebox.showwarning("⚠️ Aviso", "Selecciona un artículo")
            return

        # Validar precio
        precio = self.vars['precio'].get().strip()
        if precio:
            try:
                if float(precio) < 0:
                    messagebox.showerror("❌ Error", "El precio no puede ser negativo")
                    return
            except ValueError:
                messagebox.showerror("❌ Error", "El precio debe ser un número válido")
                return

        try:
            numero = self._numero_actual()
            datos = leer_datos_articulo(numero, avisar=False) or {}
            for clave, var in self.vars.items():
                datos[clave] = var.get().strip()
            datos['descripcion'] = self.texto_desc.get('1.0', tk.END).strip()
            datos.setdefault('disponibilidad', 'Publicar como disponible')
            guardar_datos_articulo(numero, datos)

            nombre = self.articulo_actual
            self._cargar_articulos()
            self._seleccionar_en_lista(nombre)
            messagebox.showinfo("✅ Éxito", f"Artículo guardado: {nombre}")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al guardar: {e}")

    def _nuevo_articulo(self):
        """Crea un nuevo artículo con el número siguiente al mayor existente"""
        numeros = numeros_articulos()
        siguiente_num = (numeros[-1] + 1) if numeros else 1
        nombre = f"Articulo_{siguiente_num}"

        try:
            crear_carpeta_articulo(siguiente_num)
            datos = leer_datos_articulo(siguiente_num, avisar=False) or {}
            datos.update({'titulo': '', 'precio': '', 'descripcion': ''})
            guardar_datos_articulo(siguiente_num, datos)

            self._cargar_articulos()
            self._seleccionar_en_lista(nombre)
            self._on_seleccionar(None)

            messagebox.showinfo("✅ Éxito", f"Artículo creado: {nombre}")

        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al crear artículo: {e}")

    def _eliminar_articulo(self):
        """Elimina el artículo seleccionado"""
        nombre = self._nombre_seleccionado()
        if not nombre:
            messagebox.showwarning("⚠️ Aviso", "Selecciona un artículo para eliminar")
            return

        confirmar = messagebox.askyesno(
            "🗑️ Confirmar eliminación",
            f"¿Estás seguro de eliminar '{nombre}'?\n\nSe eliminarán todos los datos e imágenes.\n\nEsta acción no se puede deshacer."
        )

        if not confirmar:
            return

        carpeta = os.path.join(self.carpeta_base, nombre)

        try:
            shutil.rmtree(carpeta)
            self._cargar_articulos()
            self.articulo_actual = None
            self.lbl_articulo.config(text="(ninguno seleccionado)", fg="gray")
            messagebox.showinfo("✅ Éxito", f"Artículo eliminado: {nombre}")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al eliminar: {e}")

    def _agregar_imagen(self):
        """Agrega una imagen al artículo actual"""
        if not self.articulo_actual:
            messagebox.showwarning("⚠️ Aviso", "Selecciona un artículo primero")
            return

        archivos = filedialog.askopenfilenames(
            title="Seleccionar imágenes",
            filetypes=[
                ("Imágenes", "*.jpg *.jpeg *.png *.gif *.webp"),
                ("Todos los archivos", "*.*")
            ]
        )

        if not archivos:
            return

        carpeta_imgs = os.path.join(self.carpeta_base, self.articulo_actual, "imagenes")
        os.makedirs(carpeta_imgs, exist_ok=True)

        try:
            for archivo in archivos:
                nombre = os.path.basename(archivo)
                destino = os.path.join(carpeta_imgs, nombre)
                shutil.copy2(archivo, destino)

            self._cargar_imagenes()
            self._refrescar_lista_actual()
            messagebox.showinfo("✅ Éxito", f"{len(archivos)} imagen(es) agregada(s)")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al agregar imágenes: {e}")

    def _eliminar_imagen(self):
        """Elimina la imagen seleccionada"""
        seleccion = self.lista_imagenes.curselection()
        if not seleccion:
            messagebox.showwarning("⚠️ Aviso", "Selecciona una imagen para eliminar")
            return

        if not self.articulo_actual:
            return

        nombre_img = self.lista_imagenes.get(seleccion[0])

        confirmar = messagebox.askyesno(
            "🗑️ Confirmar",
            f"¿Eliminar '{nombre_img}'?"
        )

        if not confirmar:
            return

        ruta_img = os.path.join(self.carpeta_base, self.articulo_actual, "imagenes", nombre_img)

        try:
            os.remove(ruta_img)
            self._cargar_imagenes()
            self._refrescar_lista_actual()
            messagebox.showinfo("✅ Éxito", "Imagen eliminada")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al eliminar: {e}")

    def _refrescar_lista_actual(self):
        """Actualiza la marca ✅/⚠️ de la lista sin perder la selección"""
        nombre = self.articulo_actual
        self._cargar_articulos()
        if nombre:
            self._seleccionar_en_lista(nombre)

    def ejecutar(self):
        self.root.mainloop()


def main():
    app = GestorArticulosGUI()
    app.ejecutar()


if __name__ == "__main__":
    main()