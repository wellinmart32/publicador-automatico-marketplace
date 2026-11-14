"""
Avisos por WhatsApp Web (fase 4e).

Abre WhatsApp Web en una pestaña nueva del MISMO navegador que ya está usando el atendedor (no abre otro Edge),
busca un contacto por su nombre, le escribe un mensaje y vuelve a la pestaña original.

Reutiliza de ExtractorWhatsApp la espera de carga/QR de WhatsApp Web.
"""

import re
import time
import unicodedata

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from extractores.extractor_whatsapp import ExtractorWhatsApp


URL_WHATSAPP = "https://web.whatsapp.com"

# Espacios "especiales" que WhatsApp pone en números y nombres: espacio duro, fino y marcas invisibles
ESPACIOS_ESPECIALES = "  ‎‏ "


def normalizar_nombre(texto):
    """Nombre comparable: espacios especiales como espacios normales, sin espacios repetidos y en minúsculas"""
    for c in ESPACIOS_ESPECIALES:
        texto = (texto or '').replace(c, ' ')
    return re.sub(r'\s+', ' ', texto).strip().lower()


def variantes_de_busqueda(nombre):
    """
    Textos a escribir en el buscador de WhatsApp, del más específico al más simple.
    '+593 99 504 8627 (Tú)' → ['+593 99 504 8627 (Tú)', '+593 99 504 8627']
    """
    completo = re.sub(r'\s+', ' ', (nombre or '').strip())
    sin_parentesis = re.sub(r'\s*\([^)]*\)\s*$', '', completo).strip()
    variantes = [completo]
    if sin_parentesis and sin_parentesis != completo:
        variantes.append(sin_parentesis)
    return variantes


def _comparable(texto):
    limpio = re.sub(r'[^a-z0-9]+', ' ', ''.join(
        c for c in unicodedata.normalize('NFKD', texto or '') if not unicodedata.combining(c)).lower())
    return limpio.strip()


