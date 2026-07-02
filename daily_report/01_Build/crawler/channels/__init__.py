# -*- coding: utf-8 -*-
"""
渠道模块注册器
暴露所有渠道类，供 scheduler 调用
"""

from crawler.channels.electrive import ElectriveCrawler
from crawler.channels.ofweek import OfweekCrawler
from crawler.channels.battery_news_de import BatteryNewsDECrawler
from crawler.channels.marklines import MarkLinesCrawler
from crawler.channels.thelec import ThelecCrawler
from crawler.channels.gaogong import GaogongCrawler
from crawler.channels.wode_dianchi import WodeDianchiCrawler
from crawler.channels.dongli_dianchi import DongliDianchiCrawler
from crawler.channels.xinluo_lidian import XinluoLidianCrawler
from crawler.channels.smm_lidian import SMMLidianCrawler

CHANNEL_CRAWLERS = {
    'electrive_battery': ElectriveCrawler,
    'electrive_auto': ElectriveCrawler,
    'electrive_politics': ElectriveCrawler,
    'battery_news_de': BatteryNewsDECrawler,
    'marklines': MarkLinesCrawler,
    'thelec': ThelecCrawler,
    'weike_lidian': OfweekCrawler,
    'gaogong_lidian': GaogongCrawler,
    'wode_dianchi': WodeDianchiCrawler,
    'dongli_dianchi': DongliDianchiCrawler,
    'xinluo_lidian': XinluoLidianCrawler,
    'smm_lidian': SMMLidianCrawler,
}

__all__ = ['CHANNEL_CRAWLERS', 'ElectriveCrawler', 'OfweekCrawler', 
           'BatteryNewsDECrawler', 'MarkLinesCrawler', 'ThelecCrawler',
           'GaogongCrawler', 'WodeDianchiCrawler', 'DongliDianchiCrawler',
           'XinluoLidianCrawler', 'SMMLidianCrawler']