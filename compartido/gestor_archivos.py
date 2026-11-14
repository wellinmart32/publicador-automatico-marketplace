import os
import configparser
import shutil
import time
from datetime import datetime


# ============================================================
# CONFIGURACIÓN GLOBAL
# ============================================================

def leer_config_global():
    """
    Lee config_global.txt y retorna un diccionario con la configuración
    Cada clave tiene un valor por defecto para que funcione con configuraciones antiguas
    """
    archivo_config = os.path.join(_base_dir(), "config_global.txt")

    if not os.path.exists(archivo_config):
        print("⚠️  No existe config_global.txt. Creando configuración por defecto...")
        crear_config_defecto()

    config = configparser.RawConfigParser(delimiters=('=',))
    config.read(archivo_config, encoding='utf-8')

    def texto(seccion, clave, defecto):
        return config.get(seccion, clave, fallback=defecto).split('#')[0].strip()

    def si_no(seccion, clave, defecto):
        return texto(seccion, clave, defecto).lower() == 'si'

    def numero(seccion, clave, defecto, minimo=None, maximo=None):
        try:
            valor = int(texto(seccion, clave, str(defecto)))
        except ValueError:
            valor = defecto
        if minimo is not None:
            valor = max(minimo, valor)
        if maximo is not None:
            valor = min(maximo, valor)
        return valor

    config_dict = {
        # [GENERAL]
        'nombre_proyecto': texto('GENERAL', 'nombre_proyecto', 'Marketplace Automático'),
        'carpeta_productos': texto('GENERAL', 'carpeta_productos', 'ArticulosMarketplace') or 'ArticulosMarketplace',
        'cantidad_productos': numero('GENERAL', 'cantidad_productos', 5, minimo=1, maximo=100),
        'navegador': texto('GENERAL', 'navegador', 'firefox').lower(),

        # [PRODUCTOS]
        'cantidad_por_ejecucion': numero('PRODUCTOS', 'cantidad_por_ejecucion', 1, minimo=1, maximo=10),

        # [PUBLICACION]
        'ubicacion': texto('PUBLICACION', 'ubicacion', 'Guayaquil'),
        'tiempo_entre_intentos': numero('PUBLICACION', 'tiempo_entre_intentos', 3, minimo=1),
        'max_intentos_por_publicacion': numero('PUBLICACION', 'max_intentos_por_publicacion', 3, minimo=1),
        'espera_despues_publicar': numero('PUBLICACION', 'espera_despues_publicar', 5, minimo=0),
        'tiempo_entre_publicaciones': numero('PUBLICACION', 'tiempo_entre_publicaciones', 10, minimo=0),
        'max_publicaciones_por_dia': numero('PUBLICACION', 'max_publicaciones_por_dia', 20, minimo=1),

        # [LIMITES]
        'tiempo_minimo_entre_publicaciones_segundos': numero('LIMITES', 'tiempo_minimo_entre_publicaciones_segundos', 120, minimo=0),
        'permitir_forzar_publicacion_manual': si_no('LIMITES', 'permitir_forzar_publicacion_manual', 'si'),

        # [EXTRACCION]
        'contacto_whatsapp': texto('EXTRACCION', 'contacto_whatsapp', ''),
        'auto_scroll': numero('EXTRACCION', 'auto_scroll', 5, minimo=0),
        'productos_por_extraccion': numero('EXTRACCION', 'productos_por_extraccion', 5, minimo=1),

        # [ATENCION]
        'contacto_vendedor_whatsapp': texto('ATENCION', 'contacto_vendedor_whatsapp', ''),
        'nombre_vendedor': texto('ATENCION', 'nombre_vendedor', ''),
        'contacto_abandonos_whatsapp': texto('ATENCION', 'contacto_abandonos_whatsapp', ''),
        'max_insistencias': numero('ATENCION', 'max_insistencias', 3, minimo=0, maximo=5),
        'max_conversaciones_por_ejecucion': numero('ATENCION', 'max_conversaciones_por_ejecucion', 20, minimo=1, maximo=50),
        'dias_maximos_conversacion': numero('ATENCION', 'dias_maximos_conversacion', 5, minimo=1, maximo=60),

        # [NAVEGADOR]
        'usar_perfil_existente': si_no('NAVEGADOR', 'usar_perfil_existente', 'si'),
        'perfil_compartido': si_no('NAVEGADOR', 'perfil_compartido', 'si'),
        'carpeta_perfil_custom': texto('NAVEGADOR', 'carpeta_perfil_custom', 'perfiles/facebook_marketplace'),
        'desactivar_notificaciones': si_no('NAVEGADOR', 'desactivar_notificaciones', 'si'),
        'maximizar_ventana': si_no('NAVEGADOR', 'maximizar_ventana', 'si'),

        # [SEGURIDAD]
        'confirmacion_borrado': si_no('SEGURIDAD', 'confirmacion_borrado', 'si'),
        'backup_antes_borrar': si_no('SEGURIDAD', 'backup_antes_borrar', 'si'),

        # [DEBUG]
        'modo_debug': texto('DEBUG', 'modo_debug', 'detallado').lower(),
    }

    return config_dict


