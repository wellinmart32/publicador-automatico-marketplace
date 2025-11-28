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
        publicador.iniciar_navegador()
        publicador.ir_a_marketplace()
        
        print("\n⏳ Esperando 30 segundos...")
        print("👉 Si no estás logueado, inicia sesión en Facebook ahora")
        time.sleep(30)
        
    except Exception as error:
        print(f"❌ Error: {error}")
    
    finally:
        publicador.cerrar_navegador()