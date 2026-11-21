import requests
import uuid

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

def get_pluto_channels():
    channels = []
    try:
        resp = requests.get(PLUTO_API_URL, timeout=12)
        if resp.status_code != 200:
            print(f"Error fetching Pluto TV: status {resp.status_code}")
            return []
        data = resp.json()

        for ch in data:
            ch_id = ch.get('_id') or ch.get('id')
            name = ch.get('name', '').strip()
            slug = ch.get('slug', str(ch_id))
            raw_cat = ch.get('category', 'Entretenimiento')

            # Build valid stitcher HLS URL
            dev_id = str(uuid.uuid4())
            sid = str(uuid.uuid4())
            stream_url = (
                f"https://cfd-v4-service-channel-stitcher-use1-1.prd.pluto.tv/stitch/hls/channel/{ch_id}/master.m3u8"
                f"?deviceMake=Chrome&deviceModel=web&deviceType=web&deviceVersion=120.0"
                f"&deviceDNT=0&appVersion=5.0.0&appName=web&deviceId={dev_id}&sid={sid}"
            )

            # Logo
            logo = ch.get('colorLogoPNG', {}).get('path', '')
            if not logo:
                images = ch.get('images', [])
                if images:
                    logo = images[0].get('url', '')

            cat_slug, group_name = CATEGORY_MAPPING.get(raw_cat, ("Variedades", "✨ Pluto TV"))

            channels.append({
                "id": f"pluto-{slug}",
                "name": name,
                "country": "Latinoamérica",
                "categories": [cat_slug, raw_cat, "Pluto TV"],
                "group": group_name,
                "logo": logo,
                "stream_url": stream_url,
                "stream_type": "hls",
                "cxtv_url": f"https://pluto.tv/es/live-tv/{slug}"
            })

        print(f"-> Extracted {len(channels)} Pluto TV channels.")
    except Exception as e:
        print(f"Error extracting Pluto TV channels: {e}")

    return channels

if __name__ == "__main__":
    chans = get_pluto_channels()
    if chans:
        print(f"Sample Pluto channel: {chans[0]['name']} -> {chans[0]['group']}")