def crear_config_defecto():
    """Crea config_global.txt a partir de la plantilla config_global.ejemplo.txt"""
    base = _base_dir()
    plantilla = os.path.join(base, "config_global.ejemplo.txt")
    if os.path.exists(plantilla):
        shutil.copyfile(plantilla, os.path.join(base, "config_global.txt"))
        print("   ✅ config_global.txt creado desde la plantilla")
    else:
        print("   ❌ Falta config_global.ejemplo.txt: copia manualmente config_global.txt al proyecto")


def verificar_y_crear_estructura():
    """Crea la carpeta de productos, su archivo de rotación y la carpeta de perfil si hacen falta"""
    config = leer_config_global()
    carpeta_productos = _carpeta_productos()

    carpetas_necesarias = [carpeta_productos]
    if not config['usar_perfil_existente']:
        carpetas_necesarias.append(os.path.join(_base_dir(), config['carpeta_perfil_custom']))

    carpetas_creadas = []
    for carpeta in carpetas_necesarias:
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)
            carpetas_creadas.append(carpeta)

    archivo_rotacion = os.path.join(carpeta_productos, "config.txt")
    if not os.path.exists(archivo_rotacion):
        with open(archivo_rotacion, 'w', encoding='utf-8') as f:
            f.write("1")

    if carpetas_creadas:
        print(f"✅ Carpetas creadas: {', '.join(carpetas_creadas)}")

    return True


def _base_dir():
    import sys
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _carpeta_productos():
    """Ruta absoluta de la carpeta donde están las carpetas Articulo_N"""
    nombre = leer_config_global()['carpeta_productos']
    return os.path.join(_base_dir(), nombre)


def _carpeta_articulo(numero):
    return os.path.join(_carpeta_productos(), f"Articulo_{numero}")


# ============================================================
# PRODUCTOS (carpetas Articulo_N)
# ============================================================

CLAVES_DATOS_ARTICULO = ['titulo', 'precio', 'marca', 'categoria', 'estado', 'ubicacion', 'descripcion',
                         'disponibilidad', 'encuentro_publico', 'etiquetas', 'sku']

EXTENSIONES_IMAGEN = ('.jpg', '.jpeg', '.png', '.gif', '.webp')

ESTADOS_ARTICULO = ['Nuevo', 'Usado - Como nuevo', 'Usado - En buen estado', 'Usado - Aceptable']

CATEGORIAS_ARTICULO = ['Electrónica e informática', 'Vehículos', 'Ropa y accesorios', 'Hogar y jardín',
                       'Artículos para bebés y niños']


def leer_datos_articulo(numero_articulo, avisar=True):
    """Lee datos.txt del artículo. La descripción puede tener varias líneas."""
    archivo_datos = os.path.join(_carpeta_articulo(numero_articulo), "datos.txt")

    if not os.path.exists(archivo_datos):
        if avisar:
            print(f"❌ No se encontró el archivo datos.txt en Articulo_{numero_articulo}")
        return None

    with open(archivo_datos, 'r', encoding='utf-8') as f:
        lineas = f.read().split('\n')

    datos = {}
    i = 0
    while i < len(lineas):
        linea = lineas[i].strip()

        if '=' in linea:
            clave, valor = linea.split('=', 1)
            clave = clave.strip()
            valor = valor.strip()

            if clave == 'descripcion' and valor.startswith('"'):
                # Formato entre comillas (gestor anterior): puede ocupar varias líneas
                texto = '\n'.join([linea.split('=', 1)[1].strip()] + [l.rstrip() for l in lineas[i + 1:]])
                fin = _fin_comillas(texto)
                datos[clave] = texto[1:fin].replace('\\"', '"').strip()
                i += texto[:fin].count('\n')
            elif clave == 'descripcion':
                # Leer todas las líneas hasta la siguiente clave conocida
                descripcion_completa = [valor] if valor else []
                i += 1
                while i < len(lineas):
                    siguiente_linea = lineas[i]
                    if '=' in siguiente_linea:
                        posible_clave = siguiente_linea.split('=')[0].strip()
                        if posible_clave in CLAVES_DATOS_ARTICULO:
                            i -= 1
                            break
                    descripcion_completa.append(siguiente_linea.rstrip())
                    i += 1
                datos[clave] = '\n'.join(descripcion_completa).strip()
            else:
                datos[clave] = valor

        i += 1

    return datos


