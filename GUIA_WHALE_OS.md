# Guía de Uso: CXTv IPTV & Player para Smart TV Caixun (Whale OS)

¡Bienvenido! Este proyecto convierte **CXTv** (`https://www.cxtvenvivo.com/`) en una solución IPTV completa y adaptada específicamente para tu televisor **Caixun SMART2KTVSE con Whale OS**, sin depender de Google Play Store ni de un navegador en la TV.

---

## 📁 Archivos Disponibles en este Proyecto (`c:\Users\User\caxipttv`)

| Archivo / Carpeta | Descripción |
| :--- | :--- |
| **`cxtv_caixun_smarttv.m3u`** | **⭐ Lista recomendada para tu TV Caixun.** Canales en español, Colombia, deportes, películas, series y noticias con streams HLS directos de alta compatibilidad y guía EPG integrada. |
| **`cxtv_tvporinternet.m3u`** | **⚽ Canales Premium & Deportes TVporInternet:** ESPN (1-7), Fox Sports (1-3), Directv Sports (1, 2, Plus), Sky Sports, TyC, Star Channel, Warner, Cinecanal, etc. |
| **`cxtv_teleonline.m3u`** | **📺 Canales Teleonline / iptv-org:** Canales verificados en abierto de España (TDT RTVE), Colombia y Latinoamérica. |
| **`cxtv_colombia.m3u`** | Lista exclusiva de canales de Colombia (Caracol, RCN, Señal Colombia, Win Sports, Teleantioquia, etc.). |
| **`cxtv_vod_peliculas.m3u`** | **🍿 Lista VOD Películas:** Catálogo de películas clásicas y de dominio público a la carta bajo demanda. |
| **`cxtv_pluto_tv.m3u`** | Canales FAST 24/7 de Pluto TV Latinoamérica con streaming verificado. |
| **`cxtv_latam.m3u`** | Lista completa en Español (Colombia, México, Argentina, España, Chile, Perú, etc.). |
| **`cxtv_todos.m3u`** | Lista con todos los canales directos HLS a nivel mundial. |
| **`player/index.html`** | Reproductor Web OTT moderno tipo Smart TV con pestañas En Vivo y VOD, Modo Cine, Selector de Calidad y guía EPG. |

---

## 🎯 Solución 1: Listas IPTV M3U en tu TV Caixun (Vía USB y Whale Store)

En televisores Caixun con Whale OS (sin Play Store), tienes 3 métodos sencillos para disfrutar los canales:

### 🔹 Método A: Con la app "SS IPTV" (La más fácil y recomendada)
Whale OS cuenta con su propia tienda de aplicaciones (**Whale Store** / **Zeasn App Store**). La app **SS IPTV** está disponible gratuitamente y te permite cargar la lista desde tu PC sin escribir enlaces largos con el control remoto del TV:

1. **En tu TV Caixun:**
   - Abre la tienda de aplicaciones de la TV (**Whale Store** o **App Store**).
   - Busca e instala **SS IPTV**.
   - Abre la app, ve a la tuerca de **Ajustes / Configuración** (ícono de tuerca en la esquina superior derecha).
   - En la pestaña General, selecciona **Obtener código** (Get code). Aparecerá un código alfanumérico temporal en pantalla.
2. **En tu computador con Windows 10/11:**
   - Abre tu navegador web y entra a: [https://ss-iptv.com/es/users/playlist](https://ss-iptv.com/es/users/playlist)
   - Escribe el código que viste en la pantalla del TV y haz clic en **Añadir dispositivo**.
   - Haz clic en la pestaña **Listas de reproducción externas** (External Playlists) -> **Añadir elemento**.
   - Puedes subir el archivo `cxtv_caixun_smarttv.m3u` o poner la URL local del servidor: `http://[IP_DE_TU_PC]:8080/cxtv_caixun_smarttv.m3u`.
   - Haz clic en **Guardar** (Save).
3. **De vuelta en tu TV Caixun:**
   - Regresa a la pantalla principal de SS IPTV y presiona el botón de **Actualizar** (o cierra y vuelve a abrir la app).
   - Aparecerá un nuevo mosaico con el nombre de tu lista. ¡Entra y selecciona el canal que desees!

---

### 🔹 Método B: Directo por Memoria USB
1. Conecta tu memoria USB a tu PC con Windows.
2. Haz doble clic en el archivo **`copiar_a_usb.bat`** en esta carpeta.
   - El script detectará la letra de tu memoria USB y copiará automáticamente todas las listas `.m3u` y las instrucciones.
3. Desconecta la memoria USB del PC y conéctala al puerto USB de tu TV Caixun.
4. En el televisor Caixun:
   - Presiona el botón **INPUT** o **SOURCE** en el control remoto y selecciona **USB** o **Media Center / Reproductor Multimedia**.
   - Entra a **Video** o **Listas**. Algunos modelos de Whale OS permiten reproducir archivos `.m3u` directamente o ver la carpeta `IPTV_CAIXUN`.
   - Si tienes instalado **SS IPTV** u **OTT Player**, puedes ir a "Abrir desde USB" en los ajustes de la app.

---

### 🔹 Método C: Otras Apps de Whale Store (Smart IPTV u OTT Player)
Si prefieres **OTT Player** o **Smart IPTV (SIPTV)**:
- **OTT Player:** Crea una cuenta gratuita en [https://ottplayer.tv](https://ottplayer.tv), sube `cxtv_caixun_smarttv.m3u`, asigna un nombre y luego en tu TV Caixun inicia sesión con tu usuario y contraseña. Los canales se sincronizarán al instante.

---

## 🚀 Solución 2: Servidor Local & Reproductor CXTv (Vía Wi-Fi y DLNA)

Dado que tu PC y tu TV Caixun están conectados a la misma red Wi-Fi:

### 1. Iniciar el Servidor Multimedia Local
Haz doble clic en:
```bat
iniciar_servidor.bat
```
El servidor mostrará en pantalla la dirección IP de tu computadora (por ejemplo, `192.168.1.45`) y los enlaces listos:
- **Reproductor Web en tu PC:** `http://localhost:8080/player/`
- **Lista para TV:** `http://192.168.1.45:8080/cxtv_caixun_smarttv.m3u`

### 2. Transmisión Directa a la TV por DLNA / Screen Casting (Windows 10/11)
Los televisores Caixun con Whale OS admiten el protocolo estándar **DLNA / Anyview Cast**:
1. Asegúrate de que el TV Caixun esté encendido y conectado al mismo Wi-Fi que tu PC.
2. En Windows, ve a Configuración -> Dispositivos -> Bluetooth y otros dispositivos -> Agregar dispositivo -> Dispositivo de pantalla o base inalámbrica (o Reproductor Multimedia DLNA) y vincula tu Caixun.
3. O simplemente desde el reproductor multimedia de Windows, selecciona el video o canal y pulsa **Transmitir a dispositivo** (Cast to Device) -> **Caixun TV**.

---

## 🔄 Actualización de Canales
Los canales y transmisiones en internet pueden cambiar con el tiempo. Para mantener tu lista 100% actualizada:
1. Haz doble clic en **`actualizar_canales.bat`**.
2. El sistema volverá a escanear `cxtvenvivo.com`, detectará nuevas señales y regenerará tus archivos `.m3u` sin que tengas que configurar nada manualmente.
