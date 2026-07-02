# -*- coding: utf-8 -*-
"""
日报系统唯一入口
用法：
    # 日常自动运行（采集昨天到今天的所有渠道）
    python run.py

    # 指定日期范围和渠道
    python run.py --start 2026-06-08 --end 2026-06-12 --channels electrive_battery,electrive_auto

    # 只跑某个渠道
    python run.py --channels weike_lidian

    # 跳过步骤
    python run.py --skip-crawl --skip-translate --skip-summarize --skip-eval

    # 测试模式（输出文件带日期和渠道后缀）
    python run.py --channels electrive_battery --start 2026-06-08 --end 2026-06-12
"""

import argparse
import logging
import os
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OUTPUT_DIR = 'D:/0_trea_projects_by_bela/daily_report/02_Output'


def main():
    parser = argparse.ArgumentParser(description='日报系统')

    parser.add_argument('--start', type=str, help='开始日期 YYYY-MM-DD')
    parser.add_argument('--end', type=str, help='结束日期 YYYY-MM-DD')
    parser.add_argument('--channels', type=str, help='指定渠道ID，逗号分隔')

    parser.add_argument('--skip-crawl', action='store_true', help='跳过采集')
    parser.add_argument('--skip-translate', action='store_true', help='跳过翻译')
    parser.add_argument('--skip-summarize', action='store_true', help='跳过摘要生成')
    parser.add_argument('--skip-eval', action='store_true', help='跳过渠道评估')

    args = parser.parse_args()

    if args.start and args.end:
        start_date = args.start
        end_date = args.end
    else:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    channels = None
    if args.channels:
        channels = [c.strip() for c in args.channels.split(',')]

    logger.info("=" * 50)
    logger.info(f"日报系统启动")
    logger.info(f"日期范围: {start_date} ~ {end_date}")
    logger.info(f"渠道: {channels if channels else '全部'}")
    logger.info("=" * 50)

    from utils.output_namer import OutputNamer
    namer = OutputNamer(end_date, channels)

    raw_news_path = namer.get_raw_news_path(OUTPUT_DIR)
    organized_path = namer.get_organized_path(OUTPUT_DIR)
    filtered_path = namer.get_filtered_path(OUTPUT_DIR)
    report_path = namer.get_report_path(OUTPUT_DIR)

    from main_pipeline import run_pipeline
    run_pipeline(
        start_date=start_date,
        end_date=end_date,
        channels=channels,
        raw_news_path=raw_news_path,
        organized_path=organized_path,
        filtered_path=filtered_path,
        report_path=report_path,
        skip_crawl=args.skip_crawl,
        skip_translate=args.skip_translate,
        skip_summarize=args.skip_summarize,
        skip_eval=args.skip_eval
    )

    logger.info("=" * 50)
    logger.info(f"输出文件:")
    logger.info(f"  raw_news: {raw_news_path}")
    logger.info(f"  organized_news: {organized_path}")
    logger.info(f"  filtered_news: {filtered_path}")
    logger.info(f"  daily_report: {report_path}")
    logger.info("=" * 50)


if __name__ == '__main__':
    main()