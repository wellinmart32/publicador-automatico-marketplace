import os
import configparser
import shutil
import time
from datetime import datetime


# ============================================================
# FUNCIONES DE LECTURA DE CONFIGURACIÓN
# ============================================================

def leer_config_global():
    """Lee config_global.txt y retorna un diccionario con la configuración"""
    archivo_config = "config_global.txt"
    
    if not os.path.exists(archivo_config):
        print("⚠️  No existe config_global.txt. Creando configuración por defecto...")
        crear_config_defecto()
    
    config = configparser.ConfigParser()
    config.read(archivo_config, encoding='utf-8')
    
    # Convertir a diccionario simple
    config_dict = {
        'cantidad_productos': int(config['GENERAL']['cantidad_productos']),
        'modo': config['GENERAL']['modo'],
        'contacto_whatsapp': config['EXTRACCION']['contacto_whatsapp'],
        'auto_scroll': int(config['EXTRACCION']['auto_scroll']),
        'productos_por_extraccion': int(config['EXTRACCION']['productos_por_extraccion']),
        'auto_publicar': config['PUBLICACION']['auto_publicar'].lower() == 'si',
        'tiempo_entre_publicaciones': int(config['PUBLICACION']['tiempo_entre_publicaciones']),
        'max_publicaciones_por_dia': int(config['PUBLICACION']['max_publicaciones_por_dia']),
        'publicar_todos': config['PUBLICACION']['publicar_todos'].lower() == 'si',
        'confirmacion_borrado': config['SEGURIDAD']['confirmacion_borrado'].lower() == 'si',
        'backup_antes_borrar': config['SEGURIDAD']['backup_antes_borrar'].lower() == 'si'
    }
    
    return config_dict


