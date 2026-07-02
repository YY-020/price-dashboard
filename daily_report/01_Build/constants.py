# -*- coding: utf-8 -*-
"""
日报系统配置常量
"""

# 项目路径配置
PROJECT_ROOT = "D:\\0_trea_projects_by_bela\\daily_report"
BUILD_DIR = f"{PROJECT_ROOT}\\01_Build"
OUTPUT_DIR = f"{PROJECT_ROOT}\\02_Output"

# 新闻采集渠道配置
# 渠道配置已迁移至 crawler/config/channels.yaml
# NEWS_CHANNELS = {
#     # 固定网站（6个）
#     "electrive_battery": {
#         "name": "Electrive-Battery",
#         "url": "https://www.electrive.com/category/battery-fuel-cell/",
#         "type": "rss",
#         "rss_url": "https://www.electrive.com/category/battery-fuel-cell/feed/"
#     },
#     "electrive_auto": {
#         "name": "Electrive-Auto", 
#         "url": "https://www.electrive.com/category/automobile/",
#         "type": "rss",
#         "rss_url": "https://www.electrive.com/category/automobile/feed/"
#     },
#     "electrive_politics": {
#         "name": "Electrive-Politics",
#         "url": "https://www.electrive.com/category/politics/",
#         "type": "rss", 
#         "rss_url": "https://www.electrive.com/category/politics/feed/"
#     },
#     "marklines": {
#         "name": "MarkLines-CN-News",
#         "url": "https://www.marklines.com/cn/news/tag/181/ev-battery",
#         "type": "html"
#     },
#     "battery_news_de": {
#         "name": "Battery-News-DE",
#         "url": "https://battery-news.de/en/home/",
#         "type": "rss",
#         "rss_url": "https://battery-news.de/en/feed/"
#     },
#     "thelec": {
#         "name": "Thelec",
#         "url": "https://www.thelec.net/news/articleList.html?sc_section_code=S1N4&view_type=sm",
#         "type": "html"
#     },
#     # 官网类（12个）
#     "powerco": {
#         "name": "PowerCo",
#         "url": "https://www.powerco.de/en/news.html",
#         "type": "html"
#     },
#     "catl": {
#         "name": "CATL",
#         "url": "https://www.catl.com/news/",
#         "type": "html"
#     },
#     "sk_on": {
#         "name": "SK On",
#         "url": "http://eng.sk-on.com/company/press.asp",
#         "type": "html"
#     },
#     "samsung_sdi": {
#         "name": "Samsung SDI",
#         "url": "https://www.samsungsdi.com/sdi-now/sdi-news/list.html",
#         "type": "html"
#     },
#     "panasonic": {
#         "name": "Panasonic",
#         "url": "https://news.panasonic.com/global/articles/search/category/all/recent?category=all&type=press",
#         "type": "html"
#     },
#     "tinci": {
#         "name": "天赐材料",
#         "url": "https://www.tinci.com/zxzx/",
#         "type": "html"
#     },
#     "byd": {
#         "name": "BYD",
#         "url": "https://www.byd.com/en/news-list",
#         "type": "html"
#     },
#     "capchem": {
#         "name": "新宙邦 Capchem",
#         "url": "https://www.capchem.com/news/2/",
#         "type": "html"
#     },
#     "rtxc": {
#         "name": "瑞泰新材 RTXC",
#         "url": "http://www.rtxc.com/?list_19/",
#         "type": "html"
#     },
#     "mcgc": {
#         "name": "三菱化学 CGC",
#         "url": "https://www.mcgc.com/english/news_release/index.html",
#         "type": "html"
#     },
#     "dselectera": {
#         "name": "DS Electera",
#         "url": "https://www.dselectera.com/cn/board/board.php?bo_table=press",
#         "type": "html"
#     },
#     # 微信公众号 → PC站点映射（6个）
#     "gaogong_lidian": {
#         "name": "高工锂电",
#         "type": "pc",
#         "base_url": "http://www.gg-lb.com",
#         "list_urls": [
#             "http://www.gg-lb.com/news/list-htm-catid-1.html",
#         ]
#     },
#     "wode_dianchi": {
#         "name": "我的电池网",
#         "type": "pc",
#         "base_url": "https://www.itdcw.com",
#         "list_urls": [
#             "https://www.itdcw.com/",
#             "https://www.itdcw.com/news/top/",
#             "https://www.itdcw.com/news/focus/",
#         ]
#     },
#     "dongli_dianchi": {
#         "name": "动力电池网",
#         "type": "pc",
#         "base_url": "http://www.dldcw.cn",
#         "list_urls": [
#             "http://www.dldcw.cn/M/News/index.html",
#         ]
#     },
#     "xinluo_lidian": {
#         "name": "鑫椤锂电",
#         "type": "pc",
#         "base_url": "http://www.icbattery.com",
#         "list_urls": [
#             "http://www.icbattery.com/news/li_list.php",
#             "http://www.icbattery.com/news/new_energy_vehicles_list.php",
#             "http://www.icbattery.com/news/energy_storage_list.php",
#         ]
#     },
#     "smm_lidian": {
#         "name": "SMM锂电",
#         "type": "pc",
#         "base_url": "https://news.smm.cn",
#         "list_urls": [
#             "https://news.smm.cn/l/94/pid/120",
#             "https://news.smm.cn/l/94/pid/116",
#             "https://news.smm.cn/l/94/pid/139",
#             "https://news.smm.cn/l/94/pages/1",
#         ]
#     },
#     "weike_lidian": {
#         "name": "维科网锂电",
#         "type": "pc",
#         "base_url": "https://libattery.ofweek.com",
#         "list_urls": [
#             "https://libattery.ofweek.com/CATList-36000-8100-libattery.html",
#             "https://libattery.ofweek.com/CATList-36000-8200-libattery.html"
#         ]
#     }
# }

