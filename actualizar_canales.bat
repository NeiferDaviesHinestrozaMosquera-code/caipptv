@echo off
title Actualizar Canales CXTv
cd /d "%~dp0"
echo ===================================================
echo 1. Extrayendo canales actualizados desde CXTv...
echo ===================================================
python cxtv_scraper.py
echo.
echo ===================================================
echo 2. Generando listas M3U / M3U8 para Caixun TV...
echo ===================================================
python generate_m3u.py
echo.
echo [OK] Proceso terminado con exito.
pause
