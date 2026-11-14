import sys
import time
import os
import ctypes
import configparser

# ── Colores ANSI ──────────────────────────────────────────────
V  = '\033[92m'   # verde
R  = '\033[91m'   # rojo
A  = '\033[93m'   # amarillo
C  = '\033[96m'   # cian
N  = '\033[1m'    # negrita
X  = '\033[0m'    # reset
# ─────────────────────────────────────────────────────────────

from datetime import datetime
from compartido.gestor_archivos import (
    leer_config_global,
    verificar_y_crear_estructura,
    leer_datos_articulo,
    obtener_imagenes_articulo,
    articulo_listo_para_publicar,
    obtener_articulos_a_publicar,
    avanzar_rotacion,
    numeros_articulos,
    obtener_config_tarea,
    registrar_evento_tarea,
    modulos_secuencia_general,
    MODULOS_DISPONIBLES,
)
from publicadores.publicador_marketplace import PublicadorMarketplace
from gestor_registro import GestorRegistro
from gestor_licencias import GestorLicencias

NOMBRE_APP = "Marketplace"


def verificar_licencia_inicio():
    gestor_lic = GestorLicencias(NOMBRE_APP)
    resultado = gestor_lic.verificar_e_iniciar()

    if not resultado.get('valida'):
        return None

    # Verificar expiración para TRIAL
    if resultado.get('tipo') == 'TRIAL':
        dias = resultado.get('diasRestantes', 0)
        if dias is not None and dias <= 0:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showwarning(
                "⏰ Período de Prueba Expirado",
                "Tu período de prueba ha terminado.\n\n"
                "Adquiere la versión Completa para seguir publicando.\n\n"
                "Visita: automapro-frontend.vercel.app"
            )
            root.destroy()
            return None
        print(f"\n⚠️  MODO PRUEBA - Quedan {dias} días\n")

    if resultado.get('tipo') == 'FULL' or resultado.get('developer_permanente'):
        print("\n✅ Licencia completa activada - Todas las funciones desbloqueadas\n")

    return resultado


def mostrar_banner():
    print(f"\n{N}{C}" + "="*70 + X)
    print(f"{N}{C}" + " " * 12 + "🛍️  PUBLICADOR AUTOMÁTICO DE MARKETPLACE" + X)
    print(f"{N}{C}" + " " * 22 + "Marketplace Automático" + X)
    print(f"{N}{C}" + "="*70 + X + "\n")


def mostrar_configuracion(config):
    verificar_y_crear_estructura()
    cantidad = config['cantidad_por_ejecucion']
    print(f"⚙️  {config['navegador'].capitalize()} · "
          f"{cantidad} producto{'s' if cantidad != 1 else ''} por ejecución · "
          f"máx. {config['max_publicaciones_por_dia']} por día\n")


def _iniciar_navegador(publicador):
    """Abre el navegador (el reintento por fallo inicial ya lo hace compartido/navegador.py)"""
    publicador.iniciar_navegador()


def publicar_con_reintentos(publicador, datos, imagenes, config):
    max_intentos = config.get('max_intentos_por_publicacion', 3)
    espera = config.get('tiempo_entre_intentos', 3)

    for intento in range(1, max_intentos + 1):
        try:
            if intento > 1:
                print(f"\n🔄 Reintento {intento} de {max_intentos}")
            if publicador.publicar_producto_completo(datos, imagenes):
                return True, intento
            print(f"⚠️  Intento {intento} falló")
        except Exception as e:
            print(f"❌ Error en intento {intento}: {e}")
            if intento == max_intentos:
                import traceback
                traceback.print_exc()
        if intento < max_intentos:
            print(f"⏳ Esperando {espera}s antes de reintentar...")
            time.sleep(espera)

    return False, max_intentos


