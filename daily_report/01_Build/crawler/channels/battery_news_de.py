# -*- coding: utf-8 -*-
"""
Battery-News-DE 渠道爬虫
负责 Battery-News-DE 的 RSS 采集
"""

import logging
from datetime import datetime, timedelta

from crawler.rss import RSSParser

logger = logging.getLogger(__name__)


class BatteryNewsDECrawler:
    """Battery-News-DE RSS 渠道爬虫"""
    
    def __init__(self, channel_info):
        self.channel_info = channel_info
        self.name = channel_info['name']
        self.channel_id = channel_info.get('id', '')
    
    def crawl(self, start_date, end_date):
        """
        采集指定日期范围的新闻
        
        Args:
            start_date: datetime 对象
            end_date: datetime 对象
        
        Returns:
            文章列表
        """
        parser = RSSParser()
        articles = parser.crawl_rss(self.channel_id, self.channel_info)
        
        filtered = [
            a for a in articles
            if a.get('发布时间') and start_date <= a['发布时间'] <= end_date + timedelta(days=1)
        ]
        
        if len(filtered) < 10:
            sorted_articles = sorted(articles, key=lambda x: x.get('发布时间') or datetime.min, reverse=True)
            filtered = sorted_articles[:10]
        
        logger.info(f"{self.name}: 采集 {len(articles)} 条，日期过滤后 {len(filtered)} 条")
        return filtered
