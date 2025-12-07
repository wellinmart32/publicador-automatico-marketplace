from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import requests


class ExtractorWhatsApp:
    """Extrae productos del catálogo de WhatsApp Web"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.carpeta_principal = "ArticulosMarketplace"
    
    def iniciar_navegador(self):
        """Inicia Chrome y abre WhatsApp Web"""
        print("🌐 Iniciando Chrome...")
        
        # Configurar opciones para Chrome
        opciones = webdriver.ChromeOptions()
        
        # Usar perfil dedicado para WhatsApp
        ruta_perfil = os.path.join(os.getcwd(), "perfil_whatsapp_extractor")
        opciones.add_argument(f"--user-data-dir={ruta_perfil}")
        
        # Opciones adicionales
        opciones.add_argument("--disable-blink-features=AutomationControlled")
        opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
        opciones.add_experimental_option('useAutomationExtension', False)
        
        # Iniciar driver
        servicio = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=servicio, options=opciones)
        self.wait = WebDriverWait(self.driver, 30)
        
        print("✅ Navegador iniciado")
        
        # Ir a WhatsApp Web
        print("📱 Abriendo WhatsApp Web...")
        self.driver.get("https://web.whatsapp.com")
        
        print("\n⏳ Esperando a que escanees el código QR...")
        print("   (Si ya estás logueado, esto se saltará automáticamente)\n")
    
    def esperar_whatsapp_cargado(self):
        """Espera a que WhatsApp Web esté completamente cargado"""
        try:
            # Esperar a que aparezca la barra de búsqueda (señal de que cargó)
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='3']"))
            )
            print("✅ WhatsApp Web cargado correctamente")
            time.sleep(2)
            return True
        except:
            print("❌ Error: WhatsApp Web no cargó correctamente")
            return False
    
    def buscar_contacto(self, nombre_contacto):
        """Busca un contacto en WhatsApp"""
        print(f"🔍 Buscando contacto: {nombre_contacto}")
        
        try:
            # Buscar el campo de búsqueda
            campo_busqueda = self.driver.find_element(By.XPATH, "//div[@contenteditable='true'][@data-tab='3']")
            campo_busqueda.click()
            time.sleep(0.5)
            
            # Escribir el nombre del contacto
            campo_busqueda.send_keys(nombre_contacto)
            time.sleep(2)
            
            # Hacer clic en el primer resultado
            primer_resultado = self.driver.find_element(By.XPATH, "//div[@role='listitem'][1]")
            primer_resultado.click()
            time.sleep(1.5)
            
            print(f"✅ Contacto '{nombre_contacto}' abierto")
            return True
            
        except Exception as e:
            print(f"❌ Error buscando contacto: {e}")
            return False
    
    def abrir_info_contacto(self):
        """Abre la información del contacto"""
        print("📋 Abriendo información del contacto...")
        
        try:
            # Buscar y hacer clic en el encabezado del chat para abrir info
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
            # Buscar el elemento "Productos" y hacer clic
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
        
        try:
            # Obtener todos los elementos de productos
            items_productos = self.driver.find_elements(By.XPATH, "//div[@role='listitem']")
            
            for i, item in enumerate(items_productos[:cantidad_maxima], 1):
                print(f"📦 Procesando producto {i}/{min(cantidad_maxima, len(items_productos))}...")
                
                try:
                    # Hacer clic en el producto
                    item.click()
                    time.sleep(1.5)
                    
                    # Extraer datos del producto
                    producto = self.extraer_datos_producto()
                    
                    if producto:
                        productos_extraidos.append(producto)
                        print(f"✅ Producto extraído: {producto['titulo']}\n")
                    
                    # Volver al catálogo
                    boton_atras = self.driver.find_element(By.XPATH, "//span[@data-icon='back']")
                    boton_atras.click()
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"⚠️  Error procesando producto {i}: {e}\n")
                    continue
            
            print(f"\n✅ Extracción completada: {len(productos_extraidos)} productos")
            return productos_extraidos
            
        except Exception as e:
            print(f"❌ Error en extracción de productos: {e}")
            return productos_extraidos
    
    def extraer_datos_producto(self):
        """Extrae los datos de un producto individual"""
        try:
            producto = {
                'titulo': '',
                'precio': '',
                'descripcion': '',
                'imagenes': []
            }
            
            # Extraer título
            try:
                titulo = self.driver.find_element(By.XPATH, "//div[@role='heading']").text
                producto['titulo'] = titulo
            except:
                producto['titulo'] = "Sin título"
            
            # Extraer precio
            try:
                precio = self.driver.find_element(By.XPATH, "//span[contains(text(), '$')]").text
                # Limpiar el precio (quitar $ y espacios)
                precio_limpio = precio.replace('$', '').replace(',', '').strip()
                producto['precio'] = precio_limpio
            except:
                producto['precio'] = "0"
            
            # Extraer descripción
            try:
                descripcion = self.driver.find_element(By.XPATH, "//div[@class='_ak72 _ak73']").text
                producto['descripcion'] = descripcion
            except:
                producto['descripcion'] = "Sin descripción"
            
            # Extraer URLs de imágenes
            try:
                imagenes = self.driver.find_elements(By.XPATH, "//img[@draggable='false']")
                for img in imagenes[:10]:  # Máximo 10 imágenes
                    url = img.get_attribute('src')
                    if url and url.startswith('http'):
                        producto['imagenes'].append(url)
            except:
                pass
            
            return producto
            
        except Exception as e:
            print(f"❌ Error extrayendo datos del producto: {e}")
            return None
    
    def descargar_imagen(self, url, ruta_destino):
        """Descarga una imagen desde una URL"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open(ruta_destino, 'wb') as f:
                    f.write(response.content)
                return True
        except:
            pass
        return False
    
    def guardar_producto(self, producto, numero_articulo):
        """Guarda un producto en la estructura de carpetas"""
        carpeta_articulo = os.path.join(self.carpeta_principal, f"Articulo_{numero_articulo}")
        carpeta_imagenes = os.path.join(carpeta_articulo, "imagenes")
        archivo_datos = os.path.join(carpeta_articulo, "datos.txt")
        
        # Asegurar que existen las carpetas
        os.makedirs(carpeta_imagenes, exist_ok=True)
        
        # Guardar imágenes
        print(f"  📸 Descargando {len(producto['imagenes'])} imágenes...")
        for idx, url_imagen in enumerate(producto['imagenes'], 1):
            nombre_imagen = f"imagen_{idx}.jpg"
            ruta_imagen = os.path.join(carpeta_imagenes, nombre_imagen)
            
            if self.descargar_imagen(url_imagen, ruta_imagen):
                print(f"    ✓ Imagen {idx} descargada")
            else:
                print(f"    ✗ Error descargando imagen {idx}")
        
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
            # Iniciar navegador
            self.iniciar_navegador()
            
            # Esperar a que WhatsApp cargue
            if not self.esperar_whatsapp_cargado():
                return False
            
            # Buscar contacto
            if not self.buscar_contacto(nombre_contacto):
                return False
            
            # Abrir información del contacto
            if not self.abrir_info_contacto():
                return False
            
            # Ir al catálogo
            if not self.ir_a_catalogo():
                return False
            
            # Contar productos
            total_productos = self.contar_productos_catalogo()
            
            # Extraer productos
            productos = self.extraer_productos(cantidad_productos)
            
            # Guardar productos
            print("\n💾 Guardando productos en carpetas...")
            for i, producto in enumerate(productos, 1):
                self.guardar_producto(producto, i)
            
            print("\n" + "="*60)
            print(f"✅ EXTRACCIÓN COMPLETADA - {len(productos)} productos guardados")
            print("="*60 + "\n")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error durante la extracción: {e}")
            return False
        
        finally:
            print("\n⏳ Cerrando navegador en 5 segundos...")
            time.sleep(5)
            if self.driver:
                self.driver.quit()
