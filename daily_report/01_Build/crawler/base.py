# -*- coding: utf-8 -*-
"""
爬虫基类
所有渠道爬虫的公共逻辑：网络请求、去重
删除重复的日期提取、URL/标题过滤、HTML清洗逻辑（已移至 crawler/utils/）
"""

import logging
import requests

logger = logging.getLogger(__name__)


class BaseCrawler:
    """所有渠道爬虫的基类，提供共用的网络请求和去重能力"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
        self.seen_urls = set()
    
    def fetch(self, url, timeout=30, encoding=None):
        """统一的网络请求方法，返回响应文本"""
        try:
            resp = self.session.get(url, timeout=timeout)
            resp.raise_for_status()
            if encoding:
                resp.encoding = encoding
            elif resp.apparent_encoding:
                resp.encoding = resp.apparent_encoding
            return resp.text
        except Exception as e:
            logger.warning(f"请求失败 {url[:80]}: {e}")
            return None
    
    def is_duplicate_url(self, url):
        """检查 URL 是否已采集过"""
        clean = url.split('#')[0]
        if clean in self.seen_urls or url in self.seen_urls:
            return True
        self.seen_urls.add(clean)
        self.seen_urls.add(url)
        return False