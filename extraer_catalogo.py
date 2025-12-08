from extractores.extractor_whatsapp import ExtractorWhatsApp
from compartido.gestor_archivos import leer_config_global
from gestor_registro import GestorRegistro
import sys
import time


def main():
    """Script para extraer productos del catálogo de WhatsApp - VERSIÓN SIMPLIFICADA"""
    
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
    
    # Mostrar configuración
    print("⚙️  CONFIGURACIÓN AUTOMÁTICA:\n")
    print(f"   📱 Contacto WhatsApp: {config['contacto_whatsapp']}")
    print(f"   📦 Productos a extraer: {config['productos_por_extraccion']}")
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
    
    # Inicializar gestor de registro
    gestor = GestorRegistro()
    
    # Ejecutar extracción
    extractor = ExtractorWhatsApp()
    
    try:
        print("🌐 Iniciando navegador y conectando a WhatsApp Web...")
        productos_extraidos = extractor.ejecutar(
            config['contacto_whatsapp'], 
            config['productos_por_extraccion']
        )
        
        # Registrar productos extraídos
        if productos_extraidos:
            print("\n📝 Registrando productos extraídos...")
            for idx, producto in enumerate(productos_extraidos, 1):
                gestor.registrar_extraccion(
                    articulo=idx,
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