def _publicar_productos(config):
    print(f"\n{N}{C}▶️  PUBLICAR PRODUCTOS EN MARKETPLACE{X}")
    gestor = GestorRegistro()

    puede, motivo = gestor.puede_publicar_hoy(config['max_publicaciones_por_dia'])
    print(f"📅 {motivo}")
    if not puede:
        print(f"{A}⚠️  Se alcanzó el límite diario: se publica mañana para cuidar tu cuenta de Facebook{X}")
        return

    tiempo_minimo = config['tiempo_minimo_entre_publicaciones_segundos']
    puede, motivo = gestor.puede_publicar_ahora(tiempo_minimo, config['permitir_forzar_publicacion_manual'])
    if not puede:
        print(f"\n⏱️  {motivo}")
        print(f"{A}⚠️  Aún no se cumple el tiempo mínimo entre publicaciones{X}")
        return

    # No pasar del límite diario aunque la ejecución pida más
    restantes = config['max_publicaciones_por_dia'] - gestor.publicaciones_de_hoy()
    cantidad = min(config['cantidad_por_ejecucion'], restantes)

    articulos = obtener_articulos_a_publicar(config, cantidad)
    if not articulos:
        return

    total = len(articulos)
    exitosos = 0
    publicador = PublicadorMarketplace(config)
    _iniciar_navegador(publicador)

    try:
        for i, numero in enumerate(articulos, 1):
            datos = leer_datos_articulo(numero, avisar=False)
            imagenes = obtener_imagenes_articulo(numero)
            nombre = f"Articulo_{numero}"
            titulo = datos.get('titulo', '')
            print(f"\n{N}{C}🛍️  PRODUCTO {i}/{total}: {nombre} · {titulo}{X}")

            inicio = time.time()
            exito, intentos = publicar_con_reintentos(publicador, datos, imagenes, config)
            if exito:
                exitosos += 1
                gestor.registrar_publicacion_exitosa(nombre, titulo, intentos, round(time.time() - inicio, 2))
                avanzar_rotacion(numero)
                print(f"{V}✅ Producto {i}/{total} publicado{X}")
            else:
                print(f"{R}❌ No se pudo publicar {nombre}{X}")
                gestor.registrar_error(nombre, "Falló después de todos los intentos", tipo='publicacion')

            if i < total:
                espera = config['tiempo_entre_publicaciones']
                print(f"\n⏳ Esperando {espera}s antes del siguiente producto...")
                time.sleep(espera)
    finally:
        publicador.cerrar_navegador()

    color = V if exitosos == total else (A if exitosos else R)
    print(f"\n{color}{N}📊 Productos publicados: {exitosos}/{total}{X}")


def _carpetas_destino_extraccion(cantidad):
    """
    Carpetas Articulo_N donde guardar lo extraído, sin pisar productos que ya tienes:
    primero las que están vacías o con el ejemplo, y si faltan, carpetas nuevas al final.
    """
    destinos = []
    for numero in numeros_articulos():
        datos = leer_datos_articulo(numero, avisar=False) or {}
        titulo = datos.get('titulo', '')
        if titulo in ('', 'Ejemplo Producto') and not obtener_imagenes_articulo(numero):
            destinos.append(numero)
            if len(destinos) == cantidad:
                return destinos

    siguiente = (max(numeros_articulos()) if numeros_articulos() else 0) + 1
    while len(destinos) < cantidad:
        destinos.append(siguiente)
        siguiente += 1
    return destinos


def _extraer_catalogo(config):
    print(f"\n{N}{C}🛍️  EXTRAER CATÁLOGO DE WHATSAPP{X}")
    from extractores.extractor_whatsapp import ExtractorWhatsApp

    if not config['contacto_whatsapp']:
        print(f"{A}⚠️  Falta el contacto de WhatsApp. Configúralo en el Configurador → pestaña Extractor{X}")
        return

    gestor = GestorRegistro()
    indice = gestor.obtener_indice_catalogo()
    cantidad = config['productos_por_extraccion']
    destinos = _carpetas_destino_extraccion(cantidad)

    print(f"\n📌 Catálogo de {config['contacto_whatsapp']}")
    print(f"   Último producto extraído: {indice} · próximo: {indice + 1}")
    print(f"   Se extraen hasta {cantidad} producto(s) en: {', '.join(f'Articulo_{n}' for n in destinos)}\n")

    extractor = ExtractorWhatsApp(config)
    productos = extractor.ejecutar(config['contacto_whatsapp'], destinos, indice)

    if not productos:
        print(f"{A}⚠️  No se extrajo ningún producto{X}")
        if productos is False:
            gestor.registrar_error('Extractor', 'No se pudo completar la extracción del catálogo', tipo='extraccion')
        return

    nuevo_indice = indice + len(productos)
    gestor.registrar_extraccion_catalogo(len(productos), nuevo_indice, config['contacto_whatsapp'])
    print(f"\n{V}{N}✅ Se extrajeron {len(productos)} producto(s). Revísalos en el Gestor de Productos antes de publicar.{X}")


