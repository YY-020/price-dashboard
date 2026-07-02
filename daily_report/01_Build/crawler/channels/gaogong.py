# -*- coding: utf-8 -*-
"""
高工锂电渠道爬虫
负责高工锂电的新闻采集
"""

import logging

from crawler.channels.pc_base import PCCrawler

logger = logging.getLogger(__name__)


class GaogongCrawler(PCCrawler):
    """高工锂电渠道爬虫"""
    
    def __init__(self, channel_info):
        super().__init__(channel_info)
