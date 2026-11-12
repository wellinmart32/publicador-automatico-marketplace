import json
import os
import sys
from datetime import datetime


class GestorRegistro:
    """
    Gestiona el registro de publicaciones en Facebook Marketplace
    Guarda el historial de productos publicados, los errores, el límite diario
    y el índice del catálogo de WhatsApp para la extracción
    """

    def __init__(self, archivo_registro="registro_publicaciones.json"):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        self.archivo_registro = os.path.join(base_dir, archivo_registro)
        self.registro = self.cargar_registro()

    def cargar_registro(self):
        """Carga el registro desde el archivo JSON o crea uno nuevo"""
        if not os.path.exists(self.archivo_registro):
            return self._crear_registro_vacio()

        try:
            with open(self.archivo_registro, 'r', encoding='utf-8') as f:
                registro = json.load(f)
        except Exception as e:
            print(f"⚠️  Error leyendo el registro, se crea uno nuevo: {e}")
            return self._crear_registro_vacio()

        # Registro del formato anterior (antes de la v2.0.0): conservar lo importante
        if 'estadisticas' not in registro:
            registro = self._migrar_formato_anterior(registro)

        # Asegurar que existan todos los campos necesarios
        vacio = self._crear_registro_vacio()
        for campo, valor_default in vacio.items():
            if campo not in registro:
                registro[campo] = valor_default
        for seccion in ('estadisticas', 'catalogo_whatsapp'):
            for campo, valor_default in vacio[seccion].items():
                if campo not in registro[seccion]:
                    registro[seccion][campo] = valor_default

        return registro

    def _migrar_formato_anterior(self, anterior):
        """Convierte el registro de las versiones 1.x al formato nuevo"""
        registro = self._crear_registro_vacio()
        publicados = anterior.get('total_publicados', 0) or 0
        registro['total_publicaciones'] = publicados
        registro['estadisticas']['publicaciones_exitosas'] = publicados
        registro['fecha_ultima_publicacion'] = anterior.get('fecha_ultima_publicacion')
        registro['ultima_ejecucion'] = anterior.get('ultima_ejecucion')
        registro['catalogo_whatsapp']['indice_catalogo'] = anterior.get('indice_catalogo_whatsapp', 0) or 0
        print("🔄 Registro de publicaciones convertido al formato nuevo")
        return registro

    def _crear_registro_vacio(self):
        """Crea estructura de registro vacía"""
        return {
            'total_publicaciones': 0,
            'ultima_ejecucion': None,
            'fecha_ultima_publicacion': None,
            'historial_completo': [],
            'publicaciones_por_dia': {},
            'estadisticas': {
                'publicaciones_exitosas': 0,
                'publicaciones_fallidas': 0,
                'total_intentos': 0,
                'tiempo_promedio_publicacion': 0,
                'producto_mas_publicado': None,
                'contador_productos': {}
            },
            'errores': [],
            'catalogo_whatsapp': {
                'indice_catalogo': 0,
                'total_extraidos': 0,
                'fecha_ultima_extraccion': None,
                'historial_extracciones': []
            }
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

    # ==================== LÍMITES ====================

    def puede_publicar_ahora(self, tiempo_minimo_segundos, permitir_forzar_manual=False):
        """
        Verifica si se puede publicar según el tiempo mínimo configurado

        Returns:
            tuple: (puede_publicar: bool, mensaje: str)
        """
        fecha_ultima = self.registro.get('fecha_ultima_publicacion')

        if not fecha_ultima:
            return True, "Primera publicación"

        try:
            ultima_pub = datetime.strptime(fecha_ultima, "%Y-%m-%d %H:%M:%S")
            diferencia = (datetime.now() - ultima_pub).total_seconds()

            if diferencia < tiempo_minimo_segundos:
                tiempo_restante = int(tiempo_minimo_segundos - diferencia)
                if permitir_forzar_manual:
                    return True, f"⚠️  Última publicación hace {int(diferencia)}s (forzado manual)"
                return False, f"Última publicación hace {int(diferencia)}s. Espera {tiempo_restante}s más"

            return True, f"Última publicación hace {int(diferencia)}s"

        except Exception as e:
            print(f"⚠️  Error verificando tiempo: {e}")
            return True, "Error en verificación, permitiendo publicación"

    def publicaciones_de_hoy(self):
        """Cantidad de productos publicados hoy"""
        hoy = datetime.now().strftime("%Y-%m-%d")
        return self.registro.get('publicaciones_por_dia', {}).get(hoy, 0)

    def puede_publicar_hoy(self, max_publicaciones_dia):
        """
        Verifica el límite diario de publicaciones (evita bloqueos de Facebook)

        Returns:
            tuple: (puede_publicar: bool, mensaje: str)
        """
        hoy = self.publicaciones_de_hoy()
        if hoy >= max_publicaciones_dia:
            return False, f"Ya se publicaron {hoy} productos hoy (límite diario: {max_publicaciones_dia})"
        return True, f"Publicados hoy: {hoy} de {max_publicaciones_dia}"

    # ==================== REGISTRO ====================

    def registrar_publicacion_exitosa(self, articulo, titulo, intentos, tiempo_ejecucion):
        """
        Registra una publicación exitosa

        Args:
            articulo: Carpeta del producto (ej: Articulo_3)
            titulo: Título publicado en Marketplace
            intentos: Número de intentos que tomó
            tiempo_ejecucion: Tiempo total en segundos
        """
        ahora = datetime.now()
        fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")
        dia = ahora.strftime("%Y-%m-%d")

        self.registro['historial_completo'].append({
            'fecha': fecha,
            'articulo': articulo,
            'titulo': titulo,
            'estado': 'exitoso',
            'intentos': intentos,
            'tiempo_ejecucion': tiempo_ejecucion
        })

        self.registro['total_publicaciones'] += 1
        self.registro['fecha_ultima_publicacion'] = fecha
        self.registro['ultima_ejecucion'] = fecha

        # Contador diario (solo se guardan los últimos 30 días)
        por_dia = self.registro.setdefault('publicaciones_por_dia', {})
        por_dia[dia] = por_dia.get(dia, 0) + 1
        for dia_viejo in sorted(por_dia)[:-30]:
            del por_dia[dia_viejo]

        stats = self.registro['estadisticas']
        stats['publicaciones_exitosas'] += 1
        stats['total_intentos'] += intentos

        total_pubs = stats['publicaciones_exitosas']
        tiempo_actual = stats.get('tiempo_promedio_publicacion', 0)
        stats['tiempo_promedio_publicacion'] = round(((tiempo_actual * (total_pubs - 1)) + tiempo_ejecucion) / total_pubs, 2)

        contador = stats.get('contador_productos', {})
        contador[titulo] = contador.get(titulo, 0) + 1
        stats['contador_productos'] = contador
        stats['producto_mas_publicado'] = max(contador, key=contador.get)

        self.guardar_registro()
        print(f"✅ Publicación registrada: 🛍️ {articulo} - {titulo}")

    def registrar_error(self, articulo, error, tipo='publicacion'):
        """
        Registra un error

        Args:
            articulo: Carpeta del producto o módulo donde ocurrió
            error: Descripción del error
            tipo: 'publicacion', 'extraccion' o 'atencion'
        """
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.registro['errores'].append({
            'fecha': fecha,
            'articulo': articulo,
            'error': str(error),
            'tipo': tipo
        })
        if tipo == 'publicacion':
            self.registro['estadisticas']['publicaciones_fallidas'] += 1
        self.registro['ultima_ejecucion'] = fecha

        self.guardar_registro()
        print(f"❌ Error registrado: {articulo} - {error}")

    def obtener_indice_catalogo(self):
        """Posición del catálogo de WhatsApp desde donde sigue la próxima extracción"""
        return self.registro['catalogo_whatsapp'].get('indice_catalogo', 0)

    def registrar_extraccion_catalogo(self, cantidad_extraida, nuevo_indice, contacto):
        """
        Registra una extracción del catálogo de WhatsApp Business

        Args:
            cantidad_extraida: Número de productos extraídos
            nuevo_indice: Nueva posición del índice del catálogo
            contacto: Contacto de WhatsApp dueño del catálogo
        """
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        catalogo = self.registro['catalogo_whatsapp']

        catalogo['historial_extracciones'].append({
            'fecha': fecha,
            'contacto': contacto,
            'cantidad_extraida': cantidad_extraida,
            'indice_anterior': catalogo['indice_catalogo'],
            'indice_nuevo': nuevo_indice
        })
        catalogo['indice_catalogo'] = nuevo_indice
        catalogo['total_extraidos'] += cantidad_extraida
        catalogo['fecha_ultima_extraccion'] = fecha
        self.registro['ultima_ejecucion'] = fecha

        self.guardar_registro()
        print(f"✅ Extracción registrada: {cantidad_extraida} producto(s)")
        print(f"   Índice actualizado: {nuevo_indice}")

    # ==================== ESTADÍSTICAS ====================

    def obtener_estadisticas(self):
        """
        Obtiene estadísticas del registro

        Returns:
            dict: Estadísticas completas
        """
        stats = self.registro['estadisticas']
        catalogo = self.registro['catalogo_whatsapp']

        total_exitosas = stats.get('publicaciones_exitosas', 0)
        total_fallidas = stats.get('publicaciones_fallidas', 0)
        total_publicaciones = total_exitosas + total_fallidas
        total_intentos = stats.get('total_intentos', 0)

        return {
            'total_publicaciones': total_publicaciones,
            'publicaciones_exitosas': total_exitosas,
            'publicaciones_fallidas': total_fallidas,
            'publicaciones_hoy': self.publicaciones_de_hoy(),
            'tasa_exito': round((total_exitosas / total_publicaciones * 100), 1) if total_publicaciones > 0 else 0,
            'promedio_intentos': round(total_intentos / total_exitosas, 2) if total_exitosas > 0 else 0,
            'tiempo_promedio': stats.get('tiempo_promedio_publicacion', 0),
            'total_errores': len(self.registro['errores']),
            'producto_mas_publicado': stats.get('producto_mas_publicado'),
            'productos_extraidos': catalogo.get('total_extraidos', 0),
            'ultima_extraccion': catalogo.get('fecha_ultima_extraccion'),
            'ultima_publicacion': self.registro.get('fecha_ultima_publicacion')
        }

    def mostrar_estadisticas(self):
        """Muestra estadísticas en consola de forma visual"""
        stats = self.obtener_estadisticas()

        print("\n" + "=" * 60)
        print(" " * 15 + "📊 ESTADÍSTICAS DEL SISTEMA")
        print("=" * 60)
        print(f"📈 Total publicaciones:        {stats['total_publicaciones']}")
        print(f"✅ Exitosas:                   {stats['publicaciones_exitosas']}")
        print(f"❌ Fallidas:                   {stats['publicaciones_fallidas']}")
        print(f"📅 Publicados hoy:             {stats['publicaciones_hoy']}")
        print(f"🎯 Tasa de éxito:              {stats['tasa_exito']}%")
        print(f"🔄 Promedio de intentos:       {stats['promedio_intentos']}")
        print(f"⏱️  Tiempo promedio:            {stats['tiempo_promedio']}s")
        print(f"🔥 Producto más publicado:     {stats['producto_mas_publicado']}")
        print(f"🛍️  Productos extraídos:        {stats['productos_extraidos']}")

        if stats['ultima_publicacion']:
            print(f"📅 Última publicación:         {stats['ultima_publicacion']}")

        print("=" * 60 + "\n")


def main():
    """Función de prueba del módulo"""
    print("🧪 Probando GestorRegistro...\n")
    gestor = GestorRegistro()
    gestor.mostrar_estadisticas()


if __name__ == "__main__":
    main()
