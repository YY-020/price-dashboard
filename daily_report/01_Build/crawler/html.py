# -*- coding: utf-8 -*-
"""
正文提取器
封装 newspaper4k，对给定 URL 提取标题、正文、发布日期
不包含任何渠道特定逻辑，不包含列表页爬取逻辑
"""

import logging
from datetime import datetime
from newspaper import Article, Config

from crawler.base import BaseCrawler

logger = logging.getLogger(__name__)


class HTMLCrawler(BaseCrawler):
    """HTML 渠道正文提取器，使用 newspaper4k"""
    
    def __init__(self):
        super().__init__()
        self.news_config = Config()
        self.news_config.fetch_images = False
        self.news_config.memoize_articles = False
    
    def extract_article(self, url, channel_name, language='zh'):
        """
        使用 newspaper4k 提取单篇文章
        
        Args:
            url: 文章详情页 URL
            channel_name: 来源名称
            language: 文章语言
        
        Returns:
            dict（标题/链接/摘要/来源/发布时间）或 None
        """
        article = Article(url, language=language, config=self.news_config)
        
        try:
            article.download()
            article.parse()
        except Exception as e:
            logger.warning(f"newspaper4k 下载/解析失败 {url[:80]}: {e}")
            return None
        
        title = article.title or ''
        text = article.text or ''
        publish_date = article.publish_date
        
        if not title or len(title) < 5:
            logger.warning(f"标题过短，跳过: {url[:80]}")
            return None
        
        if len(text) < 20:
            logger.warning(f"正文过短，跳过: {url[:80]}")
            return None
        
        return {
            '标题': title.strip(),
            '链接': url,
            '摘要': text[:500],
            '来源': channel_name,
            '发布时间': publish_date,
        }