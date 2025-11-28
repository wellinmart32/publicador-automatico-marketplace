import os
import time

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
        
        # Crear archivo datos.txt con plantilla
        if not os.path.exists(archivo_datos):
            plantilla = """titulo=Ejemplo Producto
precio=100
categoria=Electronica
condicion=Nuevo
descripcion=Descripción del producto aquí
ubicacion=Guayaquil, Ecuador
envio=Si"""
            with open(archivo_datos, 'w', encoding='utf-8') as f:
                f.write(plantilla)
        
        print(f"✓ Articulo_{i} preparado")
    
    print("\n✅ Estructura creada exitosamente en:", os.path.abspath(carpeta_principal))

if __name__ == "__main__":
    crear_estructura_carpetas()
    print("\nPresiona Enter para cerrar...")
    input()
