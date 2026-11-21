@echo off
title Actualizar Canales CXTv, Pluto TV y Colombia HD
cd /d "%~dp0"
echo ===================================================
echo 1. Extrayendo canales actualizados desde CXTv...
echo ===================================================
python cxtv_scraper.py
echo.
echo ===================================================
echo 2. Integrando Pluto TV y Colombia HD y M3U...
echo ===================================================
python update_all_sources.py
echo.
echo [OK] Proceso terminado con exito.
pause
