# -*- coding: utf-8 -*-
"""
新闻整理模块
调用 DeepSeek API 理解新闻内容，输出标准化标签
只做理解和分类，不做筛选决策
"""

import pandas as pd
import requests
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================
# DeepSeek API 调用
# ============================================================

def call_deepseek(prompt, api_key):
    """调用 DeepSeek API，返回结构化 JSON"""
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1  # 低温度，确保输出稳定
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        logger.error(f"API 调用失败: {e}")
        return None

# ============================================================
# 提示词模板
# ============================================================

ORGANIZER_PROMPT = """
你是一位锂电/电解液/CNT行业市场分析师。请分析以下新闻，输出JSON格式的结构化标签。

新闻标题: {title}
新闻来源: {source}
新闻摘要: {summary}

【输出字段（严格使用以下标准选项，不要自由发挥）】

1. 产业链 (industry_chain): 新闻涉及哪个产业链环节？
   标准选项: 政策 / EV / ESS / 新兴应用 / 锂电池 / 固态电池 / 电解液 / CNT / 矿 / 电池回收 / 其他

2. 动态类型 (event_type): 这是什么类型的商业动态？
   标准选项: 政策法规 / 趋势数据 / 重大技术 / 产能变动 / 订单 / 收并购 / 新产品发布 / 其他
   - 政策法规: 关税、补贴、排放标准、IRA、CRMA、电池法规
   - 趋势数据: 市场排名、渗透率、出货量统计
   - 重大技术: 技术突破、专利发布、新工艺
   - 产能变动: 建厂、扩产、停产、产能规划
   - 订单: 供货协议、采购合同、定点通知
   - 收并购: 上市、融资、收购、合并
   - 新产品发布: 新车型发布、新产品推出
   - 其他: 无法归类

3. 重要性 (importance): 对行业的影响程度。
   标准选项: 高 / 中 / 低
   - 高: 直接涉及电池/电解液/CNT产业链的实质性变动（产能、订单、技术突破、政策冲击、收并购）
   - 中: 涉及新能源车/储能/固态电池的行业趋势数据、重大动态，但与核心产业链不直接相关
   - 低: 仅沾边，无实质性产业链影响（如单一车型发布、常规评测、地方性消费补贴）

4. 地区 (region): 事件发生地。
   标准选项: 中国 / 欧洲 / 美国 / 全球 / 其他
   - 中国企业在海外建厂 → 按建厂地标记（如在匈牙利建厂→欧洲）
   - 涉及多个地区 → 全球
   - 日本、印度、巴西、土耳其、东南亚等 → 其他

5. 涉及企业 (enterprises): 从以下白名单中识别，使用标准化名称。无则返回空数组 []。
   电池企业: 宁德时代(CATL)、比亚迪(BYD)、LGES、SK On、三星SDI、远景AESC、国轩高科(Gotion)、PowerCo、松下(Panasonic)、特斯拉(Tesla)、亿纬(EVE)、中创新航(CALB)、瑞普兰钧(REPT)、海辰储能(Hithium)、欣旺达(Sunwoda)
   电解液企业: 天赐(Tinci)、新宙邦(Capchem)、威海财金、中央硝子(CGC)、东和化成(DongWha)、德山(Duksan)、Elyte、亿恩科(Enchem)、瑞泰新材(RTXC)、Soulbrain、珠海赛纬(Smoothway)、石大胜华(Shinghwa)、昆仑化学(Kunlun)、永太科技(Yonta)、中华蓝天(SINOCHEM LANTIAN)

6. 判断理由 (reason): 一句话说明为什么标记为该产业链和动态类型，20字以内。

【输出格式】
严格返回JSON对象，不要包含任何其他文字:
{{
  "industry_chain": "标准选项之一",
  "event_type": "标准选项之一",
  "importance": "高/中/低",
  "region": "标准选项之一",
  "enterprises": ["企业名1", "企业名2"],
  "reason": "判断理由"
}}

【重要规则】
- 单一车型发布/评测/交付 → industry_chain=EV, event_type=新产品发布, importance=低
- 地方性消费补贴（仅影响单一城市或单一车型）→ industry_chain=政策, event_type=政策法规, importance=低
- 电池回收/梯次利用/退役电池储能 → industry_chain=锂电池, event_type=其他, importance=低
- 车企投资电池工厂/自研电池 → industry_chain=锂电池, event_type=产能变动, importance=高
- 固态电池产品发布/装车 → industry_chain=固态电池, event_type=新产品发布, importance=中
- 固态电池技术突破/路线确定 → industry_chain=固态电池, event_type=重大技术, importance=高
- 退役电池梯次利用/储能项目 → 产业链=电池回收，动态类型=其他，重要性=低
- 自动驾驶测试/法规/跨境运营 → 重要性=低（与电池产业链无关）
"""

