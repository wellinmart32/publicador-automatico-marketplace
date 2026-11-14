from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from PIL import Image
from io import BytesIO
import time
import os

from compartido.navegador import abrir_navegador
from compartido.gestor_archivos import _carpeta_productos, guardar_datos_articulo


class ExtractorWhatsApp:
    """Extrae productos del catálogo de WhatsApp Web"""

    def __init__(self, config=None):
        self.driver = None
        self.wait = None
        self.config = config or {}
        self.carpeta_principal = _carpeta_productos()
        self.catalogo = []  # productos reales del catálogo de WhatsApp, de arriba a abajo

    def iniciar_navegador(self):
        """Abre el navegador configurado y entra a WhatsApp Web"""
        self.driver = abrir_navegador(self.config)
        self.driver.set_script_timeout(15)
        self.wait = WebDriverWait(self.driver, 60)

        print("📱 Abriendo WhatsApp Web...")
        self.driver.get("https://web.whatsapp.com")
        time.sleep(3)


    # Estados de WhatsApp Web. #side / #pane-side es la columna de chats: existe solo cuando ya cargó todo.
    MINUTOS_ESPERA_QR = 4
    MINUTOS_ESPERA_SINCRONIZACION = 10
    XPATH_LISTO = ("//div[@id='side'] | //div[@id='pane-side'] | "
                   "//*[@aria-label='Lista de chats'] | //*[@aria-label='Chat list']")
    XPATH_BUSQUEDA = ("//div[@id='side']//input[@role='textbox'] | "
                      "//div[@id='side']//input[@type='text'] | "
                      "//div[@id='side']//div[@contenteditable='true']")
    XPATH_BOTON_CATALOGO = ("//header//button[@aria-label='Catálogo' or @aria-label='Catalog'] | "
                            "//button[@aria-label='Catálogo' or @aria-label='Catalog']")
    XPATH_DETALLE = "//*[@data-testid='product-details']"
    XPATH_LEER_MAS = (XPATH_DETALLE + "//span[@role='button' and "
                      "(@aria-label='Leer más' or @aria-label='Read more')]")
    XPATH_IMAGENES_DETALLE = XPATH_DETALLE + "//img[starts-with(@src, 'blob:')]"
    XPATH_IMAGENES_FUERA_LISTA = "//img[starts-with(@src, 'blob:')][not(ancestor::div[@role='listitem'])]"

    def _estado_whatsapp(self):
        """'listo', 'qr' (pide escanear) o 'cargando' (sincronizando chats u otra pantalla intermedia)"""
        try:
            if self.driver.find_elements(By.XPATH, self.XPATH_LISTO):
                return 'listo'
            if self.driver.find_elements(By.XPATH, "//canvas[@aria-label] | //div[@data-ref]//canvas"):
                return 'qr'
        except Exception:
            pass
        return 'cargando'

    @staticmethod
    def _notificar(titulo, mensaje):
        """Aviso emergente para que el usuario vea que debe actuar en el navegador"""
        import threading

        def _mostrar():
            try:
                import tkinter as tk
                from compartido.toast import Toast
                root = tk.Tk()
                root.withdraw()
                Toast.advertencia(root, f"{titulo}\n{mensaje}", duracion=8000)
                root.after(8500, root.destroy)
                root.mainloop()
            except Exception:
                pass
        threading.Thread(target=_mostrar, daemon=True).start()

    def esperar_whatsapp_cargado(self):
        """
        Espera a que WhatsApp Web quede listo:
        - si muestra el QR, espera hasta MINUTOS_ESPERA_QR a que lo escanees;
        - después espera la sincronización de chats (la barra de carga), que la primera vez puede tardar varios minutos.
        No cerrar el navegador a mitad de la sincronización: si se corta, WhatsApp no guarda la sesión y vuelve a pedir el QR.
        """
        print("⏳ Esperando que WhatsApp Web cargue...")
        inicio = time.time()
        limite = inicio + 60 * (self.MINUTOS_ESPERA_QR + self.MINUTOS_ESPERA_SINCRONIZACION)
        limite_qr = inicio + 60 * self.MINUTOS_ESPERA_QR
        estado_anterior = None
        ultimo_aviso = 0

        while time.time() < limite:
            estado = self._estado_whatsapp()

            if estado == 'listo':
                print("✅ WhatsApp Web cargado correctamente")
                time.sleep(3)
                return True

            if estado != estado_anterior:
                if estado == 'qr':
                    print(f"\n📱 Escanea el código QR con tu celular (WhatsApp → Dispositivos vinculados). "
                          f"Tienes {self.MINUTOS_ESPERA_QR} minutos.")
                    self._notificar("Vincular WhatsApp Web",
                                    f"Escanea el código QR en el navegador.\nTienes {self.MINUTOS_ESPERA_QR} minutos.")
                else:
                    print("⏳ Cargando tus chats... la primera vez puede tardar varios minutos. No cierres el navegador.")
                estado_anterior = estado
                ultimo_aviso = time.time()

            if estado == 'qr' and time.time() > limite_qr:
                print("❌ No se escaneó el código QR a tiempo")
                return False

            if time.time() - ultimo_aviso >= 30:
                transcurrido = int(time.time() - inicio)
                print(f"   ⏳ {'Esperando el escaneo' if estado == 'qr' else 'Sigue cargando'}... ({transcurrido} s)")
                ultimo_aviso = time.time()
            time.sleep(2)

        print("❌ WhatsApp Web no terminó de cargar a tiempo")
        return False


    # ------------------------------------------------------------------
    # Buscar contacto y abrir su catálogo (WhatsApp Web, versión 2026)
    # ------------------------------------------------------------------
    def buscar_contacto(self, nombre_contacto):
        """Busca un contacto en WhatsApp y abre su chat"""
        print(f"🔍 Buscando contacto: {nombre_contacto}")
        try:
            campo_busqueda = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, self.XPATH_BUSQUEDA))
            )
            campo_busqueda.click()
            time.sleep(0.5)

            campo_busqueda.send_keys(Keys.CONTROL + "a")
            campo_busqueda.send_keys(Keys.BACKSPACE)
            time.sleep(0.3)

            for caracter in nombre_contacto:
                campo_busqueda.send_keys(caracter)
                time.sleep(0.05)

            time.sleep(2)

            resultado = None
            for xpath in (f"//span[@title={self._literal_xpath(nombre_contacto)}]",
                          f"//span[contains(@title, {self._literal_xpath(nombre_contacto)})]"):
                try:
                    resultado = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    break
                except Exception:
                    continue
            if resultado is None:
                print(f"❌ No se encontró el contacto '{nombre_contacto}' en los chats")
                return False

            try:
                resultado.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", resultado)
            time.sleep(2)

            print(f"✅ Contacto '{nombre_contacto}' abierto")
            return True

        except Exception as e:
            print(f"❌ Error buscando contacto: {e}")
            return False

    @staticmethod
    def _literal_xpath(texto):
        """Convierte un texto en literal XPath seguro (maneja comillas)"""
        if "'" not in texto:
            return f"'{texto}'"
        if '"' not in texto:
            return f'"{texto}"'
        partes = texto.split("'")
        return "concat(" + ", \"'\", ".join(f"'{p}'" for p in partes) + ")"

    def abrir_catalogo(self):
        """Abre el catálogo con el botón 'Catálogo' de la cabecera del chat"""
        print("🛒 Abriendo catálogo...")
        try:
            boton = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, self.XPATH_BOTON_CATALOGO))
            )
            try:
                boton.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", boton)
            time.sleep(3)
            print("✅ Catálogo abierto correctamente")
            return True
        except Exception:
            print("❌ Este contacto no tiene el botón 'Catálogo' en su chat "
                  "(¿es una cuenta de WhatsApp Business con catálogo?)")
            return False

    def ir_a_todos_articulos(self):
        """Entra a 'Todos los artículos' del catálogo (si existe esa sección)"""
        print("📦 Buscando 'Todos los artículos'...")
        try:
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//span[text()='Todos los artículos']"))
                )
            except Exception:
                print("   ⚠️  No hay sección 'Todos los artículos'; se usa la lista que ya está visible")
                return True

            boton = self.driver.find_element(
                By.XPATH, "//a[@role='button' and contains(@title, 'Todos los artículos')]")
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton)
            time.sleep(1)
            try:
                boton.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", boton)
            print("   ✅ Clic en 'Todos los artículos' ejecutado")
            time.sleep(4)
            return True
        except Exception as e:
            print(f"⚠️  Error en ir_a_todos_articulos: {e}")
            print("   Continuando de todos modos...")
            return True

    # ------------------------------------------------------------------
    # Lista de productos (lista virtualizada: solo se dibujan los visibles)
    # ------------------------------------------------------------------
    JS_CONTENEDOR = """
    const it = document.querySelector("div[role='listitem']");
    if (!it) return null;
    let el = it.parentElement;
    while (el && el !== document.body) {
        const o = getComputedStyle(el).overflowY;
        if ((o === 'auto' || o === 'scroll') && el.scrollHeight > el.clientHeight) return el;
        el = el.parentElement;
    }
    return null;
    """

    JS_LEER_ITEMS = """
    const cont = arguments[0];
    const base = cont ? cont.getBoundingClientRect().top : 0;
    const desp = cont ? cont.scrollTop : 0;
    return Array.from(document.querySelectorAll("div[role='listitem']")).map(it => {
        const r = it.getBoundingClientRect();
        const t = it.querySelector("[data-testid='cell-frame-title']");
        let titulo = '';
        if (t) {
            const s = t.querySelector('span[title]');
            titulo = (s && s.getAttribute('title')) || t.getAttribute('title') || t.textContent || '';
        }
        const texto = it.innerText || '';
        if (!titulo) titulo = texto.split('\\n')[0] || '';
        return {
            y: Math.round(r.top - base + desp),
            titulo: titulo.trim(),
            video: !!it.querySelector("video, [data-icon*='play']"),
            categoria: texto.includes('Ver todo'),
            imagen: !!it.querySelector('img')
        };
    });
    """

    JS_BUSCAR_ITEM = """
    const cont = arguments[0], y = arguments[1];
    const base = cont ? cont.getBoundingClientRect().top : 0;
    const desp = cont ? cont.scrollTop : 0;
    let mejor = null, dist = 1e9;
    for (const it of document.querySelectorAll("div[role='listitem']")) {
        const d = Math.abs(Math.round(it.getBoundingClientRect().top - base + desp) - y);
        if (d < dist) { dist = d; mejor = it; }
    }
    if (!mejor || dist > 40) return null;
    return mejor.querySelector("div[role='button']") || mejor;
    """

    def _contenedor_lista(self):
        """Elemento con scroll que contiene la lista de productos (None si la lista cabe entera)"""
        try:
            return self.driver.execute_script(self.JS_CONTENEDOR)
        except Exception:
            return None

    def _escanear_catalogo(self):
        """
        Recorre la lista de arriba hacia abajo y guarda la posición y el título de cada producto real
        (se descartan videos y categorías). Resultado en self.catalogo, ordenado de arriba a abajo.
        """
        print("📜 Leyendo todos los productos del catálogo...")
        encontrados = {}
        contenedor = self._contenedor_lista()
        if contenedor is not None:
            self.driver.execute_script("arguments[0].scrollTop = 0;", contenedor)
            time.sleep(1)

        for _ in range(300):
            try:
                items = self.driver.execute_script(self.JS_LEER_ITEMS, contenedor) or []
            except Exception:
                items = []
            for item in items:
                if item.get('video') or item.get('categoria'):
                    continue
                if not item.get('titulo') and not item.get('imagen'):
                    continue
                encontrados.setdefault(round(item['y'] / 20), item)

            if contenedor is None:
                break
            ya_abajo = self.driver.execute_script(
                "const c = arguments[0]; const antes = c.scrollTop; "
                "c.scrollTop = antes + Math.max(200, c.clientHeight * 0.6); "
                "return c.scrollTop === antes;", contenedor)
            time.sleep(0.8)
            if ya_abajo:
                # Una última lectura al fondo, por si quedó algo sin leer
                try:
                    items = self.driver.execute_script(self.JS_LEER_ITEMS, contenedor) or []
                except Exception:
                    items = []
                for item in items:
                    if not (item.get('video') or item.get('categoria')) and (item.get('titulo') or item.get('imagen')):
                        encontrados.setdefault(round(item['y'] / 20), item)
                break

        self.catalogo = [encontrados[k] for k in sorted(encontrados)]
        return self.catalogo

    def contar_productos_catalogo(self):
        """Cuenta los productos reales del catálogo"""
        try:
            catalogo = self._escanear_catalogo()
            print(f"📊 Productos reales en el catálogo: {len(catalogo)}")
            for numero, producto in enumerate(catalogo[:5], 1):
                print(f"   {numero}. {producto.get('titulo') or '(sin título)'}")
            if len(catalogo) > 5:
                print(f"   ... y {len(catalogo) - 5} más")
            return len(catalogo)
        except Exception as e:
            print(f"⚠️  Error contando productos: {e}")
            self.catalogo = []
            return 0

    def _abrir_producto(self, indice):
        """Baja la lista hasta el producto número 'indice' (desde 0) y lo abre"""
        producto = self.catalogo[indice]
        for intento in range(3):
            contenedor = self._contenedor_lista()
            if contenedor is not None:
                self.driver.execute_script(
                    "arguments[0].scrollTop = Math.max(0, arguments[1] - 150);", contenedor, producto['y'])
                time.sleep(1.2)
            boton = self.driver.execute_script(self.JS_BUSCAR_ITEM, contenedor, producto['y'])
            if boton is None:
                time.sleep(1.5)
                continue
            try:
                boton.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", boton)
            try:
                WebDriverWait(self.driver, 12).until(
                    EC.presence_of_element_located((By.XPATH, self.XPATH_DETALLE))
                )
                return True
            except Exception:
                continue
        return False

    def _cerrar_producto(self):
        """Vuelve de la ficha del producto a la lista"""
        try:
            botones = [b for b in self.driver.find_elements(
                By.XPATH, "//button[@aria-label='Atrás' or @aria-label='Back']") if b.is_displayed()]
            if botones:
                try:
                    botones[-1].click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", botones[-1])
            else:
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        except Exception:
            pass
        time.sleep(1.5)

    def extraer_productos(self, numeros_destino, indice_inicio_catalogo=0):
        """Extrae productos desde un índice del catálogo y los guarda en las carpetas Articulo_N indicadas"""
        cantidad_maxima = len(numeros_destino)
        print(f"\n🎯 Iniciando extracción de hasta {cantidad_maxima} productos...")
        print(f"   Guardando en: {', '.join(f'Articulo_{n}' for n in numeros_destino)}")
        print(f"   Desde producto {indice_inicio_catalogo + 1} del catálogo de WhatsApp\n")

        productos_extraidos = []
        indice_real = indice_inicio_catalogo
        total = len(self.catalogo)

        for i in range(cantidad_maxima):
            numero_articulo = numeros_destino[i]

            if indice_real >= total:
                print(f"[INFO] Solo hay {total} productos en el catálogo; llegaste al final.")
                break

            print(f"\n{'='*60}")
            print(f"📦 PRODUCTO {i + 1}/{cantidad_maxima} → ARTICULO_{numero_articulo}")
            print(f"   (Producto {indice_real + 1} de {total} del catálogo de WhatsApp: "
                  f"{self.catalogo[indice_real].get('titulo') or 'sin título'})")
            print(f"{'='*60}")

            try:
                if not self._abrir_producto(indice_real):
                    print("❌ No se pudo abrir el producto, se salta")
                else:
                    datos_producto = self.extraer_datos_producto(numero_articulo)
                    if datos_producto:
                        productos_extraidos.append(datos_producto)
                    self._cerrar_producto()
            except Exception as e:
                print(f"❌ Error extrayendo producto {i + 1}: {e}")
                self._cerrar_producto()

            indice_real += 1

        print(f"\n{'='*60}")
        print(f"✅ EXTRACCIÓN COMPLETADA: {len(productos_extraidos)} productos")
        print(f"{'='*60}\n")
        return productos_extraidos

    # ------------------------------------------------------------------
    # Ficha del producto
    # ------------------------------------------------------------------
    JS_TEXTOS_DETALLE = """
    const raiz = document.querySelector("[data-testid='product-details']");
    if (!raiz) return null;
    function leer(el) {
        let s = '';
        const w = document.createTreeWalker(el, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT);
        let n;
        while ((n = w.nextNode())) {
            if (n.nodeType === 3) s += n.data;
            else if (n.tagName === 'IMG') s += (n.getAttribute('alt') || '');
            else if (n.tagName === 'BR') s += '\\n';
        }
        return s.trim();
    }
    return Array.from(raiz.querySelectorAll("span[data-testid='selectable-text']"))
        .filter(el => !(el.parentElement && el.parentElement.closest("span[data-testid='selectable-text']")))
        .map(leer)
        .filter(t => t);
    """

    @staticmethod
    def _separar_textos(textos):
        """
        De los textos de la ficha saca título, precio y descripción:
        título = primer texto que no es precio; precio = primer texto que empieza con $;
        descripción = el texto más largo de los restantes.
        """
        titulo, precio, resto = '', '', []
        for texto in textos:
            if not precio and texto.startswith('$') and len(texto) < 20:
                precio = texto
            elif not titulo:
                titulo = texto
            else:
                resto.append(texto)
        descripcion = max(resto, key=len) if resto else ''
        return titulo, precio, descripcion

    @staticmethod
    def _limpiar_precio(texto):
        """'$42.00' → '42'  |  '$1,250.50' → '1250.50' | sin precio válido → '0'"""
        if not texto:
            return '0'
        limpio = texto.replace('$', '').replace(',', '').strip().split()[0] if texto.strip() else ''
        try:
            numero = float(limpio)
            return str(int(numero)) if numero == int(numero) else f"{numero:.2f}"
        except ValueError:
            return '0'

    def expandir_leer_mas(self):
        """Pulsa 'Leer más' en la ficha para que aparezca la descripción completa"""
        pulsados = 0
        for _ in range(4):
            botones = [b for b in self.driver.find_elements(By.XPATH, self.XPATH_LEER_MAS) if b.is_displayed()]
            if not botones:
                break
            for boton in botones:
                try:
                    self.driver.execute_script("arguments[0].click();", boton)
                    pulsados += 1
                except Exception:
                    pass
            time.sleep(1)
        print(f"   📖 'Leer más' pulsado {pulsados} vez/veces")
        return pulsados > 0

    def _imagenes_producto(self):
        """Imágenes grandes (blob:) de la ficha, sin repetir"""
        validas, vistas = [], set()
        for xpath in (self.XPATH_IMAGENES_DETALLE, self.XPATH_IMAGENES_FUERA_LISTA):
            try:
                candidatas = self.driver.find_elements(By.XPATH, xpath)
            except Exception:
                candidatas = []
            for img in candidatas:
                try:
                    src = img.get_attribute('src') or ''
                    ancho = self.driver.execute_script(
                        "return arguments[0].naturalWidth || arguments[0].width;", img) or 0
                    if src in vistas or ancho < 100:
                        continue
                    vistas.add(src)
                    validas.append(img)
                except Exception:
                    continue
            if validas:
                break
        return validas

    def extraer_datos_producto(self, numero_articulo=None):
        """Extrae título, precio, descripción e imágenes de la ficha abierta"""
        try:
            producto = {'titulo': '', 'precio': '', 'descripcion': '', 'imagen_guardada': False}

            # Esperar a que carguen las imágenes de la ficha
            for _ in range(10):
                if self._imagenes_producto():
                    break
                time.sleep(1)

            print(f"\n{'─'*60}\n🔍 PASO 1: DESCRIPCIÓN COMPLETA\n{'─'*60}")
            self.expandir_leer_mas()

            print(f"\n{'─'*60}\n🔍 PASO 2: TÍTULO, PRECIO Y DESCRIPCIÓN\n{'─'*60}")
            textos = self.driver.execute_script(self.JS_TEXTOS_DETALLE) or []
            titulo, precio_texto, descripcion = self._separar_textos(textos)
            producto['titulo'] = titulo or "Sin título"
            producto['precio'] = self._limpiar_precio(precio_texto)
            producto['descripcion'] = descripcion or producto['titulo']
            print(f"   ✅ Título: {producto['titulo']}")
            print(f"   ✅ Precio: ${producto['precio']}  (leído: {precio_texto or 'no encontrado'})")
            print(f"   ✅ Descripción: {len(producto['descripcion'])} caracteres")

            print(f"\n{'─'*60}\n🔍 PASO 3: IMÁGENES\n{'─'*60}")
            if numero_articulo is not None:
                imagenes = self._imagenes_producto()
                print(f"   ✅ {len(imagenes)} imagen(es) detectada(s)")
                if imagenes:
                    carpeta_imagenes = os.path.join(self.carpeta_principal, f"Articulo_{numero_articulo}", "imagenes")
                    os.makedirs(carpeta_imagenes, exist_ok=True)
                    guardadas = 0
                    for numero, img in enumerate(imagenes[:10], 1):
                        if self.guardar_imagen_blob(img, carpeta_imagenes, numero):
                            guardadas += 1
                            print(f"      ✓ Imagen {numero} descargada")
                        else:
                            print(f"      ✗ No se pudo descargar la imagen {numero}")
                    producto['imagen_guardada'] = guardadas > 0

            if numero_articulo:
                print(f"\n{'─'*60}\n💾 GUARDANDO DATOS EN ARTICULO_{numero_articulo}\n{'─'*60}")
                guardar_datos_articulo(numero_articulo, {
                    'titulo': producto['titulo'],
                    'precio': producto['precio'],
                    'marca': '',
                    'categoria': 'Electrónica e informática',
                    'estado': 'Nuevo',
                    'ubicacion': self.config.get('ubicacion', 'Guayaquil'),
                    'descripcion': producto['descripcion'],
                    'disponibilidad': 'Publicar como disponible',
                    'encuentro_publico': 'Si',
                    'etiquetas': '',
                    'sku': '',
                })
                print(f"\n{'='*60}")
                print(f"✅ EXTRACCIÓN COMPLETA - ARTICULO_{numero_articulo}")
                print(f"   📄 Título: {producto['titulo']}")
                print(f"   💰 Precio: ${producto['precio']}")
                print(f"   📸 Imágenes: {'Sí' if producto['imagen_guardada'] else 'No'}")
                print(f"   📝 Descripción: {len(producto['descripcion'])} caracteres")
                print(f"{'='*60}\n")

            return producto

        except Exception as e:
            print(f"❌ Error general extrayendo datos: {e}")
            import traceback
            traceback.print_exc()
            return None

    def guardar_imagen_blob(self, elemento_img, carpeta_destino, numero_imagen):
        """Guarda una imagen desde blob URL"""
        try:
            ruta_destino = os.path.join(carpeta_destino, f"imagen_{numero_imagen}.jpg")
            
            script_base64 = """
            return new Promise((resolve, reject) => {
                const img = arguments[0];
                const canvas = document.createElement('canvas');
                canvas.width = img.naturalWidth || img.width;
                canvas.height = img.naturalHeight || img.height;
                const ctx = canvas.getContext('2d');
                
                img.onload = function() {
                    ctx.drawImage(img, 0, 0);
                    resolve(canvas.toDataURL('image/jpeg').split(',')[1]);
                };
                
                if (img.complete) {
                    ctx.drawImage(img, 0, 0);
                    resolve(canvas.toDataURL('image/jpeg').split(',')[1]);
                } else {
                    setTimeout(() => {
                        ctx.drawImage(img, 0, 0);
                        resolve(canvas.toDataURL('image/jpeg').split(',')[1]);
                    }, 500);
                }
            });
            """
            
            try:
                base64_data = self.driver.execute_async_script(script_base64, elemento_img)
                
                if base64_data:
                    import base64
                    with open(ruta_destino, 'wb') as f:
                        f.write(base64.b64decode(base64_data))
                    return True
            except:
                try:
                    screenshot = elemento_img.screenshot_as_png
                    if screenshot:
                        with open(ruta_destino, 'wb') as f:
                            f.write(screenshot)
                        return True
                except:
                    pass
            
            return False
        except Exception as e:
            print(f"         ⚠️  Error guardando imagen: {e}")
            return False

    def ejecutar(self, nombre_contacto, numeros_destino, indice_inicio_catalogo=0):
        """Ejecuta el proceso completo de extracción"""
        print("\n" + "="*60)
        print("🚀 EXTRACTOR DE WHATSAPP")
        print("="*60 + "\n")
        
        try:
            self.iniciar_navegador()
            
            if not self.esperar_whatsapp_cargado():
                return False
            
            if not self.buscar_contacto(nombre_contacto):
                return False
            
            if not self.abrir_catalogo():
                return False
            
            self.ir_a_todos_articulos()
            
            if self.contar_productos_catalogo() == 0:
                print("❌ No se encontraron productos en el catálogo")
                return False

            productos = self.extraer_productos(numeros_destino, indice_inicio_catalogo)
            
            print("\n" + "="*60)
            print(f"✅ EXTRACCIÓN COMPLETADA - {len(productos)} productos")
            print("="*60 + "\n")
            
            return productos
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            print("\n⏳ Cerrando navegador en 5 segundos...")
            time.sleep(5)
            if self.driver:
                try:
                    self.driver.quit()
                except Exception:
                    pass
                self.driver = None
