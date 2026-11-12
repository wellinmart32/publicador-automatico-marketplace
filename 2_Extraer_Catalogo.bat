@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Extraer Catalogo de WhatsApp

echo.
echo ============================================================
echo      EXTRACTOR DE CATALOGO
echo        WhatsApp Business
echo ============================================================
echo.

py publicar_marketplace.py --modulo extraer

echo.
echo ============================================================
echo           Proceso finalizado
echo ============================================================
echo.
exit