def _fin_comillas(texto):
    """Posición de la comilla que cierra el texto que empieza con comilla (ignora las escapadas con \\)"""
    j = 1
    while j < len(texto):
        if texto[j] == '\\':
            j += 2
            continue
        if texto[j] == '"':
            return j
        j += 1
    return len(texto)


def guardar_datos_articulo(numero_articulo, datos):
    """
    Guarda datos.txt del artículo. La descripción va al final, entre comillas y puede tener varias líneas
    (las comillas internas se guardan como \\"). Formato que entiende leer_datos_articulo().
    """
    carpeta = _carpeta_articulo(numero_articulo)
    os.makedirs(os.path.join(carpeta, "imagenes"), exist_ok=True)
    with open(os.path.join(carpeta, "datos.txt"), 'w', encoding='utf-8') as f:
        for clave in CLAVES_DATOS_ARTICULO:
            if clave != 'descripcion':
                f.write(f"{clave}={datos.get(clave, '')}\n")
        descripcion = datos.get('descripcion', '').strip().replace('"', '\\"')
        f.write(f'descripcion="{descripcion}"\n')


def obtener_imagenes_articulo(numero_articulo):
    """Rutas absolutas de las imágenes del artículo (máximo 10, en orden alfabético)"""
    carpeta_imagenes = os.path.join(_carpeta_articulo(numero_articulo), "imagenes")

    if not os.path.exists(carpeta_imagenes):
        return []

    imagenes = [
        os.path.abspath(os.path.join(carpeta_imagenes, archivo))
        for archivo in sorted(os.listdir(carpeta_imagenes))
        if archivo.lower().endswith(EXTENSIONES_IMAGEN)
    ]
    return imagenes[:10]


def articulo_listo_para_publicar(numero_articulo):
    """Un artículo está listo si tiene título, precio y al menos una imagen"""
    datos = leer_datos_articulo(numero_articulo, avisar=False)
    if not datos or not datos.get('titulo') or not datos.get('precio'):
        return False
    if datos.get('titulo') == 'Ejemplo Producto':
        return False
    return len(obtener_imagenes_articulo(numero_articulo)) > 0


def numeros_articulos():
    """Números de las carpetas Articulo_N que existen, ordenados (puede haber huecos)"""
    carpeta_principal = _carpeta_productos()
    if not os.path.exists(carpeta_principal):
        return []
    numeros = []
    for item in os.listdir(carpeta_principal):
        if item.startswith("Articulo_") and os.path.isdir(os.path.join(carpeta_principal, item)):
            sufijo = item[len("Articulo_"):]
            if sufijo.isdigit():
                numeros.append(int(sufijo))
    return sorted(numeros)


def contar_articulos():
    """Cuántas carpetas Articulo_N existen"""
    return len(numeros_articulos())


def listar_articulos_con_titulo():
    """Retorna [(numero, titulo, listo)] de todos los artículos, ordenados por número"""
    resultado = []
    for numero in numeros_articulos():
        datos = leer_datos_articulo(numero, avisar=False) or {}
        resultado.append((numero, datos.get('titulo', ''), articulo_listo_para_publicar(numero)))
    return resultado


def obtener_estadisticas_articulos():
    """Totales de artículos y cuántos están listos para publicar"""
    articulos = listar_articulos_con_titulo()
    return {
        'total_articulos': len(articulos),
        'articulos_listos': sum(1 for _, _, listo in articulos if listo),
        'existe_carpeta': os.path.exists(_carpeta_productos()),
        'ruta_carpeta': os.path.abspath(_carpeta_productos())
    }


def leer_numero_config():
    """Número del próximo artículo a publicar (rotación secuencial)"""
    archivo_config = os.path.join(_carpeta_productos(), "config.txt")
    try:
        with open(archivo_config, 'r', encoding='utf-8') as f:
            return int(f.read().strip())
    except Exception:
        return 1


