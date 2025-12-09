from extractores.extractor_whatsapp import ExtractorWhatsApp
from compartido.gestor_archivos import leer_config_global, contar_articulos
from gestor_registro import GestorRegistro
import sys
import time


def main():
    """Script para extraer productos del catálogo de WhatsApp - CON ÍNDICE DEL CATÁLOGO"""
    
    print("\n" + "="*60)
    print("📱 EXTRACTOR DE CATÁLOGO DE WHATSAPP")
    print("="*60 + "\n")
    
    # Leer configuración
    try:
        config = leer_config_global()
    except Exception as e:
        print(f"❌ Error leyendo configuración: {e}")
        print("   Ejecuta '4_Configurador.bat' para configurar el sistema")
        input("\nPresiona Enter para salir...")
        return
    
    # Inicializar gestor de registro
    gestor = GestorRegistro()
    
    # Obtener índice actual del catálogo de WhatsApp
    indice_catalogo = gestor.obtener_indice_catalogo()
    
    # Determinar desde qué artículo (carpeta) comenzar
    articulo_inicio = 1
    total_carpetas = contar_articulos()
    
    if gestor.registro['pendientes']:
        # Si hay pendientes, extraer desde el mínimo pendiente
        articulo_inicio = min(gestor.registro['pendientes'])
        print(f"📦 Hay artículos pendientes, continuando desde Articulo_{articulo_inicio}")
        
    elif gestor.registro['ultimo_articulo_publicado'] > 0:
        # Continuar desde el siguiente al último publicado (rotación de carpetas)
        articulo_inicio = gestor.registro['ultimo_articulo_publicado'] + 1
        
        # Si excede el total de carpetas, volver a 1
        if articulo_inicio > total_carpetas:
            articulo_inicio = 1
            print(f"🔄 Rotación de carpetas: volviendo a Articulo_1")
        else:
            print(f"➡️  Continuando desde Articulo_{articulo_inicio}")
    else:
        print(f"🆕 Primera extracción")
    
    # Mostrar información del catálogo
    print(f"\n📌 ÍNDICE DEL CATÁLOGO DE WHATSAPP:")
    print(f"   Último producto extraído: {indice_catalogo}")
    print(f"   Próximo producto a extraer: {indice_catalogo + 1}")
    
    # Mostrar configuración
    print(f"\n⚙️  CONFIGURACIÓN AUTOMÁTICA:")
    print(f"   📱 Contacto WhatsApp: {config['contacto_whatsapp']}")
    print(f"   📦 Productos a extraer: {config['productos_por_extraccion']}")
    print(f"   🎯 Guardar en carpetas: Articulo_{articulo_inicio} - Articulo_{articulo_inicio + config['productos_por_extraccion'] - 1}")
    print(f"   📜 Auto scroll: {config['auto_scroll']} veces")
    print(f"   🚀 Auto publicar: {'Sí' if config['auto_publicar'] else 'No'}")
    
    print("\n" + "="*60)
    print("⏳ Iniciando en 3 segundos... (Presiona Ctrl+C para cancelar)")
    print("="*60 + "\n")
    
    # Countdown
    try:
        for i in range(3, 0, -1):
            print(f"   {i}...", end='\r', flush=True)
            sys.stdout.flush()
            time.sleep(1)
        print("   ✅ ¡Iniciando extracción!\n")
    except KeyboardInterrupt:
        print("\n\n❌ Cancelado por el usuario\n")
        sys.exit(0)
    
    # Ejecutar extracción
    extractor = ExtractorWhatsApp()
    
    try:
        print("🌐 Iniciando navegador y conectando a WhatsApp Web...")
        
        # Extraer productos desde el índice del catálogo
        productos_extraidos = extractor.ejecutar(
            nombre_contacto=config['contacto_whatsapp'],
            cantidad_productos=config['productos_por_extraccion'],
            articulo_inicio=articulo_inicio,
            indice_inicio_catalogo=indice_catalogo  # Comenzar desde aquí en el catálogo
        )
        
        # Registrar productos extraídos
        if productos_extraidos:
            print("\n📝 Registrando productos extraídos...")
            for idx, producto in enumerate(productos_extraidos):
                numero_articulo = articulo_inicio + idx
                gestor.registrar_extraccion(
                    articulo=numero_articulo,
                    titulo=producto.get('titulo', 'Sin título'),
                    precio=producto.get('precio', '0'),
                    descripcion=producto.get('descripcion', '')
                )
            
            # Actualizar índice del catálogo
            gestor.actualizar_indice_catalogo(len(productos_extraidos))
            
            print(f"\n✅ Se extrajeron {len(productos_extraidos)} productos del catálogo")
            print(f"   Nuevo índice del catálogo: {gestor.obtener_indice_catalogo()}")
        
        # Mostrar estadísticas
        gestor.mostrar_estadisticas()
        
        print("\n" + "="*60)
        print("✅ EXTRACCIÓN COMPLETADA")
        print("="*60)
        
        # Sugerir siguiente paso
        if config['auto_publicar']:
            print("\n💡 Siguiente paso:")
            print("   La publicación automática está activada.")
            print("   Ejecuta '0_Ejecutar_Todo.bat' para publicar automáticamente")
        else:
            print("\n💡 Siguiente paso:")
            print("   Ejecuta '3_Publicar_Marketplace.bat' para publicar manualmente")
        
    except Exception as e:
        print(f"\n❌ Error durante la extracción: {e}")
        import traceback
        traceback.print_exc()
    
    print()


if __name__ == "__main__":
    main()
