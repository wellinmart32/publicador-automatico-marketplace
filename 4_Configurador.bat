@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Configurador de Marketplace
py configurador_gui.py
exit
