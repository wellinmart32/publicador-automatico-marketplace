from extractores.extractor_whatsapp import ExtractorWhatsApp
import sys


def main():
    """Script RÁPIDO para extraer con valores por defecto"""
    
    print("\n" + "="*60)
    print("⚡ EXTRACCIÓN RÁPIDA DE WHATSAPP")
    print("="*60)
    print("\n💡 Usando valores por defecto:")
    print("   📱 Contacto: Trabajo John")
    print("   📦 Productos: 5")
    print("\n⏳ Iniciando en 5 segundos... (Presiona Ctrl+C para cancelar)")
    
    # Esperar 5 segundos
    try:
        import time
        for i in range(5, 0, -1):
            print(f"   {i}...", end='\r')
            time.sleep(1)
        print("   ✅ ¡Iniciando!\n")
    except KeyboardInterrupt:
        print("\n\n❌ Cancelado por el usuario")
        sys.exit(0)
    
    # Ejecutar extracción
    extractor = ExtractorWhatsApp()
    extractor.ejecutar("Trabajo John", 5)


if __name__ == "__main__":
    main()
