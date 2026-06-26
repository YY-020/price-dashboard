"""
电解液原材料价格看板 - Streamlit 应用
"""
import sys
from pathlib import Path

# 确保 01_Build 在 import 路径中
BUILD_DIR = Path(__file__).resolve().parent
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from data_loader import (
    load_price_data,
    resample_data,
    MATERIAL_GROUPS,
    DISPLAY_NAMES,
    DISPLAY_TO_CSV,
)

# ── 页面配置 ──
st.set_page_config(
    page_title="电解液原材料价格看板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Bloomberg 风格自定义 CSS ──
st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #e0e0e0; }
    h1, h2, h3 { color: #1a1a2e; font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif; }
    .dataframe { font-size: 12px; }
    .dataframe th { background-color: #f0f0f0; color: #333; font-weight: 600; }
    .dataframe td { border-bottom: 1px solid #e8e8e8; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── 数据加载（缓存） ──
@st.cache_data(ttl=300)
def load_data():
    try:
        return load_price_data()
    except FileNotFoundError as e:
        st.error(str(e))
        st.stop()


data = load_data()
materials = data["materials"]
df = data["df"]
date_min, date_max = data["date_range"]

# ── 侧边栏：筛选控件 ──
with st.sidebar:
    st.title("📊 价格看板")
    st.caption(f"数据更新至 {date_max.strftime('%Y-%m-%d')}")
    st.divider()

    # 1. 时间范围
    st.subheader("📅 时间范围")
    date_range = st.date_input(
        "选择日期区间",
        value=(date_min.date(), date_max.date()),
        min_value=date_min.date(),
        max_value=date_max.date(),
    )
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range[0]

    # 2. 时间频率 - 下拉单选
    st.subheader("⏱ 时间频率")
    freq_options = {"日均价": "D", "周均价": "W", "月均价": "ME", "季均价": "QE", "年均价": "YE"}
    freq_label = st.selectbox("选择聚合频率", list(freq_options.keys()), index=0)
    freq = freq_options[freq_label]

    # 3. 数据源 - 分组折叠 + 勾选
    st.subheader("📡 数据源")
    with st.expander("数据源选择（3个）", expanded=True):
        source_select_all = st.checkbox("全选数据源", value=True, key="all_sources")
        selected_sources = []
        for src in ["BaiInfo", "SMM", "GEO"]:
            if st.checkbox(src, value=source_select_all, key=f"source_{src}"):
                selected_sources.append(src)

    # 4. 材料选择 - 分组折叠 + 勾选（无搜索栏）
    st.subheader("🧪 材料选择")

    selected_display_names = []
    for group_name, members in MATERIAL_GROUPS.items():
        # 获取该分组下的材料
        group_mats = [m for m in materials if m["group"] == group_name]
        # 数据源过滤
        if selected_sources:
            group_mats = [m for m in group_mats if m["source"] in selected_sources]

        if not group_mats:
            continue

        mat_display_names = [m["display_name"] for m in group_mats]

        # 分组折叠展示
        with st.expander(f"📦 {group_name}（{len(mat_display_names)}种）", expanded=False):
            select_all = st.checkbox(f"全选 {group_name}", key=f"all_{group_name}")
            for dn in mat_display_names:
                if st.checkbox(dn, value=select_all, key=f"mat_{dn}"):
                    selected_display_names.append(dn)

# ── 主区域 ──
if not selected_display_names:
    st.info("请在左侧选择至少一种材料")
    st.stop()

# 将显示名映射回 CSV 列名
selected_csv_names = [DISPLAY_TO_CSV.get(dn, dn) for dn in selected_display_names]

# 筛选数据
mask = (df.index >= pd.Timestamp(start_date)) & (df.index <= pd.Timestamp(end_date))
df_filtered = df.loc[mask, selected_csv_names]
df_filtered = resample_data(df_filtered, freq)
df_filtered = df_filtered.dropna(how="all")

# ── 折线图 ──
COLORS = px.colors.qualitative.Plotly

def format_label(val, unit):
    """格式化数据标签"""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    if unit == "RMB/Wh":
        if val < 1:
            return f"{val:.3f}"
        return f"{val:.2f}"
    if val < 1:
        return f"{val:.3f}"
    if val < 100:
        return f"{val:.1f}"
    return f"{int(val)}"

fig = go.Figure()

for i, csv_name in enumerate(selected_csv_names):
    display_name = selected_display_names[i]
    color = COLORS[i % len(COLORS)]
    mat_info = next((m for m in materials if m["name"] == csv_name), None)
    unit = mat_info["unit"] if mat_info else "RMB/t"

    series = df_filtered[csv_name].dropna()

    # 数据标签策略：>50个点不显示；否则只标最大值、最小值、最新值
    if len(series) > 50:
        labels = [""] * len(series)
    elif len(series) > 0:
        labels = [""] * len(series)
        max_pos = int(series.values.argmax())
        min_pos = int(series.values.argmin())
        latest_pos = len(series) - 1
        for pos in {max_pos, min_pos, latest_pos}:
            if 0 <= pos < len(series):
                labels[pos] = format_label(series.iloc[pos], unit)
    else:
        labels = []

    fig.add_trace(go.Scatter(
        x=series.index,
        y=series.values,
        name=display_name,
        mode="lines+text",
        line=dict(color=color, width=2, shape="spline"),
        text=labels,
        textposition="top center",
        textfont=dict(size=10, color=color),
        hovertemplate=f"<b>{display_name}</b><br>日期: %{{x|%Y-%m-%d}}<br>价格: %{{y:,.2f}} {unit}<extra></extra>",
    ))

fig.update_layout(
    template="plotly_white",
    height=500,
    margin=dict(l=60, r=30, t=40, b=50),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0,
        font=dict(size=11),
    ),
    xaxis=dict(
        gridcolor="#e8e8e8",
        gridwidth=1,
        title="",
        tickfont=dict(size=11),
    ),
    yaxis=dict(
        gridcolor="#e8e8e8",
        gridwidth=1,
        title="价格",
        tickfont=dict(size=11),
    ),
    hovermode="x unified",
    plot_bgcolor="#ffffff",
    paper_bgcolor="#ffffff",
)

# 图表工具栏配置：中文化，隐藏无法中文化的文字，只保留图标
config = {
    "modeBarButtonsToRemove": [
        "lasso2d", "select2d", "autoScale2d",
        "hoverClosestCartesian", "hoverCompareCartesian",
    ],
    "displaylogo": False,
    "displayModeBar": True,
    "toImageButtonOptions": {
        "format": "png",
        "filename": "价格走势图",
        "height": 500,
        "width": 1200,
        "scale": 2,
    },
}

st.plotly_chart(fig, use_container_width=True, config=config)

# ── 数据明细表 ──
st.subheader("📋 数据明细")

# 格式化表格显示，列名用显示名
df_display = df_filtered.copy()
df_display.columns = [DISPLAY_NAMES.get(c, c) for c in df_display.columns]

for col in df_display.columns:
    mat_info = next((m for m in materials if m["display_name"] == col), None)
    unit = mat_info["unit"] if mat_info else "RMB/t"
    if unit == "RMB/Wh":
        df_display[col] = df_display[col].apply(lambda x: f"{x:.3f}" if pd.notna(x) else "")
    else:
        df_display[col] = df_display[col].apply(
            lambda x: f"{int(x)}" if pd.notna(x) and x >= 100
            else (f"{x:.1f}" if pd.notna(x) and x >= 1
                  else (f"{x:.3f}" if pd.notna(x) else ""))
        )

# 日期降序排列
df_display = df_display.sort_index(ascending=False)
df_display.index = df_display.index.strftime("%Y-%m-%d")
st.dataframe(df_display, use_container_width=True, height=300)

# ── 底部信息 ──
st.caption(f"数据来源：百川盈孚(BaiInfo)、上海有色网(SMM)、GEO内部 | 共 {len(selected_display_names)} 种材料 | {freq_label}")
