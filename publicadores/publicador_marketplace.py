from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

from compartido.navegador import abrir_navegador


class PublicadorMarketplace:
    """Maneja la automatización de publicaciones en Facebook Marketplace"""

    def __init__(self, config=None):
        self.driver = None
        self.wait = None
        self.config = config or {}
        self.sesion_verificada = False

    def iniciar_navegador(self):
        """Abre el navegador configurado (Firefox, Chrome o Edge) con su perfil de Marketplace"""
        self.driver = abrir_navegador(self.config)
        self.wait = WebDriverWait(self.driver, 20)

    @staticmethod
    def _notificar(titulo, mensaje):
        """Aviso emergente para que el usuario vea que debe actuar en el navegador"""
        import threading

        def _mostrar():
            try:
                import tkinter as tk
                from compartido.toast import Toast
                root = tk.Tk()
                root.withdraw()
                Toast.advertencia(root, f"{titulo}\n{mensaje}", duracion=8000)
                root.after(8500, root.destroy)
                root.mainloop()
            except Exception:
                pass
        threading.Thread(target=_mostrar, daemon=True).start()

    def _es_pagina_seguridad(self):
        """Detecta si Facebook mostró una verificación de seguridad"""
        try:
            url = self.driver.current_url
        except Exception:
            return False
        return any(p in url for p in ('two_step_verification', 'checkpoint', 'login/device-based',
                                      'security_check', 'identity_confirmation', 'recaptcha', 'captcha'))

    def _esperar_resolucion_seguridad(self, timeout=180):
        """Espera a que el usuario resuelva la verificación de seguridad en el navegador"""
        transcurrido = 0
        while transcurrido < timeout:
            time.sleep(5)
            transcurrido += 5
            try:
                url = self.driver.current_url
                if not self._es_pagina_seguridad() and 'login' not in url and 'facebook.com' in url:
                    print("✅ Verificación de seguridad resuelta")
                    time.sleep(3)
                    return True
                print(f"⏳ Esperando que resuelvas la verificación... ({timeout - transcurrido}s restantes)")
            except Exception:
                return True
        print("❌ Tiempo de espera agotado para la verificación de seguridad")
        return False

    def esperar_login_facebook(self):
        """Verifica la sesión de Facebook una sola vez por ejecución; si hace falta espera a que el usuario inicie sesión"""
        if self.sesion_verificada:
            return True

        print("🔐 Verificando sesión de Facebook...")
        try:
            self.driver.get("https://www.facebook.com")
            time.sleep(3)

            if self._es_pagina_seguridad():
                self._notificar("Verificación de seguridad requerida",
                                "Facebook pide verificar tu cuenta.\nResuélvelo en el navegador. Tienes 3 minutos.")
                print("\n⚠️  FACEBOOK REQUIERE VERIFICACIÓN DE SEGURIDAD")
                print("   Resuélvela en el navegador. Tienes 3 MINUTOS.\n")
                self.sesion_verificada = self._esperar_resolucion_seguridad(180)
                return self.sesion_verificada

            campos_login = self.driver.find_elements(By.XPATH, "//input[@name='email' or @name='pass']")
            if not campos_login:
                print("✅ Ya tienes sesión activa en Facebook")
                self.sesion_verificada = True
                return True

            self._notificar("Iniciar sesión en Facebook", "Ingresa tus credenciales en el navegador.\nTienes 2 minutos.")
            print("\n⚠️  NO HAS INICIADO SESIÓN EN FACEBOOK")
            print("   Inicia sesión en el navegador. Tienes 2 MINUTOS.\n")

            timeout = 120
            transcurrido = 0
            while transcurrido < timeout:
                time.sleep(5)
                transcurrido += 5
                try:
                    if self._es_pagina_seguridad():
                        print("\n⚠️  Facebook pide verificación adicional...")
                        self.sesion_verificada = self._esperar_resolucion_seguridad(180)
                        return self.sesion_verificada
                    if not self.driver.find_elements(By.XPATH, "//input[@name='email' or @name='pass']"):
                        print("✅ Sesión iniciada correctamente")
                        time.sleep(3)
                        self.sesion_verificada = True
                        return True
                    print(f"⏳ Esperando login... ({timeout - transcurrido}s restantes)")
                except Exception:
                    print("✅ Sesión iniciada correctamente")
                    self.sesion_verificada = True
                    return True

            print("❌ Tiempo de espera agotado. No se detectó inicio de sesión.")
            return False

        except Exception as e:
            print(f"⚠️  Error verificando sesión: {e}")
            print("Continuando de todos modos...")
            return True

    # ==================== AYUDANTES DEL FORMULARIO ====================
    # El formulario de Marketplace (nov 2026) marca cada campo con un <span> con su nombre visible:
    #   Título, Precio, SKU      → span + <input> hermano
    #   Descripción, Etiquetas   → span + <div> con <textarea>
    #   Categoría, Estado        → <label role="combobox"> que contiene el span
    #   Ubicación                → <input role="combobox" aria-label="Ubicación">
    #   Encuentro en un lugar público → <div role="checkbox"> en un contenedor varios niveles arriba
    #   Siguiente / Publicar     → <div role="button" aria-label="..."> (aria-disabled="true" si falta algo)
    # Descripción, etiquetas, SKU, ubicación y entrega están dentro del bloque plegable "Más detalles".

    CATEGORIA_DEFECTO = 'Electrónica e informática'
    ESTADO_DEFECTO = 'Nuevo'

    def _buscar(self, xpath, tiempo=0):
        """Primer elemento visible que cumple el xpath (espera hasta 'tiempo' segundos). None si no hay"""
        limite = time.time() + tiempo
        while True:
            for elemento in self.driver.find_elements(By.XPATH, xpath):
                try:
                    if elemento.is_displayed():
                        return elemento
                except Exception:
                    pass
            if time.time() >= limite:
                return None
            time.sleep(0.5)

    def _clic(self, elemento):
        """Clic con JavaScript: evita el error 'element click intercepted' por capas encima"""
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
        time.sleep(0.3)
        self.driver.execute_script("arguments[0].click();", elemento)

    @staticmethod
    def _xpath_texto(texto):
        """Literal xpath seguro aunque el texto tenga comillas simples"""
        if "'" not in texto:
            return f"'{texto}'"
        partes = texto.split("'")
        return "concat(" + ", \"'\", ".join(f"'{p}'" for p in partes) + ")"

    def _campo_texto(self, etiqueta, tiempo=0):
        """input o textarea que acompaña al span con ese nombre"""
        t = self._xpath_texto(etiqueta)
        return self._buscar(f"//span[normalize-space()={t}]/parent::div//*[self::input or self::textarea]", tiempo)

    def _escribir(self, campo, texto):
        """
        Escribe en un input/textarea controlado por React.
        send_keys no admite emojis en Chrome/Edge, así que en ese caso se usa el setter nativo + evento input.
        """
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", campo)
        try:
            campo.click()
        except Exception:
            self.driver.execute_script("arguments[0].focus();", campo)
        campo.send_keys(Keys.CONTROL, 'a')
        campo.send_keys(Keys.DELETE)
        if all(ord(c) <= 0xFFFF for c in texto):
            campo.send_keys(texto)
        else:
            self.driver.execute_script("""
                const campo = arguments[0];
                const prototipo = campo.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
                Object.getOwnPropertyDescriptor(prototipo, 'value').set.call(campo, arguments[1]);
                campo.dispatchEvent(new Event('input', { bubbles: true }));
                campo.dispatchEvent(new Event('change', { bubbles: true }));
            """, campo, texto)
        time.sleep(0.3)
        return (campo.get_attribute('value') or '').strip() != ''

    def _elegir_en_lista(self, etiqueta, valor):
        """Abre la lista desplegable (Categoría, Estado, Disponibilidad) y elige la opción con ese texto"""
        t = self._xpath_texto(etiqueta)
        combo = self._buscar(f"//label[@role='combobox'][.//span[normalize-space()={t}]]", 10)
        if not combo:
            print(f"   ⚠️  No se encontró la lista '{etiqueta}'")
            return False

        v = self._xpath_texto(valor)
        for intento in range(2):
            self._clic(combo)
            time.sleep(1)
            opcion = (self._buscar(f"//*[@role='option'][.//span[normalize-space()={v}]]", 3) or
                      self._buscar(f"//*[@role='listbox']//span[normalize-space()={v}]", 1) or
                      self._buscar(f"//*[@role='dialog' or @role='menu']//span[normalize-space()={v}]", 1))
            if opcion:
                self._clic(opcion)
                time.sleep(0.8)
                if valor.lower() in (combo.text or '').lower():
                    return True
            # Cerrar la lista antes de reintentar
            try:
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            except Exception:
                pass
            time.sleep(0.5)

        print(f"   ⚠️  No se pudo elegir '{valor}' en '{etiqueta}'")
        return False

    def _abrir_mas_detalles(self):
        """Despliega el bloque 'Más detalles' si está cerrado (ahí están descripción, ubicación y entrega)"""
        if self._campo_texto('Descripción'):
            return True
        boton = self._buscar("//span[normalize-space()='Más detalles']", 5)
        if not boton:
            print("   ⚠️  No se encontró 'Más detalles'")
            return False
        self._clic(boton)
        return self._campo_texto('Descripción', 5) is not None

    # ==================== CAMPOS DEL FORMULARIO ====================

    def llenar_titulo(self, titulo):
        print(f"✍️  Título: {titulo}")
        campo = self._campo_texto('Título', 10)
        if campo and self._escribir(campo, titulo):
            print("✅ Título ingresado")
            return True
        print("❌ No se pudo ingresar el título")
        return False

    def llenar_precio(self, precio):
        """Marketplace solo acepta precio entero"""
        try:
            precio_texto = str(int(float(str(precio).replace(',', '.'))))
        except ValueError:
            precio_texto = ''.join(c for c in str(precio) if c.isdigit()) or '0'
        print(f"💰 Precio: ${precio_texto}")
        campo = self._campo_texto('Precio', 5)
        if campo and self._escribir(campo, precio_texto):
            print("✅ Precio ingresado")
            return True
        print("❌ No se pudo ingresar el precio")
        return False

    def seleccionar_categoria(self, categoria):
        if not categoria:
            categoria = self.CATEGORIA_DEFECTO
            print(f"   ℹ️  El producto no tiene categoría: se usa '{categoria}'")
        print(f"📁 Categoría: {categoria}")
        if self._elegir_en_lista('Categoría', categoria):
            print("✅ Categoría seleccionada")
            return True
        return False

    def seleccionar_estado(self, estado):
        estado = estado or self.ESTADO_DEFECTO
        print(f"🏷️  Estado: {estado}")
        if self._elegir_en_lista('Estado', estado):
            print("✅ Estado seleccionado")
            return True
        return False

    def llenar_descripcion(self, descripcion):
        if not descripcion:
            print("⏭️  Sin descripción, omitiendo...")
            return True
        print(f"📝 Descripción ({len(descripcion)} caracteres)")
        self._abrir_mas_detalles()
        campo = self._campo_texto('Descripción', 5)
        if campo and self._escribir(campo, descripcion):
            print("✅ Descripción ingresada")
            return True
        print("⚠️  No se pudo ingresar la descripción")
        return False

    def configurar_ubicacion(self, ubicacion_deseada):
        """Facebook la llena con la ciudad del perfil; solo se cambia si es distinta"""
        if not ubicacion_deseada:
            return True
        self._abrir_mas_detalles()
        campo = self._buscar("//input[@aria-label='Ubicación']", 5)
        if not campo:
            print("⚠️  No se encontró el campo de ubicación (se deja la de tu perfil)")
            return False

        actual = (campo.get_attribute('value') or '').strip()
        ciudad = ubicacion_deseada.split(',')[0].strip().lower()
        if ciudad and ciudad in actual.lower():
            print(f"📍 Ubicación: {actual}")
            return True

        print(f"📍 Cambiando ubicación: {actual or '(vacía)'} → {ubicacion_deseada}")
        self._escribir(campo, ubicacion_deseada)
        time.sleep(2)
        opcion = self._buscar("//*[@role='listbox']//*[@role='option'] | //ul[@role='listbox']/li", 5)
        if opcion:
            self._clic(opcion)
            time.sleep(1)
            print(f"✅ Ubicación: {campo.get_attribute('value')}")
            return True
        print("⚠️  Facebook no sugirió esa ubicación")
        return False

    def llenar_etiquetas(self, etiquetas):
        lista = [e.strip() for e in (etiquetas or '').split(',') if e.strip()][:20]
        if not lista:
            return True
        print(f"🏷️  Etiquetas: {', '.join(lista)}")
        self._abrir_mas_detalles()
        campo = self._campo_texto('Etiquetas de producto', 5)
        if not campo:
            print("⚠️  No se encontró el campo de etiquetas")
            return False
        self._clic(campo)
        for etiqueta in lista:
            campo.send_keys(etiqueta)
            time.sleep(0.3)
            campo.send_keys(Keys.RETURN)
            time.sleep(0.3)
        print(f"✅ {len(lista)} etiqueta(s) agregada(s)")
        return True

    def llenar_sku(self, sku):
        if not sku or not sku.strip():
            return True
        print(f"🔢 SKU: {sku}")
        self._abrir_mas_detalles()
        campo = self._campo_texto('SKU', 5)
        if campo and self._escribir(campo, sku.strip()):
            print("✅ SKU ingresado")
            return True
        print("⚠️  No se pudo ingresar el SKU")
        return False

    def configurar_disponibilidad(self, disponibilidad, encuentro_publico):
        """Marca 'Encuentro en un lugar público' (la disponibilidad ya viene como 'Publicar como disponible')"""
        if (encuentro_publico or '').strip().lower() not in ('si', 'sí'):
            return True
        self._abrir_mas_detalles()
        casilla = self._buscar("//span[normalize-space()='Encuentro en un lugar público']"
                               "/ancestor::div[.//div[@role='checkbox']][1]//div[@role='checkbox']", 5)
        if not casilla:
            print("⚠️  No se encontró 'Encuentro en un lugar público'")
            return False
        if casilla.get_attribute('aria-checked') != 'true':
            self._clic(casilla)
            time.sleep(0.5)
        if casilla.get_attribute('aria-checked') == 'true':
            print("✅ Encuentro en un lugar público marcado")
            return True
        print("⚠️  No se pudo marcar 'Encuentro en un lugar público'")
        return False

    # ==================== PUBLICAR Y VERIFICAR ====================

    def _boton_habilitado(self, nombre, tiempo):
        """Botón role=button con ese aria-label, esperando a que se habilite. None si sigue desactivado"""
        limite = time.time() + tiempo
        while time.time() < limite:
            boton = self._buscar(f"//div[@role='button'][@aria-label='{nombre}']")
            if boton and boton.get_attribute('aria-disabled') != 'true':
                return boton
            time.sleep(1)
        return None

    def _errores_visibles(self):
        """Mensajes de error que muestra el formulario bajo los campos (ej. 'Selecciona una categoría.')"""
        textos = []
        for xpath in ("//span[starts-with(normalize-space(), 'Introduce')]",
                      "//span[starts-with(normalize-space(), 'Selecciona')]",
                      "//span[starts-with(normalize-space(), 'Sube al menos')]"):
            for el in self.driver.find_elements(By.XPATH, xpath):
                try:
                    if el.is_displayed() and el.text.strip() and el.text.strip() not in textos:
                        textos.append(el.text.strip())
                except Exception:
                    pass
        return textos

    def _guardar_captura_error(self):
        try:
            from compartido.gestor_archivos import _base_dir
            ruta = os.path.join(_base_dir(), "error_publicacion.png")
            self.driver.save_screenshot(ruta)
            print(f"📸 Captura guardada en {ruta}")
        except Exception:
            pass

    def publicar_articulo(self):
        """
        Siguiente → Publicar, y confirma que Facebook aceptó la publicación.
        Solo devuelve True si la página salió del formulario de creación.
        """
        print("🚀 Publicando artículo...")

        boton = self._boton_habilitado('Siguiente', 20)
        if not boton:
            errores = self._errores_visibles()
            print("❌ El botón 'Siguiente' sigue desactivado: falta algo obligatorio")
            for error in errores:
                print(f"   • {error}")
            self._guardar_captura_error()
            return False
        self._clic(boton)
        print("✅ Clic en 'Siguiente'")
        time.sleep(3)

        boton = self._boton_habilitado('Publicar', 20)
        if not boton:
            print("❌ No apareció el botón 'Publicar'")
            self._guardar_captura_error()
            return False
        self._clic(boton)
        print("✅ Clic en 'Publicar'")

        # Confirmar: Facebook sale de /marketplace/create cuando acepta la publicación
        limite = time.time() + 45
        while time.time() < limite:
            time.sleep(2)
            try:
                if '/marketplace/create' not in self.driver.current_url:
                    print("✅ Facebook aceptó la publicación")
                    return True
            except Exception:
                pass
        print("❌ Facebook no confirmó la publicación (la página sigue en el formulario)")
        self._guardar_captura_error()
        return False

    def ir_a_marketplace(self):
        """Abre el formulario de crear publicación y espera a que cargue"""
        print("📍 Abriendo el formulario de Marketplace...")
        self.driver.get("https://www.facebook.com/marketplace/create/item")
        if self._campo_texto('Título', 20):
            print("✅ Formulario listo")
            self.cerrar_overlays()
            return True
        print("❌ El formulario de Marketplace no cargó")
        return False

    def subir_imagenes(self, rutas_imagenes):
        if not rutas_imagenes:
            print("⚠️  No hay imágenes para subir")
            return False
        print(f"📸 Subiendo {len(rutas_imagenes)} imagen(es)...")
        try:
            entrada = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file'][accept*='image']")))
            entrada.send_keys("\n".join(rutas_imagenes))
            time.sleep(2 + len(rutas_imagenes))
            print("✅ Imágenes subidas")
            return True
        except Exception as e:
            print(f"❌ Error subiendo imágenes: {e}")
            return False

    def cerrar_overlays(self):
        """Oculta avisos emergentes de Facebook que tapan el formulario"""
        try:
            ocultos = self.driver.execute_script("""
                let n = 0;
                document.querySelectorAll("div[tabindex='-1']").forEach(d => {
                    const c = d.className || '';
                    if (typeof c === 'string' && (c.includes('x1uvtmcs') || c.includes('x4k7w5x'))) {
                        d.style.display = 'none'; n++;
                    }
                });
                return n;
            """)
            if ocultos:
                print(f"   🧹 {ocultos} aviso(s) ocultado(s)")
        except Exception:
            pass

    def publicar_producto_completo(self, datos, imagenes):
        """Publica un producto completo en Marketplace. True solo si Facebook confirmó la publicación"""
        print("\n" + "=" * 50)
        print("🎯 INICIANDO PUBLICACIÓN")
        print("=" * 50 + "\n")

        if not self.esperar_login_facebook():
            print("❌ No se pudo verificar la sesión de Facebook")
            return False

        if not self.ir_a_marketplace():
            return False

        if not self.subir_imagenes(imagenes):
            return False

        # Obligatorios
        self.llenar_titulo(datos.get('titulo', ''))
        self.llenar_precio(datos.get('precio', '0'))
        self.seleccionar_categoria(datos.get('categoria', ''))
        self.seleccionar_estado(datos.get('estado', ''))

        # Más detalles (opcionales)
        self.llenar_descripcion(datos.get('descripcion', ''))
        self.llenar_etiquetas(datos.get('etiquetas', ''))
        self.llenar_sku(datos.get('sku', ''))
        self.configurar_ubicacion(datos.get('ubicacion') or self.config.get('ubicacion', ''))
        self.configurar_disponibilidad(datos.get('disponibilidad', ''), datos.get('encuentro_publico', 'Si'))

        exito = self.publicar_articulo()
        if exito:
            print("\n" + "=" * 50)
            print("✅ PUBLICACIÓN COMPLETADA")
            print("=" * 50 + "\n")
            time.sleep(self.config.get('espera_despues_publicar', 5))
        return exito

    def cerrar_navegador(self):
        """Cierra el navegador"""
        if self.driver:
            print("\n🔒 Cerrando navegador...")
            try:
                self.driver.quit()
                print("✅ Navegador cerrado")
            except Exception:
                pass
            self.driver = None
