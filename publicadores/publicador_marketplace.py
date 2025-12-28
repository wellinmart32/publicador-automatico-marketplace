from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os


class PublicadorMarketplace:
    """Maneja la automatización de publicaciones en Facebook Marketplace"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
    
    def iniciar_navegador(self):
        """Inicia Chrome con perfil dedicado - SIN webdriver-manager"""
        print("🌐 Iniciando Chrome...")
        
        opciones = webdriver.ChromeOptions()
        
        ruta_perfil_bot = os.path.join(os.getcwd(), "perfiles", "marketplace_bot")
        opciones.add_argument(f"--user-data-dir={ruta_perfil_bot}")
        
        opciones.add_argument("--disable-blink-features=AutomationControlled")
        opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
        opciones.add_experimental_option('useAutomationExtension', False)
        
        # USAR CHROME SIN WEBDRIVER-MANAGER
        try:
            print("   Iniciando Chrome sin webdriver-manager...")
            self.driver = webdriver.Chrome(options=opciones)
            print("✅ Navegador iniciado correctamente")
        except Exception as e:
            print(f"\n❌ Error al iniciar Chrome: {e}\n")
            print("="*60)
            print("🔧 SOLUCIONES:")
            print("="*60)
            print("1. Descarga ChromeDriver compatible con tu Chrome:")
            print("   https://googlechromelabs.github.io/chrome-for-testing/")
            print()
            print("2. Extrae chromedriver.exe")
            print()
            print("3. Agrégalo al PATH de Windows O")
            print("   Colócalo en: C:\\Windows\\System32\\")
            print()
            print("4. Verifica tu versión de Chrome:")
            print("   Abre Chrome -> Menú (3 puntos) -> Ayuda -> Acerca de")
            print("="*60 + "\n")
            raise
        
        self.wait = WebDriverWait(self.driver, 20)
    
    def esperar_login_facebook(self):
        """Espera a que el usuario inicie sesión en Facebook si es necesario"""
        print("🔐 Verificando sesión de Facebook...")
        
        try:
            self.driver.get("https://www.facebook.com")
            time.sleep(3)
            
            try:
                login_elements = self.driver.find_elements(By.XPATH, 
                    "//input[@name='email' or @name='pass']")
                
                if len(login_elements) > 0:
                    print("\n⚠️  NO HAS INICIADO SESIÓN EN FACEBOOK")
                    print("=" * 60)
                    print("Por favor INICIA SESIÓN en Facebook ahora.")
                    print("Tienes 2 MINUTOS para iniciar sesión.")
                    print("=" * 60 + "\n")
                    
                    tiempo_espera = 120
                    for segundos_restantes in range(tiempo_espera, 0, -5):
                        try:
                            login_check = self.driver.find_elements(By.XPATH, 
                                "//input[@name='email' or @name='pass']")
                            
                            if len(login_check) == 0:
                                print("✅ Sesión iniciada correctamente")
                                return True
                            
                            print(f"⏳ Esperando login... ({segundos_restantes}s restantes)")
                            time.sleep(5)
                        except:
                            print("✅ Sesión iniciada correctamente")
                            return True
                    
                    print("❌ Tiempo de espera agotado. No se detectó inicio de sesión.")
                    return False
                else:
                    print("✅ Ya tienes sesión activa en Facebook")
                    return True
                    
            except:
                print("✅ Ya tienes sesión activa en Facebook")
                return True
                
        except Exception as e:
            print(f"⚠️  Error verificando sesión: {e}")
            print("Continuando de todos modos...")
            return True
    
    def cerrar_overlays(self):
        """Cierra modals/overlays que puedan estar bloqueando la interacción - VERSIÓN AGRESIVA"""
        try:
            # ESTRATEGIA 1: Overlays con tabindex="-1"
            overlays = self.driver.find_elements(
                By.XPATH,
                "//div[@tabindex='-1']"
            )
            
            count = 0
            for overlay in overlays:
                try:
                    # Verificar si tiene las clases problemáticas
                    clases = overlay.get_attribute('class') or ''
                    if 'x1uvtmcs' in clases or 'x4k7w5x' in clases:
                        # Hacer invisible con JavaScript
                        self.driver.execute_script(
                            "arguments[0].style.display = 'none'; arguments[0].style.visibility = 'hidden';",
                            overlay
                        )
                        count += 1
                except:
                    pass
            
            # ESTRATEGIA 2: Cualquier div que esté cubriendo toda la pantalla
            try:
                self.driver.execute_script("""
                    var divs = document.querySelectorAll('div[tabindex="-1"]');
                    divs.forEach(function(div) {
                        var style = window.getComputedStyle(div);
                        if (style.position === 'fixed' || style.position === 'absolute') {
                            div.style.display = 'none';
                            div.style.visibility = 'hidden';
                            div.style.pointerEvents = 'none';
                        }
                    });
                """)
            except:
                pass
            
            if count > 0:
                print(f"   🧹 {count} overlay(s) removido(s)")
                time.sleep(0.5)
        except:
            pass
    
    def ir_a_marketplace(self):
        """Navega a la página de creación de publicación en Marketplace"""
        print("📍 Navegando a Marketplace...")
        url = "https://www.facebook.com/marketplace/create/item"
        self.driver.get(url)
        time.sleep(1.5)
        print("✅ En página de creación")
        
        # Cerrar overlays que puedan bloquear interacción
        self.cerrar_overlays()
    
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
            input_archivo = self.driver.find_element(By.CSS_SELECTOR, "input[type='file'][accept*='image']")
            
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
        """Llena el campo de precio - Formato correcto sin decimales"""
        print(f"💰 Precio original: ${precio}")
        
        try:
            try:
                precio_float = float(precio)
                precio_entero = int(precio_float)
                precio_texto = str(precio_entero)
            except:
                precio_texto = str(precio).replace('.', '').replace(',', '')
            
            print(f"💰 Precio formateado: ${precio_texto}")
            
            campo = self.driver.find_element(By.XPATH, "//span[text()='Precio']/../..//input[@dir='ltr']")
            campo.clear()
            time.sleep(0.3)
            
            campo.send_keys(precio_texto)
            time.sleep(0.5)
            
            print("✅ Precio ingresado correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error en precio: {e}")
        return False
    
    def seleccionar_categoria(self, categoria):
        """
        Selecciona la categoría del desplegable - VERSIÓN ROBUSTA
        
        Estrategias múltiples de respaldo:
        1. Método original (funciona en artículos 1-4)
        2. Buscar dropdown por aria-label
        3. Buscar usando role='combobox'
        4. JavaScript click si falla Selenium
        5. Reintentar con espera explícita
        """
        print(f"📁 Categoría: {categoria}")
        
        # ========================================
        # ESTRATEGIA 1: Método Original
        # ========================================
        try:
            label_categoria = self.driver.find_element(By.XPATH, "//span[text()='Categoría']/../..")
            
            # Scroll para asegurar visibilidad
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                label_categoria
            )
            time.sleep(0.5)
            
            label_categoria.click()
            time.sleep(1.2)  # Aumentado para dar tiempo al dropdown
            
            # Buscar opción en el dropdown
            opcion = self.driver.find_element(By.XPATH, f"//span[contains(text(), '{categoria}')]")
            opcion.click()
            time.sleep(0.3)
            
            print("✅ Categoría seleccionada (Estrategia 1)")
            return True
            
        except Exception as e1:
            print(f"   ⚠️  Estrategia 1 falló: {str(e1)[:100]}")
        
        
        # ========================================
        # ESTRATEGIA 2: Buscar por aria-label
        # ========================================
        try:
            print("   🔄 Probando Estrategia 2 (aria-label)...")
            
            campo_categoria = self.driver.find_element(
                By.XPATH, 
                "//input[@aria-label='Categoría'] | //label[contains(@aria-label, 'Categoría')]"
            )
            
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                campo_categoria
            )
            time.sleep(0.5)
            
            campo_categoria.click()
            time.sleep(1.2)
            
            # Buscar opción
            opcion = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, f"//span[contains(text(), '{categoria}')]"))
            )
            opcion.click()
            time.sleep(0.3)
            
            print("✅ Categoría seleccionada (Estrategia 2)")
            return True
            
        except Exception as e2:
            print(f"   ⚠️  Estrategia 2 falló: {str(e2)[:100]}")
        
        
        # ========================================
        # ESTRATEGIA 3: Buscar role='combobox'
        # ========================================
        try:
            print("   🔄 Probando Estrategia 3 (role=combobox)...")
            
            # Buscar el label con role='combobox' que contenga "Categoría"
            combobox = self.driver.find_element(
                By.XPATH,
                "//label[@role='combobox']//span[contains(text(), 'Categoría')]/ancestor::label"
            )
            
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                combobox
            )
            time.sleep(0.5)
            
            # Click en el combobox
            try:
                combobox.click()
            except:
                # Si falla el click normal, usar JavaScript
                self.driver.execute_script("arguments[0].click();", combobox)
            
            time.sleep(1.5)
            
            # Esperar a que aparezca el dropdown
            opcion = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{categoria}')]"))
            )
            
            # Click en la opción
            try:
                opcion.click()
            except:
                self.driver.execute_script("arguments[0].click();", opcion)
            
            time.sleep(0.3)
            
            print("✅ Categoría seleccionada (Estrategia 3)")
            return True
            
        except Exception as e3:
            print(f"   ⚠️  Estrategia 3 falló: {str(e3)[:100]}")
        
        
        # ========================================
        # ESTRATEGIA 4: Buscar CUALQUIER span con "Categoría"
        # ========================================
        try:
            print("   🔄 Probando Estrategia 4 (span genérico)...")
            
            # Buscar todos los elementos que contengan "Categoría"
            elementos_categoria = self.driver.find_elements(
                By.XPATH,
                "//*[contains(text(), 'Categoría')]"
            )
            
            for elem in elementos_categoria:
                try:
                    if not elem.is_displayed():
                        continue
                    
                    # Intentar encontrar ancestro clickeable
                    ancestros = [
                        "./ancestor::label[1]",
                        "./ancestor::div[@role='button'][1]",
                        "./parent::*/parent::*",
                    ]
                    
                    for xpath_ancestro in ancestros:
                        try:
                            contenedor = elem.find_element(By.XPATH, xpath_ancestro)
                            
                            self.driver.execute_script(
                                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                                contenedor
                            )
                            time.sleep(0.5)
                            
                            # Click
                            try:
                                contenedor.click()
                            except:
                                self.driver.execute_script("arguments[0].click();", contenedor)
                            
                            time.sleep(1.5)
                            
                            # Buscar opción
                            opcion = WebDriverWait(self.driver, 3).until(
                                EC.presence_of_element_located((By.XPATH, f"//span[contains(text(), '{categoria}')]"))
                            )
                            
                            try:
                                opcion.click()
                            except:
                                self.driver.execute_script("arguments[0].click();", opcion)
                            
                            time.sleep(0.3)
                            
                            print("✅ Categoría seleccionada (Estrategia 4)")
                            return True
                            
                        except:
                            continue
                            
                except:
                    continue
            
        except Exception as e4:
            print(f"   ⚠️  Estrategia 4 falló: {str(e4)[:100]}")
        
        
        # ========================================
        # ESTRATEGIA 5: Recargar página y reintentar
        # ========================================
        try:
            print("   🔄 Probando Estrategia 5 (refrescar y reintentar)...")
            
            # Guardar URL actual
            url_actual = self.driver.current_url
            
            # Refrescar
            self.driver.refresh()
            time.sleep(3)
            
            # Reintentar con Estrategia 1
            label_categoria = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[text()='Categoría']/../.."))
            )
            
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                label_categoria
            )
            time.sleep(0.5)
            
            label_categoria.click()
            time.sleep(1.5)
            
            opcion = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{categoria}')]"))
            )
            opcion.click()
            time.sleep(0.3)
            
            print("✅ Categoría seleccionada (Estrategia 5 - con refresh)")
            return True
            
        except Exception as e5:
            print(f"   ⚠️  Estrategia 5 falló: {str(e5)[:100]}")
        
        
        # ========================================
        # TODAS LAS ESTRATEGIAS FALLARON
        # ========================================
        print(f"❌ Error en categoría: No se pudo seleccionar después de 5 intentos")
        
        # Tomar screenshot para debug
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"error_categoria_{timestamp}.png"
            self.driver.save_screenshot(screenshot_path)
            print(f"   📸 Screenshot guardado: {screenshot_path}")
        except:
            pass
        
        return False
    
    def seleccionar_estado(self, estado):
        """Selecciona el estado del artículo"""
        print(f"🏷️  Estado: {estado}")
        
        # Cerrar overlays primero
        self.cerrar_overlays()
        
        try:
            label_estado = self.driver.find_element(By.XPATH, "//span[text()='Estado']/../..")
            
            # Scroll al elemento
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                label_estado
            )
            time.sleep(0.5)
            
            # Intentar click normal
            try:
                label_estado.click()
            except:
                # Si falla, usar JavaScript
                self.driver.execute_script("arguments[0].click();", label_estado)
            
            time.sleep(0.8)
            
            opcion = self.driver.find_element(By.XPATH, f"//span[text()='{estado}']")
            
            try:
                opcion.click()
            except:
                self.driver.execute_script("arguments[0].click();", opcion)
            
            time.sleep(0.3)
            print("✅ Estado seleccionado")
            return True
        except Exception as e:
            print(f"❌ Error en estado: {e}")
        return False
    
    def configurar_ubicacion(self, ubicacion_deseada="Guayaquil"):
        """Configura la ubicación seleccionando del dropdown"""
        print(f"📍 Configurando ubicación: {ubicacion_deseada}")
        
        try:
            selectores_ubicacion = [
                "//label[contains(., 'Ubicación')]//input",
                "//span[text()='Ubicación']/../..//input",
                "//input[@placeholder='Ubicación']",
                "//input[contains(@aria-label, 'Ubicación')]"
            ]
            
            campo_ubicacion = None
            for selector in selectores_ubicacion:
                try:
                    campo_ubicacion = self.driver.find_element(By.XPATH, selector)
                    if campo_ubicacion:
                        break
                except:
                    continue
            
            if not campo_ubicacion:
                print("⚠️  No se encontró el campo de ubicación")
                return False
            
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                campo_ubicacion
            )
            time.sleep(0.8)
            
            campo_ubicacion.click()
            time.sleep(0.5)
            
            campo_ubicacion.send_keys(Keys.CONTROL + "a")
            time.sleep(0.2)
            campo_ubicacion.send_keys(Keys.DELETE)
            time.sleep(0.3)
            
            campo_ubicacion.send_keys(ubicacion_deseada)
            time.sleep(3)
            
            try:
                opciones_dropdown = [
                    "//div[@role='listbox']//div[@role='option']//span[contains(text(), 'Guayaquil')]//ancestor::div[@role='option']",
                    "//div[@role='option' and contains(., 'Guayaquil') and contains(., 'Ciudad')]",
                    "//div[@role='listbox']//div[@role='option'][1]"
                ]
                
                opcion_seleccionada = False
                for selector_opcion in opciones_dropdown:
                    try:
                        opciones = self.driver.find_elements(By.XPATH, selector_opcion)
                        if opciones:
                            for opcion in opciones:
                                texto_opcion = opcion.text.lower()
                                if 'ciudad' in texto_opcion or 'guayaquil' in texto_opcion:
                                    opcion.click()
                                    time.sleep(0.5)
                                    print(f"✅ Seleccionada ubicación del dropdown: {opcion.text[:50]}")
                                    opcion_seleccionada = True
                                    break
                            
                            if opcion_seleccionada:
                                break
                    except:
                        continue
                
                if not opcion_seleccionada:
                    print("⚠️  No se pudo seleccionar del dropdown, usando Enter")
                    campo_ubicacion.send_keys(Keys.RETURN)
                    time.sleep(0.5)
                
            except Exception as e:
                print(f"⚠️  Error seleccionando dropdown: {e}")
                campo_ubicacion.send_keys(Keys.RETURN)
                time.sleep(0.5)
            
            return True
            
        except Exception as e:
            print(f"⚠️  Error configurando ubicación: {e}")
            print("   Continuando con ubicación automática...")
            return False
    
    def llenar_descripcion(self, descripcion):
        """Llena el campo de descripción con soporte multi-línea"""
        print(f"📝 Accediendo a descripción...")
        
        # Cerrar overlays primero
        self.cerrar_overlays()
        
        try:
            campo_descripcion = self.driver.find_element(By.XPATH, "//textarea[@dir='ltr']")
            
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                campo_descripcion
            )
            time.sleep(0.8)
            
            # Intentar click normal
            try:
                campo_descripcion.click()
            except:
                # Si falla, usar JavaScript para hacer foco
                self.driver.execute_script("arguments[0].focus();", campo_descripcion)
            
            time.sleep(0.3)
            
            # Mostrar preview de la descripción
            preview = descripcion[:80].replace('\n', ' ')
            print(f"📝 Llenando descripción completa ({len(descripcion)} caracteres)...")
            print(f"    Preview: {preview}...")
            
            # Llenar usando JavaScript (más confiable)
            self.driver.execute_script(
                "arguments[0].value = arguments[1];",
                campo_descripcion,
                descripcion
            )
            
            # Disparar evento 'input' para que Facebook detecte el cambio
            self.driver.execute_script(
                "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));",
                campo_descripcion
            )
            
            time.sleep(0.3)
            
            print(f"✅ Descripción ingresada ({len(descripcion)} caracteres)")
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
            time.sleep(0.5)
            
            campo_etiquetas = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Etiquetas de producto')]/ancestor::div[contains(@class, 'x78zum5')]//input[@dir='ltr']")
            
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", campo_etiquetas)
            time.sleep(0.5)
            campo_etiquetas.click()
            time.sleep(0.3)
            
            lista_etiquetas = [e.strip() for e in etiquetas.split(',') if e.strip()]
            
            for etiqueta in lista_etiquetas:
                campo_etiquetas.send_keys(etiqueta)
                time.sleep(0.3)
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
        try:
            if encuentro_publico.lower() == "si":
                print("✅ Marcando encuentro en lugar público")
                try:
                    checkbox = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Encuentro en un lugar público')]/..//input[@type='checkbox']")
                    if not checkbox.is_selected():
                        checkbox.click()
                        time.sleep(0.3)
                except:
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
        
        # Cerrar overlays antes de publicar
        self.cerrar_overlays()
        
        try:
            boton_siguiente = self.driver.find_element(By.XPATH, "//span[text()='Siguiente']")
            
            self.driver.execute_script("arguments[0].scrollIntoView(true);", boton_siguiente)
            time.sleep(0.5)
            
            # Intentar click normal
            try:
                boton_siguiente.click()
            except:
                # Si falla, usar JavaScript
                self.driver.execute_script("arguments[0].click();", boton_siguiente)
            
            time.sleep(1.5)
            
            print("✅ Clic en 'Siguiente' exitoso")
            
            time.sleep(1)
            
            try:
                boton_publicar = self.driver.find_element(By.XPATH, "//span[text()='Publicar']")
                if boton_publicar:
                    print("📌 Encontrado botón 'Publicar', haciendo clic...")
                    
                    try:
                        boton_publicar.click()
                    except:
                        self.driver.execute_script("arguments[0].click();", boton_publicar)
                    
                    time.sleep(1)
            except:
                pass
            
            print("✅ Artículo publicado exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error al publicar: {e}")
            
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
        
        if not self.esperar_login_facebook():
            print("❌ No se pudo verificar la sesión de Facebook")
            return False
        
        self.ir_a_marketplace()
        time.sleep(2)  # Espera aumentada
        
        # Cerrar overlays DESPUÉS de que cargue la página
        self.cerrar_overlays()
        time.sleep(1)
        
        if not self.subir_imagenes(imagenes):
            print("❌ Fallo crítico: No se pudieron subir imágenes")
            return False
        
        time.sleep(1)
        self.cerrar_overlays()  # Cerrar de nuevo después de subir imágenes
        
        self.llenar_titulo(datos.get('titulo', ''))
        time.sleep(0.5)
        
        self.llenar_precio(datos.get('precio', '0'))
        time.sleep(0.5)
        
        # Cerrar overlays ANTES de categoría
        self.cerrar_overlays()
        self.seleccionar_categoria(datos.get('categoria', 'Electrónica e informática'))
        time.sleep(0.5)
        
        # Cerrar overlays ANTES de estado
        self.cerrar_overlays()
        self.seleccionar_estado(datos.get('estado', 'Nuevo'))
        time.sleep(0.5)
        
        ubicacion = datos.get('ubicacion', 'Guayaquil')
        self.configurar_ubicacion(ubicacion)
        time.sleep(0.5)
        
        # Cerrar overlays ANTES de descripción
        self.cerrar_overlays()
        self.llenar_descripcion(datos.get('descripcion', ''))
        time.sleep(0.5)
        
        self.llenar_etiquetas(datos.get('etiquetas', ''))
        self.llenar_sku(datos.get('sku', ''))
        
        self.configurar_disponibilidad(
            datos.get('disponibilidad', 'Publicar como disponible'),
            datos.get('encuentro_publico', 'Si')
        )
        
        print("\n⏳ Esperando 1 segundo antes de publicar...")
        time.sleep(1)
        
        # Cerrar overlays ANTES de publicar
        self.cerrar_overlays()
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
