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
from data_loader import get_data_for_frontend, load_price_data

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
    .supabase-status {{
        position: fixed;
        top: 10px;
        left: 10px;
        z-index: 9999;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: bold;
    }}
    .supabase-success {{
        background: #dcfce7;
        color: #166534;
        border: 1px solid #bbf7d0;
    }}
    .supabase-error {{
        background: #fee2e2;
        color: #991b1b;
        border: 1px solid #fecaca;
    }}
</style>
""", unsafe_allow_html=True)

supabase_status = {"success": False, "message": ""}

try:
    loaded_data = load_price_data()
    if loaded_data.get("data_source") == "supabase":
        supabase_status["success"] = True
        supabase_status["message"] = "✅ Supabase 连接成功"
    else:
        supabase_status["success"] = False
        supabase_status["message"] = "🟡 使用本地 CSV（Supabase 连接失败）"
    
    dashboard_data = {
        "price_data": loaded_data["data"],
        "date_range": loaded_data["date_range"],
        "materials": loaded_data["materials"],
        "material_groups": loaded_data["material_groups"],
        "data_source": loaded_data.get("data_source", "unknown"),
    }
except Exception as e:
    supabase_status["success"] = False
    supabase_status["message"] = f"❌ 数据加载失败: {str(e)}"
    st.error(f"数据加载失败: {str(e)}")
    st.stop()

data_json = json.dumps(dashboard_data, ensure_ascii=False)

html_file = BUILD_DIR / "static" / "ui_prototype.html"
html_content = html_file.read_text(encoding="utf-8")

status_class = "supabase-success" if supabase_status["success"] else "supabase-error"
status_div = f"""
<div class="supabase-status {status_class}">
    {supabase_status["message"]}
</div>
"""

html_content = html_content.replace("</body>", status_div + "</body>")

data_injection = f"""
<script>
    window.DASHBOARD_DATA = {data_json};
</script>
"""

html_content = html_content.replace("</head>", data_injection + "</head>")

st.components.v1.html(html_content, height=1000, scrolling=True)