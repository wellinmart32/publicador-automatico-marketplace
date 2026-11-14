"""
Atender interesados de Facebook Marketplace (lectura del inbox).

Fase 4c: lista las conversaciones de la Bandeja de entrada de Marketplace, descarta las que no corresponden
(producto que no es de tu catálogo o conversación demasiado antigua) y sabe abrir, leer y cerrar un chat.
El envío de respuestas y el seguimiento de cada interesado llegan en las fases siguientes.

Estructura de Facebook (nov 2026, interfaz en español):
  - Inbox: https://www.facebook.com/marketplace/inbox/
  - Cada conversación de la lista es un <div role="button" tabindex="0"> sin aria-label, con el texto
    "Nombre · Producto", el último mensaje y la fecha, cada uno en su línea.
  - Al hacer clic se abre un chat emergente (abajo a la derecha) con:
      <div role="log" aria-label="Mensajes de la conversación llamada Nombre · Producto">
        <div role="button" aria-label="Escribir, Mensaje enviado a las 28 de mayo de 2026, 13:06 por Axel: texto">
      y un cuadro de texto <div role="textbox" aria-label="Escribe en Nombre · Producto">.
    El botón para cerrarlo tiene aria-label="Cerrar chat".
"""

import re
import time
import unicodedata
from datetime import date, datetime, timedelta

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from compartido.gestor_archivos import extraer_celular_ecuador
from publicadores.publicador_marketplace import PublicadorMarketplace


URL_INBOX = "https://www.facebook.com/marketplace/inbox/"

MESES = {'ene': 1, 'feb': 2, 'mar': 3, 'abr': 4, 'may': 5, 'jun': 6,
         'jul': 7, 'ago': 8, 'sep': 9, 'set': 9, 'oct': 10, 'nov': 11, 'dic': 12}
DIAS_SEMANA = {'lun': 0, 'mar': 1, 'mie': 2, 'jue': 3, 'vie': 4, 'sab': 5, 'dom': 6}


# ============================================================
# FUNCIONES DE TEXTO (no dependen del navegador)
# ============================================================

def _sin_acentos(texto):
    return ''.join(c for c in unicodedata.normalize('NFKD', texto) if not unicodedata.combining(c))


def normalizar_titulo(texto):
    """Título comparable: minúsculas, sin acentos, emojis ni símbolos ('▫️ Verde - Morado' → 'verdemorado')"""
    return re.sub(r'[^a-z0-9]', '', _sin_acentos(texto or '').lower())


def producto_coincide(producto_chat, titulos_normalizados):
    """True si el producto del chat es uno de los títulos (el chat puede traer el título cortado con '…')"""
    producto = normalizar_titulo(producto_chat)
    if not producto:
        return False
    for titulo in titulos_normalizados:
        if producto == titulo:
            return True
        if len(producto) >= 6 and len(titulo) >= 6 and (producto in titulo or titulo in producto):
            return True
    return False


def fecha_de_lista(texto, hoy=None):
    """
    Fecha de una conversación según como la muestra la lista: '26 jun.', '8 jun. 2025', 'Ayer', '10:35',
    'mar' (día de la semana), '5 d', '1 sem'. Devuelve un date o None si no la reconoce.
    """
    hoy = hoy or date.today()
    t = _sin_acentos((texto or '').strip().lower())
    if not t:
        return None

    if t == 'hoy':
        return hoy
    if t == 'ayer':
        return hoy - timedelta(days=1)
    if re.fullmatch(r'\d{1,2}:\d{2}\s*(?:[ap]\.?\s?m\.?)?', t):
        return hoy

    m = re.fullmatch(r'(\d+)\s*(min|m|h|d|sem|s|w)\.?', t)
    if m:
        cantidad, unidad = int(m.group(1)), m.group(2)
        if unidad in ('min', 'm', 'h'):
            return hoy
        if unidad == 'd':
            return hoy - timedelta(days=cantidad)
        return hoy - timedelta(weeks=cantidad)

    m = re.fullmatch(r'(\d{1,2})\s+(?:de\s+)?([a-z]{3,10})\.?(?:\s+(?:de\s+)?(\d{4}))?', t)
    if m and m.group(2)[:3] in MESES:
        dia, mes = int(m.group(1)), MESES[m.group(2)[:3]]
        try:
            if m.group(3):
                return date(int(m.group(3)), mes, dia)
            fecha = date(hoy.year, mes, dia)
            return fecha if fecha <= hoy else date(hoy.year - 1, mes, dia)
        except ValueError:
            return None

    m = re.fullmatch(r'([a-z]{3,9})\.?', t)
    if m and m.group(1)[:3] in DIAS_SEMANA:
        atras = (hoy.weekday() - DIAS_SEMANA[m.group(1)[:3]]) % 7 or 7
        return hoy - timedelta(days=atras)

    return None


