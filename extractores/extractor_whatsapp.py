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
            campo_busqueda = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='3']"))
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
            
            resultado = self.driver.find_element(By.XPATH, f"//span[@title='{nombre_contacto}']")
            resultado.click()
            time.sleep(2)
            
            print(f"✅ Contacto '{nombre_contacto}' abierto")
            return True
            
        except Exception as e:
            print(f"❌ Error buscando contacto: {e}")
            return False
    
    def abrir_catalogo_directo(self):
        """Abre el catálogo haciendo clic directo en el ícono del header"""
        print("🛒 Abriendo catálogo directo desde header...")
        try:
            time.sleep(2)
            
            icono_catalogo = self.driver.find_element(
                By.XPATH, 
                "//span[@data-icon='storefront' or @data-icon='storefront-refreshed']"
            )
            print("   ✅ Ícono 'storefront' encontrado")
            
            boton_catalogo = icono_catalogo
            for _ in range(5):
                boton_catalogo = boton_catalogo.find_element(By.XPATH, "..")
                try:
                    if boton_catalogo.get_attribute('role') in ['button', 'link']:
                        print("   ✅ Botón clickeable encontrado")
                        break
                except:
                    continue
            
            if not boton_catalogo:
                print("   ❌ No se encontró ancestro clickeable")
                return False
            
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_catalogo)
            time.sleep(1)
            
            try:
                boton_catalogo.click()
                print("   ✅ Clic en botón de catálogo exitoso")
            except:
                self.driver.execute_script("arguments[0].click();", boton_catalogo)
                print("   ✅ Clic JavaScript en botón de catálogo exitoso")
            
            time.sleep(3)
            print("✅ Catálogo abierto correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error abriendo catálogo directo: {e}")
            return False
    
    def ir_a_todos_articulos(self):
        """Navega a 'Todos los artículos' haciendo clic en 'Ver todo' - VERSIÓN ORIGINAL"""
        print("📦 Buscando 'Todos los artículos'...")
        
        try:
            # Scroll hacia arriba para ver el inicio del catálogo
            for _ in range(5):
                self.driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(0.2)
            
            # Buscar "Todos los artículos" con scroll
            encontrado = False
            for i in range(10):
                self.driver.execute_script("window.scrollBy(0, 250);")
                time.sleep(0.5)
                
                try:
                    elementos = self.driver.find_elements(By.XPATH, "//span[text()='Todos los artículos']")
                    if elementos and elementos[0].is_displayed():
                        print(f"   ✅ 'Todos los artículos' encontrado después de {i + 1} scroll(s)")
                        encontrado = True
                        break
                except:
                    pass
            
            if not encontrado:
                print("   ⚠️  'Todos los artículos' no encontrado, continuando de todos modos...")
                return True
            
            time.sleep(2)
            
            # Buscar botón "Ver todo" de "Todos los artículos"
            print("🔍 Buscando botón 'Ver todo'...")
            
            boton_ver_todo = self.driver.find_element(By.XPATH, 
                "//a[@role='button' and contains(@title, 'Todos los artículos')]"
            )
            print("   ✅ Botón 'Ver todo' encontrado")
            
            # Scroll al botón y hacer clic
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_ver_todo)
            time.sleep(2)
            
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(self.driver)
            actions.move_to_element(boton_ver_todo).pause(0.3).click().perform()
            print("   ✅ Clic en 'Ver todo' ejecutado")
            
            time.sleep(4)
            
            # Verificar que se abrió correctamente
            try:
                boton_atras = self.driver.find_elements(By.XPATH, "//button[@aria-label='Atrás']")
                if boton_atras and boton_atras[0].is_displayed():
                    print("✅ 'Todos los artículos' abierto correctamente")
                    return True
            except:
                pass
            
            print("✅ Proceso completado")
            return True
            
        except Exception as e:
            print(f"⚠️  Error en ir_a_todos_articulos: {e}")
            print("   Continuando de todos modos...")
            return True
    
    def contar_productos_catalogo(self):
        """Cuenta cuántos productos REALES hay en el catálogo - CON LAZY LOADING"""
        try:
            # PASO 1: Hacer scroll para cargar TODOS los productos (lazy loading)
            print(f"📜 Cargando todos los productos del catálogo...")
            
            productos_anteriores = 0
            scroll_count = 0
            max_scrolls = 30
            
            while scroll_count < max_scrolls:
                # Obtener productos actuales
                items = self.driver.find_elements(By.XPATH, "//div[@role='listitem']")
                items_count = len(items)
                
                if scroll_count == 0:
                    print(f"   Productos inicialmente visibles: {items_count}")
                
                # Si no aumentó = fin del catálogo
                if items_count == productos_anteriores and scroll_count > 0:
                    print(f"   ✅ Catálogo completo cargado: {items_count} items\n")
                    break
                
                # Scroll al ÚLTIMO producto para activar lazy loading
                if items:
                    try:
                        ultimo = items[-1]
                        self.driver.execute_script(
                            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});",
                            ultimo
                        )
                        time.sleep(1.5)
                    except:
                        break
                
                productos_anteriores = items_count
                scroll_count += 1
            
            # PASO 2: Esperar carga final
            time.sleep(2)
            
            # PASO 3: Contar y filtrar productos
            selectores_productos = [
                "//div[@role='listitem']",
                "//div[contains(@class, '_ak72')]",
                "//div[@tabindex='0' and @role='button']//div[contains(@class, '_ak72')]",
            ]
            
            items = []
            selector_usado = None
            for selector in selectores_productos:
                try:
                    elementos = self.driver.find_elements(By.XPATH, selector)
                    if len(elementos) > 0:
                        items = elementos
                        selector_usado = selector
                        break
                except:
                    continue
            
            if not items:
                print(f"⚠️  No se encontraron items con ningún selector")
                return 0
            
            productos_reales = []
            videos_detectados = 0
            categorias_detectadas = 0
            
            for item in items:
                try:
                    tiene_video = len(item.find_elements(By.TAG_NAME, 'video')) > 0
                    tiene_play = len(item.find_elements(By.XPATH, ".//*[contains(@data-icon, 'play')]")) > 0
                    
                    if tiene_video or tiene_play:
                        videos_detectados += 1
                        continue
                    
                    texto_item = item.text[:100] if item.text else ""
                    es_categoria = 'Ver todo' in texto_item or 'ver todo' in texto_item
                    
                    if es_categoria:
                        categorias_detectadas += 1
                        continue
                    
                    productos_reales.append(item)
                    
                except:
                    pass
            
            total_real = len(productos_reales)
            total_items = len(items)
            
            print(f"📊 Análisis del catálogo:")
            print(f"   Selector usado: {selector_usado[:60]}...")
            print(f"   Total de items: {total_items}")
            print(f"   Productos reales: {total_real}")
            print(f"   Videos filtrados: {videos_detectados}")
            print(f"   Categorías filtradas: {categorias_detectadas}")
            
            return total_real
        except Exception as e:
            print(f"⚠️  Error contando productos: {e}")
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
                
                selectores_productos = [
                    "//div[@role='listitem']",
                    "//div[contains(@class, '_ak72')]",
                    "//div[@tabindex='0' and @role='button']//div[contains(@class, '_ak72')]",
                ]
                
                items = []
                for selector in selectores_productos:
                    try:
                        elementos = self.driver.find_elements(By.XPATH, selector)
                        if len(elementos) > 0:
                            items = elementos
                            print(f"[DEBUG] Selector funcionó: {selector[:60]}... → {len(items)} items")
                            break
                    except:
                        continue
                
                if not items:
                    print(f"[ERROR] No se encontraron productos con ningún selector")
                    break
                
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
                
                print(f"[DEBUG] Productos reales encontrados: {len(productos_reales)}")
                
                if indice_real >= len(productos_reales):
                    print(f"[INFO] Solo hay {len(productos_reales)} productos en el catálogo")
                    print(f"       Llegaste al final del catálogo.")
                    break
                
                producto_actual = productos_reales[indice_real]
                
                print(f"⏳ Esperando que se cargue SOLO el producto actual...")
                time.sleep(3)
                
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                    producto_actual
                )
                time.sleep(1)
                
                try:
                    producto_actual.click()
                except:
                    self.driver.execute_script("arguments[0].click();", producto_actual)
                
                time.sleep(3)
                
                datos_producto = self.extraer_datos_producto(numero_articulo)
                
                if datos_producto:
                    productos_extraidos.append(datos_producto)
                
                try:
                    boton_cerrar = self.driver.find_element(
                        By.XPATH,
                        "//span[@data-icon='x-viewer' or @data-icon='back' or @data-icon='back-refreshed']/ancestor::div[@role='button'][1]"
                    )
                    boton_cerrar.click()
                    time.sleep(1)
                except:
                    try:
                        self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                        time.sleep(1)
                    except:
                        pass
                
                indice_real += 1
                
            except Exception as e:
                print(f"❌ Error extrayendo producto {i + 1}: {e}")
                try:
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
        """Expande descripción completa"""
        print("📖 Expandiendo descripción completa...")
        
        max_intentos_globales = 5
        botones_clickeados = 0
        
        for intento_global in range(max_intentos_globales):
            try:
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
        """Extrae título, precio, descripción e imágenes"""
        try:
            producto = {
                'titulo': '',
                'precio': '',
                'descripcion': '',
                'imagen_guardada': False
            }
            
            time.sleep(5)
            
            print(f"\n{'─'*60}")
            print(f"🔍 PASO 1: EXTRAYENDO IMÁGENES")
            print(f"{'─'*60}")
            
            if numero_articulo is not None:
                try:
                    selectores_imagen = [
                        "//img[@class='_ak9n' and @draggable='false']",
                        "//img[contains(@class, '_ak9n')]",
                        "//img[@draggable='false']"
                    ]
                    
                    imagenes_encontradas = []
                    
                    print("   🔎 Buscando elementos de imagen...")
                    for idx, selector in enumerate(selectores_imagen, 1):
                        try:
                            imgs = self.driver.find_elements(By.XPATH, selector)
                            if imgs:
                                print(f"   Selector {idx}/{len(selectores_imagen)}: {len(imgs)} elemento(s) encontrado(s)")
                                imagenes_encontradas.extend(imgs)
                                break
                        except:
                            continue
                    
                    imagenes_validas = []
                    for img in imagenes_encontradas[:10]:
                        try:
                            if img.is_displayed():
                                src = img.get_attribute('src')
                                if src and 'blob:' in src:
                                    imagenes_validas.append(img)
                        except:
                            continue
                    
                    print(f"   ✅ {len(imagenes_validas)} imagen(es) válida(s) detectada(s)")
                    
                    if imagenes_validas:
                        carpeta_articulo = os.path.join(self.carpeta_principal, f"Articulo_{numero_articulo}")
                        carpeta_imagenes = os.path.join(carpeta_articulo, "imagenes")
                        os.makedirs(carpeta_imagenes, exist_ok=True)
                        
                        print("   📥 Descargando imágenes...")
                        imagenes_guardadas = 0
                        
                        for idx, img in enumerate(imagenes_validas[:10], 1):
                            try:
                                if self.guardar_imagen_blob(img, carpeta_imagenes, idx):
                                    print(f"      ✓ Imagen {idx}/{len(imagenes_validas[:10])} descargada")
                                    imagenes_guardadas += 1
                            except Exception as e:
                                print(f"      ✗ Error descargando imagen {idx}: {e}")
                        
                        if imagenes_guardadas > 0:
                            producto['imagen_guardada'] = True
                            print(f"   ✅ {imagenes_guardadas} imagen(es) guardada(s) exitosamente")
                        
                except Exception as e:
                    print(f"   ⚠️  Error guardando imágenes: {e}")
            
            print(f"\n{'─'*60}")
            print(f"🔍 PASO 2: EXTRAYENDO TÍTULO")
            print(f"{'─'*60}")
            
            try:
                selectores_titulo = [
                    "//span[@data-testid='selectable-text' and contains(@class, '_ao3e') and @dir='auto' and not(contains(@class, 'x1fj9vlw'))]",
                    "//span[contains(@class, '_ao3e') and contains(@class, '_aupe') and not(contains(@class, 'x1fj9vlw')) and @dir='auto']",
                    "//span[contains(@class, 'copyable-text') and @dir='auto' and not(contains(@class, 'x1fj9vlw'))]"
                ]
                
                titulo_encontrado = None
                for selector in selectores_titulo:
                    try:
                        elementos = self.driver.find_elements(By.XPATH, selector)
                        print(f"   🔎 Buscando título: {len(elementos)} elemento(s) encontrado(s)")
                        
                        for elemento in elementos[:5]:
                            if not elemento.is_displayed():
                                continue
                            
                            texto = elemento.text.strip()
                            
                            if (texto and 
                                len(texto) > 5 and 
                                len(texto) < 200 and
                                not texto.startswith('$') and
                                '$' not in texto[:10] and
                                'Leer más' not in texto and
                                'Enviar mensaje' not in texto):
                                
                                titulo_encontrado = texto
                                print(f"   ✅ Título encontrado: '{titulo_encontrado}'")
                                break
                        
                        if titulo_encontrado:
                            break
                    except:
                        continue
                
                if titulo_encontrado:
                    producto['titulo'] = titulo_encontrado
                else:
                    producto['titulo'] = "Sin título"
                    print(f"   ⚠️  No se encontró título válido")
                    
            except Exception as e:
                producto['titulo'] = "Sin título"
                print(f"   ❌ Error extrayendo título: {e}")
            
            print(f"\n{'─'*60}")
            print(f"🔍 PASO 3: EXTRAYENDO PRECIO")
            print(f"{'─'*60}")
            
            try:
                precios = self.driver.find_elements(By.XPATH, 
                    "//*[starts-with(text(), '$') and string-length(text()) < 15]"
                )
                
                print(f"   🔎 Buscando precio entre {len(precios)} elementos...")
                precios_procesados = []
                
                for idx, precio_elem in enumerate(precios[:10]):
                    try:
                        if not precio_elem.is_displayed():
                            continue
                        
                        estilo = precio_elem.value_of_css_property('text-decoration')
                        esta_tachado = 'line-through' in estilo if estilo else False
                        
                        precio_texto = precio_elem.text.strip()
                        
                        if esta_tachado:
                            print(f"      • {precio_texto} (tachado - ignorado)")
                            continue
                        
                        precio_limpio = precio_texto.split()[0].replace('$', '').replace(',', '').strip()
                        
                        if precio_limpio and precio_limpio.replace('.', '').isdigit():
                            try:
                                precio_float = float(precio_limpio)
                                precio_entero = int(precio_float)
                                producto['precio'] = str(precio_entero)
                                print(f"   ✅ Precio encontrado: ${precio_entero}")
                                print(f"      (Original: {precio_texto}, Procesado: ${precio_entero})")
                                break
                            except:
                                producto['precio'] = precio_limpio
                                print(f"   ✅ Precio encontrado: ${precio_limpio}")
                                break
                    except:
                        continue
                
                if not producto['precio']:
                    producto['precio'] = "0"
                    print(f"   ⚠️  No se encontró precio válido, usando: $0")
            except Exception as e:
                producto['precio'] = "0"
                print(f"   ❌ Error extrayendo precio: {e}")
            
            self.expandir_leer_mas_agresivo()
            
            print(f"\n{'─'*60}")
            print(f"🔍 PASO 4: EXTRAYENDO DESCRIPCIÓN")
            print(f"{'─'*60}")
            
            try:
                selectores_descripcion = [
                    "//span[@data-testid='selectable-text' and contains(@class, 'x1fj9vlw') and @dir='auto']",
                    "//span[contains(@class, 'x1fj9vlw') and contains(@class, '_ao3e')]",
                    "//span[contains(@class, 'x1fj9vlw') and contains(@class, 'copyable-text')]"
                ]
                
                descripcion_encontrada = None
                for selector in selectores_descripcion:
                    try:
                        elemento = self.driver.find_element(By.XPATH, selector)
                        
                        if elemento.is_displayed():
                            texto = elemento.text.strip()
                            
                            if texto and len(texto) > 20:
                                descripcion_encontrada = texto
                                print(f"   ✅ Descripción encontrada: {len(texto)} caracteres")
                                print(f"      Preview: {texto[:100]}...")
                                break
                    except:
                        continue
                
                if descripcion_encontrada:
                    producto['descripcion'] = descripcion_encontrada
                else:
                    producto['descripcion'] = producto['titulo']
                    print(f"   ⚠️  No se encontró descripción, usando título")
                    
            except Exception as e:
                print(f"   ❌ Error extrayendo descripción: {e}")
                producto['descripcion'] = producto['titulo']
            
            print(f"\n{'─'*60}")
            print(f"🔧 POST-PROCESAMIENTO")
            print(f"{'─'*60}")
            
            if producto['titulo'] == "Sin título" and producto['descripcion']:
                fragmentos_desc = producto['descripcion'].split(' | ')
                
                fragmentos_titulo = []
                for fragmento in fragmentos_desc[:5]:
                    fragmento = fragmento.strip()
                    if ':' in fragmento:
                        break
                    fragmentos_titulo.append(fragmento)
                
                if fragmentos_titulo:
                    titulo_extraido = ' | '.join(fragmentos_titulo)
                    if titulo_extraido and len(titulo_extraido) > 5:
                        producto['titulo'] = titulo_extraido
                        print(f"   ✅ Título extraído de descripción: '{titulo_extraido}'")
            
            if numero_articulo:
                print(f"\n{'─'*60}")
                print(f"💾 GUARDANDO DATOS EN ARTICULO_{numero_articulo}")
                print(f"{'─'*60}")
                
                carpeta_articulo = os.path.join(self.carpeta_principal, f"Articulo_{numero_articulo}")
                archivo_datos = os.path.join(carpeta_articulo, "datos.txt")
                os.makedirs(carpeta_articulo, exist_ok=True)
                
                # Escapar comillas en la descripción
                descripcion_escapada = producto['descripcion'].replace('"', '\\"')
                
                plantilla = f"""titulo={producto['titulo']}
precio={producto['precio']}
marca=
categoria=Electrónica e informática
estado=Nuevo
ubicacion=Guayaquil
descripcion="{descripcion_escapada}"
disponibilidad=Publicar como disponible
encuentro_publico=Si
etiquetas=
sku="""
                
                with open(archivo_datos, 'w', encoding='utf-8') as f:
                    f.write(plantilla)
                
                print(f"   ✅ Archivo datos.txt guardado")
                
                print(f"\n{'='*60}")
                print(f"✅ EXTRACCIÓN COMPLETA - ARTICULO_{numero_articulo}")
                print(f"{'='*60}")
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
            
            if not self.abrir_catalogo_directo():
                return False
            
            self.ir_a_todos_articulos()
            
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
