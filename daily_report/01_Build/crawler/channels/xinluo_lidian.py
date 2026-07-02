# -*- coding: utf-8 -*-
"""
鑫椤锂电渠道爬虫
负责鑫椤锂电的新闻采集
"""

import logging

from crawler.channels.pc_base import PCCrawler

logger = logging.getLogger(__name__)


class XinluoLidianCrawler(PCCrawler):
    """鑫椤锂电渠道爬虫"""
    
    def __init__(self, channel_info):
        super().__init__(channel_info)
