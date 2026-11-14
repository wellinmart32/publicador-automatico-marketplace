"""
Seguimiento de los avisos por WhatsApp (fase 4f).

Guarda en conversaciones_marketplace.json (junto al programa) los avisos que hay que mandar por WhatsApp y si ya
se enviaron. Sirve para dos cosas:
  - si WhatsApp falla, el aviso queda pendiente y se reintenta en la siguiente ejecución;
  - el mismo aviso nunca se manda dos veces.

El estado de cada conversación NO se guarda aquí: se reconstruye siempre leyendo el chat de Facebook.
Cada aviso se identifica por  'Nombre · Producto' + número de ciclo + tipo, porque una conversación se puede
reiniciar (el cliente vuelve a escribir después de la despedida) y entonces es un caso nuevo.
"""

import json
import os
from datetime import datetime, timedelta

NOMBRE_ARCHIVO = 'conversaciones_marketplace.json'
MAX_INTENTOS = 10          # después de tantos intentos fallidos el aviso deja de reintentarse
DIAS_CONSERVAR_ENVIADOS = 60


def _ruta_por_defecto():
    from compartido.gestor_archivos import _base_dir
    return os.path.join(_base_dir(), NOMBRE_ARCHIVO)


class SeguimientoInteresados:

    def __init__(self, ruta=None):
        self.ruta = ruta or _ruta_por_defecto()
        self.avisos = self._leer()
        self._limpiar_antiguos()

    # ------------------------------------------------------------

    def _leer(self):
        if not os.path.exists(self.ruta):
            return {}
        try:
            with open(self.ruta, 'r', encoding='utf-8') as f:
                avisos = json.load(f).get('avisos', {})
            return avisos if isinstance(avisos, dict) else {}
        except Exception as e:
            copia = self.ruta + '.corrupto'
            try:
                os.replace(self.ruta, copia)
            except Exception:
                copia = '(no se pudo copiar)'
            print(f"⚠️  No se pudo leer {NOMBRE_ARCHIVO} ({e}). Se empieza uno nuevo; el anterior quedó en {copia}")
            return {}

    def _guardar(self):
        """Escribe a un archivo temporal y lo reemplaza, para no dejar el JSON a medias si se corta el programa"""
        try:
            temporal = self.ruta + '.tmp'
            with open(temporal, 'w', encoding='utf-8') as f:
                json.dump({'version': 1, 'avisos': self.avisos}, f, indent=2, ensure_ascii=False)
            os.replace(temporal, self.ruta)
            return True
        except Exception as e:
            print(f"⚠️  No se pudo guardar {NOMBRE_ARCHIVO}: {e}")
            return False

    def _limpiar_antiguos(self):
        limite = datetime.now() - timedelta(days=DIAS_CONSERVAR_ENVIADOS)
        borrar = []
        for clave, aviso in self.avisos.items():
            if aviso.get('estado') != 'enviado':
                continue
            try:
                if datetime.fromisoformat(aviso.get('enviado_en', '')) < limite:
                    borrar.append(clave)
            except ValueError:
                pass
        if borrar:
            for clave in borrar:
                del self.avisos[clave]
            self._guardar()

    # ------------------------------------------------------------

    @staticmethod
    def clave(chat, ciclo, tipo):
        return f"{chat['titulo']}#{ciclo}#{tipo}"

    def existe(self, chat, ciclo, tipo):
        return self.clave(chat, ciclo, tipo) in self.avisos

    def registrar(self, chat, ciclo, tipo, texto):
        """Anota un aviso pendiente. Devuelve False si ya estaba anotado (pendiente o enviado)."""
        clave = self.clave(chat, ciclo, tipo)
        if clave in self.avisos:
            return False
        self.avisos[clave] = {
            'tipo': tipo, 'titulo': chat['titulo'], 'ciclo': ciclo, 'texto': texto,
            'estado': 'pendiente', 'intentos': 0, 'creado_en': datetime.now().isoformat(timespec='seconds'),
        }
        self._guardar()
        return True

    def pendientes(self):
        """[(clave, aviso)] de los avisos que faltan por enviar y aún se pueden reintentar"""
        return [(c, a) for c, a in self.avisos.items()
                if a.get('estado') == 'pendiente' and a.get('intentos', 0) < MAX_INTENTOS]

    def abandonados(self):
        """Avisos que fallaron MAX_INTENTOS veces y ya no se reintentan"""
        return [(c, a) for c, a in self.avisos.items()
                if a.get('estado') == 'pendiente' and a.get('intentos', 0) >= MAX_INTENTOS]

    def marcar_enviado(self, clave):
        if clave in self.avisos:
            self.avisos[clave]['estado'] = 'enviado'
            self.avisos[clave]['enviado_en'] = datetime.now().isoformat(timespec='seconds')
            self._guardar()

    def marcar_fallo(self, clave):
        if clave in self.avisos:
            self.avisos[clave]['intentos'] = self.avisos[clave].get('intentos', 0) + 1
            self._guardar()
