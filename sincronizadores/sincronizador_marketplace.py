"""
Sincronizar con Marketplace (fase 6a).

Lee "Tus publicaciones" de Facebook Marketplace y refleja lo que el vendedor ya tiene publicado en el Gestor de
Productos: crea un artículo por cada anuncio que la app no conoce (con título, precio, descripción, estado del
producto y fotos) y mantiene al día el estado de cada uno (Disponible, Pendiente, Vendido, Rechazado, Eliminado).

Cada artículo guarda en datos.txt tres campos:
  id_marketplace      número del anuncio en Facebook (el que sale en facebook.com/marketplace/item/<id>)
  estado_marketplace  Disponible · Pendiente · Vendido · Rechazado (parece duplicado) · Eliminado en Facebook · Borrador
  firma_marketplace   'título|Publicado el dd/mm/aaaa' del anuncio: sirve para reconocerlo sin abrirlo otra vez

Estructura de Facebook (nov 2026, interfaz en español), página https://www.facebook.com/marketplace/you/selling :
  - Cada anuncio es una tarjeta con un botón aria-label="Título, 12 $, Disponible, Publicado el 28/12/2025,
    Publicado en Marketplace, 0 clics en la publicación" y un botón "Más opciones de Título".
  - Menú "Más opciones": Ver publicación · Editar publicación · Eliminar publicación...
    "Ver publicación" abre el anuncio en facebook.com/marketplace/item/<id>.
  - En la página del anuncio: bajo "Detalles" van "Estado: Nuevo" y la descripción; las fotos son
    <img alt="Foto de producto de Título">.
"""

import os
import re
import time
import unicodedata
import urllib.request

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from compartido.gestor_archivos import (
    CLAVES_DATOS_ARTICULO, ESTADOS_ARTICULO, _carpeta_articulo, guardar_datos_articulo, leer_datos_articulo,
    numeros_articulos, obtener_imagenes_articulo)
from publicadores.publicador_marketplace import PublicadorMarketplace


URL_VENTA = "https://www.facebook.com/marketplace/you/selling"
URL_ANUNCIO = "https://www.facebook.com/marketplace/item/{}"

ESTADO_DISPONIBLE = 'Disponible'
ESTADO_PENDIENTE = 'Pendiente'
ESTADO_VENDIDO = 'Vendido'
ESTADO_RECHAZADO = 'Rechazado (parece duplicado)'
ESTADO_BORRADOR = 'Borrador'
ESTADO_ELIMINADO = 'Eliminado en Facebook'

# En estos estados el anuncio está activo en Facebook: la rotación no debe volver a publicarlo
ESTADOS_ACTIVOS = (ESTADO_DISPONIBLE, ESTADO_PENDIENTE)
CATEGORIA_POR_DEFECTO = 'Electrónica e informática'


def categoria_mas_usada(locales):
    """Categoría que más se repite en los productos locales; si no hay ninguna, la de por defecto"""
    cuenta = {}
    for datos in locales.values():
        categoria = (datos.get('categoria') or '').strip()
        if categoria:
            cuenta[categoria] = cuenta.get(categoria, 0) + 1
    return max(cuenta, key=cuenta.get) if cuenta else CATEGORIA_POR_DEFECTO

MAX_ANUNCIOS_NUEVOS_POR_EJECUCION = 60


# ============================================================
# FUNCIONES DE TEXTO (no dependen del navegador)
# ============================================================

def _sin_acentos(texto):
    return ''.join(c for c in unicodedata.normalize('NFKD', texto or '') if not unicodedata.combining(c))


def normalizar_titulo(texto):
    """Título comparable: minúsculas, sin acentos, emojis ni símbolos ('▫️ EYooso Z - 11' → 'eyoosoz11')"""
    return re.sub(r'[^a-z0-9]', '', _sin_acentos(texto).lower())


