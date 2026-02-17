import requests
import json
from pathlib import Path


class GestorLicencias:
    """Gestor de licencias para AutomaPro"""
    
    def __init__(self, nombre_app="Marketplace"):
        self.directorio_config = Path.home() / ".config" / "AutomaPro" / nombre_app
        self.archivo_config = self.directorio_config / "config.json"
        self.url_backend = "http://localhost:8080"
        
        self.directorio_config.mkdir(parents=True, exist_ok=True)
    
    def obtener_codigo_guardado(self):
        """Obtener código de licencia guardado localmente"""
        if not self.archivo_config.exists():
            return None
        
        try:
            with open(self.archivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('licencia_codigo')
        except Exception as e:
            print(f"Error leyendo configuración: {e}")
            return None
    
    def guardar_codigo_licencia(self, codigo):
        """Guardar código de licencia localmente"""
        config = {
            'licencia_codigo': codigo,
            'app_id': 'automapro-marketplace',
            'backend_url': self.url_backend
        }
        
        try:
            with open(self.archivo_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error guardando configuración: {e}")
            return False
    
    def verificar_licencia(self, codigo):
        """Verificar licencia contra el backend"""
        try:
            url = f"{self.url_backend}/api/public/verificar-licencia/{codigo}"
            respuesta = requests.get(url, timeout=10)
            
            if respuesta.status_code == 200:
                return respuesta.json()
            else:
                return {"valida": False, "mensaje": "Error al verificar licencia"}
        
        except requests.exceptions.ConnectionError:
            return {"valida": False, "mensaje": "No se pudo conectar con el servidor"}
        except requests.exceptions.Timeout:
            return {"valida": False, "mensaje": "Tiempo de espera agotado"}
        except Exception as e:
            return {"valida": False, "mensaje": f"Error: {str(e)}"}
    
    def verificar_e_iniciar(self):
        """Verificar licencia al iniciar la aplicación"""
        codigo = self.obtener_codigo_guardado()
        
        if not codigo:
            return {
                'necesita_ingreso': True,
                'mensaje': 'Ingresa tu código de licencia'
            }
        
        licencia = self.verificar_licencia(codigo)
        
        if not licencia.get('valida'):
            return {
                'error': True,
                'mensaje': licencia.get('mensaje', 'Licencia inválida')
            }
        
        if licencia.get('tipo') == 'FULL':
            return {
                'tipo': 'FULL',
                'expirado': False,
                'mensaje': 'Licencia completa activada'
            }
        
        if licencia.get('tipo') == 'TRIAL' and licencia.get('expirado'):
            return {
                'tipo': 'TRIAL',
                'expirado': True,
                'codigo': codigo,
                'mensaje': 'Tu período de prueba ha terminado'
            }
        
        if licencia.get('tipo') == 'TRIAL':
            dias = licencia.get('diasRestantes', 0)
            return {
                'tipo': 'TRIAL',
                'expirado': False,
                'dias_restantes': dias,
                'mensaje': f'Quedan {dias} días de prueba'
            }
        
        return {
            'error': True,
            'mensaje': 'Estado de licencia desconocido'
        }