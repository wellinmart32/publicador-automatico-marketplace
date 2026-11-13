"""
Apertura del navegador (Firefox, Chrome o Edge) compartida por el publicador y el extractor.

Perfil del navegador (donde quedan las sesiones de Facebook y WhatsApp):
- Compartido (por defecto): %LOCALAPPDATA%\\AutomaPro\\perfiles\\<navegador>, el mismo para todas las apps
  AutomaPro, así se inicia sesión y se escanea el QR de WhatsApp una sola vez.
- Propio: carpeta perfiles\\<navegador> dentro de esta app.
Un perfil solo puede estar abierto por un programa a la vez: si otra app lo está usando, se espera a que termine.
"""

import os
import sys
import time
import subprocess
import tempfile

from selenium import webdriver
from selenium.webdriver.firefox.options import Options as OpcionesFirefox
from selenium.webdriver.chrome.options import Options as OpcionesChrome


def _base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Espera máxima cuando otra app AutomaPro tiene abierto el perfil compartido
MINUTOS_ESPERA_PERFIL = 10
SEGUNDOS_ENTRE_REVISIONES = 30


def carpeta_perfil(config):
    """Carpeta del perfil dedicado según la configuración (compartido entre apps AutomaPro o propio de esta app)"""
    navegador = config.get('navegador', 'firefox')
    if config.get('perfil_compartido', True):
        raiz = os.environ.get('LOCALAPPDATA') or os.path.join(os.path.expanduser('~'), 'AppData', 'Local')
        ruta = os.path.join(raiz, 'AutomaPro', 'perfiles', navegador)
    else:
        ruta = os.path.join(_base_dir(), 'perfiles', navegador)
    os.makedirs(ruta, exist_ok=True)
    return ruta


def _perfil_ocupado(ruta):
    """
    Indica si otro programa tiene abierto el perfil.
    Chrome/Edge dejan 'lockfile' y Firefox 'parent.lock' abiertos en exclusiva mientras usan el perfil:
    si el archivo existe pero no se puede abrir, el perfil está en uso.
    """
    for nombre in ('lockfile', 'parent.lock'):
        archivo = os.path.join(ruta, nombre)
        if os.path.exists(archivo):
            try:
                with open(archivo, 'a'):
                    pass
            except (PermissionError, OSError):
                return True
    return False


def _esperar_perfil_libre(ruta):
    """Si otra app está usando el perfil espera a que lo libere. Devuelve False si se agota la espera"""
    if not _perfil_ocupado(ruta):
        return True
    print(f"⏳ Otra aplicación AutomaPro está usando el navegador. Esperando a que termine "
          f"(máximo {MINUTOS_ESPERA_PERFIL} min)...")
    limite = time.time() + MINUTOS_ESPERA_PERFIL * 60
    while time.time() < limite:
        time.sleep(SEGUNDOS_ENTRE_REVISIONES)
        if not _perfil_ocupado(ruta):
            print("   ✅ El navegador quedó libre")
            return True
        restantes = int((limite - time.time()) / 60) + 1
        print(f"   ⏳ Sigue ocupado... (hasta {restantes} min más)")
    return False


def _proceso_abierto(proceso):
    """Indica si el navegador ya está corriendo (consulta tasklist de Windows)"""
    try:
        resultado = subprocess.run(['tasklist', '/FI', f'IMAGENAME eq {proceso}', '/NH'],
                                   capture_output=True, text=True)
        return proceso in resultado.stdout.lower()
    except Exception:
        return False


def _abrir_firefox(config, perfil_dedicado):
    firefox_ya_abierto = _proceso_abierto('firefox.exe')

    if config.get('usar_perfil_existente', True) and not firefox_ya_abierto:
        from compartido.gestor_archivos import obtener_ruta_perfil_navegador
        ruta_perfil = obtener_ruta_perfil_navegador()
        if ruta_perfil:
            opciones = OpcionesFirefox()
            if config.get('desactivar_notificaciones', True):
                opciones.set_preference("dom.webnotifications.enabled", False)
            opciones.add_argument("-profile")
            opciones.add_argument(ruta_perfil)
            try:
                return webdriver.Firefox(options=opciones)
            except Exception as e:
                print(f"   ⚠️  Perfil principal bloqueado ({e}), usando perfil dedicado...")
    elif firefox_ya_abierto:
        print("   ℹ️  Firefox ya está abierto, usando perfil dedicado...")

    opciones = OpcionesFirefox()
    if config.get('desactivar_notificaciones', True):
        opciones.set_preference("dom.webnotifications.enabled", False)
    opciones.add_argument("-profile")
    opciones.add_argument(perfil_dedicado)
    print(f"   ✓ Usando perfil dedicado: {perfil_dedicado}")
    return webdriver.Firefox(options=opciones)


