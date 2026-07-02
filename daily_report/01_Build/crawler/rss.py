# -*- coding: utf-8 -*-
"""
RSS 解析器
只做 RSS/Atom XML 解析，不包含任何渠道特定逻辑
"""

import logging
import requests
from bs4 import BeautifulSoup

from crawler.utils import parse_rss_date, extract_date_from_url, extract_date_from_title
from crawler.utils import should_block_url, should_block_title, clean_html

logger = logging.getLogger(__name__)


class RSSParser:
    """RSS/Atom Feed 解析器，支持日期解析、内容提取、URL/标题过滤"""

    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })

    def crawl_rss(self, channel_id, channel_info):
        """采集 RSS 订阅源"""
        try:
            rss_url = channel_info.get('rss_url') or channel_info.get('url', '')
            if not rss_url:
                logger.error(f"RSS采集失败 {channel_info['name']}: 无 RSS URL")
                return []
            logger.info(f"正在采集 RSS: {channel_info['name']}")
            response = self.session.get(rss_url, timeout=30)
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}")

            soup = BeautifulSoup(response.text, 'xml')
            news_list = []
            items = soup.find_all('item')
            if not items:
                items = soup.find_all('entry')

            for item in items:
                try:
                    title_tag = item.find('title')
                    title = title_tag.get_text(strip=True) if title_tag else ''

                    link_tag = item.find('link')
                    if link_tag:
                        link = link_tag.get('href') if link_tag.get('href') else link_tag.get_text(strip=True)
                    else:
                        link = ''

                    if should_block_url(link):
                        continue
                    if should_block_title(title):
                        continue

                    summary_tag = item.find('description') or item.find('summary')
                    summary = clean_html(summary_tag.get_text(strip=True)) if summary_tag else ''

                    published_tag = item.find('pubDate') or item.find('published')
                    published_str = published_tag.get_text(strip=True) if published_tag else ''

                    published_time = None
                    if published_str:
                        published_time = parse_rss_date(published_str)
                    if not published_time:
                        published_time = extract_date_from_url(link)
                    if not published_time:
                        published_time = extract_date_from_title(title)
                    if not published_time:
                        continue

                    news_list.append({
                        '标题': title,
                        '链接': link,
                        '摘要': summary[:500],
                        '来源': channel_info['name'],
                        '发布时间': published_time,
                        '渠道ID': channel_id
                    })
                except:
                    continue

            logger.info(f"RSS采集成功: {channel_info['name']}，共 {len(news_list)} 条")
            return news_list
        except Exception as e:
            logger.error(f"RSS采集失败 {channel_info['name']}: {str(e)}")
            return []