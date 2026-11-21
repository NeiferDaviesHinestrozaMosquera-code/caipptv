import os
import json
from fetch_pluto import get_pluto_channels
from fetch_colombia import get_colombia_channels
from fetch_tvporinternet import get_tvporinternet_channels
from fetch_teleonline import get_teleonline_channels
import validate_streams
import generate_m3u

MASTER_JSON = "cxtv_channels.json"
PLAYER_JSON = os.path.join("player", "cxtv_channels.json")

def merge_sources():
    print("=" * 65)
    print("   🌐 ACTUALIZADOR MULTI-FUENTE:")
    print("   CXTv + TVporInternet + Teleonline + Pluto TV + Colombia HD")
    print("=" * 65)

    # 1. Base CXTv channels
    base_channels = []
    if os.path.exists(MASTER_JSON):
        with open(MASTER_JSON, "r", encoding="utf-8") as f:
            base_channels = json.load(f)
    print(f"\n[1/5] Canales base CXTv cargados: {len(base_channels)}")

    # 2. Fetch Colombia HD
    print("\n[2/5] Obteniendo canales nacionales y regionales de Colombia HD...")
    colombia_channels = get_colombia_channels()

    # 3. Fetch TVporInternet (ESPN, Fox Sports, Directv Sports, Star Channel, etc.)
    print("\n[3/5] Obteniendo canales Premium y Deportes de TVporInternet (https://www.tvporinternet.org/)...")
    tvpi_channels = get_tvporinternet_channels()

    # 4. Fetch Teleonline (https://teleonline.org/ / iptv-org)
    print("\n[4/5] Obteniendo canales de Teleonline (https://teleonline.org/)...")
    teleonline_channels = get_teleonline_channels(limit_verification=120)

    # 5. Fetch Pluto TV Latin America
    print("\n[5/5] Obteniendo canales FAST gratuitos de Pluto TV...")
    pluto_channels = get_pluto_channels()

    # Merge strategy:
    # Priority order:
    # 1. Colombia HD
    # 2. TVporInternet (Premium sports & entertainment)
    # 3. Teleonline (Spain / International verified)
    # 4. Pluto TV
    # 5. CXTv existing channels
    channels_dict = {}

    for ch in colombia_channels:
        channels_dict[ch["id"]] = ch

    for ch in tvpi_channels:
        channels_dict[ch["id"]] = ch

    for ch in teleonline_channels:
        channels_dict[ch["id"]] = ch

    for ch in pluto_channels:
        channels_dict[ch["id"]] = ch

    for ch in base_channels:
        cid = ch.get("id")
        if cid and cid not in channels_dict:
            channels_dict[cid] = ch

    merged_list = list(channels_dict.values())
    print(f"\n[+] Total de canales unificados en catálogo: {len(merged_list)}")
    direct_hls = sum(1 for c in merged_list if c.get("stream_type") == "hls")
    print(f"[+] Canales con señal directa HLS (.m3u8): {direct_hls}")

    # Save to root and player directory
    with open(MASTER_JSON, "w", encoding="utf-8") as f:
        json.dump(merged_list, f, ensure_ascii=False, indent=2)

    if os.path.exists("player"):
        with open(PLAYER_JSON, "w", encoding="utf-8") as pf:
            json.dump(merged_list, pf, ensure_ascii=False, indent=2)

    print(f"[+] Archivos JSON actualizados con éxito en raíz y player/.")

    # 6. Stream Health Check on channels
    print("\n[+] Ejecutando validación de señales activas (Health Check)...")
    latam_and_priority = [
        c for c in merged_list 
        if c.get("country") in ["Colombia", "Latinoamérica", "México", "Argentina", "España"] 
        or c.get("id", "").startswith("tvpi-")
        or c.get("id", "").startswith("tlo-")
        or c.get("id", "").startswith("pluto-")
    ]
    validate_streams.validate_all_streams(max_workers=35, target_channels=latam_and_priority)

    # 7. Regenerate all M3U playlists with EPG
    print("\n[+] Regenerando todas las listas M3U con guía EPG y nuevas fuentes integradas...")
    generate_m3u.generate_playlists()

    print("\n" + "=" * 65)
    print("   🎉 MULTI-FUENTE TELEONLINE + TVPORINTERNET INTEGRADA CON ÉXITO")
    print("=" * 65)

if __name__ == "__main__":
    merge_sources()
