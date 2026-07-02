# -*- coding: utf-8 -*-
"""
维科网渠道爬虫
负责维科网锂电的列表页翻页 + 详情页提取
恢复旧代码中的完整采集逻辑
"""

import re
import time
import logging
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

from crawler.base import BaseCrawler

logger = logging.getLogger(__name__)


class OfweekCrawler(BaseCrawler):
    """维科网锂电渠道爬虫"""
    
    def __init__(self, channel_info):
        super().__init__()
        self.channel_info = channel_info
        self.name = channel_info['name']
        self.channel_id = channel_info.get('id', '')
        self.base_url = channel_info.get('base_url', 'https://libattery.ofweek.com')
        self.list_urls = channel_info.get('list_urls', [
            f"{self.base_url}/CATList-36000-8100-libattery.html",
            f"{self.base_url}/CATList-36000-8200-libattery.html",
        ])
    
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
            for page in range(1, 30):
                if page == 1:
                    url = list_url
                else:
                    url = list_url.replace('.html', f'-{page}.html')
                
                resp = self.fetch(url, encoding='gbk')
                if not resp:
                    if page > 2:
                        break
                    continue
                
                soup = BeautifulSoup(resp, 'html.parser')
                articles_found = 0
                newest_date = None
                
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    title = link.get_text(strip=True)
                    
                    if not title or len(title) < 4:
                        continue
                    
                    art_match = re.search(r'/(\d{4})-(\d{2})/ART-\d+-\d+-\d+\.html', href)
                    if not art_match:
                        continue
                    
                    if self.is_duplicate_url(href):
                        continue
                    
                    full_url = href if href.startswith('http') else f"{self.base_url}{href}"
                    
                    summary = ''
                    
                    # 从 URL 提取日期
                    try:
                        pub_date = datetime(int(art_match.group(1)), int(art_match.group(2)), 1)
                    except:
                        continue
                    
                    # 从 DOM 上下文提取精确日期
                    block = link.parent
                    for _ in range(5):
                        if block is None:
                            break
                        text = block.get_text() if hasattr(block, 'get_text') else ''
                        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
                        if date_match:
                            try:
                                pub_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
                                break
                            except:
                                pass
                        block = block.parent if hasattr(block, 'parent') else None
                    
                    if not pub_date:
                        continue
                    
                    if pub_date < start_date:
                        continue
                    
                    if pub_date > end_date + timedelta(days=1):
                        continue
                    
                    # 提取摘要（优先使用详情页内容）
                    article_data = self._extract_article_direct(full_url)
                    if article_data:
                        summary = article_data.get('摘要', '')
                        if not pub_date:
                            pub_date = article_data.get('发布时间', pub_date)
                    
                    # 如果详情页提取失败，尝试从相邻 p 标签提取
                    if not summary or len(summary) < 20:
                        parent_block = link.parent
                        if parent_block:
                            for _ in range(3):
                                parent_block = parent_block.parent
                                if parent_block is None:
                                    break
                            if parent_block:
                                p_tag = parent_block.find('p')
                                if p_tag:
                                    summary = p_tag.get_text(strip=True)[:500]
                    
                    all_articles.append({
                        '标题': title,
                        '链接': full_url,
                        '摘要': summary,
                        '来源': self.name,
                        '发布时间': pub_date,
                        '渠道ID': self.channel_id
                    })
                    articles_found += 1
                    
                    if newest_date is None or pub_date > newest_date:
                        newest_date = pub_date
                
                logger.info(f"  page={page}: {articles_found} 条")
                if articles_found == 0:
                    break
                
                if newest_date and newest_date < start_date:
                    logger.info(f"  最新文章日期早于目标起始日期，停止翻页")
                    break
                
                time.sleep(1.5)
        
        # 去重
        unique = {}
        for a in all_articles:
            if a['链接'] not in unique:
                unique[a['链接']] = a
        all_articles = list(unique.values())
        
        # 确保至少10条
        if len(all_articles) < 10:
            sorted_articles = sorted(all_articles, key=lambda x: x.get('发布时间') or datetime.min, reverse=True)
            all_articles = sorted_articles[:10]
        
        logger.info(f"{self.name}: 采集完成，共 {len(all_articles)} 条")
        return all_articles
    
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