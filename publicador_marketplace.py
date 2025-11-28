from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time
import os

class PublicadorMarketplace:
    """Maneja la automatización de publicaciones en Facebook Marketplace"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
    
    def iniciar_navegador(self):
        """Inicia Opera con la sesión actual de Facebook"""
        print("🌐 Iniciando Opera...")
        
        # Ruta de Opera One en Windows
        ruta_opera = r"C:\Users\welli\AppData\Local\Programs\Opera\opera.exe"
        
        # Ruta del driver de Opera (descarga manual necesaria)
        ruta_driver = r"C:\Users\welli\OneDrive\Documents\Repositorios\publicador-automatico-marketplace\drivers\operadriver.exe"
        
        # Configurar opciones para Opera
        opciones = webdriver.ChromeOptions()
        opciones.binary_location = ruta_opera
        
        # Usar perfil existente para mantener sesión de Facebook
        ruta_perfil = r"C:\Users\welli\AppData\Roaming\Opera Software\Opera Stable"
        opciones.add_argument(f"--user-data-dir={ruta_perfil}")
        
        # Crear directorio temporal para evitar conflictos
        opciones.add_argument("--remote-debugging-port=9222")
        
        # Opciones adicionales
        opciones.add_argument("--disable-blink-features=AutomationControlled")
        opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
        opciones.add_experimental_option('useAutomationExtension', False)
        
        # Verificar que existe el driver
        if not os.path.exists(ruta_driver):
            print(f"❌ No se encontró el driver en: {ruta_driver}")
            print("\n📥 Descarga el OperaDriver desde:")
            print("https://github.com/operasoftware/operachromiumdriver/releases")
            print("Busca la versión 140.x y extrae operadriver.exe en la carpeta 'drivers'")
            return False
        
        # Iniciar driver
        try:
            servicio = Service(ruta_driver)
            self.driver = webdriver.Chrome(service=servicio, options=opciones)
            self.wait = WebDriverWait(self.driver, 20)
            print("✅ Navegador iniciado")
            return True
        except Exception as e:
            print(f"❌ Error al iniciar navegador: {e}")
            return False
    
    def ir_a_marketplace(self):
        """Navega a la página de creación de publicación en Marketplace"""
        print("📍 Navegando a Marketplace...")
        url = "https://www.facebook.com/marketplace/create/item"
        self.driver.get(url)
        time.sleep(3)
        print("✅ En página de creación")
    
    def cerrar_navegador(self):
        """Cierra el navegador"""
        if self.driver:
            print("🔒 Cerrando navegador...")
            self.driver.quit()
            print("✅ Navegador cerrado")


# Prueba básica
if __name__ == "__main__":
    publicador = PublicadorMarketplace()
    
    try:
        if publicador.iniciar_navegador():
            publicador.ir_a_marketplace()
            
            print("\n⏳ Esperando 10 segundos para que veas la página...")
            time.sleep(10)
        
    except Exception as error:
        print(f"❌ Error: {error}")
    
    finally:
        publicador.cerrar_navegador()
