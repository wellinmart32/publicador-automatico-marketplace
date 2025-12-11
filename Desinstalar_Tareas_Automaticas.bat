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
echo   DESINSTALADOR DE TAREAS PROGRAMADAS - MARKETPLACE
echo ════════════════════════════════════════════════════════════
echo.
echo Este script eliminará todas las tareas programadas de Marketplace
echo.
echo ⚠️  ¿Estás seguro que quieres continuar?
echo.
pause

echo.
echo ════════════════════════════════════════════════════════════
echo Eliminando tareas programadas...
echo ════════════════════════════════════════════════════════════
echo.

echo 🔍 Buscando tareas instaladas...
echo.

REM Listar tareas antes de eliminar
schtasks /query /fo list | findstr /C:"MarketplaceAuto"

echo.
echo ────────────────────────────────────────────────────────────
echo.

REM Eliminar tareas con nombres simplificados
echo 📌 Eliminando MarketplaceAuto1900...
schtasks /delete /tn MarketplaceAuto1900 /f
if %errorlevel% equ 0 (
    echo    ✅ MarketplaceAuto1900 eliminada
) else (
    echo    ⚠️  MarketplaceAuto1900 no encontrada
)
echo.

echo 📌 Eliminando MarketplaceAuto1930...
schtasks /delete /tn MarketplaceAuto1930 /f
if %errorlevel% equ 0 (
    echo    ✅ MarketplaceAuto1930 eliminada
) else (
    echo    ⚠️  MarketplaceAuto1930 no encontrada
)
echo.

echo 📌 Eliminando MarketplaceAuto2000...
schtasks /delete /tn MarketplaceAuto2000 /f
if %errorlevel% equ 0 (
    echo    ✅ MarketplaceAuto2000 eliminada
) else (
    echo    ⚠️  MarketplaceAuto2000 no encontrada
)
echo.

REM Eliminar tareas con nombres antiguos (si existen)
echo 🔍 Buscando tareas con nombres antiguos...
schtasks /delete /tn "Marketplace Auto - 09:00 Mañana" /f 2>nul
schtasks /delete /tn "Marketplace Auto - 09:00 Manana" /f 2>nul
schtasks /delete /tn "Marketplace Auto - 12:00 Mediodía" /f 2>nul
schtasks /delete /tn "Marketplace Auto - 12:00 Mediodia" /f 2>nul
schtasks /delete /tn "Marketplace Auto - 15:00 Tarde" /f 2>nul
schtasks /delete /tn "Marketplace Auto - 18:00 Noche" /f 2>nul
schtasks /delete /tn "Marketplace Auto - 19:00 Noche" /f 2>nul
schtasks /delete /tn "Marketplace Auto - 19:30 Noche" /f 2>nul
schtasks /delete /tn "Marketplace Auto - 20:00 Noche" /f 2>nul

echo.
echo ────────────────────────────────────────────────────────────
echo.
echo 🔍 Verificando que se eliminaron...
schtasks /query /fo list | findstr /C:"MarketplaceAuto" /C:"Marketplace Auto"

if %errorlevel% equ 0 (
    echo.
    echo ⚠️  Algunas tareas aún existen
) else (
    echo.
    echo ✅ Todas las tareas fueron eliminadas
)

echo.
echo ════════════════════════════════════════════════════════════
echo ✅ DESINSTALACIÓN COMPLETADA
echo ════════════════════════════════════════════════════════════
echo.
echo 💡 Verifica en Programador de Tareas (taskschd.msc)
echo.
pause
