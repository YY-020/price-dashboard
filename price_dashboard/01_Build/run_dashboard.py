"""
锂电产业链价格看板 - 独立运行脚本
支持本地开发测试，优先从Supabase读取数据
"""
import sys
import json
import gzip
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from datetime import datetime, timedelta

BUILD_DIR = Path(__file__).resolve().parent
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from data_loader import get_data_for_frontend, export_to_wide_excel

print("Loading data...")
try:
    dashboard_data = get_data_for_frontend()
    print(f"Data loaded from Supabase: {len(dashboard_data['price_data'])} records")
except Exception as e:
    print(f"Failed to load from Supabase: {e}")
    print("Falling back to local CSV...")
    from data_loader_local import get_data_for_frontend as get_local_data
    dashboard_data = get_local_data()

data_json = json.dumps(dashboard_data, ensure_ascii=False)
print(f"Data loaded: {len(dashboard_data['price_data'])} records")

html_file = BUILD_DIR / "static" / "ui_prototype.html"
html_content = html_file.read_text(encoding="utf-8")

data_file = BUILD_DIR / "static" / "dashboard_data.json"
data_file.write_text(data_json, encoding="utf-8")
print(f"Data JSON generated: {data_file}")

data_loader_script = """<script>
    window.DASHBOARD_DATA_LOADED = false;
    window.DASHBOARD_DATA = null;
    
    async function loadDashboardData() {
        try {
            const response = await fetch('dashboard_data.json');
            window.DASHBOARD_DATA = await response.json();
            window.DASHBOARD_DATA_LOADED = true;
            console.log('Data loaded via AJAX:', window.DASHBOARD_DATA.price_data.length, 'records');
            
            if (document.readyState === 'complete' || document.readyState === 'interactive') {
                initializeDashboard();
            }
        } catch(e) {
            console.error('Failed to load data:', e);
            window.DASHBOARD_DATA = {};
            window.DASHBOARD_DATA_LOADED = true;
            if (document.readyState === 'complete' || document.readyState === 'interactive') {
                initializeDashboard();
            }
        }
    }
    
    function initializeDashboard() {
        console.log('DOM loaded, initializing data...');
        try {
            if (window.DASHBOARD_DATA) {
                console.log('DASHBOARD_DATA exists, parsing...');
                MATERIAL_GROUPS = window.DASHBOARD_DATA.material_groups || DEFAULT_MATERIAL_GROUPS;
                ALL_MATERIALS = window.DASHBOARD_DATA.materials || Object.values(MATERIAL_GROUPS).flat();
                PRICE_DATA = window.DASHBOARD_DATA.price_data || [];
                
                PRICE_DATA.forEach(function(d) {
                    if (d.unit) UNIT_MAP[d.material_key] = d.unit;
                });
                
                console.log('Data initialized:', PRICE_DATA.length, 'records,', ALL_MATERIALS.length, 'materials');
            } else {
                console.log('DASHBOARD_DATA not found, using defaults');
                MATERIAL_GROUPS = DEFAULT_MATERIAL_GROUPS;
                ALL_MATERIALS = Object.values(MATERIAL_GROUPS).flat();
                generateMockData();
            }
            
            document.getElementById('loading').classList.add('hidden');
            console.log('Calling initApp...');
            initApp();
            console.log('Dashboard initialized successfully');
        } catch (e) {
            console.error('Critical error during initialization:', e);
            document.getElementById('loading').classList.add('hidden');
        }
    }
    
    loadDashboardData();
    
    document.addEventListener('DOMContentLoaded', function() {
        if (window.DASHBOARD_DATA_LOADED) {
            initializeDashboard();
        } else {
            console.log('DOM loaded but data not yet loaded, waiting...');
        }
    });
</script>"""

html_content = html_content.replace('</body>', data_loader_script + '</body>')

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

server = HTTPServer(("0.0.0.0", PORT), Handler)
server.serve_forever()
