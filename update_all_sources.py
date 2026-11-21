import os
import json
from fetch_pluto import get_pluto_channels
from fetch_colombia import get_colombia_channels
import generate_m3u

MASTER_JSON = "cxtv_channels.json"
PLAYER_JSON = os.path.join("player", "cxtv_channels.json")

def merge_sources():
    print("=" * 60)
    print("   🌐 ACTUALIZADOR MULTI-FUENTE CXTv + PLUTO TV + COLOMBIA HD")
    print("=" * 60)

    # 1. Base CXTv channels
    base_channels = []
    if os.path.exists(MASTER_JSON):
        with open(MASTER_JSON, "r", encoding="utf-8") as f:
            base_channels = json.load(f)
    print(f"\n[1/3] Canales base CXTv cargados: {len(base_channels)}")

    # 2. Fetch Colombia HD
    print("\n[2/3] Obteniendo canales nacionales y regionales de Colombia HD...")
    colombia_channels = get_colombia_channels()

    # 3. Fetch Pluto TV Latin America
    print("\n[3/3] Obteniendo canales FAST gratuitos de Pluto TV...")
    pluto_channels = get_pluto_channels()

    # Merge strategy:
    # Top priority: Colombia HD channels
    # Next: CXTv existing channels (excluding any duplicated ids)
    # Next: Pluto TV channels
    channels_dict = {}

    # Add Colombia channels first
    for ch in colombia_channels:
        channels_dict[ch["id"]] = ch

    # Add CXTv channels (if not already added)
    for ch in base_channels:
        cid = ch.get("id")
        if cid and cid not in channels_dict:
            channels_dict[cid] = ch

    # Add Pluto channels
    for ch in pluto_channels:
        cid = ch.get("id")
        if cid and cid not in channels_dict:
            channels_dict[cid] = ch

    merged_list = list(channels_dict.values())
    print(f"\n[+] Total de canales unificados: {len(merged_list)}")
    direct_hls = sum(1 for c in merged_list if c.get("stream_type") == "hls")
    print(f"[+] Canales con señal directa HLS (.m3u8): {direct_hls}")

    # Save to root and player directory
    with open(MASTER_JSON, "w", encoding="utf-8") as f:
        json.dump(merged_list, f, ensure_ascii=False, indent=2)

    if os.path.exists("player"):
        with open(PLAYER_JSON, "w", encoding="utf-8") as pf:
            json.dump(merged_list, pf, ensure_ascii=False, indent=2)

    print(f"\n[+] Archivos JSON actualizados con éxito.")

    # 4. Regenerate all M3U playlists
    print("\n[+] Regenerando todas las listas M3U / M3U8...")
    generate_m3u.generate_playlists()

    print("\n" + "=" * 60)
    print("   🎉 MULTI-FUENTE INTEGRADA CON ÉXITO")
    print("=" * 60)

if __name__ == "__main__":
    merge_sources()