def separar_chat(texto):
    """
    Del texto de una conversación de la lista saca nombre, producto, último mensaje y fecha.
    Facebook muestra el título en varias líneas ('Jesus' / '· Verde - Morado') o en una sola ('Jesus · Verde - Morado').
    Devuelve None si no tiene el formato 'Nombre · Producto'.
    """
    lineas = [re.sub(r'\s+', ' ', l).strip() for l in (texto or '').split('\n')]
    lineas = [l for l in lineas if l]

    indice = next((n for n, l in enumerate(lineas[:4]) if '·' in l), None)
    if indice is None or len(lineas) < 2:
        return None

    antes, _, despues = lineas[indice].partition('·')
    nombre = re.sub(r'\s+', ' ', ' '.join(lineas[:indice] + [antes])).strip()
    producto = despues.strip()
    if not nombre or not producto:
        return None

    titulo = f"{nombre} · {producto}"
    resto = lineas[indice + 1:]

    fecha_texto = ''
    if len(resto) >= 2 and fecha_de_lista(resto[-1]) is not None:
        fecha_texto = resto.pop()
    elif resto:
        # La fecha puede venir pegada al final del mensaje: 'Hola · 26 jun.'
        m = re.search(r'\s·?\s*(\d{1,2}\s+[A-Za-zÁÉÍÓÚáéíóú]{3,4}\.?|Ayer|Hoy|\d+\s?(?:min|h|d|sem))$', resto[-1])
        if m and fecha_de_lista(m.group(1)) is not None:
            fecha_texto = m.group(1)
            resto[-1] = resto[-1][:m.start()].rstrip()

    return {
        'titulo': titulo,
        'nombre': nombre,
        'producto': producto,
        'ultimo_mensaje': ' '.join(resto).strip(),
        'fecha_texto': fecha_texto,
        'fecha': fecha_de_lista(fecha_texto),
    }


