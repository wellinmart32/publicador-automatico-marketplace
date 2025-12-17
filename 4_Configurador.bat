@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Configurador del Sistema
py configurador_interactivo.py
exit
