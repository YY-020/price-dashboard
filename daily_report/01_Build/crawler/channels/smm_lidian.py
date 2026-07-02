# -*- coding: utf-8 -*-
"""
SMM锂电渠道爬虫
负责SMM锂电的新闻采集
"""

import logging

from crawler.channels.pc_base import PCCrawler

logger = logging.getLogger(__name__)


class SMMLidianCrawler(PCCrawler):
    """SMM锂电渠道爬虫"""
    
    def __init__(self, channel_info):
        super().__init__(channel_info)
