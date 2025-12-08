import os
import re
import configparser
from compartido.gestor_archivos import contar_articulos


class ConfiguradorInteractivo:
    """Configurador interactivo con validaciones para config_global.txt"""
    
    def __init__(self):
        self.archivo_config = "config_global.txt"
        self.config = configparser.ConfigParser()
        self.cambios_realizados = False
        
        # Valores por defecto
        self.defaults = {
            'GENERAL': {
                'cantidad_productos': '5',
                'modo': 'completo'
            },
            'EXTRACCION': {
                'contacto_whatsapp': 'Trabajo John',
                'auto_scroll': '5',
                'productos_por_extraccion': '5'
            },
            'PUBLICACION': {
                'auto_publicar': 'si',
                'tiempo_entre_publicaciones': '10',
                'max_publicaciones_por_dia': '20',
                'publicar_todos': 'si'
            },
            'SEGURIDAD': {
                'confirmacion_borrado': 'si',
                'backup_antes_borrar': 'si'
            }
        }
    
    def limpiar_pantalla(self):
        """Limpia la consola"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def mostrar_header(self):
        """Muestra el encabezado"""
        print("=" * 70)
        print(" " * 15 + "🎛️  CONFIGURADOR DEL SISTEMA")
        print("=" * 70)
        print()
    
    def cargar_config(self):
        """Carga la configuración actual o crea una nueva"""
        if os.path.exists(self.archivo_config):
            self.config.read(self.archivo_config, encoding='utf-8')
            print("✅ Configuración cargada desde config_global.txt\n")
        else:
            print("⚠️  No existe config_global.txt. Creando configuración por defecto...\n")
            self.crear_config_defecto()
    
    def crear_config_defecto(self):
        """Crea configuración por defecto"""
        for seccion, valores in self.defaults.items():
            self.config[seccion] = valores
        self.guardar_config()
    
    def guardar_config(self):
        """Guarda la configuración en el archivo"""
        with open(self.archivo_config, 'w', encoding='utf-8') as f:
            # Escribir encabezado
            f.write("# ============================================================\n")
            f.write("# CONFIGURACIÓN GLOBAL DEL SISTEMA\n")
            f.write("# ============================================================\n\n")
            self.config.write(f)
        print("\n💾 Configuración guardada exitosamente en config_global.txt")
    
    def mostrar_config_actual(self):
        """Muestra la configuración actual"""
        print("\n📋 CONFIGURACIÓN ACTUAL:\n")
        
        for seccion in self.config.sections():
            print(f"[{seccion}]")
            for clave, valor in self.config[seccion].items():
                print(f"  {clave} = {valor}")
            print()
    
    def validar_numero_positivo(self, valor, min_val=1, max_val=None):
        """Valida que sea un número positivo"""
        try:
            num = int(valor)
            if num < min_val:
                return False, f"❌ El valor debe ser mayor o igual a {min_val}"
            if max_val and num > max_val:
                return False, f"❌ El valor no puede ser mayor a {max_val}"
            return True, num
        except ValueError:
            return False, "❌ Debe ser un número válido"
    
    def validar_si_no(self, valor):
        """Valida que sea 'si' o 'no'"""
        valor_lower = valor.lower().strip()
        if valor_lower in ['si', 'sí', 's', 'yes', 'y']:
            return True, 'si'
        elif valor_lower in ['no', 'n']:
            return True, 'no'
        else:
            return False, "❌ Debe ser 'si' o 'no'"
    
    def validar_modo(self, valor):
        """Valida que sea un modo válido"""
        modos_validos = ['completo', 'solo_extraer', 'solo_publicar']
        valor_lower = valor.lower().strip()
        if valor_lower in modos_validos:
            return True, valor_lower
        else:
            return False, f"❌ Debe ser uno de: {', '.join(modos_validos)}"
    
    def validar_contacto(self, valor):
        """Valida el nombre del contacto"""
        if len(valor.strip()) < 3:
            return False, "❌ El nombre debe tener al menos 3 caracteres"
        if len(valor.strip()) > 50:
            return False, "❌ El nombre no puede exceder 50 caracteres"
        return True, valor.strip()
    
    def menu_principal(self):
        """Muestra el menú principal"""
        while True:
            self.limpiar_pantalla()
            self.mostrar_header()
            self.mostrar_config_actual()
            
            print("=" * 70)
            print("\n🔧 OPCIONES DE CONFIGURACIÓN:\n")
            print("  1. ⚙️  Configuración General")
            print("  2. 📱 Configuración de Extracción (WhatsApp)")
            print("  3. 🚀 Configuración de Publicación (Marketplace)")
            print("  4. 🔒 Configuración de Seguridad")
            print("  5. 📄 Ver configuración completa")
            print("  6. 💾 Guardar y salir")
            print("  7. ❌ Salir sin guardar")
            print("\n" + "=" * 70)
            
            opcion = input("\n👉 Selecciona una opción (1-7): ").strip()
            
            if opcion == '1':
                self.menu_general()
            elif opcion == '2':
                self.menu_extraccion()
            elif opcion == '3':
                self.menu_publicacion()
            elif opcion == '4':
                self.menu_seguridad()
            elif opcion == '5':
                input("\nPresiona Enter para continuar...")
            elif opcion == '6':
                if self.cambios_realizados:
                    self.guardar_config()
                    print("\n✅ Configuración guardada. Cambios aplicados.")
                else:
                    print("\n✅ No hay cambios para guardar.")
                input("\nPresiona Enter para salir...")
                break
            elif opcion == '7':
                if self.cambios_realizados:
                    confirmar = input("\n⚠️  Hay cambios sin guardar. ¿Salir de todos modos? (si/no): ")
                    if confirmar.lower() in ['si', 'sí', 's']:
                        print("\n❌ Cambios descartados.")
                        break
                else:
                    break
            else:
                print("\n❌ Opción inválida")
                input("Presiona Enter para continuar...")
    
    def menu_general(self):
        """Menú de configuración general"""
        self.limpiar_pantalla()
        self.mostrar_header()
        print("⚙️  CONFIGURACIÓN GENERAL\n")
        
        # Cantidad de productos
        print("📦 Cantidad de productos (carpetas Articulo_X)")
        carpetas_actuales = contar_articulos()
        print(f"   Actual: {self.config['GENERAL']['cantidad_productos']}")
        if carpetas_actuales > 0:
            print(f"   ℹ️  Carpetas existentes: {carpetas_actuales}")
        
        nuevo_valor = input("   Nuevo valor (Enter para mantener): ").strip()
        if nuevo_valor:
            valido, resultado = self.validar_numero_positivo(nuevo_valor, min_val=1, max_val=50)
            if valido:
                if carpetas_actuales > 0 and resultado < carpetas_actuales:
                    print(f"\n   ⚠️  ADVERTENCIA: Reducirás de {carpetas_actuales} a {resultado} carpetas")
                    print(f"   Se eliminarán las carpetas Articulo_{resultado+1} en adelante")
                    confirmar = input("   ¿Continuar? (si/no): ")
                    if confirmar.lower() in ['si', 'sí', 's']:
                        self.config['GENERAL']['cantidad_productos'] = str(resultado)
                        self.cambios_realizados = True
                        print("   ✅ Cambiado")
                    else:
                        print("   ❌ Cancelado")
                else:
                    self.config['GENERAL']['cantidad_productos'] = str(resultado)
                    self.cambios_realizados = True
                    print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")
        
        # Modo de operación
        print("\n🎯 Modo de operación")
        print("   Actual:", self.config['GENERAL']['modo'])
        print("   Opciones: completo | solo_extraer | solo_publicar")
        nuevo_valor = input("   Nuevo valor (Enter para mantener): ").strip()
        if nuevo_valor:
            valido, resultado = self.validar_modo(nuevo_valor)
            if valido:
                self.config['GENERAL']['modo'] = resultado
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")
        
        input("\n✅ Presiona Enter para volver al menú principal...")
    
    def menu_extraccion(self):
        """Menú de configuración de extracción"""
        self.limpiar_pantalla()
        self.mostrar_header()
        print("📱 CONFIGURACIÓN DE EXTRACCIÓN (WhatsApp)\n")
        
        # Contacto de WhatsApp
        print("👤 Nombre del contacto en WhatsApp")
        print(f"   Actual: {self.config['EXTRACCION']['contacto_whatsapp']}")
        nuevo_valor = input("   Nuevo valor (Enter para mantener): ").strip()
        if nuevo_valor:
            valido, resultado = self.validar_contacto(nuevo_valor)
            if valido:
                self.config['EXTRACCION']['contacto_whatsapp'] = resultado
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")
        
        # Auto scroll
        print("\n📜 Auto scroll (veces que hace scroll en catálogo)")
        print(f"   Actual: {self.config['EXTRACCION']['auto_scroll']}")
        nuevo_valor = input("   Nuevo valor (Enter para mantener): ").strip()
        if nuevo_valor:
            valido, resultado = self.validar_numero_positivo(nuevo_valor, min_val=1, max_val=20)
            if valido:
                self.config['EXTRACCION']['auto_scroll'] = str(resultado)
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")
        
        # Productos por extracción
        print("\n📦 Productos por extracción")
        print(f"   Actual: {self.config['EXTRACCION']['productos_por_extraccion']}")
        cantidad_max = int(self.config['GENERAL']['cantidad_productos'])
        print(f"   ℹ️  Máximo recomendado: {cantidad_max} (según cantidad_productos)")
        nuevo_valor = input("   Nuevo valor (Enter para mantener): ").strip()
        if nuevo_valor:
            valido, resultado = self.validar_numero_positivo(nuevo_valor, min_val=1, max_val=50)
            if valido:
                if resultado > cantidad_max:
                    print(f"\n   ⚠️  ADVERTENCIA: Extraerás {resultado} productos pero solo hay {cantidad_max} carpetas")
                    print(f"   Se sobrescribirán productos existentes")
                    confirmar = input("   ¿Continuar? (si/no): ")
                    if confirmar.lower() in ['si', 'sí', 's']:
                        self.config['EXTRACCION']['productos_por_extraccion'] = str(resultado)
                        self.cambios_realizados = True
                        print("   ✅ Cambiado")
                    else:
                        print("   ❌ Cancelado")
                else:
                    self.config['EXTRACCION']['productos_por_extraccion'] = str(resultado)
                    self.cambios_realizados = True
                    print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")
        
        input("\n✅ Presiona Enter para volver al menú principal...")
    
    def menu_publicacion(self):
        """Menú de configuración de publicación"""
        self.limpiar_pantalla()
        self.mostrar_header()
        print("🚀 CONFIGURACIÓN DE PUBLICACIÓN (Marketplace)\n")
        
        # Auto publicar
        print("🤖 Publicar automáticamente después de extraer")
        print(f"   Actual: {self.config['PUBLICACION']['auto_publicar']}")
        nuevo_valor = input("   Nuevo valor (si/no, Enter para mantener): ").strip()
        if nuevo_valor:
            valido, resultado = self.validar_si_no(nuevo_valor)
            if valido:
                self.config['PUBLICACION']['auto_publicar'] = resultado
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")
        
        # Tiempo entre publicaciones
        print("\n⏱️  Tiempo entre publicaciones (segundos)")
        print(f"   Actual: {self.config['PUBLICACION']['tiempo_entre_publicaciones']}")
        print("   ℹ️  Recomendado: 10-30 segundos (evitar detección de spam)")
        nuevo_valor = input("   Nuevo valor (Enter para mantener): ").strip()
        if nuevo_valor:
            valido, resultado = self.validar_numero_positivo(nuevo_valor, min_val=5, max_val=300)
            if valido:
                if resultado < 10:
                    print("\n   ⚠️  ADVERTENCIA: Menos de 10 segundos puede causar detección de spam")
                    confirmar = input("   ¿Continuar de todos modos? (si/no): ")
                    if confirmar.lower() in ['si', 'sí', 's']:
                        self.config['PUBLICACION']['tiempo_entre_publicaciones'] = str(resultado)
                        self.cambios_realizados = True
                        print("   ✅ Cambiado")
                    else:
                        print("   ❌ Cancelado")
                else:
                    self.config['PUBLICACION']['tiempo_entre_publicaciones'] = str(resultado)
                    self.cambios_realizados = True
                    print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")
        
        # Máximo por día
        print("\n📊 Máximo de publicaciones por día")
        print(f"   Actual: {self.config['PUBLICACION']['max_publicaciones_por_dia']}")
        print("   ℹ️  Recomendado: 10-30 (evitar bloqueo de Facebook)")
        nuevo_valor = input("   Nuevo valor (Enter para mantener): ").strip()
        if nuevo_valor:
            valido, resultado = self.validar_numero_positivo(nuevo_valor, min_val=1, max_val=100)
            if valido:
                if resultado > 50:
                    print("\n   ⚠️  ADVERTENCIA: Más de 50 publicaciones diarias puede causar bloqueo")
                    confirmar = input("   ¿Continuar de todos modos? (si/no): ")
                    if confirmar.lower() in ['si', 'sí', 's']:
                        self.config['PUBLICACION']['max_publicaciones_por_dia'] = str(resultado)
                        self.cambios_realizados = True
                        print("   ✅ Cambiado")
                    else:
                        print("   ❌ Cancelado")
                else:
                    self.config['PUBLICACION']['max_publicaciones_por_dia'] = str(resultado)
                    self.cambios_realizados = True
                    print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")
        
        # Publicar todos
        print("\n📤 Publicar todos los productos disponibles")
        print(f"   Actual: {self.config['PUBLICACION']['publicar_todos']}")
        print("   si = Publica todos | no = Solo publica el siguiente")
        nuevo_valor = input("   Nuevo valor (si/no, Enter para mantener): ").strip()
        if nuevo_valor:
            valido, resultado = self.validar_si_no(nuevo_valor)
            if valido:
                self.config['PUBLICACION']['publicar_todos'] = resultado
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")
        
        input("\n✅ Presiona Enter para volver al menú principal...")
    
    def menu_seguridad(self):
        """Menú de configuración de seguridad"""
        self.limpiar_pantalla()
        self.mostrar_header()
        print("🔒 CONFIGURACIÓN DE SEGURIDAD\n")
        
        # Confirmación de borrado
        print("⏱️  Confirmación antes de borrar carpetas")
        print(f"   Actual: {self.config['SEGURIDAD']['confirmacion_borrado']}")
        print("   si = Countdown de 5-10 segundos | no = Borra inmediatamente")
        nuevo_valor = input("   Nuevo valor (si/no, Enter para mantener): ").strip()
        if nuevo_valor:
            valido, resultado = self.validar_si_no(nuevo_valor)
            if valido:
                self.config['SEGURIDAD']['confirmacion_borrado'] = resultado
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")
        
        # Backup antes de borrar
        print("\n💾 Crear backup antes de borrar carpetas")
        print(f"   Actual: {self.config['SEGURIDAD']['backup_antes_borrar']}")
        print("   si = Guarda backup en carpeta 'backups/' | no = Borra directo")
        nuevo_valor = input("   Nuevo valor (si/no, Enter para mantener): ").strip()
        if nuevo_valor:
            valido, resultado = self.validar_si_no(nuevo_valor)
            if valido:
                self.config['SEGURIDAD']['backup_antes_borrar'] = resultado
                self.cambios_realizados = True
                print("   ✅ Cambiado")
            else:
                print(f"   {resultado}")
        
        input("\n✅ Presiona Enter para volver al menú principal...")
    
    def ejecutar(self):
        """Ejecuta el configurador"""
        try:
            self.cargar_config()
            self.menu_principal()
        except KeyboardInterrupt:
            print("\n\n❌ Configuración cancelada por el usuario")
        except Exception as e:
            print(f"\n❌ Error: {e}")


def main():
    """Función principal"""
    configurador = ConfiguradorInteractivo()
    configurador.ejecutar()


if __name__ == "__main__":
    main()
