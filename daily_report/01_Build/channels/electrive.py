import logging
import requests
from datetime import datetime
from email.utils import parsedate_to_datetime
from crawler_base import BaseCrawler

logger = logging.getLogger(__name__)

class ElectriveCrawler(BaseCrawler):
    """Electrive RSS 爬虫"""

    def crawl(self, channel_info):
        rss_url = channel_info.get('rss_url', channel_info['url'])
        channel_name = channel_info['name']
        articles = []

        try:
            resp = requests.get(rss_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }, timeout=30)
            resp.raise_for_status()

            soup = self.make_xml_soup(resp.text)
            items = soup.find_all('item')

            for item in items:
                title_tag = item.find('title')
                title = title_tag.get_text(strip=True) if title_tag else ''

                link_tag = item.find('link')
                link = link_tag.get_text(strip=True) if link_tag else ''

                if not title or not link:
                    continue

                if self.is_duplicate_url(link):
                    continue

                pub_date_str = item.find('pubDate').get_text(strip=True) if item.find('pubDate') else ''
                try:
                    pub_date = parsedate_to_datetime(pub_date_str).replace(tzinfo=None)
                except:
                    pub_date = self.extract_date_from_url(link)

                if not pub_date:
                    continue

                summary_tag = item.find('description') or item.find('summary')
                summary = self.clean_html(summary_tag.get_text(strip=True)) if summary_tag else ''

                articles.append({
                    '标题': title,
                    '链接': link,
                    '摘要': summary[:500],
                    '来源': channel_name,
                    '发布时间': pub_date,
                    '渠道ID': channel_info.get('name', ''),
                })
        except Exception as e:
            logger.error(f"Electrive 采集失败: {e}")

        return articles