def guardar_numero_config(numero):
    """Guarda el número del próximo artículo a publicar"""
    os.makedirs(_carpeta_productos(), exist_ok=True)
    with open(os.path.join(_carpeta_productos(), "config.txt"), 'w', encoding='utf-8') as f:
        f.write(str(numero))


def obtener_articulos_a_publicar(config, cantidad=None):
    """
    Arma la lista de artículos a publicar en esta ejecución, en orden de rotación.
    Salta los artículos que no están listos (sin título, precio o imágenes).

    Returns:
        list[int]: números de artículo
    """
    numeros = numeros_articulos()
    total = len(numeros)
    if total == 0:
        print("❌ No hay artículos en la carpeta de productos")
        return []

    cantidad = min(cantidad or config['cantidad_por_ejecucion'], total)
    siguiente = leer_numero_config()
    # Empezar en el primer artículo existente desde el número guardado (o volver al inicio)
    inicio = next((k for k, n in enumerate(numeros) if n >= siguiente), 0)

    resultado = []
    for paso in range(total):
        numero = numeros[(inicio + paso) % total]
        if articulo_listo_para_publicar(numero):
            resultado.append(numero)
            if len(resultado) == cantidad:
                break

    print(f"📦 Total de artículos: {total}")
    print(f"🔢 Cantidad por ejecución: {cantidad}")
    for i, numero in enumerate(resultado, 1):
        print(f"   {i}. 📋 Articulo_{numero}")

    if not resultado:
        print("📭 Ningún artículo está listo para publicar (falta título, precio o imágenes)")

    return resultado


def avanzar_rotacion(numero_publicado):
    """Deja la rotación apuntando al artículo siguiente al publicado"""
    numeros = numeros_articulos()
    if not numeros:
        return
    siguientes = [n for n in numeros if n > numero_publicado]
    guardar_numero_config(siguientes[0] if siguientes else numeros[0])


def crear_estructura_carpetas():
    """Crea o ajusta las carpetas Articulo_N según cantidad_productos de config_global.txt"""
    config = leer_config_global()
    cantidad_deseada = config['cantidad_productos']
    carpeta_principal = _carpeta_productos()

    verificar_y_crear_estructura()

    carpetas_actuales = contar_articulos()

    print(f"\n📊 Estado actual:")
    print(f"   Carpetas existentes: {carpetas_actuales}")
    print(f"   Carpetas deseadas: {cantidad_deseada}")

    if carpetas_actuales == cantidad_deseada:
        print(f"\n✅ Ya existen {cantidad_deseada} carpetas. No se requiere acción.")
    elif cantidad_deseada > carpetas_actuales:
        faltantes = cantidad_deseada - carpetas_actuales
        print(f"\n📦 Faltan {faltantes} carpeta(s). Creando...")
        for i in range(carpetas_actuales + 1, cantidad_deseada + 1):
            crear_carpeta_articulo(i)
        print(f"\n✅ {faltantes} carpeta(s) creada(s) exitosamente")
    else:
        sobrantes = carpetas_actuales - cantidad_deseada
        print(f"\n🗑️  Sobran {sobrantes} carpeta(s). Procediendo a eliminar...")
        eliminar_carpetas_sobrantes(cantidad_deseada + 1, carpetas_actuales, config)

    crear_gitkeep_en_imagenes()
    print(f"\n✅ Estructura actualizada en: {os.path.abspath(carpeta_principal)}")


def crear_carpeta_articulo(numero):
    """Crea una carpeta Articulo_N con su subcarpeta de imágenes y su datos.txt de plantilla"""
    carpeta_articulo = _carpeta_articulo(numero)
    carpeta_imagenes = os.path.join(carpeta_articulo, "imagenes")
    archivo_datos = os.path.join(carpeta_articulo, "datos.txt")

    os.makedirs(carpeta_imagenes, exist_ok=True)

    if not os.path.exists(archivo_datos):
        ubicacion = leer_config_global()['ubicacion']
        plantilla = (
            "titulo=Ejemplo Producto\n"
            "precio=100\n"
            "categoria=Electrónica e informática\n"
            "estado=Nuevo\n"
            f"ubicacion={ubicacion}\n"
            "descripcion=Descripción detallada del producto aquí\n"
            "disponibilidad=Publicar como disponible\n"
            "encuentro_publico=Si\n"
            "etiquetas=\n"
            "sku="
        )
        with open(archivo_datos, 'w', encoding='utf-8') as f:
            f.write(plantilla)

    print(f"  ✓ Articulo_{numero} creado")


