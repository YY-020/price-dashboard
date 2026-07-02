# -*- coding: utf-8 -*-
"""
PC站点通用爬虫基类
提供列表页解析和详情页提取的通用逻辑
"""

import re
import time
import logging
from datetime import datetime, timedelta
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from crawler.base import BaseCrawler
from crawler.html import HTMLCrawler

logger = logging.getLogger(__name__)


class PCCrawler(BaseCrawler):
    """PC站点通用爬虫基类"""
    
    def __init__(self, channel_info):
        super().__init__()
        self.channel_info = channel_info
        self.name = channel_info['name']
        self.channel_id = channel_info.get('id', '')
        self.base_url = channel_info.get('base_url', '')
        self.list_urls = channel_info.get('list_urls', [])
    
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
        
        for list_url in self.list_urls:
            logger.info(f"  抓取列表: {list_url}")
            articles = self._crawl_list_page(list_url, start_date, end_date)
            all_articles.extend(articles)
        
        unique = {}
        for a in all_articles:
            if a['链接'] not in unique:
                unique[a['链接']] = a
        all_articles = list(unique.values())
        
        if len(all_articles) < 10:
            sorted_articles = sorted(all_articles, key=lambda x: x.get('发布时间') or datetime.min, reverse=True)
            all_articles = sorted_articles[:10]
        
        logger.info(f"{self.name}: 采集完成，共 {len(all_articles)} 条")
        return all_articles
    
    def _crawl_list_page(self, list_url, start_date, end_date):
        """
        抓取列表页
        
        Args:
            list_url: 列表页URL
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            文章列表
        """
        articles = []
        
        try:
            response = self.fetch(list_url, timeout=15)
            if not response:
                return articles
            
            soup = BeautifulSoup(response, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                title = link.get_text(strip=True)
                
                if not title or len(title) < 4:
                    continue
                
                if not self._is_valid_article_url(href):
                    continue
                
                full_url = urljoin(self.base_url, href)
                
                if self.is_duplicate_url(full_url):
                    continue
                
                pub_date = self._extract_date(list_url, link)
                
                if pub_date and pub_date < start_date - timedelta(days=7):
                    continue
                
                if pub_date and pub_date > end_date + timedelta(days=1):
                    continue
                
                articles.append({
                    '标题': title,
                    '链接': full_url,
                    '摘要': '',
                    '来源': self.name,
                    '发布时间': pub_date or datetime.now(),
                    '渠道ID': self.channel_id
                })
                
                if len(articles) >= 20:
                    break
            
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"  抓取列表页异常 {list_url}: {e}")
        
        return articles
    
    def _extract_article_direct(self, url):
        """直接用BeautifulSoup提取文章内容，不依赖newspaper4k"""
        try:
            response = self.fetch(url, timeout=10)
            if not response:
                return None
            
            soup = BeautifulSoup(response, 'html.parser')
            
            title = ''
            for tag in ['h1', 'h2', '.title', '.article-title', '.news-title']:
                elem = soup.select_one(tag)
                if elem:
                    title = elem.get_text(strip=True)
                    break
            
            content_text = ''
            content_selectors = [
                '.article-content', '.content', '.article-body', '.detail-content',
                '.main-content', '.news-content', '.article_text', '.text_content',
                '#article-content', '#content', '#article-body', '.body'
            ]
            for selector in content_selectors:
                elem = soup.select_one(selector)
                if elem:
                    content_text = elem.get_text(strip=True)
                    break
            
            if not content_text:
                paragraphs = soup.find_all('p')
                if paragraphs:
                    content_text = '\n'.join(p.get_text(strip=True) for p in paragraphs)
            
            if not title:
                title = soup.title.get_text(strip=True) if soup.title else ''
            
            if not title or len(title) < 5:
                return None
            
            if len(content_text) < 20:
                return None
            
            pub_date = None
            date_patterns = [
                r'(\d{4}-\d{2}-\d{2})',
                r'(\d{4}/\d{2}/\d{2})',
                r'(\d{4}年\d{1,2}月\d{1,2}日)',
                r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})'
            ]
            for pattern in date_patterns:
                match = re.search(pattern, content_text[:500])
                if match:
                    try:
                        if '年' in match.group(1):
                            pub_date = datetime.strptime(match.group(1), '%Y年%m月%d日')
                        elif '/' in match.group(1):
                            pub_date = datetime.strptime(match.group(1), '%Y/%m/%d')
                        elif ' ' in match.group(1):
                            pub_date = datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S')
                        else:
                            pub_date = datetime.strptime(match.group(1), '%Y-%m-%d')
                        break
                    except:
                        pass
            
            return {
                '标题': title,
                '链接': url,
                '摘要': content_text[:500],
                '发布时间': pub_date
            }
            
        except Exception as e:
            logger.warning(f"直接提取文章失败 {url[:80]}: {e}")
            return None
    
    def _is_valid_article_url(self, href):
        """判断是否为有效文章URL"""
        share_patterns = [
            r'api\.qrserver\.com', r'service\.weibo\.com',
            r'connect\.qq\.com', r'sns\.qzone\.qq\.com'
        ]
        for pattern in share_patterns:
            if re.search(pattern, href, re.IGNORECASE):
                return False
        
        article_patterns = [
            r'/article/', r'/news/\d+', r'/detail/', r'/content/',
            r'/ART-', r'/html/', r'\.html$', r'\.php\?'
        ]
        
        for pattern in article_patterns:
            if re.search(pattern, href, re.IGNORECASE):
                return True
        
        exclude_patterns = [
            r'/list/', r'/category/', r'/tag/', r'/page/',
            r'/index\.', r'/home', r'/about', r'/contact',
            r'/login', r'/register', r'/search', r'/l/'
        ]
        
        for pattern in exclude_patterns:
            if re.search(pattern, href, re.IGNORECASE):
                return False
        
        return True
    
    def _extract_date(self, list_url, link):
        """从链接上下文中提取日期"""
        parent = link.parent
        for _ in range(3):
            if parent is None:
                break
            
            text = parent.get_text() if hasattr(parent, 'get_text') else ''
            
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
            if date_match:
                try:
                    return datetime.strptime(date_match.group(1), '%Y-%m-%d')
                except:
                    pass
            
            date_match = re.search(r'(\d{4}/\d{2}/\d{2})', text)
            if date_match:
                try:
                    return datetime.strptime(date_match.group(1), '%Y/%m/%d')
                except:
                    pass
            
            date_match = re.search(r'(\d{4}年\d{1,2}月\d{1,2}日)', text)
            if date_match:
                try:
                    return datetime.strptime(date_match.group(1), '%Y年%m月%d日')
                except:
                    pass
            
            parent = parent.parent
        
        date_in_url = re.search(r'/(\d{4})[-/](\d{2})[-/](\d{2})/', link.get('href', ''))
        if date_in_url:
            try:
                return datetime(
                    int(date_in_url.group(1)),
                    int(date_in_url.group(2)),
                    int(date_in_url.group(3))
                )
            except:
                pass
        
        return None
