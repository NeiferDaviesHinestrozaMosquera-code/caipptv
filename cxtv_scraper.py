import os
import re
import json
import time
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

SITEMAP_FILE = "sitemap.xml"
OUTPUT_JSON = "cxtv_channels.json"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

def load_sitemap_urls():
    if not os.path.exists(SITEMAP_FILE):
        print(f"Error: {SITEMAP_FILE} not found.")
        return []
    with open(SITEMAP_FILE, "r", encoding="utf-8") as f:
        text = f.read()
    urls = re.findall(r'<loc>(https?://[^<]+)</loc>', text)
    channel_urls = [u for u in urls if '/tv-en-vivo/' in u]
    return list(dict.fromkeys(channel_urls))

def scrape_single_channel(url, session):
    try:
        resp = session.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, 'html.parser')

        # 1. Channel Name
        h1 = soup.find('h1')
        raw_name = h1.get_text(strip=True) if h1 else url.split('/')[-1].replace('-', ' ').title()
        clean_name = re.sub(r'\s+en vivo$', '', raw_name, flags=re.I).strip()

        # 2. Logo
        logo = ""
        img = soup.select_one('.cxp-hd .lg img')
        if img:
            logo = img.get('src') or ''
        if not logo:
            meta_img = soup.find('meta', property='og:image')
            if meta_img:
                logo = meta_img.get('content') or ''

        # 3. Country (from nav.mig)
        country = "Internacional"
        mig = soup.select_one('nav.mig')
        if mig:
            p_link = mig.select_one('a[href*="/tv/paises/"]')
            if p_link:
                country = p_link.get_text(strip=True)

        # 4. Categories (from .cxp-tags)
        categories = []
        for a in soup.select('.cxp-tags a[href*="/tv/categorias/"]'):
            c_text = a.get_text(strip=True)
            if c_text and c_text not in categories:
                categories.append(c_text)
        category_str = ";".join(categories) if categories else "General"

        # 5. Stream extraction
        stream_type = "none"
        stream_url = ""

        # Priority A: <video data-stream-url="...">
        video = soup.find('video')
        if video and video.get('data-stream-url'):
            stream_url = video['data-stream-url'].strip()
            stream_type = "hls"
        
        # Priority B: m3u8 inside HTML
        if not stream_url:
            m3u8_matches = re.findall(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', resp.text)
            for m in m3u8_matches:
                if not any(bad in m.lower() for bad in ['schema', 'w3.org', 'videojs']):
                    stream_url = m.strip()
                    stream_type = "hls"
                    break

        # Priority C: Iframe player (YouTube, Livepush, Dailymotion, etc.)
        if not stream_url:
            iframe = soup.find('iframe')
            if iframe:
                src = iframe.get('src') or iframe.get('data-src') or ''
                if src:
                    stream_url = src.strip()
                    if 'youtube.com' in src or 'youtu.be' in src:
                        stream_type = "youtube"
                    else:
                        stream_type = "iframe"

        # Priority D: External player link
        if not stream_url:
            ext = soup.select_one('.cxp-player a.openPlayer')
            if ext and ext.get('href'):
                stream_url = ext['href'].strip()
                stream_type = "external"

        return {
            'id': url.split('/')[-1],
            'name': clean_name,
            'country': country,
            'categories': categories,
            'group': f"{country};{categories[0]}" if categories else country,
            'logo': logo,
            'stream_url': stream_url,
            'stream_type': stream_type,
            'cxtv_url': url
        }
    except Exception as e:
        return None

def main():
    urls = load_sitemap_urls()
    print(f"Loaded {len(urls)} channels from sitemap.")

    # Load existing if available
    channels_db = {}
    if os.path.exists(OUTPUT_JSON):
        try:
            with open(OUTPUT_JSON, 'r', encoding='utf-8') as f:
                data = json.load(f)
                channels_db = {c['id']: c for c in data if 'id' in c}
                print(f"Found {len(channels_db)} previously scraped channels.")
        except Exception:
            pass

    to_scrape = [u for u in urls if u.split('/')[-1] not in channels_db]
    print(f"Channels remaining to scrape: {len(to_scrape)}")

    session = requests.Session()
    # Configure adapter with pool
    adapter = requests.adapters.HTTPAdapter(pool_connections=35, pool_maxsize=35, max_retries=1)
    session.mount('https://', adapter)
    session.mount('http://', adapter)

    start_time = time.time()
    count = 0
    direct_hls_count = sum(1 for c in channels_db.values() if c.get('stream_type') == 'hls')

    with ThreadPoolExecutor(max_workers=30) as executor:
        future_to_url = {executor.submit(scrape_single_channel, u, session): u for u in to_scrape}
        for future in as_completed(future_to_url):
            res = future.result()
            count += 1
            if res:
                channels_db[res['id']] = res
                if res['stream_type'] == 'hls':
                    direct_hls_count += 1

            if count % 100 == 0 or count == len(to_scrape):
                elapsed = time.time() - start_time
                print(f"Progress: {count}/{len(to_scrape)} ({count/len(to_scrape)*100:.1f}%) | "
                      f"Total in DB: {len(channels_db)} | Direct HLS: {direct_hls_count} | Time: {elapsed:.1f}s")
                # Save checkpoint
                with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
                    json.dump(list(channels_db.values()), f, ensure_ascii=False, indent=2)

    # Final save
    all_channels = list(channels_db.values())
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(all_channels, f, ensure_ascii=False, indent=2)

    print(f"\nDone! Scraped {len(all_channels)} total channels. Direct HLS: {direct_hls_count}")

if __name__ == "__main__":
    main()