# 话题标签及关键词
TOPIC_TAGS = {
    "政策": ["关税", "贸易壁垒", "补贴", "IRA", "关键原材料法案", "电池护照", 
            "碳足迹", "反补贴", "出口管制", "领导人会晤", "贸易谈判", "政策", "法案", "法规",
            "tariff", "subsidy", "regulation", "IRA", "trade", "export control",
            "policy", "legislation", "battery passport", "carbon footprint"],
    "新能源车": ["电动车", "EV", "电动汽车", "乘用车", "商用车", "新能源车", 
               "新车发布", "销量", "产能", "新能源",
              "electric vehicle", "EV", "plug-in", "hybrid", "BEV", "PHEV",
              "new car", "launch", "model", "sales", "delivery",
              "all-electric", "electric", "charging", "charging point",
              "charger", "充电", "充电桩", "充电站"],
    "储能": ["储能", "ESS", "BESS", "电站", "电网", "调频", "数据中心储能",
            "energy storage", "grid storage", "grid", "BESS", "ESS",
            "power plant", "frequency regulation"],
    "锂电池": ["电池", "锂电", "电芯", "GWh", "TWh", "产线", "4680", "4695", 
              "大圆柱", "钠离子电池", "动力电池",
              "battery", "cell", "lithium", "Li-ion", "sodium-ion", "LFP",
              "NCM", "NCA", "GWh", "TWh", "4680", "4695", "cylindrical",
              "anode", "cathode", "separator", "BMS", "battery management"],
    "固态电池": ["固态", "固液混合", "固态电解质", "硫化物", "氧化物",
               "solid-state", "solid state", "sulfide", "oxide electrolyte",
               "semi-solid", "all-solid"],
    "电解液": ["电解液", "六氟磷酸锂", "LiFSI", "溶剂", "DMC", "EMC", "EC", 
              "DEC", "添加剂", "VC", "FEC", "锂盐",
              "electrolyte", "LiPF6", "solvent", "additive", "LiFSI"],
    "CNT": ["碳纳米管", "CNT", "导电剂", "单壁", "多壁", "导电浆料",
            "carbon nanotube", "CNT", "conductive agent", "SWCNT", "MWCNT"],
    "矿产": ["锂矿", "碳酸锂", "氢氧化锂", "盐湖提锂", "DLE", "钴", "镍", 
            "石墨", "负极材料", "黑粉", "回收", "锂",
            "lithium mine", "lithium carbonate", "lithium hydroxide",
            "cobalt", "nickel", "graphite", "recycling", "black mass",
            "raw material", "mineral", "mining"],
    "新兴应用": ["eVTOL", "飞行汽车", "电动船舶", "机器人", "人形机器人", "AI数据中心",
               "eVTOL", "air taxi", "electric ship", "robot", "data center",
               "humanoid", "drone", "electric aircraft"]
}

# 企业白名单
ENTERPRISE_WHITELIST = {
    "电池企业": ["CATL", "BYD", "LGES", "SK On", "SDI", "Envision AESC", "Gotion", 
                "PowerCo", "Panasonic", "Tesla", "亿纬", "CALB", "国轩高科", 
                "瑞普蓝军", "海辰储能", "欣旺达"],
    "电解液企业": ["天赐Tinci", "新宙邦Capchem", "威海财金", "CGC", "DongWha", "Duksan", 
                  "Elyte", "Enchem", "RTXC", "Soulbrain", "珠海赛纬", "石大胜华", 
                  "昆仑化学", "永太科技", "中华蓝天", "瑞泰新材"]
}

# 噪音过滤关键词
NOISE_KEYWORDS = ["财报", "股价", "股票", "涨停", "跌停", "考虑", "探索", 
                  "计划", "拟", "将", "可能", "或", "广告", "软文", "招聘", 
                  "人事变动", "高管变动"]

# 输出文件路径
RAW_NEWS_FILE = f"{OUTPUT_DIR}\\raw_news.xlsx"
FILTERED_NEWS_FILE = f"{OUTPUT_DIR}\\filtered_news.xlsx"
ORGANIZED_NEWS_FILE = f"{OUTPUT_DIR}\\organized_news.xlsx"
DAILY_REPORT_FILE = f"{OUTPUT_DIR}\\daily_report.txt"
CRAWLER_LOG_FILE = f"{OUTPUT_DIR}\\crawler_report.txt"

# 采集时间范围
DEFAULT_START_DATE = "2026-06-01"
DEFAULT_END_DATE = "2026-06-05"

# API配置 - 从环境变量读取，不要硬编码
import os
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")