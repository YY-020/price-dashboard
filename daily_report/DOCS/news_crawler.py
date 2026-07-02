# -*- coding: utf-8 -*-
"""
新闻采集模块
支持RSS订阅和HTML页面解析
"""

import os
import re
import time
import logging
import pandas as pd
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from constants import NEWS_CHANNELS, RAW_NEWS_FILE, CRAWLER_LOG_FILE

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# URL过滤关键词
URL_BLOCK_KEYWORDS = [
    'login', 'career', 'careers', 'privacy', 'contact', 'about', 'terms',
    'cookie', 'subscribe', 'register', 'signup', 'data-protection', 'imprint',
    'legal', 'podcast', 'press-portal', 'press portal', 'footer', 'header',
    'navigation', 'imprint', 'disclaimer', 'accessibility'
]

# 标题过滤关键词
TITLE_BLOCK_KEYWORDS = [
    'login', 'careers', 'business', 'press portal', 'data protection declaration',
    'professionals', 'professionals valencia', 'professionals canada',
    'professionals salzgitter', 'imprint', 'legal notice', 'podcast',
    'cookie policy', 'privacy policy', 'terms of use', 'accessibility'
]

def clean_html(html_text):
    """清理HTML标签，提取纯文本"""
    if not html_text:
        return ""
    soup = BeautifulSoup(str(html_text), 'html.parser')
    return soup.get_text(separator=' ', strip=True)

