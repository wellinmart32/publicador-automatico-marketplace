@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Secuencia Completa - Marketplace

echo.
echo ============================================================
echo      SECUENCIA COMPLETA
echo        Modulos configurados en el Configurador
echo ============================================================
echo.

py publicar_marketplace.py --secuencia

echo.
echo ============================================================
echo           Proceso finalizado
echo ============================================================
echo.
exit
