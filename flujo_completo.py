import subprocess
import sys
from compartido.gestor_archivos import leer_config_global, crear_estructura_carpetas
from gestor_registro import GestorRegistro


def ejecutar_script(script_name, descripcion):
    """Ejecuta un script de Python y maneja errores"""
    print(f"\n{'='*60}")
    print(f"🚀 {descripcion}")
    print(f"{'='*60}\n")
    
    try:
        resultado = subprocess.run(
            [sys.executable, script_name],
            capture_output=False,
            text=True
        )
        
        if resultado.returncode == 0:
            print(f"\n✅ {descripcion} - Completado")
            return True
        else:
            print(f"\n⚠️  {descripcion} - Finalizado con advertencias")
            return False
            
    except Exception as e:
        print(f"\n❌ Error ejecutando {script_name}: {e}")
        return False


def main():
    """Orquestador maestro - Ejecuta el flujo completo"""
    
    print("\n" + "="*60)
    print(" " * 15 + "🎯 FLUJO COMPLETO AUTOMÁTICO")
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
    print("⚙️  CONFIGURACIÓN DEL FLUJO:\n")
    print(f"   📦 Productos: {config['cantidad_productos']}")
    print(f"   🎯 Modo: {config['modo']}")
    print(f"   📱 Contacto: {config['contacto_whatsapp']}")
    print(f"   🚀 Auto publicar: {'Sí' if config['auto_publicar'] else 'No'}")
    print(f"   📅 Límite diario: {config['max_publicaciones_por_dia']}")
    
    # Inicializar gestor
    gestor = GestorRegistro()
    gestor.mostrar_estadisticas()
    
    print("\n" + "="*60)
    print("ESTE PROCESO EJECUTARÁ:")
    print("="*60)
    
    modo = config['modo']
    
    if modo == 'completo':
        print("  1️⃣  Crear/actualizar estructura de carpetas")
        print("  2️⃣  Extraer productos de WhatsApp")
        print("  3️⃣  Publicar automáticamente en Marketplace")
        
    elif modo == 'solo_extraer':
        print("  1️⃣  Crear/actualizar estructura de carpetas")
        print("  2️⃣  Extraer productos de WhatsApp")
        print("  ⏭️   Publicación desactivada")
        
    elif modo == 'solo_publicar':
        print("  1️⃣  Verificar estructura de carpetas")
        print("  2️⃣  Publicar productos existentes en Marketplace")
        print("  ⏭️   Extracción desactivada")
    
    print("="*60 + "\n")
    
    # Confirmación
    input("⏳ Presiona Enter para continuar (o Ctrl+C para cancelar)...")
    
    # FASE 1: Crear/actualizar estructura
    print("\n" + "="*60)
    print("📁 FASE 1: ESTRUCTURA DE CARPETAS")
    print("="*60 + "\n")
    
    try:
        crear_estructura_carpetas()
    except Exception as e:
        print(f"❌ Error creando estructura: {e}")
        input("\nPresiona Enter para salir...")
        return
    
    # FASE 2: Extracción (si aplica)
    if modo in ['completo', 'solo_extraer']:
        print("\n" + "="*60)
        print("📱 FASE 2: EXTRACCIÓN DE WHATSAPP")
        print("="*60 + "\n")
        
        exito_extraccion = ejecutar_script(
            "extraer_catalogo.py",
            "Extracción de WhatsApp"
        )
        
        if not exito_extraccion:
            print("\n⚠️  La extracción tuvo problemas.")
            continuar = input("¿Continuar con la publicación de todos modos? (si/no): ")
            if continuar.lower() not in ['si', 'sí', 's']:
                print("\n❌ Proceso cancelado")
                return
    
    # FASE 3: Publicación (si aplica)
    if modo in ['completo', 'solo_publicar']:
        # Verificar si debe publicar automáticamente
        if modo == 'completo' and not config['auto_publicar']:
            print("\n" + "="*60)
            print("⏭️  PUBLICACIÓN AUTOMÁTICA DESACTIVADA")
            print("="*60)
            print("\n💡 Para publicar, ejecuta '3_Publicar_Marketplace.bat'")
            print("   O activa 'auto_publicar' en '4_Configurador.bat'")
        else:
            print("\n" + "="*60)
            print("🚀 FASE 3: PUBLICACIÓN EN MARKETPLACE")
            print("="*60 + "\n")
            
            # Verificar límite diario
            if not gestor.puede_publicar_hoy(config['max_publicaciones_por_dia']):
                print(f"⚠️  LÍMITE DIARIO ALCANZADO")
                print(f"   Ya publicaste {gestor.registro['publicaciones_hoy']} productos hoy")
                print(f"   Límite: {config['max_publicaciones_por_dia']}")
            else:
                ejecutar_script(
                    "automatizador_marketplace.py",
                    "Publicación en Marketplace"
                )
    
    # RESUMEN FINAL
    print("\n" + "="*60)
    print("✅ FLUJO COMPLETO FINALIZADO")
    print("="*60 + "\n")
    
    # Mostrar estadísticas finales
    gestor_final = GestorRegistro()
    gestor_final.mostrar_estadisticas()
    
    print("💡 Próxima ejecución:")
    print("   • Ejecuta '0_Ejecutar_Todo.bat' para repetir el proceso")
    print("   • Ejecuta '4_Configurador.bat' para cambiar configuración")
    print("   • Los productos se rotan automáticamente\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Proceso cancelado por el usuario\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        input("\nPresiona Enter para salir...")
