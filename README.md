# 🚀 Publicador Automático para Facebook Marketplace

Sistema modular completo para gestionar y publicar productos en Facebook Marketplace, con extracción automática de catálogos de WhatsApp Business.

## 📋 Características

- ✅ **Creación automática de estructura de carpetas** para organizar productos
- ✅ **Extracción de productos desde WhatsApp Business** (catálogos)
- ✅ **Publicación automática en Facebook Marketplace**
- ✅ **Gestión de imágenes** (hasta 10 por producto)
- ✅ **Rotación automática** de productos
- ✅ **Compatible con Git** (carpetas vacías con .gitkeep)

---

## 🗂️ Estructura del Proyecto
```
publicador-automatico-marketplace/
├── compartido/              # Funciones compartidas
│   └── gestor_archivos.py
├── extractores/             # Extracción de catálogos
│   └── extractor_whatsapp.py
├── publicadores/            # Publicación en plataformas
│   └── publicador_marketplace.py
├── ArticulosMarketplace/    # Datos de productos
│   ├── config.txt
│   ├── Articulo_1/
│   │   ├── imagenes/
│   │   └── datos.txt
│   └── Articulo_2/
├── crear_estructura.py
├── extraer_catalogo.py
├── automatizador_marketplace.py
├── 1_Crear_Estructura.bat
├── 2_Extraer_Catalogo.bat
└── 3_Publicar_Marketplace.bat
```

---

## 🔧 Instalación

### 1. Clonar el repositorio
```bash
git clone <tu-repositorio>
cd publicador-automatico-marketplace
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Requisitos adicionales

- **Python 3.8+**
- **Google Chrome** instalado
- **ChromeDriver** (se descarga automáticamente)

---

## 🎯 Flujo de Trabajo

### **MÓDULO 1: Crear Estructura de Carpetas**

Crea la estructura base para organizar tus productos.

**Ejecutar:**
```bash
# Opción 1: Doble clic
1_Crear_Estructura.bat

# Opción 2: Comando
python crear_estructura.py
```

**Resultado:**
- Crea 5 carpetas `Articulo_1` a `Articulo_5`
- Cada una con subcarpeta `imagenes/` y archivo `datos.txt`
- Archivos `.gitkeep` para mantener carpetas vacías en Git

---

### **MÓDULO 2: Extraer Catálogo de WhatsApp** ⭐ NUEVO

Extrae productos automáticamente desde un catálogo de WhatsApp Business.

**Ejecutar:**
```bash
# Opción 1: Doble clic
2_Extraer_Catalogo.bat

# Opción 2: Comando
python extraer_catalogo.py
```

**Pasos:**
1. Se abre WhatsApp Web en Chrome
2. Escanea el código QR (primera vez)
3. Ingresa el nombre del contacto (ej: "Trabajo John")
4. Ingresa cantidad de productos a extraer
5. El bot:
   - Navega al catálogo del contacto
   - Extrae título, precio, descripción e imágenes
   - Descarga las imágenes automáticamente
   - Crea los archivos `datos.txt` con la información

**Resultado:**
- Carpetas `Articulo_X` pobladas con imágenes y datos listos para publicar

---

### **MÓDULO 3: Publicar en Marketplace**

Publica automáticamente los productos en Facebook Marketplace.

**Ejecutar:**
```bash
# Opción 1: Doble clic
3_Publicar_Marketplace.bat

# Opción 2: Comando
python automatizador_marketplace.py
```

**Pasos:**
1. Se abre Facebook en Chrome
2. Inicia sesión (primera vez)
3. El bot automáticamente:
   - Sube imágenes
   - Llena título, precio, categoría, estado
   - Agrega descripción
   - Configura etiquetas y SKU
   - Publica el artículo

**Resultado:**
- Producto publicado en Marketplace
- Sistema actualiza `config.txt` para rotar al siguiente producto

---

## 📝 Formato del archivo `datos.txt`

Cada carpeta de artículo debe tener un archivo `datos.txt` con este formato:
```txt
titulo=Teclado Mecánico RGB Gamer
precio=45
categoria=Electrónica e informática
estado=Nuevo
descripcion=Teclado mecánico con iluminación RGB, switches azules, cable desmontable. Perfecto estado.
disponibilidad=Publicar como disponible
encuentro_publico=Si
etiquetas=teclado,rgb,gaming,mecanico
sku=TECL-001
```

### Categorías disponibles:
- Electrónica e informática
- Vehículos
- Ropa y accesorios
- Hogar y jardín
- Artículos para bebés y niños

### Estados disponibles:
- Nuevo
- Usado - Como nuevo
- Usado - En buen estado
- Usado - Aceptable

---

## 🖼️ Imágenes

- Ubicación: `ArticulosMarketplace/Articulo_X/imagenes/`
- Formatos soportados: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`
- Máximo: 10 imágenes por producto
- Se suben en orden alfabético

---

## 🔄 Rotación Automática

El sistema usa `config.txt` para rotar productos automáticamente:
- Después de publicar `Articulo_3`, el siguiente será `Articulo_4`
- Al llegar al último, vuelve a `Articulo_1`
- Puedes seleccionar manualmente durante 7 segundos al ejecutar

---

## 🛠️ Uso Manual vs Automático

### **Opción A: Manual** (sin WhatsApp)
1. Ejecuta `1_Crear_Estructura.bat`
2. Agrega imágenes en `Articulo_X/imagenes/`
3. Edita `datos.txt` con la información del producto
4. Ejecuta `3_Publicar_Marketplace.bat`

### **Opción B: Automático** (con WhatsApp) ⭐
1. Ejecuta `1_Crear_Estructura.bat`
2. Ejecuta `2_Extraer_Catalogo.bat`
3. Ejecuta `3_Publicar_Marketplace.bat`

---

## 🔐 Seguridad

- Los perfiles de Chrome se guardan localmente
- **NO subas** las carpetas `perfil_bot_marketplace/` ni `perfil_whatsapp_extractor/` a Git
- El `.gitignore` ya está configurado para proteger datos sensibles

---

## 📦 Dependencias

- **selenium**: Automatización de navegadores
- **webdriver-manager**: Gestión automática de ChromeDriver
- **requests**: Descarga de imágenes

---

## ❓ Solución de Problemas

### El navegador no se abre
- Verifica que Chrome esté instalado
- Ejecuta: `pip install --upgrade selenium webdriver-manager`

### WhatsApp Web no carga
- Asegúrate de tener buena conexión a internet
- Cierra otras sesiones de WhatsApp Web
- Escanea el código QR cuando aparezca

### No encuentra el contacto en WhatsApp
- Verifica que el nombre sea exacto (ej: "Trabajo John")
- Asegúrate de que el contacto tenga catálogo de productos

### Error al publicar en Marketplace
- Verifica que estés logueado en Facebook
- Revisa que las imágenes existan en la carpeta
- Confirma que el archivo `datos.txt` tenga todos los campos

---

## 📄 Licencia

Este proyecto es de uso personal/comercial.

---

## 🤝 Contribuciones

Desarrollado para automatizar la publicación en Facebook Marketplace con integración de catálogos de WhatsApp Business.

---

## 📞 Soporte

Para problemas o mejoras, revisa la documentación en cada módulo:
- `compartido/gestor_archivos.py` - Gestión de carpetas
- `extractores/extractor_whatsapp.py` - Extracción de WhatsApp
- `publicadores/publicador_marketplace.py` - Publicación en Marketplace