def extract_date_from_url(url):
    """从URL中提取日期，如 /2026/06/05/"""
    patterns = [
        r'/(\d{4})/(\d{2})/(\d{2})/',
        r'/(\d{4})/(\d{2})/(\d{2})\.',
        r'[_-](\d{4})[_-](\d{2})[_-](\d{2})',
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            try:
                return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            except:
                pass
    return None

def extract_date_from_title(title):
    """从标题中提取日期，如 '06/16/2023' 或 '2025.09.01' 或 '3月21日'"""
    if not title:
        return None
    patterns = [
        r'(\d{2})/(\d{2})/(\d{4})',
        r'(\d{4})\.(\d{2})\.(\d{2})',
        r'(\d{4})-(\d{2})-(\d{2})',
        # 中文日期：2025年3月21日 或 3月21日
        r'(\d{4})年(\d{1,2})月(\d{1,2})日',
        r'(\d{1,2})月(\d{1,2})日',
    ]
    for p in patterns:
        m = re.search(p, str(title))
        if m:
            try:
                groups = m.groups()
                if len(groups) == 3 and len(groups[0]) == 4:
                    # YYYY年MM月DD日
                    return datetime(int(groups[0]), int(groups[1]), int(groups[2]))
                elif len(groups) == 3:
                    # MM/DD/YYYY
                    return datetime(int(groups[2]), int(groups[0]), int(groups[1]))
                elif len(groups) == 2:
                    # MM月DD日（无年份，默认当前年份）
                    month, day = int(groups[0]), int(groups[1])
                    if 1 <= month <= 12 and 1 <= day <= 31:
                        return datetime(datetime.now().year, month, day)
            except:
                pass
    return None

def should_block_url(url):
    """检查URL是否应该被过滤"""
    if not url or len(url) < 30:
        return True
    url_lower = url.lower()
    # 双斜杠拼接错误
    if '//' in url.replace('https://', '').replace('http://', ''):
        if 'news//news' in url or '/news//' in url:
            return True
        if 'press.asp/press' in url:
            return True
        if '?list_19//?list' in url:
            return True
    for kw in URL_BLOCK_KEYWORDS:
        if kw in url_lower:
            return True
    return False

def should_block_title(title):
    """检查标题是否应该被过滤"""
    if not title or len(title) < 10:
        return True
    title_lower = title.strip().lower()
    for kw in TITLE_BLOCK_KEYWORDS:
        if title_lower == kw or title_lower.startswith(kw):
            return True
    # 过滤纯日期+Business格式
    if re.match(r'^[a-z]{3}\.\s*\d{1,2},\s*\d{4}\s*business$', title_lower):
        return True
    # 过滤纯数字日期
    if re.match(r'^\d{2}/\d{2}/\d{4}$', title.strip()):
        return True
    return False

class NewsCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        })
        self.crawl_results = []
        self.failed_channels = []

    def parse_rss_date(self, date_str):
        """解析RSS日期字符串，返回naive datetime"""
        date_formats = [
            '%a, %d %b %Y %H:%M:%S %z',
            '%a, %d %b %Y %H:%M:%S %Z',
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%d %b %Y %H:%M:%S',
        ]
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                # 去掉时区信息，转为naive datetime
                if dt.tzinfo is not None:
                    dt = dt.replace(tzinfo=None)
                return dt
            except:
                continue
        return None

    def crawl_rss(self, channel_id, channel_info):
        """采集RSS订阅源"""
        try:
            rss_url = channel_info.get('rss_url', channel_info['url'])
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

                    # URL过滤
                    if should_block_url(link):
                        continue
                    if should_block_title(title):
                        continue

                    summary_tag = item.find('description') or item.find('summary')
                    summary = clean_html(summary_tag.get_text(strip=True)) if summary_tag else ''

                    published_tag = item.find('pubDate') or item.find('published')
                    published_str = published_tag.get_text(strip=True) if published_tag else ''

                    # 优先从RSS pubDate提取时间
                    published_time = None
                    if published_str:
                        published_time = self.parse_rss_date(published_str)
                    if not published_time:
                        published_time = extract_date_from_url(link)
                    if not published_time:
                        published_time = extract_date_from_title(title)
                    if not published_time:
                        continue  # 无法确定时间的不收录

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
            self.failed_channels.append({
                'channel': channel_info['name'],
                'url': channel_info.get('rss_url', channel_info['url']),
                'error': str(e),
                'suggestion': '检查RSS地址是否有效'
            })
            return []

    def crawl_html(self, channel_id, channel_info):
        """采集HTML页面"""
        try:
            url = channel_info['url']
            logger.info(f"正在采集 HTML: {channel_info['name']}")
            response = self.session.get(url, timeout=30)
            response.encoding = response.apparent_encoding
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}")

            soup = BeautifulSoup(response.text, 'html.parser')
            news_list = []

            # 尝试多种新闻列表结构
            selectors = [
                'article', 'div.news-item', 'div[class*="news"]',
                'ul.news-list li', 'div[class*="article"]', '.news-list li',
                '.article-list li', 'table tr'
            ]
            articles = []
            for selector in selectors:
                articles = soup.select(selector)
                if articles:
                    break

            if not articles:
                all_links = soup.find_all('a', href=True)
                for a in all_links:
                    href = a['href']
                    text = a.get_text(strip=True)
                    if text and len(text) > 10:
                        if not href.startswith('http'):
                            base = '/'.join(url.split('/')[:3])
                            href = base + href if href.startswith('/') else url.rstrip('/') + '/' + href
                        articles.append({'title': text, 'link': href})

            seen_titles = set()
            for article in articles:
                try:
                    if isinstance(article, dict):
                        title = article['title']
                        link = article['link']
                    else:
                        title_tag = article.find(['h2', 'h3', 'h4', 'a'])
                        title = title_tag.get_text(strip=True) if title_tag else article.get_text(strip=True)
                        link_tag = article.find('a', href=True)
                        link = link_tag['href'] if link_tag else url

                    if not title or len(title) < 10:
                        continue
                    if title in seen_titles:
                        continue
                    if should_block_title(title):
                        continue

                    # 补全相对链接
                    if not link.startswith('http'):
                        base = '/'.join(url.split('/')[:3])
                        link = base + link if link.startswith('/') else url.rstrip('/') + '/' + link

                    if should_block_url(link):
                        continue

                    seen_titles.add(title)

                    # 提取时间：URL > 标题 > time标签 > 今天
                    published_time = extract_date_from_url(link)
                    if not published_time:
                        published_time = extract_date_from_title(title)
                    if not published_time and not isinstance(article, dict):
                        time_tag = article.find('time')
                        if time_tag and time_tag.get('datetime'):
                            try:
                                published_time = datetime.fromisoformat(time_tag['datetime'].replace('Z', '+00:00'))
                            except:
                                pass
                    # 无法提取时间的使用今天，后续由时间筛选过滤
                    if not published_time:
                        published_time = datetime.now()

                    news_list.append({
                        '标题': title,
                        '链接': link,
                        '摘要': '',
                        '来源': channel_info['name'],
                        '发布时间': published_time,
                        '渠道ID': channel_id
                    })
                except:
                    continue

            logger.info(f"HTML采集成功: {channel_info['name']}，共 {len(news_list)} 条")
            return news_list
        except Exception as e:
            logger.error(f"HTML采集失败 {channel_info['name']}: {str(e)}")
            self.failed_channels.append({
                'channel': channel_info['name'],
                'url': channel_info['url'],
                'error': str(e),
                'suggestion': '检查网络连接或网站是否可访问'
            })
            return []

    def crawl_pc(self, channel_id, channel_info):
        """PC站点采集（公众号对应的官方网站）"""
        name = channel_info['name']
        base_url = channel_info.get('base_url', '')
        if not base_url:
            logger.warning(f"PC站点 {name} 无 base_url 配置")
            self.failed_channels.append({
                'channel': name, 'url': 'PC站点',
                'error': '无 base_url 配置',
                'suggestion': '在 constants.py 中为该渠道添加 base_url'
            })
            return []
        logger.info(f"PC站点 {name} → 网站抓取: {base_url}")

        # 根据 channel_id 分发到不同的抓取方法
        if channel_id == 'weike_lidian':
            return self.crawl_ofweek(channel_id, channel_info)
        elif channel_id == 'wode_dianchi':
            return self.crawl_wode_dianchi(channel_id, channel_info)
        elif channel_id == 'dongli_dianchi':
            return self.crawl_dongli_dianchi(channel_id, channel_info)
        elif channel_id == 'xinluo_lidian':
            return self.crawl_xinluo_lidian(channel_id, channel_info)
        elif channel_id == 'smm_lidian':
            return self.crawl_smm_lidian(channel_id, channel_info)
        elif channel_id == 'gaogong_lidian':
            return self.crawl_gaogong(channel_id, channel_info)
        else:
            return self.crawl_generic_pc(channel_id, channel_info)

    def crawl_ofweek(self, channel_id, channel_info):
        """从 ofweek.com 网站抓取新闻（维科网锂电等公众号的网站版）"""
        name = channel_info['name']
        base_url = channel_info.get('base_url', 'https://libattery.ofweek.com')
        list_urls = channel_info.get('list_urls', [
            f"{base_url}/CATList-36000-8100-libattery.html",  # 快讯
            f"{base_url}/CATList-36000-8200-libattery.html",  # 深度
        ])

        all_articles = []
        seen_urls = set()

        for list_url in list_urls:
            logger.info(f"  抓取列表: {list_url}")
            # page=1 内容不稳定，从 page=2 开始（已验证显示最新文章）
            for page in range(2, 30):  # 最多翻 30 页
                # 分页格式: CATList-...-libattery.html → CATList-...-libattery-2.html
                url = list_url.replace('.html', f'-{page}.html')

                try:
                    resp = self.session.get(url, timeout=30)
                    if resp.status_code != 200:
                        if page > 1:
                            break  # 无更多页面
                        continue
                    resp.encoding = 'gbk'  # ofweek 网站使用 gbk 编码
                except Exception as e:
                    logger.warning(f"  请求失败 page={page}: {e}")
                    break

                soup = BeautifulSoup(resp.text, 'html.parser')
                articles_found = 0
                oldest_date = None
                newest_date = None

                # 查找文章条目：标题链接 + 日期
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    title = link.get_text(strip=True)
                    if not title or len(title) < 4:
                        continue
                    # 匹配文章链接: /YYYY-MM/ART-XXXXX-XXXXX-XXXXXXXX.html（ofweek 用横杠分隔年月）
                    art_match = re.search(r'/(\d{4})-(\d{2})/ART-\d+-\d+-\d+\.html', href)
                    if not art_match:
                        continue
                    if href in seen_urls:
                        continue
                    # 去重：去掉 #content 片段
                    clean_href = href.split('#')[0]
                    if clean_href in seen_urls:
                        seen_urls.add(href)
                        continue
                    seen_urls.add(clean_href)
                    seen_urls.add(href)

                    full_url = clean_href if clean_href.startswith('http') else f"https://libattery.ofweek.com{clean_href}"

                    # 提取日期（从上下文文本查找 YYYY-MM-DD）
                    pub_date = None
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

                    # 提取摘要（从相邻的 p 标签）
                    summary = ''
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
                        '来源': name,
                        '发布时间': pub_date,
                        '渠道ID': channel_id
                    })
                    articles_found += 1

                    if oldest_date is None or pub_date < oldest_date:
                        oldest_date = pub_date
                    if newest_date is None or pub_date > newest_date:
                        newest_date = pub_date

                logger.info(f"  page={page}: {articles_found} 条, 日期范围={oldest_date} ~ {newest_date}")
                if articles_found == 0:
                    break
                # 如果本页最新文章日期早于目标起始日期，说明已超出范围，停止翻页
                if newest_date and self.start_date and newest_date < self.start_date:
                    logger.info(f"  最新文章日期 {newest_date.strftime('%Y-%m-%d')} 早于目标起始日期 {self.start_date.strftime('%Y-%m-%d')}，停止翻页")
                    break

                time.sleep(1.5)  # 礼貌间隔

        # 去重（按链接）
        unique = {}
        for a in all_articles:
            if a['链接'] not in unique:
                unique[a['链接']] = a
        all_articles = list(unique.values())

        logger.info(f"维科网采集完成: {len(all_articles)} 条（去重后）")
        return all_articles

    def crawl_channel(self, channel_id, channel_info):
        channel_type = channel_info.get('type', 'html')
        if channel_type == 'rss':
            return self.crawl_rss(channel_id, channel_info)
        elif channel_type == 'pc':
            return self.crawl_pc(channel_id, channel_info)
        elif channel_type == 'wechat':
            return self.crawl_pc(channel_id, channel_info)  # 兼容旧 wechat 类型
        else:
            return self.crawl_html(channel_id, channel_info)

    def crawl_all(self, start_date=None, end_date=None, demo=None):
        """采集所有渠道
        demo: None=全量, 'electrive'=Electrive三版块, 'wechat'=PC站点
        """
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        channels = NEWS_CHANNELS
        if demo == 'electrive':
            demo_ids = ["electrive_battery", "electrive_auto", "electrive_politics"]
            channels = {k: v for k, v in NEWS_CHANNELS.items() if k in demo_ids}
            logger.info(f"Demo模式（Electrive）：仅采集 {len(channels)} 个渠道")
        elif demo == 'wechat':
            demo_ids = ["gaogong_lidian", "wode_dianchi", "dongli_dianchi", "xinluo_lidian", "smm_lidian", "weike_lidian"]
            channels = {k: v for k, v in NEWS_CHANNELS.items() if k in demo_ids}
            logger.info(f"Demo模式（PC站点）：仅采集 {len(channels)} 个渠道")
        elif demo == 'demo3':
            demo_ids = ["electrive_battery", "electrive_auto", "electrive_politics", "weike_lidian"]
            channels = {k: v for k, v in NEWS_CHANNELS.items() if k in demo_ids}
            logger.info(f"Demo3模式（Electrive+维科网）：仅采集 {len(channels)} 个渠道")
        else:
            logger.info("开始采集所有新闻渠道...")
        all_news = []
        for channel_id, channel_info in channels.items():
            news = self.crawl_channel(channel_id, channel_info)
            all_news.extend(news)
            time.sleep(1)

        # 严格时间过滤
        if start_date and end_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            before = len(all_news)
            def in_range(n):
                title = str(n.get('标题', ''))
                t = n['发布时间']
                # 标题中带有2022/2023/2024/2025年份的，直接排除
                for old_year in ['2022', '2023', '2024', '2025']:
                    if f'/{old_year}/' in str(n.get('链接', '')):
                        return False
                    if old_year in title and '2026' not in title:
                        return False
                if t is None:
                    return True  # 无法确定日期，保留
                if start_dt <= t < end_dt:
                    return True
                return False
            all_news = [n for n in all_news if in_range(n)]
            logger.info(f"时间过滤: {before} -> {len(all_news)} (范围 {start_date}~{end_date})")

        self.crawl_results = all_news
        return all_news

    def save_results(self):
        if not self.crawl_results:
            logger.warning("没有采集到任何新闻")
            return
        df = pd.DataFrame(self.crawl_results)
        df['发布时间'] = df['发布时间'].apply(
            lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, datetime) else x
        )
        # URL 去重（同一文章可能出现在多个 RSS 渠道）
        before = len(df)
        df = df.drop_duplicates(subset=['链接'], keep='first')
        if before > len(df):
            logger.info(f"URL 去重: {before} -> {len(df)} 条")
        df.to_excel(RAW_NEWS_FILE, index=False)
        logger.info(f"采集结果已保存到: {RAW_NEWS_FILE}")

        with open(CRAWLER_LOG_FILE, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n新闻采集报告\n" + "=" * 60 + "\n")
            f.write(f"采集时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总采集新闻数: {len(self.crawl_results)}\n\n【成功渠道统计】\n")
            channel_counts = df['来源'].value_counts()
            for source, count in channel_counts.items():
                f.write(f"- {source}: {count} 条\n")
            f.write("\n【失败渠道列表】\n")
            if self.failed_channels:
                for fail in self.failed_channels:
                    f.write(f"\n渠道: {fail['channel']}\nURL: {fail['url']}\n")
                    f.write(f"错误: {fail['error']}\n建议: {fail['suggestion']}\n")
            else:
                f.write("无\n")
        logger.info(f"采集报告已保存到: {CRAWLER_LOG_FILE}")

    def get_report(self):
        return {
            'total_news': len(self.crawl_results),
            'success_channels': self._get_success_channels(),
            'failed_channels': self.failed_channels
        }

    def _get_success_channels(self):
        if not self.crawl_results:
            return {}
        df = pd.DataFrame(self.crawl_results)
        return df['来源'].value_counts().to_dict()

    # ========== 各PC站点专用爬虫 ==========

    def crawl_wode_dianchi(self, channel_id, channel_info):
        """我的电池网 itdcw.com"""
        name = channel_info['name']
        list_urls = channel_info['list_urls']
        all_articles = []
        seen_urls = set()

        for list_url in list_urls:
            is_home = list_url.rstrip('/') == 'https://www.itdcw.com'
            logger.info(f"  抓取列表: {list_url}")

            if is_home:
                # 首页没有分页，一次性抓取
                try:
                    resp = self.session.get(list_url, timeout=30)
                    resp.encoding = resp.apparent_encoding
                    if resp.status_code != 200:
                        continue
                except Exception as e:
                    logger.warning(f"  请求失败: {e}")
                    continue

                soup = BeautifulSoup(resp.text, 'html.parser')
                articles_found = 0

                for link in soup.find_all('a', href=True):
                    href = link['href']
                    title = link.get_text(strip=True)
                    if not title or len(title) < 4:
                        continue
                    # 匹配文章链接: /news/xxx/MMDDXXXX2026.html
                    if not re.search(r'/news/.*?/(\d{8,10})2026\.html', href):
                        continue
                    if href in seen_urls:
                        continue
                    seen_urls.add(href)

                    full_url = href if href.startswith('http') else f"https://www.itdcw.com{href}"

                    # 提取日期：从URL中提取 MMDD
                    pub_date = None
                    date_match = re.search(r'/(\d{2})(\d{2})\d{4,6}2026\.html', href)
                    if date_match:
                        try:
                            month, day = int(date_match.group(1)), int(date_match.group(2))
                            if 1 <= month <= 12 and 1 <= day <= 31:
                                pub_date = datetime(2026, month, day)
                        except:
                            pass

                    # 备用：从上下文文本查找日期
                    if not pub_date:
                        block = link.parent
                        for _ in range(5):
                            if block is None:
                                break
                            text = block.get_text() if hasattr(block, 'get_text') else ''
                            date_match2 = re.search(r'(\d{4}-\d{2}-\d{2})', text)
                            if date_match2:
                                try:
                                    pub_date = datetime.strptime(date_match2.group(1), '%Y-%m-%d')
                                    break
                                except:
                                    pass
                            block = block.parent if hasattr(block, 'parent') else None

                    if not pub_date:
                        continue

                    summary = ''
                    parent = link.parent
                    if parent:
                        for _ in range(3):
                            parent = parent.parent
                            if parent is None:
                                break
                        if parent:
                            p_tag = parent.find('p')
                            if p_tag:
                                summary = p_tag.get_text(strip=True)[:500]

                    all_articles.append({
                        '标题': title,
                        '链接': full_url,
                        '摘要': summary,
                        '来源': name,
                        '发布时间': pub_date,
                        '渠道ID': channel_id
                    })
                    articles_found += 1

                logger.info(f"  首页: {articles_found} 条")
                continue

            # 非首页：分页抓取
            for page in range(1, 30):
                if page == 1:
                    url = list_url
                else:
                    url = list_url.rstrip('/') + f'/list_177_{page}.html'

                try:
                    resp = self.session.get(url, timeout=30)
                    if resp.status_code != 200:
                        if page > 1:
                            break
                        continue
                    resp.encoding = resp.apparent_encoding
                except Exception as e:
                    logger.warning(f"  请求失败 page={page}: {e}")
                    break

                soup = BeautifulSoup(resp.text, 'html.parser')
                articles_found = 0
                oldest_date = None
                newest_date = None

                for h2 in soup.find_all(['h2', 'h3', 'h4']):
                    link = h2.find('a', href=True)
                    if not link:
                        continue
                    href = link['href']
                    title = link.get_text(strip=True)
                    if not title or len(title) < 4:
                        continue

                    if not re.search(r'/news/.*?/(\d{8,10})2026\.html', href):
                        continue
                    if href in seen_urls:
                        continue
                    seen_urls.add(href)

                    full_url = href if href.startswith('http') else f"https://www.itdcw.com{href}"

                    pub_date = None
                    date_match = re.search(r'/(\d{2})(\d{2})\d{4,6}2026\.html', href)
                    if date_match:
                        try:
                            month, day = int(date_match.group(1)), int(date_match.group(2))
                            if 1 <= month <= 12 and 1 <= day <= 31:
                                pub_date = datetime(2026, month, day)
                        except:
                            pass

                    if not pub_date:
                        block = h2.parent
                        for _ in range(5):
                            if block is None:
                                break
                            text = block.get_text() if hasattr(block, 'get_text') else ''
                            date_match2 = re.search(r'(\d{4}-\d{2}-\d{2})', text)
                            if date_match2:
                                try:
                                    pub_date = datetime.strptime(date_match2.group(1), '%Y-%m-%d')
                                    break
                                except:
                                    pass
                            block = block.parent if hasattr(block, 'parent') else None

                    if not pub_date:
                        continue

                    summary = ''
                    parent = h2.parent
                    if parent:
                        p_tag = parent.find('p')
                        if p_tag:
                            summary = p_tag.get_text(strip=True)[:500]

                    all_articles.append({
                        '标题': title,
                        '链接': full_url,
                        '摘要': summary,
                        '来源': name,
                        '发布时间': pub_date,
                        '渠道ID': channel_id
                    })
                    articles_found += 1

                    if oldest_date is None or pub_date < oldest_date:
                        oldest_date = pub_date
                    if newest_date is None or pub_date > newest_date:
                        newest_date = pub_date

                logger.info(f"  page={page}: {articles_found} 条, 日期范围={oldest_date} ~ {newest_date}")
                if articles_found == 0:
                    break
                if newest_date and self.start_date and newest_date < self.start_date:
                    break
                time.sleep(1.5)

        unique = {}
        for a in all_articles:
            if a['链接'] not in unique:
                unique[a['链接']] = a
        all_articles = list(unique.values())
        logger.info(f"我的电池网采集完成: {len(all_articles)} 条（去重后）")
        return all_articles

    def crawl_dongli_dianchi(self, channel_id, channel_info):
        """动力电池网 dldcw.cn"""
        name = channel_info['name']
        list_urls = channel_info['list_urls']
        all_articles = []
        seen_urls = set()

        for list_url in list_urls:
            logger.info(f"  抓取列表: {list_url}")
            for page in range(1, 30):
                if page == 1:
                    url = list_url
                else:
                    url = f"http://www.dldcw.cn/M/News/index_{page}.html"

                try:
                    resp = self.session.get(url, timeout=30)
                    if resp.status_code != 200:
                        if page > 1:
                            break
                        continue
                    resp.encoding = resp.apparent_encoding
                except Exception as e:
                    logger.warning(f"  请求失败 page={page}: {e}")
                    break

                soup = BeautifulSoup(resp.text, 'html.parser')
                articles_found = 0
                oldest_date = None
                newest_date = None

                for link in soup.find_all('a', href=True):
                    href = link['href']
                    title = link.get_text(strip=True)
                    if not title or len(title) < 4:
                        continue
                    # 匹配: /M/News/数字.html
                    if not re.search(r'/M/News/\d+\.html', href):
                        continue
                    if href in seen_urls:
                        continue
                    seen_urls.add(href)

                    full_url = href if href.startswith('http') else f"http://www.dldcw.cn{href}"

                    # 日期：从URL无法直接提取，需要从上下文获取
                    pub_date = None
                    block = link.parent
                    for _ in range(5):
                        if block is None:
                            break
                        text = block.get_text() if hasattr(block, 'get_text') else ''
                        # 尝试匹配中文日期: 2026年6月15日
                        date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', text)
                        if date_match:
                            try:
                                pub_date = datetime(int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3)))
                                break
                            except:
                                pass
                        block = block.parent if hasattr(block, 'parent') else None

                    if not pub_date:
                        continue

                    summary = ''
                    parent = link.parent
                    if parent:
                        p_tag = parent.find('p')
                        if p_tag:
                            summary = p_tag.get_text(strip=True)[:500]

                    all_articles.append({
                        '标题': title,
                        '链接': full_url,
                        '摘要': summary,
                        '来源': name,
                        '发布时间': pub_date,
                        '渠道ID': channel_id
                    })
                    articles_found += 1

                    if oldest_date is None or pub_date < oldest_date:
                        oldest_date = pub_date
                    if newest_date is None or pub_date > newest_date:
                        newest_date = pub_date

                logger.info(f"  page={page}: {articles_found} 条, 日期范围={oldest_date} ~ {newest_date}")
                if articles_found == 0:
                    break
                if newest_date and self.start_date and newest_date < self.start_date:
                    break
                time.sleep(1.5)

        unique = {}
        for a in all_articles:
            if a['链接'] not in unique:
                unique[a['链接']] = a
        all_articles = list(unique.values())
        logger.info(f"动力电池网采集完成: {len(all_articles)} 条（去重后）")
        return all_articles

    def crawl_xinluo_lidian(self, channel_id, channel_info):
        """鑫椤锂电 icbattery.com - 使用原始正则解析"""
        name = channel_info['name']
        list_urls = channel_info['list_urls']
        all_articles = []
        seen_urls = set()

        for list_url in list_urls:
            logger.info(f"  抓取列表: {list_url}")
            for page in range(1, 20):
                if page == 1:
                    url = list_url
                else:
                    url = f"{list_url}{'&' if '?' in list_url else '?'}page={page}"

                try:
                    resp = self.session.get(url, timeout=30)
                    if resp.status_code != 200:
                        if page > 1:
                            break
                        continue
                    resp.encoding = resp.apparent_encoding
                except Exception as e:
                    logger.warning(f"  请求失败 page={page}: {e}")
                    break

                html = resp.text
                articles_found = 0
                oldest_date = None
                newest_date = None

                # 用正则匹配：<span>&nbsp;MM-DD</span><a href="...news/show-htm-itemid-XXX.html">title</a>
                # 日期格式: MM-DD（如 06-15）
                pattern = re.compile(
                    r'<span[^>]*>\s*&nbsp;(\d{2})-(\d{2})\s*</span>\s*'
                    r'<a[^>]*href="([^"]*?/news/show-htm-itemid-\d+\.html)"[^>]*>'
                    r'([^<]+)'
                    r'</a>',
                    re.DOTALL
                )
                for m in pattern.findall(html):
                    month_str, day_str, href, title = m
                    title = re.sub(r'<[^>]+>', '', title).strip()
                    if not title or len(title) < 4:
                        continue
                    if href in seen_urls:
                        continue
                    seen_urls.add(href)

                    full_url = href if href.startswith('http') else f"http://www.icbattery.com{href}"

                    try:
                        month, day = int(month_str), int(day_str)
                        if 1 <= month <= 12 and 1 <= day <= 31:
                            pub_date = datetime(2026, month, day)
                        else:
                            continue
                    except:
                        continue

                    all_articles.append({
                        '标题': title,
                        '链接': full_url,
                        '摘要': '',
                        '来源': name,
                        '发布时间': pub_date,
                        '渠道ID': channel_id
                    })
                    articles_found += 1

                    if oldest_date is None or pub_date < oldest_date:
                        oldest_date = pub_date
                    if newest_date is None or pub_date > newest_date:
                        newest_date = pub_date

                logger.info(f"  page={page}: {articles_found} 条, 日期范围={oldest_date} ~ {newest_date}")
                if articles_found == 0:
                    break
                if newest_date and self.start_date and newest_date < self.start_date:
                    break
                time.sleep(1.5)

        unique = {}
        for a in all_articles:
            if a['链接'] not in unique:
                unique[a['链接']] = a
        all_articles = list(unique.values())
        logger.info(f"鑫椤锂电采集完成: {len(all_articles)} 条（去重后）")
        return all_articles

    def crawl_smm_lidian(self, channel_id, channel_info):
        """SMM锂电 news.smm.cn - 解析 __NEXT_DATA__"""
        name = channel_info['name']
        list_urls = channel_info['list_urls']
        all_articles = []
        seen_ids = set()

        for list_url in list_urls:
            logger.info(f"  抓取列表: {list_url}")
            for page in range(1, 10):
                if page == 1:
                    url = list_url
                else:
                    url = f"{list_url}/pages/{page}"
                    if list_url.endswith('/pages/1'):
                        url = list_url.replace('/pages/1', f'/pages/{page}')

                try:
                    resp = self.session.get(url, timeout=30)
                    if resp.status_code != 200:
                        if page > 1:
                            break
                        continue
                    resp.encoding = resp.apparent_encoding
                except Exception as e:
                    logger.warning(f"  请求失败 page={page}: {e}")
                    break

                # 解析 __NEXT_DATA__
                import json
                nd_match = re.search(r'<script[^>]*>\s*(\{"props":\{.*?\})\s*</script>', resp.text, re.DOTALL)
                if not nd_match:
                    logger.warning(f"  未找到 __NEXT_DATA__")
                    break

                try:
                    data = json.loads(nd_match.group(1))
                except:
                    logger.warning(f"  JSON解析失败")
                    break

                page_props = data.get('props', {}).get('pageProps', {})
                news_list = page_props.get('newsList', {})
                list_data = news_list.get('data', {})
                articles = list_data.get('listList', [])

                if not articles:
                    logger.info(f"  page={page}: 无文章，停止翻页")
                    break

                articles_found = 0
                oldest_date = None
                newest_date = None

                for a in articles:
                    news_id = str(a.get('newsId', ''))
                    if news_id in seen_ids:
                        continue
                    seen_ids.add(news_id)

                    title = a.get('title', '')
                    date_str = a.get('date', '')
                    profile = a.get('profile', '')

                    if not title or not date_str:
                        continue

                    try:
                        pub_date = datetime.strptime(date_str, '%Y-%m-%d')
                    except:
                        continue

                    article_url = f"https://news.smm.cn/news/{news_id}"

                    all_articles.append({
                        '标题': title,
                        '链接': article_url,
                        '摘要': profile[:200] if profile else '',
                        '来源': name,
                        '发布时间': pub_date,
                        '渠道ID': channel_id
                    })
                    articles_found += 1

                    if oldest_date is None or pub_date < oldest_date:
                        oldest_date = pub_date
                    if newest_date is None or pub_date > newest_date:
                        newest_date = pub_date

                logger.info(f"  page={page}: {articles_found} 条, 日期范围={oldest_date} ~ {newest_date}")

                # 如果最早日期早于 start_date，停止翻页
                if self.start_date and oldest_date and oldest_date < self.start_date:
                    break

                time.sleep(1.5)

        logger.info(f"SMM锂电采集完成: {len(all_articles)} 条")
        return all_articles

    def crawl_gaogong(self, channel_id, channel_info):
        """高工锂电 gg-lb.com"""
        name = channel_info['name']
        list_urls = channel_info['list_urls']
        all_articles = []
        seen_urls = set()

        for list_url in list_urls:
            logger.info(f"  抓取列表: {list_url}")
            for page in range(1, 20):
                if page == 1:
                    url = list_url
                else:
                    url = list_url.replace('.html', f'-{page}.html')

                try:
                    resp = self.session.get(url, timeout=30)
                    if resp.status_code != 200:
                        if page > 1:
                            break
                        continue
                    resp.encoding = resp.apparent_encoding
                except Exception as e:
                    logger.warning(f"  请求失败 page={page}: {e}")
                    break

                soup = BeautifulSoup(resp.text, 'html.parser')
                articles_found = 0
                oldest_date = None
                newest_date = None

                for link in soup.find_all('a', href=True):
                    href = link['href']
                    title = link.get_text(strip=True)
                    if not title or len(title) < 4:
                        continue
                    # 匹配新闻链接格式
                    if not re.search(r'/news/(show|detail|article|html)', href, re.I):
                        continue
                    if href in seen_urls:
                        continue
                    seen_urls.add(href)

                    full_url = href if href.startswith('http') else f"http://www.gg-lb.com{href}"

                    # 日期：从上下文文本查找
                    pub_date = None
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
                        date_match2 = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', text)
                        if date_match2:
                            try:
                                pub_date = datetime(int(date_match2.group(1)), int(date_match2.group(2)), int(date_match2.group(3)))
                                break
                            except:
                                pass
                        block = block.parent if hasattr(block, 'parent') else None

                    if not pub_date:
                        continue

                    summary = ''
                    parent = link.parent
                    if parent:
                        for _ in range(3):
                            parent = parent.parent
                            if parent is None:
                                break
                        if parent:
                            p_tag = parent.find('p')
                            if p_tag:
                                summary = p_tag.get_text(strip=True)[:500]

                    all_articles.append({
                        '标题': title,
                        '链接': full_url,
                        '摘要': summary,
                        '来源': name,
                        '发布时间': pub_date,
                        '渠道ID': channel_id
                    })
                    articles_found += 1

                    if oldest_date is None or pub_date < oldest_date:
                        oldest_date = pub_date
                    if newest_date is None or pub_date > newest_date:
                        newest_date = pub_date

                logger.info(f"  page={page}: {articles_found} 条, 日期范围={oldest_date} ~ {newest_date}")
                if articles_found == 0:
                    break
                if newest_date and self.start_date and newest_date < self.start_date:
                    break
                time.sleep(1.5)

        unique = {}
        for a in all_articles:
            if a['链接'] not in unique:
                unique[a['链接']] = a
        all_articles = list(unique.values())
        logger.info(f"高工锂电采集完成: {len(all_articles)} 条（去重后）")
        return all_articles

    def crawl_generic_pc(self, channel_id, channel_info):
        """通用PC站点爬虫（兜底方案）"""
        name = channel_info['name']
        base_url = channel_info['base_url']
        list_urls = channel_info.get('list_urls', [base_url])
        all_articles = []
        seen_urls = set()

        for list_url in list_urls:
            logger.info(f"  抓取列表: {list_url}")
            try:
                resp = self.session.get(list_url, timeout=30)
                resp.encoding = resp.apparent_encoding
                if resp.status_code != 200:
                    logger.warning(f"  请求失败: HTTP {resp.status_code}")
                    continue
            except Exception as e:
                logger.warning(f"  请求失败: {e}")
                continue

            soup = BeautifulSoup(resp.text, 'html.parser')
            articles_found = 0

            for link in soup.find_all('a', href=True):
                href = link['href']
                title = link.get_text(strip=True)
                if not title or len(title) < 4:
                    continue
                if href in seen_urls:
                    continue
                seen_urls.add(href)

                full_url = href if href.startswith('http') else f"{base_url.rstrip('/')}{href}"

                pub_date = None
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
                    date_match2 = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', text)
                    if date_match2:
                        try:
                            pub_date = datetime(int(date_match2.group(1)), int(date_match2.group(2)), int(date_match2.group(3)))
                            break
                        except:
                            pass
                    block = block.parent if hasattr(block, 'parent') else None

                if not pub_date:
                    pub_date = datetime.now()

                all_articles.append({
                    '标题': title,
                    '链接': full_url,
                    '摘要': '',
                    '来源': name,
                    '发布时间': pub_date,
                    '渠道ID': channel_id
                })
                articles_found += 1

            logger.info(f"  找到 {articles_found} 条")

        logger.info(f"通用PC采集完成: {name}, {len(all_articles)} 条")
        return all_articles