def _atender_interesados(config, prueba=False):
    """
    Lee la bandeja de entrada de Marketplace y responde a los interesados (pide el celular, insiste, confirma y se despide).
    Con prueba=True (py publicar_marketplace.py --modulo atender --prueba) no envía nada: abre 3 chats y muestra
    el estado que reconstruye y el mensaje que enviaría.
    """
    print(f"\n{N}{C}💬 ATENDER INTERESADOS{X}")
    from atendedores.atendedor_interesados import AtendedorInteresados

    print(f"   Se atienden conversaciones con actividad de los últimos {config['dias_maximos_conversacion']} días "
          f"(máx. {config['max_conversaciones_por_ejecucion']} por ejecución)")
    AtendedorInteresados(config).ejecutar(modo_prueba=prueba)
    if prueba:
        print(f"\n{A}🧪 Prueba terminada: no se envió ningún mensaje.{X}")


def _ejecutar_modulos(config, lista, id_de_tarea=None):
    """Ejecuta las acciones en orden. Con id_de_tarea valida cada una antes y nunca se queda esperando respuesta"""
    nombres = dict(MODULOS_DISPONIBLES)

    for modulo in lista:
        if id_de_tarea and not _validar_modulo_tarea(config, modulo, id_de_tarea):
            continue

        if modulo == 'publicar':
            _publicar_productos(config)
        elif modulo == 'extraer':
            _extraer_catalogo(config)
        elif modulo == 'atender':
            _atender_interesados(config)
        else:
            print(f"{A}⚠️  Acción desconocida: {modulo}{X}")
            continue

        if id_de_tarea:
            registrar_evento_tarea(id_de_tarea, f"✅ Ejecutada \"{nombres.get(modulo, modulo).split('  ')[-1]}\"")


def _problema_modulo(config, modulo):
    """Qué le falta a una acción: (problema, pestaña del Configurador) o (None, None) si está todo"""
    if modulo == 'extraer' and not config['contacto_whatsapp']:
        return "Falta el contacto de WhatsApp del catálogo", 'extractor'
    if modulo == 'atender' and not config['contacto_vendedor_whatsapp']:
        return "Falta el contacto de WhatsApp del vendedor", 'atencion'
    if modulo == 'publicar' and not numeros_articulos():
        return "No hay productos para publicar", None
    return None, None


def _abrir_configurador_sin_esperar(pestana):
    import subprocess
    base_dir = _base_dir_app()
    exe_cfg = os.path.join(base_dir, "ConfiguradorMarketplace.exe")
    try:
        if os.path.exists(exe_cfg):
            subprocess.Popen([exe_cfg, f"--pestana={pestana}"])
        else:
            subprocess.Popen([sys.executable, os.path.join(base_dir, "configurador_gui.py"), f"--pestana={pestana}"])
    except Exception as e:
        print(f"⚠️  No se pudo abrir el Configurador: {e}")


def _validar_modulo_tarea(config, modulo, id_de_tarea):
    """Revisa lo que necesita una acción de una tarea; si falta algo avisa con cuenta regresiva y la omite"""
    from compartido.aviso_temporizado import AvisoTemporizado

    problema, pestana = _problema_modulo(config, modulo)
    if not problema:
        return True

    nombre_modulo = dict(MODULOS_DISPONIBLES).get(modulo, modulo).split('  ')[-1]
    print(f"\n{A}⚠️  {problema} → se omite \"{nombre_modulo}\"{X}")
    eleccion, respondio = AvisoTemporizado.preguntar(
        problema,
        f"La acción \"{nombre_modulo}\" de la tarea \"{id_de_tarea}\" no se puede ejecutar.\n"
        "Las demás acciones de la tarea continúan.",
        [('configurar', "Abrir Configurador"), ('omitir', "Omitir esta acción")],
        'omitir'
    )
    if eleccion == 'configurar' and pestana:
        _abrir_configurador_sin_esperar(pestana)

    detalle = "respondido" if respondio else f"sin respuesta, {AvisoTemporizado.SEGUNDOS_DEFECTO} s"
    registrar_evento_tarea(id_de_tarea, f"⏭️ Omitida \"{nombre_modulo}\": {problema} ({detalle})")
    return False


def _ejecutar_secuencia_full(config):
    _ejecutar_modulos(config, modulos_secuencia_general())


