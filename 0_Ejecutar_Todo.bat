@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Flujo Completo Automático

echo.
echo ============================================================
echo           FLUJO COMPLETO AUTOMATICO
echo ============================================================
echo.
echo Este proceso ejecutara:
echo   1. Crear/actualizar estructura de carpetas
echo   2. Extraer productos de WhatsApp
echo   3. Publicar automaticamente en Marketplace
echo.
echo ============================================================
echo.

py flujo_completo.py
pause