def crear_config_defecto():
    """Crea config_global.txt con valores por defecto"""
    contenido = """# ============================================================
# CONFIGURACIÓN GLOBAL DEL SISTEMA
# ============================================================

[GENERAL]
cantidad_productos = 5
modo = completo

[EXTRACCION]
contacto_whatsapp = Trabajo John
auto_scroll = 5
productos_por_extraccion = 5

[PUBLICACION]
auto_publicar = si
tiempo_entre_publicaciones = 10
max_publicaciones_por_dia = 20
publicar_todos = si

[SEGURIDAD]
confirmacion_borrado = si
backup_antes_borrar = si
"""
    
    with open("config_global.txt", 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("✅ config_global.txt creado con valores por defecto")


# ============================================================
# FUNCIONES DE GESTIÓN DE CARPETAS
# ============================================================

def crear_estructura_carpetas():
    """Crea/actualiza la jerarquía de carpetas según config_global.txt"""
    config = leer_config_global()
    cantidad_deseada = config['cantidad_productos']
    
    carpeta_principal = "ArticulosMarketplace"
    
    # Crear carpeta principal si no existe
    if not os.path.exists(carpeta_principal):
        os.makedirs(carpeta_principal)
        print(f"✓ Carpeta principal '{carpeta_principal}' creada")
    
    # Crear archivo de configuración si no existe
    archivo_config = os.path.join(carpeta_principal, "config.txt")
    if not os.path.exists(archivo_config):
        with open(archivo_config, 'w', encoding='utf-8') as f:
            f.write("1")
        print(f"✓ Archivo 'config.txt' creado")
    
    # Contar carpetas actuales
    carpetas_actuales = contar_articulos()
    
    print(f"\n📊 Estado actual:")
    print(f"   Carpetas existentes: {carpetas_actuales}")
    print(f"   Carpetas deseadas: {cantidad_deseada}")
    
    # Decidir qué hacer
    if carpetas_actuales == cantidad_deseada:
        print(f"\n✅ Ya existen {cantidad_deseada} carpetas. No se requiere acción.")
        return
    
    elif cantidad_deseada > carpetas_actuales:
        # AGREGAR carpetas faltantes
        faltantes = cantidad_deseada - carpetas_actuales
        print(f"\n📦 Faltan {faltantes} carpeta(s). Creando...")
        
        for i in range(carpetas_actuales + 1, cantidad_deseada + 1):
            crear_carpeta_articulo(i)
        
        print(f"\n✅ {faltantes} carpeta(s) creada(s) exitosamente")
    
    else:
        # ELIMINAR carpetas sobrantes
        sobrantes = carpetas_actuales - cantidad_deseada
        print(f"\n🗑️  Sobran {sobrantes} carpeta(s). Procediendo a eliminar...")
        
        eliminar_carpetas_sobrantes(cantidad_deseada + 1, carpetas_actuales, config)
    
    # Crear archivos .gitkeep
    crear_gitkeep_en_imagenes()
    
    print(f"\n✅ Estructura actualizada en: {os.path.abspath(carpeta_principal)}")


def crear_carpeta_articulo(numero):
    """Crea una carpeta de artículo individual con su estructura"""
    carpeta_principal = "ArticulosMarketplace"
    carpeta_articulo = os.path.join(carpeta_principal, f"Articulo_{numero}")
    carpeta_imagenes = os.path.join(carpeta_articulo, "imagenes")
    archivo_datos = os.path.join(carpeta_articulo, "datos.txt")
    
    # Crear carpeta del artículo
    if not os.path.exists(carpeta_articulo):
        os.makedirs(carpeta_articulo)
    
    # Crear carpeta de imágenes
    if not os.path.exists(carpeta_imagenes):
        os.makedirs(carpeta_imagenes)
    
    # ✅ PLANTILLA ACTUALIZADA (agregar campo ubicacion)
    if not os.path.exists(archivo_datos):
        plantilla = """titulo=Ejemplo Producto
precio=100
categoria=Electrónica e informática
estado=Nuevo
ubicacion=Mall del Sol, Guayaquil
descripcion=Descripción detallada del producto aquí
disponibilidad=Publicar como disponible
encuentro_publico=Si
etiquetas=
sku="""
        with open(archivo_datos, 'w', encoding='utf-8') as f:
            f.write(plantilla)
    
    print(f"  ✓ Articulo_{numero} creado")


def eliminar_carpetas_sobrantes(desde, hasta, config):
    """Elimina carpetas sobrantes con confirmación y backup opcional"""
    carpeta_principal = "ArticulosMarketplace"
    carpetas_a_eliminar = []
    carpetas_con_datos = []
    
    # Analizar carpetas a eliminar
    for i in range(desde, hasta + 1):
        carpeta = os.path.join(carpeta_principal, f"Articulo_{i}")
        if os.path.exists(carpeta):
            carpetas_a_eliminar.append(i)
            
            # Verificar si tiene contenido
            info = verificar_contenido_carpeta(i)
            if info['tiene_datos'] or info['tiene_imagenes']:
                carpetas_con_datos.append(info)
    
    if not carpetas_a_eliminar:
        print("✅ No hay carpetas para eliminar")
        return
    
    # Mostrar advertencia si hay datos
    if carpetas_con_datos:
        print(f"\n⚠️  ADVERTENCIA: {len(carpetas_con_datos)} carpeta(s) contienen datos:")
        for info in carpetas_con_datos:
            detalles = []
            if info['tiene_imagenes']:
                detalles.append(f"{info['num_imagenes']} imagen(es)")
            if info['tiene_datos']:
                detalles.append("datos.txt presente")
            print(f"   - Articulo_{info['numero']}: {', '.join(detalles)}")
    
    # Decidir tiempo de confirmación
    if config['confirmacion_borrado']:
        if carpetas_con_datos:
            tiempo_espera = 10  # 10 segundos si hay datos
            print(f"\n🗑️  Se eliminarán en {tiempo_espera} segundos...")
        else:
            tiempo_espera = 5  # 5 segundos si están vacías
            print(f"\n🗑️  Se eliminarán {len(carpetas_a_eliminar)} carpeta(s) vacía(s) en {tiempo_espera} segundos...")
        
        print("   Presiona Ctrl+C para CANCELAR\n")
        
        # Countdown
        try:
            for i in range(tiempo_espera, 0, -1):
                print(f"   {i}...", end='\r', flush=True)
                time.sleep(1)
            print()
        except KeyboardInterrupt:
            print("\n\n❌ Eliminación cancelada por el usuario")
            return
    
    # Crear backup si está configurado
    if config['backup_antes_borrar'] and carpetas_con_datos:
        crear_backup(carpetas_a_eliminar)
    
    # Eliminar carpetas
    print("\n🗑️  Eliminando carpetas...")
    for i in carpetas_a_eliminar:
        carpeta = os.path.join(carpeta_principal, f"Articulo_{i}")
        try:
            shutil.rmtree(carpeta)
            print(f"  ✓ Articulo_{i} eliminado")
        except Exception as e:
            print(f"  ✗ Error eliminando Articulo_{i}: {e}")
    
    print(f"\n✅ {len(carpetas_a_eliminar)} carpeta(s) eliminada(s)")


def verificar_contenido_carpeta(numero):
    """Verifica si una carpeta tiene imágenes o datos"""
    carpeta_principal = "ArticulosMarketplace"
    carpeta_articulo = os.path.join(carpeta_principal, f"Articulo_{numero}")
    carpeta_imagenes = os.path.join(carpeta_articulo, "imagenes")
    archivo_datos = os.path.join(carpeta_articulo, "datos.txt")
    
    info = {
        'numero': numero,
        'tiene_imagenes': False,
        'num_imagenes': 0,
        'tiene_datos': False
    }
    
    # Verificar imágenes
    if os.path.exists(carpeta_imagenes):
        imagenes = [f for f in os.listdir(carpeta_imagenes) 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))
                   and f != '.gitkeep']
        info['num_imagenes'] = len(imagenes)
        info['tiene_imagenes'] = len(imagenes) > 0
    
    # Verificar datos.txt
    if os.path.exists(archivo_datos):
        # Verificar que no sea la plantilla vacía
        with open(archivo_datos, 'r', encoding='utf-8') as f:
            contenido = f.read()
            # Si tiene más de 200 caracteres, asumimos que tiene datos reales
            info['tiene_datos'] = len(contenido) > 200 and 'Ejemplo Producto' not in contenido
    
    return info