PATRON_ETIQUETA = re.compile(
    r'^(?P<titulo>.+?), (?P<precio>(?:US)?\$?\s?\d[\d.,]*\s?\$?), (?P<estado>[^,]+), (?P<resto>.*)$', re.DOTALL)
PATRON_FECHA = re.compile(r'(?:Publicado|Renovado|Actualizado)\s+el\s+(\d{1,2}/\d{1,2}(?:/\d{2,4})?)', re.IGNORECASE)


def parsear_tarjeta(etiqueta, texto=''):
    """
    Convierte el aria-label de la tarjeta de un anuncio en un diccionario, o None si no es un anuncio.
    'Morado - Celeste, 12 $, Disponible, Publicado el 28/12/2025, Publicado en Marketplace, 0 clics...'
    """
    m = PATRON_ETIQUETA.match(re.sub(r'\s+', ' ', etiqueta or '').strip())
    if not m:
        return None

    titulo = m.group('titulo').strip()
    precio_texto = re.sub(r'[^\d.,]', '', m.group('precio'))
    precio = _numero_precio(precio_texto)
    estado_bruto = m.group('estado').strip()
    fecha = PATRON_FECHA.search(m.group('resto'))
    fecha_texto = fecha.group(1) if fecha else ''

    return {
        'titulo': titulo,
        'precio': precio,
        'estado': _estado_de_facebook(estado_bruto, texto),
        'estado_bruto': estado_bruto,
        'fecha': fecha_texto,
        'firma': f"{titulo}|{fecha_texto}",
    }


def _numero_precio(texto):
    """'12' → '12' · '37,50' → '37.50' · '1.200' → '1200' (punto de miles)"""
    texto = texto.strip('.,')
    if not texto:
        return ''
    if ',' in texto and '.' in texto:
        texto = texto.replace('.', '').replace(',', '.') if texto.rfind(',') > texto.rfind('.') else texto.replace(',', '')
    elif ',' in texto:
        texto = texto.replace(',', '.') if len(texto.split(',')[-1]) <= 2 else texto.replace(',', '')
    elif '.' in texto and len(texto.split('.')[-1]) == 3:
        texto = texto.replace('.', '')
    try:
        numero = float(texto)
    except ValueError:
        return ''
    return str(int(numero)) if numero == int(numero) else f"{numero:.2f}"


def _estado_de_facebook(estado_bruto, texto_tarjeta=''):
    if 'parece un duplicado' in _sin_acentos(texto_tarjeta).lower():
        return ESTADO_RECHAZADO
    e = _sin_acentos(estado_bruto).lower()
    if 'vendid' in e or 'agotad' in e:
        return ESTADO_VENDIDO
    if 'pendient' in e:
        return ESTADO_PENDIENTE
    if 'borrador' in e:
        return ESTADO_BORRADOR
    if 'disponible' in e:
        return ESTADO_DISPONIBLE
    return estado_bruto.strip().capitalize() or ESTADO_DISPONIBLE


def estado_del_producto(texto):
    """'Nuevo' → 'Nuevo' · 'Usado - como nuevo' → 'Usado - Como nuevo'. Si no se reconoce, 'Nuevo'."""
    comparable = _sin_acentos(texto or '').lower().strip()
    for estado in ESTADOS_ARTICULO:
        if _sin_acentos(estado).lower() == comparable:
            return estado
    return 'Nuevo'


