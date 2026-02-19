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
from gestor_licencias import GestorLicencias
from dialogos_licencia import DialogosLicencia


def verificar_licencia_inicio():
    """Verificar licencia al iniciar la aplicación"""
    gestor = GestorLicencias("Marketplace")
    codigo_guardado = gestor.obtener_codigo_guardado()
    
    if not codigo_guardado:
        codigo = DialogosLicencia.solicitar_codigo_licencia()
        if codigo:
            gestor.guardar_codigo_licencia(codigo)
            codigo_guardado = codigo
        else:
            print("❌ No se ingresó código de licencia")
            return None
    
    resultado = gestor.verificar_licencia(codigo_guardado)
    
    if not resultado['valida']:
        DialogosLicencia.mostrar_trial_expirado()
        return None
    
    if resultado.get('developer_permanente'):
        print("\n👑 Código developer permanente detectado")
        print("✅ Licencia completa activada - Todas las funciones desbloqueadas\n")
    elif resultado['tipo'] == 'TRIAL':
        DialogosLicencia.mostrar_banner_trial(resultado.get('diasRestantes', 0))
    else:
        print("\n✅ Licencia completa activada - Todas las funciones desbloqueadas\n")
    
    return resultado


def publicar_articulo_individual(numero_articulo, publicador, gestor, config):
    """Publica un artículo individual y registra el resultado"""
    
    print(f"\n{'='*60}")
    print(f"📦 PUBLICANDO ARTICULO_{numero_articulo}")
    print(f"{'='*60}\n")
    
    datos = leer_datos_articulo(numero_articulo)
    imagenes = obtener_imagenes_articulo(numero_articulo)
    
    if not datos:
        print(f"❌ No se pudieron leer los datos de Articulo_{numero_articulo}")
        gestor.registrar_error(numero_articulo, "Sin datos", "Archivo datos.txt no encontrado o inválido")
        return False
    
    print(f"📄 Datos del artículo:")
    print(f"  Título: {datos.get('titulo', 'N/A')}")
    print(f"  Precio: ${datos.get('precio', 'N/A')}")
    print(f"  Categoría: {datos.get('categoria', 'N/A')}")
    print(f"  Estado: {datos.get('estado', 'N/A')}")
    print(f"\n📸 Imágenes encontradas: {len(imagenes)}")
    
    if len(imagenes) == 0:
        print("⚠️  No hay imágenes. Agrega imágenes en la carpeta 'imagenes' antes de publicar.")
    
    inicio = time.time()
    exito = publicador.publicar_producto_completo(datos, imagenes)
    tiempo = time.time() - inicio
    
    if exito:
        gestor.registrar_publicacion_exitosa(
            f"Articulo_{numero_articulo}",
            datos.get('titulo', ''),
            len(str(datos)),
            1,
            tiempo
        )
        print(f"\n✅ Articulo_{numero_articulo} publicado exitosamente")
        return True
    else:
        gestor.registrar_error(
            f"Articulo_{numero_articulo}",
            "publicacion",
            "Falló el proceso de publicación"
        )
        print(f"\n❌ No se pudo publicar Articulo_{numero_articulo}")
        return False


def main():
    """Función principal del publicador de marketplace"""
    
    # VERIFICAR LICENCIA PRIMERO
    estado_licencia = verificar_licencia_inicio()
    
    if not estado_licencia:
        print("\n❌ No se pudo verificar la licencia. Cerrando aplicación...")
        input("\nPresiona Enter para salir...")
        return
    
    print("\n" + "="*60)
    print(" " * 10 + "🚀 PUBLICADOR AUTOMÁTICO MARKETPLACE")
    print("="*60 + "\n")
    
    # Cargar configuración
    try:
        config = leer_config_global()
    except Exception as e:
        print(f"❌ Error leyendo configuración: {e}")
        input("\nPresiona Enter para salir...")
        return
    
    # Inicializar gestor de registro
    gestor = GestorRegistro()
    
    # Mostrar estadísticas
    gestor.mostrar_estadisticas()
    
    # Contar artículos disponibles
    total_articulos = contar_articulos()
    
    if total_articulos == 0:
        print("❌ No hay artículos para publicar")
        print("   Ejecuta primero: py crear_estructura.py")
        input("\nPresiona Enter para salir...")
        return
    
    print(f"\n📦 Artículos disponibles: {total_articulos}")
    
    # Obtener número de artículo a publicar
    numero_articulo = obtener_numero_articulo()
    
    print(f"\n🎯 Publicando Articulo_{numero_articulo}...")
    
    # Inicializar publicador
    print("\n🌐 Inicializando navegador...")
    publicador = PublicadorMarketplace()
    
    try:
        exito = publicar_articulo_individual(numero_articulo, publicador, gestor, config)
        
        if exito:
            # Avanzar al siguiente artículo
            siguiente = (numero_articulo % total_articulos) + 1
            guardar_numero_config(siguiente)
            print(f"\n➡️  Próxima vez se publicará: Articulo_{siguiente}")
            
            print("\n" + "="*60)
            print("✅ PROCESO COMPLETADO EXITOSAMENTE")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("❌ NO SE PUDO COMPLETAR LA PUBLICACIÓN")
            print("="*60)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso cancelado por el usuario")
    
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        publicador.cerrar_navegador()
    
    print("\n" + "="*70)
    print("✅ Proceso completado - La ventana se cerrará en 10 segundos...")
    print("="*70)

    import time
    for i in range(10, 0, -1):
        print(f"\rCerrando en {i} segundos...", end='', flush=True)
        time.sleep(1)
    print("\r" + " " * 50 + "\r", end='')


if __name__ == "__main__":
    main()