def crear_backup(carpetas_a_eliminar):
    """Crea backup de las carpetas antes de eliminarlas"""
    carpeta_principal = "ArticulosMarketplace"
    carpeta_backup = os.path.join("backups", datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    
    os.makedirs(carpeta_backup, exist_ok=True)
    
    print(f"\n💾 Creando backup en: {carpeta_backup}")
    
    for i in carpetas_a_eliminar:
        carpeta_origen = os.path.join(carpeta_principal, f"Articulo_{i}")
        carpeta_destino = os.path.join(carpeta_backup, f"Articulo_{i}")
        
        if os.path.exists(carpeta_origen):
            try:
                shutil.copytree(carpeta_origen, carpeta_destino)
                print(f"  ✓ Articulo_{i} respaldado")
            except Exception as e:
                print(f"  ✗ Error respaldando Articulo_{i}: {e}")
    
    print(f"✅ Backup completado")


# ============================================================
# FUNCIONES EXISTENTES (Mantener compatibilidad)
# ============================================================

def contar_articulos():
    """Cuenta cuántas carpetas de artículos existen"""
    carpeta_principal = "ArticulosMarketplace"
    contador = 0
    
    if not os.path.exists(carpeta_principal):
        return 0
    
    # Contar carpetas que empiecen con "Articulo_"
    for item in os.listdir(carpeta_principal):
        ruta_completa = os.path.join(carpeta_principal, item)
        if os.path.isdir(ruta_completa) and item.startswith("Articulo_"):
            contador += 1
    
    return contador


def leer_numero_config():
    """Lee el número del último artículo publicado desde config.txt"""
    archivo_config = os.path.join("ArticulosMarketplace", "config.txt")
    
    try:
        with open(archivo_config, 'r', encoding='utf-8') as f:
            numero = int(f.read().strip())
            return numero
    except:
        return 1


def guardar_numero_config(numero):
    """Guarda el número del próximo artículo a publicar en config.txt"""
    archivo_config = os.path.join("ArticulosMarketplace", "config.txt")
    
    with open(archivo_config, 'w', encoding='utf-8') as f:
        f.write(str(numero))


def obtener_numero_articulo():
    """Solicita número al usuario o lee automáticamente de config.txt"""
    import threading
    
    total_articulos = contar_articulos()
    
    if total_articulos == 0:
        print("❌ No hay artículos disponibles.")
        return None
    
    print(f"\n📦 Total de artículos disponibles: {total_articulos}")
    print("Ingresa el número del artículo a publicar (0 o Enter para automático):")
    print("Esperando 7 segundos...")
    
    # Variable para almacenar el input
    entrada_usuario = [""]
    
    def obtener_input():
        try:
            entrada_usuario[0] = input("Número: ")
        except:
            pass
    
    # Crear thread para input
    thread_input = threading.Thread(target=obtener_input)
    thread_input.daemon = True
    thread_input.start()
    
    # Esperar 7 segundos
    thread_input.join(timeout=7)
    
    # Procesar entrada
    numero = None
    if entrada_usuario[0].strip():
        try:
            numero = int(entrada_usuario[0])
            if numero <= 0 or numero > total_articulos:
                print(f"❌ Número inválido. Usando automático...")
                numero = None
        except:
            print(f"❌ Entrada inválida. Usando automático...")
            numero = None
    
    # Si no hay número válido, leer de config
    if numero is None:
        numero = leer_numero_config()
        print(f"📖 Usando automáticamente: Artículo {numero}")
    else:
        print(f"✅ Seleccionado manualmente: Artículo {numero}")
    
    # Validar que el número esté en rango
    if numero > total_articulos:
        numero = 1
    
    return numero


def leer_datos_articulo(numero_articulo):
    """Lee los datos del archivo datos.txt del artículo especificado"""
    carpeta_articulo = os.path.join("ArticulosMarketplace", f"Articulo_{numero_articulo}")
    archivo_datos = os.path.join(carpeta_articulo, "datos.txt")
    
    if not os.path.exists(archivo_datos):
        print(f"❌ No se encontró el archivo datos.txt en Articulo_{numero_articulo}")
        return None
    
    # Leer archivo y parsear campos
    datos = {}
    with open(archivo_datos, 'r', encoding='utf-8') as f:
        for linea in f:
            linea = linea.strip()
            if '=' in linea:
                clave, valor = linea.split('=', 1)
                datos[clave.strip()] = valor.strip()
    
    return datos


def crear_gitkeep_en_imagenes():
    """Crea archivos .gitkeep en carpetas de imágenes para mantenerlas en Git"""
    carpeta_principal = "ArticulosMarketplace"
    
    if not os.path.exists(carpeta_principal):
        return
    
    for item in os.listdir(carpeta_principal):
        ruta_articulo = os.path.join(carpeta_principal, item)
        if os.path.isdir(ruta_articulo) and item.startswith("Articulo_"):
            carpeta_imagenes = os.path.join(ruta_articulo, "imagenes")
            archivo_gitkeep = os.path.join(carpeta_imagenes, ".gitkeep")
            
            if os.path.exists(carpeta_imagenes) and not os.path.exists(archivo_gitkeep):
                with open(archivo_gitkeep, 'w') as f:
                    f.write("")


def obtener_imagenes_articulo(numero_articulo):
    """Obtiene la lista de rutas de imágenes del artículo"""
    carpeta_imagenes = os.path.join("ArticulosMarketplace", f"Articulo_{numero_articulo}", "imagenes")
    
    if not os.path.exists(carpeta_imagenes):
        return []
    
    # Obtener archivos de imagen
    extensiones_validas = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    imagenes = []
    
    for archivo in os.listdir(carpeta_imagenes):
        extension = os.path.splitext(archivo)[1].lower()
        if extension in extensiones_validas:
            ruta_completa = os.path.abspath(os.path.join(carpeta_imagenes, archivo))
            imagenes.append(ruta_completa)
    
    return imagenes[:10]  # Máximo 10 imágenes
    