_MESES_LARGOS = {'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6, 'julio': 7,
                 'agosto': 8, 'septiembre': 9, 'setiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12}


def parsear_mensaje(aria):
    """
    Convierte el aria-label de un mensaje en un diccionario:
    'Escribir, Mensaje enviado a las 28 de mayo de 2026, 13:06 por Axel: 0992213123'
      → {'fecha': datetime(2026, 5, 28, 13, 6), 'autor': 'Axel', 'es_mio': False, 'texto': '0992213123', ...}
    Devuelve None si no es un mensaje.
    """
    m = re.search(r'Mensaje enviado a las (?P<fecha>.+?) por (?P<autor>.+?)(?::\s*(?P<texto>.*))?$', aria or '', re.DOTALL)
    if not m:
        return None

    fecha = None
    mf = re.search(r'(\d{1,2}) de ([a-záéíóú]+) de (\d{4}),?\s+(\d{1,2}):(\d{2})', m.group('fecha'))
    if mf:
        mes = _MESES_LARGOS.get(_sin_acentos(mf.group(2).lower()))
        if mes:
            try:
                fecha = datetime(int(mf.group(3)), mes, int(mf.group(1)), int(mf.group(4)), int(mf.group(5)))
            except ValueError:
                fecha = None

    texto = (m.group('texto') or '')
    texto = re.sub(r'\n?\s*Has enviado\s*\n?', '\n', texto).strip()
    autor = m.group('autor').strip()

    return {
        'fecha': fecha,
        'autor': autor,
        'es_mio': _sin_acentos(autor.lower()) in ('tu', 'you'),
        'texto': texto,
        'es_sistema': texto.lower().endswith('ha iniciado este chat.'),
    }


def titulos_de_productos():
    """
    Títulos (normalizados) de los productos que se publican con esta app: los artículos de la carpeta de
    productos más los que ya se publicaron según el registro de publicaciones.
    """
    from compartido.gestor_archivos import listar_articulos_con_titulo
    titulos = set()
    for _, titulo, _ in listar_articulos_con_titulo():
        if titulo:
            titulos.add(normalizar_titulo(titulo))
    try:
        from gestor_registro import GestorRegistro
        for publicacion in GestorRegistro().registro.get('historial_completo', []):
            if publicacion.get('estado') == 'exitoso' and publicacion.get('titulo'):
                titulos.add(normalizar_titulo(publicacion['titulo']))
    except Exception:
        pass
    titulos.discard('')
    return titulos


def filtrar_chats(chats, titulos_normalizados, dias_maximos, hoy=None):
    """
    Separa las conversaciones en (relevantes, descartadas).
    descartadas = [(chat, motivo)]. Una conversación con fecha que no se pudo leer se deja pasar:
    la fecha exacta se vuelve a comprobar con los mensajes al abrir el chat.
    """
    hoy = hoy or date.today()
    relevantes, descartadas = [], []
    for chat in chats:
        if not producto_coincide(chat['producto'], titulos_normalizados):
            descartadas.append((chat, "el producto no es de tu catálogo"))
            continue
        if chat['fecha'] is not None and (hoy - chat['fecha']).days > dias_maximos:
            descartadas.append((chat, f"última actividad hace más de {dias_maximos} días ({chat['fecha_texto']})"))
            continue
        relevantes.append(chat)
    return relevantes, descartadas


# ============================================================
# ESTADO DE LA CONVERSACIÓN Y MENSAJES A ENVIAR (no dependen del navegador)
# ============================================================

# Orden de comparación: si dos plantillas se parecen, gana la que más texto fijo coincide
PLANTILLAS_DE_RESPUESTA = ('DESPEDIDA', 'CONFIRMACION', 'INSISTIR_CELULAR', 'PEDIR_CELULAR')
PALABRAS_PEDIDO = re.compile(r'n[uú]mero|celular|whatsapp|tel[eé]fono', re.IGNORECASE)


def _texto_comparable(texto):
    """Texto sin emojis, signos ni acentos, en minúsculas y con espacios simples (Facebook puede cambiar emojis y comillas)"""
    limpio = re.sub(r'[^a-z0-9]+', ' ', _sin_acentos(texto or '').lower())
    return limpio.strip()


def _partes_fijas(plantilla):
    """Trozos de la plantilla que no son variables ({nombre}, {producto}...), ya comparables"""
    partes = (_texto_comparable(p) for p in re.split(r'\{\w+\}', plantilla or ''))
    return [p for p in partes if len(p) >= 3]


def tipo_de_mensaje_mio(texto, plantillas):
    """
    Qué plantilla es un mensaje que yo envié: 'PEDIR_CELULAR', 'INSISTIR_CELULAR', 'CONFIRMACION', 'DESPEDIDA'
    o None si lo escribí a mano. Compara los trozos fijos de cada plantilla, en orden, con el mensaje.
    """
    comparable = _texto_comparable(texto)
    mejor, mejor_largo = None, 0
    for clave in PLANTILLAS_DE_RESPUESTA:
        partes = _partes_fijas(plantillas.get(clave, ''))
        if not partes:
            continue
        posicion, coincide = 0, True
        for parte in partes:
            indice = comparable.find(parte, posicion)
            if indice < 0:
                coincide = False
                break
            posicion = indice + len(parte)
        largo = sum(len(p) for p in partes)
        if coincide and largo > mejor_largo:
            mejor, mejor_largo = clave, largo
    return mejor


def _es_ruido(mensaje):
    """Mensajes que no cuentan: avisos de Facebook y mensajes sin texto (fotos, tarjeta del producto)"""
    texto = (mensaje['texto'] or '').strip()
    if mensaje['es_sistema'] or not texto:
        return True
    return _sin_acentos(texto.lower()).endswith('esta esperando tu respuesta.')


def analizar_conversacion(mensajes, plantillas, max_insistencias):
    """
    Reconstruye en qué punto está una conversación leyendo TODO su historial (así funciona también con
    conversaciones que atendiste a mano) y decide qué hay que hacer.

    Estados: 'nuevo' · 'celular_pedido' · 'celular_recibido' · 'confirmado' · 'abandonado' · 'revisar' (varios números distintos)
    Acciones: 'PEDIR_CELULAR' · 'INSISTIR_CELULAR' · 'CONFIRMACION' · 'DESPEDIDA' · None (no hacer nada)

    Un mensaje tuyo que no es plantilla pero habla de número/celular/whatsapp cuenta como un pedido de celular.
    Si el cliente escribe después de una despedida, la conversación se reinicia como nueva.
    """
    estado, pedidos, celular = 'nuevo', 0, None
    celulares = []           # celulares distintos que mandó el cliente (desde el último reinicio)
    pendiente = False        # el último mensaje con texto es del cliente y aún no se le respondió
    reiniciada = False

    for m in mensajes:
        if _es_ruido(m):
            continue
        texto = m['texto'].strip()

        if m['es_mio']:
            tipo = tipo_de_mensaje_mio(texto, plantillas)
            if tipo in ('PEDIR_CELULAR', 'INSISTIR_CELULAR') or (tipo is None and PALABRAS_PEDIDO.search(texto)):
                pedidos += 1
            elif tipo == 'CONFIRMACION':
                estado = 'confirmado'
            elif tipo == 'DESPEDIDA':
                estado = 'abandonado'
            pendiente = False
        else:
            if estado == 'abandonado':
                estado, pedidos, celular, reiniciada = 'nuevo', 0, None, True
                celulares = []
            if estado == 'confirmado':
                continue
            encontrado = extraer_celular_ecuador(texto)
            if encontrado:
                celular = encontrado
                if encontrado not in celulares:
                    celulares.append(encontrado)
            pendiente = True

    insistencias = max(pedidos - 1, 0)
    resultado = {'estado': estado, 'accion': None, 'celular': celular, 'pedidos': pedidos,
                 'insistencias': insistencias, 'reiniciada': reiniciada, 'motivo': '', 'celulares': celulares}

    if estado == 'confirmado':
        resultado['motivo'] = "ya se le confirmó al cliente"
    elif estado == 'abandonado':
        resultado['motivo'] = "ya se despidió y el cliente no ha vuelto a escribir"
    elif len(celulares) >= 2:
        resultado['estado'] = 'revisar'
        resultado['motivo'] = ("el cliente mandó varios números (" + ', '.join(celulares) +
                               "); revísalo a mano para no avisar un número equivocado")
    elif celular:
        resultado['estado'] = 'celular_recibido'
        if pendiente:
            resultado['accion'] = 'CONFIRMACION'
        else:
            resultado['motivo'] = "ya hay celular y ya le respondiste (a mano)"
    elif not pendiente:
        resultado['estado'] = 'celular_pedido' if pedidos else 'nuevo'
        resultado['motivo'] = "esperando respuesta del cliente"
    elif pedidos == 0:
        resultado['accion'] = 'PEDIR_CELULAR'
    elif insistencias < max_insistencias:
        resultado['estado'] = 'celular_pedido'
        resultado['accion'] = 'INSISTIR_CELULAR'
    else:
        resultado['estado'] = 'celular_pedido'
        resultado['accion'] = 'DESPEDIDA'

    return resultado


def rellenar_plantilla(plantilla, **valores):
    """Reemplaza {nombre}, {producto}, {celular}, {vendedor}; una variable desconocida se deja tal cual"""
    return re.sub(r'\{(\w+)\}', lambda m: str(valores.get(m.group(1), m.group(0))), plantilla or '')


def titulo_completo(producto_chat):
    """Título real del producto (el chat puede traerlo cortado con '…'); si no se encuentra, el del chat"""
    from compartido.gestor_archivos import listar_articulos_con_titulo
    candidatos = [t for _, t, _ in listar_articulos_con_titulo() if t]
    try:
        from gestor_registro import GestorRegistro
        candidatos += [p['titulo'] for p in GestorRegistro().registro.get('historial_completo', [])
                       if p.get('estado') == 'exitoso' and p.get('titulo')]
    except Exception:
        pass
    for titulo in candidatos:
        if producto_coincide(producto_chat, {normalizar_titulo(titulo)}):
            return titulo
    return producto_chat


def texto_a_enviar(accion, chat, analisis, plantillas, config):
    """Mensaje final (con nombre, producto, celular y vendedor ya puestos) para la acción decidida"""
    nombre = (chat['nombre'].split() or [''])[0]
    return rellenar_plantilla(
        plantillas.get(accion, ''),
        nombre=nombre,
        producto=titulo_completo(chat['producto']),
        celular=analisis.get('celular') or '',
        vendedor=config.get('nombre_vendedor') or 'nuestro asesor')


# ============================================================
# NAVEGADOR
# ============================================================

class AtendedorInteresados:
    """Lee y gestiona las conversaciones de la Bandeja de entrada de Marketplace"""

    # Conversaciones de la lista: botones sin aria-label, de varias líneas, con 'Nombre · Producto' arriba
    JS_CANDIDATOS = """
    function lineasDe(el) {
        return (el.innerText || '').split('\\n').map(l => l.replace(/\\s+/g, ' ').trim()).filter(l => l);
    }
    function partes(lineas) {
        // 'Jesus' / '· Verde - Morado' / mensaje / fecha  (o 'Jesus · Verde - Morado' en una sola línea)
        const i = lineas.findIndex((l, n) => n < 4 && l.includes('·'));
        if (i < 0) return null;
        const antes = lineas.slice(0, i).join(' ');
        const partesLinea = lineas[i].split('·');
        const nombre = (antes + ' ' + partesLinea[0]).replace(/\\s+/g, ' ').trim();
        const producto = partesLinea.slice(1).join('·').replace(/\\s+/g, ' ').trim();
        if (!nombre || !producto) return null;
        return {nombre: nombre, producto: producto, titulo: nombre + ' · ' + producto};
    }
    function candidatos() {
        return Array.from(document.querySelectorAll("div[role='button'][tabindex='0']")).filter(el => {
            if (el.getAttribute('aria-label')) return false;
            if (el.closest("[role='log']")) return false;
            const texto = (el.innerText || '').trim();
            if (texto.length > 400) return false;
            const lineas = lineasDe(el);
            return lineas.length >= 2 && partes(lineas) !== null;
        });
    }
    function titulo(el) {
        const p = partes(lineasDe(el));
        return p ? p.titulo : '';
    }
    """

    JS_DIAGNOSTICO = """
    const botones = Array.from(document.querySelectorAll("div[role='button'][tabindex='0']"));
    const sinEtiqueta = botones.filter(b => !b.getAttribute('aria-label'));
    const conPunto = sinEtiqueta.filter(b => (b.innerText || '').includes('·'));
    return {
        url: location.href,
        titulo: document.title,
        botones: botones.length,
        sin_etiqueta: sinEtiqueta.length,
        con_punto: conPunto.length,
        ejemplos: conPunto.slice(0, 3).map(b => (b.innerText || '').slice(0, 120)),
        textos_pagina: (document.body.innerText || '').slice(0, 300)
    };
    """

    JS_LISTAR = JS_CANDIDATOS + """
    return candidatos().map(el => el.innerText);
    """

    JS_BAJAR = JS_CANDIDATOS + """
    const lista = candidatos();
    if (!lista.length) return 0;
    lista[lista.length - 1].scrollIntoView({block: 'end'});
    return lista.length;
    """

    JS_BUSCAR = JS_CANDIDATOS + """
    const buscado = arguments[0];
    const el = candidatos().find(e => titulo(e) === buscado);
    if (!el) return null;
    el.scrollIntoView({block: 'center'});
    return el;
    """

    JS_MENSAJES = """
    const log = Array.from(document.querySelectorAll("div[role='log']")).find(
        l => (l.getAttribute('aria-label') || '').replace(/\\s+/g, ' ').includes(arguments[0]));
    if (!log) return null;
    return Array.from(log.querySelectorAll("div[role='button'][aria-label*='Mensaje enviado a las']"))
        .map(e => e.getAttribute('aria-label'));
    """

    JS_CERRAR = """
    let el = Array.from(document.querySelectorAll("div[role='log']")).find(
        l => (l.getAttribute('aria-label') || '').replace(/\\s+/g, ' ').includes(arguments[0]));
    for (let i = 0; el && i < 20; i++, el = el.parentElement) {
        const b = el.querySelector("[aria-label='Cerrar chat'], [aria-label='Close chat']");
        if (b) return b;
    }
    return null;
    """

    JS_SUBIR_HISTORIAL = """
    const log = Array.from(document.querySelectorAll("div[role='log']")).find(
        l => (l.getAttribute('aria-label') || '').replace(/\\s+/g, ' ').includes(arguments[0]));
    if (!log) return false;
    let el = log;
    for (let i = 0; el && i < 15; i++, el = el.parentElement) {
        const sobra = el.scrollHeight > el.clientHeight + 5;
        const desplaza = ['auto', 'scroll'].includes(getComputedStyle(el).overflowY);
        if (sobra && desplaza) { el.scrollTop = 0; return true; }
    }
    return false;
    """

    JS_CAJA_TEXTO = """
    let el = Array.from(document.querySelectorAll("div[role='log']")).find(
        l => (l.getAttribute('aria-label') || '').replace(/\\s+/g, ' ').includes(arguments[0]));
    for (let i = 0; el && i < 20; i++, el = el.parentElement) {
        const c = el.querySelector("div[role='textbox']");
        if (c) return c;
    }
    return null;
    """

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

    def __init__(self, config=None):
        self.config = config or {}
        self.fb = PublicadorMarketplace(self.config)
        self.driver = None

    def iniciar_navegador(self):
        """Abre el navegador y comprueba la sesión de Facebook"""
        self.fb.iniciar_navegador()
        self.driver = self.fb.driver
        self.driver.set_script_timeout(15)
        return self.fb.esperar_login_facebook()

    def ir_al_inbox(self):
        """Abre la Bandeja de entrada de Marketplace y espera a que aparezcan las conversaciones"""
        print("📥 Abriendo la bandeja de entrada de Marketplace...")
        self.driver.get(URL_INBOX)
        for segundo in range(1, 61):
            time.sleep(1)
            if self.driver.execute_script(self.JS_LISTAR):
                time.sleep(1)
                print("✅ Bandeja de entrada cargada")
                return True
            if segundo in (10, 30):
                self._imprimir_diagnostico(f"a los {segundo} s")
        print("❌ No aparecieron conversaciones en la bandeja de entrada (¿está vacía o cambió la página?)")
        self._imprimir_diagnostico("al fallar")
        try:
            self.driver.save_screenshot("error_inbox.png")
            print("📸 Captura guardada en error_inbox.png (carpeta del programa)")
        except Exception:
            pass
        print("⏳ Dejo el navegador abierto 40 segundos por si quieres mirar la página...")
        time.sleep(40)
        return False

    def _imprimir_diagnostico(self, cuando):
        try:
            d = self.driver.execute_script(self.JS_DIAGNOSTICO)
        except Exception as e:
            print(f"   🔎 Diagnóstico {cuando}: no se pudo leer ({e})")
            return
        print(f"   🔎 Diagnóstico {cuando}:")
        print(f"      URL: {d['url']}")
        print(f"      Título de la pestaña: {d['titulo']}")
        print(f"      Botones role=button: {d['botones']} | sin aria-label: {d['sin_etiqueta']} | con '·': {d['con_punto']}")
        for ejemplo in d['ejemplos']:
            print(f"      ejemplo: {ejemplo!r}")
        print(f"      Texto de la página: {d['textos_pagina']!r}")

    def listar_chats(self, dias_maximos=None, max_bajadas=15):
        """
        Lee las conversaciones de la lista. La lista va de la más reciente a la más antigua y se carga al bajar,
        así que con dias_maximos se deja de bajar cuando aparece una conversación más antigua que ese límite.
        """
        chats, vistos = [], set()
        hoy = date.today()
        cantidad_anterior = -1

        for _ in range(max_bajadas + 1):
            for texto in self.driver.execute_script(self.JS_LISTAR) or []:
                chat = separar_chat(texto)
                if chat and chat['titulo'] not in vistos:
                    vistos.add(chat['titulo'])
                    chats.append(chat)

            if dias_maximos is not None and chats and chats[-1]['fecha'] is not None \
                    and (hoy - chats[-1]['fecha']).days > dias_maximos:
                break
            if len(chats) == cantidad_anterior:
                break
            cantidad_anterior = len(chats)

            self.driver.execute_script(self.JS_BAJAR)
            time.sleep(1.5)

        return chats

    def abrir_chat(self, chat):
        """Abre la conversación (chat emergente) y espera a que carguen sus mensajes"""
        for _ in range(3):
            elemento = self.driver.execute_script(self.JS_BUSCAR, chat['titulo'])
            if elemento is None:
                self.driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)
                continue
            try:
                elemento.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", elemento)
            for _ in range(15):
                time.sleep(1)
                if self.driver.execute_script(self.JS_MENSAJES, chat['titulo']):
                    self._cargar_historial(chat)
                    return True
        print(f"   ⚠️  No se pudo abrir el chat de {chat['nombre']}")
        return False

    def _cargar_historial(self, chat, max_subidas=12):
        """
        Facebook solo carga los mensajes más recientes al abrir el chat; los antiguos aparecen al subir el scroll.
        Sube hasta que la cantidad de mensajes deje de aumentar, para analizar la conversación completa.
        """
        anterior, repeticiones = -1, 0
        for _ in range(max_subidas):
            self.driver.execute_script(self.JS_SUBIR_HISTORIAL, chat['titulo'])
            time.sleep(1.2)
            cantidad = len(self.driver.execute_script(self.JS_MENSAJES, chat['titulo']) or [])
            if cantidad == anterior:
                repeticiones += 1
                if repeticiones >= 2:
                    break
            else:
                anterior, repeticiones = cantidad, 0

    def leer_mensajes(self, chat):
        """Mensajes del chat abierto, del más antiguo al más reciente"""
        etiquetas = self.driver.execute_script(self.JS_MENSAJES, chat['titulo']) or []
        mensajes = [m for m in (parsear_mensaje(e) for e in etiquetas) if m]
        return mensajes

    def cerrar_chat(self, chat):
        """Cierra el chat emergente"""
        try:
            boton = self.driver.execute_script(self.JS_CERRAR, chat['titulo'])
            if boton is None:
                print("   ⚠️  No se encontró el botón para cerrar el chat")
                return False
            try:
                boton.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", boton)
            time.sleep(1)
            return True
        except Exception:
            return False

    def enviar_mensaje(self, chat, texto):
        """Escribe el texto en el chat abierto y lo envía. Devuelve True si el mensaje aparece en la conversación."""
        caja = self.driver.execute_script(self.JS_CAJA_TEXTO, chat['titulo'])
        if caja is None:
            print("   ⚠️  No se encontró el cuadro de texto del chat")
            return False

        mios_antes = sum(1 for m in self.leer_mensajes(chat) if m['es_mio'])
        try:
            caja.click()
        except Exception:
            pass

        clave = _texto_comparable(texto)[:25]
        escrito = self.driver.execute_script(self.JS_PEGAR, caja, texto)
        if clave not in _texto_comparable(escrito):
            self.driver.execute_script(self.JS_INSERTAR, caja, texto)
            escrito = caja.text
            if clave not in _texto_comparable(escrito):
                print("   ⚠️  No se pudo escribir el mensaje en el cuadro de texto")
                return False

        time.sleep(0.5)
        caja.send_keys(Keys.ENTER)

        for _ in range(10):
            time.sleep(1)
            if sum(1 for m in self.leer_mensajes(chat) if m['es_mio']) > mios_antes:
                return True
        print("   ⚠️  El mensaje no apareció en la conversación después de enviarlo")
        return False

    def atender(self, chats, plantillas):
        """
        Atiende las conversaciones: abre cada una, reconstruye su estado y envía la respuesta que toque.
        Devuelve una lista con lo ocurrido en cada conversación (la usarán los avisos por WhatsApp).
        """
        max_insistencias = self.config.get('max_insistencias', 3)
        resultados = []

        for chat in chats:
            print(f"\n💬 {chat['titulo']}")
            if not self.abrir_chat(chat):
                continue
            analisis = analizar_conversacion(self.leer_mensajes(chat), plantillas, max_insistencias)
            enviado = False

            if analisis['accion']:
                texto = texto_a_enviar(analisis['accion'], chat, analisis, plantillas, self.config)
                print(f"   ➡️  {analisis['accion']}" + ("  (la conversación estaba cerrada y se reinicia)" if analisis['reiniciada'] else ""))
                if texto.strip():
                    enviado = self.enviar_mensaje(chat, texto)
                    print(f"   {'✅ Enviado' if enviado else '❌ No se pudo enviar'}")
                else:
                    print(f"   ⚠️  La plantilla {analisis['accion']} está vacía; configúrala en el Configurador")
            else:
                print(f"   ⏸️  Sin acción: {analisis['motivo']}")

            self.cerrar_chat(chat)
            resultados.append({'chat': chat, 'analisis': analisis, 'enviado': enviado})

        return resultados

    # ------------------------------------------------------------

    def ejecutar(self, modo_prueba=False):
        """
        Lista las conversaciones, muestra cuáles se atienden y cuáles se descartan y por qué, y atiende las relevantes
        (hasta el máximo por ejecución). Con modo_prueba no envía nada: abre los 3 primeros chats de la lista,
        imprime sus mensajes, el estado que reconstruye y el mensaje que enviaría, y los cierra.
        """
        dias = self.config.get('dias_maximos_conversacion', 5)
        resultado = {'relevantes': [], 'descartadas': []}

        try:
            if not self.iniciar_navegador():
                return None
            if not self.ir_al_inbox():
                return None

            print("📜 Leyendo conversaciones...")
            chats = self.listar_chats(None if modo_prueba else dias)
            print(f"   {len(chats)} conversación(es) leída(s)")

            titulos = titulos_de_productos()
            relevantes, descartadas = filtrar_chats(chats, titulos, dias)
            resultado = {'relevantes': relevantes, 'descartadas': descartadas}

            print(f"\n✅ A atender ({len(relevantes)}):")
            for chat in relevantes:
                print(f"   • {chat['nombre']} · {chat['producto']}  [{chat['fecha_texto'] or 'sin fecha'}]")
                print(f"       último mensaje: {chat['ultimo_mensaje'][:70]}")
            if not relevantes:
                print("   (ninguna)")

            print(f"\n⏭️  Descartadas ({len(descartadas)}):")
            for chat, motivo in descartadas[:25]:
                print(f"   • {chat['nombre']} · {chat['producto']} → {motivo}")
            if len(descartadas) > 25:
                print(f"   ... y {len(descartadas) - 25} más")

            from compartido.gestor_archivos import leer_plantillas_atencion
            plantillas = leer_plantillas_atencion()

            if modo_prueba:
                self._probar_lectura(chats[:3], plantillas)
            else:
                maximo = self.config.get('max_conversaciones_por_ejecucion', 20)
                if len(relevantes) > maximo:
                    print(f"\n⚠️  Hay {len(relevantes)} conversaciones; se atienden {maximo} en esta ejecución")
                resultado['atendidos'] = self.atender(relevantes[:maximo], plantillas)
                enviados = sum(1 for r in resultado['atendidos'] if r['enviado'])
                print(f"\n📊 Mensajes enviados: {enviados} de {len(resultado['atendidos'])} conversación(es)")

            return resultado

        finally:
            if self.driver:
                time.sleep(2)
                try:
                    self.driver.quit()
                except Exception:
                    pass
                self.driver = None

    def _probar_lectura(self, chats, plantillas):
        print(f"\n🧪 PRUEBA DE LECTURA (solo lee, no escribe nada)")
        max_insistencias = self.config.get('max_insistencias', 3)
        for chat in chats:
            print(f"\n💬 {chat['titulo']}")
            if not self.abrir_chat(chat):
                continue
            mensajes = self.leer_mensajes(chat)
            print(f"   {len(mensajes)} mensaje(s) cargado(s):")
            for m in mensajes:
                hora = m['fecha'].strftime('%Y-%m-%d %H:%M') if m['fecha'] else 'fecha ?'
                quien = 'YO' if m['es_mio'] else m['autor']
                marca = ' (sistema)' if m['es_sistema'] else ''
                texto = (m['texto'] or '(sin texto)').replace('\n', ' ⏎ ')
                print(f"     [{hora}] {quien}{marca}: {texto[:90]}")

            analisis = analizar_conversacion(mensajes, plantillas, max_insistencias)
            print(f"   🧠 Estado: {analisis['estado']} · pedidos de celular míos: {analisis['pedidos']} · "
                  f"celular del cliente: {analisis['celular'] or '—'}")
            if analisis['accion']:
                texto = texto_a_enviar(analisis['accion'], chat, analisis, plantillas, self.config)
                print(f"   ➡️  Enviaría ({analisis['accion']}):")
                for linea in texto.split('\n'):
                    print(f"        | {linea}")
            else:
                print(f"   ⏸️  No enviaría nada: {analisis['motivo']}")
            print(f"   Chat cerrado: {'sí' if self.cerrar_chat(chat) else 'NO'}")
