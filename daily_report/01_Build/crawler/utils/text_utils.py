# -*- coding: utf-8 -*-
"""
文本工具模块
合并 base.py 和 rss.py 中重复的 HTML 清洗逻辑
"""

from bs4 import BeautifulSoup


def clean_html(html_text):
    """清理 HTML 标签，提取纯文本"""
    if not html_text:
        return ""
    soup = BeautifulSoup(str(html_text), 'html.parser')
    return soup.get_text(separator=' ', strip=True)