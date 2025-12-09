from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from PIL import Image
from io import BytesIO
import time
import os


class ExtractorWhatsApp:
    """Extrae productos del catálogo de WhatsApp Web"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.carpeta_principal = "ArticulosMarketplace"
    
    def iniciar_navegador(self):
        """Inicia Chrome y abre WhatsApp Web"""
        print("🌐 Iniciando Chrome...")
        
        opciones = webdriver.ChromeOptions()
        ruta_perfil = os.path.join(os.getcwd(), "perfiles", "whatsapp_extractor")
        opciones.add_argument(f"--user-data-dir={ruta_perfil}")
        opciones.add_argument("--disable-blink-features=AutomationControlled")
        opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
        opciones.add_experimental_option('useAutomationExtension', False)
        opciones.add_argument("--start-maximized")
        
        self.driver = webdriver.Chrome(options=opciones)
        self.driver.maximize_window()
        self.driver.set_script_timeout(15)
        self.wait = WebDriverWait(self.driver, 60)
        
        print("✅ Navegador iniciado")
        print("📱 Abriendo WhatsApp Web...")
        self.driver.get("https://web.whatsapp.com")
        time.sleep(3)
        
        print("\n⏳ Esperando a que escanees el código QR...")
        print("   (Si ya estás logueado, esto se saltará automáticamente)\n")
    
    def esperar_whatsapp_cargado(self):
        """Espera a que WhatsApp Web esté completamente cargado"""
        try:
            print("⏳ Esperando que WhatsApp Web cargue completamente...")
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='3']"))
            )
            print("✅ WhatsApp Web cargado correctamente")
            time.sleep(5)
            return True
        except Exception as e:
            print(f"❌ Error: WhatsApp Web no cargó correctamente: {e}")
            return False
    
    def buscar_contacto(self, nombre_contacto):
        """Busca un contacto en WhatsApp"""
        print(f"🔍 Buscando contacto: {nombre_contacto}")
        
        try:
            campo_busqueda = self.driver.find_element(By.XPATH, "//div[@contenteditable='true'][@data-tab='3']")
            campo_busqueda.click()
            time.sleep(1)
            
            campo_busqueda.clear()
            time.sleep(0.5)
            campo_busqueda.send_keys(nombre_contacto)
            time.sleep(5)
            
            try:
                contacto = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, f"//span[@title='{nombre_contacto}']"))
                )
                contacto.click()
                time.sleep(3)
                print(f"✅ Contacto '{nombre_contacto}' abierto")
                return True
            except:
                contacto_alt = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{nombre_contacto}')]"))
                )
                contacto_alt.click()
                time.sleep(3)
                print(f"✅ Contacto '{nombre_contacto}' abierto")
                return True
        except Exception as e:
            print(f"❌ Error buscando contacto: {e}")
            return False
    
    def abrir_info_contacto(self):
        """Abre la información del contacto"""
        print("📋 Abriendo información del contacto...")
        try:
            encabezado = self.driver.find_element(By.XPATH, "//header//div[@role='button']")
            encabezado.click()
            time.sleep(1.5)
            print("✅ Información del contacto abierta")
            return True
        except Exception as e:
            print(f"❌ Error abriendo info del contacto: {e}")
            return False
    
    def ir_a_catalogo(self):
        """Navega al catálogo de productos"""
        print("📦 Buscando catálogo de productos...")
        try:
            elemento_productos = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Productos')]")
            elemento_productos.click()
            time.sleep(3)
            print("✅ Catálogo abierto")
            return True
        except Exception as e:
            print(f"❌ Error abriendo catálogo: {e}")
            return False
    
    def ir_a_todos_articulos(self):
        """Navega a la sección 'Todos los artículos' del catálogo"""
        print("📦 Buscando sección 'Todos los artículos'...")
        try:
            todos_articulos = self.driver.find_element(By.XPATH, 
                "//span[contains(text(), 'Todos los artículos') or contains(text(), 'todos los artículos')]"
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", todos_articulos)
            time.sleep(1)
            todos_articulos.click()
            time.sleep(3)
            print("✅ Sección 'Todos los artículos' abierta")
            return True
        except Exception as e:
            print(f"⚠️  No se encontró 'Todos los artículos': {e}")
            print("   Continuando con el catálogo principal...")
            return False
    
    def hacer_scroll_catalogo(self, veces=3):
        """Hace scroll en el catálogo para cargar más productos"""
        print(f"📜 Haciendo scroll para cargar más productos...")
        try:
            contenedor = self.driver.find_element(By.XPATH, "//div[@role='list']")
            for i in range(veces):
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", contenedor)
                print(f"  → Scroll {i+1}/{veces}...")
                time.sleep(2)
            print("✅ Scroll completado")
            return True
        except Exception as e:
            print(f"⚠️  Error haciendo scroll: {e}")
            return False
    
    def contar_productos_catalogo(self):
        """Cuenta cuántos productos hay en el catálogo"""
        try:
            productos = self.driver.find_elements(By.XPATH, "//div[@role='listitem']")
            total = len(productos)
            print(f"📊 Total de productos encontrados: {total}")
            return total
        except:
            print("⚠️  No se pudieron contar los productos")
            return 0
    
    def extraer_productos(self, cantidad_maxima=5, articulo_inicio=1, indice_inicio_catalogo=0):
        """Extrae productos desde un índice específico del catálogo"""
        print(f"\n🎯 Iniciando extracción de hasta {cantidad_maxima} productos...")
        print(f"   Guardando en: Articulo_{articulo_inicio} hasta Articulo_{articulo_inicio + cantidad_maxima - 1}")
        print(f"   Desde producto {indice_inicio_catalogo + 1} del catálogo de WhatsApp\n")
        
        productos_extraidos = []
        indice_real = indice_inicio_catalogo
        
        for i in range(cantidad_maxima):
            numero_articulo = articulo_inicio + i
            
            print(f"\n{'='*60}")
            print(f"📦 PRODUCTO {i + 1}/{cantidad_maxima} → ARTICULO_{numero_articulo}")
            print(f"   (Producto {indice_real + 1} del catálogo de WhatsApp)")
            print(f"{'='*60}")
            
            try:
                time.sleep(2)
                
                items = self.driver.find_elements(By.XPATH, "//div[@role='listitem']")
                productos_reales = []
                
                for item in items:
                    try:
                        texto_item = item.text[:100] if item.text else "[sin texto]"
                        tiene_video = len(item.find_elements(By.TAG_NAME, 'video')) > 0
                        tiene_play = len(item.find_elements(By.XPATH, ".//*[contains(@data-icon, 'play')]")) > 0
                        es_categoria = 'Ver todo' in texto_item
                        
                        if not tiene_video and not tiene_play and not es_categoria:
                            productos_reales.append(item)
                    except:
                        pass
                
                if indice_real >= len(productos_reales):
                    print(f"[INFO] Solo hay {len(productos_reales)} productos en el catálogo")
                    print(f"       Has llegado al final. Considera rotar al inicio.")
                    break
                
                producto_item = productos_reales[indice_real]
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", producto_item)
                time.sleep(1.5)
                producto_item.click()
                time.sleep(6)
                
                videos = self.driver.find_elements(By.TAG_NAME, 'video')
                if len(videos) > 0:
                    self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                    time.sleep(2)
                    indice_real += 1
                    continue
                
                producto = self.extraer_datos_producto(numero_articulo=numero_articulo)
                
                if producto:
                    productos_extraidos.append(producto)
                
                indice_real += 1
                
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                time.sleep(5)
                
            except Exception as e:
                print(f"\n[ERROR] ❌ Excepción: {e}")
                try:
                    for _ in range(3):
                        self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                        time.sleep(1)
                except:
                    pass
                indice_real += 1
        
        print(f"\n{'='*60}")
        print(f"✅ EXTRACCIÓN COMPLETADA: {len(productos_extraidos)} productos")
        print(f"{'='*60}\n")
        return productos_extraidos
    
    def expandir_leer_mas_agresivo(self):
        """Expande descripción completa - SELECTORES CORREGIDOS"""
        print("📖 Expandiendo descripción completa...")
        
        max_intentos_globales = 5
        botones_clickeados = 0
        
        for intento_global in range(max_intentos_globales):
            try:
                # SELECTORES CORREGIDOS basados en el HTML real
                selectores = [
                    "//span[@class='x1ph7ams']",
                    "//span[contains(text(), 'Leer más')]",
                    "//span[@class='x1ph7ams' and contains(text(), 'Leer más')]",
                    "//div[contains(@class, 'x1f6kntn')]//span[contains(text(), 'Leer más')]"
                ]
                
                boton_encontrado = False
                
                for selector in selectores:
                    try:
                        botones = self.driver.find_elements(By.XPATH, selector)
                        print(f"  [Intento {intento_global + 1}] Selector: {selector[:50]}... → {len(botones)} botón(es)")
                        
                        for idx, boton in enumerate(botones):
                            try:
                                if boton.is_displayed():
                                    self.driver.execute_script(
                                        "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", 
                                        boton
                                    )
                                    time.sleep(0.5)
                                    
                                    try:
                                        boton.click()
                                        botones_clickeados += 1
                                        print(f"  ✅ Botón {idx + 1} expandido con clic normal")
                                        time.sleep(2)
                                        boton_encontrado = True
                                    except:
                                        try:
                                            self.driver.execute_script("arguments[0].click();", boton)
                                            botones_clickeados += 1
                                            print(f"  ✅ Botón {idx + 1} expandido con JavaScript")
                                            time.sleep(2)
                                            boton_encontrado = True
                                        except:
                                            pass
                            except:
                                continue
                        
                        if boton_encontrado:
                            break
                            
                    except:
                        continue
                
                if not boton_encontrado:
                    print(f"  ⚠️  No se encontraron más botones 'Leer más'")
                    break
                
                time.sleep(1)
                
            except Exception as e:
                print(f"  ⚠️  Error en intento {intento_global + 1}: {e}")
                break
        
        print(f"✅ Expansión completada: {botones_clickeados} botón(es) clickeado(s)")
        time.sleep(3)
        
        return botones_clickeados > 0
    
    def extraer_datos_producto(self, numero_articulo=None):
        """Extrae título, precio, descripción e imágenes del producto"""
        try:
            producto = {
                'titulo': '',
                'precio': '',
                'descripcion': '',
                'imagen_guardada': False
            }
            
            time.sleep(5)
            
            # Guardar imágenes
            if numero_articulo is not None:
                try:
                    selectores_imagen = [
                        "//img[@class='_ak9n' and @draggable='false']",
                        "//img[contains(@class, '_ak9n')]",
                        "//img[@draggable='false']"
                    ]
                    
                    imagenes_encontradas = []
                    for selector in selectores_imagen:
                        try:
                            elementos = self.driver.find_elements(By.XPATH, selector)
                            for elem in elementos:
                                if elem.is_displayed():
                                    src = elem.get_attribute('src')
                                    es_video = src and 'video' in src.lower()
                                    if not es_video and elem not in imagenes_encontradas:
                                        imagenes_encontradas.append(elem)
                            if imagenes_encontradas:
                                break
                        except:
                            continue
                    
                    if imagenes_encontradas:
                        carpeta_imagenes = os.path.join(self.carpeta_principal, f"Articulo_{numero_articulo}", "imagenes")
                        os.makedirs(carpeta_imagenes, exist_ok=True)
                        
                        imagenes_guardadas = 0
                        for idx, imagen_elem in enumerate(imagenes_encontradas[:10]):
                            ruta_imagen = os.path.join(carpeta_imagenes, f"imagen_{idx + 1}.jpg")
                            if self.descargar_imagen_blob(imagen_elem, ruta_imagen):
                                imagenes_guardadas += 1
                        
                        if imagenes_guardadas > 0:
                            producto['imagen_guardada'] = True
                except:
                    pass
            
            # Extraer título
            try:
                titulos_posibles = self.driver.find_elements(By.XPATH, 
                    "//div[contains(@class, 'x1okw0bk')]//span[contains(@class, 'selectable-text')]"
                )
                
                for titulo_elem in titulos_posibles[:15]:
                    try:
                        if not titulo_elem.is_displayed():
                            continue
                        
                        texto = titulo_elem.text.strip()
                        
                        if (texto and 
                            8 < len(texto) < 70 and 
                            '$' not in texto and 
                            '○' not in texto and 
                            'Marca:' not in texto and
                            'Trabajo' not in texto and
                            'Leer más' not in texto):
                            
                            producto['titulo'] = texto
                            break
                    except:
                        continue
                
                if not producto['titulo']:
                    producto['titulo'] = "Sin título"
            except:
                producto['titulo'] = "Sin título"
            
            # Extraer precio
            try:
                precios = self.driver.find_elements(By.XPATH, 
                    "//*[starts-with(text(), '$') and string-length(text()) < 15]"
                )
                
                for precio_elem in precios[:5]:
                    try:
                        if precio_elem.is_displayed():
                            precio_texto = precio_elem.text.strip()
                            precio_limpio = precio_texto.split()[0].replace('$', '').replace(',', '').strip()
                            
                            if precio_limpio and precio_limpio.replace('.', '').isdigit():
                                try:
                                    precio_float = float(precio_limpio)
                                    precio_entero = int(precio_float)
                                    producto['precio'] = str(precio_entero)
                                except:
                                    producto['precio'] = precio_limpio
                                break
                    except:
                        continue
                
                if not producto['precio']:
                    producto['precio'] = "0"
            except:
                producto['precio'] = "0"
            
            # Expandir descripción - CON SELECTORES CORREGIDOS
            self.expandir_leer_mas_agresivo()
            
            # Extraer descripción completa - MÉTODO MEJORADO
            try:
                detalles = []
                detalles_vistos = set()  # Para evitar duplicados
                
                # Buscar TODOS los elementos que contengan "○"
                elementos_bullets = self.driver.find_elements(By.XPATH, "//*[contains(text(), '○')]")
                
                print(f"📋 Encontrados {len(elementos_bullets)} elementos con ○")
                
                # Procesar CADA elemento por separado
                for elem in elementos_bullets[:50]:
                    try:
                        if not elem.is_displayed():
                            continue
                        
                        # Obtener TODO el texto del elemento
                        texto_completo = elem.text.strip()
                        
                        # Dividir por "○" y procesar cada parte
                        partes = texto_completo.split('○')
                        
                        for parte in partes:
                            linea = parte.strip()
                            
                            # Validar la línea
                            if (linea and 
                                len(linea) > 3 and 
                                len(linea) < 300 and
                                linea not in detalles_vistos and
                                linea != producto['titulo'] and 
                                '$' not in linea and
                                'Leer más' not in linea and
                                'Ver más' not in linea and
                                'Enviar mensaje' not in linea):
                                
                                detalles.append(linea)
                                detalles_vistos.add(linea)
                                
                    except:
                        continue
                
                if detalles:
                    producto['descripcion'] = ' | '.join(detalles)
                    print(f"✅ Descripción capturada: {len(detalles)} detalles")
                else:
                    producto['descripcion'] = producto['titulo']
                    print("⚠️  No se encontraron detalles, usando título")
            except:
                producto['descripcion'] = producto['titulo']
            
            # Guardar datos.txt
            if numero_articulo:
                carpeta_articulo = os.path.join(self.carpeta_principal, f"Articulo_{numero_articulo}")
                archivo_datos = os.path.join(carpeta_articulo, "datos.txt")
                os.makedirs(carpeta_articulo, exist_ok=True)
                
                plantilla = f"""titulo={producto['titulo']}