def eliminar_carpetas_sobrantes(desde, hasta, config):
    """Elimina carpetas sobrantes con cuenta regresiva y respaldo opcional"""
    carpetas_a_eliminar = []
    carpetas_con_datos = []

    for i in range(desde, hasta + 1):
        if os.path.exists(_carpeta_articulo(i)):
            carpetas_a_eliminar.append(i)
            info = verificar_contenido_carpeta(i)
            if info['tiene_datos'] or info['tiene_imagenes']:
                carpetas_con_datos.append(info)

    if not carpetas_a_eliminar:
        print("✅ No hay carpetas para eliminar")
        return

    if carpetas_con_datos:
        print(f"\n⚠️  ADVERTENCIA: {len(carpetas_con_datos)} carpeta(s) contienen datos:")
        for info in carpetas_con_datos:
            detalles = []
            if info['tiene_imagenes']:
                detalles.append(f"{info['num_imagenes']} imagen(es)")
            if info['tiene_datos']:
                detalles.append("datos.txt presente")
            print(f"   - Articulo_{info['numero']}: {', '.join(detalles)}")

    if config['confirmacion_borrado']:
        tiempo_espera = 10 if carpetas_con_datos else 5
        print(f"\n🗑️  Se eliminarán {len(carpetas_a_eliminar)} carpeta(s) en {tiempo_espera} segundos...")
        print("   Presiona Ctrl+C para CANCELAR\n")
        try:
            for i in range(tiempo_espera, 0, -1):
                print(f"   {i}...", end='\r', flush=True)
                time.sleep(1)
            print()
        except KeyboardInterrupt:
            print("\n\n❌ Eliminación cancelada por el usuario")
            return

    if config['backup_antes_borrar'] and carpetas_con_datos:
        crear_backup(carpetas_a_eliminar)

    print("\n🗑️  Eliminando carpetas...")
    for i in carpetas_a_eliminar:
        try:
            shutil.rmtree(_carpeta_articulo(i))
            print(f"  ✓ Articulo_{i} eliminado")
        except Exception as e:
            print(f"  ✗ Error eliminando Articulo_{i}: {e}")

    print(f"\n✅ {len(carpetas_a_eliminar)} carpeta(s) eliminada(s)")


def verificar_contenido_carpeta(numero):
    """Indica si una carpeta Articulo_N tiene imágenes o datos reales"""
    carpeta_imagenes = os.path.join(_carpeta_articulo(numero), "imagenes")
    archivo_datos = os.path.join(_carpeta_articulo(numero), "datos.txt")

    info = {'numero': numero, 'tiene_imagenes': False, 'num_imagenes': 0, 'tiene_datos': False}

    if os.path.exists(carpeta_imagenes):
        imagenes = [f for f in os.listdir(carpeta_imagenes) if f.lower().endswith(EXTENSIONES_IMAGEN)]
        info['num_imagenes'] = len(imagenes)
        info['tiene_imagenes'] = len(imagenes) > 0

    if os.path.exists(archivo_datos):
        with open(archivo_datos, 'r', encoding='utf-8') as f:
            contenido = f.read()
        info['tiene_datos'] = len(contenido) > 200 and 'Ejemplo Producto' not in contenido

    return info


def crear_backup(carpetas_a_eliminar):
    """Copia las carpetas indicadas a backups/<fecha> antes de eliminarlas"""
    carpeta_backup = os.path.join(_base_dir(), "backups", datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    os.makedirs(carpeta_backup, exist_ok=True)

    print(f"\n💾 Creando backup en: {carpeta_backup}")
    for i in carpetas_a_eliminar:
        if os.path.exists(_carpeta_articulo(i)):
            try:
                shutil.copytree(_carpeta_articulo(i), os.path.join(carpeta_backup, f"Articulo_{i}"))
                print(f"  ✓ Articulo_{i} respaldado")
            except Exception as e:
                print(f"  ✗ Error respaldando Articulo_{i}: {e}")
    print("✅ Backup completado")


def crear_gitkeep_en_imagenes():
    """Crea .gitkeep en cada carpeta de imágenes para mantenerlas en Git"""
    carpeta_principal = _carpeta_productos()
    if not os.path.exists(carpeta_principal):
        return

    for item in os.listdir(carpeta_principal):
        carpeta_imagenes = os.path.join(carpeta_principal, item, "imagenes")
        archivo_gitkeep = os.path.join(carpeta_imagenes, ".gitkeep")
        if item.startswith("Articulo_") and os.path.isdir(carpeta_imagenes) and not os.path.exists(archivo_gitkeep):
            with open(archivo_gitkeep, 'w') as f:
                f.write("")


# ============================================================
# TAREAS AUTOMÁTICAS
# ============================================================

MODULOS_DISPONIBLES = [
    ("extraer",  "🛍️  Extraer Catálogo de WhatsApp"),
    ("publicar", "▶️  Publicar Productos en Marketplace"),
    ("atender",  "💬  Atender Interesados en Messenger"),
]


def id_tarea(nombre):
    """Convierte el nombre de una tarea en un id sin espacios ni acentos, seguro para la línea de comandos"""
    import re
    import unicodedata
    sin_acentos = unicodedata.normalize('NFKD', nombre).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^A-Za-z0-9]+', '_', sin_acentos).strip('_') or 'Tarea'


