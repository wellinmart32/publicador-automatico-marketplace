from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
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
            time.sleep(2)
            
            print("✅ Catálogo abierto")
            return True
            
        except Exception as e:
            print(f"❌ Error abriendo catálogo: {e}")
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
    
    def extraer_productos(self, cantidad_maxima=5):
        """Extrae los datos de los productos del catálogo"""
        print(f"\n🎯 Iniciando extracción de hasta {cantidad_maxima} productos...\n")
        
        productos_extraidos = []
        
        for intento_producto in range(cantidad_maxima):
            print(f"📦 Procesando producto {intento_producto + 1}/{cantidad_maxima}...")
            
            try:
                time.sleep(2.5)
                
                items_productos = self.driver.find_elements(By.XPATH, "//div[@role='listitem']")
                
                if intento_producto >= len(items_productos):
                    print(f"  ⚠️  Solo hay {len(items_productos)} productos en esta vista")
                    break
                
                # Scroll y clic
                producto_actual = items_productos[intento_producto]
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", producto_actual)
                time.sleep(1.5)
                
                producto_actual.click()
                time.sleep(4)  # Esperar más tiempo a que cargue completamente
                
                # Extraer datos
                producto = self.extraer_datos_producto()
                
                if producto:
                    productos_extraidos.append(producto)
                    print(f"✅ Producto extraído: {producto['titulo']}\n")
                
                # Volver
                self.volver_a_catalogo()
                time.sleep(3.5)  # Esperar más antes del siguiente
                
            except StaleElementReferenceException:
                print(f"  ⚠️  Elemento obsoleto, continuando...\n")
                time.sleep(2)
                continue
                
            except Exception as e:
                print(f"  ⚠️  Error procesando producto {intento_producto + 1}: {e}\n")
                try:
                    self.volver_a_catalogo()
                    time.sleep(2)
                except:
                    pass
                continue
        
        print(f"\n✅ Extracción completada: {len(productos_extraidos)} productos")
        return productos_extraidos
    
    def volver_a_catalogo(self):
        """Vuelve al catálogo de productos"""
        try:
            print("  ← Volviendo al catálogo...")
            
            # Método 1: Buscar el primer botón del header
            botones_header = self.driver.find_elements(By.XPATH, "//header//button")
            
            if botones_header:
                botones_header[0].click()
                time.sleep(2)
                return True
            else:
                # Método 2: ESC
                from selenium.webdriver.common.keys import Keys
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                time.sleep(2)
                return True
                
        except Exception as e:
            print(f"  ⚠️  Error al volver: {e}")
            return False
    
    def extraer_datos_producto(self):
        """Extrae los datos de un producto - VERSIÓN MEJORADA"""
        try:
            producto = {
                'titulo': '',
                'precio': '',
                'descripcion': '',
                'imagen_elemento': None
            }
            
            # Esperar a que cargue completamente
            time.sleep(3)
            
            # EXTRAER TÍTULO - Solo del área principal de detalles
            try:
                # Buscar específicamente en el contenedor de detalles del producto
                # Evitar el nombre del contacto
                titulos_posibles = self.driver.find_elements(By.XPATH, 
                    "//div[contains(@class, 'x1okw0bk')]//span[contains(@class, 'selectable-text')]"
                )
                
                for titulo_elem in titulos_posibles[:8]:
                    try:
                        if not titulo_elem.is_displayed():
                            continue
                        
                        texto = titulo_elem.text.strip()
                        
                        # Validaciones estrictas
                        if (texto and 
                            8 < len(texto) < 70 and 
                            '$' not in texto and 
                            '○' not in texto and 
                            '◯' not in texto and
                            'Marca:' not in texto and
                            'Modelo:' not in texto and
                            'Color:' not in texto and
                            'Trabajo' not in texto and  # Evitar nombre del contacto
                            'John' not in texto and
                            'Detalles' not in texto and
                            'Catálogo' not in texto and
                            'TECLADOS' not in texto and
                            'MOUSES' not in texto):
                            
                            producto['titulo'] = texto
                            print(f"  → Título encontrado: {texto}")
                            break
                    except:
                        continue
                
                if not producto['titulo']:
                    producto['titulo'] = "Sin título"
                    
            except Exception as e:
                print(f"  ⚠️  Error extrayendo título")
                producto['titulo'] = "Sin título"
            
            # EXTRAER PRECIO
            try:
                precios = self.driver.find_elements(By.XPATH, 
                    "//*[starts-with(text(), '$') and string-length(text()) < 15]"
                )
                
                for precio_elem in precios[:3]:
                    try:
                        if precio_elem.is_displayed():
                            precio_texto = precio_elem.text.strip()
                            # Tomar solo el primer precio (puede haber precio tachado)
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
            
            # HACER CLIC EN "Leer más"
            try:
                leer_mas = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Leer más')]")
                if leer_mas.is_displayed():
                    leer_mas.click()
                    time.sleep(2)
                    print("  → Expandiendo descripción...")
            except:
                pass
            
            # EXTRAER DESCRIPCIÓN - Solo elementos visibles en el área de detalles
            try:
                detalles = []
                
                # Buscar SOLO en el área de detalles visible
                contenedor_detalles = self.driver.find_element(By.XPATH, 
                    "//div[contains(@class, 'x1okw0bk')]"
                )
                
                elementos_detalles = contenedor_detalles.find_elements(By.XPATH, 
                    ".//*[contains(text(), '○') or contains(text(), '◯') or contains(text(), 'Marca:')]"
                )
                
                textos_unicos = set()
                
                for detalle_elem in elementos_detalles[:15]:
                    try:
                        # Verificar que el elemento esté en el viewport
                        location = detalle_elem.location
                        size = detalle_elem.size
                        
                        # Solo elementos que realmente están visibles
                        if location['y'] > 0 and size['height'] > 0:
                            texto = detalle_elem.text.strip()
                            
                            if texto and 5 < len(texto) < 200:
                                # Tomar solo la primera línea si hay múltiples
                                primera_linea = texto.split('\n')[0].strip()
                                
                                if (primera_linea and 
                                    primera_linea not in textos_unicos and
                                    len(detalles) < 10):
                                    
                                    detalles.append(primera_linea)
                                    textos_unicos.add(primera_linea)
                        
                        if len(detalles) >= 10:
                            break
                            
                    except:
                        continue
                
                if detalles:
                    producto['descripcion'] = ' | '.join(detalles)
                    print(f"  → Descripción: {len(detalles)} detalles capturados")
                else:
                    producto['descripcion'] = "Sin descripción"
                    
            except Exception as e:
                print(f"  ⚠️  Error extrayendo descripción")
                producto['descripcion'] = "Sin descripción"
            
            # CAPTURAR ELEMENTO DE IMAGEN para screenshot
            try:
                # Esperar a que la imagen termine de cargar
                time.sleep(2)
                
                # Buscar la imagen principal
                imagen = self.driver.find_element(By.XPATH, 
                    "//img[@class='_ak9n' or (contains(@class, '_ak9n') and @draggable='false')]"
                )
                
                if imagen and imagen.is_displayed():
                    producto['imagen_elemento'] = imagen
                    print("  → Imagen encontrada")
                else:
                    print("  ⚠️  Imagen no visible")
                    
            except Exception as e:
                print(f"  ⚠️  No se encontró imagen")
            
            return producto
            
        except Exception as e:
            print(f"❌ Error extrayendo datos del producto: {e}")
            return None
    
    def capturar_screenshot_imagen(self, elemento, ruta_destino):
        """Captura screenshot optimizado de la imagen del producto"""
        try:
            print(f"  📸 Capturando imagen...")
            
            # Hacer scroll al elemento y esperar
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", 
                elemento
            )
            time.sleep(1.5)
            
            # Obtener posición y tamaño
            location = elemento.location
            size = elemento.size
            
            # Tomar screenshot completo de la ventana
            screenshot = self.driver.get_screenshot_as_png()
            img = Image.open(BytesIO(screenshot))
            
            # Calcular coordenadas con margen generoso
            margen = 50
            left = max(0, location['x'] - margen)
            top = max(0, location['y'] - margen)
            right = min(img.width, location['x'] + size['width'] + margen)
            bottom = min(img.height, location['y'] + size['height'] + margen)
            
            # Verificar que las coordenadas sean válidas
            if right > left and bottom > top:
                imagen_recortada = img.crop((left, top, right, bottom))
                imagen_recortada.save(ruta_destino, 'JPEG', quality=95)
                return True
            else:
                print(f"      Coordenadas inválidas")
                return False
                
        except Exception as e:
            print(f"      Error capturando: {e}")
            return False
    
    def guardar_producto(self, producto, numero_articulo):
        """Guarda un producto en la estructura de carpetas"""
        carpeta_articulo = os.path.join(self.carpeta_principal, f"Articulo_{numero_articulo}")
        carpeta_imagenes = os.path.join(carpeta_articulo, "imagenes")
        archivo_datos = os.path.join(carpeta_articulo, "datos.txt")
        
        os.makedirs(carpeta_imagenes, exist_ok=True)
        
        # Guardar imagen mediante screenshot
        if producto.get('imagen_elemento'):
            ruta_imagen = os.path.join(carpeta_imagenes, "imagen_1.jpg")
            
            if self.capturar_screenshot_imagen(producto['imagen_elemento'], ruta_imagen):
                print(f"    ✓ Imagen guardada correctamente")
            else:
                print(f"    ✗ No se pudo guardar la imagen")
        else:
            print(f"    ⚠️  No se encontró imagen para este producto")
        
        # Guardar datos.txt
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
        print("🚀 EXTRACTOR DE CATÁLOGO DE WHATSAPP")
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
