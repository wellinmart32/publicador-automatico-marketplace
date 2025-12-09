from extractores.extractor_whatsapp import ExtractorWhatsApp
from compartido.gestor_archivos import leer_config_global, contar_articulos
from gestor_registro import GestorRegistro
import sys
import time


def main():
    """Script para extraer productos del catálogo de WhatsApp - CON CONTINUACIÓN INTELIGENTE"""
    
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
    
    # Determinar desde qué artículo comenzar - LÓGICA MEJORADA
    articulo_inicio = 1
    total_carpetas = contar_articulos()
    
    if gestor.registro['pendientes']:
        # Si hay pendientes, extraer desde el mínimo pendiente
        articulo_inicio = min(gestor.registro['pendientes'])
        print(f"📦 Hay artículos pendientes, continuando desde Articulo_{articulo_inicio}\n")
        
    elif gestor.registro['ultimo_articulo_publicado'] > 0:
        # Verificar si ya están todos extraídos
        total_extraidos = len(gestor.registro['historial'])
        
        # Si ya se extrajeron productos y no hay pendientes, salir
        if total_extraidos >= total_carpetas and len(gestor.registro['pendientes']) == 0:
            print(f"\n✅ Todos los artículos ya están extraídos y publicados")
            print(f"   Total extraídos: {total_extraidos}")
            print(f"   Total publicados: {gestor.registro['total_publicados']}")
            print(f"\n💡 Para re-extraer productos nuevos:")
            print(f"   1. Ejecuta '1_Crear_Estructura.bat' para limpiar")
            print(f"   2. O aumenta 'cantidad_productos' en '4_Configurador.bat'\n")
            input("Presiona Enter para salir...")
            return
        
        # Continuar desde el siguiente al último publicado
        articulo_inicio = gestor.registro['ultimo_articulo_publicado'] + 1
        
        # Si excede el total, volver a 1 (rotación)
        if articulo_inicio > total_carpetas:
            articulo_inicio = 1
            print(f"🔄 Rotación completada, reiniciando desde Articulo_1\n")
        else:
            print(f"➡️  Continuando desde Articulo_{articulo_inicio}\n")
    else:
        print(f"🆕 Primera extracción, comenzando desde Articulo_1\n")
    
    # Mostrar configuración
    print("⚙️  CONFIGURACIÓN AUTOMÁTICA:\n")
    print(f"   📱 Contacto WhatsApp: {config['contacto_whatsapp']}")
    print(f"   📦 Productos a extraer: {config['productos_por_extraccion']}")
    print(f"   🎯 Artículo inicial: {articulo_inicio}")
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
        productos_extraidos = extractor.ejecutar(
            config['contacto_whatsapp'], 
            config['productos_por_extraccion'],
            articulo_inicio
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
