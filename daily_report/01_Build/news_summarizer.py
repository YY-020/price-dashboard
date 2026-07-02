# -*- coding: utf-8 -*-
"""
新闻摘要生成器
为中文新闻生成高质量摘要
针对维科网等无现成摘要的渠道
"""

import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SUMMARIZE_PROMPT = """
你是一位锂电/电解液/CNT行业市场分析师。请为以下中文新闻生成一句话摘要。

要求：
- 包含时间、事件、关键数字、影响
- 简洁有力，30-50字
- 突出对产业链的影响

新闻标题: {title}
新闻摘要: {summary}

请直接输出摘要文本，不要包含任何其他内容：
"""


class NewsSummarizer:
    """新闻摘要生成器"""
    
    def __init__(self, api_key):
        from utils.llm_client import LLMClient
        self.client = LLMClient(api_key)
    
    def summarize(self, input_path, output_path):
        """
        主流程：读取新闻 → 为中文新闻生成摘要 → 输出
        
        Args:
            input_path: 输入 Excel 文件路径
            output_path: 输出 Excel 文件路径
        """
        df = pd.read_excel(input_path)
        
        if '摘要_CN' not in df.columns:
            df['摘要_CN'] = ''
        
        to_summarize = df[df['筛选结果'] == '保留'].copy()
        
        if len(to_summarize) == 0:
            logger.info("没有需要生成摘要的新闻")
            df.to_excel(output_path, index=False)
            return df
        
        logger.info(f"需要生成摘要 {len(to_summarize)} 条")
        
        for idx in to_summarize.index:
            title = df.at[idx, '标题']
            summary = df.at[idx, '摘要']
            
            # 如果已有中文摘要且非空，跳过
            if '摘要_CN' in df.columns and df.at[idx, '摘要_CN']:
                continue
            
            prompt = SUMMARIZE_PROMPT.format(title=title, summary=summary)
            
            result = self.client.call(prompt, temperature=0.2)
            
            if result:
                df.at[idx, '摘要_CN'] = result.strip()
                logger.info(f"摘要生成 [{idx}]: {result.strip()[:30]}")
            else:
                df.at[idx, '摘要_CN'] = summary[:100]
                logger.warning(f"摘要生成失败，使用原文前100字 [{idx}]")
        
        df.to_excel(output_path, index=False)
        logger.info(f"摘要生成完成，输出: {output_path}")
        
        return df