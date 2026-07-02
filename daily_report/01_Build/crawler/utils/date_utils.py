# -*- coding: utf-8 -*-
"""
日期工具模块
合并 base.py 和 rss.py 中重复的日期提取逻辑
"""

import re
from datetime import datetime


def parse_rss_date(date_str):
    """解析 RSS 日期字符串，返回 naive datetime"""
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
            if dt.tzinfo is not None:
                dt = dt.replace(tzinfo=None)
            return dt
        except:
            continue
    return None


def extract_date_from_url(url):
    """从 URL 中提取日期"""
    patterns = [
        r'/(\d{4})/(\d{2})/(\d{2})/',
        r'/(\d{4})/(\d{2})/(\d{2})\.',
        r'/(\d{4})-(\d{2})/(\d{2})/',
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
    """从标题中提取日期"""
    if not title:
        return None
    patterns = [
        r'(\d{2})/(\d{2})/(\d{4})',
        r'(\d{4})\.(\d{2})\.(\d{2})',
        r'(\d{4})-(\d{2})-(\d{2})',
        r'(\d{4})年(\d{1,2})月(\d{1,2})日',
        r'(\d{1,2})月(\d{1,2})日',
    ]
    for p in patterns:
        m = re.search(p, str(title))
        if m:
            try:
                groups = m.groups()
                if len(groups) == 3 and len(groups[0]) == 4:
                    return datetime(int(groups[0]), int(groups[1]), int(groups[2]))
                elif len(groups) == 3:
                    return datetime(int(groups[2]), int(groups[0]), int(groups[1]))
                elif len(groups) == 2:
                    month, day = int(groups[0]), int(groups[1])
                    if 1 <= month <= 12 and 1 <= day <= 31:
                        return datetime(datetime.now().year, month, day)
            except:
                pass
    return None


def extract_date_from_text(text):
    """从文本中提取日期"""
    if not text:
        return None
    
    m = re.search(r'(\d{4})-(\d{2})-(\d{2})', str(text))
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except:
            pass
    
    m = re.search(r'(\d{2})-(\d{2})', str(text))
    if m:
        try:
            month, day = int(m.group(1)), int(m.group(2))
            if 1 <= month <= 12 and 1 <= day <= 31:
                return datetime(datetime.now().year, month, day)
        except:
            pass
    
    return None