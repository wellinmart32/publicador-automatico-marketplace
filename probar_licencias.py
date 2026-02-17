from gestor_licencias import GestorLicencias
from dialogos_licencia import DialogosLicencia


def probar_sistema_licencias():
    """Script de prueba para el sistema de licencias"""
    
    print("\n" + "="*60)
    print(" " * 15 + "🔐 PRUEBA DE LICENCIAS - MARKETPLACE")
    print("="*60 + "\n")
    
    gestor = GestorLicencias("Marketplace")
    
    codigo_guardado = gestor.obtener_codigo_guardado()
    
    if codigo_guardado:
        print(f"📋 Código guardado: {codigo_guardado}\n")
    else:
        print("📋 No hay código guardado\n")
    
    print("Opciones de prueba:")
    print("1. LIC-TRIAL002      - Licencia TRIAL activa (Marketplace)")
    print("2. LIC-DEV-WELLI-002 - Licencia FULL developer")
    print("3. LIC-INVALID       - Licencia inválida")
    print("4. Usar código guardado")
    print("5. Ingresar código personalizado\n")
    
    opcion = input("Selecciona una opción (1-5): ").strip()
    
    if opcion == "1":
        codigo = "LIC-TRIAL002"
    elif opcion == "2":
        codigo = "LIC-DEV-WELLI-002"
    elif opcion == "3":
        codigo = "LIC-INVALID"
    elif opcion == "4":
        if not codigo_guardado:
            print("\n❌ No hay código guardado")
            return
        codigo = codigo_guardado
    elif opcion == "5":
        codigo = input("\nIngresa el código: ").strip()
    else:
        print("\n❌ Opción inválida")
        return
    
    print(f"\n🔍 Verificando: {codigo}")
    print("⏳ Conectando con el backend...\n")
    
    resultado = gestor.verificar_licencia(codigo)
    
    print("="*60)
    print("RESPUESTA DEL BACKEND:")
    print("="*60)
    for clave, valor in resultado.items():
        print(f"  {clave}: {valor}")
    print("="*60 + "\n")
    
    if resultado.get('valida'):
        guardar = input("¿Deseas guardar este código? (s/n): ").strip().lower()
        if guardar == 's':
            if gestor.guardar_codigo_licencia(codigo):
                print("✅ Código guardado correctamente")
            else:
                print("❌ Error al guardar código")
    
    print("\n" + "="*60)
    print("PRUEBA DE FLUJO COMPLETO:")
    print("="*60 + "\n")
    
    estado = gestor.verificar_e_iniciar()
    for clave, valor in estado.items():
        print(f"  {clave}: {valor}")
    
    print("\n✅ Prueba completada")


if __name__ == "__main__":
    try:
        probar_sistema_licencias()
    except KeyboardInterrupt:
        print("\n\n⚠️  Prueba cancelada")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPresiona Enter para salir...")