# -*- coding: utf-8 -*-
"""
新闻采集调度器
职责：读取渠道配置 → 遍历渠道 → 调用对应渠道爬虫 → 汇总结果
不再做具体的解析逻辑（交给 crawler/channels/ 下的渠道类）
"""

import yaml
import logging
import pandas as pd
from datetime import datetime
from pathlib import Path

from crawler.channels import CHANNEL_CRAWLERS

logger = logging.getLogger(__name__)

CHANNELS_CONFIG = Path(__file__).parent / 'config' / 'channels.yaml'


class NewsCrawler:
    """新闻采集调度器"""
    
    def __init__(self):
        self.results = []
        self.channels_config = self._load_config()
    
    def _load_config(self):
        """加载渠道配置文件"""
        try:
            with open(CHANNELS_CONFIG, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"已加载渠道配置: {len(config)} 个渠道")
            return config
        except Exception as e:
            logger.error(f"加载渠道配置失败: {e}")
            return {}
    
    def run(self, start_date, end_date, channels=None):
        """
        运行所有渠道的采集
        
        Args:
            start_date: 开始日期（datetime 对象）
            end_date: 结束日期（datetime 对象）
            channels: 要采集的渠道ID列表，None 表示全部
        
        Returns:
            采集到的文章列表
        """
        logger.info(f"开始采集: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        
        if channels is None:
            channels = list(self.channels_config.keys())
        
        for channel_id in channels:
            if channel_id not in self.channels_config:
                logger.warning(f"渠道 {channel_id} 不在配置中，跳过")
                continue
            
            channel_info = self.channels_config[channel_id]
            channel_info['id'] = channel_id
            
            # 获取渠道爬虫类
            if channel_id in CHANNEL_CRAWLERS:
                crawler_class = CHANNEL_CRAWLERS[channel_id]
            else:
                logger.warning(f"渠道 {channel_id} 无对应爬虫类，跳过")
                continue
            
            try:
                crawler = crawler_class(channel_info)
                articles = crawler.crawl(start_date, end_date)
                self.results.extend(articles)
                logger.info(f"  {channel_info['name']}: {len(articles)} 条")
                
            except Exception as e:
                logger.error(f"采集失败 {channel_info['name']}: {e}")
        
        logger.info(f"全部采集完成: {len(self.results)} 条")
        return self.results
    
    def save(self, output_path):
        """保存采集结果到 Excel"""
        if not self.results:
            logger.warning("无采集结果，不保存")
            return
        
        df = pd.DataFrame(self.results)
        
        if '发布时间' in df.columns:
            df['发布时间'] = df['发布时间'].apply(
                lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, datetime) else str(x)
            )
        
        before = len(df)
        if '链接' in df.columns:
            df = df.drop_duplicates(subset=['链接'], keep='first')
            logger.info(f"URL 去重: {before} → {len(df)} 条")
        
        df.to_excel(output_path, index=False)
        logger.info(f"已保存: {output_path} ({len(df)} 条)")