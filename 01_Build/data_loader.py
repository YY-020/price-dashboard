"""
数据加载模块 - 从 02_Output/price_data_clean.csv 和 price_data_meta.csv 读取清洗后的数据
"""
import pandas as pd
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "02_Output"
CLEAN_CSV = OUTPUT_DIR / "price_data_clean.csv"
META_CSV = OUTPUT_DIR / "price_data_meta.csv"

# 材料分组定义（key=CSV列名, value=显示名，严格照搬用户指定命名）
MATERIAL_GROUPS = {
    "上游原材料": {
        "乙烯": "乙烯 (C2H4)",
        "乙炔": "乙炔 (C₂H₂) ≥98%",
        "硫酸镍": "硫酸镍 (NiSO₄)",
        "硫酸钴": "硫酸钴 (CoSO₄)",
        "硫酸锰": "硫酸锰 (MnSO₄)",
        "碳酸锂": "碳酸锂 (Li₂CO₃)",
        "氢氧化锂（微粉）": "氢氧化锂 (LiOH)-微粉",
        "氢氧化锂（粗颗粒）": "氢氧化锂 (LiOH)-粗颗粒",
    },
    "电解液溶剂": {
        "碳酸乙烯酯": "碳酸乙烯酯 (EC)",
        "碳酸丙烯酯": "碳酸丙烯酯 (PC)",
        "碳酸二甲酯": "碳酸二甲酯 (DMC)",
        "碳酸甲乙酯": "碳酸甲乙酯 (EMC)",
        "碳酸二乙酯": "碳酸二乙酯 (DEC)",
        "乙酸甲酯": "乙酸甲酯 (MA)",
    },
    "电解液添加剂": {
        "碳酸亚乙烯酯（SMM）": "碳酸亚乙烯酯 (VC)-SMM",
        "碳酸亚乙烯酯（BaiInfo）": "碳酸亚乙烯酯 (VC)-百川",
        "氟代碳酸乙烯酯": "氟代碳酸乙烯酯 (FEC)",
        "硫酸乙烯酯": "硫酸乙烯酯 (DTD)",
        "丙烯磺酸内酯": "丙烯磺酸内酯 (PRS)",
        "1,3-丙烷磺酸内酯": "1,3-丙烷磺酸内酯 (PS)",
    },
    "电解液锂盐": {
        "双(氟磺酰)亚胺锂·折固": "双(氟磺酰)亚胺锂 (LiFSi)-折固",
        "双(氟磺酰)亚胺锂·固体": "双(氟磺酰)亚胺锂 (LiFSi)-固体",
        "六氟磷酸锂": "六氟磷酸锂 (LiPF6)-固体",
        "二氟草酸硼酸锂": "二氟草酸硼酸锂 (LiDFOB)-固体",
        "二氟磷酸锂": "二氟磷酸锂 (LiPO2F2)-固体",
    },
    "电解液": {
        "电解液·三元用": "电解液-三元",
        "电解液·磷酸铁锂用": "电解液-磷酸铁锂",
    },
    "磷酸铁锂": {
        "磷酸铁": "磷酸铁 (FP)",
        "磷酸铁锂·储能高端型": "磷酸铁锂 (LFP)-高端储能型",
        "磷酸铁锂·动力高端型": "磷酸铁锂 (LFP)-高端动力型",
    },
    "碳纳米管": {
        "多壁碳纳米管浆料·低端": "多壁碳纳米管浆料 (MWCNT浆料)-低端",
        "多壁碳纳米管浆料·高端": "多壁碳纳米管浆料 (MWCNT浆料)-高端",
        "多壁碳纳米管粉体·高端": "多壁碳纳米管粉体 (MWCNT粉体)-高端",
        "多壁碳纳米管粉体·低端": "多壁碳纳米管粉体 (MWCNT粉体)-低端",
        "单壁碳纳米管粉体·最低价格": "单壁碳纳米管粉体-最低价",
        "单壁碳纳米管粉体·最高价格": "单壁碳纳米管粉体-最高价",
        "N-甲基吡咯烷酮": "N-甲基吡咯烷酮 (NMP)",
    },
    "电芯": {
        "8系方形三元电芯": "8系方形镍钴锰电池-动力型 158Ah",
        "方形磷酸铁锂电芯·储能型,314Ah": "方形磷酸铁锂电池-储能型 314Ah",
        "方形磷酸铁锂电芯·动力型,174Ah": "方形磷酸铁锂电池-动力型 174Ah",
    },
}

# 构建 CSV列名 -> 显示名 的扁平映射
DISPLAY_NAMES = {}
for group, members in MATERIAL_GROUPS.items():
    for csv_name, display_name in members.items():
        DISPLAY_NAMES[csv_name] = display_name

# 反向映射：显示名 -> CSV列名
DISPLAY_TO_CSV = {v: k for k, v in DISPLAY_NAMES.items()}


def load_price_data() -> dict:
    """
    从清洗后的 CSV 加载价格数据，返回结构化字典：
    {
        'materials': [{name, display_name, group, unit, source, formula, spec}, ...],
        'df': DataFrame (index=日期, columns=CSV列名),
        'date_range': (min_date, max_date),
        'sources': [数据源列表],
    }
    """
    if not CLEAN_CSV.exists():
        raise FileNotFoundError(
            f"未找到清洗后的数据文件: {CLEAN_CSV}\n"
            "请先运行 data_cleaner.py 生成清洗数据"
        )

    # 读取数据
    df = pd.read_csv(str(CLEAN_CSV), encoding="utf-8-sig", parse_dates=["日期"])
    df = df.set_index("日期").sort_index()

    # 读取元信息
    meta = None
    if META_CSV.exists():
        meta = pd.read_csv(str(META_CSV), encoding="utf-8-sig")
        meta = meta.set_index("行标签")

    # 构建材料列表
    price_cols = [c for c in df.columns if c != "日期"]
    materials = []

    for col_name in price_cols:
        unit = _get_meta(meta, col_name, "单位")
        source = _get_meta(meta, col_name, "数据源")
        formula = _get_meta(meta, col_name, "化学式")
        spec = _get_meta(meta, col_name, "规格")
        group = _find_group(col_name)
        display_name = DISPLAY_NAMES.get(col_name, col_name)

        materials.append({
            "name": col_name,
            "display_name": display_name,
            "group": group,
            "unit": unit,
            "source": source,
            "formula": formula,
            "spec": spec,
        })

    sources = sorted(set(m["source"] for m in materials if m["source"] and m["source"] != "/"))

    return {
        "materials": materials,
        "df": df,
        "date_range": (df.index.min(), df.index.max()),
        "sources": sources,
    }


def _get_meta(meta: pd.DataFrame, col_name: str, row_label: str) -> str:
    """从元信息 DataFrame 中提取指定列和行的值"""
    if meta is None:
        return ""
    if col_name not in meta.columns:
        return ""
    if row_label not in meta.index:
        return ""
    val = meta.loc[row_label, col_name]
    if pd.isna(val):
        return ""
    return str(val).strip()


def _find_group(material_name: str) -> str:
    """根据材料名找到所属分组"""
    for group, members in MATERIAL_GROUPS.items():
        if material_name in members:
            return group
    return "其他"


def resample_data(df: pd.DataFrame, freq: str) -> pd.DataFrame:
    """
    按频率重采样均价
    freq: 'D'(日), 'W'(周), 'ME'(月), 'QE'(季), 'YE'(年)
    """
    if freq == "D":
        return df
    return df.resample(freq).mean()
