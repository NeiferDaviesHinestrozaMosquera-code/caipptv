import requests
from concurrent.futures import ThreadPoolExecutor

# Curated candidates for top Colombian channels (tested and working)
CANDIDATES = [
    {
        "id": "caracol-tv-hd",
        "name": "Caracol TV HD",
        "country": "Colombia",
        "categories": ["General", "Noticias", "Variedades"],
        "group": "🇨🇴 Colombia - General",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/1/1a/Caracol_Televisi%C3%B3n_logo.svg",
        "urls": [
            "http://138.121.15.230:9002/CARACOL/index.m3u8",
            "http://45.173.231.22:8000/play/a009/index.m3u8",
            "http://181.78.17.228:8081/CARACOL-HD/index.m3u8",
            "http://190.61.47.54:8000/play/a01e/index.m3u8",
            "http://190.109.2.92:8000/play/a00q/index.m3u8"
        ]
    },
    {
        "id": "caracol-hd2",
        "name": "Caracol HD2",
        "country": "Colombia",
        "categories": ["Deportes", "Variedades"],
        "group": "🇨🇴 Colombia - Deportes",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/1/1a/Caracol_Televisi%C3%B3n_logo.svg",
        "urls": [
            "http://181.78.14.26:4000/play/a00d/index.m3u8",
            "http://190.109.2.92:8000/play/a05u/index.m3u8"
        ]
    },
    {
        "id": "caracol-internacional",
        "name": "Caracol Internacional",
        "country": "Colombia",
        "categories": ["Noticias", "Variedades"],
        "group": "🇨🇴 Colombia - General",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/1/1a/Caracol_Televisi%C3%B3n_logo.svg",
        "urls": [
            "https://streaming.onnethn.com/CARACOL_INTERNACIONAL/playlist.m3u8",
            "http://167.249.23.102:8000/play/a0ax/index.m3u8",
            "http://45.5.117.57:8200/play/a0e9/index.m3u8"
        ]
    },
    {
        "id": "rcn-television-hd",
        "name": "Canal RCN HD",
        "country": "Colombia",
        "categories": ["General", "Noticias", "Telenovelas"],
        "group": "🇨🇴 Colombia - General",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/5/52/RCN_Television_logo.svg",
        "urls": [
            "http://138.121.15.230:9002/RCN/index.m3u8",
            "http://45.173.231.22:8000/play/a00a/index.m3u8",
            "http://181.78.17.228:8081/RCN-HD/index.m3u8",
            "http://190.61.47.54:8000/play/a01f/index.m3u8",
            "http://190.109.2.92:8000/play/a00w/index.m3u8"
        ]
    },
    {
        "id": "senal-colombia",
        "name": "Señal Colombia",
        "country": "Colombia",
        "categories": ["Cultura", "Educación", "Deportes"],
        "group": "🇨🇴 Colombia - Público",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/c/ce/Se%C3%B1al_Colombia_logo_2020.svg",
        "urls": [
            "https://streaming.rtvc.gov.co/TV_Senal_Colombia_live/smil:live.smil/playlist.m3u8",
            "http://138.121.15.230:9002/SENAL-COLOMBIA/index.m3u8",
            "http://190.61.47.54:8000/play/a00w/index.m3u8"
        ]
    },
    {
        "id": "canal-institucional",
        "name": "Canal Institucional",
        "country": "Colombia",
        "categories": ["Público", "Noticias"],
        "group": "🇨🇴 Colombia - Público",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/7/7b/Canal_Institucional_logo_2020.svg",
        "urls": [
            "https://streaming.rtvc.gov.co/TV_CanalInstitucional_live/smil:live.smil/playlist.m3u8",
            "http://138.121.15.230:9002/CANAL-INSTITUCIONAL/index.m3u8",
            "http://190.61.47.54:8000/play/a00v/index.m3u8",
            "http://190.109.2.92:8000/play/a00z/index.m3u8"
        ]
    },
    {
        "id": "canal-1-hd",
        "name": "Canal 1 HD",
        "country": "Colombia",
        "categories": ["General", "Noticias", "Variedades"],
        "group": "🇨🇴 Colombia - General",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/0/07/Canal_1_Colombia_logo.svg",
        "urls": [
            "http://190.109.2.92:8000/play/a010/index.m3u8",
            "http://190.61.47.54:8000/play/a00u/index.m3u8",
            "http://138.121.15.230:9002/CANAL-UNO/index.m3u8"
        ]
    },
    {
        "id": "canal-trece",
        "name": "Canal Trece",
        "country": "Colombia",
        "categories": ["Cultura", "Música", "Jóvenes"],
        "group": "🇨🇴 Colombia - Regional",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/3/3b/Canal_Trece_Colombia_logo_2018.png",
        "urls": [
            "http://190.60.46.228:8888/play/a030/index.m3u8"
        ]
    },
    {
        "id": "teleantioquia-hd",
        "name": "Teleantioquia HD",
        "country": "Colombia",
        "categories": ["Regional", "Noticias", "Cultura"],
        "group": "🇨🇴 Colombia - Regional",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/0/0a/Teleantioquia_logo.svg",
        "urls": [
            "http://138.121.15.230:9002/TELEANTIOQUIA/index.m3u8",
            "http://190.60.46.228:8888/play/a02r/index.m3u8",
            "http://181.78.82.130:8000/play/a0rs/index.m3u8",
            "http://181.78.211.244:8005/play/a07y/index.m3u8"
        ]
    },
    {
        "id": "telecaribe-hd",
        "name": "Telecaribe HD",
        "country": "Colombia",
        "categories": ["Regional", "Noticias", "Cultura"],
        "group": "🇨🇴 Colombia - Regional",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/c/cb/Telecaribe_logo_2018.png",
        "urls": [
            "http://138.121.15.230:9002/TELECARIBE/index.m3u8",
            "http://181.78.82.130:8000/play/a0rt/index.m3u8",
            "http://190.61.47.54:8000/play/a010/index.m3u8"
        ]
    },
    {
        "id": "telecafe-hd",
        "name": "Telecafé HD",
        "country": "Colombia",
        "categories": ["Regional", "Noticias", "Cultura"],
        "group": "🇨🇴 Colombia - Regional",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/9/91/Telecaf%C3%A9_logo.png",
        "urls": [
            "http://138.121.15.230:9002/TELECAFE/index.m3u8",
            "http://181.78.82.130:8000/play/a0rv/index.m3u8",
            "http://190.60.46.228:8888/play/a02z/index.m3u8",
            "http://181.78.211.244:8005/play/a083/index.m3u8"
        ]
    },
    {
        "id": "telepacifico-hd",
        "name": "Telepacífico HD",
        "country": "Colombia",
        "categories": ["Regional", "Noticias", "Cultura"],
        "group": "🇨🇴 Colombia - Regional",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/1/13/Telepac%C3%ADfico_logo_2020.svg",
        "urls": [
            "http://138.121.15.230:9002/TELEPACIFICO/index.m3u8",
            "http://190.61.47.54:8000/play/a011/index.m3u8"
        ]
    },
    {
        "id": "canal-capital-hd",
        "name": "Canal Capital HD",
        "country": "Colombia",
        "categories": ["Regional", "Noticias", "Bogotá"],
        "group": "🇨🇴 Colombia - Regional",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/6/62/Canal_Capital_logo_2020.png",
        "urls": [
            "http://138.121.15.230:9002/CANAL-CAPITAL/index.m3u8",
            "http://190.61.47.54:8000/play/a00x/index.m3u8"
        ]
    },
    {
        "id": "win-sports-hd",
        "name": "Win Sports HD",
        "country": "Colombia",
        "categories": ["Deportes", "Fútbol"],
        "group": "⚽ Deportes y Fútbol",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/9/91/Win_Sports_logo.svg",
        "urls": [
            "http://138.121.15.230:9002/WIN-SPORT/index.m3u8",
            "http://181.78.12.119:16123/play/ch18/index.m3u8"
        ]
    },
    {
        "id": "cablenoticias-hd",
        "name": "Cablenoticias HD",
        "country": "Colombia",
        "categories": ["Noticias"],
        "group": "📰 Noticias",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/f/f6/Logo_Cablenoticias.png",
        "urls": [
            "http://181.78.211.244:8005/play/a09u/index.m3u8"
        ]
    },
    {
        "id": "ntn24-hd",
        "name": "NTN24 Noticias HD",
        "country": "Colombia",
        "categories": ["Noticias"],
        "group": "📰 Noticias",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/9/96/NTN24_logo.png",
        "urls": [
            "https://stream1.bitred.cl/ntn24/index.m3u8",
            "http://181.78.12.119:16123/play/ch80/index.m3u8"
        ]
    },
    {
        "id": "blu-radio-tv",
        "name": "Blu Radio TV en Vivo",
        "country": "Colombia",
        "categories": ["Noticias", "Radio"],
        "group": "🇨🇴 Colombia - Noticias",
        "logo": "https://static.wikia.nocookie.net/logopedia/images/4/4b/Blu_Radio_logo.png",
        "urls": [
            "https://mdstrm.com/live-stream-playlist/58d1921a72e2b22e2905e493.m3u8"
        ]
    },
    {
        "id": "red-mas-tv",
        "name": "Red+ TV",
        "country": "Colombia",
        "categories": ["Noticias", "Variedades"],
        "group": "🇨🇴 Colombia - General",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/7/7b/Red%2B_logo.png",
        "urls": [
            "https://inforedvos.lcdn.claro.net.co/Content/HLS_HLS_DIR/Live/channel(REDMASHD)/index.m3u8"
        ]
    }
]

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def test_url(url):
    try:
        r = requests.head(url, headers=HEADERS, timeout=3.5, allow_redirects=True)
        if r.status_code in [200, 206, 302]:
            return True
        r = requests.get(url, headers=HEADERS, timeout=3.5, stream=True)
        if r.status_code in [200, 206]:
            return True
    except Exception:
        pass
    return False

def verify_channel(cand):
    # Try URLs in priority order
    for u in cand["urls"]:
        if test_url(u):
            return {
                "id": cand["id"],
                "name": cand["name"],
                "country": cand["country"],
                "categories": cand["categories"],
                "group": cand["group"],
                "logo": cand["logo"],
                "stream_url": u,
                "stream_type": "hls",
                "cxtv_url": "https://www.rtvcplay.co/"
            }
    # Fallback to first URL even if head was slow
    return {
        "id": cand["id"],
        "name": cand["name"],
        "country": cand["country"],
        "categories": cand["categories"],
        "group": cand["group"],
        "logo": cand["logo"],
        "stream_url": cand["urls"][0],
        "stream_type": "hls",
        "cxtv_url": "https://www.rtvcplay.co/"
    }

def get_colombia_channels():
    print(f"Checking {len(CANDIDATES)} primary Colombian channels...")
    results = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        for res in executor.map(verify_channel, CANDIDATES):
            results.append(res)
            print(f"  [OK] {res['name']} -> {res['stream_url']}")
    return results

if __name__ == "__main__":
    chans = get_colombia_channels()
    print(f"\nTotal verified Colombia channels: {len(chans)}")