def _ruta_tareas_programadas():
    return os.path.join(_base_dir(), 'tareas_programadas.json')


def leer_tareas_programadas():
    """Retorna {id_tarea: config} con la configuración propia de cada tarea automática"""
    import json
    ruta = _ruta_tareas_programadas()
    if not os.path.exists(ruta):
        return {}
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            return json.load(f).get('tareas', {})
    except Exception as e:
        print(f"⚠️  Error leyendo tareas programadas: {e}")
        return {}


def _guardar_tareas_programadas(tareas):
    import json
    try:
        with open(_ruta_tareas_programadas(), 'w', encoding='utf-8') as f:
            json.dump({'tareas': tareas}, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"⚠️  Error guardando tareas programadas: {e}")
        return False


def obtener_config_tarea(id_de_tarea):
    """
    Retorna la configuración de una tarea o None si no tiene.

    Formato: {'nombre': str, 'modulos': [str], 'cantidad': None | int}
    cantidad None significa usar la cantidad de productos por ejecución de la configuración general.
    """
    return leer_tareas_programadas().get(id_de_tarea)


def guardar_config_tarea(id_de_tarea, nombre, modulos, cantidad=None):
    tareas = leer_tareas_programadas()
    tareas[id_de_tarea] = {
        'nombre': nombre,
        'modulos': [m for m in modulos if m in dict(MODULOS_DISPONIBLES)],
        'cantidad': cantidad
    }
    return _guardar_tareas_programadas(tareas)


def eliminar_config_tarea(id_de_tarea):
    tareas = leer_tareas_programadas()
    if id_de_tarea in tareas:
        del tareas[id_de_tarea]
        _guardar_tareas_programadas(tareas)


PREFIJO_TAREAS = "AutomaPro_Marketplace"


def id_de_nombre_tarea(nombre):
    """Id en tareas_programadas.json a partir del nombre de la tarea en Windows"""
    n = nombre[1:] if nombre.startswith('\\') else nombre
    if n.startswith(PREFIJO_TAREAS + "_"):
        n = n[len(PREFIJO_TAREAS) + 1:]
    return id_tarea(n)


def modulos_secuencia_general():
    """Módulos activos de [SECUENCIA] en config_global.txt (lo que hacían las tareas antiguas)"""
    cfg = configparser.RawConfigParser(delimiters=('=',))
    cfg.read(os.path.join(_base_dir(), "config_global.txt"), encoding='utf-8')
    modulos = cfg.get('SECUENCIA', 'modulos_activos', fallback='publicar')
    return [m.strip() for m in modulos.split(',') if m.strip()]


def _comando_de_tarea_windows(nombre):
    """Comando que ejecuta una tarea de Windows, o '' si no se pudo leer"""
    import subprocess
    try:
        resultado = subprocess.run(
            ['schtasks', '/Query', '/TN', nombre, '/FO', 'LIST', '/V'],
            capture_output=True, text=True, encoding='cp850', errors='ignore',
            stdin=subprocess.DEVNULL, timeout=20,
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)
        )
    except Exception:
        return ''
    for linea in resultado.stdout.split('\n'):
        if ':' in linea:
            clave, valor = linea.split(':', 1)
            if 'Tarea que se ejecutar' in clave or 'Task To Run' in clave:
                return valor.strip()
    return ''


