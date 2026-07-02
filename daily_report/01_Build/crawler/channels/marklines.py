# -*- coding: utf-8 -*-
"""
MarkLines 渠道爬虫
负责 MarkLines-CN-News 的列表页采集和详情页提取
"""

import logging
from datetime import datetime, timedelta
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from crawler.base import BaseCrawler

logger = logging.getLogger(__name__)


class MarkLinesCrawler(BaseCrawler):
    """MarkLines 渠道爬虫"""
    
    def __init__(self, channel_info):
        super().__init__()
        self.channel_info = channel_info
        self.name = channel_info['name']
        self.channel_id = channel_info.get('id', '')
        self.base_url = channel_info.get('url', '')
    
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
        
        logger.info(f"  抓取列表: {self.base_url}")
        
        try:
            response = self.fetch(self.base_url, timeout=15)
            if not response:
                return all_articles
            
            soup = BeautifulSoup(response, 'html.parser')
            
            article_blocks = soup.find_all('div', class_='news-card-text-area')
            if not article_blocks:
                article_blocks = soup.find_all('article')
            if not article_blocks:
                article_blocks = soup.find_all('div', class_=['news-item', 'list-item', 'article-item'])
            
            for block in article_blocks:
                links = block.find_all('a')
                if not links:
                    continue
                
                full_url = None
                title = ''
                for link in links:
                    href = link.get('href', '')
                    if href.startswith('/cn/news/') and '/news/search' not in href:
                        full_url = urljoin(self.base_url, href)
                        title = link.get_text(strip=True)
                        break
                
                if not full_url:
                    continue
                
                if self.is_duplicate_url(full_url):
                    continue
                
                date_str = ''
                date_tags = block.find_all(['time', 'span', 'div'])
                for tag in date_tags:
                    text = tag.get_text(strip=True)
                    if any(char.isdigit() for char in text):
                        date_str = text
                        break
                
                pub_date = self._parse_date(date_str)
                
                summary = self._extract_summary(full_url)
                
                all_articles.append({
                    '标题': title,
                    '链接': full_url,
                    '摘要': summary[:500] if summary else title,
                    '来源': self.name,
                    '发布时间': pub_date or datetime.now(),
                    '渠道ID': self.channel_id
                })
                
        except Exception as e:
            logger.error(f"  MarkLines 采集异常: {e}")
        
        # 日期过滤
        filtered = []
        for article in all_articles:
            pub_date = article.get('发布时间')
            if pub_date:
                if pub_date > end_date + timedelta(days=1):
                    continue
                if pub_date < start_date - timedelta(days=30):
                    continue
            filtered.append(article)
        
        # 确保至少10条
        if len(filtered) < 10:
            sorted_articles = sorted(all_articles, key=lambda x: x.get('发布时间') or datetime.min, reverse=True)
            filtered = sorted_articles[:10]
        
        logger.info(f"{self.name}: 采集完成，共 {len(filtered)} 条")
        return filtered
    
    def _extract_summary(self, url):
        """直接用BeautifulSoup提取文章摘要"""
        try:
            response = self.fetch(url, timeout=10)
            if not response:
                return ''
            
            soup = BeautifulSoup(response, 'html.parser')
            
            content_selectors = [
                '.news-detail-content', '.article-content', '.content', '.article-body',
                '.detail-content', '.main-content', '.news-content', '.article_text',
                '#article-content', '#content', '#article-body', '.body'
            ]
            
            for selector in content_selectors:
                elem = soup.select_one(selector)
                if elem:
                    return elem.get_text(strip=True)
            
            paragraphs = soup.find_all('p')
            if paragraphs:
                return '\n'.join(p.get_text(strip=True) for p in paragraphs)
            
            return ''
            
        except Exception as e:
            logger.warning(f"提取摘要失败 {url[:80]}: {e}")
            return ''
    
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
            '%d.%m.%Y',
            '%Y年%m月%d日',
            '%m月%d日',
        ]
        
        for fmt in formats:
            try:
                if '%m月%d日' in fmt and not '年' in date_str:
                    return datetime.strptime(f"{datetime.now().year}年{date_str}", '%Y年%m月%d日')
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
