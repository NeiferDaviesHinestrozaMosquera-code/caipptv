import os
import sys
import socket
import urllib.request
import urllib.parse
import re
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8080

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

class IPTVRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS')
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

    def do_GET(self):
        # Handle /proxy?url=
        if self.path.startswith('/proxy?') or self.path.startswith('/proxy/'):
            parsed = urllib.parse.urlparse(self.path)
            qs = urllib.parse.parse_qs(parsed.query)
            target_url = qs.get('url', [''])[0]
            if not target_url:
                self.send_error(400, "Missing 'url' parameter")
                return

            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                    'Referer': 'https://pluto.tv/'
                }
                req = urllib.request.Request(target_url, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    content = resp.read()
                    content_type = resp.headers.get('Content-Type', '')

                    # If m3u8 playlist, rewrite internal sub-manifest links
                    if 'mpegurl' in content_type or '.m3u8' in target_url:
                        text = content.decode('utf-8', errors='ignore')
                        target_base = target_url.rsplit('/', 1)[0] + '/'
                        proxy_base = f"http://{self.headers.get('Host', f'localhost:{PORT}')}/proxy"

                        lines = text.splitlines()
                        new_lines = []
                        for line in lines:
                            s = line.strip()
                            if not s:
                                new_lines.append(line)
                                continue
                            if s.startswith('#'):
                                if 'URI="' in s:
                                    def replace_uri(m):
                                        u = m.group(1)
                                        full = u if u.startswith('http') else urllib.parse.urljoin(target_base, u)
                                        return f'URI="{proxy_base}?url={urllib.parse.quote(full)}"'
                                    line = re.sub(r'URI="([^"]+)"', replace_uri, s)
                                new_lines.append(line)
                            else:
                                full = s if s.startswith('http') else urllib.parse.urljoin(target_base, s)
                                if '.m3u8' in full:
                                    new_lines.append(f"{proxy_base}?url={urllib.parse.quote(full)}")
                                else:
                                    new_lines.append(full)

                        output = "\n".join(new_lines).encode('utf-8')
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/vnd.apple.mpegurl')
                        self.send_header('Content-Length', str(len(output)))
                        self.end_headers()
                        self.wfile.write(output)
                        return
                    else:
                        self.send_response(resp.status)
                        self.send_header('Content-Type', content_type)
                        self.send_header('Content-Length', str(len(content)))
                        self.end_headers()
                        self.wfile.write(content)
                        return
            except Exception as e:
                self.send_error(502, f"Proxy Error: {e}")
                return

        return super().do_GET()

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
    print(f"  * Lista Master VLC:       http://{local_ip}:{PORT}/cxtv_master_vlc.m3u")
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

if __name__ == "__main__":
    run_server()
