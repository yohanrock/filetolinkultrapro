#!/usr/bin/env python3
"""
Direct Local Test Server for filetolinkultrapro
------------------------------------------------
Runs a lightweight local web server to test webav.html in your browser immediately,
with any direct stream link.

Usage:
    python test_server.py
    python test_server.py "<direct_stream_url>"
    python test_server.py --url "<direct_stream_url>" --name "MyMovie.mkv"
    python test_server.py --open
"""

import os
import sys
import socket
import webbrowser
import argparse
import urllib.parse
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

# Ensure UTF-8 output on Windows console without crashes
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PORT = 8080
TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web", "template", "webav.html")

# Default video link
DEFAULT_VIDEO = "https://pro-rockstar.mummy16.workers.dev/1527?hash=AgADOC"
DEFAULT_NAME = "@Infinity_Movies2 Baththa.2026.720p.NF.WEB-DL.Telugu.AAC.mkv"

ACTIVE_VIDEO = DEFAULT_VIDEO
ACTIVE_NAME = DEFAULT_NAME
ACTIVE_SIZE = "885.8 MB"

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def probe_stream_metadata(url):
    name = None
    size_str = "Unknown"
    try:
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req, timeout=6) as r:
            cd = r.headers.get('Content-Disposition', '')
            cl = r.headers.get('Content-Length')
            if cd:
                for part in cd.split(';'):
                    part = part.strip()
                    if part.lower().startswith('filename='):
                        raw = part.split('=', 1)[1].strip('"\' ')
                        name = urllib.parse.unquote(raw)
                    elif part.lower().startswith("filename*="):
                        raw = part.split('=', 1)[1].strip('"\' ')
                        if "''" in raw:
                            raw = raw.split("''", 1)[1]
                        name = urllib.parse.unquote(raw)
            if cl and cl.isdigit():
                b = int(cl)
                if b >= 1024**3:
                    size_str = f"{b / (1024**3):.2f} GB"
                else:
                    size_str = f"{b / (1024**2):.1f} MB"
    except Exception:
        pass

    if not name:
        clean_url = url.split('?')[0]
        base = clean_url.rstrip('/').split('/')[-1]
        name = urllib.parse.unquote(base) if base else "video.mp4"
    return name, size_str

class TestPlayerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)

        # Allow user to specify custom video via ?url=... or fallback to active video
        video_url = qs.get("url", [ACTIVE_VIDEO])[0]
        
        # If user passed custom url in query param, check if name was also passed
        if video_url != ACTIVE_VIDEO:
            file_name = qs.get("name", [None])[0]
            if not file_name:
                file_name, file_size = probe_stream_metadata(video_url)
            else:
                file_size = "Unknown"
        else:
            file_name = qs.get("name", [ACTIVE_NAME])[0]
            file_size = ACTIVE_SIZE

        if not os.path.exists(TEMPLATE_PATH):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Error: web/template/webav.html not found.")
            return

        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        # Mock Jinja template replacements for local testing
        replacements = {
            "{{file_name}}": file_name,
            "{{file_url}}": video_url,
            "{{file_size}}": file_size,
            "{{file_unique_id}}": "test_unique_id_12345",
            "{{template_ne}}": "Infinity Movies",
            "{{disclaimer}}": "Direct terminal preview test of filetolinkultrapro.",
            "{{report_link}}": "https://github.com/rockstaryohan/filetolinkultrapro",
            "{{tg_button}}": "https://t.me/Infinity_movies_updates",
            "{{ colours.header.background }}": "#48cffe",
            "{{ colours.header.color }}": "#ffffff",
            "{{ colours.create_link.background }}": "#ffd700",
            "{{ colours.create_link.color }}": "#000000",
            "{{ colours.share.background }}": "#ff1744",
            "{{ colours.share.color }}": "#ffffff",
            "{{ colours.file_information.background }}": "#292b2c",
            "{{ colours.file_information.color }}": "#ffffff",
            "{{ colours.description.background }}": "#fff2c8",
            "{{ colours.description.color }}": "#6c4c00",
        }

        for k, v in replacements.items():
            content = content.replace(k, str(v))

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))

    def log_message(self, format, *args):
        try:
            msg = str(args[0]) if args else ''
            print(f"[{self.log_date_time_string()}] {msg}")
        except Exception:
            pass

def main():
    global ACTIVE_VIDEO, ACTIVE_NAME, ACTIVE_SIZE

    parser = argparse.ArgumentParser(description="Direct Test Player Server")
    parser.add_argument("url", nargs="?", default=None, help="Direct video stream link to test")
    parser.add_argument("--url", dest="opt_url", default=None, help="Direct video stream link to test")
    parser.add_argument("--name", dest="name", default=None, help="Custom file name display")
    parser.add_argument("--port", type=int, default=PORT, help="Server port (default: 8080)")
    parser.add_argument("--open", action="store_true", default=False, help="Automatically open browser")
    args = parser.parse_args()

    target_url = args.url or args.opt_url
    if target_url:
        ACTIVE_VIDEO = target_url
        print(f"Probing stream metadata for: {ACTIVE_VIDEO} ...")
        detected_name, detected_size = probe_stream_metadata(ACTIVE_VIDEO)
        ACTIVE_NAME = args.name or detected_name
        ACTIVE_SIZE = detected_size

    local_ip = get_local_ip()
    port = args.port

    server = HTTPServer(("0.0.0.0", port), TestPlayerHandler)

    print("=" * 68)
    print("  FILETOLINKULTRAPRO - DIRECT PLAYER TEST SERVER")
    print("=" * 68)
    print(f"  * Active File : {ACTIVE_NAME}")
    print(f"  * File Size   : {ACTIVE_SIZE}")
    print(f"  * Stream URL  : {ACTIVE_VIDEO}")
    print("-" * 68)
    print("  DIRECT TEST LINKS:")
    print(f"  * PC / Desktop:   http://localhost:{port}")
    print(f"  * Local Network:  http://127.0.0.1:{port}")
    print(f"  * Mobile (Wi-Fi): http://{local_ip}:{port}")
    print("-" * 68)
    print("  TEST ANY OTHER DIRECT LINK DYNAMICALLY:")
    print(f"  * In browser: http://localhost:{port}/?url=<DIRECT_VIDEO_URL>")
    print(f"  * In terminal: python test_server.py \"<DIRECT_VIDEO_URL>\"")
    print("=" * 68)
    print("Press Ctrl+C to stop the server.")

    if args.open:
        try:
            webbrowser.open(f"http://localhost:{port}")
        except Exception:
            pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.server_close()

if __name__ == "__main__":
    main()
