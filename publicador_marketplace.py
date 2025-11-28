from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

class PublicadorMarketplace:
    """Maneja la automatización de publicaciones en Facebook Marketplace"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
    
    def iniciar_navegador(self):
        """Inicia Chrome con perfil dedicado para el bot"""
        print("🌐 Iniciando Chrome...")
        
        # Configurar opciones para Chrome
        opciones = webdriver.ChromeOptions()
        
        # Usar perfil dedicado para el bot (se creará automáticamente)
        ruta_perfil_bot = os.path.join(os.getcwd(), "perfil_bot_marketplace")
        opciones.add_argument(f"--user-data-dir={ruta_perfil_bot}")
        
        # Opciones adicionales
        opciones.add_argument("--disable-blink-features=AutomationControlled")
        opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
        opciones.add_experimental_option('useAutomationExtension', False)
        
        # Iniciar driver
        servicio = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=servicio, options=opciones)
        self.wait = WebDriverWait(self.driver, 20)
        
        print("✅ Navegador iniciado")
    
    def ir_a_marketplace(self):
        """Navega a la página de creación de publicación en Marketplace"""
        print("📍 Navegando a Marketplace...")
        url = "https://www.facebook.com/marketplace/create/item"
        self.driver.get(url)
        time.sleep(3)
        print("✅ En página de creación")
    
    def esperar_elemento(self, selector, tipo=By.CSS_SELECTOR, tiempo=20):
        """Espera a que un elemento esté presente y visible"""
        try:
            elemento = WebDriverWait(self.driver, tiempo).until(
                EC.presence_of_element_located((tipo, selector))
            )
            return elemento
        except:
            return None
    
    def subir_imagenes(self, rutas_imagenes):
        """Sube las imágenes del artículo"""
        if not rutas_imagenes:
            print("⚠️  No hay imágenes para subir")
            return False
        
        print(f"📸 Subiendo {len(rutas_imagenes)} imágenes...")
        
        try:
            # Buscar el input de archivos (está oculto)
            input_archivo = self.driver.find_element(By.CSS_SELECTOR, "input[type='file'][accept*='image']")
            
            # Subir todas las imágenes a la vez (separadas por \n)
            rutas_concatenadas = "\n".join(rutas_imagenes)
            input_archivo.send_keys(rutas_concatenadas)
            
            time.sleep(2)
            print("✅ Imágenes subidas")
            return True
        except Exception as e:
            print(f"❌ Error subiendo imágenes: {e}")
            return False
    
    def llenar_titulo(self, titulo):
        """Llena el campo de título"""
        print(f"✍️  Título: {titulo}")
        try:
            # Intentar varios selectores posibles
            selectores = [
                "input[aria-label='Título']",
                "input[placeholder='Título']",
                "//label[contains(text(), 'Título')]//following::input[1]"
            ]
            
            for selector in selectores:
                try:
                    if selector.startswith("//"):
                        campo = self.driver.find_element(By.XPATH, selector)
                    else:
                        campo = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if campo:
                        campo.clear()
                        campo.send_keys(titulo)
                        time.sleep(0.5)
                        print("✅ Título ingresado")
                        return True
                except:
                    continue
        except Exception as e:
            print(f"❌ Error en título: {e}")
        return False
    
    def llenar_precio(self, precio):
        """Llena el campo de precio"""
        print(f"💰 Precio: ${precio}")
        try:
            # Intentar varios selectores posibles
            selectores = [
                "input[aria-label='Precio']",
                "input[placeholder='Precio']",
                "//label[contains(text(), 'Precio')]//following::input[1]"
            ]
            
            for selector in selectores:
                try:
                    if selector.startswith("//"):
                        campo = self.driver.find_element(By.XPATH, selector)
                    else:
                        campo = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if campo:
                        campo.clear()
                        campo.send_keys(str(precio))
                        time.sleep(0.5)
                        print("✅ Precio ingresado")
                        return True
                except:
                    continue
        except Exception as e:
            print(f"❌ Error en precio: {e}")
        return False
    
    def seleccionar_categoria(self, categoria):
        """Selecciona la categoría del desplegable"""
        print(f"📁 Categoría: {categoria}")
        try:
            # Buscar el div que contiene "Categoría"
            desplegable = self.driver.find_element(By.XPATH, "//label[contains(text(), 'Categoría')]//following-sibling::div[1]")
            desplegable.click()
            time.sleep(1.5)
            
            # Buscar la opción específica
            opcion = self.driver.find_element(By.XPATH, f"//span[contains(text(), '{categoria}')]")
            opcion.click()
            time.sleep(0.5)
            print("✅ Categoría seleccionada")
            return True
        except Exception as e:
            print(f"❌ Error en categoría: {e}")
            # Intentar cerrar el desplegable si quedó abierto
            try:
                self.driver.find_element(By.TAG_NAME, "body").click()
            except:
                pass
        return False
    
    def seleccionar_estado(self, estado):
        """Selecciona el estado del artículo"""
        print(f"🏷️  Estado: {estado}")
        try:
            # Buscar el div que contiene "Estado"
            desplegable = self.driver.find_element(By.XPATH, "//label[contains(text(), 'Estado')]//following-sibling::div[1]")
            desplegable.click()
            time.sleep(1.5)
            
            # Buscar la opción específica
            opcion = self.driver.find_element(By.XPATH, f"//span[text()='{estado}']")
            opcion.click()
            time.sleep(0.5)
            print("✅ Estado seleccionado")
            return True
        except Exception as e:
            print(f"❌ Error en estado: {e}")
            # Intentar cerrar el desplegable si quedó abierto
            try:
                self.driver.find_element(By.TAG_NAME, "body").click()
            except:
                pass
        return False
    
    def llenar_descripcion(self, descripcion):
        """Llena el campo de descripción"""
        print(f"📝 Descripción: {descripcion[:50]}...")
        try:
            # Expandir "Más detalles" si está colapsado
            try:
                boton_mas_detalles = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Más detalles')]")
                if boton_mas_detalles:
                    boton_mas_detalles.click()
                    time.sleep(1)
            except:
                pass
            
            # Llenar descripción
            campo_descripcion = self.esperar_elemento("textarea[placeholder*='Descripción']")
            if campo_descripcion:
                campo_descripcion.clear()
                campo_descripcion.send_keys(descripcion)
                time.sleep(0.5)
                return True
        except Exception as e:
            print(f"❌ Error en descripción: {e}")
        return False
    
    def configurar_disponibilidad(self, disponibilidad, encuentro_publico):
        """Configura disponibilidad y encuentro en lugar público"""
        print(f"📦 Disponibilidad: {disponibilidad}")
        try:
            # Seleccionar disponibilidad
            if disponibilidad == "Publicar como disponible":
                # Buscar el desplegable de disponibilidad
                desplegable_disp = self.esperar_elemento("label[aria-label*='Disponibilidad'] + div")
                if desplegable_disp:
                    desplegable_disp.click()
                    time.sleep(1)
                    
                    # Seleccionar "Publicar como disponible"
                    opciones = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Publicar como disponible')]")
                    for opcion in opciones:
                        if opcion.is_displayed():
                            opcion.click()
                            time.sleep(0.5)
                            break
            
            # Marcar encuentro en lugar público
            if encuentro_publico.lower() == "si":
                print("✅ Marcando encuentro en lugar público")
                try:
                    checkbox = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Encuentro en un lugar público')]/..//input[@type='checkbox']")
                    if not checkbox.is_selected():
                        checkbox.click()
                        time.sleep(0.5)
                except:
                    # Intentar hacer clic en el label
                    try:
                        label = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Encuentro en un lugar público')]")
                        label.click()
                        time.sleep(0.5)
                    except:
                        pass
            
            return True
        except Exception as e:
            print(f"❌ Error en disponibilidad: {e}")
        return False
    
    def publicar_articulo(self):
        """Hace clic en el botón Siguiente/Publicar"""
        print("🚀 Publicando artículo...")
        try:
            # Buscar botón "Siguiente"
            boton_siguiente = self.esperar_elemento("div[aria-label='Siguiente']", tiempo=5)
            if boton_siguiente:
                boton_siguiente.click()
                time.sleep(2)
                print("✅ Artículo publicado exitosamente")
                return True
            else:
                print("⚠️  No se encontró el botón 'Siguiente'")
        except Exception as e:
            print(f"❌ Error al publicar: {e}")
        return False
    
    def publicar_producto_completo(self, datos, imagenes):
        """Publica un producto completo en Marketplace"""
        print("\n" + "="*50)
        print("🎯 INICIANDO PUBLICACIÓN")
        print("="*50 + "\n")
        
        # Ir a marketplace
        self.ir_a_marketplace()
        time.sleep(3)
        
        # Subir imágenes
        if not self.subir_imagenes(imagenes):
            print("❌ Fallo crítico: No se pudieron subir imágenes")
            return False
        
        time.sleep(2)
        
        # Llenar campos obligatorios
        self.llenar_titulo(datos.get('titulo', ''))
        self.llenar_precio(datos.get('precio', '0'))
        self.seleccionar_categoria(datos.get('categoria', 'Electrónica e informática'))
        self.seleccionar_estado(datos.get('estado', 'Nuevo'))
        
        # Llenar descripción
        self.llenar_descripcion(datos.get('descripcion', ''))
        
        # Configurar disponibilidad
        self.configurar_disponibilidad(
            datos.get('disponibilidad', 'Publicar como disponible'),
            datos.get('encuentro_publico', 'Si')
        )
        
        # Esperar un momento antes de publicar
        print("\n⏳ Esperando 3 segundos antes de publicar...")
        time.sleep(3)
        
        # Publicar
        exito = self.publicar_articulo()
        
        if exito:
            print("\n" + "="*50)
            print("✅ PUBLICACIÓN COMPLETADA")
            print("="*50 + "\n")
        
        return exito
    
    def cerrar_navegador(self):
        """Cierra el navegador"""
        if self.driver:
            print("🔒 Cerrando navegador...")
            self.driver.quit()
            print("✅ Navegador cerrado")
