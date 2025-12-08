import time
from compartido.gestor_archivos import (
    crear_estructura_carpetas,
    contar_articulos,
    obtener_numero_articulo,
    leer_datos_articulo,
    obtener_imagenes_articulo,
    guardar_numero_config,
    leer_config_global
)
from publicadores.publicador_marketplace import PublicadorMarketplace
from gestor_registro import GestorRegistro


def publicar_articulo_individual(numero_articulo, publicador, gestor, config):
    """Publica un artículo individual y registra el resultado"""
    
    print(f"\n{'='*60}")
    print(f"📦 PUBLICANDO ARTICULO_{numero_articulo}")
    print(f"{'='*60}\n")
    
    # Leer datos del artículo
    datos = leer_datos_articulo(numero_articulo)
    imagenes = obtener_imagenes_articulo(numero_articulo)
    
    if not datos:
        print(f"❌ No se pudieron leer los datos de Articulo_{numero_articulo}")
        gestor.registrar_error(numero_articulo, "Sin datos", "Archivo datos.txt no encontrado o inválido")
        return False
    
    # Mostrar información del artículo
    print(f"📄 Datos del artículo:")
    print(f"  Título: {datos.get('titulo', 'N/A')}")
    print(f"  Precio: ${datos.get('precio', 'N/A')}")
    print(f"  Categoría: {datos.get('categoria', 'N/A')}")
    print(f"  Estado: {datos.get('estado', 'N/A')}")
    print(f"\n📸 Imágenes encontradas: {len(imagenes)}")
    
    if len(imagenes) == 0:
        print("⚠️  No hay imágenes. Agrega imágenes en la carpeta 'imagenes' antes de publicar.")
        gestor.registrar_error(numero_articulo, datos.get('titulo', 'Sin título'), "Sin imágenes")
        return False
    
    # Publicar
    try:
        exito = publicador.publicar_producto_completo(datos, imagenes)
        
        if exito:
            # Registrar publicación exitosa
            gestor.registrar_publicacion_exitosa(
                articulo=numero_articulo,
                titulo=datos.get('titulo', 'Sin título')
            )
            
            print(f"\n✅ Articulo_{numero_articulo} publicado exitosamente")
            
            # Esperar entre publicaciones
            if config['tiempo_entre_publicaciones'] > 0:
                print(f"\n⏳ Esperando {config['tiempo_entre_publicaciones']}s antes de continuar...")
                time.sleep(config['tiempo_entre_publicaciones'])
            
            return True
        else:
            gestor.registrar_error(numero_articulo, datos.get('titulo', 'Sin título'), "Error en publicación")
            return False
            
    except Exception as error:
        print(f"❌ Error durante la publicación: {error}")
        gestor.registrar_error(numero_articulo, datos.get('titulo', 'Sin título'), str(error))
        return False


def main():
    """Función principal que orquesta la publicación"""
    
    print("\n" + "="*60)
    print("🚀 PUBLICADOR AUTOMÁTICO DE MARKETPLACE")
    print("="*60 + "\n")
    
    # Leer configuración
    try:
        config = leer_config_global()
    except Exception as e:
        print(f"❌ Error leyendo configuración: {e}")
        input("\nPresiona Enter para salir...")
        return
    
    # Crear estructura si no existe
    crear_estructura_carpetas()
    
    # Inicializar gestor de registro
    gestor = GestorRegistro()
    
    # Verificar límite diario
    if not gestor.puede_publicar_hoy(config['max_publicaciones_por_dia']):
        print(f"⚠️  LÍMITE DIARIO ALCANZADO")
        print(f"   Ya publicaste {gestor.registro['publicaciones_hoy']} productos hoy")
        print(f"   Límite configurado: {config['max_publicaciones_por_dia']}")
        print("\n💡 Puedes cambiar el límite en '4_Configurador.bat'")
        input("\nPresiona Enter para salir...")
        return
    
    # Mostrar estadísticas
    gestor.mostrar_estadisticas()
    
    # Determinar qué publicar
    if config['publicar_todos']:
        # MODO: Publicar todos los artículos disponibles
        total_articulos = contar_articulos()
        
        if total_articulos == 0:
            print("❌ No hay artículos disponibles.")
            input("\nPresiona Enter para salir...")
            return
        
        print(f"📦 MODO: Publicar todos los artículos")
        print(f"   Total disponibles: {total_articulos}")
        print(f"   Límite diario restante: {config['max_publicaciones_por_dia'] - gestor.registro['publicaciones_hoy']}")
        
        # Obtener pendientes o empezar desde el siguiente
        pendientes = gestor.obtener_articulos_pendientes()
        
        if pendientes:
            print(f"\n⏳ Artículos pendientes: {pendientes}")
            articulos_a_publicar = pendientes[:config['max_publicaciones_por_dia'] - gestor.registro['publicaciones_hoy']]
        else:
            # Publicar desde el siguiente artículo
            siguiente = gestor.obtener_siguiente_articulo()
            articulos_a_publicar = list(range(siguiente, min(siguiente + config['max_publicaciones_por_dia'] - gestor.registro['publicaciones_hoy'], total_articulos + 1)))
        
        print(f"\n🎯 Se publicarán los artículos: {articulos_a_publicar}")
        
    else:
        # MODO: Publicar solo el siguiente artículo
        print(f"📦 MODO: Publicar siguiente artículo")
        
        numero_articulo = obtener_numero_articulo()
        
        if not numero_articulo:
            input("\nPresiona Enter para salir...")
            return
        
        articulos_a_publicar = [numero_articulo]
        print(f"\n✅ Artículo seleccionado: Articulo_{numero_articulo}")
    
    # Iniciar publicación automática
    publicador = PublicadorMarketplace()
    
    try:
        publicador.iniciar_navegador()
        
        publicaciones_exitosas = 0
        publicaciones_fallidas = 0
        
        for numero in articulos_a_publicar:
            # Verificar límite diario
            if not gestor.puede_publicar_hoy(config['max_publicaciones_por_dia']):
                print(f"\n⚠️  Límite diario alcanzado. Deteniendo publicación.")
                break
            
            exito = publicar_articulo_individual(numero, publicador, gestor, config)
            
            if exito:
                publicaciones_exitosas += 1
                
                # Calcular siguiente número (con rotación)
                total = contar_articulos()
                siguiente = numero + 1 if numero < total else 1
                guardar_numero_config(siguiente)
            else:
                publicaciones_fallidas += 1
        
        # Resumen final
        print("\n" + "="*60)
        print("📊 RESUMEN DE PUBLICACIÓN")
        print("="*60)
        print(f"✅ Exitosas: {publicaciones_exitosas}")
        print(f"❌ Fallidas: {publicaciones_fallidas}")
        print(f"📅 Publicadas hoy: {gestor.registro['publicaciones_hoy']}/{config['max_publicaciones_por_dia']}")
        print("="*60)
        
        # Mostrar estadísticas actualizadas
        gestor.mostrar_estadisticas()
        
        print("\n⏳ Esperando 2 segundos...")
        time.sleep(2)
        
    except Exception as error:
        print(f"❌ Error durante la publicación: {error}")
        import traceback
        traceback.print_exc()
    
    finally:
        publicador.cerrar_navegador()
    
    print("\n✅ Proceso finalizado\n")


if __name__ == "__main__":
    main()
