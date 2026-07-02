# -*- coding: utf-8 -*-
"""
新闻筛选模块
基于 organized 输出的标准化标签做硬性筛选
只做决策，不理解内容
"""

import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class NewsFilter:
    """基于标准化标签的新闻筛选器"""
    
    def __init__(self):
        # 目标地区列表
        self.target_regions = ['中国', '欧洲', '美国', '全球']
    
    def filter(self, organized_path, output_path):
        """
        主流程：读取 organized_news → 逐条判断 → 输出 filtered_news
        
        筛选规则：
        1. 重要性=高 → 保留，⭐高
        2. 重要性=中 → 保留，●中
        3. 重要性=低 → 排除
        4. 地区=其他 + 产业链≠矿 → 排除（兜底规则）
        5. 地区=其他 + 产业链=矿 + 重要性=高 → 保留，⭐高
        """
        df = pd.read_excel(organized_path)
        
        # 初始化筛选结果列
        df['筛选结果'] = ''
        df['删除原因'] = ''
        df['优先级'] = ''
        
        for idx, row in df.iterrows():
            importance = row.get('重要性', '')
            region = row.get('地区', '')
            industry = row.get('产业链', '')
            enterprises = row.get('涉及企业', '')
            
            # 规则1：重要性=高 → 保留
            if importance == '高':
                df.at[idx, '筛选结果'] = '保留'
                # 产业链属于核心关注 → ⭐高，其他 → ●中
                if industry in ['锂电池', '电解液', 'CNT', '政策', '矿']:
                    df.at[idx, '优先级'] = '⭐高'
                else:
                    df.at[idx, '优先级'] = '●中'
                continue
            
            # 规则2：重要性=中 → 保留
            if importance == '中':
                df.at[idx, '筛选结果'] = '保留'
                df.at[idx, '优先级'] = '●中'
                continue
            
            # 规则3：重要性=低 → 排除
            if importance == '低':
                df.at[idx, '筛选结果'] = '排除'
                df.at[idx, '删除原因'] = f'重要性低（{industry}+{df.at[idx, "动态类型"]}），无产业链影响'
                continue
            
            # 规则5：地区=其他 + 产业链≠矿 → 排除（兜底）
            if region == '其他' and industry != '矿':
                df.at[idx, '筛选结果'] = '排除'
                df.at[idx, '删除原因'] = f'地区为{region}，非目标市场'
                continue
            
            # 规则6：地区=其他 + 产业链=矿 + 重要性=高 → 保留（已在规则1处理，此处兜底）
            if region == '其他' and industry == '矿' and importance == '高':
                df.at[idx, '筛选结果'] = '保留'
                df.at[idx, '优先级'] = '⭐高'
                continue
            
            # 其余情况默认排除
            df.at[idx, '筛选结果'] = '排除'
            df.at[idx, '删除原因'] = '未匹配任何保留规则'
        
        # 统计
        kept = len(df[df['筛选结果'] == '保留'])
        deleted = len(df[df['筛选结果'] == '排除'])
        review = len(df[df['筛选结果'] == '待人工审核'])
        
        logger.info(f"筛选完成: 保留 {kept} 条, 排除 {deleted} 条, 待审核 {review} 条")
        
        if deleted > 0:
            del_df = df[df['筛选结果'] == '排除']
            logger.info("删除原因分布:")
            for reason, count in del_df['删除原因'].value_counts().items():
                logger.info(f"  - {reason}: {count} 条")
        
        # 输出列顺序
        output_columns = [
            '标题', '链接', '摘要', '来源', '发布时间', '渠道ID',
            '产业链', '动态类型', '重要性', '地区', '涉及企业',
            '筛选结果', '删除原因', '优先级'
        ]
        # 只保留实际存在的列
        existing_columns = [c for c in output_columns if c in df.columns]
        df[existing_columns].to_excel(output_path, index=False)
        
        logger.info(f"筛选结果已保存: {output_path}")
        
        return df