from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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
        time.sleep(1.5)
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
            
            time.sleep(1)
            print("✅ Imágenes subidas")
            return True
        except Exception as e:
            print(f"❌ Error subiendo imágenes: {e}")
            return False
    
    def llenar_titulo(self, titulo):
        """Llena el campo de título"""
        print(f"✍️  Título: {titulo}")
        try:
            # Buscar input con dir="ltr" dentro del label que contiene "Título"
            campo = self.driver.find_element(By.XPATH, "//span[text()='Título']/../..//input[@dir='ltr']")
            campo.clear()
            campo.send_keys(titulo)
            time.sleep(0.3)
            print("✅ Título ingresado")
            return True
        except Exception as e:
            print(f"❌ Error en título: {e}")
        return False
    
    def llenar_precio(self, precio):
        """Llena el campo de precio"""
        print(f"💰 Precio: ${precio}")
        try:
            # Buscar input con dir="ltr" dentro del label que contiene "Precio"
            campo = self.driver.find_element(By.XPATH, "//span[text()='Precio']/../..//input[@dir='ltr']")
            campo.clear()
            campo.send_keys(str(precio))
            time.sleep(0.3)
            print("✅ Precio ingresado")
            return True
        except Exception as e:
            print(f"❌ Error en precio: {e}")
        return False
    
    def seleccionar_categoria(self, categoria):
        """Selecciona la categoría del desplegable"""
        print(f"📁 Categoría: {categoria}")
        try:
            # Hacer clic en el label de categoría
            label_categoria = self.driver.find_element(By.XPATH, "//span[text()='Categoría']/../..")
            label_categoria.click()
            time.sleep(0.8)
            
            # Buscar y hacer clic en la opción
            opcion = self.driver.find_element(By.XPATH, f"//span[contains(text(), '{categoria}')]")
            opcion.click()
            time.sleep(0.3)
            print("✅ Categoría seleccionada")
            return True
        except Exception as e:
            print(f"❌ Error en categoría: {e}")
        return False
    
    def seleccionar_estado(self, estado):
        """Selecciona el estado del artículo"""
        print(f"🏷️  Estado: {estado}")
        try:
            # Hacer clic en el label de estado
            label_estado = self.driver.find_element(By.XPATH, "//span[text()='Estado']/../..")
            label_estado.click()
            time.sleep(0.8)
            
            # Buscar y hacer clic en la opción
            opcion = self.driver.find_element(By.XPATH, f"//span[text()='{estado}']")
            opcion.click()
            time.sleep(0.3)
            print("✅ Estado seleccionado")
            return True
        except Exception as e:
            print(f"❌ Error en estado: {e}")
        return False
    
    def llenar_descripcion(self, descripcion):
        """Llena el campo de descripción"""
        print(f"📝 Accediendo a descripción...")
        try:
            # Buscar específicamente el textarea de descripción
            campo_descripcion = self.driver.find_element(By.XPATH, "//textarea[@dir='ltr']")
            
            # Hacer scroll hasta el campo
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", campo_descripcion)
            time.sleep(0.8)
            
            # Hacer clic en el campo
            campo_descripcion.click()
            time.sleep(0.3)
            
            # Llenar descripción
            print(f"📝 Llenando descripción: {descripcion[:50]}...")
            campo_descripcion.clear()
            campo_descripcion.send_keys(descripcion)
            time.sleep(0.3)
            print("✅ Descripción ingresada")
            return True
            
        except Exception as e:
            print(f"❌ Error en descripción: {e}")
        return False
    
    def llenar_etiquetas(self, etiquetas):
        """Llena el campo de etiquetas de producto"""
        if not etiquetas or etiquetas.strip() == "":
            print("⏭️  Sin etiquetas, omitiendo...")
            return True
            
        print(f"🏷️  Intentando llenar etiquetas: {etiquetas}")
        try:
            # Hacer scroll para asegurar que el campo esté visible
            time.sleep(0.5)
            
            # Buscar el input que esté después del texto "Etiquetas de producto"
            campo_etiquetas = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Etiquetas de producto')]/ancestor::div[contains(@class, 'x78zum5')]//input[@dir='ltr']")
            
            # Hacer scroll y clic
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", campo_etiquetas)
            time.sleep(0.5)
            campo_etiquetas.click()
            time.sleep(0.3)
            
            # Dividir etiquetas por comas y agregarlas una por una
            lista_etiquetas = [e.strip() for e in etiquetas.split(',') if e.strip()]
            
            for etiqueta in lista_etiquetas:
                campo_etiquetas.send_keys(etiqueta)
                time.sleep(0.3)
                # Simular Enter para agregar la etiqueta
                campo_etiquetas.send_keys(Keys.RETURN)
                time.sleep(0.3)
            
            print(f"✅ {len(lista_etiquetas)} etiqueta(s) agregada(s)")
            return True
                    
        except Exception as e:
            print(f"⚠️  No se pudieron agregar etiquetas: {e}")
        return False
    
    def llenar_sku(self, sku):
        """Llena el campo SKU"""
        if not sku or sku.strip() == "":
            print("⏭️  Sin SKU, omitiendo...")
            return True
            
        print(f"🔢 SKU: {sku}")
        try:
            # Buscar el input que esté después del texto "SKU"
            campo_sku = self.driver.find_element(By.XPATH, "//span[contains(text(), 'SKU')]/ancestor::div[contains(@class, 'x78zum5')]//input[@dir='ltr']")
            
            campo_sku.click()
            time.sleep(0.3)
            campo_sku.clear()
            campo_sku.send_keys(sku)
            time.sleep(0.3)
            print("✅ SKU ingresado")
            return True
                    
        except Exception as e:
            print(f"⚠️  No se pudo agregar SKU: {e}")
        return False
    
    def configurar_disponibilidad(self, disponibilidad, encuentro_publico):
        """Configura disponibilidad y encuentro en lugar público"""
        # Omitir disponibilidad ya que Facebook la pone por defecto
        # print(f"📦 Disponibilidad: {disponibilidad}")
        
        try:
            # Marcar encuentro en lugar público
            if encuentro_publico.lower() == "si":
                print("✅ Marcando encuentro en lugar público")
                try:
                    # Buscar el checkbox directamente
                    checkbox = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Encuentro en un lugar público')]/..//input[@type='checkbox']")
                    if not checkbox.is_selected():
                        checkbox.click()
                        time.sleep(0.3)
                except:
                    # Intentar hacer clic en el label/contenedor
                    try:
                        contenedor = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Encuentro en un lugar público')]/ancestor::div[@role='button']")
                        contenedor.click()
                        time.sleep(0.3)
                    except:
                        print("⚠️  No se pudo marcar encuentro público")
            
            return True
        except Exception as e:
            print(f"❌ Error configurando preferencias: {e}")
        return False
    
    def publicar_articulo(self):
        """Hace clic en el botón Siguiente/Publicar"""
        print("🚀 Publicando artículo...")
        try:
            # Buscar el botón "Siguiente" por el texto
            boton_siguiente = self.driver.find_element(By.XPATH, "//span[text()='Siguiente']")
            
            # Hacer scroll hasta el botón para asegurarnos que sea visible
            self.driver.execute_script("arguments[0].scrollIntoView(true);", boton_siguiente)
            time.sleep(0.5)
            
            # Hacer clic
            boton_siguiente.click()
            time.sleep(1.5)
            
            print("✅ Clic en 'Siguiente' exitoso")
            
            # Esperar a que aparezca confirmación o la siguiente pantalla
            time.sleep(1)
            
            # Verificar si llegamos a la página de confirmación o si hay otro paso
            try:
                # Buscar si hay un botón "Publicar" final
                boton_publicar = self.driver.find_element(By.XPATH, "//span[text()='Publicar']")
                if boton_publicar:
                    print("📌 Encontrado botón 'Publicar', haciendo clic...")
                    boton_publicar.click()
                    time.sleep(1)
            except:
                # No hay botón "Publicar", significa que ya se publicó con "Siguiente"
                pass
            
            print("✅ Artículo publicado exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error al publicar: {e}")
            
            # Intentar tomar screenshot para debug
            try:
                self.driver.save_screenshot("error_publicacion.png")
                print("📸 Screenshot guardado en error_publicacion.png")
            except:
                pass
                
        return False
    
    def publicar_producto_completo(self, datos, imagenes):
        """Publica un producto completo en Marketplace"""
        print("\n" + "="*50)
        print("🎯 INICIANDO PUBLICACIÓN")
        print("="*50 + "\n")
        
        # Ir a marketplace
        self.ir_a_marketplace()
        time.sleep(1.5)
        
        # Subir imágenes
        if not self.subir_imagenes(imagenes):
            print("❌ Fallo crítico: No se pudieron subir imágenes")
            return False
        
        time.sleep(1)
        
        # Llenar campos obligatorios
        self.llenar_titulo(datos.get('titulo', ''))
        self.llenar_precio(datos.get('precio', '0'))
        self.seleccionar_categoria(datos.get('categoria', 'Electrónica e informática'))
        self.seleccionar_estado(datos.get('estado', 'Nuevo'))
        
        # Llenar descripción
        self.llenar_descripcion(datos.get('descripcion', ''))
        
        # Llenar etiquetas
        self.llenar_etiquetas(datos.get('etiquetas', ''))
        
        # Llenar SKU
        self.llenar_sku(datos.get('sku', ''))
        
        # Configurar disponibilidad
        self.configurar_disponibilidad(
            datos.get('disponibilidad', 'Publicar como disponible'),
            datos.get('encuentro_publico', 'Si')
        )
        
        # Esperar un momento antes de publicar
        print("\n⏳ Esperando 1 segundo antes de publicar...")
        time.sleep(1)
        
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