# ============================================================
# 新闻整理主类
# ============================================================

class NewsOrganizer:
    def __init__(self, api_key=None):
        from constants import DEEPSEEK_API_KEY
        self.api_key = api_key or DEEPSEEK_API_KEY

    def organize(self, raw_news_path, output_path):
        """主流程：读取raw_news → 逐条调用API → 输出organized_news"""
        df = pd.read_excel(raw_news_path)
        
        # 新增字段
        df['产业链'] = ''
        df['动态类型'] = ''
        df['重要性'] = ''
        df['地区'] = ''
        df['涉及企业'] = ''
        df['判断理由'] = ''

        for idx, row in df.iterrows():
            title = row.get('标题', '')
            summary = row.get('摘要', '')
            source = row.get('来源', '')

            # 检查摘要有效性：如果摘要与标题相同或过短，使用标题代替
            if pd.isna(summary) or len(str(summary)) < 20 or str(summary) == str(title):
                summary = title

            prompt = ORGANIZER_PROMPT.format(
                title=title,
                source=source,
                summary=summary
            )

            result = call_deepseek(prompt, self.api_key)
            if result:
                try:
                    # 清理可能的markdown代码块标记
                    result = result.strip()
                    if result.startswith('```'):
                        result = result.split('\n', 1)[1]
                        if result.endswith('```'):
                            result = result[:-3]
                    
                    tags = json.loads(result)
                    df.at[idx, '产业链'] = tags.get('industry_chain', '')
                    df.at[idx, '动态类型'] = tags.get('event_type', '')
                    df.at[idx, '重要性'] = tags.get('importance', '')
                    df.at[idx, '地区'] = tags.get('region', '')
                    df.at[idx, '涉及企业'] = ','.join(tags.get('enterprises', []))
                    df.at[idx, '判断理由'] = tags.get('reason', '')
                    
                    logger.info(f"[{idx+1}/{len(df)}] {tags.get('industry_chain')} | {tags.get('event_type')} | {title[:50]}")
                except Exception as e:
                    logger.error(f"JSON解析失败 [{idx}]: {e}")
                    # 解析失败时填入默认值
                    df.at[idx, '产业链'] = '其他'
                    df.at[idx, '动态类型'] = '其他'
                    df.at[idx, '重要性'] = '低'
                    df.at[idx, '地区'] = '其他'
                    df.at[idx, '判断理由'] = 'API解析失败'
            else:
                # API调用失败时填入默认值
                df.at[idx, '产业链'] = '其他'
                df.at[idx, '动态类型'] = '其他'
                df.at[idx, '重要性'] = '低'
                df.at[idx, '地区'] = '其他'
                df.at[idx, '判断理由'] = 'API调用失败'

        df.to_excel(output_path, index=False)
        logger.info(f"整理完成，输出: {output_path}")
        
        # 输出统计
        logger.info(f"产业链分布: {df['产业链'].value_counts().to_dict()}")
        logger.info(f"动态类型分布: {df['动态类型'].value_counts().to_dict()}")
        logger.info(f"重要性分布: {df['重要性'].value_counts().to_dict()}")
        
        return df