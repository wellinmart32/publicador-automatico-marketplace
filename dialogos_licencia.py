import tkinter as tk
from tkinter import messagebox, simpledialog
import webbrowser


class DialogosLicencia:
    """Diálogos de interfaz para gestión de licencias"""
    
    @staticmethod
    def solicitar_codigo_licencia():
        """Mostrar diálogo para ingresar código de licencia"""
        root = tk.Tk()
        root.withdraw()
        
        codigo = simpledialog.askstring(
            "Código de Licencia",
            "Ingresa tu código de licencia:\n\n(Ejemplo: LIC-TRIAL002)",
            parent=root
        )
        
        root.destroy()
        return codigo
    
    @staticmethod
    def mostrar_trial_expirado(codigo_licencia):
        """Mostrar diálogo cuando expira el trial"""
        root = tk.Tk()
        root.withdraw()
        
        mensaje = (
            "Tu período de prueba ha terminado\n\n"
            "Desbloquea todas las funciones premium ahora\n\n"
            "Precio: $49.99 USD (pago único)\n"
            "✅ Sin suscripciones\n"
            "✅ Actualizaciones gratis\n"
            "✅ Soporte prioritario"
        )
        
        respuesta = messagebox.askquestion(
            "Trial Expirado",
            mensaje,
            icon='warning',
            type='yesno',
            default='yes'
        )
        
        root.destroy()
        
        if respuesta == 'yes':
            url = f"http://localhost:4200/cliente/comprar?codigo={codigo_licencia}&app=2"
            webbrowser.open(url)
        
        return False
    
    @staticmethod
    def mostrar_banner_trial(dias_restantes):
        """Mostrar mensaje de trial activo"""
        print(f"\n{'='*60}")
        print(f"⚠️  MODO TRIAL - Quedan {dias_restantes} días")
        print(f"{'='*60}\n")
    
    @staticmethod
    def mostrar_error(mensaje):
        """Mostrar diálogo de error"""
        root = tk.Tk()
        root.withdraw()
        
        messagebox.showerror("Error de Licencia", mensaje)
        
        root.destroy()
    
    @staticmethod
    def mostrar_exito(mensaje):
        """Mostrar diálogo de éxito"""
        root = tk.Tk()
        root.withdraw()
        
        messagebox.showinfo("Licencia Activada", mensaje)
        
        root.destroy()