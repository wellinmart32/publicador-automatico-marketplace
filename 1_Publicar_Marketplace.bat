@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Publicar en Marketplace

echo.
echo ============================================================
echo      PUBLICADOR DE PRODUCTOS
echo        Facebook Marketplace
echo ============================================================
echo.

py publicar_marketplace.py --modulo publicar

echo.
echo ============================================================
echo           Proceso finalizado
echo ============================================================
echo.
exit
