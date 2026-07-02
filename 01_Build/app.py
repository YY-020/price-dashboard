"""
锂电产业链价格看板 - Streamlit 应用
"""
import sys
import json
from pathlib import Path

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
</style>
""", unsafe_allow_html=True)

try:
    dashboard_data = get_data_for_frontend()
except Exception as e:
    st.error(f"数据加载失败: {str(e)}")
    st.stop()

data_json = json.dumps(dashboard_data, ensure_ascii=False)

html_file = BUILD_DIR / "static" / "ui_prototype.html"
html_content = html_file.read_text(encoding="utf-8")

data_injection = f"""
<script>
    window.DASHBOARD_DATA = {data_json};
</script>
"""

html_content = html_content.replace("</head>", data_injection + "</head>")

st.components.v1.html(html_content, height=1000, scrolling=True)