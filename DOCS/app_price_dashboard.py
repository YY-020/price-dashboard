"""
电解液原材料价格看板 V1.0
基于 Streamlit + Plotly
数据源：百川盈孚 / SMM / GEO
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ──────────────────────────────────────
# 页面配置
# ──────────────────────────────────────
st.set_page_config(
    page_title="电解液原材料价格看板",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────
# 数据加载（带缓存，避免每次交互都重新读取）
# ──────────────────────────────────────
@st.cache_data
def load_data(filepath):
    """读取 Excel，跳过前 7 行表头，自动处理日期"""
    df = pd.read_excel(filepath, header=None, skiprows=7)
    
    # 第一列是日期，后面 40 列用数字命名
    df.columns = ['日期'] + list(range(40))
    df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
    df = df.dropna(subset=['日期'])
    
    return df

# ──────────────────────────────────────
# 材料分组定义
# ──────────────────────────────────────
# 这里的 key 是分组名，value 是列索引（从 0 算，跳过日期列）
MATERIAL_GROUPS = {
    "上游原材料": {
        0: "乙烯 (BaiInfo)",
        1: "乙炔 (BaiInfo)",
        2: "硫酸镍 (SMM)",
        3: "硫酸钴 (SMM)",
        4: "硫酸锰 (SMM)",
        5: "碳酸锂 (SMM)",
        6: "氢氧化锂·微粉 (SMM)",
        7: "氢氧化锂·粗颗粒 (SMM)"
    },
    "电解液溶剂": {
        8: "碳酸乙烯酯 EC (BaiInfo)",
        9: "碳酸丙烯酯 PC (BaiInfo)",
        10: "碳酸二甲酯 DMC (BaiInfo)",
        11: "碳酸甲乙酯 EMC (BaiInfo)",
        12: "碳酸二乙酯 DEC (BaiInfo)",
        13: "乙酸甲酯 MA (GEO)"
    },
    "电解液添加剂": {
        14: "碳酸亚乙烯酯 (BaiInfo)",
        15: "碳酸亚乙烯酯 (SMM)",
        16: "氟代碳酸乙烯酯 FEC (BaiInfo)",
        17: "硫酸乙烯酯 DTD (BaiInfo)",
        18: "丙烯磺酸内酯 PRS (GEO)",
        19: "1,3-丙烷磺酸内酯 PS (BaiInfo)"
    },
    "电解液锂盐": {
        20: "LiFSi·折固 (BaiInfo)",
        21: "LiFSi·固体 (BaiInfo)",
        22: "六氟磷酸锂 LiFP6 (SMM)",
        23: "LiDFOB·固体 (SMM)",
        24: "LiPO2F2·固体 (GEO)"
    },
    "电解液": {
        25: "电解液·三元用 (SMM)",
        26: "电解液·磷酸铁锂用 (SMM)"
    },
    "磷酸铁": {
        27: "磷酸铁 (SMM)"
    },
    "磷酸铁锂": {
        28: "磷酸铁锂·储能高端型 (SMM)",
        29: "磷酸铁锂·动力高端型 (SMM)"
    },
    "碳纳米管": {
        30: "多壁碳纳米管浆料·高端 (BaiInfo)",
        31: "多壁碳纳米管浆料·低端 (BaiInfo)",
        32: "多壁碳纳米管粉体·高端 (BaiInfo)",
        33: "多壁碳纳米管粉体·低端 (BaiInfo)",
        34: "单壁碳纳米管粉体·最低 (GEO)",
        35: "单壁碳纳米管粉体·最高 (GEO)"
    },
    "N-甲基吡咯烷酮": {
        36: "NMP (BaiInfo)"
    },
    "电芯": {
        37: "8系方形三元电芯·动力型 (SMM)",
        38: "方形磷酸铁锂电芯·储能型 (SMM)",
        39: "方形磷酸铁锂电芯·动力型 (SMM)"
    }
}

# 构建列索引 → 材料名称的映射
COL_TO_NAME = {}
for group_name, items in MATERIAL_GROUPS.items():
    for col_idx, mat_name in items.items():
        COL_TO_NAME[col_idx] = {"材料名": mat_name, "分组": group_name}

# ──────────────────────────────────────
# 文件路径
# ──────────────────────────────────────
from config.paths import PRICE_DATA
DATA_PATH = PRICE_DATA

# ──────────────────────────────────────
# 主界面 - 侧边栏
# ──────────────────────────────────────
with st.sidebar:
    st.title("🔋 价格看板")
    st.caption("电解液原材料价格走势")
    st.divider()

    # ---- 时间范围 ----
    st.subheader("📅 时间范围")
    default_start = datetime(2025, 10, 1)
    default_end = datetime(2026, 4, 23)
    start_date = st.date_input("起始日期", value=default_start)
    end_date = st.date_input("结束日期", value=default_end)

    # ---- 时间频率 ----
    st.subheader("⏱ 时间频率")
    freq_option = st.selectbox(
        "选择聚合频率",
        options=["日均价", "周均价", "月均价", "季均价", "年均价"],
        index=0
    )

    # ---- 数据源 ----
    st.subheader("📡 数据源")
    source_option = st.radio(
        "选择数据来源",
        options=["全部", "BaiInfo", "SMM", "GEO"],
        horizontal=False
    )

    # ---- 材料分组选择 ----
    st.subheader("🧪 材料选择")
    st.caption("勾选分组，展开选择具体材料")

    selected_materials = []
    for group_name, items in MATERIAL_GROUPS.items():
        with st.expander(f"📦 {group_name} ({len(items)}种)", expanded=False):
            # 全选/取消全选按钮
            material_names = [v for v in items.values()]
            select_all = st.checkbox(f"全选 {group_name}", key=f"all_{group_name}")
            
            selected_in_group = []
            for mat_name in material_names:
                default_selected = group_name in ["电解液锂盐", "电解液溶剂"]
                if select_all:
                    checked = st.checkbox(mat_name, value=True, key=mat_name)
                else:
                    checked = st.checkbox(mat_name, value=default_selected, key=mat_name)
                if checked:
                    selected_in_group.append(mat_name)
            
            selected_materials.extend(selected_in_group)

    st.divider()
    st.caption("数据更新：手动替换 Excel 文件后刷新页面")

# ──────────────────────────────────────
# 主区域
# ──────────────────────────────────────
st.title("电解液关键原材料价格走势")
st.caption("数据截至：2026-04-23 | 来源：百川盈孚 & SMM & GEO")

# 加载数据
try:
    df_raw = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(f"❌ 找不到文件：{DATA_PATH}")
    st.info("请确认文件路径正确，文件名是否为 price_data_0513.xlsx")
    st.stop()
except Exception as e:
    st.error(f"❌ 读取文件出错：{e}")
    st.stop()

# ──────────────────────────────────────
# 数据处理：宽表 → 长表
# ──────────────────────────────────────
# 只保留日期 + 材料列
df_plot = df_raw.copy()
df_plot = df_plot[['日期'] + list(range(40))]

# 转换：每个材料列变成一列
melted_data = []
for col_idx, info in COL_TO_NAME.items():
    if col_idx in df_plot.columns:
        temp = df_plot[['日期', col_idx]].copy()
        temp.columns = ['日期', '价格']
        temp['材料'] = info['材料名']
        temp['分组'] = info['分组']
        temp['数据源'] = info['材料名'].split('(')[-1].replace(')', '') if '(' in info['材料名'] else 'Unknown'
        temp['价格'] = pd.to_numeric(temp['价格'], errors='coerce')
        melted_data.append(temp)

df_long = pd.concat(melted_data, ignore_index=True)
df_long = df_long.dropna(subset=['价格'])

# 筛选时间范围
df_long = df_long[(df_long['日期'] >= pd.to_datetime(start_date)) & 
                  (df_long['日期'] <= pd.to_datetime(end_date))]

# 筛选数据源
if source_option != "全部":
    df_long = df_long[df_long['数据源'] == source_option]

# 筛选材料
if selected_materials:
    df_long = df_long[df_long['材料'].isin(selected_materials)]
else:
    st.warning("⚠️ 请先在侧边栏选择至少一种材料")
    st.stop()

if df_long.empty:
    st.warning("⚠️ 当前筛选条件下没有数据，请调整时间范围或材料选择")
    st.stop()

# ──────────────────────────────────────
# 时间频率聚合
# ──────────────────────────────────────
freq_map = {
    "日均价": None,
    "周均价": "W",
    "月均价": "ME",
    "季均价": "QE",
    "年均价": "YE"
}

if freq_option == "日均价":
    df_display = df_long.copy()
else:
    freq_code = freq_map[freq_option]
    df_display = df_long.groupby(['材料', '分组', '数据源', pd.Grouper(key='日期', freq=freq_code)])\
                        .agg({'价格': 'mean'})\
                        .reset_index()

# ──────────────────────────────────────
# 颜色配置
# ──────────────────────────────────────
colors = [
    '#2c5f8a', '#d97706', '#0f7b4e', '#8b1e3f', '#6b4e71',
    '#3a7ca5', '#bc4a1f', '#2d8a6e', '#c44569', '#574b90',
    '#1e5a99', '#e08e0b', '#1a6b4a', '#a42a4b', '#7d5f8c',
    '#4a90c4', '#d45d2c', '#3d9e73', '#d64a6e', '#6b5ca0'
]

# ──────────────────────────────────────
# 图表区域
# ──────────────────────────────────────
st.subheader("📈 价格走势图")

fig = go.Figure()

for i, mat_name in enumerate(df_display['材料'].unique()):
    mat_data = df_display[df_display['材料'] == mat_name]
    color = colors[i % len(colors)]
    
    fig.add_trace(go.Scatter(
        x=mat_data['日期'],
        y=mat_data['价格'],
        mode='lines+markers',
        name=mat_name,
        line=dict(color=color, width=2),
        marker=dict(size=3, color=color),
        hovertemplate='<b>%{text}</b><br>日期: %{x}<br>价格: %{y:,.0f} RMB/t<extra></extra>',
        text=[mat_name] * len(mat_data)
    ))

fig.update_layout(
    xaxis_title="日期",
    yaxis_title="价格 (RMB/t)",
    hovermode="x unified",
    height=500,
    template="plotly_white",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.4,
        xanchor="center",
        x=0.5,
        font=dict(size=11)
    ),
    margin=dict(b=120),
    plot_bgcolor='white',
    paper_bgcolor='white',
    xaxis=dict(
        showgrid=True,
        gridcolor='#e5e7eb',
        gridwidth=0.5,
        zeroline=False
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='#e5e7eb',
        gridwidth=0.5,
        zeroline=False,
        tickformat=","
    )
)

st.plotly_chart(fig, use_container_width=True)

# ──────────────────────────────────────
# 数据明细表
# ──────────────────────────────────────
st.divider()
st.subheader("📋 数据明细表")

# 格式化显示
df_table = df_display.pivot_table(
    index='日期', 
    columns='材料', 
    values='价格',
    aggfunc='mean'
).reset_index()

df_table['日期'] = df_table['日期'].dt.strftime('%Y-%m-%d')
df_table = df_table.sort_values('日期', ascending=False)

# 数值格式化
for col in df_table.columns:
    if col != '日期':
        df_table[col] = df_table[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "-")

st.dataframe(
    df_table,
    use_container_width=True,
    height=400,
    hide_index=True
)

# ──────────────────────────────────────
# 页脚
# ──────────────────────────────────────
st.divider()
st.caption("电解液市场数据平台 · 价格看板 V1.0 | 首席记录员：DeepSeek")