def migrar_tareas_antiguas():
    """
    Agrega --tarea al comando de las tareas creadas antes de esta versión, sin tocar sus días ni su hora,
    para que nunca se ejecuten por el camino del doble clic (que puede quedarse esperando una respuesta).
    Conserva el ejecutable que ya tenían. Retorna cuántas tareas convirtió.
    """
    import subprocess
    sin_ventana = getattr(subprocess, 'CREATE_NO_WINDOW', 0)

    try:
        lista = subprocess.run(
            ['schtasks', '/Query', '/FO', 'CSV', '/NH'],
            capture_output=True, text=True, encoding='cp850', errors='ignore',
            stdin=subprocess.DEVNULL, timeout=30, creationflags=sin_ventana
        )
    except Exception as e:
        print(f"⚠️  No se pudieron consultar las tareas: {e}")
        return 0

    nombres = []
    for linea in lista.stdout.splitlines():
        nombre = linea.split('","')[0].strip().strip('"')
        if PREFIJO_TAREAS in nombre:
            nombres.append(nombre.split('\\')[-1])

    migradas = 0
    for nombre in nombres:
        comando_actual = _comando_de_tarea_windows(nombre)
        if not comando_actual or '--tarea' in comando_actual:
            continue

        id_de_tarea = id_de_nombre_tarea(nombre)
        if comando_actual.lower().startswith('cmd /c') and comando_actual.endswith('"'):
            comando_nuevo = f'{comando_actual[:-1]} --tarea={id_de_tarea}"'
        else:
            comando_nuevo = f'{comando_actual} --tarea={id_de_tarea}'

        try:
            resultado = subprocess.run(
                ['schtasks', '/Change', '/TN', nombre, '/TR', comando_nuevo],
                capture_output=True, text=True, stdin=subprocess.DEVNULL,
                timeout=20, creationflags=sin_ventana
            )
        except Exception as e:
            print(f"⚠️  No se pudo actualizar la tarea {nombre}: {e}")
            continue

        if resultado.returncode == 0:
            if not obtener_config_tarea(id_de_tarea):
                guardar_config_tarea(id_de_tarea, nombre, modulos_secuencia_general())
            migradas += 1
        else:
            print(f"⚠️  No se pudo actualizar la tarea {nombre}: {resultado.stderr.strip()}")

    return migradas


def registrar_evento_tarea(id_de_tarea, texto):
    """Agrega una línea a registro_tareas.log para revisar después qué pasó en una ejecución automática"""
    linea = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  {id_de_tarea}  {texto}\n"
    try:
        with open(os.path.join(_base_dir(), 'registro_tareas.log'), 'a', encoding='utf-8') as f:
            f.write(linea)
    except Exception as e:
        print(f"⚠️  No se pudo escribir en registro_tareas.log: {e}")


# ============================================================
# NAVEGADOR
# ============================================================

def obtener_ruta_perfil_navegador():
    """
    Obtiene la ruta del perfil del navegador según configuración

    Returns:
        str: Ruta al perfil o None si usa perfil existente del sistema
    """
    config = leer_config_global()

    if config['usar_perfil_existente']:
        if config['navegador'] == 'firefox':
            return obtener_primer_perfil_firefox()
        elif config['navegador'] == 'chrome':
            return None
        else:
            print(f"⚠️  Navegador desconocido: {config['navegador']}")
            return None
    else:
        carpeta_perfil = os.path.join(_base_dir(), config['carpeta_perfil_custom'])
        if not os.path.exists(carpeta_perfil):
            os.makedirs(carpeta_perfil)
            print(f"✅ Carpeta de perfil creada: {carpeta_perfil}")
        return os.path.abspath(carpeta_perfil)


def obtener_primer_perfil_firefox():
    """
    Encuentra automáticamente el primer perfil de Firefox disponible

    Returns:
        str: Ruta al perfil de Firefox o None si no se encuentra
    """
    ruta_perfiles = os.path.expanduser("~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles")

    if not os.path.exists(ruta_perfiles):
        print(f"⚠️  No se encontró la carpeta de perfiles de Firefox: {ruta_perfiles}")
        return None

    perfiles = [f for f in os.listdir(ruta_perfiles) if os.path.isdir(os.path.join(ruta_perfiles, f))]

    if not perfiles:
        print("⚠️  No se encontraron perfiles de Firefox")
        return None

    perfil_seleccionado = os.path.join(ruta_perfiles, perfiles[0])
    print(f"🦊 Perfil Firefox detectado: {perfiles[0]}")
    return perfil_seleccionado


# ============================================================
# ATENCIÓN DE INTERESADOS (plantillas de mensajes)
# ============================================================

