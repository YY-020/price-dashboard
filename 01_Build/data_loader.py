"""
数据加载模块 - 从 Supabase 读取价格数据，本地 CSV 作为备用
"""
import pandas as pd
import streamlit as st
from pathlib import Path
import json
from io import BytesIO

EXCHANGE_RATE = 7.24

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LONG_CSV = PROJECT_ROOT / "02_Output" / "price_data_long.csv"
LONG_CSV_FALLBACK = PROJECT_ROOT / "01_Build" / "price_data_long.csv"
META_CSV = PROJECT_ROOT / "02_Output" / "price_data_meta.csv"
META_CSV_FALLBACK = PROJECT_ROOT / "01_Build" / "price_data_meta.csv"

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
KEY_TO_LABEL = {}
KEY_TO_CHEM = {}
KEY_TO_GROUP = {}

for group, items in MATERIAL_GROUPS.items():
    for item in items:
        ALL_MATERIALS.append(item)
        KEY_TO_LABEL[item["key"]] = item["label"]
        KEY_TO_CHEM[item["key"]] = item["chem"]
        KEY_TO_GROUP[item["key"]] = group


def get_supabase_client():
    """获取 Supabase 客户端"""
    try:
        from supabase import create_client, Client
        
        supabase_url = st.secrets.get("SUPABASE_URL")
        supabase_key = st.secrets.get("SUPABASE_KEY")
        
        if not supabase_url:
            raise Exception("SUPABASE_URL 未配置")
        if not supabase_key:
            raise Exception("SUPABASE_KEY 未配置")
        
        return create_client(supabase_url, supabase_key)
    except ImportError as e:
        raise Exception(f"supabase 包未安装: {str(e)}")
    except Exception as e:
        raise Exception(f"创建 Supabase 客户端失败: {str(e)}")


def load_meta_data():
    """加载元数据，返回 {material_key: {unit, source, chem}}"""
    if META_CSV.exists():
        csv_path = META_CSV
    elif META_CSV_FALLBACK.exists():
        csv_path = META_CSV_FALLBACK
    else:
        return {}
    
    df = pd.read_csv(str(csv_path))
    df = df.set_index("行标签")
    
    meta_dict = {}
    for col in df.columns:
        material_key = col.strip()
        if material_key in KEY_TO_LABEL:
            meta_dict[material_key] = {
                "unit": df.loc["单位", col] if "单位" in df.index else "RMB/t",
                "source": df.loc["数据源", col] if "数据源" in df.index else "",
                "chem": df.loc["化学式", col] if "化学式" in df.index else "",
            }
    return meta_dict


def load_price_data_from_supabase(min_date=None):
    """从 Supabase 加载价格数据"""
    supabase = get_supabase_client()
    if not supabase:
        raise Exception("Supabase 客户端未配置")
    
    query = supabase.table("price_data").select("*")
    
    if min_date:
        query = query.gte("date", min_date)
    
    response = query.order("date", desc=False).execute()
    
    if not response.data:
        raise Exception("Supabase 没有返回数据")
    
    df = pd.DataFrame(response.data)
    
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
    
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.dropna(subset=["price"])
    
    df = df.sort_values(["material_key", "date"])
    
    meta_dict = load_meta_data()
    
    data_rows = []
    for _, row in df.iterrows():
        mat_key = row["material_key"]
        unit_info = meta_dict.get(mat_key, {})
        
        data_rows.append({
            "date": row["date"].strftime("%Y-%m-%d"),
            "material_key": mat_key,
            "price": float(row["price"]),
            "unit": unit_info.get("unit", "RMB/t"),
            "source": unit_info.get("source", ""),
            "chem": unit_info.get("chem", ""),
        })
    
    date_range = (df["date"].min().strftime("%Y-%m-%d"), df["date"].max().strftime("%Y-%m-%d"))
    
    return {
        "data": data_rows,
        "date_range": date_range,
        "materials": ALL_MATERIALS,
        "material_groups": MATERIAL_GROUPS,
    }