precio={producto['precio']}
categoria=Electrónica e informática
estado=Nuevo
ubicacion=Guayaquil
descripcion={producto['descripcion']}
disponibilidad=Publicar como disponible
encuentro_publico=Si
etiquetas=
sku="""
                
                with open(archivo_datos, 'w', encoding='utf-8') as f:
                    f.write(plantilla)
                
                print(f"[GUARDADO] ✅ Articulo_{numero_articulo} guardado correctamente")
            
            return producto
            
        except Exception as e:
            print(f"❌ Error extrayendo datos: {e}")
            return None
    
    def descargar_imagen_blob(self, elemento_imagen, ruta_destino):
        """Descarga imagen desde blob URL usando JavaScript"""
        try:
            src = elemento_imagen.get_attribute('src')
            
            if src.startswith('http'):
                import requests
                response = requests.get(src, timeout=10)
                with open(ruta_destino, 'wb') as f:
                    f.write(response.content)
                return True
            
            elif src.startswith('blob:'):
                try:
                    base64_data = self.driver.execute_async_script("""
                        const src = arguments[0];
                        const callback = arguments[1];
                        
                        fetch(src)
                            .then(r => r.blob())
                            .then(blob => {
                                const reader = new FileReader();
                                reader.onload = () => callback(reader.result.split(',')[1]);
                                reader.readAsDataURL(blob);
                            })
                            .catch(err => callback(null));
                        
                        setTimeout(() => callback(null), 10000);
                    """, src)
                    
                    if base64_data:
                        import base64
                        with open(ruta_destino, 'wb') as f:
                            f.write(base64.b64decode(base64_data))
                        return True
                except:
                    pass
            
            return False
        except:
            return False
    
    def ejecutar(self, nombre_contacto, cantidad_productos=5, articulo_inicio=1, indice_inicio_catalogo=0):
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
            
            if not self.abrir_info_contacto():
                return False
            
            if not self.ir_a_catalogo():
                return False
            
            self.ir_a_todos_articulos()
            self.hacer_scroll_catalogo(veces=5)
            self.contar_productos_catalogo()
            
            productos = self.extraer_productos(cantidad_productos, articulo_inicio, indice_inicio_catalogo)
            
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
                self.driver.quit()
