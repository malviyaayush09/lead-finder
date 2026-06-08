from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import json
import os

PORT = 5000

class ProxyHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        print(f"  {args[0]} {args[1]}")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors()
        self.end_headers()

    def do_GET(self):
        if self.path == "/":
            self.serve_file("index.html", "text/html")
        elif self.path.startswith("/api/"):
            self.proxy_google()
        else:
            self.send_response(404)
            self.end_headers()

    def serve_file(self, filename, content_type):
        filepath = os.path.join(os.path.dirname(__file__), filename)
        try:
            with open(filepath, "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_cors()
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()

    def proxy_google(self):
        path = self.path[5:]
        endpoint_map = {
            "geocode": "https://maps.googleapis.com/maps/api/geocode/json",
            "nearbysearch": "https://maps.googleapis.com/maps/api/place/nearbysearch/json",
            "details": "https://maps.googleapis.com/maps/api/place/details/json",
        }
        parts = path.split("?", 1)
        endpoint_key = parts[0].rstrip("/")
        query = parts[1] if len(parts) > 1 else ""
        base_url = endpoint_map.get(endpoint_key)
        if not base_url:
            self.send_response(404)
            self.end_headers()
            return
        url = f"{base_url}?{query}"
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = resp.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_cors()
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_cors()
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def send_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

if __name__ == "__main__":
    server = HTTPServer(("localhost", PORT), ProxyHandler)
    print(f"\n  Lead Finder running at http://localhost:{PORT}")
    print("  Press Ctrl+C to stop\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
