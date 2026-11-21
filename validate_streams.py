import os
import json
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

JSON_FILE = "cxtv_channels.json"
PLAYER_JSON = os.path.join("player", "cxtv_channels.json")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

def check_single_stream(channel):
    url = channel.get("stream_url", "").strip()
    if not url or channel.get("stream_type") not in ["hls", "direct"]:
        # Keep web/youtube or uncheckable streams as is
        channel["is_active"] = bool(url)
        return channel

    try:
        # Step 1: Fast HEAD request
        r = requests.head(url, headers=HEADERS, timeout=4, allow_redirects=True)
        if r.status_code in [200, 206, 302]:
            channel["is_active"] = True
            return channel
        
        # Step 2: Fallback GET with stream=True (read only first chunk)
        r = requests.get(url, headers=HEADERS, timeout=4, stream=True)
        if r.status_code in [200, 206]:
            channel["is_active"] = True
            return channel
    except Exception:
        pass

    channel["is_active"] = False
    return channel

def validate_all_streams(max_workers=35, target_channels=None):
    print("=" * 60)
    print("   ⚡ VALIDADOR DE SEÑALES STREAM HEALTH CHECK")
    print("=" * 60)

    if not os.path.exists(JSON_FILE):
        print(f"Error: {JSON_FILE} no encontrado.")
        return []

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        channels = json.load(f)

    to_test = target_channels if target_channels else channels
    hls_channels = [c for c in to_test if c.get("stream_type") == "hls" and c.get("stream_url")]
    print(f"\n[+] Total de canales a verificar: {len(hls_channels)} (concurrencia: {max_workers})")

    active_count = 0
    inactive_count = 0
    start_time = time.time()

    validated_results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_single_stream, c): c for c in hls_channels}
        done_count = 0
        for f in as_completed(futures):
            res = f.result()
            validated_results.append(res)
            done_count += 1
            if res.get("is_active"):
                active_count += 1
            else:
                inactive_count += 1

            if done_count % 200 == 0 or done_count == len(hls_channels):
                elapsed = time.time() - start_time
                print(f"  Progreso: {done_count}/{len(hls_channels)} ({done_count/len(hls_channels)*100:.1f}%) | "
                      f"Activos: {active_count} | Caídos: {inactive_count} | Tiempo: {elapsed:.1f}s")

    # Update map
    validated_map = {c["id"]: c.get("is_active", False) for c in validated_results}
    for c in channels:
        if c.get("id") in validated_map:
            c["is_active"] = validated_map[c["id"]]

    # Save results
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(channels, f, ensure_ascii=False, indent=2)

    if os.path.exists("player"):
        with open(PLAYER_JSON, "w", encoding="utf-8") as pf:
            json.dump(channels, pf, ensure_ascii=False, indent=2)

    total_active = sum(1 for c in channels if c.get("is_active", False))
    print(f"\n[+] Verificación finalizada: {total_active} canales activos comprobados.")
    print("=" * 60)
    return channels

if __name__ == "__main__":
    validate_all_streams()
