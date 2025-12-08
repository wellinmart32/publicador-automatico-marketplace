from compartido.gestor_archivos import crear_estructura_carpetas
import time
import sys


def main():
    """Script para crear la estructura de carpetas de artículos - CON CONTADOR"""
    
    print("\n" + "="*60)
    print("📁 CREADOR DE ESTRUCTURA DE ARTÍCULOS")
    print("="*60 + "\n")
    
    print("⏳ Iniciando creación en 3 segundos...")
    print("   (Presiona Ctrl+C para cancelar)\n")
    
    try:
        for i in range(3, 0, -1):
            print(f"   {i}...", end='\r')
            sys.stdout.flush()
            time.sleep(1)
        print("   ✅ ¡Creando estructura!\n")
    except KeyboardInterrupt:
        print("\n\n❌ Cancelado por el usuario\n")
        sys.exit(0)
    
    crear_estructura_carpetas()
    
    print("\n💡 Siguiente paso:")
    print("   Ejecuta '2_Extraer_Catalogo.bat' para poblar con datos de WhatsApp")
    print("   O llena manualmente las carpetas con imágenes y datos.txt")
    
    print("\n⏳ Cerrando en 3 segundos...")
    time.sleep(3)


if __name__ == "__main__":
    main()
