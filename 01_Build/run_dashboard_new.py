import http.server
import socketserver
import os

PORT = 8508

os.chdir(r'd:\0_trea_projects_by_bela\price_dashboard\01_Build\static')

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()