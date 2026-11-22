import requests
import uuid
import concurrent.futures

PLUTO_API_URL = "https://api.pluto.tv/v2/channels"

CATEGORY_MAPPING = {
    "Películas": ("Cine", "🎬 Cine y Series"),
    "Series": ("Serie", "🎬 Cine y Series"),
    "Novelas": ("Telenovelas", "🎬 Cine y Series"),
    "Retro": ("Serie", "🎬 Cine y Series"),
    "Comedia": ("Variedades", "📺 Variedades y Comedia"),
    "Deportes": ("Deportes", "⚽ Deportes"),
    "Animé & Gaming": ("Anime", "👾 Animé y Gaming"),
    "Anime": ("Anime", "👾 Animé y Gaming"),
    "Kids": ("Niños", "👶 Niños e Infantil"),
    "Teen": ("Niños", "👶 Niños e Infantil"),
    "Música": ("Música", "🎵 Música"),
    "Musica": ("Música", "🎵 Música"),
    "Curiosidad": ("Documentales", "📚 Cultura y Documentales"),
    "Investigación": ("Documentales", "📚 Cultura y Documentales"),
    "Estilo de Vida": ("Variedades", "📺 Variedades y Estilo de Vida"),
    "Competencia": ("Variedades", "📺 Variedades y Entretenimiento"),
    "Reality": ("Variedades", "📺 Variedades y Entretenimiento"),
    "Entretenimiento": ("Variedades", "📺 Variedades y Entretenimiento"),
    "Noticias": ("Noticias", "📰 Noticias"),
    "South Park ve": ("Animación", "✨ Pluto TV Exclusivos")
}

# Palabras clave en URLs de segmentos que indican contenido bloqueado/slate
BLOCKED_KEYWORDS = [
    "takedownslates",
    "takedown_slates",
    "ptv_takedown",
    "slates_all",
    "geo_block",
    "not_available",
]

def build_stream_url(ch_id):
    dev_id = str(uuid.uuid4())
    sid = str(uuid.uuid4())
    return (
        f"https://cfd-v4-service-channel-stitcher-use1-1.prd.pluto.tv/stitch/hls/channel/{ch_id}/master.m3u8"
        f"?deviceMake=Chrome&deviceModel=web&deviceType=web&deviceVersion=120.0"
        f"&deviceDNT=0&appVersion=5.0.0&appName=web&deviceId={dev_id}&sid={sid}"
    )

def is_channel_blocked(ch_id, name):
    """
    Verifica si un canal de Pluto TV sirve contenido geo-bloqueado (takedown slates).
    Descarga el master manifest → elige la variante de menor calidad → lee 2-3 líneas
    de la variante para ver si los segmentos contienen palabras clave de slate.
    Retorna True si está bloqueado, False si parece contenido real.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://pluto.tv/",
        "Origin": "https://pluto.tv",
    }
    try:
        master_url = build_stream_url(ch_id)
        r = requests.get(master_url, headers=headers, timeout=10, allow_redirects=True)
        if r.status_code != 200:
            # Si el master no responde, asumir bloqueado
            print(f"  ⚠ [{name}] Master 404/error ({r.status_code}) → skip")
            return True

        master_text = r.text
        # Buscar la primera variante (#EXT-X-STREAM-INF → siguiente línea)
        lines = master_text.splitlines()
        variant_url = None
        for i, line in enumerate(lines):
            if line.startswith("#EXT-X-STREAM-INF") and i + 1 < len(lines):
                candidate = lines[i + 1].strip()
                if candidate and not candidate.startswith("#"):
                    variant_url = candidate
                    break  # usar primera (menor calidad generalmente al final, pero cualquiera sirve)

        if not variant_url:
            # No hay variantes → bloqueado
            return True

        # Si la variante es relativa, construir URL absoluta
        if not variant_url.startswith("http"):
            base = master_url.split("master.m3u8")[0]
            variant_url = base + variant_url

        # Descargar variante
        rv = requests.get(variant_url, headers=headers, timeout=10, allow_redirects=True)
        if rv.status_code != 200:
            return True

        variant_text = rv.text
        # Revisar los primeros segmentos para palabras clave de slate
        for keyword in BLOCKED_KEYWORDS:
            if keyword in variant_text.lower():
                print(f"  🚫 [{name}] Contenido bloqueado detectado: '{keyword}' → omitir")
                return True

        return False  # Canal OK

    except Exception as e:
        print(f"  ⚠ [{name}] Error verificando: {e} → omitir")
        return True  # Si no podemos verificar, descartar por seguridad


def get_pluto_channels(verify=True, max_workers=10):
    channels = []
    blocked_count = 0
    try:
        resp = requests.get(PLUTO_API_URL, timeout=12)
        if resp.status_code != 200:
            print(f"Error fetching Pluto TV: status {resp.status_code}")
            return []
        data = resp.json()
        print(f"-> API retornó {len(data)} canales Pluto TV. Verificando geo-bloqueo...")

        # Construir lista preliminar
        candidates = []
        for ch in data:
            ch_id = ch.get('_id') or ch.get('id')
            name = ch.get('name', '').strip()
            slug = ch.get('slug', str(ch_id))
            raw_cat = ch.get('category', 'Entretenimiento')

            logo = ch.get('colorLogoPNG', {}).get('path', '')
            if not logo:
                images = ch.get('images', [])
                if images:
                    logo = images[0].get('url', '')

            cat_slug, group_name = CATEGORY_MAPPING.get(raw_cat, ("Variedades", "✨ Pluto TV"))

            candidates.append({
                "_id": ch_id,
                "id": f"pluto-{slug}",
                "name": name,
                "country": "Latinoamérica",
                "categories": [cat_slug, raw_cat, "Pluto TV"],
                "group": group_name,
                "logo": logo,
                "stream_url": None,  # Se asigna después de verificación
                "stream_type": "hls",
                "cxtv_url": f"https://pluto.tv/es/live-tv/{slug}"
            })

        if verify:
            # Prueba rápida inicial (Canal sonda) para no demorar si todo Pluto TV está geo-bloqueado
            probe_id = "5dcb62e63d4d8f0009f36881" # Cine Acción
            print("-> Verificando sonda de región Pluto TV...")
            if is_channel_blocked(probe_id, "Pluto TV Sonda"):
                print("-> 🚫 Pluto TV está sirviendo 'takedown slates' (geo-bloqueo total para esta región). Omitiendo Pluto TV para evitar bucles de error.")
                return []

        # Verificación paralela de geo-bloqueo
        def check_channel(c):
            ch_id = c["_id"]
            name = c["name"]
            blocked = is_channel_blocked(ch_id, name)
            return c, blocked

        print(f"-> Verificando {len(candidates)} canales con {max_workers} hilos (puede tardar ~1-2 min)...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(check_channel, c): c for c in candidates}
            for future in concurrent.futures.as_completed(futures):
                try:
                    c, blocked = future.result()
                    if blocked:
                        blocked_count += 1
                    else:
                        c["stream_url"] = build_stream_url(c["_id"])
                        channels.append(c)
                except Exception as e:
                    print(f"  Error en future: {e}")

        print(f"-> ✅ {len(channels)} canales activos | 🚫 {blocked_count} geo-bloqueados/sin contenido omitidos")

    except Exception as e:
        print(f"Error extrayendo canales Pluto TV: {e}")

    return channels


if __name__ == "__main__":
    chans = get_pluto_channels(verify=True, max_workers=12)
    if chans:
        print(f"\nEjemplo: {chans[0]['name']} -> {chans[0]['group']}")
        print(f"Total canales válidos: {len(chans)}")