# Secciones del archivo de plantillas: (clave, título para mostrar)
PLANTILLAS_ATENCION = [
    ("PEDIR_CELULAR",    "1. Pedir el celular (primer mensaje al interesado)"),
    ("INSISTIR_CELULAR", "2. Insistir si no responde con un celular"),
    ("CONFIRMACION",     "3. Confirmar al interesado cuando envía su celular"),
    ("AVISO_VENDEDOR",   "4. Aviso al vendedor por WhatsApp"),
    ("DESPEDIDA",        "5. Despedida si no envía su celular tras las insistencias"),
    ("AVISO_ABANDONO",   "6. Aviso por WhatsApp de un interesado que no dio su celular"),
]

VARIABLES_PLANTILLAS = "{nombre} = interesado · {producto} = título · {celular} · {vendedor}"


PATRON_CELULAR_ECUADOR = None


def extraer_celular_ecuador(texto):
    """
    Busca un celular de Ecuador dentro de un texto y lo devuelve normalizado como 09XXXXXXXX
    (o None si no hay ninguno). Acepta 0991234567, 991234567, 099 123 4567, 099-123-4567,
    +593 99 123 4567 y 593991234567. No toma números más largos (cédulas, teléfonos fijos de 9 dígitos que no empiezan en 9).
    """
    import re
    global PATRON_CELULAR_ECUADOR
    if PATRON_CELULAR_ECUADOR is None:
        sep = r"[\s\-.()]*"
        PATRON_CELULAR_ECUADOR = re.compile(
            r"(?<![\d+])(?:(?:\+?593|0)" + sep + r")?9(?:" + sep + r"\d){8}(?!\d)")
    if not texto:
        return None
    for coincidencia in PATRON_CELULAR_ECUADOR.finditer(texto):
        digitos = re.sub(r"\D", "", coincidencia.group(0))
        if digitos.startswith("593"):
            digitos = digitos[3:]
        digitos = digitos.lstrip("0")
        if len(digitos) == 9 and digitos.startswith("9"):
            return "0" + digitos
    return None


def _ruta_plantillas_atencion(ejemplo=False):
    nombre = "plantillas.ejemplo.txt" if ejemplo else "plantillas.txt"
    return os.path.join(_base_dir(), "plantillas-atencion", nombre)


def leer_plantillas_atencion():
    """
    Retorna {clave: texto} de las plantillas de atención.
    Si aún no existe plantillas.txt, usa plantillas.ejemplo.txt.
    """
    ruta = _ruta_plantillas_atencion()
    if not os.path.exists(ruta):
        ruta = _ruta_plantillas_atencion(ejemplo=True)

    plantillas = _leer_archivo_plantillas(ruta)
    # Plantillas que faltan en el archivo personal (ej: las agregadas en versiones nuevas): se toman del ejemplo
    if any(not texto for texto in plantillas.values()):
        ejemplo = _leer_archivo_plantillas(_ruta_plantillas_atencion(ejemplo=True))
        for clave, texto in plantillas.items():
            if not texto:
                plantillas[clave] = ejemplo.get(clave, "")
    return plantillas


def _leer_archivo_plantillas(ruta):
    """{clave: texto} de un archivo de plantillas (claves sin texto quedan vacías)"""
    plantillas = {clave: "" for clave, _ in PLANTILLAS_ATENCION}
    if not os.path.exists(ruta):
        return plantillas

    seccion = None
    lineas = {clave: [] for clave, _ in PLANTILLAS_ATENCION}
    with open(ruta, 'r', encoding='utf-8') as f:
        for linea in f.read().split('\n'):
            limpia = linea.strip()
            if limpia.startswith('[') and limpia.endswith(']') and limpia[1:-1] in lineas:
                seccion = limpia[1:-1]
            elif seccion:
                lineas[seccion].append(linea.rstrip())

    for clave in lineas:
        plantillas[clave] = '\n'.join(lineas[clave]).strip()
    return plantillas


def guardar_plantillas_atencion(plantillas):
    """Guarda {clave: texto} en plantillas-atencion/plantillas.txt (archivo personal, no se sube a GitHub)"""
    ruta = _ruta_plantillas_atencion()
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    try:
        with open(ruta, 'w', encoding='utf-8') as f:
            for clave, _ in PLANTILLAS_ATENCION:
                f.write(f"[{clave}]\n{plantillas.get(clave, '').strip()}\n\n")
        return True
    except Exception as e:
        print(f"❌ Error guardando plantillas de atención: {e}")
        return False
