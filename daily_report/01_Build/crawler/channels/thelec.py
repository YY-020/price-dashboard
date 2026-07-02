# -*- coding: utf-8 -*-
"""
Thelec 渠道爬虫
负责 Thelec 的列表页采集和详情页提取
"""

import logging
from datetime import datetime, timedelta
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from crawler.base import BaseCrawler
from crawler.html import HTMLCrawler

logger = logging.getLogger(__name__)


class ThelecCrawler(BaseCrawler):
    """Thelec 渠道爬虫"""
    
    def __init__(self, channel_info):
        super().__init__()
        self.channel_info = channel_info
        self.name = channel_info['name']
        self.channel_id = channel_info.get('id', '')
        self.base_url = "https://www.thelec.net"
        self.list_url = channel_info.get('url', '')
        self.html_crawler = HTMLCrawler()
    
    def crawl(self, start_date, end_date):
        """
        采集指定日期范围的新闻
        
        Args:
            start_date: datetime 对象
            end_date: datetime 对象
        
        Returns:
            文章列表
        """
        all_articles = []
        
        logger.info(f"  抓取列表: {self.list_url}")
        
        try:
            response = self.fetch(self.list_url)
            if not response:
                return all_articles
            
            soup = BeautifulSoup(response, 'html.parser')
            
            article_blocks = soup.find_all('div', class_='list-item')
            if not article_blocks:
                article_blocks = soup.find_all('div', class_=['article-item', 'news-item'])
            
            for block in article_blocks:
                link = block.find('a')
                if not link:
                    continue
                
                href = link.get('href', '')
                if not href:
                    continue
                
                full_url = urljoin(self.base_url, href)
                
                if self.is_duplicate_url(full_url):
                    continue
                
                title = link.get_text(strip=True)
                
                date_str = ''
                date_elem = block.find('span', class_=['date', 'time'])
                if date_elem:
                    date_str = date_elem.get_text(strip=True)
                
                pub_date = self._parse_date(date_str)
                
                if pub_date and pub_date > end_date + timedelta(days=1):
                    continue
                
                if pub_date and pub_date < start_date - timedelta(days=3):
                    continue
                
                article_data = self.html_crawler.extract_article(full_url, self.name, language='zh')
                summary = article_data.get('摘要', '') if article_data else ''
                
                if pub_date is None and article_data:
                    pub_date = article_data.get('发布时间')
                
                all_articles.append({
                    '标题': title,
                    '链接': full_url,
                    '摘要': summary[:500] if summary else title,
                    '来源': self.name,
                    '发布时间': pub_date or datetime.now(),
                    '渠道ID': self.channel_id
                })
                
        except Exception as e:
            logger.error(f"  Thelec 采集异常: {e}")
        
        # 确保至少10条
        if len(all_articles) < 10:
            sorted_articles = sorted(all_articles, key=lambda x: x.get('发布时间') or datetime.min, reverse=True)
            all_articles = sorted_articles[:10]
        
        logger.info(f"{self.name}: 采集完成，共 {len(all_articles)} 条")
        return all_articles
    
    def _parse_date(self, date_str):
        """解析日期字符串"""
        if not date_str:
            return None
        
        date_str = date_str.strip()
        
        formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%m-%d-%Y',
            '%m/%d/%Y',
            '%Y.%m.%d',
            '%Y년 %m월 %d일',
            '%Y年%m月%d日',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
