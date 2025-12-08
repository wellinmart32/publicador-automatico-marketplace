import time
from compartido.gestor_archivos import (
    crear_estructura_carpetas,
    contar_articulos,
    obtener_numero_articulo,
    leer_datos_articulo,
    obtener_imagenes_articulo,
    guardar_numero_config
)
from publicadores.publicador_marketplace import PublicadorMarketplace


def main():
    """Función principal que orquesta la publicación"""
    
    # Crear estructura si no existe
    crear_estructura_carpetas()
    
    # Obtener número de artículo
    numero_articulo = obtener_numero_articulo()
    
    if not numero_articulo:
        return
    
    print(f"\n✅ Artículo seleccionado: Articulo_{numero_articulo}")
    
    # Leer datos del artículo
    datos = leer_datos_articulo(numero_articulo)
    imagenes = obtener_imagenes_articulo(numero_articulo)
    
    if not datos:
        print("❌ No se pudieron leer los datos del artículo")
        return
    
    # Mostrar información del artículo
    print("\n📄 Datos del artículo:")
    print(f"  Título: {datos.get('titulo', 'N/A')}")
    print(f"  Precio: ${datos.get('precio', 'N/A')}")
    print(f"  Categoría: {datos.get('categoria', 'N/A')}")
    print(f"  Estado: {datos.get('estado', 'N/A')}")
    print(f"\n📸 Imágenes encontradas: {len(imagenes)}")
    
    if len(imagenes) == 0:
        print("⚠️  No hay imágenes. Agrega imágenes en la carpeta 'imagenes' antes de publicar.")
        return
    
    # Iniciar publicación automática
    publicador = PublicadorMarketplace()
    
    try:
        publicador.iniciar_navegador()
        exito = publicador.publicar_producto_completo(datos, imagenes)
        
        if exito:
            # Calcular siguiente número (con rotación)
            total = contar_articulos()
            siguiente = numero_articulo + 1 if numero_articulo < total else 1
            guardar_numero_config(siguiente)
            print(f"💾 Próximo artículo será: Articulo_{siguiente}")
        
        print("\n⏳ Esperando 2 segundos...")
        time.sleep(2)
        
    except Exception as error:
        print(f"❌ Error durante la publicación: {error}")
    
    finally:
        publicador.cerrar_navegador()
    
    print("\n✅ Proceso finalizado")


if __name__ == "__main__":
    main()
