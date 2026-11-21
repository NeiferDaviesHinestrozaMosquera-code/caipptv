@echo off
title CXTv IPTV Master - VLC Media Player
cls
echo ============================================================
echo    🎬 REPRODUCTOR IPTV CXTV MASTER PARA VLC MEDIA PLAYER
echo ============================================================
echo.
set VLC_EXE=""
if exist "C:\Program Files\VideoLAN\VLC\vlc.exe" set VLC_EXE="C:\Program Files\VideoLAN\VLC\vlc.exe"
if exist "C:\Program Files (x86)\VideoLAN\VLC\vlc.exe" set VLC_EXE="C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"
if exist "%LOCALAPPDATA%\Programs\VLC\vlc.exe" set VLC_EXE="%LOCALAPPDATA%\Programs\VLC\vlc.exe"

if %VLC_EXE%=="" (
    echo [!] No se encontro VLC Media Player instalado en las rutas predeterminadas.
    echo Puedes descargarlo gratis desde: https://www.videolan.org/vlc/
    echo O abre manualmente el archivo 'cxtv_master_vlc.m3u' en tu reproductor favorito.
    pause
    exit /b
)

echo [+] VLC detectado en: %VLC_EXE%
echo [+] Abriendo lista maestra completa con todos los canales y peliculas VOD...
echo.
echo [TIP] Dentro de VLC:
echo       - Presiona Ctrl+L para abrir la Lista de reproduccion.
echo       - Veras los canales organizados en carpetas y categorias.
echo       - Doble clic en cualquier canal para iniciar la transmision.
echo.
start "" %VLC_EXE% --network-caching=2500 --meta-title="CXTv IPTV Master" "%~dp0cxtv_master_vlc.m3u"
exit /b
