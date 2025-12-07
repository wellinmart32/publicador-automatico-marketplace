from compartido.gestor_archivos import crear_estructura_carpetas


def main():
    """Script para crear la estructura de carpetas de artículos"""
    
    print("\n" + "="*60)
    print("📁 CREADOR DE ESTRUCTURA DE ARTÍCULOS")
    print("="*60 + "\n")
    
    crear_estructura_carpetas()
    
    print("\n💡 Siguiente paso:")
    print("   Ejecuta '2_Extraer_Catalogo.bat' para poblar con datos de WhatsApp")
    print("   O llena manualmente las carpetas con imágenes y datos.txt\n")


if __name__ == "__main__":
    main()
