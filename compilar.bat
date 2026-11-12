@echo off
chcp 65001 >nul
title Compilador - Marketplace AutomaPro
cd /d "%~dp0"

echo.
echo ============================================================
echo     COMPILADOR - MARKETPLACE AUTOMAPRO
echo ============================================================
echo.
echo Este script compila todos los ejecutables del proyecto.
echo Asegurate de tener PyInstaller instalado.
echo.
pause

set PYINSTALLER=py -m PyInstaller
set DATOS_BASE=--add-data "compartido;compartido" --add-data "iconos;iconos" --add-data "version.txt;."
set FLAGS=--onefile --windowed --noconfirm
set FLAGS_CONSOLA=--onefile --noconfirm

echo.
echo [1/6] Compilando PublicadorMarketplace.exe...
%PYINSTALLER% %FLAGS_CONSOLA% %DATOS_BASE% --add-data "publicadores;publicadores" --add-data "extractores;extractores" --icon=iconos/tienda.ico --name PublicadorMarketplace publicar_marketplace.py
echo.

echo [2/6] Compilando PanelControl.exe...
%PYINSTALLER% %FLAGS% %DATOS_BASE% --icon=iconos/dashboard.ico --name PanelControl panel_control.py
echo.

echo [3/6] Compilando WizardMarketplace.exe...
%PYINSTALLER% %FLAGS% %DATOS_BASE% --icon=iconos/wizard.ico --name WizardMarketplace wizard_primera_vez.py
echo.

echo [4/6] Compilando ConfiguradorMarketplace.exe...
%PYINSTALLER% %FLAGS% %DATOS_BASE% --icon=iconos/settings.ico --name ConfiguradorMarketplace configurador_gui.py
echo.

echo [5/6] Compilando GestorArticulos.exe...
%PYINSTALLER% %FLAGS% %DATOS_BASE% --icon=iconos/edit.ico --name GestorArticulos gestor_articulos_gui.py
echo.

echo [6/6] Compilando GestorTareasMarketplace.exe...
%PYINSTALLER% %FLAGS% %DATOS_BASE% --icon=iconos/calendar.ico --name GestorTareasMarketplace gestor_tareas_gui.py
echo.

echo ============================================================
echo  COMPILACION COMPLETADA
echo  Los .exe estan en la carpeta: dist\
echo ============================================================
echo.
pause
