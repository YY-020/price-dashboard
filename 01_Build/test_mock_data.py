"""
测试脚本：使用最小化数据验证UI是否能正常加载
"""
import sys
import json
import gzip
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

BUILD_DIR = Path(__file__).resolve().parent
STATIC_DIR = str(BUILD_DIR / "static")
PORT = 8507

# 最小化mock数据：仅10条记录
mock_data = {
    "material_groups": {
        "上游·原材料": ["碳酸锂", "氢氧化锂"],
        "中游·电解液/LFP/CNT": ["六氟磷酸锂", "VC"],
        "下游·电芯": ["LFP电芯"]
    },
    "materials": ["碳酸锂", "氢氧化锂", "六氟磷酸锂", "VC", "LFP电芯"],
    "price_data": [
        {"date": "2026-06-01", "material_key": "碳酸锂", "price": 285000, "unit": "RMB/t", "source": "SMM", "chem": "Li₂CO₃"},
        {"date": "2026-06-02", "material_key": "碳酸锂", "price": 283000, "unit": "RMB/t", "source": "SMM", "chem": "Li₂CO₃"},
        {"date": "2026-06-03", "material_key": "碳酸锂", "price": 281000, "unit": "RMB/t", "source": "SMM", "chem": "Li₂CO₃"},
        {"date": "2026-06-04", "material_key": "碳酸锂", "price": 279000, "unit": "RMB/t", "source": "SMM", "chem": "Li₂CO₃"},
        {"date": "2026-06-05", "material_key": "碳酸锂", "price": 277000, "unit": "RMB/t", "source": "SMM", "chem": "Li₂CO₃"},
        {"date": "2026-06-01", "material_key": "氢氧化锂", "price": 295000, "unit": "RMB/t", "source": "SMM", "chem": "LiOH·H₂O"},
        {"date": "2026-06-02", "material_key": "氢氧化锂", "price": 293000, "unit": "RMB/t", "source": "SMM", "chem": "LiOH·H₂O"},
        {"date": "2026-06-03", "material_key": "氢氧化锂", "price": 291000, "unit": "RMB/t", "source": "SMM", "chem": "LiOH·H₂O"},
        {"date": "2026-06-04", "material_key": "氢氧化锂", "price": 289000, "unit": "RMB/t", "source": "SMM", "chem": "LiOH·H₂O"},
        {"date": "2026-06-05", "material_key": "氢氧化锂", "price": 287000, "unit": "RMB/t", "source": "SMM", "chem": "LiOH·H₂O"},
    ],
    "date_range": ("2026-06-01", "2026-06-05")
}

data_json = json.dumps(mock_data, ensure_ascii=False)
print(f"Mock data size: {len(data_json)} characters")
print(f"Records: {len(mock_data['price_data'])}")

# 读取UI原型
html_file = BUILD_DIR / "static" / "ui_prototype.html"
html_content = html_file.read_text(encoding="utf-8")

# 嵌入mock数据
data_script = f"""<script>
    window.DASHBOARD_DATA = {data_json};
</script>"""

html_content = html_content.replace('</body>', data_script + '</body>')

# 写入测试文件
output_html = BUILD_DIR / "static" / "test_mock_dashboard.html"
output_html.write_text(html_content, encoding="utf-8")
print(f"Test HTML generated: {output_html}")
print(f"File size: {len(html_content):,} bytes")

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        path = self.path
        if path == '/':
            path = '/test_mock_dashboard.html'
        
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

print(f"\nStarting test server on http://localhost:{PORT}")
print("Open your browser and navigate to: http://localhost:8507/test_mock_dashboard.html")

server = HTTPServer(("0.0.0.0", PORT), Handler)
server.serve_forever()
