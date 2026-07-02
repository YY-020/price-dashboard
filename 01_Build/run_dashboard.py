"""
锂电产业链价格看板 - 独立运行脚本
修复方案：数据内嵌 + gzip压缩 + 减少数据量
"""
import sys
import json
import gzip
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

BUILD_DIR = Path(__file__).resolve().parent
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

print("Loading data...")
from data_loader import get_data_for_frontend, export_to_wide_excel

dashboard_data = get_data_for_frontend()
data_json = json.dumps(dashboard_data, ensure_ascii=False)
print(f"Data loaded: {len(dashboard_data['price_data'])} records")

html_file = BUILD_DIR / "static" / "ui_prototype.html"
html_content = html_file.read_text(encoding="utf-8")

data_script = f"""<script>
    window.DASHBOARD_DATA = {data_json};
</script>"""

html_content = html_content.replace('</body>', data_script + '</body>')

output_html = BUILD_DIR / "static" / "dashboard.html"
output_html.write_text(html_content, encoding="utf-8")
print(f"Dashboard HTML generated: {output_html}")

PORT = 8506
STATIC_DIR = str(BUILD_DIR / "static")

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        if self.path.startswith('/download_data'):
            self.handle_download_data()
        else:
            self.serve_static_file()
    
    def serve_static_file(self):
        path = self.path
        if path == '/':
            path = '/dashboard.html'
        
        file_path = Path(STATIC_DIR) / path.lstrip('/')
        
        if not file_path.exists() or not file_path.is_file():
            self.send_error(404, "File not found")
            return
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            content_type = 'text/html'
            if path.endswith('.css'):
                content_type = 'text/css'
            elif path.endswith('.js'):
                content_type = 'application/javascript'
            elif path.endswith('.json'):
                content_type = 'application/json'
            
            accept_encoding = self.headers.get('Accept-Encoding', '')
            if 'gzip' in accept_encoding.lower() and path.endswith(('.html', '.css', '.js', '.json')):
                content = gzip.compress(content)
                self.send_response(200)
                self.send_header('Content-Type', content_type + '; charset=utf-8')
                self.send_header('Content-Encoding', 'gzip')
                self.send_header('Content-Length', len(content))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_response(200)
                self.send_header('Content-Type', content_type + '; charset=utf-8')
                self.send_header('Content-Length', len(content))
                self.end_headers()
                self.wfile.write(content)
        except Exception as e:
            self.send_error(500, str(e))
    
    def handle_download_data(self):
        try:
            full_path = self.path
            if '?' in full_path:
                path_part, query = full_path.split('?', 1)
            else:
                path_part = full_path
                query = ''
            
            params = urllib.parse.parse_qs(query, keep_blank_values=True, encoding='utf-8')
            
            material_keys = params.get('materials', [])
            start_date = params.get('start_date', [None])[0]
            end_date = params.get('end_date', [None])[0]
            
            excel_data = export_to_wide_excel(material_keys, start_date, end_date)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            self.send_header('Content-Disposition', 'attachment; filename="price_data.xlsx"')
            self.end_headers()
            self.wfile.write(excel_data.read())
        except Exception as e:
            self.send_error(500, str(e))

print(f"\nStarting server on http://localhost:{PORT}")
print("Open your browser and navigate to: http://localhost:8506/dashboard.html")
print("API endpoint: http://localhost:8506/api/data")

server = HTTPServer(("0.0.0.0", PORT), Handler)
server.serve_forever()
