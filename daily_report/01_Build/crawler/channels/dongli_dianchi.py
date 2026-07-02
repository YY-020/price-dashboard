# -*- coding: utf-8 -*-
"""
动力电池网渠道爬虫
负责动力电池网的新闻采集
"""

import logging

from crawler.channels.pc_base import PCCrawler

logger = logging.getLogger(__name__)


class DongliDianchiCrawler(PCCrawler):
    """动力电池网渠道爬虫"""
    
    def __init__(self, channel_info):
        super().__init__(channel_info)
