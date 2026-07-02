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
import pandas as pd
from datetime import datetime, timedelta

BUILD_DIR = Path(__file__).resolve().parent
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

PROJECT_ROOT = BUILD_DIR.parent
LONG_CSV = PROJECT_ROOT / "02_Output" / "price_data_long.csv"

MATERIAL_GROUPS = {
    '上游-原材料': [
        {"key": "乙烯", "label": "乙烯 (C₂H₄)", "chem": "C₂H₄"},
        {"key": "乙炔", "label": "乙炔 (C₂H₂)", "chem": "C₂H₂"},
        {"key": "硫酸镍", "label": "硫酸镍 (NiSO₄)", "chem": "NiSO₄"},
        {"key": "硫酸钴", "label": "硫酸钴 (CoSO₄)", "chem": "CoSO₄"},
        {"key": "硫酸锰", "label": "硫酸锰 (MnSO₄)", "chem": "MnSO₄"},
        {"key": "碳酸锂", "label": "碳酸锂 (Li₂CO₃)", "chem": "Li₂CO₃"},
        {"key": "氢氧化锂（微粉）", "label": "氢氧化锂 (LiOH)-微粉", "chem": "LiOH"},
        {"key": "氢氧化锂（粗颗粒）", "label": "氢氧化锂 (LiOH)-粗颗粒", "chem": "LiOH"},
    ],
    '中游-电解液溶剂': [
        {"key": "碳酸乙烯酯", "label": "碳酸乙烯酯 (EC)", "chem": "EC"},
        {"key": "碳酸丙烯酯", "label": "碳酸丙烯酯 (PC)", "chem": "PC"},
        {"key": "碳酸二甲酯", "label": "碳酸二甲酯 (DMC)", "chem": "DMC"},
        {"key": "碳酸甲乙酯", "label": "碳酸甲乙酯 (EMC)", "chem": "EMC"},
        {"key": "碳酸二乙酯", "label": "碳酸二乙酯 (DEC)", "chem": "DEC"},
        {"key": "乙酸甲酯", "label": "乙酸甲酯 (MA)", "chem": "MA"},
    ],
    '中游-电解液添加剂': [
        {"key": "碳酸亚乙烯酯（BaiInfo）", "label": "碳酸亚乙烯酯 (VC)-百川", "chem": "VC"},
        {"key": "碳酸亚乙烯酯（SMM）", "label": "碳酸亚乙烯酯 (VC)-有色网", "chem": "VC"},
        {"key": "氟代碳酸乙烯酯", "label": "氟代碳酸乙烯酯 (FEC)", "chem": "FEC"},
        {"key": "硫酸乙烯酯", "label": "硫酸乙烯酯 (DTD)", "chem": "DTD"},
        {"key": "丙烯磺酸内酯", "label": "丙烯磺酸内酯 (PRS)", "chem": "PRS"},
        {"key": "1,3-丙烷磺酸内酯", "label": "1,3-丙烷磺酸内酯 (PS)", "chem": "PS"},
    ],
    '中游-电解液锂盐': [
        {"key": "双(氟磺酰)亚胺锂·折固", "label": "双(氟磺酰)亚胺锂 (LiFSi)-折固", "chem": "LiFSi"},
        {"key": "双(氟磺酰)亚胺锂·固体", "label": "双(氟磺酰)亚胺锂 (LiFSi)-固体", "chem": "LiFSi"},
        {"key": "六氟磷酸锂", "label": "六氟磷酸锂 (LiPF₆)", "chem": "LiPF₆"},
        {"key": "二氟草酸硼酸锂", "label": "二氟草酸硼酸锂 (LiDFOB)", "chem": "LiDFOB"},
        {"key": "二氟磷酸锂", "label": "二氟磷酸锂 (LiPO₂F₂)", "chem": "LiPO₂F₂"},
    ],
    '中游-电解液': [
        {"key": "电解液·三元用", "label": "电解液-三元", "chem": ""},
        {"key": "电解液·磷酸铁锂用", "label": "电解液-磷酸铁锂", "chem": ""},
    ],
    '中游-LFP': [
        {"key": "磷酸铁", "label": "磷酸铁 (FP)", "chem": "FP"},
        {"key": "磷酸铁锂·储能高端型", "label": "磷酸铁锂 (LFP)-储能高端型", "chem": "LFP"},
        {"key": "磷酸铁锂·动力高端型", "label": "磷酸铁锂 (LFP)-动力高端型", "chem": "LFP"},
    ],
    '中游-CNT': [
        {"key": "多壁碳纳米管浆料·高端", "label": "多壁碳纳米管浆料 (MWCNT)-高端", "chem": "MWCNT"},
        {"key": "多壁碳纳米管浆料·低端", "label": "多壁碳纳米管浆料 (MWCNT)-低端", "chem": "MWCNT"},
        {"key": "多壁碳纳米管粉体·高端", "label": "多壁碳纳米管粉体 (MWCNT)-高端", "chem": "MWCNT"},
        {"key": "多壁碳纳米管粉体·低端", "label": "多壁碳纳米管粉体 (MWCNT)-低端", "chem": "MWCNT"},
        {"key": "单壁碳纳米管粉体·最低价格", "label": "单壁碳纳米管粉体-最低价", "chem": "SWCNT"},
        {"key": "单壁碳纳米管粉体·最高价格", "label": "单壁碳纳米管粉体-最高价", "chem": "SWCNT"},
        {"key": "N-甲基吡咯烷酮", "label": "N-甲基吡咯烷酮 (NMP)", "chem": "NMP"},
    ],
    '下游-电芯': [
        {"key": "8系方形三元电芯", "label": "8系方形镍钴锰电池-动力型 158Ah", "chem": "NCM-811"},
        {"key": "方形磷酸铁锂电芯·储能型,314Ah", "label": "方形磷酸铁锂电池-储能型 314Ah", "chem": "LFP-314Ah"},
        {"key": "方形磷酸铁锂电芯·动力型,174Ah", "label": "方形磷酸铁锂电池-动力型 174Ah", "chem": "LFP-174Ah"},
    ],
}

