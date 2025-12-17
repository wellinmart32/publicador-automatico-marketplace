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
    
    def abrir_catalogo_directo(self):
        """Abre el catálogo usando el botón directo del header (ruta correcta)"""
        print("🛒 Abriendo catálogo directo desde header...")
        
        try:
            # Estrategia 1: Buscar el ícono storefront y su ancestro clickeable
            icono = self.driver.find_element(By.XPATH, "//span[@data-icon='storefront']")
            print("   ✅ Ícono 'storefront' encontrado")
            
            # Encontrar ancestro clickeable
            ancestros = [
                "./ancestor::div[@role='button'][1]",
                "./ancestor::button[1]",
                "./ancestor::a[1]",
                "./parent::*/parent::*[@role='button']",
            ]
            
            boton_catalogo = None
            for xpath_ancestro in ancestros:
                try:
                    boton = icono.find_element(By.XPATH, xpath_ancestro)
                    if boton.is_displayed():
                        boton_catalogo = boton
                        print(f"   ✅ Botón clickeable encontrado")
                        break
                except:
                    continue
            
            if not boton_catalogo:
                print("   ❌ No se encontró ancestro clickeable")
                return False
            
            # Hacer clic en el botón
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
    
    def abrir_info_contacto(self):
        """DEPRECATED - Ya no se usa, usar abrir_catalogo_directo()"""
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
        """Navega a 'Todos los artículos' haciendo clic en 'Ver todo'"""
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
                return True  # No es crítico, continuar
            
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
        """Cuenta cuántos productos REALES hay en el catálogo (sin videos ni categorías)"""
        try:
            time.sleep(2)
            
            # SELECTORES MÚLTIPLES (igual que en extraer_productos)
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
                    # Detectar videos
                    tiene_video = len(item.find_elements(By.TAG_NAME, 'video')) > 0
                    tiene_play = len(item.find_elements(By.XPATH, ".//*[contains(@data-icon, 'play')]")) > 0
                    
                    if tiene_video or tiene_play:
                        videos_detectados += 1
                        continue
                    
                    # Detectar categorías/secciones (tienen "Ver todo")
                    texto_item = item.text[:100] if item.text else ""
                    es_categoria = 'Ver todo' in texto_item or 'ver todo' in texto_item
                    
                    if es_categoria:
                        categorias_detectadas += 1
                        continue
                    
                    # Es un producto real
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
                
                # SELECTORES MÚLTIPLES para productos (funcionan en diferentes interfaces)
                selectores_productos = [
                    "//div[@role='listitem']",  # Vista principal del catálogo
                    "//div[contains(@class, '_ak72')]",  # Vista "Ver todo" (más específico)
                    "//div[@tabindex='0' and @role='button']//div[contains(@class, '_ak72')]",  # Productos clickeables
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
                    
                    # ROTACIÓN AUTOMÁTICA: Volver al inicio
                    if len(productos_extraidos) == 0 and i == 0:
                        print(f"\n🔄 ROTACIÓN AUTOMÁTICA: Volviendo al inicio del catálogo...")
                        indice_real = 0
                        print(f"   Empezando desde el producto 1\n")
                        
                        # Verificar nuevamente si hay productos
                        if len(productos_reales) == 0:
                            print(f"[ERROR] No hay productos disponibles después de rotar")
                            break
                    else:
                        print(f"       Productos extraídos hasta ahora: {len(productos_extraidos)}")
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
        """Extrae título, precio, descripción e imágenes - VERSIÓN MEJORADA"""
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
            
            # Guardar imágenes
            if numero_articulo is not None:
                try:
                    selectores_imagen = [
                        "//img[@class='_ak9n' and @draggable='false']",
                        "//img[contains(@class, '_ak9n')]",
                        "//img[@draggable='false']"
                    ]
                    
                    imagenes_encontradas = []
                    print(f"   🔎 Buscando elementos de imagen...")
                    
                    for idx_selector, selector in enumerate(selectores_imagen):
                        try:
                            elementos = self.driver.find_elements(By.XPATH, selector)
                            print(f"   Selector {idx_selector + 1}/3: {len(elementos)} elemento(s) encontrado(s)")
                            
                            for elem in elementos:
                                if elem.is_displayed():
                                    src = elem.get_attribute('src')
                                    es_video = src and 'video' in src.lower()
                                    if not es_video and elem not in imagenes_encontradas:
                                        imagenes_encontradas.append(elem)
                            if imagenes_encontradas:
                                print(f"   ✅ {len(imagenes_encontradas)} imagen(es) válida(s) detectada(s)")
                                break
                        except:
                            continue
                    
                    if imagenes_encontradas:
                        carpeta_imagenes = os.path.join(self.carpeta_principal, f"Articulo_{numero_articulo}", "imagenes")
                        os.makedirs(carpeta_imagenes, exist_ok=True)
                        
                        print(f"   📥 Descargando imágenes...")
                        imagenes_guardadas = 0
                        for idx, imagen_elem in enumerate(imagenes_encontradas[:10]):
                            ruta_imagen = os.path.join(carpeta_imagenes, f"imagen_{idx + 1}.jpg")
                            if self.descargar_imagen_blob(imagen_elem, ruta_imagen):
                                imagenes_guardadas += 1
                                print(f"      ✓ Imagen {idx + 1}/10 descargada")
                        
                        if imagenes_guardadas > 0:
                            producto['imagen_guardada'] = True
                            print(f"   ✅ {imagenes_guardadas} imagen(es) guardada(s) exitosamente")
                    else:
                        print(f"   ⚠️  No se encontraron imágenes")
                except Exception as e:
                    print(f"   ❌ Error descargando imágenes: {e}")
            
            print(f"\n{'─'*60}")
            print(f"🔍 PASO 2: EXTRAYENDO TÍTULO")
            print(f"{'─'*60}")
            
            # Extraer título
            try:
                titulos_posibles = self.driver.find_elements(By.XPATH, 
                    "//div[contains(@class, 'x1okw0bk')]//span[contains(@class, 'selectable-text')]"
                )
                
                print(f"   🔎 Buscando título entre {len(titulos_posibles)} elementos...")
                candidatos_rechazados = []
                
                for idx, titulo_elem in enumerate(titulos_posibles[:15]):
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
                            print(f"   ✅ Título encontrado: '{texto}'")
                            print(f"      (Candidato {idx + 1}, longitud: {len(texto)} caracteres)")
                            break
                        else:
                            razon = []
                            if len(texto) <= 8: razon.append("muy corto")
                            if len(texto) >= 70: razon.append("muy largo")
                            if '$' in texto: razon.append("contiene precio")
                            if '○' in texto: razon.append("es descripción")
                            if 'Marca:' in texto: razon.append("es marca")
                            if texto:
                                candidatos_rechazados.append(f"'{texto[:40]}...' ({', '.join(razon)})")
                    except:
                        continue
                
                if not producto['titulo']:
                    producto['titulo'] = "Sin título"
                    print(f"   ⚠️  No se encontró título válido")
                    if candidatos_rechazados:
                        print(f"   📋 Candidatos rechazados:")
                        for candidato in candidatos_rechazados[:3]:
                            print(f"      • {candidato}")
            except Exception as e:
                producto['titulo'] = "Sin título"
                print(f"   ❌ Error extrayendo título: {e}")
            
            print(f"\n{'─'*60}")
            print(f"🔍 PASO 3: EXTRAYENDO PRECIO")
            print(f"{'─'*60}")
            
            # Extraer precio
            try:
                # Buscar precios en elementos que NO estén tachados (text-decoration: line-through)
                precios = self.driver.find_elements(By.XPATH, 
                    "//*[starts-with(text(), '$') and string-length(text()) < 15]"
                )
                
                print(f"   🔎 Buscando precio entre {len(precios)} elementos...")
                precios_procesados = []
                
                for idx, precio_elem in enumerate(precios[:10]):  # Aumentar a 10 para tener más opciones
                    try:
                        if not precio_elem.is_displayed():
                            continue
                        
                        # Verificar si el precio está tachado
                        estilo = precio_elem.value_of_css_property('text-decoration')
                        esta_tachado = 'line-through' in estilo if estilo else False
                        
                        precio_texto = precio_elem.text.strip()
                        
                        if esta_tachado:
                            print(f"      • {precio_texto} (tachado - ignorado)")
                            continue  # Saltar precios tachados (precios antiguos)
                        
                        precio_limpio = precio_texto.split()[0].replace('$', '').replace(',', '').strip()
                        
                        if precio_limpio and precio_limpio.replace('.', '').isdigit():
                            try:
                                precio_float = float(precio_limpio)
                                precio_entero = int(precio_float)
                                producto['precio'] = str(precio_entero)
                                print(f"   ✅ Precio encontrado: ${precio_entero}")
                                print(f"      (Original: {precio_texto}, Procesado: ${precio_entero})")
                                break  # Tomar el primer precio NO tachado
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
            
            # Expandir descripción
            self.expandir_leer_mas_agresivo()
            
            print(f"\n{'─'*60}")
            print(f"🔍 PASO 4: EXTRAYENDO DESCRIPCIÓN")
            print(f"{'─'*60}")
            
            # ═══════════════════════════════════════════════════════════
            # EXTRACCIÓN DE DESCRIPCIÓN MEJORADA - CAPTURA TODO EL TEXTO
            # ═══════════════════════════════════════════════════════════
            try:
                descripcion_completa = []
                textos_vistos = set()
                
                print(f"   🔎 Estrategia 1: Buscando contenedores principales...")
                
                print(f"📋 Extrayendo descripción completa...")
                
                # ESTRATEGIA 1: Buscar contenedor principal de descripción
                selectores_contenedor = [
                    "//div[contains(@class, 'x1okw0bk')]",  # Contenedor principal
                    "//div[@role='dialog']//div[contains(@class, 'x78zum5')]",  # Dialog content
                    "//div[contains(@class, 'x1n2onr6')]"  # Alternative container
                ]
                
                for selector_contenedor in selectores_contenedor:
                    try:
                        contenedores = self.driver.find_elements(By.XPATH, selector_contenedor)
                        
                        for contenedor in contenedores[:5]:  # Limitar a primeros 5 contenedores
                            if not contenedor.is_displayed():
                                continue
                            
                            # Extraer TODO el texto del contenedor
                            texto_contenedor = contenedor.text.strip()
                            
                            if not texto_contenedor or len(texto_contenedor) < 10:
                                continue
                            
                            # Dividir por líneas
                            lineas = texto_contenedor.split('\n')
                            
                            for linea in lineas:
                                linea = linea.strip()
                                
                                # Filtrar líneas no deseadas
                                if (linea and 
                                    len(linea) > 5 and 
                                    len(linea) < 500 and
                                    linea not in textos_vistos and
                                    linea != producto['titulo'] and 
                                    linea != producto['precio'] and
                                    not linea.startswith('$') and  # Excluir cualquier precio
                                    '$' not in linea[:5] and  # Evitar líneas que empiezan con precio
                                    'Leer más' not in linea and
                                    'Ver más' not in linea and
                                    'Enviar mensaje' not in linea and
                                    'Trabajo' not in linea and
                                    'WhatsApp' not in linea and  # Excluir mensajes del sistema
                                    'mensajes anteriores' not in linea and  # Excluir avisos de WhatsApp
                                    'Añadir al carrito' not in linea and  # Excluir botones
                                    'empresa' not in linea.lower()):
                                    
                                    # Limpiar bullets y caracteres especiales
                                    linea_limpia = linea.replace('○', '').replace('•', '').strip()
                                    
                                    if linea_limpia and linea_limpia not in textos_vistos:
                                        descripcion_completa.append(linea_limpia)
                                        textos_vistos.add(linea_limpia)
                        
                        if descripcion_completa:
                            break  # Si encontramos contenido, salir
                            
                    except:
                        continue
                
                # ESTRATEGIA 2: Si no se encontró nada, buscar spans con texto
                if not descripcion_completa:
                    print(f"   ⚠️  Estrategia 1 vacía, probando Estrategia 2...")
                    print(f"   🔎 Estrategia 2: Buscando spans individuales...")
                    
                    spans_texto = self.driver.find_elements(By.XPATH, 
                        "//span[contains(@class, 'selectable-text') and string-length(text()) > 10]"
                    )
                    
                    print(f"      Encontrados {len(spans_texto)} spans con texto...")
                    
                    for span in spans_texto[:30]:
                        try:
                            if not span.is_displayed():
                                continue
                            
                            texto = span.text.strip()
                            
                            if (texto and 
                                len(texto) > 10 and 
                                len(texto) < 500 and
                                texto not in textos_vistos and
                                texto != producto['titulo'] and
                                '$' not in texto and
                                'Leer más' not in texto and
                                'WhatsApp' not in texto and  # Excluir mensajes del sistema
                                'mensajes anteriores' not in texto and  # Excluir avisos
                                'Añadir al carrito' not in texto and
                                'empresa' not in texto.lower()):
                                
                                texto_limpio = texto.replace('○', '').replace('•', '').strip()
                                
                                if texto_limpio and texto_limpio not in textos_vistos:
                                    descripcion_completa.append(texto_limpio)
                                    textos_vistos.add(texto_limpio)
                        except:
                            continue
                    
                    if descripcion_completa:
                        print(f"   ✅ Estrategia 2 exitosa: {len(descripcion_completa)} fragmento(s)")
                else:
                    print(f"   ✅ Estrategia 1 exitosa: {len(descripcion_completa)} fragmento(s)")
                
                # Construir descripción final
                print(f"   📝 Construyendo descripción final...")
                
                if descripcion_completa:
                    # Validar que la descripción no sea solo mensajes del sistema
                    descripcion_valida = []
                    fragmentos_rechazados = 0
                    
                    for fragmento in descripcion_completa:
                        # Filtro final: excluir fragmentos problemáticos
                        if (fragmento and
                            'WhatsApp' not in fragmento and
                            'mensajes anteriores' not in fragmento and
                            'Usa WhatsApp en tu teléfono' not in fragmento and
                            len(fragmento) > 15):  # Al menos 15 caracteres útiles
                            descripcion_valida.append(fragmento)
                        else:
                            fragmentos_rechazados += 1
                    
                    if fragmentos_rechazados > 0:
                        print(f"      🗑️  {fragmentos_rechazados} fragmento(s) rechazado(s) por filtros")
                    
                    if descripcion_valida:
                        # Unir con separador
                        producto['descripcion'] = ' | '.join(descripcion_valida)
                        print(f"   ✅ Descripción capturada: {len(descripcion_valida)} fragmento(s) válido(s)")
                        print(f"      Preview: {producto['descripcion'][:100]}...")
                    else:
                        producto['descripcion'] = producto['titulo']
                        print(f"   ⚠️  Todos los fragmentos fueron rechazados, usando título")
                else:
                    # Fallback: usar título
                    producto['descripcion'] = producto['titulo']
                    print(f"   ⚠️  No se encontró descripción, usando título")
                    
            except Exception as e:
                print(f"   ❌ Error extrayendo descripción: {e}")
                producto['descripcion'] = producto['titulo']
            
            # Guardar datos.txt
            if numero_articulo:
                print(f"\n{'─'*60}")
                print(f"💾 GUARDANDO DATOS EN ARTICULO_{numero_articulo}")
                print(f"{'─'*60}")
                
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
                
                print(f"   ✅ Archivo datos.txt guardado")
                
                # RESUMEN FINAL DEL PRODUCTO
                print(f"\n{'='*60}")
                print(f"✅ EXTRACCIÓN COMPLETA - ARTICULO_{numero_articulo}")
                print(f"{'='*60}")
                print(f"   📄 Título: {producto['titulo']}")
                print(f"   💰 Precio: ${producto['precio']}")
                print(f"   📸 Imágenes: {'Sí' if producto['imagen_guardada'] else 'No'}")
                print(f"   📝 Descripción: {len(producto['descripcion'])} caracteres")
                if len(producto['descripcion']) > 100:
                    print(f"   📋 Preview descripción:")
                    print(f"      {producto['descripcion'][:150]}...")
                print(f"{'='*60}\n")
            
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
            
            # RUTA CORRECTA: Usar botón de catálogo directo
            if not self.abrir_catalogo_directo():
                return False
            
            # Ir a "Todos los artículos"
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
