import time
import json
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
    
    # CRÍTICO: Recargar el gestor DESPUÉS de cualquier operación previa
    # Esto asegura que tengamos los datos MÁS RECIENTES del JSON
    print("⏳ Esperando sincronización del sistema de archivos (5 segundos)...")
    time.sleep(5)
    
    print("\n🔄 Recargando registro desde archivo...")
    
    gestor = GestorRegistro()
    gestor.registro = gestor.cargar_registro()  # Forzar recarga del archivo
    
    # DEBUG ULTRA DETALLADO
    print(f"\n🔍 DEBUG POST-RECARGA:")
    print(f"   📄 Archivo JSON: {gestor.archivo_registro}")
    print(f"   📊 Índice en memoria: {gestor.registro.get('indice_catalogo_whatsapp', 'NO EXISTE')}")
    print(f"   ⏳ Pendientes en memoria: {gestor.registro.get('pendientes', 'NO EXISTE')}")
    print(f"   📅 Publicados hoy en memoria: {gestor.registro.get('publicaciones_hoy', 'NO EXISTE')}")
    print(f"   🔢 Total elementos historial: {len(gestor.registro.get('historial', []))}")
    
    # DEBUG: Detectar productos duplicados
    print(f"\n   🔍 Verificando productos duplicados en historial:")
    articulos_vistos = {}
    for entrada in gestor.registro.get('historial', []):
        num_art = entrada.get('articulo')
        titulo = entrada.get('titulo', 'Sin título')[:30]
        estado = entrada.get('estado', 'sin estado')
        
        if num_art in articulos_vistos:
            print(f"      ⚠️  DUPLICADO: Articulo_{num_art} ({titulo}) - Estado: {estado}")
            print(f"         Primera aparición: {articulos_vistos[num_art]}")
        else:
            articulos_vistos[num_art] = f"{titulo} - {estado}"
    
    # Verificar que el archivo físico coincide
    try:
        with open(gestor.archivo_registro, 'r', encoding='utf-8') as f:
            archivo_real = json.load(f)
            print(f"\n   🗂️  VERIFICACIÓN ARCHIVO FÍSICO:")
            print(f"      Índice en disco: {archivo_real.get('indice_catalogo_whatsapp', 'NO EXISTE')}")
            print(f"      Pendientes en disco: {archivo_real.get('pendientes', 'NO EXISTE')}")
            
            if archivo_real.get('indice_catalogo_whatsapp') != gestor.registro.get('indice_catalogo_whatsapp'):
                print(f"      ❌ DESINCRONIZADO: archivo != memoria")
            else:
                print(f"      ✅ Sincronizado correctamente")
    except Exception as e:
        print(f"   ❌ Error leyendo archivo físico: {e}")
    
    print()
    
    # Verificar que la recarga funcionó
    indice_catalogo = gestor.registro.get('indice_catalogo_whatsapp', 0)
    pendientes_count = len(gestor.registro.get('pendientes', []))
    
    print(f"   ✅ Registro recargado")
    print(f"   📊 Índice catálogo: {indice_catalogo}")
    print(f"   📦 Pendientes detectados: {pendientes_count}")
    print()
    
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
    total_articulos = contar_articulos()
    articulos_a_publicar = []
    
    if config['publicar_todos']:
        # MODO: Publicar todos los artículos disponibles
        print(f"📦 MODO: Publicar todos los artículos")
        print(f"   Total disponibles: {total_articulos}")
        print(f"   Límite diario restante: {config['max_publicaciones_por_dia'] - gestor.registro['publicaciones_hoy']}")
        
        # Obtener pendientes
        pendientes = gestor.obtener_articulos_pendientes()
        
        if pendientes:
            print(f"\n⏳ Artículos pendientes: {pendientes}")
            # Limitar por el máximo diario
            articulos_a_publicar = pendientes[:config['max_publicaciones_por_dia'] - gestor.registro['publicaciones_hoy']]
        else:
            print(f"\n✅ No hay artículos pendientes de publicar")
            articulos_a_publicar = []
        
        if articulos_a_publicar:
            print(f"\n🎯 Se publicarán los artículos: {articulos_a_publicar}")
        else:
            print(f"\n⚠️  No hay artículos para publicar")
            print(f"   • Si acabas de extraer, verifica que se hayan registrado correctamente")
            print(f"   • Si ya publicaste todo, ejecuta de nuevo para extraer más productos")
            
            # DEBUG: Mostrar el contenido del registro para diagnóstico
            print(f"\n🔍 DEBUG - Estado del registro:")
            print(f"   Pendientes en registro: {gestor.registro['pendientes']}")
            print(f"   Último publicado: {gestor.registro.get('ultimo_articulo_publicado', 0)}")
            print(f"   Historial (últimos 3):")
            for entrada in gestor.registro['historial'][-3:]:
                print(f"     - Articulo {entrada['articulo']}: {entrada['estado']}")
            
            input("\nPresiona Enter para salir...")
            return
        
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
