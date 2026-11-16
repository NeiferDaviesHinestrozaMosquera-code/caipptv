import os
import sys
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8080

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        # Doesn't actually send packets
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

class IPTVRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS for Smart TV apps and browsers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

    def guess_type(self, path):
        if path.endswith('.m3u') or path.endswith('.m3u8'):
            return 'application/vnd.apple.mpegurl'
        if path.endswith('.json'):
            return 'application/json; charset=utf-8'
        return super().guess_type(path)

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def run_server():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    local_ip = get_local_ip()

    server_address = ('', PORT)
    httpd = HTTPServer(server_address, IPTVRequestHandler)

    print("=" * 65)
    print("       🚀 CXTv IPTV & Media Server - Caixun Whale OS 🚀")
    print("=" * 65)
    print(f"\n[+] Tu PC está listo en la red Wi-Fi.")
    print(f"[+] IP Local de tu PC: {local_ip}")
    print("\n" + "-" * 65)
    print("📺 ENLACES PARA CONFIGURAR EN TU TV CAIXUN (SS IPTV / SMART IPTV):")
    print("-" * 65)
    print(f"  * Lista Caixun Smart TV:  http://{local_ip}:{PORT}/cxtv_caixun_smarttv.m3u")
    print(f"  * Lista Colombia:         http://{local_ip}:{PORT}/cxtv_colombia.m3u")
    print(f"  * Lista Latinoamérica:    http://{local_ip}:{PORT}/cxtv_latam.m3u")
    print(f"  * Lista Todos Canales:    http://{local_ip}:{PORT}/cxtv_todos.m3u")
    print("\n" + "-" * 65)
    print("💻 REPRODUCTOR WEB (Desde PC, Celular o Navegador):")
    print("-" * 65)
    print(f"  * En este PC:             http://localhost:{PORT}/player/")
    print(f"  * Desde otro dispositivo: http://{local_ip}:{PORT}/player/")
    print("=" * 65)
    print("\nPresiona CTRL + C en cualquier momento para detener el servidor.\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
        sys.exit(0)

if __name__ == '__main__':
    run_server()
