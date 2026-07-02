# -*- coding: utf-8 -*-
"""
日报生成模块
根据整理后的新闻生成日报文本
"""

import logging
import pandas as pd
from datetime import datetime
from constants import FILTERED_NEWS_FILE, DAILY_REPORT_FILE

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self):
        self.topic_order = ["政策", "新能源车", "储能", "锂电池", "固态电池",
                          "电解液", "CNT", "矿产", "新兴应用"]

    def _get_topic_label(self, topic):
        """获取中文话题标签"""
        if not topic or str(topic) in ("nan", "None", ""):
            return "其他"
        return str(topic)

    def load_filtered_news(self, file_path=None):
        if file_path is None:
            file_path = FILTERED_NEWS_FILE
        try:
            df = pd.read_excel(file_path)
            logger.info(f"加载筛选后新闻，共 {len(df)} 条")
            return df
        except Exception as e:
            logger.error(f"加载失败: {e}")
            raise

    def generate_report(self, df):
        logger.info("开始生成日报...")

        # 只保留筛选通过的新闻（删除原因为空或NaN）
        if "删除原因" in df.columns:
            before = len(df)
            df = df[df["删除原因"].isna() | (df["删除原因"] == "")].copy()
            logger.info(f"筛选后保留 {len(df)} 条（共 {before} 条）")

        report_lines = []
        today = datetime.now().strftime('%Y年%m月%d日')

        report_lines.append(f"【锂电行业日报】{today}")
        report_lines.append("=" * 60)
        report_lines.append("")

        # 统计概览
        report_lines.append(f"📊 今日共收录 {len(df)} 条重要新闻")
        priority_counts = df["优先级"].value_counts()
        for p in ["🚨置顶", "⭐高", "●中", "○低"]:
            c = priority_counts.get(p, 0)
            if c > 0:
                report_lines.append(f"   {p}: {c} 条")
        report_lines.append("")

        # 先输出置顶板块（仅当有置顶内容时）
        top_pin = df[df["优先级"] == "🚨置顶"]
        if len(top_pin) > 0:
            report_lines.append("🚨 重大事件")
            report_lines.append("-" * 40)
            for _, row in top_pin.iterrows():
                self._append_news_item(report_lines, row)
            report_lines.append("")

        # 按话题标签分组输出
        for topic in self.topic_order:
            topic_news = df[(df["产业链"] == topic) & (df["优先级"] != "🚨置顶")]
            if len(topic_news) == 0:
                continue

            report_lines.append(f"【{self._get_topic_label(topic)}】")
            report_lines.append("-" * 40)

            # 按优先级排序
            po = {"🚨置顶": 0, "⭐高": 1, "●中": 2, "○低": 3}
            topic_news = topic_news.copy()
            topic_news["_s"] = topic_news["优先级"].map(po)
            topic_news = topic_news.sort_values("_s")

            for _, row in topic_news.iterrows():
                self._append_news_item(report_lines, row)
            report_lines.append("")

        # 未分类
        uncat = df[(df["产业链"].isin(["", "其他", "nan"])) & (df["优先级"] != "🚨置顶")]
        if len(uncat) > 0:
            report_lines.append("【其他】")
            report_lines.append("-" * 40)
            for _, row in uncat.iterrows():
                self._append_news_item(report_lines, row)
            report_lines.append("")

        report_lines.append("=" * 60)
        report_lines.append(f"⏰ 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("📝 备注：本日报为自动生成，请人工审核后发送")

        return "\n".join(report_lines)

    def _append_news_item(self, lines, row):
        priority = row.get("优先级", "")
        title = row.get("标题_CN", "") or row.get("标题", "")
        summary = row.get("摘要_CN", "") or row.get("摘要_AI", "")
        link = row.get("链接", "")
        enterprise = row.get("企业标签", "")

        line = f"{priority} {title}"
        if enterprise and str(enterprise) not in ("无", "nan", ""):
            line += f" ({enterprise})"
        lines.append(line)

        if summary:
            lines.append(f"    摘要：{summary}")
        lines.append(f"    链接：{link}")
        lines.append("")

    def save_report(self, report_text, file_path=None):
        if file_path is None:
            file_path = DAILY_REPORT_FILE
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        logger.info(f"日报已保存到: {file_path}")
        return file_path

    def generate(self, input_path, output_path):
        """便捷方法：读取筛选结果 → 生成日报 → 保存"""
        df = pd.read_excel(input_path)
        if df.empty:
            logger.warning("没有筛选后的新闻")
            return None
        report = self.generate_report(df)
        self.save_report(report, output_path)
        return report

    def run(self):
        df = self.load_filtered_news()
        if df.empty:
            logger.warning("没有筛选后的新闻")
            return None
        report = self.generate_report(df)
        self.save_report(report)
        return report