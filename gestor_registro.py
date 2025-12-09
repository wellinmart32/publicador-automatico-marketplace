import json
import os
from datetime import datetime


class GestorRegistro:
    """Gestiona el registro de publicaciones y el índice del catálogo de WhatsApp"""
    
    def __init__(self, archivo_registro="registro_publicaciones.json"):
        self.archivo_registro = archivo_registro
        self.registro = self.cargar_registro()
    
    def cargar_registro(self):
        """Carga el registro desde el archivo JSON o crea uno nuevo"""
        if os.path.exists(self.archivo_registro):
            try:
                with open(self.archivo_registro, 'r', encoding='utf-8') as f:
                    registro = json.load(f)
                    # Asegurar que exista el campo indice_catalogo_whatsapp
                    if 'indice_catalogo_whatsapp' not in registro:
                        registro['indice_catalogo_whatsapp'] = 0
                    return registro
            except Exception as e:
                print(f"⚠️  Error cargando registro: {e}")
                return self._crear_registro_vacio()
        else:
            print("📝 Creando nuevo registro_publicaciones.json")
            return self._crear_registro_vacio()
    
    def _crear_registro_vacio(self):
        """Crea estructura de registro vacía"""
        return {
            "ultimo_articulo_publicado": 0,
            "total_publicados": 0,
            "historial": [],
            "pendientes": [],
            "errores": [],
            "publicaciones_hoy": 0,
            "fecha_ultima_publicacion": None,
            "ultima_ejecucion": None,
            "indice_catalogo_whatsapp": 0
        }
    
    def guardar_registro(self):
        """Guarda el registro en el archivo JSON"""
        try:
            with open(self.archivo_registro, 'w', encoding='utf-8') as f:
                json.dump(self.registro, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error guardando registro: {e}")
            return False
    
    def obtener_siguiente_articulo(self):
        """Obtiene el número del siguiente artículo a publicar"""
        return self.registro.get('ultimo_articulo_publicado', 0) + 1
    
    def obtener_articulos_pendientes(self):
        """Obtiene la lista de artículos pendientes de publicar"""
        return self.registro.get('pendientes', [])
    
    def obtener_indice_catalogo(self):
        """Obtiene el índice actual del catálogo de WhatsApp"""
        return self.registro.get('indice_catalogo_whatsapp', 0)
    
    def actualizar_indice_catalogo(self, cantidad_extraida):
        """Actualiza el índice del catálogo después de extraer productos"""
        indice_actual = self.registro.get('indice_catalogo_whatsapp', 0)
        nuevo_indice = indice_actual + cantidad_extraida
        self.registro['indice_catalogo_whatsapp'] = nuevo_indice
        self.guardar_registro()
        print(f"📌 Índice del catálogo actualizado: {indice_actual} → {nuevo_indice}")
    
    def registrar_extraccion(self, articulo, titulo, precio, descripcion):
        """Registra un producto extraído de WhatsApp"""
        entrada = {
            "articulo": articulo,
            "titulo": titulo,
            "precio": precio,
            "descripcion": descripcion[:100] + "..." if len(descripcion) > 100 else descripcion,
            "fecha_extraccion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fecha_publicacion": None,
            "estado": "extraido_pendiente",
            "url_marketplace": None
        }
        
        # Actualizar o agregar al historial
        actualizado = False
        for entrada_existente in self.registro['historial']:
            if entrada_existente['articulo'] == articulo:
                entrada_existente.update(entrada)
                actualizado = True
                break
        
        if not actualizado:
            self.registro['historial'].append(entrada)
        
        # Agregar a pendientes si no está
        if articulo not in self.registro['pendientes']:
            self.registro['pendientes'].append(articulo)
        
        self.registro['ultima_ejecucion'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.guardar_registro()
        
        print(f"📝 Registrado: Articulo_{articulo} - {titulo}")
    
    def registrar_publicacion_exitosa(self, articulo, titulo=None, url_marketplace=None):
        """Registra una publicación exitosa en Marketplace"""
        # Actualizar en historial
        for entrada in self.registro['historial']:
            if entrada['articulo'] == articulo and entrada['estado'] == 'extraido_pendiente':
                entrada['fecha_publicacion'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                entrada['estado'] = 'publicado_exitosamente'
                if url_marketplace:
                    entrada['url_marketplace'] = url_marketplace
                if titulo:
                    entrada['titulo'] = titulo
                break
        else:
            # Si no existe en historial, crear entrada
            entrada = {
                "articulo": articulo,
                "titulo": titulo or f"Articulo_{articulo}",
                "precio": "N/A",
                "descripcion": "Publicado sin extracción previa",
                "fecha_extraccion": None,
                "fecha_publicacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "estado": "publicado_exitosamente",
                "url_marketplace": url_marketplace
            }
            self.registro['historial'].append(entrada)
        
        # Quitar de pendientes
        if articulo in self.registro['pendientes']:
            self.registro['pendientes'].remove(articulo)
        
        # Actualizar contadores
        self.registro['ultimo_articulo_publicado'] = articulo
        self.registro['total_publicados'] += 1
        self.registro['publicaciones_hoy'] += 1
        self.registro['fecha_ultima_publicacion'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.registro['ultima_ejecucion'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.guardar_registro()
        
        print(f"✅ Publicación registrada: Articulo_{articulo}")
    
    def registrar_error(self, articulo, titulo, error):
        """Registra un error durante la publicación"""
        entrada_error = {
            "articulo": articulo,
            "titulo": titulo,
            "error": str(error),
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.registro['errores'].append(entrada_error)
        
        # Actualizar estado en historial
        for entrada in self.registro['historial']:
            if entrada['articulo'] == articulo:
                entrada['estado'] = 'error_publicacion'
                break
        
        self.guardar_registro()
        
        print(f"❌ Error registrado: Articulo_{articulo} - {error}")
    
    def resetear_contador_diario(self):
        """Resetea SOLO el contador de publicaciones diarias (NO todo el registro)"""
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        fecha_ultima = self.registro.get('fecha_ultima_publicacion', '')
        
        # Si es un día diferente, resetear SOLO publicaciones_hoy
        if fecha_ultima and not fecha_ultima.startswith(fecha_actual):
            self.registro['publicaciones_hoy'] = 0
            self.guardar_registro()
            print("🔄 Contador diario reseteado")
    
    def puede_publicar_hoy(self, max_publicaciones_dia):
        """Verifica si se pueden publicar más productos hoy"""
        self.resetear_contador_diario()
        return self.registro['publicaciones_hoy'] < max_publicaciones_dia
    
    def obtener_estadisticas(self):
        """Obtiene estadísticas del registro"""
        total_extraidos = sum(1 for e in self.registro['historial'] if e.get('fecha_extraccion'))
        total_publicados = self.registro['total_publicados']
        total_pendientes = len(self.registro['pendientes'])
        total_errores = len(self.registro['errores'])
        indice_catalogo = self.registro.get('indice_catalogo_whatsapp', 0)
        
        return {
            'total_extraidos': total_extraidos,
            'total_publicados': total_publicados,
            'total_pendientes': total_pendientes,
            'total_errores': total_errores,
            'publicaciones_hoy': self.registro['publicaciones_hoy'],
            'ultimo_publicado': self.registro['ultimo_articulo_publicado'],
            'indice_catalogo': indice_catalogo
        }
    
    def mostrar_estadisticas(self):
        """Muestra estadísticas en consola"""
        stats = self.obtener_estadisticas()
        
        print("\n" + "="*50)
        print("📊 ESTADÍSTICAS DEL SISTEMA")
        print("="*50)
        print(f"📦 Total extraídos:      {stats['total_extraidos']}")
        print(f"✅ Total publicados:     {stats['total_publicados']}")
        print(f"⏳ Pendientes:           {stats['total_pendientes']}")
        print(f"❌ Errores:              {stats['total_errores']}")
        print(f"📅 Publicados hoy:       {stats['publicaciones_hoy']}")
        print(f"🔢 Último publicado:     Articulo_{stats['ultimo_publicado']}")
        print(f"📌 Índice catálogo:      Producto {stats['indice_catalogo']} del catálogo de WhatsApp")
        print("="*50 + "\n")
    
    def limpiar_registro(self):
        """Limpia el registro (usar con precaución)"""
        confirmacion = input("⚠️  ¿Seguro que quieres limpiar TODO el registro? (escribe 'CONFIRMAR'): ")
        if confirmacion == 'CONFIRMAR':
            self.registro = self._crear_registro_vacio()
            self.guardar_registro()
            print("🗑️  Registro limpiado completamente")
        else:
            print("❌ Limpieza cancelada")
    
    def exportar_historial_csv(self, archivo_salida="historial_publicaciones.csv"):
        """Exporta el historial a CSV para análisis"""
        try:
            import csv
            
            with open(archivo_salida, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Articulo', 'Titulo', 'Precio', 'Fecha Extraccion', 
                                'Fecha Publicacion', 'Estado', 'URL Marketplace'])
                
                for entrada in self.registro['historial']:
                    writer.writerow([
                        entrada.get('articulo', ''),
                        entrada.get('titulo', ''),
                        entrada.get('precio', ''),
                        entrada.get('fecha_extraccion', ''),
                        entrada.get('fecha_publicacion', ''),
                        entrada.get('estado', ''),
                        entrada.get('url_marketplace', '')
                    ])
            
            print(f"📄 Historial exportado a: {archivo_salida}")
            return True
        except Exception as e:
            print(f"❌ Error exportando: {e}")
            return False


def main():
    """Función de prueba"""
    print("🧪 Probando GestorRegistro...\n")
    
    gestor = GestorRegistro()
    
    # Mostrar estadísticas
    gestor.mostrar_estadisticas()
    
    # Ejemplo de uso
    print("Ejemplo de uso:")
    print("gestor.registrar_extraccion(1, 'Teclado RGB', '45.00', 'Descripcion...')")
    print("gestor.registrar_publicacion_exitosa(1)")
    print("gestor.actualizar_indice_catalogo(5)  # Después de extraer 5 productos")


if __name__ == "__main__":
    main()
