"""
锂电产业链价格看板 - Streamlit 应用
"""
import sys
import json
import threading
import time
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

BUILD_DIR = Path(__file__).resolve().parent
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

import streamlit as st
from data_loader import get_data_for_frontend

st.set_page_config(
    page_title="LiPrice Dashboard",
    page_icon="⛁",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    header { display: none; }
    .stApp { background: #f5f7fc; padding: 0; margin: 0; width: 100%; overflow-x: hidden; }
    .st-emotion-cache-13ln4jf { padding: 0; }
    .st-emotion-cache-16txtl3 { padding: 0; }
    iframe { border: none; width: 100%; }
</style>
""", unsafe_allow_html=True)

try:
    dashboard_data = get_data_for_frontend()
except Exception as e:
    st.error(f"数据加载失败: {str(e)}")
    st.stop()

data_json = json.dumps(dashboard_data, ensure_ascii=False)
data_file = BUILD_DIR / "static" / "dashboard_data.json"
data_file.write_text(data_json, encoding="utf-8")

PORT = 8504

def start_server():
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(BUILD_DIR / "static"), **kwargs)
        def log_message(self, format, *args):
            pass
    
    server = HTTPServer(("localhost", PORT), Handler)
    server.serve_forever()

thread = threading.Thread(target=start_server, daemon=True)
thread.start()

time.sleep(1)

st.markdown(f'<iframe src="http://localhost:{PORT}/ui_prototype.html" width="100%" height="900" style="border:none;"></iframe>', unsafe_allow_html=True)