import os
import json
import re

JSON_FILE = "cxtv_channels.json"

SPANISH_COUNTRIES = [
    "Colombia", "México", "Mejico", "Argentina", "España", "Chile", "Perú", "Peru",
    "Ecuador", "Venezuela", "Bolivia", "Uruguay", "Paraguay", "Panamá", "Panama",
    "Costa Rica", "Guatemala", "Honduras", "El Salvador", "Nicaragua",
    "República Dominicana", "Puerto Rico", "Cuba", "Latinoamérica"
]

def clean_string(s):
    return re.sub(r'[\r\n\t]+', ' ', s).strip()

def get_canonical_category(channel):
    # Preserved designated emoji category
    if channel.get('group') and any(channel.get('group', '').startswith(e) for e in ['🇨🇴', '⚽', '🎬', '📰', '👶', '🎵', '📺', '📚', '🙏', '👾', '✨', '🌎', '🌐', '🇪🇸', '🍿']):
        return channel['group']

    cid = channel.get('id', '')
    cat = channel.get('category', '')
    categories = [c.lower() for c in channel.get('categories', [])]
    if cat:
        categories.append(cat.lower())
    country = channel.get('country', 'Internacional')

    # TVporInternet Premium Channels
    if cid.startswith('tvpi-') or channel.get('source') == 'TVporInternet.org':
        if 'deportes' in categories:
            return "⚽ Deportes Premium (TVpI)"
        if any(k in categories for k in ['cine', 'cine y series', 'series']):
            return "🎬 Cine y Series Premium (TVpI)"
        if 'infantil' in categories:
            return "👶 Niños e Infantil (TVpI)"
        if 'documentales' in categories:
            return "📚 Documentales (TVpI)"
        return "🌎 Variedades Premium (TVpI)"

    # Teleonline Channels
    if cid.startswith('tlo-') or 'Teleonline' in channel.get('source', ''):
        if country == "España":
            return "🇪🇸 España TDT (Teleonline)"
        if country == "Colombia":
            return "🇨🇴 Colombia (Teleonline)"
        if any(k in categories for k in ['sports', 'deportes']):
            return "⚽ Deportes (Teleonline)"
        if any(k in categories for k in ['news', 'noticias']):
            return "📰 Noticias (Teleonline)"
        return f"🌎 {country} (Teleonline)"

    # Priority for Colombia
    if country == "Colombia":
        if any(k in categories for k in ['deportes', 'deportes1', 'futbol']):
            return "🇨🇴 Colombia - Deportes"
        if any(k in categories for k in ['noticias']):
            return "🇨🇴 Colombia - Noticias"
        return "🇨🇴 Colombia"
        
    if any(k in categories for k in ['deportes', 'deportes1', 'futbol', 'coches', 'sports']):
        return "⚽ Deportes"
    if any(k in categories for k in ['cine', 'serie', 'telenovelas', 'movies', 'series']):
        return "🎬 Cine y Series"
    if any(k in categories for k in ['noticias', 'clima', 'news']):
        return "📰 Noticias"
    if any(k in categories for k in ['niños', 'ninos', 'kids', 'animation']):
        return "👶 Niños e Infantil"
    if any(k in categories for k in ['música', 'musica', 'music']):
        return "🎵 Música"
    if any(k in categories for k in ['documentales', 'educación', 'educacion', 'cultura', 'documentary']):
        return "📚 Cultura y Documentales"
    if any(k in categories for k in ['católico', 'catolico', 'evangélico', 'evangelico', 'religious']):
        return "🙏 Religión y Fe"
    if country in SPANISH_COUNTRIES:
        return f"🌎 {country} - Variedades"
    
    return f"🌐 Internacional ({country})"

def build_m3u_entry(channel, epg_url=""):
    name = clean_string(channel.get('name', 'Canal'))
    logo = channel.get('logo', '')
    group_title = get_canonical_category(channel)
    stream_url = channel.get('stream_url', '')

    tvg_id = channel.get('tvg_id') or channel.get('id', name.replace(' ', ''))
    
    entry = f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{name}" tvg-logo="{logo}" group-title="{group_title}",{name}\n{stream_url}\n'
    return entry