def planificar(anuncios, locales):
    """
    Decide qué hacer con cada anuncio de Facebook (sin tocar nada).

    anuncios: [{'titulo', 'precio', 'estado', 'firma', ...}]  (los de la lista de Facebook)
    locales:  {numero: datos del artículo}
    Devuelve (acciones, eliminados):
      acciones   = [{'anuncio', 'accion', 'numero', 'motivo'}]  con accion en
                   'actualizar' (ya vinculado: solo estado) · 'vincular' (existe un artículo con ese título) ·
                   'importar' (artículo nuevo)
      eliminados = [numero] de artículos vinculados cuyo anuncio ya no está en Facebook
    Para 'vincular' e 'importar' hace falta abrir el anuncio para saber su id; eso lo resuelve el navegador.
    """
    por_firma = {n: d.get('firma_marketplace', '') for n, d in locales.items() if d.get('firma_marketplace')}
    firma_a_numero = {f: n for n, f in por_firma.items()}
    usados = set()
    acciones = []

    for anuncio in anuncios:
        numero = firma_a_numero.get(anuncio['firma'])
        if numero is not None and numero not in usados:
            usados.add(numero)
            acciones.append({'anuncio': anuncio, 'accion': 'actualizar', 'numero': numero, 'motivo': 'ya vinculado'})
        else:
            acciones.append({'anuncio': anuncio, 'accion': None, 'numero': None, 'motivo': ''})

    # Los que no se reconocieron por firma: buscar un artículo sin vincular con el mismo título.
    # Primero los que además tienen el mismo precio y después los que solo coinciden en el título.
    def sin_vincular(anuncio, mismo_precio):
        titulo = normalizar_titulo(anuncio['titulo'])
        return [n for n, d in locales.items()
                if n not in usados and not d.get('id_marketplace') and normalizar_titulo(d.get('titulo', '')) == titulo
                and (not mismo_precio or _numero_precio(str(d.get('precio', ''))) == anuncio['precio'])]

    for exigir_precio in (True, False):
        for accion in acciones:
            if accion['accion']:
                continue
            candidatos = sin_vincular(accion['anuncio'], exigir_precio)
            if candidatos:
                usados.add(candidatos[0])
                accion.update(accion='vincular', numero=candidatos[0], motivo='ya existe un artículo con ese título')

    for accion in acciones:
        if not accion['accion']:
            accion.update(accion='importar', motivo='anuncio nuevo para la app')

    eliminados = [n for n, d in locales.items()
                  if (d.get('id_marketplace') or d.get('firma_marketplace')) and n not in usados
                  and d.get('estado_marketplace') != ESTADO_ELIMINADO]
    return acciones, eliminados


# ============================================================
# NAVEGADOR
# ============================================================

