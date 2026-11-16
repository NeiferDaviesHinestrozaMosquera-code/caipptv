import os
import shutil
import string
import ctypes

def get_removable_drives():
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drive_path = f"{letter}:\\"
            drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive_path)
            # DRIVE_REMOVABLE = 2
            if drive_type == 2:
                drives.append(f"{letter}:")
        bitmask >>= 1
    return drives

def main():
    print("=" * 60)
    print("   💾 COPIADOR DE CANALES IPTV A MEMORIA USB (CAIXUN TV)")
    print("=" * 60)

    drives = get_removable_drives()
    target_drive = ""

    if drives:
        print(f"\n[+] Se detectó(aron) la(s) siguiente(s) memoria(s) USB:")
        for idx, d in enumerate(drives):
            print(f"    [{idx + 1}] Unidad {d}")
        
        choice = input(f"\nSelecciona el número de la memoria USB [1-{len(drives)}] (o escribe la letra ej. E:): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(drives):
            target_drive = drives[int(choice) - 1]
        elif len(choice) >= 1 and choice[0].upper() in string.ascii_uppercase:
            target_drive = f"{choice[0].upper()}:"
        else:
            target_drive = drives[0]
    else:
        print("\n[!] No se detectó automáticamente ninguna memoria USB extraíble.")
        custom = input("Por favor ingresa la letra de tu memoria USB (ejemplo: E, F o D): ").strip().upper()
        if custom:
            target_drive = f"{custom[0]}:"
        else:
            print("Operación cancelada.")
            return

    target_dir = os.path.join(target_drive, "\\", "IPTV_CAIXUN")
    os.makedirs(target_dir, exist_ok=True)
    print(f"\nCopiando archivos IPTV a: {target_dir} ...\n")

    files_to_copy = [
        "cxtv_caixun_smarttv.m3u",
        "cxtv_colombia.m3u",
        "cxtv_latam.m3u",
        "cxtv_todos.m3u",
        "cxtv_channels.json"
    ]

    copied = 0
    for f in files_to_copy:
        if os.path.exists(f):
            dest = os.path.join(target_dir, f)
            shutil.copy2(f, dest)
            # Also copy to root of USB for maximum compatibility with TV media players
            root_dest = os.path.join(target_drive, "\\", f)
            shutil.copy2(f, root_dest)
            print(f" [OK] {f} -> {target_drive}\\ y {target_dir}\\")
            copied += 1
        else:
            print(f" [!] {f} no encontrado en la carpeta actual.")

    # Also copy web player
    player_src = "player"
    player_dst = os.path.join(target_dir, "player")
    if os.path.exists(player_src):
        if os.path.exists(player_dst):
            shutil.rmtree(player_dst)
        shutil.copytree(player_src, player_dst)
        print(f" [OK] Carpeta player/ -> {player_dst}")

    # Create README on USB
    readme_path = os.path.join(target_drive, "\\", "LEEME_CAIXUN_WHALE_OS.txt")
    with open(readme_path, "w", encoding="utf-8") as rf:
        rf.write("""============================================================
CANALES IPTV CXTV PARA TU SMART TV CAIXUN (WHALE OS)
============================================================

Archivos listos en esta memoria USB:
1. cxtv_caixun_smarttv.m3u -> Lista recomendada y optimizada para Smart TV Caixun
2. cxtv_colombia.m3u        -> Canales exclusivos de Colombia
3. cxtv_latam.m3u           -> Canales en español (Colombia, México, Argentina, etc.)
4. cxtv_todos.m3u           -> Todos los canales mundiales con señal directa HLS

COMO USAR EN TU TV CAIXUN:
------------------------------------------------------------
MÉTODO 1: Por la App SS IPTV (Recomendado para Whale OS)
1. En tu TV Caixun abre la tienda "Whale Store" o "App Store".
2. Busca e instala "SS IPTV".
3. Abre SS IPTV en el TV, ve a la tuerca de "Configuración" y pulsa "Obtener código" (Get code).
4. En tu computador abre: https://ss-iptv.com/es/users/playlist
5. Introduce el código de tu TV y pulsa "Añadir dispositivo".
6. Ve a "Listas de reproducción externas", pulsa "Añadir elemento", selecciona el archivo "cxtv_caixun_smarttv.m3u" de esta USB y guarda.
7. ¡Regresa a tu TV Caixun y los canales aparecerán listos para ver!

MÉTODO 2: Reproductor de Medios por USB
1. Conecta esta USB en el puerto USB de tu TV Caixun.
2. Entra en "Media" / "Reproductor de Medios" / "Video".
3. Navega y selecciona el archivo de lista .m3u o los canales de la carpeta IPTV_CAIXUN.
============================================================
""")
    print(f" [OK] Creado archivo de instrucciones: {readme_path}")
    print("\n" + "=" * 60)
    print(" ¡LISTO! Tu memoria USB ya tiene todos los canales preparados.")
    print("=" * 60)

if __name__ == "__main__":
    main()
