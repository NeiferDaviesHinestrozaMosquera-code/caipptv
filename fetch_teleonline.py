import urllib.request
import ssl
import re
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://teleonline.org/'
}

IPTV_SOURCES = [
    {
        'url': 'https://iptv-org.github.io/iptv/countries/es.m3u',
        'country': 'España'
    },
    {
        'url': 'https://iptv-org.github.io/iptv/countries/co.m3u',
        'country': 'Colombia'
    },
    {
        'url': 'https://iptv-org.github.io/iptv/languages/spa.m3u',
        'country': 'Latinoamérica'
    }
]

def parse_m3u_content(content, default_country):
    channels = []
    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF:"):
            info = line
            i += 1
            while i < len(lines) and (lines[i].strip().startswith("#") or not lines[i].strip()):
                i += 1
            if i < len(lines):
                stream_url = lines[i].strip()
                if stream_url.startswith("http") and ".m3u8" in stream_url:
                    # Parse attributes
                    name_match = re.search(r',([^,]+)$', info)
                    name = name_match.group(1).strip() if name_match else "Canal"
                    
                    tvg_id_match = re.search(r'tvg-id="([^"]*)"', info)
                    tvg_id = tvg_id_match.group(1) if tvg_id_match else ""
                    
                    logo_match = re.search(r'tvg-logo="([^"]*)"', info)
                    logo = logo_match.group(1) if logo_match else ""
                    
                    group_match = re.search(r'group-title="([^"]*)"', info)
                    category = group_match.group(1) if group_match else "General"
                    if not category or category == "Undefined":
                        category = "Variedades"
                        
                    clean_id = re.sub(r'[^a-zA-Z0-9]', '', (tvg_id or name)).lower()
                    channels.append({
                        'id': f"tlo-{clean_id}",
                        'name': f"{name} (TLO)",
                        'display_name': name,
                        'category': category,
                        'country': default_country,
                        'stream_url': stream_url,
                        'stream_type': 'hls',
                        'logo': logo,
                        'tvg_id': tvg_id or f"{clean_id}.tlo",
                        'source': 'Teleonline / iptv-org',
                        'page_url': 'https://teleonline.org/',
                        'is_direct': True
                    })
        i += 1
    return channels

def verify_stream(channel):
    url = channel['stream_url']
    try:
        req = urllib.request.Request(url, headers={'User-Agent': HEADERS['User-Agent']})
        with urllib.request.urlopen(req, context=ctx, timeout=3.0) as resp:
            if resp.status == 200:
                return channel
    except Exception:
        pass
    return None

def get_teleonline_channels(limit_verification=150):
    print("[*] Obteniendo canales de Teleonline / iptv-org...")
    raw_channels = []
    
    for src in IPTV_SOURCES:
        try:
            req = urllib.request.Request(src['url'], headers=HEADERS)
            with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
                content = resp.read().decode('utf-8', errors='ignore')
                parsed = parse_m3u_content(content, src['country'])
                print(f" [+] {src['country']} ({src['url']}): {len(parsed)} canales extraídos")
                raw_channels.extend(parsed)
        except Exception as e:
            print(f" [!] Error en {src['url']}: {e}")

    # Remove duplicates by stream_url
    unique_channels = {}
    for c in raw_channels:
        if c['stream_url'] not in unique_channels:
            unique_channels[c['stream_url']] = c
            
    channel_list = list(unique_channels.values())
    print(f"[*] Canales únicos encontrados: {len(channel_list)}. Verificando señales activas (muestra rápida)...")

    # Verify top priority channels (Spain and Colombia first, then others)
    priority = [c for c in channel_list if c['country'] in ['España', 'Colombia']]
    others = [c for c in channel_list if c['country'] not in ['España', 'Colombia']]
    to_verify = (priority + others)[:limit_verification]

    verified = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(verify_stream, c): c for c in to_verify}
        for f in as_completed(futures):
            res = f.result()
            if res:
                verified.append(res)

    print(f"[+] Teleonline: {len(verified)} canales HLS verificados activos.")
    
    with open("teleonline_working.json", "w", encoding="utf-8") as f:
        json.dump(verified, f, indent=2, ensure_ascii=False)
        
    return verified

if __name__ == "__main__":
    chans = get_teleonline_channels(limit_verification=100)
    print(f"Teleonline: {len(chans)} canales activos.")
