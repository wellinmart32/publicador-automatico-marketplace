@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Sincronizar con Marketplace

echo.
echo ============================================================
echo      SINCRONIZAR CON MARKETPLACE
echo        Lee tus anuncios de Facebook
echo ============================================================
echo.

py publicar_marketplace.py --modulo sincronizar

echo.
echo ============================================================
echo           Proceso finalizado
echo ============================================================
echo.
exit
