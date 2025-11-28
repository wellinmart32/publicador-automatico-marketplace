import os

def crear_estructura_carpetas():
    """Crea la jerarquía de carpetas para los artículos"""
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
    
    # Crear 5 carpetas de artículos por defecto
    for i in range(1, 6):
        carpeta_articulo = os.path.join(carpeta_principal, f"Articulo_{i}")
        carpeta_imagenes = os.path.join(carpeta_articulo, "imagenes")
        archivo_datos = os.path.join(carpeta_articulo, "datos.txt")
        
        # Crear carpeta del artículo
        if not os.path.exists(carpeta_articulo):
            os.makedirs(carpeta_articulo)
        
        # Crear carpeta de imágenes
        if not os.path.exists(carpeta_imagenes):
            os.makedirs(carpeta_imagenes)
        
        # Crear archivo datos.txt con plantilla actualizada
        if not os.path.exists(archivo_datos):
            plantilla = """titulo=Ejemplo Producto
precio=100
categoria=Electrónica e informática
estado=Nuevo
descripcion=Descripción detallada del producto aquí
disponibilidad=Publicar como disponible
encuentro_publico=Si
etiquetas=
sku="""
            with open(archivo_datos, 'w', encoding='utf-8') as f:
                f.write(plantilla)
        
        print(f"✓ Articulo_{i} preparado")
    
    print("\n✅ Estructura creada exitosamente en:", os.path.abspath(carpeta_principal))


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
    total_articulos = contar_articulos()
    
    if total_articulos == 0:
        print("❌ No hay artículos disponibles. Ejecuta primero la creación de estructura.")
        return None
    
    print(f"\n📦 Total de artículos disponibles: {total_articulos}")
    print("Ingresa el número del artículo a publicar (0 para automático):")
    print("Esperando 5 segundos...")
    
    # Esperar input del usuario
    entrada_usuario = ""
    
    try:
        entrada_usuario = input("Número: ")
    except:
        entrada_usuario = ""
    
    # Procesar entrada
    try:
        numero = int(entrada_usuario)
        
        # Si es 0 o inválido, leer de config
        if numero <= 0 or numero > total_articulos:
            numero = leer_numero_config()
            print(f"📖 Leyendo de config.txt: Artículo {numero}")
    except:
        # Si no es un número válido, leer de config
        numero = leer_numero_config()
        print(f"📖 Leyendo de config.txt: Artículo {numero}")
    
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
