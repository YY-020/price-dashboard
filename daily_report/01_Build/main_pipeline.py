# -*- coding: utf-8 -*-
"""
日报系统主流程
执行顺序：采集 → 理解分类 → 筛选 → 摘要生成 → 翻译 → 日报生成 → 渠道评估
只做流程编排，不做参数解析，不做日期计算
"""

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from constants import DEEPSEEK_API_KEY


def run_pipeline(
    start_date, end_date, channels=None,
    raw_news_path=None, organized_path=None, filtered_path=None, report_path=None,
    skip_crawl=False, skip_translate=False, skip_summarize=False, skip_eval=False
):
    """
    主流程编排
    
    Args:
        start_date: 开始日期字符串 YYYY-MM-DD
        end_date: 结束日期字符串 YYYY-MM-DD
        channels: 渠道列表
        raw_news_path: 原始新闻输出路径
        organized_path: 整理后新闻输出路径
        filtered_path: 筛选后新闻输出路径
        report_path: 日报输出路径
        skip_crawl: 是否跳过采集
        skip_translate: 是否跳过翻译
        skip_summarize: 是否跳过摘要生成
        skip_eval: 是否跳过渠道评估
    """
    from datetime import datetime
    
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')

    # Step 1: 采集
    if not skip_crawl:
        logger.info("[1/7] 新闻采集...")
        from crawler.scheduler import NewsCrawler
        crawler = NewsCrawler()
        crawler.run(start_dt, end_dt, channels=channels)
        crawler.save(raw_news_path)
    else:
        logger.info("[1/7] 跳过采集")

    # Step 2: 理解分类
    logger.info("[2/7] 新闻整理...")
    from news_organizer import NewsOrganizer
    organizer = NewsOrganizer(api_key=DEEPSEEK_API_KEY)
    organizer.organize(raw_news_path, organized_path)

    # Step 3: 筛选
    logger.info("[3/7] 新闻筛选...")
    from news_filter import NewsFilter
    news_filter = NewsFilter()
    news_filter.filter(organized_path, filtered_path)

    # Step 4: 摘要生成
    if not skip_summarize:
        logger.info("[4/7] 摘要生成...")
        from news_summarizer import NewsSummarizer
        summarizer = NewsSummarizer(api_key=DEEPSEEK_API_KEY)
        summarizer.summarize(filtered_path, filtered_path)
    else:
        logger.info("[4/7] 跳过摘要生成")

    # Step 5: 翻译
    if not skip_translate:
        logger.info("[5/7] 翻译...")
        from news_translator import NewsTranslator
        translator = NewsTranslator(api_key=DEEPSEEK_API_KEY)
        translator.translate(filtered_path, filtered_path)
    else:
        logger.info("[5/7] 跳过翻译")

    # Step 6: 生成日报
    logger.info("[6/7] 日报生成...")
    from report_generator import ReportGenerator
    generator = ReportGenerator()
    generator.generate(filtered_path, report_path)

    # Step 7: 渠道评估
    if not skip_eval:
        logger.info("[7/7] 渠道评估...")
        try:
            from channel_evaluation import ChannelEvaluator
            evaluator = ChannelEvaluator()
            evaluator.evaluate(organized_path, filtered_path, report_path.replace('.txt', '_eval.txt'))
        except ImportError:
            logger.info("[7/7] 渠道评估模块未安装，跳过")
    else:
        logger.info("[7/7] 跳过渠道评估")

    logger.info("=" * 50)
    logger.info("完成")
    logger.info("=" * 50)