def _ejecutar_tarea(config, id_de_tarea):
    """Ejecuta las acciones propias de una tarea automática"""
    config_tarea = obtener_config_tarea(id_de_tarea)

    if not config_tarea:
        print(f"{A}⚠️  La tarea '{id_de_tarea}' no tiene configuración propia. Se usa la secuencia general.{X}")
        registrar_evento_tarea(id_de_tarea, "⚠️ Sin configuración propia: se usó la secuencia general")
        _ejecutar_secuencia_full(config)
        return

    modulos = config_tarea.get('modulos', [])
    cantidad = config_tarea.get('cantidad')
    nombres = dict(MODULOS_DISPONIBLES)
    # Copia para no alterar la configuración general que usan los demás módulos
    config = dict(config)
    if cantidad:
        config['cantidad_por_ejecucion'] = cantidad

    print(f"\n{N}{C}🗓️  TAREA AUTOMÁTICA: {config_tarea.get('nombre', id_de_tarea)}{X}")
    for i, modulo in enumerate(modulos, 1):
        print(f"   {i}. {nombres.get(modulo, modulo)}")
    if 'publicar' in modulos:
        print(f"   🛍️  Productos a publicar: {f'{cantidad} propios de la tarea' if cantidad else 'los de la configuración general'}")

    if not modulos:
        print(f"{A}⚠️  La tarea no tiene acciones activas{X}")
        registrar_evento_tarea(id_de_tarea, "⚠️ Sin acciones activas")
        return

    registrar_evento_tarea(id_de_tarea, "▶️ Inicio")
    _ejecutar_modulos(config, modulos, id_de_tarea)
    registrar_evento_tarea(id_de_tarea, "🏁 Fin")


def _base_dir_app():
    return os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))


def _ocultar_consola():
    try:
        _hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if _hwnd:
            ctypes.windll.user32.ShowWindow(_hwnd, 0)
    except Exception:
        pass


