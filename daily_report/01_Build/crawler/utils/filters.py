# -*- coding: utf-8 -*-
"""
过滤工具模块
合并 base.py 和 rss.py 中重复的 URL/标题过滤逻辑
"""

import re


def should_block_url(url):
    """检查 URL 是否应该被过滤"""
    if not url or len(url) < 30:
        return True
    
    url_lower = url.lower()
    block_keywords = [
        'login', 'career', 'careers', 'privacy', 'contact', 'about', 'terms',
        'cookie', 'subscribe', 'register', 'signup', 'data-protection',
        'imprint', 'legal', 'podcast', 'press-portal', 'press portal',
        'footer', 'header', 'navigation', 'disclaimer', 'accessibility'
    ]
    for kw in block_keywords:
        if kw in url_lower:
            return True
    
    clean_url = url.replace('https://', '').replace('http://', '')
    if '//' in clean_url:
        if 'news//news' in url or '/news//' in url:
            return True
        if 'press.asp/press' in url:
            return True
        if '?list_19//?list' in url:
            return True
    
    return False


def should_block_title(title):
    """检查标题是否应该被过滤"""
    if not title or len(title) < 10:
        return False
    
    title_lower = title.strip().lower()
    block_keywords = [
        'login', 'careers', 'business', 'press portal',
        'data protection declaration', 'professionals',
        'professionals valencia', 'professionals canada',
        'professionals salzgitter', 'imprint', 'legal notice',
        'podcast', 'cookie policy', 'privacy policy',
        'terms of use', 'accessibility'
    ]
    for kw in block_keywords:
        if title_lower == kw or title_lower.startswith(kw):
            return True
    
    if re.match(r'^[a-z]{3}\.\s*\d{1,2},\s*\d{4}\s*business$', title_lower):
        return True
    
    if re.match(r'^\d{2}/\d{2}/\d{4}$', title.strip()):
        return True
    
    return False