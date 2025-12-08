from compartido.gestor_archivos import crear_estructura_carpetas, leer_config_global


def main():
    """Script para crear/actualizar la estructura de carpetas - VERSIÓN INTELIGENTE"""
    
    print("\n" + "="*60)
    print("📁 GESTOR INTELIGENTE DE ESTRUCTURA")
    print("="*60 + "\n")
    
    # Leer configuración
    try:
        config = leer_config_global()
        print(f"⚙️  Configuración cargada:")
        print(f"   Carpetas configuradas: {config['cantidad_productos']}")
        print(f"   Confirmación de borrado: {'Sí' if config['confirmacion_borrado'] else 'No'}")
        print(f"   Backup antes de borrar: {'Sí' if config['backup_antes_borrar'] else 'No'}")
    except Exception as e:
        print(f"⚠️  Error leyendo configuración: {e}")
        print("   Usando valores por defecto...")
    
    print("\n" + "="*60)
    print("Este script hará:")
    print("  ✓ Crear carpetas faltantes")
    print("  ✓ Eliminar carpetas sobrantes (con confirmación)")
    print("  ✓ Crear backup antes de eliminar (si está configurado)")
    print("="*60 + "\n")
    
    # Ejecutar creación/actualización
    crear_estructura_carpetas()
    
    print("\n💡 Siguiente paso:")
    print("   Ejecuta '2_Extraer_Catalogo.bat' para poblar con datos de WhatsApp")
    print("   O llena manualmente las carpetas con imágenes y datos.txt\n")


if __name__ == "__main__":
    main()