def _abrir_chromium(config, navegador, perfil_dedicado):
    """Chrome y Edge comparten motor (Chromium): misma lógica, distinta clase de Selenium"""
    if navegador == 'edge':
        # Microsoft cerró el servidor antiguo de msedgedriver
        os.environ.setdefault("SE_DRIVER_MIRROR_URL", "https://msedgedriver.microsoft.com")
        from selenium.webdriver.edge.options import Options as OpcionesNavegador
        clase_driver = webdriver.Edge
        proceso, nombre = 'msedge.exe', 'Edge'
    else:
        OpcionesNavegador = OpcionesChrome
        clase_driver = webdriver.Chrome
        proceso, nombre = 'chrome.exe', 'Chrome'

    def _opciones_base():
        op = OpcionesNavegador()
        if config.get('desactivar_notificaciones', True):
            op.add_argument("--disable-notifications")
        op.add_argument("--disable-blink-features=AutomationControlled")
        op.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        op.add_argument("--log-level=3")
        op.add_experimental_option('useAutomationExtension', False)
        op.add_argument("--no-first-run")
        op.add_argument("--no-default-browser-check")
        op.add_argument("--disable-session-crashed-bubble")
        op.add_argument("--hide-crash-restore-bubble")
        op.add_argument("--disable-features=InfiniteSessionRestore")
        op.add_experimental_option("prefs", {
            "profile.exit_type": "Normal",
            "profile.exited_cleanly": True
        })
        return op

    if _proceso_abierto(proceso):
        print(f"   ℹ️  {nombre} ya está abierto, iniciando instancia separada con perfil dedicado...")

    if config.get('usar_perfil_existente', True):
        opciones = _opciones_base()
        opciones.add_argument(f"--user-data-dir={perfil_dedicado}")
        try:
            return clase_driver(options=opciones)
        except Exception as e:
            print(f"   ⚠️  No se pudo abrir con el perfil dedicado ({e}), usando perfil temporal...")

    perfil_tmp = tempfile.mkdtemp(prefix=f"{navegador}_automapro_tmp_")
    opciones = _opciones_base()
    opciones.add_argument(f"--user-data-dir={perfil_tmp}")
    return clase_driver(options=opciones)


def abrir_navegador(config):
    """
    Abre el navegador elegido en la configuración y devuelve el driver de Selenium.
    Facebook y WhatsApp usan el mismo perfil, así sus sesiones quedan guardadas juntas.
    Reintenta una vez: a veces falla la primera vez (driver descargándose, perfil ocupado un instante).
    """
    navegador = config.get('navegador', 'firefox')
    if navegador not in ('firefox', 'chrome', 'edge'):
        raise Exception(f"Navegador no soportado: {navegador}")

    nombres = {'firefox': 'Firefox', 'chrome': 'Chrome', 'edge': 'Edge'}
    perfil = carpeta_perfil(config)
    tipo = "compartido con las apps AutomaPro" if config.get('perfil_compartido', True) else "propio de esta app"
    print(f"🌐 Iniciando {nombres[navegador]} (perfil {tipo})...")

    if config.get('usar_perfil_existente', True) and not _esperar_perfil_libre(perfil):
        raise Exception(f"El navegador sigue ocupado por otra aplicación AutomaPro después de "
                        f"{MINUTOS_ESPERA_PERFIL} minutos. Intenta de nuevo cuando termine.")

    def _intentar():
        if navegador == 'firefox':
            return _abrir_firefox(config, perfil)
        return _abrir_chromium(config, navegador, perfil)

    try:
        driver = _intentar()
    except Exception as e:
        print(f"⚠️  No se pudo abrir el navegador ({type(e).__name__}). Reintentando en 10 s...")
        time.sleep(10)
        driver = _intentar()

    if config.get('maximizar_ventana', True):
        try:
            driver.maximize_window()
        except Exception:
            pass
    print("   ✅ Navegador iniciado")
    return driver