ALL_MATERIALS = []
for group, items in MATERIAL_GROUPS.items():
    ALL_MATERIALS.extend(items)

def load_price_data_direct(min_date=None):
    df = pd.read_csv(str(LONG_CSV))
    df["date"] = pd.to_datetime(df["date"])
    
    if min_date:
        min_date_dt = pd.to_datetime(min_date)
        df = df[df["date"] >= min_date_dt]
    
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.dropna(subset=["price"])
    df = df.sort_values(["material_key", "date"])
    
    data_rows = []
    for _, row in df.iterrows():
        data_rows.append({
            "date": row["date"].strftime("%Y-%m-%d"),
            "material_key": row["material_key"],
            "price": float(row["price"]),
            "unit": "RMB/t",
            "source": "",
            "chem": "",
        })
    
    return data_rows

print("Loading data...")
six_months_ago = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
price_data = load_price_data_direct(min_date=six_months_ago)

dashboard_data = {
    "price_data": price_data,
    "date_range": ("2025-01-01", datetime.now().strftime("%Y-%m-%d")),
    "materials": ALL_MATERIALS,
    "material_groups": MATERIAL_GROUPS,
}

data_json = json.dumps(dashboard_data, ensure_ascii=False)
print(f"Data loaded: {len(price_data)} records")

from data_loader import export_to_wide_excel

html_file = BUILD_DIR / "static" / "ui_prototype.html"
html_content = html_file.read_text(encoding="utf-8")

# Save data to separate JSON file
data_file = BUILD_DIR / "static" / "dashboard_data.json"
data_file.write_text(data_json, encoding="utf-8")
print(f"Data JSON generated: {data_file}")

# Replace with AJAX loader that initializes page after data is loaded
data_loader_script = """<script>
    window.DASHBOARD_DATA_LOADED = false;
    window.DASHBOARD_DATA = null;
    
    async function loadDashboardData() {
        try {
            const response = await fetch('dashboard_data.json');
            window.DASHBOARD_DATA = await response.json();
            window.DASHBOARD_DATA_LOADED = true;
            console.log('Data loaded via AJAX:', window.DASHBOARD_DATA.price_data.length, 'records');
            
            // Trigger re-initialization if DOM is already loaded
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
    
    // Start loading data immediately
    loadDashboardData();
    
    // Also listen for DOMContentLoaded to handle race condition
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
print("API endpoint: http://localhost:8506/api/data")

server = HTTPServer(("0.0.0.0", PORT), Handler)
server.serve_forever()
