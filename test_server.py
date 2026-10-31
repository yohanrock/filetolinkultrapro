#!/usr/bin/env python3
"""
Direct Local Test Server for filetolinkultrapro
------------------------------------------------
Runs a lightweight local web server to test webav.html in your browser immediately,
without requiring Telegram bot tokens or MongoDB.

Usage:
    python test_server.py
Then open http://localhost:8080 in your browser!
"""

import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

PORT = 8080
TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web", "template", "webav.html")

# Sample test video with multi-audio & subtitles support
DEFAULT_VIDEO = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
SAMPLE_MKV = "https://ia800201.us.archive.org/12/items/BigBuckBunny_328/BigBuckBunny_512kb.mp4"

class TestPlayerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)

        # Allow user to specify custom video via ?url=...
        video_url = qs.get("url", [DEFAULT_VIDEO])[0]
        file_name = qs.get("name", ["Big_Buck_Bunny_1080p_MultiAudio.mkv"])[0]

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
            "{{file_size}}": "1.05 GB",
            "{{file_unique_id}}": "test_unique_id_12345",
            "{{template_ne}}": "Infinity Movies",
            "{{disclaimer}}": "This is a direct local preview test of the filetolinkultrapro video player.",
            "{{report_link}}": "https://github.com/yohanrock/filetolinkultrapro",
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
        # Clean logging
        print(f"[{self.log_date_time_string()}] {args[0]}")

def run():
    server = HTTPServer(("0.0.0.0", PORT), TestPlayerHandler)
    print("=" * 60)
    print("Direct Player Test Server running at:")
    print(f"   * http://localhost:{PORT}")
    print(f"   * http://127.0.0.1:{PORT}")
    print("=" * 60)
    print("Press Ctrl+C to stop the server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.server_close()

if __name__ == "__main__":
    run()
