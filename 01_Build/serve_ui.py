import http.server
import socketserver
import threading
import time

PORT = 8504

def start_server():
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()

server_thread = threading.Thread(target=start_server)
server_thread.daemon = True
server_thread.start()

time.sleep(1)

print(f"UI server running on http://localhost:{PORT}")