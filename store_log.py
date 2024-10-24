import http.server
import socketserver
import urllib.parse

class LogRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        url_parts = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(url_parts.query)
        ip = query.get('ip', [None])[0]
        if ip:
            print(f"Received IP: {ip}")
            with open('log.txt', 'a') as f:
                f.write(ip + '\n')
        self.send_response(200)
        self.end_headers()

PORT = 8001  # You can change this to any unused port

Handler = LogRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("Server started at port", PORT)
    httpd.serve_forever()