def _abrir_consola():
    try:
        _hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if _hwnd:
            ctypes.windll.user32.ShowWindow(_hwnd, 5)
    except Exception:
        pass
    try:
        ctypes.windll.kernel32.SetConsoleMode(ctypes.windll.kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass
    try:
        _hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if _hwnd:
            _base = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
            _ico = os.path.join(_base, 'iconos', 'tienda.ico')
            if os.path.exists(_ico):
                _hicon = ctypes.windll.user32.LoadImageW(0, _ico, 1, 0, 0, 0x10)
                if _hicon:
                    ctypes.windll.user32.SendMessageW(_hwnd, 0x0080, 1, _hicon)
                    ctypes.windll.user32.SendMessageW(_hwnd, 0x0080, 0, _hicon)
    except Exception:
        pass


def _avisar_actualizacion(id_de_tarea):
    """Al terminar una tarea avisa si hay versión nueva: como máximo una vez al día y sin bloquear la tarea"""
    import json
    base_dir = _base_dir_app()
    ruta_aviso = os.path.join(base_dir, 'aviso_actualizacion.json')
    hoy = datetime.now().strftime('%Y-%m-%d')
    try:
        with open(ruta_aviso, 'r', encoding='utf-8') as f:
            if json.load(f).get('fecha') == hoy:
                return
    except Exception:
        pass

    try:
        with open(os.path.join(base_dir, 'version.txt'), 'r', encoding='utf-8') as f:
            version_local = f.read().strip()
    except Exception:
        return

    resultado = GestorLicencias(NOMBRE_APP).verificar_actualizacion(version_local)
    if not resultado.get('hay_actualizacion') or not resultado.get('ruta_archivo'):
        return

    version_nueva = resultado['version_nueva']
    try:
        with open(ruta_aviso, 'w', encoding='utf-8') as f:
            json.dump({'fecha': hoy, 'version': version_nueva}, f)
    except Exception:
        pass

    from compartido.aviso_temporizado import AvisoTemporizado
    clave, _ = AvisoTemporizado.preguntar(
        f"🔄 Hay una nueva versión de Marketplace Automático ({version_nueva})",
        f"Tienes la {version_local}. Al actualizar se conservan tus productos, tu configuración y tus tareas.",
        [('actualizar', '⬇️ Actualizar ahora'), ('despues', 'Más tarde')],
        'despues',
        color=AvisoTemporizado.COLOR_INFO
    )

    if clave != 'actualizar':
        print(f"\nℹ️  Hay una nueva versión ({version_nueva}). Puedes actualizar desde el Panel de Control.")
        if id_de_tarea:
            registrar_evento_tarea(id_de_tarea, f"🔄 Versión {version_nueva} disponible: se dejó para más tarde")
        return

    if id_de_tarea:
        registrar_evento_tarea(id_de_tarea, f"⬇️ Actualizando a la versión {version_nueva}")
    print(f"\n⬇️  Descargando la versión {version_nueva}...")
    try:
        import tempfile
        import urllib.request
        import subprocess
        ruta_instalador = os.path.join(tempfile.gettempdir(), f"InstaladorMarketplace_{version_nueva}.exe")
        urllib.request.urlretrieve(resultado['ruta_archivo'], ruta_instalador)
        print("🚀 Instalando la nueva versión...")
        subprocess.Popen([ruta_instalador, '/SILENT'])
    except Exception as e:
        print(f"❌ No se pudo descargar la actualización: {e}")
        if id_de_tarea:
            registrar_evento_tarea(id_de_tarea, f"❌ No se pudo descargar la versión {version_nueva}")


def _esperar_cierre(sin_pausa):
    """En ejecuciones manuales deja la consola abierta para leer el resultado; en tareas se cierra sola"""
    if sin_pausa:
        time.sleep(2)
        return
    try:
        input("\nPresiona Enter para cerrar...")
    except (EOFError, KeyboardInterrupt):
        pass


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--secuencia', action='store_true')
    parser.add_argument('--modulo', default=None)
    parser.add_argument('--tarea', default=None)
    parser.add_argument('--prueba', action='store_true')
    args, _ = parser.parse_known_args()

    es_doble_clic = not args.secuencia and args.modulo is None and args.tarea is None

    estado_licencia = verificar_licencia_inicio()
    if not estado_licencia:
        _abrir_consola()
        print("\n⏰ Acceso bloqueado — período de prueba expirado o licencia inválida.")
        if args.tarea:
            registrar_evento_tarea(args.tarea, "⛔ No se ejecutó: licencia inválida o expirada")
        else:
            input("\nPresiona Enter para cerrar...")
        return

    try:
        config = leer_config_global()
    except Exception as e:
        _abrir_consola()
        print(f"❌ Error leyendo configuración: {e}")
        return

    es_full = estado_licencia.get('tipo') in ['FULL', 'MASTER'] or estado_licencia.get('developer_permanente')

    if not es_full:
        config['cantidad_por_ejecucion'] = 1

    _abrir_consola()
    mostrar_banner()
    mostrar_configuracion(config)

    try:
        if args.tarea and es_full:
            _ejecutar_tarea(config, args.tarea)
            _avisar_actualizacion(args.tarea)
        elif args.tarea:
            _publicar_productos(config)
            _avisar_actualizacion(args.tarea)
        elif args.modulo == 'publicar':
            _publicar_productos(config)
        elif args.modulo == 'extraer':
            _extraer_catalogo(config)
        elif args.modulo == 'atender':
            _atender_interesados(config, prueba=args.prueba)
        elif args.modulo:
            print(f"{A}⚠️  Acción desconocida: {args.modulo}. Usa publicar, extraer o atender.{X}")
        elif args.secuencia or es_doble_clic:
            _ejecutar_secuencia_full(config)
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso cancelado por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print(f"\n{N}👋 Finalizando programa...{X}")
        _esperar_cierre(sin_pausa=bool(args.tarea))


def _verificar_wizard_completado():
    try:
        import subprocess
        import json
        config_path = os.path.join(
            os.path.expanduser("~"), ".config", "AutomaPro", NOMBRE_APP, "config.json"
        )
        tiene_configuracion = False
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    if json.load(f).get('codigo_licencia'):
                        tiene_configuracion = True
            except Exception:
                pass

        if not tiene_configuracion:
            if getattr(sys, 'frozen', False):
                wizard = os.path.join(os.path.dirname(sys.executable), "WizardMarketplace.exe")
                comando = [wizard]
            else:
                wizard = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wizard_primera_vez.py")
                comando = [sys.executable, wizard]
            if os.path.exists(wizard):
                subprocess.Popen(comando)
            return False
        return True
    except Exception:
        return True


if __name__ == "__main__":
    # Registrar AppUserModelID para icono correcto en barra de tareas
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('AutomaPro.Marketplace')
    except Exception:
        pass

    _ocultar_consola()

    if not _verificar_wizard_completado():
        sys.exit(0)

    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Proceso cancelado por el usuario\n")
        sys.exit(0)
    except Exception as e:
        import traceback
        print(f"\n❌ Error inesperado: {e}")
        traceback.print_exc()
