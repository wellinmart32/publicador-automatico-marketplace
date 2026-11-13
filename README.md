# 🛍️ Marketplace Automático

Publica tus productos en **Facebook Marketplace** de forma automática, extrae tu catálogo de **WhatsApp Business** y (próximamente) atiende a los interesados. Parte de la plataforma **AutomaPro**.

Versión 2.0.0 · Windows 10/11 · Python 3.8+ (solo para ejecutar desde el código)

---

## ✨ Qué hace

| Acción | Qué hace |
|---|---|
| ▶️ **Publicar productos** | Publica uno o varios productos por ejecución, en rotación, con reintentos y límites diarios para cuidar tu cuenta |
| 🛍️ **Extraer catálogo** | Copia productos (título, precio, descripción e imágenes) de tu catálogo de WhatsApp Business a las carpetas de productos |
| 💬 **Atender interesados** | Responde a quienes preguntan por tus productos y avisa al vendedor *(llega en una próxima actualización)* |

Funciona con **Firefox, Chrome o Edge**. Cada acción guarda su sesión en `perfiles/` para no volver a iniciar sesión.

---

## 📁 Estructura

```
publicar_marketplace.py     Programa principal (--modulo, --tarea, --secuencia)
panel_control.py            Panel de Control (interfaz principal)
configurador_gui.py         Configurador
gestor_articulos_gui.py     Gestor de Productos
gestor_tareas_gui.py        Gestor de Tareas automáticas
wizard_primera_vez.py       Asistente de primera vez (licencia y configuración)
gestor_licencias.py         Licencias
gestor_registro.py          Registro y estadísticas
compartido/                 Configuración, productos, tareas, navegador, avisos
publicadores/               Publicación en Marketplace
extractores/                Extracción del catálogo de WhatsApp
ArticulosMarketplace/       Tus productos: Articulo_N/datos.txt + imagenes/
```

---

## 🚀 Uso

La forma normal es abrir el **Panel de Control** (`py panel_control.py` o el acceso directo del instalador).
También puedes lanzar cada acción desde los `.bat`:

- `0_Ejecutar_Todo.bat` → secuencia configurada
- `1_Publicar_Marketplace.bat` → publicar
- `2_Extraer_Catalogo.bat` → extraer catálogo
- `3_Atender_Interesados.bat` → atender interesados
- `4_Configurador.bat` → configuración

Desde la línea de comandos:

```bash
py publicar_marketplace.py --modulo publicar
py publicar_marketplace.py --modulo extraer
py publicar_marketplace.py --secuencia
py publicar_marketplace.py --tarea=NombreDeLaTarea
```

---

## 📦 Productos

Cada producto es una carpeta `ArticulosMarketplace/Articulo_N/` con `datos.txt` (título, precio, categoría, estado, ubicación, descripción…) y una subcarpeta `imagenes/` (hasta 10). Un producto está **listo** cuando tiene título, precio y al menos una imagen. Edítalos desde el **Gestor de Productos**.

---

## ⚙️ Límites que cuidan tu cuenta

- Máximo de publicaciones por día (`max_publicaciones_por_dia`)
- Tiempo mínimo entre ejecuciones y entre productos
- Reintentos automáticos por producto

Todo se cambia en el **Configurador**; `config_global.txt` es personal de cada equipo y no se sube a GitHub.

---

## 🗓️ Tareas automáticas

El **Gestor de Tareas** crea tareas del Programador de Windows con las acciones y la cantidad de productos que elijas. Cada ejecución queda anotada en `registro_tareas.log`.

---

## 🧰 Problemas frecuentes

- **El navegador no abre**: cierra el navegador y vuelve a intentar; se reintenta una vez solo.
- **Facebook pide iniciar sesión o verificar**: hazlo en la ventana que se abrió; el programa espera hasta 2–3 minutos.
- **Un producto no se publica**: revisa que tenga ✅ en el Gestor de Productos.