class NotificadorWhatsApp(ExtractorWhatsApp):
    """Envía mensajes por WhatsApp Web usando un navegador que ya está abierto"""

    XPATH_CAJA_MENSAJE = ("//footer//div[@contenteditable='true'][@role='textbox'] | "
                          "//footer//div[@contenteditable='true']")

    JS_PEGAR = """
    const caja = arguments[0], texto = arguments[1];
    caja.focus();
    const datos = new DataTransfer();
    datos.setData('text/plain', texto);
    caja.dispatchEvent(new ClipboardEvent('paste', {clipboardData: datos, bubbles: true, cancelable: true}));
    return (caja.innerText || '');
    """

    JS_INSERTAR = """
    const caja = arguments[0], lineas = arguments[1].split('\\n');
    caja.focus();
    lineas.forEach((linea, i) => {
        if (linea) document.execCommand('insertText', false, linea);
        if (i < lineas.length - 1) document.execCommand('insertLineBreak');
    });
    return (caja.innerText || '');
    """

    def __init__(self, driver, config=None):
        super().__init__(config)
        self.driver = driver
        self.wait = WebDriverWait(driver, 60)
        self.pestana_original = None
        self.pestana_whatsapp = None

    # ------------------------------------------------------------

    def abrir(self):
        """Abre WhatsApp Web en una pestaña nueva y espera a que cargue (o a que escanees el QR)"""
        try:
            self.pestana_original = self.driver.current_window_handle
            try:
                self.driver.switch_to.new_window('tab')
            except Exception:
                self.driver.execute_script("window.open('about:blank', '_blank');")
                self.driver.switch_to.window(self.driver.window_handles[-1])
            self.pestana_whatsapp = self.driver.current_window_handle

            print("📱 Abriendo WhatsApp Web en una pestaña nueva...")
            self.driver.get(URL_WHATSAPP)
            time.sleep(3)
            return self.esperar_whatsapp_cargado()
        except Exception as e:
            print(f"❌ No se pudo abrir WhatsApp Web: {e}")
            return False

    def cerrar(self):
        """Cierra la pestaña de WhatsApp y vuelve a la pestaña original"""
        try:
            if self.pestana_whatsapp and self.pestana_whatsapp in self.driver.window_handles:
                self.driver.switch_to.window(self.pestana_whatsapp)
                self.driver.close()
            if self.pestana_original and self.pestana_original in self.driver.window_handles:
                self.driver.switch_to.window(self.pestana_original)
        except Exception:
            pass

    # ------------------------------------------------------------

    def _xpath_resultado(self, nombre, exacto):
        """Chats de la lista cuyo título coincide con el nombre, sin importar los espacios especiales"""
        normalizado = f"normalize-space(translate(@title, '{ESPACIOS_ESPECIALES}', '     '))"
        literal = self._literal_xpath(normalizar_nombre(nombre))
        minusculas = ("translate({0}, 'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚÑ', 'abcdefghijklmnopqrstuvwxyzáéíóúñ')"
                      .format(normalizado))
        if exacto:
            return f"//div[@id='pane-side']//span[{minusculas} = {literal}]"
        return f"//div[@id='pane-side']//span[contains({minusculas}, {literal})]"

    def abrir_chat_de(self, nombre):
        """Busca el contacto por nombre y abre su chat. Devuelve True si lo abrió."""
        print(f"🔍 Buscando contacto en WhatsApp: {nombre}")
        try:
            for texto_busqueda in variantes_de_busqueda(nombre):
                campo = self.wait.until(EC.element_to_be_clickable((By.XPATH, self.XPATH_BUSQUEDA)))
                campo.click()
                time.sleep(0.3)
                campo.send_keys(Keys.CONTROL + "a")
                campo.send_keys(Keys.BACKSPACE)
                time.sleep(0.3)
                for caracter in texto_busqueda:
                    campo.send_keys(caracter)
                    time.sleep(0.04)
                time.sleep(2)

                resultado = None
                for exacto, referencia in ((True, nombre), (False, nombre),
                                           (False, texto_busqueda)):
                    try:
                        resultado = WebDriverWait(self.driver, 6).until(
                            EC.presence_of_element_located((By.XPATH, self._xpath_resultado(referencia, exacto))))
                        break
                    except Exception:
                        continue
                if resultado is None:
                    continue

                try:
                    resultado.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", resultado)
                time.sleep(2)
                return True

            print(f"❌ No se encontró el contacto '{nombre}' en WhatsApp")
            return False
        except Exception as e:
            print(f"❌ Error buscando el contacto '{nombre}': {e}")
            return False

    def enviar(self, nombre_contacto, texto):
        """
        Escribe el texto en el chat del contacto y lo envía.
        Devuelve True si el mensaje se escribió y el cuadro de texto quedó vacío después de enviar.
        """
        if not self.abrir_chat_de(nombre_contacto):
            return False
        try:
            caja = self.wait.until(EC.presence_of_element_located((By.XPATH, self.XPATH_CAJA_MENSAJE)))
            try:
                caja.click()
            except Exception:
                pass

            clave = _comparable(texto)[:25]
            escrito = self.driver.execute_script(self.JS_PEGAR, caja, texto)
            if clave not in _comparable(escrito):
                self.driver.execute_script(self.JS_INSERTAR, caja, texto)
                if clave not in _comparable(caja.text):
                    print("   ⚠️  No se pudo escribir el mensaje en WhatsApp")
                    return False

            time.sleep(0.7)
            caja.send_keys(Keys.ENTER)

            for _ in range(10):
                time.sleep(1)
                if not (caja.text or '').strip():
                    time.sleep(1)
                    return True
            print("   ⚠️  El mensaje sigue en el cuadro de texto: puede que no se haya enviado")
            return False
        except Exception as e:
            print(f"   ❌ Error enviando por WhatsApp: {e}")
            return False