def load_price_data_from_csv(min_date=None):
    """从本地长表 CSV 加载价格数据"""
    if LONG_CSV.exists():
        csv_path = LONG_CSV
    elif LONG_CSV_FALLBACK.exists():
        csv_path = LONG_CSV_FALLBACK
    else:
        raise FileNotFoundError(f"数据文件不存在: {LONG_CSV}")
    
    df = pd.read_csv(str(csv_path))
    df["date"] = pd.to_datetime(df["date"])
    
    if min_date:
        min_date_dt = pd.to_datetime(min_date)
        df = df[df["date"] >= min_date_dt]
    
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.dropna(subset=["price"])
    
    df = df.sort_values(["material_key", "date"])
    
    meta_dict = load_meta_data()
    
    data_rows = []
    for _, row in df.iterrows():
        mat_key = row["material_key"]
        unit_info = meta_dict.get(mat_key, {})
        
        data_rows.append({
            "date": row["date"].strftime("%Y-%m-%d"),
            "material_key": mat_key,
            "price": float(row["price"]),
            "unit": unit_info.get("unit", "RMB/t"),
            "source": unit_info.get("source", ""),
            "chem": unit_info.get("chem", ""),
        })
    
    date_range = (df["date"].min().strftime("%Y-%m-%d"), df["date"].max().strftime("%Y-%m-%d"))
    
    return {
        "data": data_rows,
        "date_range": date_range,
        "materials": ALL_MATERIALS,
        "material_groups": MATERIAL_GROUPS,
        "data_source": "supabase",
    }


def load_price_data_from_csv(min_date=None):
    """从本地长表 CSV 加载价格数据"""
    if LONG_CSV.exists():
        csv_path = LONG_CSV
    elif LONG_CSV_FALLBACK.exists():
        csv_path = LONG_CSV_FALLBACK
    else:
        raise FileNotFoundError(f"数据文件不存在: {LONG_CSV}")
    
    df = pd.read_csv(str(csv_path))
    df["date"] = pd.to_datetime(df["date"])
    
    if min_date:
        min_date_dt = pd.to_datetime(min_date)
        df = df[df["date"] >= min_date_dt]
    
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.dropna(subset=["price"])
    
    df = df.sort_values(["material_key", "date"])
    
    meta_dict = load_meta_data()
    
    data_rows = []
    for _, row in df.iterrows():
        mat_key = row["material_key"]
        unit_info = meta_dict.get(mat_key, {})
        
        data_rows.append({
            "date": row["date"].strftime("%Y-%m-%d"),
            "material_key": mat_key,
            "price": float(row["price"]),
            "unit": unit_info.get("unit", "RMB/t"),
            "source": unit_info.get("source", ""),
            "chem": unit_info.get("chem", ""),
        })
    
    date_range = (df["date"].min().strftime("%Y-%m-%d"), df["date"].max().strftime("%Y-%m-%d"))
    
    return {
        "data": data_rows,
        "date_range": date_range,
        "materials": ALL_MATERIALS,
        "material_groups": MATERIAL_GROUPS,
        "data_source": "local_csv",
    }


@st.cache_data(ttl=300)
def load_price_data(min_date=None):
    """加载价格数据，优先从 Supabase，失败则回退到本地 CSV"""
    try:
        return load_price_data_from_supabase(min_date)
    except Exception as e:
        print(f"Supabase 加载失败，回退到本地 CSV: {str(e)}")
        return load_price_data_from_csv(min_date)


def get_data_for_frontend():
    """获取前端需要的数据格式"""
    from datetime import datetime, timedelta
    six_months_ago = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
    loaded = load_price_data(min_date=six_months_ago)
    
    return {
        "price_data": loaded["data"],
        "date_range": loaded["date_range"],
        "materials": loaded["materials"],
        "material_groups": loaded["material_groups"],
        "data_source": loaded.get("data_source", "unknown"),
    }


def export_to_wide_excel(material_keys=None, start_date=None, end_date=None):
    """
    将价格数据导出为宽表格式的Excel文件
    :param material_keys: 材料列表，None表示全部材料
    :param start_date: 起始日期，None表示最早日期
    :param end_date: 终止日期，None表示最晚日期
    :return: BytesIO对象，包含Excel文件内容
    """
    loaded = load_price_data(min_date=None)
    data_rows = loaded["data"]
    
    df = pd.DataFrame(data_rows)
    df["date"] = pd.to_datetime(df["date"])
    
    if material_keys:
        df = df[df["material_key"].isin(material_keys)]
    
    if start_date:
        df = df[df["date"] >= pd.to_datetime(start_date)]
    
    if end_date:
        df = df[df["date"] <= pd.to_datetime(end_date)]
    
    wide_df = df.pivot(index="date", columns="material_key", values="price")
    wide_df = wide_df.sort_index()
    wide_df.index.name = "日期"
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        wide_df.to_excel(writer, sheet_name="价格数据")
    
    output.seek(0)
    return output