from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from PIL import Image
from io import BytesIO
import time
import os


class ExtractorWhatsApp:
    """Extrae productos del catálogo de WhatsApp Web - VERSIÓN MEJORADA"""
    
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
        self.driver.set_script_timeout(15)  # ✅ Timeout para scripts async
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
            print("  → Localizando campo de búsqueda...")
            campo_busqueda = self.driver.find_element(By.XPATH, "//div[@contenteditable='true'][@data-tab='3']")
            campo_busqueda.click()
            time.sleep(1)
            
            campo_busqueda.clear()
            time.sleep(0.5)
            
            print(f"  → Escribiendo '{nombre_contacto}'...")
            campo_busqueda.send_keys(nombre_contacto)
            
            print("  → Esperando resultados de búsqueda...")
            time.sleep(5)
            
            try:
                print(f"  → Buscando '{nombre_contacto}' en los resultados...")
                
                contacto = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, f"//span[@title='{nombre_contacto}']"))
                )
                
                print("  → Contacto encontrado, haciendo clic...")
                contacto.click()
                time.sleep(3)
                
                print(f"✅ Contacto '{nombre_contacto}' abierto")
                return True
                
            except:
                print("  → Intentando método alternativo...")
                try:
                    contacto_alt = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{nombre_contacto}')]"))
                    )
                    contacto_alt.click()
                    time.sleep(3)
                    
                    print(f"✅ Contacto '{nombre_contacto}' abierto")
                    return True
                except:
                    print("❌ No se pudo hacer clic en el contacto.")
                    return False
            
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
    
    def verificar_en_catalogo(self):
        """Verifica que estamos en el catálogo - SIMPLIFICADO"""
        try:
            items = self.driver.find_elements(By.XPATH, "//div[@role='listitem']")
            return len(items) > 5  # Al menos 5 productos visibles
        except:
            return False
    
    def ir_a_todos_articulos(self):
        """Navega a la sección 'Todos los artículos' del catálogo"""
        print("📦 Buscando sección 'Todos los artículos'...")
        
        try:
            # Buscar el elemento "Todos los artículos" o "Ver todo"
            todos_articulos = self.driver.find_element(By.XPATH, 
                "//span[contains(text(), 'Todos los artículos') or contains(text(), 'todos los artículos')]"
            )
            
            # Hacer scroll hasta el elemento
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", todos_articulos)
            time.sleep(1)
            
            # Hacer clic
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
            # Buscar el contenedor de la lista
            contenedor = self.driver.find_element(By.XPATH, "//div[@role='list']")
            
            for i in range(veces):
                # Scroll hasta el final del contenedor
                self.driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight;",
                    contenedor
                )
                print(f"  → Scroll {i+1}/{veces}...")
                time.sleep(2)  # Esperar a que carguen más productos
            
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
    
    def hacer_scroll_lista_productos(self):
        """Hace scroll en el contenedor de productos para cargar más elementos"""
        try:
            contenedor_scroll = self.driver.find_element(By.XPATH, "//div[@role='list']")
            
            # Hacer scroll hasta el final
            self.driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight;",
                contenedor_scroll
            )
            time.sleep(1.5)
            
            print("  → Scroll realizado para cargar productos")
            return True
        except:
            return False
    
    def esperar_producto_cargado(self):
        """Espera a que el producto esté completamente cargado"""
        try:
            # Esperar a que aparezca la imagen
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//img[@draggable='false']"))
            )
            time.sleep(2.5)  # Espera adicional para estabilidad
            print("  ✓ Producto completamente cargado")
            return True
        except:
            print("  ⚠️  Timeout esperando carga del producto")
            return False
    
    def extraer_productos(self, cantidad_maxima=5):
        """Extrae productos - CON LOGS ULTRA DETALLADOS PARA DEBUG"""
        print(f"\n🎯 Iniciando extracción de hasta {cantidad_maxima} productos...\n")
        
        productos_extraidos = []
        indice_real = 0
        
        for i in range(cantidad_maxima):
            print(f"\n{'='*60}")
            print(f"📦 PRODUCTO {i + 1}/{cantidad_maxima}")
            print(f"{'='*60}")
            
            try:
                time.sleep(2)
                
                # PASO 1: Buscar todos los items
                items = self.driver.find_elements(By.XPATH, "//div[@role='listitem']")
                print(f"[DEBUG] Total items en DOM: {len(items)}")
                
                # PASO 2: Analizar cada item detalladamente
                productos_reales = []
                for idx, item in enumerate(items):
                    try:
                        # Obtener info del item
                        texto_item = item.text[:100] if item.text else "[sin texto]"
                        tiene_video = len(item.find_elements(By.TAG_NAME, 'video')) > 0
                        tiene_play = len(item.find_elements(By.XPATH, ".//*[contains(@data-icon, 'play')]")) > 0
                        tiene_imagen = len(item.find_elements(By.TAG_NAME, 'img')) > 0
                        
                        # ✅ NUEVO: Detectar categorías
                        es_categoria = 'Ver todo' in texto_item
                        
                        # ⚠️ NO filtrar por precio - WhatsApp no siempre lo muestra en lista
                        
                        print(f"[DEBUG] Item {idx}:")
                        print(f"        texto='{texto_item[:50]}...'")
                        print(f"        video={tiene_video} play={tiene_play} img={tiene_imagen}")
                        print(f"        categoría={es_categoria}")
                        
                        # ✅ Solo agregar si NO es video y NO es categoría
                        if not tiene_video and not tiene_play and not es_categoria:
                            productos_reales.append(item)
                            print(f"[DEBUG]   └─> ✅ PRODUCTO VÁLIDO (índice real: {len(productos_reales)-1})")
                        else:
                            razones = []
                            if tiene_video or tiene_play:
                                razones.append("video/multimedia")
                            if es_categoria:
                                razones.append("categoría")
                            print(f"[DEBUG]   └─> ❌ DESCARTADO ({', '.join(razones)})")
                    except Exception as e:
                        print(f"[DEBUG] Item {idx}: Error - {e}")
                
                print(f"\n[RESUMEN] Productos válidos: {len(productos_reales)}/{len(items)}")
                
                if indice_real >= len(productos_reales):
                    print(f"[INFO] Solo hay {len(productos_reales)} productos reales disponibles")
                    break
                
                # PASO 3: Seleccionar producto
                producto_item = productos_reales[indice_real]
                print(f"\n[ACCIÓN] Seleccionando producto real #{indice_real + 1}")
                print(f"[DEBUG] Texto del producto: '{producto_item.text[:100]}'")
                
                # PASO 4: Scroll y click
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", 
                    producto_item
                )
                time.sleep(1.5)
                producto_item.click()
                print(f"[ACCIÓN] ✅ Clic realizado")
                
                # PASO 5: Esperar carga
                print(f"[ESPERA] Esperando 6 segundos para carga...")
                time.sleep(6)
                
                # PASO 6: Verificar si es video
                print(f"[VERIFICACIÓN] Comprobando si abrió un video...")
                videos = self.driver.find_elements(By.TAG_NAME, 'video')
                if len(videos) > 0:
                    print(f"[ALERTA] ⚠️  Detectado {len(videos)} video(s), saltando...")
                    self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                    time.sleep(2)
                    indice_real += 1
                    continue
                
                print(f"[VERIFICACIÓN] ✅ No es video, es producto válido")
                
                # PASO 7: Verificar que estamos en vista de producto
                print(f"[DEBUG] Verificando URL actual...")
                url_actual = self.driver.current_url
                print(f"[DEBUG] URL: {url_actual}")
                
                # Verificar título de la página
                try:
                    titulo_pagina = self.driver.title
                    print(f"[DEBUG] Título página: {titulo_pagina}")
                except:
                    pass
                
                # PASO 8: Extraer datos
                print(f"\n[EXTRACCIÓN] Iniciando extracción de datos...")
                producto = self.extraer_datos_producto(numero_articulo=i+1)
                
                if producto:
                    print(f"[EXTRACCIÓN] ✅ Datos extraídos:")
                    print(f"  - Título: {producto['titulo']}")
                    print(f"  - Precio: ${producto['precio']}")
                    print(f"  - Descripción: {producto['descripcion'][:50]}...")
                    print(f"  - Imagen guardada: {producto.get('imagen_guardada', False)}")
                    
                    # Guardar datos.txt
                    carpeta_articulo = os.path.join(self.carpeta_principal, f"Articulo_{i+1}")
                    archivo_datos = os.path.join(carpeta_articulo, "datos.txt")
                    os.makedirs(carpeta_articulo, exist_ok=True)
                    
                    plantilla = f"""titulo={producto['titulo']}
precio={producto['precio']}
categoria=Electrónica e informática
estado=Nuevo
descripcion={producto['descripcion']}
disponibilidad=Publicar como disponible
encuentro_publico=Si
etiquetas=
sku="""
                    
                    with open(archivo_datos, 'w', encoding='utf-8') as f:
                        f.write(plantilla)
                    
                    productos_extraidos.append(producto)
                    print(f"[GUARDADO] ✅ Producto guardado en Articulo_{i+1}\n")
                
                indice_real += 1
                
                # PASO 9: Volver
                print(f"[ACCIÓN] Presionando ESC para volver...")
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                time.sleep(5)
                print(f"[ACCIÓN] ✅ Vuelto al catálogo\n")
                
            except Exception as e:
                print(f"\n[ERROR] ❌ Excepción capturada: {e}")
                import traceback
                traceback.print_exc()
                
                # Intentar volver
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
    
    def volver_a_catalogo(self):
        """Vuelve al catálogo - MÉTODO SIMPLIFICADO"""
        try:
            # Método 1: ESC (más confiable que el botón)
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            print("  ← ESC presionado")
            time.sleep(5)  # Espera larga para asegurar carga
            
            # Verificar items
            items = self.driver.find_elements(By.XPATH, "//div[@role='listitem']")
            print(f"  → Items visibles: {len(items)}")
            
            return len(items) > 0
            
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
            return False
    
    def volver_a_catalogo_forzado(self):
        """Vuelve al catálogo usando múltiples métodos - VERSIÓN ULTRA ROBUSTA"""
        try:
            print("  [FORZADO] Intentando volver al catálogo...")
            
            # Método 1: Botón header CON VERIFICACIÓN
            try:
                botones = self.driver.find_elements(By.XPATH, "//header//button")
                if botones:
                    print(f"  [FORZADO] Método 1: Clic en botón ({len(botones)} disponibles)")
                    botones[0].click()
                    time.sleep(4)
                    
                    # Verificar items visibles
                    items = self.driver.find_elements(By.XPATH, "//div[@role='listitem']")
                    print(f"  [FORZADO] Items visibles: {len(items)}")
                    
                    if len(items) > 0:
                        print("  [FORZADO] ✓ Método 1 exitoso")
                        return True
            except Exception as e:
                print(f"  [FORZADO] Método 1 falló: {e}")
            
            # Método 2: ESC
            try:
                print("  [FORZADO] Método 2: Presionar ESC")
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                time.sleep(3)
                
                items = self.driver.find_elements(By.XPATH, "//div[@role='listitem']")
                print(f"  [FORZADO] Items visibles: {len(items)}")
                
                if len(items) > 0:
                    print("  [FORZADO] ✓ Método 2 exitoso")
                    return True
            except Exception as e:
                print(f"  [FORZADO] Método 2 falló: {e}")
            
            # Método 3: Buscar y hacer clic en "Catálogo"
            try:
                print("  [FORZADO] Método 3: Buscar enlace 'Catálogo'")
                enlace_catalogo = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Catálogo')]")
                enlace_catalogo.click()
                time.sleep(3)
                
                items = self.driver.find_elements(By.XPATH, "//div[@role='listitem']")
                print(f"  [FORZADO] Items visibles: {len(items)}")
                
                if len(items) > 0:
                    print("  [FORZADO] ✓ Método 3 exitoso")
                    return True
            except Exception as e:
                print(f"  [FORZADO] Método 3 falló: {e}")
            
            # Método 4: ESC múltiple (emergencia)
            try:
                print("  [FORZADO] Método 4: ESC x3 (emergencia)")
                for i in range(3):
                    self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                    time.sleep(1)
                
                time.sleep(2)
                items = self.driver.find_elements(By.XPATH, "//div[@role='listitem']")
                print(f"  [FORZADO] Items visibles: {len(items)}")
                
                if len(items) > 0:
                    print("  [FORZADO] ✓ Método 4 exitoso")
                    return True
            except Exception as e:
                print(f"  [FORZADO] Método 4 falló: {e}")
            
            print("  [FORZADO] ❌ Todos los métodos fallaron")
            return False
            
        except Exception as e:
            print(f"  ❌ Error en volver forzado: {e}")
            return False
    
    def extraer_datos_producto(self, numero_articulo=None):
        """Extrae los datos de un producto - CON LOGS ULTRA DETALLADOS"""
        try:
            print(f"[EXTRACCIÓN] Esperando 5 segundos...")
            
            producto = {
                'titulo': '',
                'precio': '',
                'descripcion': '',
                'imagen_guardada': False
            }
            
            time.sleep(5)
            
            # SI SE PROPORCIONA numero_articulo, GUARDAR IMÁGENES INMEDIATAMENTE
            if numero_articulo is not None:
                print(f"[IMAGEN] Buscando imágenes para Articulo_{numero_articulo}...")
                try:
                    # Buscar TODAS las imágenes del producto
                    selectores_imagen = [
                        "//img[@class='_ak9n' and @draggable='false']",
                        "//img[contains(@class, '_ak9n')]",
                        "//img[@draggable='false']"
                    ]
                    
                    imagenes_encontradas = []
                    for idx, selector in enumerate(selectores_imagen):
                        print(f"[IMAGEN] Probando selector {idx + 1}: {selector}")
                        try:
                            elementos = self.driver.find_elements(By.XPATH, selector)
                            print(f"[IMAGEN]   └─> Encontrados: {len(elementos)} elementos")
                            
                            for elem in elementos:
                                if elem.is_displayed():
                                    src = elem.get_attribute('src')
                                    
                                    # ✅ PROTECCIÓN CONTRA VIDEOS - Verificar múltiples condiciones
                                    es_video = False
                                    
                                    # Check 1: src contiene 'video'
                                    if src and 'video' in src.lower():
                                        es_video = True
                                    
                                    # Check 2: Elemento padre es <video>
                                    try:
                                        parent_tag = elem.find_element(By.XPATH, "..").tag_name
                                        if parent_tag == 'video':
                                            es_video = True
                                    except:
                                        pass
                                    
                                    # Check 3: Elemento tiene atributo de video
                                    try:
                                        if elem.get_attribute('poster') or elem.get_attribute('data-video'):
                                            es_video = True
                                    except:
                                        pass
                                    
                                    # Check 4: Buscar <video> cercano (hermanos o hijos)
                                    try:
                                        videos_cercanos = elem.find_elements(By.XPATH, ".//video | ../video | ../../video")
                                        if len(videos_cercanos) > 0:
                                            es_video = True
                                    except:
                                        pass
                                    
                                    if es_video:
                                        print(f"[IMAGEN]       └─> Saltado (es video o relacionado)")
                                        continue
                                    
                                    # Evitar duplicados
                                    if elem not in imagenes_encontradas:
                                        imagenes_encontradas.append(elem)
                                        print(f"[IMAGEN]       └─> Imagen {len(imagenes_encontradas)} agregada")
                            
                            if imagenes_encontradas:
                                print(f"[IMAGEN] ✅ {len(imagenes_encontradas)} imagen(es) encontrada(s) con selector {idx + 1}")
                                break
                        except Exception as e:
                            print(f"[IMAGEN]   └─> Error: {e}")
                            continue
                    
                    if imagenes_encontradas:
                        print(f"[IMAGEN] Guardando {len(imagenes_encontradas)} imagen(es)...")
                        carpeta_imagenes = os.path.join(self.carpeta_principal, f"Articulo_{numero_articulo}", "imagenes")
                        os.makedirs(carpeta_imagenes, exist_ok=True)
                        
                        # Guardar hasta 10 imágenes
                        imagenes_guardadas = 0
                        for idx, imagen_elem in enumerate(imagenes_encontradas[:10]):
                            ruta_imagen = os.path.join(carpeta_imagenes, f"imagen_{idx + 1}.jpg")
                            
                            if self.descargar_imagen_blob(imagen_elem, ruta_imagen):
                                imagenes_guardadas += 1
                                print(f"[IMAGEN]   ✓ Imagen {idx + 1} guardada")
                            else:
                                print(f"[IMAGEN]   ✗ Error guardando imagen {idx + 1}")
                        
                        if imagenes_guardadas > 0:
                            producto['imagen_guardada'] = True
                            print(f"[IMAGEN] ✅ {imagenes_guardadas} imagen(es) guardada(s) correctamente")
                        else:
                            print(f"[IMAGEN] ❌ No se pudo guardar ninguna imagen")
                    else:
                        print(f"[IMAGEN] ⚠️  No se encontró ninguna imagen visible")
                except Exception as e:
                    print(f"[IMAGEN] ❌ Excepción: {e}")
            
            # EXTRAER TÍTULO
            print(f"\n[TÍTULO] Buscando título...")
            try:
                titulos_posibles = self.driver.find_elements(By.XPATH, 
                    "//div[contains(@class, 'x1okw0bk')]//span[contains(@class, 'selectable-text')]"
                )
                
                print(f"[TÍTULO] Encontrados {len(titulos_posibles)} elementos candidatos")
                
                for idx, titulo_elem in enumerate(titulos_posibles[:15]):
                    try:
                        if not titulo_elem.is_displayed():
                            print(f"[TÍTULO] Elemento {idx}: NO visible, saltando...")
                            continue
                        
                        texto = titulo_elem.text.strip()
                        print(f"[TÍTULO] Elemento {idx}: '{texto[:50]}...'")
                        
                        # Filtros mejorados
                        if (texto and 
                            8 < len(texto) < 70 and 
                            '$' not in texto and 
                            '○' not in texto and 
                            '◯' not in texto and
                            'Marca:' not in texto and
                            'Modelo:' not in texto and
                            'Color:' not in texto and
                            'Trabajo' not in texto and
                            'John' not in texto and
                            'Detalles' not in texto and
                            'Catálogo' not in texto and
                            'TECLADOS' not in texto and
                            'MOUSES' not in texto and
                            'MOUSEPADS' not in texto and
                            'Leer más' not in texto and
                            'Leer menos' not in texto):
                            
                            producto['titulo'] = texto
                            print(f"[TÍTULO] ✅ SELECCIONADO: '{texto}'")
                            break
                        else:
                            print(f"[TÍTULO]   └─> Rechazado (no cumple filtros)")
                    except Exception as e:
                        print(f"[TÍTULO] Elemento {idx}: Error - {e}")
                        continue
                
                if not producto['titulo']:
                    # Método alternativo: buscar en todo el contenedor
                    try:
                        contenedor_principal = self.driver.find_element(By.XPATH, "//div[contains(@class, 'x1okw0bk')]")
                        textos_span = contenedor_principal.find_elements(By.TAG_NAME, "span")
                        
                        for span in textos_span[:20]:
                            try:
                                texto = span.text.strip()
                                if (texto and 
                                    10 < len(texto) < 70 and
                                    '$' not in texto and
                                    'Marca:' not in texto):
                                    producto['titulo'] = texto
                                    print(f"  → Título (alternativo): {texto}")
                                    break
                            except:
                                continue
                    except:
                        pass
                
                if not producto['titulo']:
                    producto['titulo'] = "Sin título"
                    
            except Exception as e:
                print(f"  ⚠️  Error extrayendo título: {e}")
                producto['titulo'] = "Sin título"
            
            # EXTRAER PRECIO
            print(f"\n[PRECIO] Buscando precio...")
            try:
                precios = self.driver.find_elements(By.XPATH, 
                    "//*[starts-with(text(), '$') and string-length(text()) < 15]"
                )
                
                print(f"[PRECIO] Encontrados {len(precios)} elementos con '$'")
                
                for idx, precio_elem in enumerate(precios[:5]):
                    try:
                        if precio_elem.is_displayed():
                            precio_texto = precio_elem.text.strip()
                            print(f"[PRECIO] Elemento {idx}: '{precio_texto}'")
                            precio_limpio = precio_texto.split()[0].replace('$', '').replace(',', '').strip()
                            
                            if precio_limpio and precio_limpio.replace('.', '').isdigit():
                                producto['precio'] = precio_limpio
                                print(f"[PRECIO] ✅ SELECCIONADO: ${precio_limpio}")
                                break
                            else:
                                print(f"[PRECIO]   └─> Rechazado (no es número válido)")
                    except Exception as e:
                        print(f"[PRECIO] Elemento {idx}: Error - {e}")
                        continue
                
                if not producto['precio']:
                    producto['precio'] = "0"
                    
            except:
                producto['precio'] = "0"
            
            # EXPANDIR DESCRIPCIÓN
            try:
                leer_mas = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Leer más')]")
                if leer_mas.is_displayed():
                    leer_mas.click()
                    time.sleep(2)
                    print("  → Descripción expandida")
            except:
                pass
            
            # EXPANDIR DESCRIPCIÓN si hay botón "Leer más"
            print(f"\n[DESCRIPCIÓN] Verificando si hay botón 'Leer más'...")
            try:
                # Intentar múltiples selectores para encontrar "Leer más"
                selectores_leer_mas = [
                    # Selector ESPECÍFICO para el span con role="button"
                    "//span[@role='button' and contains(text(), 'Leer más')]",
                    "//span[@role='button' and contains(text(), 'leer más')]",
                    "//span[@class='x1ph7ams' and @role='button']",
                    # Selectores genéricos
                    "//span[contains(text(), 'Leer más')]",
                    "//span[contains(text(), 'leer más')]",
                    "//*[contains(text(), 'Leer más')]",
                    "//*[contains(text(), 'leer más')]",
                    "//div[contains(text(), 'Leer más')]",
                    "//a[contains(text(), 'Leer más')]"
                ]
                
                leer_mas_encontrado = False
                
                for idx, selector in enumerate(selectores_leer_mas):
                    try:
                        print(f"[DESCRIPCIÓN]   Probando selector {idx + 1}/{len(selectores_leer_mas)}...")
                        elementos = self.driver.find_elements(By.XPATH, selector)
                        
                        if elementos:
                            print(f"[DESCRIPCIÓN]   → Encontrados {len(elementos)} elementos")
                            
                            for elem in elementos:
                                try:
                                    # Verificar que el texto contenga "Leer más" (con o sin espacio)
                                    texto = elem.text.strip()
                                    if 'leer más' not in texto.lower():
                                        continue
                                    
                                    if elem.is_displayed():
                                        # Hacer scroll hasta el elemento
                                        self.driver.execute_script(
                                            "arguments[0].scrollIntoView({block: 'center'});", 
                                            elem
                                        )
                                        time.sleep(0.5)
                                        
                                        print(f"[DESCRIPCIÓN]   ✓ Encontrado '{texto}', haciendo clic...")
                                        
                                        # Intentar clic directo primero
                                        try:
                                            elem.click()
                                        except:
                                            # Si falla, usar JavaScript
                                            print(f"[DESCRIPCIÓN]   → Usando JavaScript para clic...")
                                            self.driver.execute_script("arguments[0].click();", elem)
                                        
                                        time.sleep(2.5)  # Esperar a que se expanda
                                        print(f"[DESCRIPCIÓN]   ✓ Descripción expandida")
                                        leer_mas_encontrado = True
                                        break
                                except Exception as e:
                                    print(f"[DESCRIPCIÓN]   ✗ Error en elemento: {e}")
                                    continue
                            
                            if leer_mas_encontrado:
                                break
                    except Exception as e:
                        continue
                
                if not leer_mas_encontrado:
                    print(f"[DESCRIPCIÓN]   ℹ️  No se encontró botón 'Leer más' (puede estar expandido)")
                    
            except Exception as e:
                print(f"[DESCRIPCIÓN]   ℹ️  No hay botón 'Leer más'")
            
            # Esperar un poco más después de expandir
            time.sleep(1)
            
            # EXTRAER DESCRIPCIÓN - MÉTODO MULTI-ESTRATEGIA
            print(f"[DESCRIPCIÓN] Extrayendo descripción completa...")
            try:
                detalles = []
                
                # MÉTODO 1: Buscar todos los elementos con ○
                try:
                    print(f"[DESCRIPCIÓN] Método 1: Buscando bullets con ○")
                    elementos_bullets = self.driver.find_elements(By.XPATH, 
                        "//*[contains(text(), '○')]"
                    )
                    
                    print(f"[DESCRIPCIÓN]   → Encontrados {len(elementos_bullets)} elementos")
                    
                    for elem in elementos_bullets[:30]:
                        try:
                            if elem.is_displayed():
                                texto_completo = elem.text.strip()
                                
                                # Dividir por ○ para obtener cada detalle
                                partes = texto_completo.split('○')
                                
                                for parte in partes:
                                    linea = parte.strip()
                                    
                                    # Filtrar líneas relevantes
                                    if linea and len(linea) > 5 and len(linea) < 200:
                                        # Verificar palabras clave
                                        if any(palabra in linea.lower() for palabra in 
                                               ['marca:', 'modelo:', 'color:', 'material:', 'ancho:', 'largo:', 
                                                'peso:', 'tamaño:', 'garantía:', 'conectividad:', 'bluetooth:',
                                                'cable:', 'batería:', 'teclas:', 'dpi:', 'switch:', 'modos:',
                                                'interfaz:', 'incluye', 'tipo:', 'estándar:', 'teclado:',
                                                'velocidad:', 'iluminación:', 'retroiluminado:', 'ideal:']):
                                            
                                            # Validar que no sea el título ni precio
                                            if (linea not in detalles and 
                                                linea != producto['titulo'] and 
                                                '$' not in linea and
                                                'Trabajo' not in linea and
                                                'John' not in linea):
                                                
                                                detalles.append(linea)
                                                print(f"[DESCRIPCIÓN]     Detalle {len(detalles)}: '{linea[:70]}...'")
                                                
                                                if len(detalles) >= 15:
                                                    break
                        except:
                            continue
                    
                    if detalles:
                        print(f"[DESCRIPCIÓN] Método 1 exitoso: {len(detalles)} detalles")
                
                except Exception as e:
                    print(f"[DESCRIPCIÓN] Método 1 falló: {e}")
                
                # MÉTODO 2: Si no hay detalles, buscar por span[dir='auto']
                if not detalles:
                    try:
                        print(f"[DESCRIPCIÓN] Método 2: Buscando spans con dir='auto'")
                        spans = self.driver.find_elements(By.XPATH, "//span[@dir='auto']")
                        
                        print(f"[DESCRIPCIÓN]   → Encontrados {len(spans)} elementos")
                        
                        for span in spans[:50]:
                            try:
                                texto = span.text.strip()
                                
                                if texto and len(texto) > 5 and len(texto) < 200:
                                    if any(palabra in texto.lower() for palabra in 
                                           ['marca:', 'modelo:', 'color:', 'material:', 'ancho:', 'largo:', 
                                            'conectividad:', 'bluetooth:', 'teclas:', 'ideal:']):
                                        
                                        if (texto not in detalles and 
                                            texto != producto['titulo'] and 
                                            '$' not in texto):
                                            
                                            detalles.append(texto)
                                            print(f"[DESCRIPCIÓN]     Detalle {len(detalles)}: '{texto[:70]}...'")
                                            
                                            if len(detalles) >= 15:
                                                break
                            except:
                                continue
                        
                        if detalles:
                            print(f"[DESCRIPCIÓN] Método 2 exitoso: {len(detalles)} detalles")
                    
                    except Exception as e:
                        print(f"[DESCRIPCIÓN] Método 2 falló: {e}")
                
                # Si encontramos detalles, usarlos
                if detalles:
                    producto['descripcion'] = ' | '.join(detalles)
                    print(f"[DESCRIPCIÓN] ✅ CAPTURADOS: {len(detalles)} detalles")
                else:
                    # Fallback: usar título
                    producto['descripcion'] = producto['titulo']
                    print(f"[DESCRIPCIÓN] ⚠️  Sin detalles, usando título")
                    
            except Exception as e:
                print(f"[DESCRIPCIÓN] ❌ Error: {e}")
                producto['descripcion'] = producto['titulo']
            
            return producto
            
        except Exception as e:
            print(f"❌ Error extrayendo datos del producto: {e}")
            return None
    
    def descargar_imagen_blob(self, elemento_imagen, ruta_destino):
        """Descarga imagen desde blob URL usando JavaScript"""
        try:
            print(f"  📸 Descargando imagen...")
            
            # Obtener el src
            src = elemento_imagen.get_attribute('src')
            
            if src.startswith('http'):
                # URL normal - descargar con requests
                import requests
                response = requests.get(src, timeout=10)
                with open(ruta_destino, 'wb') as f:
                    f.write(response.content)
                print("    ✓ Imagen descargada (HTTP)")
                return True
                
            elif src.startswith('blob:'):
                # URL blob - convertir con JavaScript
                try:
                    # Intentar método asíncrono con timeout
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
                        
                        // Timeout de 10 segundos
                        setTimeout(() => callback(null), 10000);
                    """, src)
                    
                    if base64_data:
                        import base64
                        with open(ruta_destino, 'wb') as f:
                            f.write(base64.b64decode(base64_data))
                        print("    ✓ Imagen descargada (blob)")
                        return True
                    else:
                        print("    ⚠️  Blob timeout, usando screenshot...")
                        return self.capturar_screenshot_imagen(elemento_imagen, ruta_destino)
                        
                except Exception as e:
                    print(f"    ⚠️  Error con blob: {e}, usando screenshot...")
                    return self.capturar_screenshot_imagen(elemento_imagen, ruta_destino)
            
            else:
                # base64 inline - guardar directamente
                if src.startswith('data:image'):
                    import base64
                    base64_data = src.split(',')[1]
                    with open(ruta_destino, 'wb') as f:
                        f.write(base64.b64decode(base64_data))
                    print("    ✓ Imagen guardada (base64)")
                    return True
                    
            return False
            
        except Exception as e:
            print(f"    ⚠️  Error descargando: {e}")
            # Fallback a screenshot
            return self.capturar_screenshot_imagen(elemento_imagen, ruta_destino)
    def capturar_screenshot_imagen(self, elemento, ruta_destino):
        """Captura screenshot optimizado de la imagen - MÉTODO FALLBACK"""
        try:
            print(f"  📸 Capturando imagen...")
            
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", 
                elemento
            )
            time.sleep(2)
            
            location = elemento.location
            size = elemento.size
            
            screenshot = self.driver.get_screenshot_as_png()
            img = Image.open(BytesIO(screenshot))
            
            margen = 50
            left = max(0, location['x'] - margen)
            top = max(0, location['y'] - margen)
            right = min(img.width, location['x'] + size['width'] + margen)
            bottom = min(img.height, location['y'] + size['height'] + margen)
            
            if right > left and bottom > top:
                imagen_recortada = img.crop((left, top, right, bottom))
                imagen_recortada.save(ruta_destino, 'JPEG', quality=95)
                print(f"    ✓ Imagen guardada")
                return True
            else:
                print(f"    ✗ Coordenadas inválidas")
                return False
                
        except Exception as e:
            print(f"    ✗ Error capturando: {e}")
            return False
    
    def guardar_producto(self, producto, numero_articulo):
        """Guarda los datos del producto (la imagen ya fue guardada)"""
        carpeta_articulo = os.path.join(self.carpeta_principal, f"Articulo_{numero_articulo}")
        archivo_datos = os.path.join(carpeta_articulo, "datos.txt")
        
        os.makedirs(carpeta_articulo, exist_ok=True)
        
        plantilla = f"""titulo={producto['titulo']}
