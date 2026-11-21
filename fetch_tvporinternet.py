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
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def categorize_slug(slug):
    slug_lower = slug.lower()
    if any(k in slug_lower for k in ['espn', 'fox', 'sport', 'liga', 'tudn', 'tyc', 'campeones']):
        return "Deportes"
    elif any(k in slug_lower for k in ['cine', 'movie', 'tnt', 'star', 'warner', 'axn', 'amc', 'sony', 'universal', 'golden', 'space', 'fx']):
        return "Cine y Series"
    elif any(k in slug_lower for k in ['disney', 'cartoon', 'toon', 'nick', 'infantil']):
        return "Infantil"
    elif any(k in slug_lower for k in ['history', 'discovery', 'geo', 'animal', 'docu']):
        return "Documentales"
    elif any(k in slug_lower for k in ['noticia', 'news', 'cnn']):
        return "Noticias"
    else:
        return "Variedades"

def get_tvporinternet_channels():
    print("[*] Conectando con TVporInternet (https://www.tvporinternet.org/)...")
    
    # 1. Fetch channel directory
    channels = []
    try:
        url = "https://www.tvporinternet.org/"
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            links = re.findall(r'<a[^>]+href=["\']([^"\']+-en-vivo-online\.php)["\'][^>]*>([\s\S]*?)</a>', html)
            for href, inner in links:
                lines = [line.strip() for line in re.sub(r'<[^>]+>', '', inner).splitlines() if line.strip() and line.strip() not in ['EN VIVO', '▶'] and not line.strip().isdigit()]
                name = lines[0] if lines else ""
                img_match = re.search(r'src=["\']([^"\']+)["\']', inner)
                logo = img_match.group(1) if img_match else ""
                if not href.startswith('http'):
                    href = 'https://www.tvporinternet.org/' + href.lstrip('/')
                slug = href.split('/')[-1].replace('-en-vivo-online.php', '')
                if not name:
                    name = slug.replace('-', ' ').title()
                if logo and not logo.startswith('http'):
                    logo = f"https://www.tvporinternet.org/{logo.lstrip('/')}"
                channels.append({
                    'name': name,
                    'slug': slug,
                    'url': href,
                    'logo': logo
                })
    except Exception as e:
        print(f"[!] Error leyendo directorio de TVporInternet: {e}")
        # If network error, try loading from cache if available
        if os.path.exists("tvporinternet_working.json"):
            with open("tvporinternet_working.json", "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    print(f"[*] Directorio obtenido: {len(channels)} canales. Extrayendo señales HLS activas...")

    def resolve_stream(ch):
        slug = ch['slug']
        for core_num in ['live', 'live2', 'live3']:
            core_url = f"https://www.tvporinternet.org/{core_num}/core.php?canal={slug}"
            try:
                req = urllib.request.Request(core_url, headers={**HEADERS, 'Referer': ch['url']})
                with urllib.request.urlopen(req, context=ctx, timeout=3.5) as resp:
                    core_html = resp.read().decode('utf-8', errors='ignore')
                    iframes = re.findall(r'<iframe[^>]+src=[\'"]([^\'"]+)[\'"]', core_html, re.I)
                    if not iframes:
                        continue
                    stream_page = iframes[0].replace('&amp;', '&')
                    
                    req2 = urllib.request.Request(stream_page, headers={**HEADERS, 'Referer': core_url})
                    with urllib.request.urlopen(req2, context=ctx, timeout=3.5) as resp2:
                        stream_html = resp2.read().decode('utf-8', errors='ignore')
                        m3u8_matches = re.findall(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', stream_html.replace('\\/', '/'))
                        if m3u8_matches:
                            cand = m3u8_matches[0]
                            # Verify active stream
                            req3 = urllib.request.Request(cand, headers={**HEADERS, 'Referer': stream_page})
                            with urllib.request.urlopen(req3, context=ctx, timeout=3.5) as resp3:
                                if resp3.status == 200:
                                    category = categorize_slug(slug)
                                    return {
                                        'id': f"tvpi-{slug}",
                                        'name': f"{ch['name']} (TVpI)",
                                        'display_name': ch['name'],
                                        'category': category,
                                        'country': 'Latinoamérica',
                                        'stream_url': cand,
                                        'stream_type': 'hls',
                                        'logo': ch['logo'],
                                        'tvg_id': f"{slug}.tvpi",
                                        'source': 'TVporInternet.org',
                                        'page_url': ch['url'],
                                        'is_direct': True
                                    }
            except Exception:
                continue
        return None

    working_channels = []
    with ThreadPoolExecutor(max_workers=14) as executor:
        futures = {executor.submit(resolve_stream, ch): ch for ch in channels}
        for f in as_completed(futures):
            res = f.result()
            if res:
                working_channels.append(res)

    print(f"[+] TVporInternet: {len(working_channels)} canales HLS directos verificados.")
    
    # Save cache
    with open("tvporinternet_working.json", "w", encoding="utf-8") as f:
        json.dump(working_channels, f, indent=2, ensure_ascii=False)
        
    return working_channels

if __name__ == "__main__":
    chans = get_tvporinternet_channels()
    print(f"Obtenidos {len(chans)} canales.")
