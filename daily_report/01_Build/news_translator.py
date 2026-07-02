# -*- coding: utf-8 -*-
"""
新闻翻译模块
仅负责英文→中文翻译
不做摘要生成（摘要生成由 news_summarizer.py 负责）
"""

import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TRANSLATE_PROMPT = """将以下英文新闻翻译成中文。

要求：
- 标题：简洁有力，20-30字
- 摘要：时间+事件+关键数字+影响，30-50字

英文标题: {title}
英文摘要: {summary}

严格返回JSON格式，不要包含其他文字:
{{"title_cn": "中文标题", "summary_cn": "中文摘要"}}"""


class NewsTranslator:
    """新闻翻译器，仅负责英文→中文翻译"""
    
    def __init__(self, api_key):
        from utils.llm_client import LLMClient
        self.client = LLMClient(api_key)
    
    def translate(self, input_path, output_path):
        """
        主流程：读取筛选后新闻 → 翻译保留的英文新闻 → 输出
        
        Args:
            input_path: 输入 Excel 文件路径
            output_path: 输出 Excel 文件路径
        """
        df = pd.read_excel(input_path)
        
        if '标题_CN' not in df.columns:
            df['标题_CN'] = ''
        if '摘要_CN' not in df.columns:
            df['摘要_CN'] = ''
        
        to_translate = df[df['筛选结果'] == '保留'].copy()
        
        if len(to_translate) == 0:
            logger.info("没有需要翻译的新闻")
            df.to_excel(output_path, index=False)
            return df
        
        logger.info(f"需要翻译 {len(to_translate)} 条新闻")
        
        for idx in to_translate.index:
            title = df.at[idx, '标题']
            summary = df.at[idx, '摘要']
            
            # 检查是否已是中文（简单判断：包含中文字符）
            if any('\u4e00' <= c <= '\u9fff' for c in str(title)):
                df.at[idx, '标题_CN'] = title
                df.at[idx, '摘要_CN'] = summary
                continue
            
            prompt = TRANSLATE_PROMPT.format(title=title, summary=summary)
            
            result = self.client.call_json(prompt)
            
            if result:
                df.at[idx, '标题_CN'] = result.get('title_cn', title)
                df.at[idx, '摘要_CN'] = result.get('summary_cn', summary)
                logger.info(f"翻译完成 [{idx}]: {result.get('title_cn', '')[:30]}")
            else:
                df.at[idx, '标题_CN'] = title
                df.at[idx, '摘要_CN'] = summary
                logger.warning(f"翻译失败，使用原文 [{idx}]")
        
        df.to_excel(output_path, index=False)
        logger.info(f"翻译完成，输出: {output_path}")
        
        return df