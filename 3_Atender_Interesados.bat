@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Atender Interesados

echo.
echo ============================================================
echo      ATENCION DE INTERESADOS
echo        Messenger de Marketplace
echo ============================================================
echo.

py publicar_marketplace.py --modulo atender

echo.
echo ============================================================
echo           Proceso finalizado
echo ============================================================
echo.
exit
