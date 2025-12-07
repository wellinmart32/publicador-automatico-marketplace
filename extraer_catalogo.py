from extractores.extractor_whatsapp import ExtractorWhatsApp


def main():
    """Script para extraer productos del catálogo de WhatsApp"""
    
    print("\n🔧 CONFIGURACIÓN DE EXTRACCIÓN\n")
    
    # Solicitar nombre del contacto
    nombre_contacto = input("📱 Nombre del contacto de WhatsApp (ej: Trabajo John): ").strip()
    
    if not nombre_contacto:
        print("❌ Debes ingresar un nombre de contacto")
        return
    
    # Solicitar cantidad de productos
    try:
        cantidad = input("📦 ¿Cuántos productos extraer? (por defecto 5): ").strip()
        cantidad_productos = int(cantidad) if cantidad else 5
    except:
        cantidad_productos = 5
    
    print(f"\n✅ Configuración:")
    print(f"   Contacto: {nombre_contacto}")
    print(f"   Productos a extraer: {cantidad_productos}\n")
    
    # Ejecutar extracción
    extractor = ExtractorWhatsApp()
    extractor.ejecutar(nombre_contacto, cantidad_productos)


if __name__ == "__main__":
    main()