class SincronizadorMarketplace:
    """Lee 'Tus publicaciones' de Marketplace y las refleja en la carpeta de productos"""

    # Tarjetas: botón con aria-label 'Título, 12 $, Disponible, Publicado el ...'; la tarjeta es el contenedor más
    # alto que aún tiene poco texto (así incluye el aviso 'Parece un duplicado').
    JS_TARJETAS = """
    const resultado = [];
    const vistos = new Set();
    document.querySelectorAll("[role='button'][aria-label]").forEach(b => {
        const etiqueta = b.getAttribute('aria-label') || '';
        if (!/ (Publicado|Renovado|Actualizado) el /.test(etiqueta) && !/clics? en la publicaci/.test(etiqueta)) return;
        if (etiqueta.startsWith('Número de veces')) return;
        let c = b;
        for (let i = 0; i < 6 && c.parentElement; i++) {
            if ((c.parentElement.innerText || '').length > 500) break;
            if (c.parentElement.querySelectorAll("[aria-label^='Marcar como agotado']").length > 1) break;
            c = c.parentElement;
        }
        if (vistos.has(c)) return;
        vistos.add(c);
        resultado.push({etiqueta: etiqueta, texto: (c.innerText || '').slice(0, 400)});
    });
    return resultado;
    """

    JS_BAJAR = """
    const botones = Array.from(document.querySelectorAll("[role='button'][aria-label^='Más opciones de']"));
    if (botones.length) botones[botones.length - 1].scrollIntoView({block: 'end'});
    // Bajar también toda la página y cualquier contenedor con scroll
    window.scrollTo(0, document.body.scrollHeight);
    const base = document.scrollingElement || document.documentElement;
    base.scrollTop = base.scrollHeight;
    Array.from(document.querySelectorAll('div')).forEach(d => {
        if (d.scrollHeight > d.clientHeight + 50 && d.clientHeight > 200) {
            const o = getComputedStyle(d).overflowY;
            if (o === 'auto' || o === 'scroll') d.scrollTop = d.scrollHeight;
        }
    });
    // Si hay un botón 'Ver más', pulsarlo
    const ver = Array.from(document.querySelectorAll("[role='button']")).find(
        x => ((x.innerText || '').trim() === 'Ver más'));
    if (ver) ver.click();
    return botones.length;
    """

    # Abre el menú '···' del anuncio cuyo título es arguments[0] (la n-ésima coincidencia: arguments[1])
    JS_ABRIR_MENU = """
    const titulo = arguments[0], n = arguments[1];
    const botones = Array.from(document.querySelectorAll("[role='button'][aria-label]")).filter(
        b => (b.getAttribute('aria-label') || '') === 'Más opciones de ' + titulo);
    const b = botones[Math.min(n, botones.length - 1)];
    if (!b) return false;
    b.scrollIntoView({block: 'center'});
    b.click();
    return true;
    """

    JS_VER_PUBLICACION = """
    const o = Array.from(document.querySelectorAll("[role='menuitem'], [role='menu'] [role='button'], [role='menu'] div"))
        .find(e => (e.innerText || '').trim() === 'Ver publicación');
    if (!o) return false;
    o.click();
    return true;
    """

    JS_EXPANDIR = """
    Array.from(document.querySelectorAll("[role='button'], span")).forEach(e => {
        if (/^(Ver más|See more)$/i.test((e.innerText || '').trim())) e.click();
    });
    """

    # Descripción = el texto más largo entre 'Detalles' y 'Información del vendedor'
    JS_DETALLE = """
    const spans = Array.from(document.querySelectorAll('span'));
    const texto = e => (e.innerText || '').trim();
    const ini = spans.find(s => texto(s) === 'Detalles');
    const fin = spans.find(s => /^(Información del vendedor|Detalles del vendedor)$/.test(texto(s)));
    let descripcion = '', estado = '';
    if (ini) {
        let dentro = false;
        spans.forEach((s, i) => {
            if (s === ini) { dentro = true; return; }
            if (s === fin) dentro = false;
            if (!dentro || s.children.length > 0) return;
            const t = texto(s);
            if (t === 'Estado' && spans[i + 1]) estado = texto(spans[i + 1]);
            if (t.length > descripcion.length && s.getAttribute('dir') === 'auto' && t !== estado) descripcion = t;
        });
    }
    const fotos = Array.from(document.querySelectorAll("img[alt^='Foto de producto']"))
        .map(i => i.getAttribute('src') || '').filter(Boolean);
    return {descripcion: descripcion, estado: estado, fotos: fotos, url: location.href};
    """

    JS_SIGUIENTE_FOTO = """
    const b = Array.from(document.querySelectorAll("[role='button'][aria-label]")).find(
        e => /^(Siguiente|Next)/i.test(e.getAttribute('aria-label')));
    if (!b) return false;
    b.click();
    return true;
    """

    def __init__(self, config=None):
        self.config = config or {}
        self.fb = PublicadorMarketplace(self.config)
        self.driver = None

    def iniciar_navegador(self):
        self.fb.iniciar_navegador()
        self.driver = self.fb.driver
        self.driver.set_script_timeout(30)
        return self.fb.esperar_login_facebook()

    # ------------------------------------------------------------ lista

    def ir_a_la_lista(self):
        """Abre 'Tus publicaciones' y espera a que aparezcan los anuncios"""
        self.driver.get(URL_VENTA)
        for _ in range(40):
            time.sleep(1)
            if self.driver.execute_script(self.JS_TARJETAS):
                time.sleep(1)
                return True
        return False

    def _bajar_como_persona(self):
        """Baja con la rueda del ratón y la tecla Fin (Facebook solo carga más con un scroll real)"""
        try:
            self.driver.execute_script(self.JS_BAJAR)
            for _ in range(4):
                ActionChains(self.driver).scroll_by_amount(0, 800).perform()
                time.sleep(0.4)
            ActionChains(self.driver).send_keys(Keys.END).perform()
        except Exception:
            try:
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            except Exception:
                pass

    def leer_anuncios(self, max_bajadas=60):
        """Baja hasta cargar todos los anuncios y devuelve [{'titulo', 'precio', 'estado', 'fecha', 'firma', 'n'}]"""
        anterior, iguales = -1, 0
        for _ in range(max_bajadas):
            cantidad = len(self.driver.execute_script(self.JS_TARJETAS) or [])
            altura = self.driver.execute_script("return document.body.scrollHeight") or 0
            if cantidad != anterior:
                print(f"   Cargando anuncios... {cantidad} (altura de página: {altura})")
            iguales = iguales + 1 if cantidad == anterior else 0
            if iguales >= 4:
                break
            anterior = cantidad
            self._bajar_como_persona()
            time.sleep(3)

        if anterior < 12:
            try:
                self.driver.save_screenshot('error_sincronizar.png')
                print("   ⚠️  Pocos anuncios leídos; captura guardada en error_sincronizar.png")
            except Exception:
                pass

        anuncios, vistos, repetidos = [], {}, {}
        for tarjeta in self.driver.execute_script(self.JS_TARJETAS) or []:
            anuncio = parsear_tarjeta(tarjeta['etiqueta'], tarjeta['texto'])
            if not anuncio:
                continue
            # Facebook repite en 'Requieren atención' los anuncios que también salen en 'Todas las publicaciones'
            if tarjeta['etiqueta'] in vistos:
                continue
            repetidos[anuncio['titulo']] = repetidos.get(anuncio['titulo'], -1) + 1
            anuncio['n'] = repetidos[anuncio['titulo']]      # n-ésimo anuncio con ese mismo título
            vistos[tarjeta['etiqueta']] = True
            anuncios.append(anuncio)
        return anuncios

    # ------------------------------------------------------------ un anuncio

    def obtener_id(self, anuncio):
        """Abre ··· → 'Ver publicación' y devuelve el id del anuncio (o None). Deja el anuncio abierto."""
        for _ in range(2):
            if not self.driver.execute_script(self.JS_ABRIR_MENU, anuncio['titulo'], anuncio['n']):
                return None
            time.sleep(1)
            if not self.driver.execute_script(self.JS_VER_PUBLICACION):
                self.driver.execute_script("document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape'}));")
                time.sleep(1)
                continue
            for _ in range(10):
                time.sleep(1)
                m = re.search(r'/marketplace/item/(\d+)', self.driver.current_url)
                if m:
                    return m.group(1)
        return None

    def volver_a_la_lista(self, esperadas):
        """Cierra el anuncio y vuelve a 'Tus publicaciones' con los anuncios cargados"""
        self.driver.back()
        for _ in range(8):
            time.sleep(1)
            if '/marketplace/you/selling' in self.driver.current_url and \
                    len(self.driver.execute_script(self.JS_TARJETAS) or []) >= esperadas:
                return True
        if not self.ir_a_la_lista():
            return False
        self.leer_anuncios()
        return True

    def leer_detalle(self, id_anuncio):
        """Lee descripción, estado del producto y fotos del anuncio, abriéndolo por su dirección en una pestaña nueva"""
        principal = self.driver.current_window_handle
        self.driver.switch_to.new_window('tab')
        try:
            self.driver.get(URL_ANUNCIO.format(id_anuncio))
            detalle = None
            for _ in range(20):
                time.sleep(1)
                detalle = self.driver.execute_script(self.JS_DETALLE)
                if detalle['fotos'] or detalle['descripcion']:
                    break
            self.driver.execute_script(self.JS_EXPANDIR)
            time.sleep(1)
            detalle = self.driver.execute_script(self.JS_DETALLE) or detalle

            fotos = list(dict.fromkeys(detalle['fotos']))
            for _ in range(9):                       # recorre el carrusel si el anuncio tiene varias fotos
                if not self.driver.execute_script(self.JS_SIGUIENTE_FOTO):
                    break
                time.sleep(1)
                nuevas = [f for f in self.driver.execute_script(self.JS_DETALLE)['fotos'] if f not in fotos]
                if not nuevas:
                    break
                fotos += nuevas
            detalle['fotos'] = fotos
            return detalle
        finally:
            self.driver.close()
            self.driver.switch_to.window(principal)

    @staticmethod
    def descargar_foto(url, ruta):
        peticion = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(peticion, timeout=30) as respuesta, open(ruta, 'wb') as f:
            f.write(respuesta.read())

    # ------------------------------------------------------------ guardar en el Gestor

    @staticmethod
    def _carpeta_nueva():
        """Número de la carpeta donde guardar un anuncio nuevo: una vacía (o con el ejemplo) o una al final"""
        for numero in numeros_articulos():
            datos = leer_datos_articulo(numero, avisar=False) or {}
            if datos.get('titulo', '') in ('', 'Ejemplo Producto') and not obtener_imagenes_articulo(numero):
                return numero
        return (max(numeros_articulos()) if numeros_articulos() else 0) + 1

    def guardar_importado(self, anuncio, id_anuncio, detalle, categoria=''):
        numero = self._carpeta_nueva()
        datos = {clave: '' for clave in CLAVES_DATOS_ARTICULO}
        datos.update({
            'titulo': anuncio['titulo'], 'precio': anuncio['precio'], 'descripcion': detalle['descripcion'],
            'categoria': categoria,
            'estado': estado_del_producto(detalle['estado']), 'disponibilidad': 'Publicar como disponible',
            'id_marketplace': id_anuncio, 'estado_marketplace': anuncio['estado'], 'firma_marketplace': anuncio['firma'],
        })
        guardar_datos_articulo(numero, datos)

        carpeta_imagenes = os.path.join(_carpeta_articulo(numero), 'imagenes')
        descargadas = 0
        for k, url in enumerate(detalle['fotos'][:10], 1):
            try:
                self.descargar_foto(url, os.path.join(carpeta_imagenes, f"imagen_{k}.jpg"))
                descargadas += 1
            except Exception as e:
                print(f"      ⚠️  No se pudo descargar la foto {k}: {e}")
        return numero, descargadas

    @staticmethod
    def actualizar_datos(numero, **cambios):
        datos = leer_datos_articulo(numero, avisar=False) or {}
        datos.update(cambios)
        guardar_datos_articulo(numero, datos)

    # ------------------------------------------------------------

    def ejecutar(self, modo_prueba=False, solo_vincular=False):
        """
        Sincroniza el Gestor con 'Tus publicaciones'. Con modo_prueba solo lee y muestra lo que haría
        (abre como máximo 2 anuncios para probar la lectura) y no crea ni cambia ningún artículo.
        Con solo_vincular marca el estado de tus productos pero no importa los anuncios que no tengas en la app.
        """
        try:
            if not self.iniciar_navegador():
                return None
            print("📥 Abriendo 'Tus publicaciones' de Marketplace...")
            if not self.ir_a_la_lista():
                print("❌ No aparecieron anuncios (¿no tienes publicaciones o cambió la página?)")
                return None

            print("📜 Leyendo anuncios...")
            anuncios = self.leer_anuncios()
            print(f"   {len(anuncios)} anuncio(s) en Facebook")
            if not anuncios:
                return None

            locales = {n: leer_datos_articulo(n, avisar=False) or {} for n in numeros_articulos()}
            acciones, eliminados = planificar(anuncios, locales)

            print("\n📋 Qué se hará con cada anuncio:")
            for a in acciones:
                an = a['anuncio']
                destino = f"Articulo_{a['numero']}" if a['numero'] else "carpeta nueva"
                print(f"   • {an['titulo']} · {an['precio']} $ · {an['estado']}  →  {a['accion']} ({destino})")
            for numero in eliminados:
                print(f"   • Articulo_{numero} ({locales[numero].get('titulo', '')}) → ya no está en Facebook")

            self._aplicar(acciones, eliminados, locales, len(anuncios), modo_prueba, solo_vincular)
            return acciones
        finally:
            if self.driver:
                time.sleep(2)
                try:
                    self.driver.quit()
                except Exception:
                    pass
                self.driver = None

    def _aplicar(self, acciones, eliminados, locales, total, modo_prueba, solo_vincular=False):
        resumen = {'actualizados': 0, 'vinculados': 0, 'importados': 0, 'eliminados': 0, 'fallidos': 0}
        pendientes = [a for a in acciones if a['accion'] in ('vincular', 'importar')]
        if solo_vincular:
            omitidos = [a for a in pendientes if a['accion'] == 'importar']
            pendientes = [a for a in pendientes if a['accion'] == 'vincular']
            if omitidos:
                print(f"\nℹ️  Solo vincular: {len(omitidos)} anuncio(s) que no tienes en la app no se importan")
        categoria = categoria_mas_usada(locales)

        if modo_prueba:
            print("\n🧪 PRUEBA (no se crea ni se cambia ningún artículo)")
            pruebas = pendientes[:2]
        else:
            pruebas = pendientes[:MAX_ANUNCIOS_NUEVOS_POR_EJECUCION]
            if len(pendientes) > len(pruebas):
                print(f"\n⚠️  Hay {len(pendientes)} anuncios nuevos; se procesan {len(pruebas)} ahora y el resto en la próxima sincronización")

        for a in acciones:
            if a['accion'] == 'actualizar' and not modo_prueba:
                self.actualizar_datos(a['numero'], estado_marketplace=a['anuncio']['estado'])
                resumen['actualizados'] += 1

        for a in pruebas:
            an = a['anuncio']
            print(f"\n🔎 {an['titulo']}")
            id_anuncio = self.obtener_id(an)
            if not id_anuncio:
                print("   ❌ No se pudo abrir el anuncio para leer su id")
                resumen['fallidos'] += 1
                self.volver_a_la_lista(total)
                continue
            print(f"   id: {id_anuncio}")

            if a['accion'] == 'vincular':
                if not modo_prueba:
                    self.actualizar_datos(a['numero'], id_marketplace=id_anuncio,
                                          estado_marketplace=an['estado'], firma_marketplace=an['firma'])
                    resumen['vinculados'] += 1
                    print(f"   ✅ Vinculado con Articulo_{a['numero']}")
                else:
                    print(f"   (se vincularía con Articulo_{a['numero']})")
            else:
                detalle = self.leer_detalle(id_anuncio)
                print(f"   estado del producto: {detalle['estado'] or '(no se leyó)'} · fotos: {len(detalle['fotos'])}")
                print(f"   descripción: {(detalle['descripcion'] or '(no se leyó)')[:90]!r}")
                if not modo_prueba:
                    numero, fotos = self.guardar_importado(an, id_anuncio, detalle, categoria)
                    resumen['importados'] += 1
                    print(f"   ✅ Importado como Articulo_{numero} ({fotos} foto(s))")
            self.volver_a_la_lista(total)

        if not modo_prueba:
            # Los productos que vienen de Marketplace sin categoría reciben la más usada (se puede cambiar en el Gestor)
            for numero, datos in locales.items():
                if datos.get('id_marketplace') and not (datos.get('categoria') or '').strip():
                    self.actualizar_datos(numero, categoria=categoria)
            for numero in eliminados:
                self.actualizar_datos(numero, estado_marketplace=ESTADO_ELIMINADO)
                resumen['eliminados'] += 1
            print(f"\n📊 Actualizados: {resumen['actualizados']} · Vinculados: {resumen['vinculados']} · "
                  f"Importados: {resumen['importados']} · Eliminados en Facebook: {resumen['eliminados']} · "
                  f"Fallidos: {resumen['fallidos']}")
