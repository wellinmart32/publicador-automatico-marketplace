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
        """Verifica que estamos en la vista del catálogo - VERSIÓN MEJORADA"""
        try:
            # Método 1: Buscar texto "Catálogo"
            catalogo_texto = self.driver.find_elements(By.XPATH, "//span[contains(text(), 'Catálogo')]")
            if len(catalogo_texto) > 0:
                print("  [DEBUG] Catálogo detectado por texto")
                return True
            
            # Método 2: Buscar lista de productos (role='list')
            lista_productos = self.driver.find_elements(By.XPATH, "//div[@role='list']")
            if len(lista_productos) > 0:
                print("  [DEBUG] Catálogo detectado por lista de productos")
                return True
            
            # Método 3: Buscar items de producto (role='listitem')
            items_productos = self.driver.find_elements(By.XPATH, "//div[@role='listitem']")
            if len(items_productos) > 0:
                print(f"  [DEBUG] Catálogo detectado: {len(items_productos)} items visibles")
                return True
            
            # Método 4: Verificar que NO estamos en vista de producto individual
            # (si hay botón de volver pero no hay lista, estamos EN el producto)
            imagen_producto = self.driver.find_elements(By.XPATH, "//img[@draggable='false']")
            if len(imagen_producto) > 0 and len(items_productos) == 0:
                print("  [DEBUG] En vista de producto individual (no catálogo)")
                return False
            
            print("  [DEBUG] No se pudo confirmar catálogo")
            return False
            
        except Exception as e:
            print(f"  [DEBUG] Error verificando catálogo: {e}")
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
        """Extrae los datos de los productos del catálogo - VERSIÓN ULTRA ROBUSTA V2"""
        print(f"\n🎯 Iniciando extracción de hasta {cantidad_maxima} productos...\n")
        
        productos_extraidos = []
        productos_procesados_indices = set()
        
        for intento_producto in range(cantidad_maxima):
            print(f"📦 Procesando producto {intento_producto + 1}/{cantidad_maxima}...")
            
            intentos_click = 0
            max_intentos = 3  # ✅ REDUCIDO de 5 a 3 para evitar loops eternos
            producto_extraido_exitosamente = False
            
            while intentos_click < max_intentos and not producto_extraido_exitosamente:
                try:
                    # PASO 1: Verificar catálogo
                    time.sleep(2.5)
                    
                    if not self.verificar_en_catalogo():
                        print("  ⚠️  No estamos en el catálogo, volviendo...")
                        if not self.volver_a_catalogo_forzado():
                            print("  ❌ No se pudo volver al catálogo")
                            intentos_click += 1
                            continue
                        time.sleep(3)
                    
                    # PASO 2: Hacer scroll
                    self.hacer_scroll_lista_productos()
                    time.sleep(1.5)
                    
                    # PASO 3: RE-BUSCAR productos
                    items_productos = self.driver.find_elements(By.XPATH, "//div[@role='listitem']")
                    
                    print(f"  → Productos encontrados en DOM: {len(items_productos)}")
                    
                    if len(items_productos) == 0:
                        print("  ⚠️  No se encontraron productos, reintentando...")
                        intentos_click += 1
                        time.sleep(3)
                        continue
                    
                    if intento_producto >= len(items_productos):
                        print(f"  ✓ Completado: {len(items_productos)} productos disponibles")
                        return productos_extraidos
                    
                    # PASO 4: Scroll al producto
                    producto_actual = items_productos[intento_producto]
                    
                    print(f"  → Haciendo scroll al producto {intento_producto + 1}...")
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                        producto_actual
                    )
                    time.sleep(2)
                    
                    # PASO 5: Click
                    print(f"  → Haciendo clic en producto {intento_producto + 1}...")
                    producto_actual.click()
                    
                    # PASO 6: Esperar carga completa
                    time.sleep(5)
                    self.esperar_producto_cargado()
                    
                    # PASO 7: Extraer datos
                    producto = self.extraer_datos_producto()
                    
                    if producto:
                        # ✅ Control de duplicados
                        if intento_producto not in productos_procesados_indices:
                            productos_extraidos.append(producto)
                            productos_procesados_indices.add(intento_producto)
                            print(f"✅ Producto {intento_producto + 1} extraído: {producto['titulo']}\n")
                            producto_extraido_exitosamente = True  # ✅ MARCAR COMO EXITOSO
                        else:
                            print(f"  ⚠️  Producto {intento_producto + 1} ya fue extraído (duplicado)")
                            # ✅ Si es duplicado, significa que NO volvimos correctamente
                            # Incrementar intentos y forzar salida del while
                            intentos_click += 1
                            if intentos_click >= max_intentos:
                                print(f"  ⚠️  Demasiados duplicados, forzando avance al siguiente producto")
                                producto_extraido_exitosamente = True  # ✅ FORZAR SALIDA
                    
                    # PASO 8: Volver al catálogo
                    print("  ← Volviendo al catálogo...")
                    volver_exitoso = False
                    
                    # Intentar método principal
                    if self.volver_a_catalogo():
                        time.sleep(2)
                        # Verificar items
                        items_check = self.driver.find_elements(By.XPATH, "//div[@role='listitem']")
                        if len(items_check) > 0:
                            volver_exitoso = True
                    
                    # Si falla, usar método forzado
                    if not volver_exitoso:
                        print("  ⚠️  Método principal falló, usando alternativo...")
                        if self.volver_a_catalogo_forzado():
                            volver_exitoso = True
                    
                    time.sleep(3.5)
                    
                    # PASO 9: VERIFICAR que volvimos
                    items_final = self.driver.find_elements(By.XPATH, "//div[@role='listitem']")
                    
                    if len(items_final) > 0:
                        print(f"  ✓ Confirmado: {len(items_final)} productos en catálogo")
                        break  # ✅ Salir del while de reintentos
                    else:
                        print("  ⚠️  No se confirmó vuelta, reintentando...")
                        intentos_click += 1
                        continue
                    
                except StaleElementReferenceException:
                    intentos_click += 1
                    print(f"  ⚠️  Elemento obsoleto, reintento {intentos_click}/{max_intentos}...")
                    time.sleep(3)
                    if intentos_click >= max_intentos:
                        print(f"  ❌ Máximo de reintentos alcanzado")
                        break
                    continue
                    
                except Exception as e:
                    print(f"  ⚠️  Error: {e}")
                    intentos_click += 1
                    try:
                        self.volver_a_catalogo_forzado()
                        time.sleep(3)
                    except:
                        pass
                    
                    if intentos_click >= max_intentos:
                        print(f"  ❌ Máximo de reintentos alcanzado\n")
                        break
                    continue
            
            # ✅ Si salimos del while sin éxito, continuar con el siguiente producto
            if not producto_extraido_exitosamente and intento_producto not in productos_procesados_indices:
                print(f"  ⚠️  No se pudo extraer producto {intento_producto + 1}, continuando...\n")
        
        print(f"\n✅ Extracción completada: {len(productos_extraidos)} productos")
        return productos_extraidos
    
    def volver_a_catalogo(self):
        """Vuelve al catálogo de productos - VERSIÓN MEJORADA"""
        try:
            print("  ← Intentando volver al catálogo...")
            
            # Buscar botones en el header
            botones_header = self.driver.find_elements(By.XPATH, "//header//button")
            
            if len(botones_header) > 0:
                print(f"  [DEBUG] Encontrados {len(botones_header)} botones en header")
                
                # Hacer clic en el primer botón (botón volver)
                botones_header[0].click()
                print("  [DEBUG] Clic en botón volver")
                
                # Esperar más tiempo para que la navegación se complete
                time.sleep(4)  # Aumentado de 2.5 a 4 segundos
                
                # Verificar si volvimos
                items = self.driver.find_elements(By.XPATH, "//div[@role='listitem']")
                print(f"  [DEBUG] Items visibles después de volver: {len(items)}")
                
                if len(items) > 0:
                    return True
                else:
                    print("  [DEBUG] No se ven items, esperando más...")
                    time.sleep(2)
                    items = self.driver.find_elements(By.XPATH, "//div[@role='listitem']")
                    print(f"  [DEBUG] Items después de espera adicional: {len(items)}")
                    return len(items) > 0
            else:
                print("  [DEBUG] No se encontraron botones en header")
                return False
                
        except Exception as e:
            print(f"  ⚠️  Error al volver: {e}")
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
    
    def extraer_datos_producto(self):
        """Extrae los datos de un producto - VERSIÓN MEJORADA CON MÁS ESPERA"""
        try:
            producto = {
                'titulo': '',
                'precio': '',
                'descripcion': '',
                'imagen_elemento': None
            }
            
            # Esperar más tiempo para asegurar carga completa
            time.sleep(5)
            
            # EXTRAER TÍTULO
            try:
                titulos_posibles = self.driver.find_elements(By.XPATH, 
                    "//div[contains(@class, 'x1okw0bk')]//span[contains(@class, 'selectable-text')]"
                )
                
                for titulo_elem in titulos_posibles[:15]:
                    try:
                        if not titulo_elem.is_displayed():
                            continue
                        
                        texto = titulo_elem.text.strip()
                        
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
                            print(f"  → Título encontrado: {texto}")
                            break
                    except:
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
                                producto['precio'] = precio_limpio
                                print(f"  → Precio encontrado: ${precio_limpio}")
                                break
                    except:
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
            
            # EXTRAER DESCRIPCIÓN - MÉTODO MEJORADO
            try:
                detalles = []
                textos_unicos = set()
                
                # Método 1: Buscar bullets
                try:
                    contenedor = self.driver.find_element(By.XPATH, "//div[contains(@class, 'x1okw0bk')]")
                    elementos = contenedor.find_elements(By.XPATH, ".//*[self::span or self::div]")
                    
                    for elem in elementos[:30]:
                        try:
                            texto = elem.text.strip()
                            
                            if (texto and 
                                5 < len(texto) < 200 and
                                texto not in textos_unicos and
                                '$' not in texto and
                                texto != producto['titulo'] and
                                'Catálogo' not in texto and
                                'Detalles' not in texto):
                                
                                # Verificar si contiene información relevante
                                if any(palabra in texto.lower() for palabra in ['marca', 'modelo', 'color', 'garantía', 'tamaño', 'peso', 'material']):
                                    primera_linea = texto.split('\n')[0].strip()
                                    if primera_linea and len(detalles) < 10:
                                        detalles.append(primera_linea)
                                        textos_unicos.add(primera_linea)
                        except:
                            continue
                except:
                    pass
                
                # Método 2: Si no hay detalles, tomar texto del contenedor
                if not detalles:
                    try:
                        contenedor = self.driver.find_element(By.XPATH, "//div[contains(@class, 'x1okw0bk')]")
                        texto_completo = contenedor.text
                        
                        # Dividir por líneas y filtrar
                        lineas = texto_completo.split('\n')
                        for linea in lineas[:20]:
                            linea = linea.strip()
                            if (linea and 
                                10 < len(linea) < 200 and
                                linea != producto['titulo'] and
                                '$' not in linea and
                                len(detalles) < 5):
                                detalles.append(linea)
                    except:
                        pass
                
                if detalles:
                    producto['descripcion'] = ' | '.join(detalles)
                    print(f"  → Descripción: {len(detalles)} detalles capturados")
                else:
                    producto['descripcion'] = producto['titulo']  # Usar título como fallback
                    
            except Exception as e:
                print(f"  ⚠️  Error extrayendo descripción: {e}")
                producto['descripcion'] = producto['titulo']
            
            # CAPTURAR IMAGEN - MÉTODO MEJORADO
            try:
                time.sleep(2.5)
                
                # Intentar múltiples selectores
                selectores_imagen = [
                    "//img[@class='_ak9n' and @draggable='false']",
                    "//img[contains(@class, '_ak9n')]",
                    "//img[@draggable='false']"
                ]
                
                imagen = None
                for selector in selectores_imagen:
                    try:
                        imagen = self.driver.find_element(By.XPATH, selector)
                        if imagen and imagen.is_displayed():
                            producto['imagen_elemento'] = imagen
                            print("  → Imagen encontrada")
                            break
                    except:
                        continue
                
                if not producto['imagen_elemento']:
                    print("  ⚠️  No se encontró imagen")
                    
            except Exception as e:
                print(f"  ⚠️  Error buscando imagen: {e}")
            
            return producto
            
        except Exception as e:
            print(f"❌ Error extrayendo datos del producto: {e}")
            return None
    
    def capturar_screenshot_imagen(self, elemento, ruta_destino):
        """Captura screenshot optimizado de la imagen"""
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
        """Guarda un producto en la estructura de carpetas"""
        carpeta_articulo = os.path.join(self.carpeta_principal, f"Articulo_{numero_articulo}")
        carpeta_imagenes = os.path.join(carpeta_articulo, "imagenes")
        archivo_datos = os.path.join(carpeta_articulo, "datos.txt")
        
        os.makedirs(carpeta_imagenes, exist_ok=True)
        
        if producto.get('imagen_elemento'):
            ruta_imagen = os.path.join(carpeta_imagenes, "imagen_1.jpg")
            
            if self.capturar_screenshot_imagen(producto['imagen_elemento'], ruta_imagen):
                print(f"    ✓ Imagen guardada correctamente")
            else:
                print(f"    ✗ No se pudo guardar la imagen")
        else:
            print(f"    ⚠️  No se encontró imagen para este producto")
        
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
            
            total_productos = self.contar_productos_catalogo()
            
            productos = self.extraer_productos(cantidad_productos)
            
            print("\n💾 Guardando productos en carpetas...")
            for i, producto in enumerate(productos, 1):
                self.guardar_producto(producto, i)
            
            print("\n" + "="*60)
            print(f"✅ EXTRACCIÓN COMPLETADA - {len(productos)} productos guardados")
            print("="*60 + "\n")
            
            return True
            
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