def generate_playlists():
    if not os.path.exists(JSON_FILE):
        print(f"Error: {JSON_FILE} not found. Please run the scraper first.")
        return

    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        channels = json.load(f)

    print(f"Loaded {len(channels)} channels from database.")

    # 1. Direct HLS streams only
    hls_channels = [c for c in channels if c.get('stream_type') == 'hls' and c.get('stream_url')]
    
    # 2. Source-specific channels
    tvpi_channels = [c for c in hls_channels if c.get('id', '').startswith('tvpi-') or c.get('source') == 'TVporInternet.org']
    teleonline_channels = [c for c in hls_channels if c.get('id', '').startswith('tlo-') or 'Teleonline' in c.get('source', '')]
    pluto_channels = [c for c in hls_channels if 'pluto' in c.get('id', '') or 'Pluto TV' in c.get('categories', [])]

    # 3. Colombia channels
    colombia_channels = [c for c in hls_channels if c.get('country') == 'Colombia']

    # 4. Spanish / LATAM channels
    latam_channels = [
        c for c in hls_channels 
        if any(sc.lower() in c.get('country', '').lower() for sc in SPANISH_COUNTRIES) or c.get('id', '').startswith(('tvpi-', 'tlo-'))
    ]

    # 5. Smart TV Curated list (Latin America + Top Entertainment / Sports / News)
    # Exclude streams verified as dead/offline
    active_hls = [c for c in hls_channels if c.get('is_active') is not False]
    
    smart_tv_channels = []
    # Add TVporInternet premium first (ESPN, Directv Sports, Warner, etc.)
    for c in tvpi_channels:
        if c.get('is_active') is not False and c not in smart_tv_channels:
            smart_tv_channels.append(c)
            
    # Add Colombia HD
    for c in colombia_channels:
        if c.get('is_active') is not False and c not in smart_tv_channels:
            smart_tv_channels.append(c)

    # Add verified Teleonline (Spain / Latam)
    for c in teleonline_channels:
        if c.get('is_active') is not False and c not in smart_tv_channels:
            smart_tv_channels.append(c)

    # Add Latam and Pluto
    for c in active_hls:
        if c not in smart_tv_channels:
            if any(sc.lower() in c.get('country', '').lower() for sc in SPANISH_COUNTRIES) or c.get('id', '').startswith('pluto-'):
                smart_tv_channels.append(c)

    # 6. Specialized Category Playlists (All direct HLS)
    def match_cat(c, keywords):
        cats = [k.lower() for k in c.get('categories', [])]
        if c.get('category'):
            cats.append(c.get('category').lower())
        return any(k in cats for k in keywords)

    deportes_channels = [c for c in hls_channels if match_cat(c, ['deportes', 'deportes1', 'futbol', 'coches', 'sports'])]
    cine_channels = [c for c in hls_channels if match_cat(c, ['cine', 'serie', 'telenovelas', 'movies', 'series', 'cine y series'])]
    noticias_channels = [c for c in hls_channels if match_cat(c, ['noticias', 'clima', 'news'])]
    infantil_channels = [c for c in hls_channels if match_cat(c, ['niños', 'ninos', 'infantil', 'kids', 'animation'])]
    musica_channels = [c for c in hls_channels if match_cat(c, ['música', 'musica', 'music'])]

    # 7. Full list including web & youtube
    all_with_web = [c for c in channels if c.get('stream_url')]

    # Write files
    def write_m3u(filename, channel_list, header_title="CXTv IPTV"):
        content = f'#EXTM3U url-tvg="https://epgshare01.online/epgshare01/epg_ripper_CO1.xml.gz" x-tvg-url="https://epgshare01.online/epgshare01/epg_ripper_CO1.xml.gz,https://epgshare01.online/epgshare01/epg_ripper_ALL_SOURCES1.xml.gz"\n'
        content += f'# CXTv IPTV Playlist: {header_title}\n'
        content += f'# Guía EPG: Colombia y LATAM integrada\n'
        content += f'# Generado para Smart TV Caixun (Whale OS) y reproductores compatibles\n\n'
        for c in channel_list:
            content += build_m3u_entry(c)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

        player_dir = "player"
        if os.path.exists(player_dir):
            with open(os.path.join(player_dir, filename), 'w', encoding='utf-8') as pf:
                pf.write(content)

        print(f"-> Generated {filename} with {len(channel_list)} channels.")

    write_m3u("cxtv_caixun_smarttv.m3u", smart_tv_channels, "Optimizado para Caixun Whale OS con Categorías")
    write_m3u("cxtv_tvporinternet.m3u", tvpi_channels, "Canales Deportes y Premium TVporInternet")
    write_m3u("cxtv_teleonline.m3u", teleonline_channels, "Canales Teleonline e Internacionales")
    write_m3u("cxtv_colombia.m3u", colombia_channels, "Canales de Colombia")
    write_m3u("cxtv_latam.m3u", latam_channels, "Canales en Español y Latinoamérica")
    write_m3u("cxtv_pluto_tv.m3u", pluto_channels, "Canales FAST Gratuitos Pluto TV Latino")
    write_m3u("cxtv_deportes.m3u", deportes_channels, "Canales de Deportes y Fútbol")
    write_m3u("cxtv_cine.m3u", cine_channels, "Canales de Cine, Series y Telenovelas")
    write_m3u("cxtv_noticias.m3u", noticias_channels, "Canales de Noticias en Vivo")
    write_m3u("cxtv_infantil.m3u", infantil_channels, "Canales para Niños e Infantiles")
    write_m3u("cxtv_musica.m3u", musica_channels, "Canales de Música y Videos")
    write_m3u("cxtv_todos.m3u", hls_channels, "Todos los canales directos HLS")
    write_m3u("cxtv_completa_web.m3u", all_with_web, "Completa (Directos + Web/YouTube)")

    # 8. VOD Movies & Series
    vod_file = "vod_catalog.json"
    if os.path.exists(vod_file):
        try:
            with open(vod_file, "r", encoding="utf-8") as vf:
                vod_items = json.load(vf)
            vod_channels = []
            for v in vod_items:
                vod_channels.append({
                    "id": v["id"],
                    "name": f"{v['title']} ({v.get('year', '')})",
                    "country": "VOD",
                    "categories": [v.get("category", "Cine"), "Películas"],
                    "group": f"🍿 Cine VOD - {v.get('category', 'Películas')}",
                    "logo": v.get("poster", ""),
                    "stream_url": v["stream_url"],
                    "stream_type": v.get("stream_type", "mp4")
                })
            write_m3u("cxtv_vod_peliculas.m3u", vod_channels, "Películas y Series a la Carta VOD")
        except Exception as e:
            print(f"Error generating VOD m3u: {e}")

if __name__ == "__main__":
    generate_playlists()
