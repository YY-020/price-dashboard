"""
锂电产业链价格看板 - 独立运行脚本
"""
import sys
import json
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

BUILD_DIR = Path(__file__).resolve().parent
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from data_loader import get_data_for_frontend

try:
    print("Loading data...")
    dashboard_data = get_data_for_frontend()
    print(f"Data loaded: {len(dashboard_data['price_data'])} records")
except Exception as e:
    print(f"数据加载失败: {str(e)}")
    sys.exit(1)

data_json = json.dumps(dashboard_data, ensure_ascii=False)

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

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BUILD_DIR / "static"), **kwargs)
    
    def log_message(self, format, *args):
        pass

print(f"\nStarting server on http://localhost:{PORT}")
print("Open your browser and navigate to: http://localhost:8506/dashboard.html")

server = HTTPServer(("0.0.0.0", PORT), Handler)
server.serve_forever()