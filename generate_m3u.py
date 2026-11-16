import os
import json
import re

JSON_FILE = "cxtv_channels.json"

SPANISH_COUNTRIES = [
    "Colombia", "México", "Mejico", "Argentina", "España", "Chile", "Perú", "Peru",
    "Ecuador", "Venezuela", "Bolivia", "Uruguay", "Paraguay", "Panamá", "Panama",
    "Costa Rica", "Guatemala", "Honduras", "El Salvador", "Nicaragua",
    "República Dominicana", "Puerto Rico", "Cuba"
]

def clean_string(s):
    return re.sub(r'[\r\n\t]+', ' ', s).strip()

def get_canonical_category(channel):
    country = channel.get('country', 'Internacional')
    categories = [c.lower() for c in channel.get('categories', [])]
    
    # Priority for Colombia
    if country == "Colombia":
        if any(k in categories for k in ['deportes', 'deportes1', 'futbol']):
            return "🇨🇴 Colombia - Deportes"
        if any(k in categories for k in ['noticias']):
            return "🇨🇴 Colombia - Noticias"
        return "🇨🇴 Colombia"
        
    if any(k in categories for k in ['deportes', 'deportes1', 'futbol', 'coches']):
        return "⚽ Deportes"
    if any(k in categories for k in ['cine', 'serie', 'telenovelas']):
        return "🎬 Cine y Series"
    if any(k in categories for k in ['noticias', 'clima']):
        return "📰 Noticias"
    if any(k in categories for k in ['niños', 'ninos']):
        return "👶 Niños e Infantil"
    if any(k in categories for k in ['música', 'musica']):
        return "🎵 Música"
    if any(k in categories for k in ['documentales', 'educación', 'educacion', 'cultura']):
        return "📚 Cultura y Documentales"
    if any(k in categories for k in ['católico', 'catolico', 'evangélico', 'evangelico']):
        return "🙏 Religión y Fe"
    if country in SPANISH_COUNTRIES:
        return f"🌎 {country} - Variedades"
    
    return f"🌐 Internacional ({country})"

def build_m3u_entry(channel, epg_url=""):
    name = clean_string(channel.get('name', 'Canal'))
    logo = channel.get('logo', '')
    group_title = get_canonical_category(channel)
    stream_url = channel.get('stream_url', '')

    tvg_id = channel.get('id', name.replace(' ', ''))
    
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
    
    # 2. Colombia channels
    colombia_channels = [c for c in hls_channels if c.get('country') == 'Colombia']

    # 3. Spanish / LATAM channels
    latam_channels = [
        c for c in hls_channels 
        if any(sc.lower() in c.get('country', '').lower() for sc in SPANISH_COUNTRIES)
    ]

    # 4. Smart TV Curated list (Latin America + Top Entertainment / Sports / News)
    smart_tv_channels = []
    smart_tv_channels.extend(latam_channels)
    for c in hls_channels:
        if c not in smart_tv_channels:
            cats = [cat.lower() for cat in c.get('categories', [])]
            if any(k in cats for k in ['cine', 'serie', 'musica', 'deportes1', 'futbol', 'documentales']):
                smart_tv_channels.append(c)

    # 5. Specialized Category Playlists (All direct HLS)
    def match_cat(c, keywords):
        cats = [k.lower() for k in c.get('categories', [])]
        return any(k in cats for k in keywords)

    deportes_channels = [c for c in hls_channels if match_cat(c, ['deportes', 'deportes1', 'futbol', 'coches'])]
    cine_channels = [c for c in hls_channels if match_cat(c, ['cine', 'serie', 'telenovelas'])]
    noticias_channels = [c for c in hls_channels if match_cat(c, ['noticias', 'clima'])]
    infantil_channels = [c for c in hls_channels if match_cat(c, ['niños', 'ninos'])]
    musica_channels = [c for c in hls_channels if match_cat(c, ['música', 'musica'])]

    # 6. Full list including web & youtube
    all_with_web = [c for c in channels if c.get('stream_url')]

    # Write files
    def write_m3u(filename, channel_list, header_title="CXTv IPTV"):
        content = f'#EXTM3U x-tvg-url="https://raw.githubusercontent.com/iptv-org/epg/master/sites/directv.com.ar.epg.xml"\n'
        content += f'# CXTv IPTV Playlist: {header_title}\n'
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
    write_m3u("cxtv_colombia.m3u", colombia_channels, "Canales de Colombia")
    write_m3u("cxtv_latam.m3u", latam_channels, "Canales en Español y Latinoamérica")
    write_m3u("cxtv_deportes.m3u", deportes_channels, "Canales de Deportes y Fútbol")
    write_m3u("cxtv_cine.m3u", cine_channels, "Canales de Cine, Series y Telenovelas")
    write_m3u("cxtv_noticias.m3u", noticias_channels, "Canales de Noticias en Vivo")
    write_m3u("cxtv_infantil.m3u", infantil_channels, "Canales para Niños e Infantiles")
    write_m3u("cxtv_musica.m3u", musica_channels, "Canales de Música y Videos")
    write_m3u("cxtv_todos.m3u", hls_channels, "Todos los canales directos HLS")
    write_m3u("cxtv_completa_web.m3u", all_with_web, "Completa (Directos + Web/YouTube)")

if __name__ == "__main__":
    generate_playlists()