precio={producto['precio']}
categoria=Electrónica e informática
estado=Nuevo
descripcion={producto['descripcion']}
disponibilidad=Publicar como disponible
encuentro_publico=Si
etiquetas=
sku="""
        
        with open(archivo_datos, 'w', encoding='utf-8') as f:
            f.write(plantilla)
        
        print(f"  ✓ Datos guardados en Articulo_{numero_articulo}")
    
    def ejecutar(self, nombre_contacto, cantidad_productos=5):
        """Ejecuta el proceso completo de extracción"""
        print("\n" + "="*60)
        print("🚀 EXTRACTOR DE CATÁLOGO DE WHATSAPP - VERSIÓN MEJORADA")
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
            
            # ✅ NUEVO: Intentar ir a "Todos los artículos"
            self.ir_a_todos_articulos()
            
            # ✅ NUEVO: Hacer scroll para cargar más productos
            self.hacer_scroll_catalogo(veces=5)
            
            total_productos = self.contar_productos_catalogo()
            
            productos = self.extraer_productos(cantidad_productos)
            
            print("\n" + "="*60)
            print(f"✅ EXTRACCIÓN COMPLETADA - {len(productos)} productos guardados")
            print("="*60 + "\n")
            
            return productos
            
        except Exception as e:
            print(f"\n❌ Error durante la extracción: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            print("\n⏳ Cerrando navegador en 5 segundos...")
            time.sleep(5)
            if self.driver:
                self.driver.quit()
