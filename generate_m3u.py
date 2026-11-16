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

def build_m3u_entry(channel, epg_url=""):
    name = clean_string(channel.get('name', 'Canal'))
    logo = channel.get('logo', '')
    country = channel.get('country', 'General')
    categories = channel.get('categories', [])
    category_str = categories[0] if categories else 'General'
    group_title = f"{country} - {category_str}"
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
    # Add all LATAM
    smart_tv_channels.extend(latam_channels)
    # Add top international music/documentaries/news in English or global
    for c in hls_channels:
        if c not in smart_tv_channels:
            cats = [cat.lower() for cat in c.get('categories', [])]
            if any(k in cats for k in ['cine', 'serie', 'musica', 'deportes1', 'futbol', 'documentales']):
                smart_tv_channels.append(c)

    # 5. Full list including web & youtube
    all_with_web = [c for c in channels if c.get('stream_url')]

    # Write files
    def write_m3u(filename, channel_list, header_title="CXTv IPTV"):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f'#EXTM3U x-tvg-url="https://raw.githubusercontent.com/iptv-org/epg/master/sites/directv.com.ar.epg.xml"\n')
            f.write(f'# CXTv IPTV Playlist: {header_title}\n')
            f.write(f'# Generado para Smart TV Caixun (Whale OS) y reproductores compatibles\n\n')
            for c in channel_list:
                f.write(build_m3u_entry(c))
        print(f"-> Generated {filename} with {len(channel_list)} channels.")

    write_m3u("cxtv_todos.m3u", hls_channels, "Todos los canales directos HLS")
    write_m3u("cxtv_colombia.m3u", colombia_channels, "Canales de Colombia")
    write_m3u("cxtv_latam.m3u", latam_channels, "Canales en Español y Latinoamérica")
    write_m3u("cxtv_caixun_smarttv.m3u", smart_tv_channels, "Optimizado para Caixun Whale OS")
    write_m3u("cxtv_completa_web.m3u", all_with_web, "Completa (Directos + Web/YouTube)")

if __name__ == "__main__":
    generate_playlists()
