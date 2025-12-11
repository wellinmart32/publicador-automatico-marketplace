@echo off
chcp 65001 >nul

REM ============================================================
REM VERIFICAR Y SOLICITAR PERMISOS DE ADMINISTRADOR
REM ============================================================
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

if '%errorlevel%' NEQ '0' (
    echo.
    echo ════════════════════════════════════════════════════════════
    echo   ⚠️  PERMISOS DE ADMINISTRADOR REQUERIDOS
    echo ════════════════════════════════════════════════════════════
    echo.
    echo Este script requiere permisos de administrador.
    echo Solicitando permisos...
    echo.
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )
    pushd "%CD%"
    CD /D "%~dp0"

REM ============================================================
REM SCRIPT PRINCIPAL
REM ============================================================
echo.
echo ════════════════════════════════════════════════════════════
echo      INSTALADOR DE TAREAS PROGRAMADAS - MARKETPLACE
echo          Publicación Automática de Productos
echo ════════════════════════════════════════════════════════════
echo.
echo Este script creará 3 tareas programadas:
echo   - 19:00 - Publicación noche (1)
echo   - 19:30 - Publicación noche (2)
echo   - 20:00 - Publicación noche (3)
echo.
echo ════════════════════════════════════════════════════════════
echo.

REM Obtener la ruta del proyecto
set "PROYECTO_DIR=%~dp0"
set "PROYECTO_DIR=%PROYECTO_DIR:~0,-1%"

echo 📁 Ruta del proyecto: %PROYECTO_DIR%
echo.

REM Verificar que el archivo principal existe
if not exist "%PROYECTO_DIR%\0_Ejecutar_Todo.bat" (
    echo ❌ ERROR: No se encuentra 0_Ejecutar_Todo.bat
    echo    Verifica que estás ejecutando este script desde la carpeta del proyecto
    pause
    exit /b 1
)

echo ✅ Archivo principal encontrado
echo ✅ Permisos de administrador: ACTIVOS
echo.
pause

echo.
echo ════════════════════════════════════════════════════════════
echo Creando tareas programadas...
echo ════════════════════════════════════════════════════════════
echo.

REM Eliminar tareas existentes primero (para evitar duplicados)
echo 🔍 Eliminando tareas existentes (si hay)...
schtasks /delete /tn MarketplaceAuto1900 /f 2>nul
schtasks /delete /tn MarketplaceAuto1930 /f 2>nul
schtasks /delete /tn MarketplaceAuto2000 /f 2>nul
echo.

REM ============================================================
REM TAREA 1: 19:00 - Publicación noche (1)
REM ============================================================
echo 📌 Creando tarea: MarketplaceAuto1900...

schtasks /create /tn MarketplaceAuto1900 /tr %PROYECTO_DIR%\0_Ejecutar_Todo.bat /sc daily /st 19:00 /f

if %errorlevel% equ 0 (
    echo    ✅ Tarea 19:00 creada exitosamente
) else (
    echo    ❌ Error creando tarea 19:00 - Código: %errorlevel%
)
echo.

REM ============================================================
REM TAREA 2: 19:30 - Publicación noche (2)
REM ============================================================
echo 📌 Creando tarea: MarketplaceAuto1930...

schtasks /create /tn MarketplaceAuto1930 /tr %PROYECTO_DIR%\0_Ejecutar_Todo.bat /sc daily /st 19:30 /f

if %errorlevel% equ 0 (
    echo    ✅ Tarea 19:30 creada exitosamente
) else (
    echo    ❌ Error creando tarea 19:30 - Código: %errorlevel%
)
echo.

REM ============================================================
REM TAREA 3: 20:00 - Publicación noche (3)
REM ============================================================
echo 📌 Creando tarea: MarketplaceAuto2000...

schtasks /create /tn MarketplaceAuto2000 /tr %PROYECTO_DIR%\0_Ejecutar_Todo.bat /sc daily /st 20:00 /f

if %errorlevel% equ 0 (
    echo    ✅ Tarea 20:00 creada exitosamente
) else (
    echo    ❌ Error creando tarea 20:00 - Código: %errorlevel%
)
echo.

echo ════════════════════════════════════════════════════════════
echo ✅ INSTALACIÓN COMPLETADA
echo ════════════════════════════════════════════════════════════
echo.
echo 📋 Tareas creadas:
echo    1. MarketplaceAuto1900 (19:00 - Noche 1)
echo    2. MarketplaceAuto1930 (19:30 - Noche 2)
echo    3. MarketplaceAuto2000 (20:00 - Noche 3)
echo.
echo 💡 Para verificar:
echo    - Presiona Win + R
echo    - Escribe: taskschd.msc
echo    - Presiona Enter
echo    - Busca: MarketplaceAuto1900, MarketplaceAuto1930, MarketplaceAuto2000
echo.
echo 🗑️  Para eliminar las tareas:
echo    - Ejecuta "Desinstalar_Tareas_Marketplace.bat"
echo.
echo 🧪 Para probar manualmente:
echo    - Abre Programador de Tareas (taskschd.msc)
echo    - Clic derecho en una tarea
echo    - Selecciona "Ejecutar"
echo.
echo 📅 Las tareas se ejecutarán automáticamente todos los días
echo    a las 19:00, 19:30 y 20:00 (3 productos por día)
echo.
echo 📦 El sistema rotará automáticamente entre los productos
echo    disponibles, respetando el límite de 20 publicaciones/día
echo.
pause
