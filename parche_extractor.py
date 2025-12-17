"""
PARCHE RÁPIDO PARA EXTRACTOR_WHATSAPP.PY
Corrige: título, descripción y agrega marca
"""
import re

print("\n" + "="*70)
print("🔧 APLICANDO CORRECCIONES AL EXTRACTOR")
print("="*70 + "\n")

archivo = "extractores/extractor_whatsapp.py"

try:
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    print("✅ Archivo leído\n")
    
    # ========================================
    # CORRECCIÓN 1: Selector de TÍTULO
    # ========================================
    print("🔧 Corrigiendo selector de título...")
    
    # Buscar y reemplazar el selector actual
    contenido = contenido.replace(
        '"//div[contains(@class, \'x1okw0bk\')]//span[contains(@class, \'selectable-text\')]"',
        '"//span[@dir=\'ltr\' or @dir=\'auto\']"'
    )
    
    print("   ✅ Selector de título actualizado\n")
    
    # ========================================
    # CORRECCIÓN 2: Agregar filtro de marca
    # ========================================
    print("🔧 Agregando extracción de marca...")
    
    # Buscar donde dice "producto = {" y agregar campo marca
    if "'marca':" not in contenido:
        contenido = contenido.replace(
            "producto = {\n                'titulo': '',\n                'precio': '',\n                'descripcion': '',",
            "producto = {\n                'titulo': '',\n                'precio': '',\n                'marca': '',\n                'descripcion': '',"
        )
        print("   ✅ Campo 'marca' agregado al producto\n")
    
    # ========================================
    # CORRECCIÓN 3: Mejorar filtros de descripción
    # ========================================
    print("🔧 Mejorando filtros de descripción...")
    
    # Buscar sección de textos a rechazar y agregar más
    if "textos_rechazar = [" in contenido:
        # Encontrar la posición
        pos_start = contenido.find("textos_rechazar = [")
        pos_end = contenido.find("]", pos_start)
        
        # Reemplazar con lista mejorada
        nuevo_filtro = """textos_rechazar = [
                        # Textos de interfaz de WhatsApp
                        'Buscar una forma',
                        'Tus mensajes personales',
                        'cifrados de extremo',
                        'Acceder a un historial',
                        'No se pudo cargar',
                        'Abre el mensaje',
                        'Haz clic aquí',
                        'Escribe un mensaje',
                        'en tu teléfono',
                        'para actualizar',
                        # Otros
                        producto.get('titulo', ''),  # No repetir el título
                    ]"""
        
        contenido = contenido[:pos_start] + nuevo_filtro + contenido[pos_end+1:]
        print("   ✅ Filtros de descripción mejorados\n")
    
    # ========================================
    # CORRECCIÓN 4: Extraer MARCA (insertar después del precio)
    # ========================================
    print("🔧 Agregando extracción de marca...")
    
    # Buscar donde termina extracción de precio
    marca_codigo = '''
            # Extraer MARCA (si existe)
            try:
                producto['marca'] = ''
                
                # Buscar elementos que contengan "Marca:"
                elementos_marca = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Marca:')]")
                
                for elem in elementos_marca[:5]:
                    try:
                        if elem.is_displayed():
                            texto = elem.text.strip()
                            if 'Marca:' in texto:
                                # Extraer solo el valor después de "Marca:"
                                valor = texto.split('Marca:')[1].split('|')[0].strip()
                                if valor and len(valor) < 50:
                                    producto['marca'] = valor
                                    print(f"   🏷️  Marca encontrada: {valor}")
                                    break
                    except:
                        continue
                
                if not producto['marca']:
                    print(f"   ℹ️  Marca no encontrada (campo opcional)")
            except:
                producto['marca'] = ''
'''
    
    # Insertar después de "# Expandir descripción"
    if "# Expandir descripción" in contenido and "# Extraer MARCA" not in contenido:
        contenido = contenido.replace(
            "# Expandir descripción\n            self.expandir_leer_mas_agresivo()",
            marca_codigo + "\n            # Expandir descripción\n            self.expandir_leer_mas_agresivo()"
        )
        print("   ✅ Extracción de marca implementada\n")
    
    # ========================================
    # CORRECCIÓN 5: Agregar marca a datos.txt
    # ========================================
    print("🔧 Agregando marca a plantilla datos.txt...")
    
    contenido = contenido.replace(
        'plantilla = f"""titulo={producto[\'titulo\']}\nprecio={producto[\'precio\']}\ncategoria=',
        'plantilla = f"""titulo={producto[\'titulo\']}\nprecio={producto[\'precio\']}\nmarca={producto.get(\'marca\', \'\')}\ncategoria='
    )
    
    print("   ✅ Plantilla actualizada con campo marca\n")
    
    # ========================================
    # GUARDAR ARCHIVO
    # ========================================
    with open(archivo, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("="*70)
    print("✅ CORRECCIONES APLICADAS EXITOSAMENTE")
    print("="*70)
    print("\nCambios realizados:")
    print("  ✅ Selector de título mejorado")
    print("  ✅ Campo 'marca' agregado")
    print("  ✅ Extracción de marca implementada")
    print("  ✅ Filtros de descripción mejorados")
    print("  ✅ Plantilla datos.txt actualizada")
    print("\n💡 Ejecuta de nuevo: py 0_Ejecutar_Todo.bat\n")

except FileNotFoundError:
    print(f"❌ No se encontró el archivo: {archivo}")
    print("   Asegúrate de ejecutar este script desde la raíz del proyecto")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
