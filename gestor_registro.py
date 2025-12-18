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
                    if 'indice_catalogo_whatsapp' not in registro:
                        registro['indice_catalogo_whatsapp'] = 0
                    return registro
            except:
                return self._crear_registro_vacio()
        else:
            return self._crear_registro_vacio()
    
    def _crear_registro_vacio(self):
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
    
    def obtener_indice_catalogo(self):
        """Obtiene el índice actual del catálogo de WhatsApp"""
        return self.registro.get('indice_catalogo_whatsapp', 0)
    
    def obtener_articulos_pendientes(self):
        """Obtiene la lista de artículos pendientes de publicar"""
        return self.registro.get('pendientes', [])
    
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
    
    def mostrar_estadisticas(self):
        """Muestra estadísticas en consola"""
        total_extraidos = sum(1 for e in self.registro['historial'] if e.get('fecha_extraccion'))
        total_publicados = self.registro['total_publicados']
        total_pendientes = len(self.registro['pendientes'])
        indice_catalogo = self.registro.get('indice_catalogo_whatsapp', 0)
        
        print("\n" + "="*50)
        print("📊 ESTADÍSTICAS DEL SISTEMA")
        print("="*50)
        print(f"📦 Total extraídos:      {total_extraidos}")
        print(f"✅ Total publicados:     {total_publicados}")
        print(f"⏳ Pendientes:           {total_pendientes}")
        print(f"📌 Índice catálogo:      Producto {indice_catalogo} del catálogo de WhatsApp")
        print("="*50 + "\n")
    
    def resetear_contador_diario(self):
        """Resetea SOLO el contador de publicaciones diarias"""
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        fecha_ultima = self.registro.get('fecha_ultima_publicacion', '')
        
        # Si es un día diferente, resetear SOLO publicaciones_hoy
        if fecha_ultima and not fecha_ultima.startswith(fecha_actual):
            self.registro['publicaciones_hoy'] = 0
            self.guardar_registro()
    
    def puede_publicar_hoy(self, max_publicaciones_dia):
        """Verifica si se pueden publicar más productos hoy"""
        self.resetear_contador_diario()
        return self.registro['publicaciones_hoy'] < max_publicaciones_dia
    
    def registrar_publicacion_exitosa(self, articulo, titulo):
        """Registra una publicación exitosa"""
        # Actualizar historial
        for entrada in self.registro['historial']:
            if entrada['articulo'] == articulo:
                entrada['fecha_publicacion'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                entrada['estado'] = 'publicado'
                break
        
        # Remover de pendientes
        if articulo in self.registro['pendientes']:
            self.registro['pendientes'].remove(articulo)
        
        # Actualizar contadores
        self.registro['total_publicados'] += 1
        self.registro['publicaciones_hoy'] += 1
        self.registro['ultimo_articulo_publicado'] = articulo
        self.registro['fecha_ultima_publicacion'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.guardar_registro()
    
    def registrar_error(self, articulo, titulo, error):
        """Registra un error durante la publicación"""
        entrada_error = {
            "articulo": articulo,
            "titulo": titulo,
            "error": error,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.registro['errores'].append(entrada_error)
        self.guardar_registro()
