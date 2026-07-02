# -*- coding: utf-8 -*-
"""
渠道评估模块
评估各渠道的表现，包括：相关性、独特性、效率、时效性、稳定性
"""

import pandas as pd
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ChannelEvaluator:
    """渠道评估器"""
    
    def evaluate(self, organized_path, filtered_path, output_path):
        """
        评估各渠道表现
        
        Args:
            organized_path: 整理后新闻路径
            filtered_path: 筛选后新闻路径
            output_path: 评估报告输出路径
        """
        logger.info("开始渠道评估...")
        
        organized_df = pd.read_excel(organized_path)
        filtered_df = pd.read_excel(filtered_path)
        
        channels = organized_df['渠道ID'].unique()
        
        results = []
        
        for channel_id in channels:
            raw_count = len(organized_df[organized_df['渠道ID'] == channel_id])
            filtered_count = len(filtered_df[filtered_df['渠道ID'] == channel_id])
            
            channel_name = organized_df[organized_df['渠道ID'] == channel_id]['来源'].iloc[0] if raw_count > 0 else channel_id
            
            relevance = self._calculate_relevance(filtered_count, raw_count)
            uniqueness = self._calculate_uniqueness(channel_id, channel_name, organized_df, filtered_df)
            efficiency = relevance
            timeliness = self._calculate_timeliness(channel_id, organized_df)
            stability = self._calculate_stability(raw_count)
            
            results.append({
                '渠道ID': channel_id,
                '渠道名称': channel_name,
                '原始采集数': raw_count,
                '筛选保留数': filtered_count,
                '相关性(保留率)': relevance,
                '独特性(独家率)': uniqueness,
                '效率(保留率)': efficiency,
                '时效性(近期占比)': timeliness,
                '稳定性(采集成功率)': stability,
            })
        
        report = self._generate_report(results, organized_df, filtered_df)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"渠道评估报告已保存: {output_path}")
        logger.info(report)
    
    def _calculate_relevance(self, filtered_count, raw_count):
        """
        相关性：筛选后保留数 ÷ 总采集数
        越高越好，低说明噪音多
        """
        if raw_count == 0:
            return 0.0
        return round(filtered_count / raw_count, 4)
    
    def _calculate_uniqueness(self, channel_id, channel_name, organized_df, filtered_df):
        """
        独特性：独家新闻数 ÷ 该渠道保留总数
        是否有其他渠道没有的独家新闻
        """
        channel_filtered = filtered_df[filtered_df['渠道ID'] == channel_id]
        
        if len(channel_filtered) == 0:
            return 0.0
        
        other_channels = filtered_df[filtered_df['渠道ID'] != channel_id]
        other_titles = set(other_channels['标题'].str.strip())
        
        unique_count = 0
        for title in channel_filtered['标题']:
            if str(title).strip() not in other_titles:
                unique_count += 1
        
        return round(unique_count / len(channel_filtered), 4)
    
    def _calculate_timeliness(self, channel_id, organized_df):
        """
        时效性：发布日期在抓取前1-2天内的新闻占比
        新闻是否及时反映最新动态
        """
        channel_news = organized_df[organized_df['渠道ID'] == channel_id]
        
        if len(channel_news) == 0:
            return 0.0
        
        today = datetime.now()
        recent_count = 0
        
        for pub_date in channel_news['发布时间']:
            if pd.isna(pub_date):
                continue
            
            if isinstance(pub_date, str):
                try:
                    pub_date = datetime.strptime(str(pub_date)[:10], '%Y-%m-%d')
                except:
                    continue
            elif not isinstance(pub_date, datetime):
                try:
                    pub_date = pd.to_datetime(pub_date)
                except:
                    continue
            
            days_diff = (today - pub_date).days
            if days_diff <= 2:
                recent_count += 1
        
        return round(recent_count / len(channel_news), 4)
    
    def _calculate_stability(self, raw_count):
        """
        稳定性：采集成功率
        简单用是否采集到新闻来判断，后期可扩展为成功率
        """
        return 1.0 if raw_count > 0 else 0.0
    
    def _generate_report(self, results, organized_df, filtered_df):
        """生成详细评估报告"""
        total_raw = len(organized_df)
        total_filtered = len(filtered_df)
        
        report = []
        report.append("=" * 90)
        report.append("渠道评估报告")
        report.append("=" * 90)
        report.append(f"评估时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"总采集数: {total_raw}")
        report.append(f"总筛选数: {total_filtered}")
        report.append(f"整体保留率: {round(total_filtered / total_raw, 4) if total_raw > 0 else 0:.2%}")
        report.append("")
        
        report.append("-" * 90)
        report.append("各渠道评估详情")
        report.append("-" * 90)
        
        header = f"{'渠道ID':<20} {'渠道名称':<15} {'原始数':>6} {'保留数':>6} {'相关性':>8} {'独特性':>8} {'效率':>8} {'时效性':>8} {'稳定性':>8}"
        report.append(header)
        report.append("-" * 90)
        
        for r in results:
            line = f"{r['渠道ID']:<20} {r['渠道名称']:<15} {r['原始采集数']:>6} {r['筛选保留数']:>6} {r['相关性(保留率)']:>8.2%} {r['独特性(独家率)']:>8.2%} {r['效率(保留率)']:>8.2%} {r['时效性(近期占比)']:>8.2%} {r['稳定性(采集成功率)']:>8.2%}"
            report.append(line)
        
        report.append("")
        report.append("-" * 90)
        report.append("指标详细解读")
        report.append("-" * 90)
        
        for r in results:
            report.append(f"\n【{r['渠道名称']}】")
            report.append(f"  - 原始采集数: {r['原始采集数']} 条")
            report.append(f"  - 筛选保留数: {r['筛选保留数']} 条")
            
            relevance_val = r['相关性(保留率)']
            if relevance_val >= 0.8:
                relevance_desc = "优秀 - 噪音少，内容精准"
            elif relevance_val >= 0.5:
                relevance_desc = "良好 - 有一定噪音但整体质量尚可"
            else:
                relevance_desc = "较差 - 噪音较多，建议优化筛选规则"
            report.append(f"  - 相关性: {relevance_val:.2%} → {relevance_desc}")
            
            uniqueness_val = r['独特性(独家率)']
            if uniqueness_val >= 0.5:
                uniqueness_desc = "高 - 提供较多独家内容，有独特价值"
            elif uniqueness_val >= 0.2:
                uniqueness_desc = "中等 - 有部分独家内容"
            else:
                uniqueness_desc = "低 - 内容与其他渠道高度重合"
            report.append(f"  - 独特性: {uniqueness_val:.2%} → {uniqueness_desc}")
            
            timeliness_val = r['时效性(近期占比)']
            if timeliness_val >= 0.7:
                timeliness_desc = "及时 - 新闻时效性强"
            elif timeliness_val >= 0.4:
                timeliness_desc = "一般 - 部分新闻时效性不足"
            else:
                timeliness_desc = "滞后 - 新闻更新不及时"
            report.append(f"  - 时效性: {timeliness_val:.2%} → {timeliness_desc}")
            
            stability_val = r['稳定性(采集成功率)']
            if stability_val == 1.0:
                stability_desc = "稳定 - 采集成功"
            else:
                stability_desc = "不稳定 - 采集失败"
            report.append(f"  - 稳定性: {stability_val:.2%} → {stability_desc}")
        
        report.append("")
        report.append("-" * 90)
        report.append("综合评估")
        report.append("-" * 90)
        
        good_channels = [r for r in results if r['相关性(保留率)'] >= 0.5 and r['稳定性(采集成功率)'] == 1.0]
        bad_channels = [r for r in results if r['相关性(保留率)'] < 0.3 or r['稳定性(采集成功率)'] == 0.0]
        
        if good_channels:
            report.append(f"✓ 优质渠道 ({len(good_channels)}个):")
            for r in good_channels:
                report.append(f"  - {r['渠道名称']}: 相关性{r['相关性(保留率)']:.2%}，独特性{r['独特性(独家率)']:.2%}")
        
        if bad_channels:
            report.append(f"\n✗ 需优化渠道 ({len(bad_channels)}个):")
            for r in bad_channels:
                if r['稳定性(采集成功率)'] == 0.0:
                    report.append(f"  - {r['渠道名称']}: 采集失败，需检查爬虫逻辑")
                else:
                    report.append(f"  - {r['渠道名称']}: 相关性仅{r['相关性(保留率)']:.2%}，噪音较多")
        
        report.append(f"\n整体渠道质量评估:")
        avg_relevance = sum(r['相关性(保留率)'] for r in results) / len(results) if results else 0
        avg_uniqueness = sum(r['独特性(独家率)'] for r in results) / len(results) if results else 0
        
        if avg_relevance >= 0.7:
            quality_desc = "优秀"
        elif avg_relevance >= 0.5:
            quality_desc = "良好"
        else:
            quality_desc = "一般"
        
        report.append(f"  - 平均相关性: {avg_relevance:.2%}")
        report.append(f"  - 平均独特性: {avg_uniqueness:.2%}")
        report.append(f"  - 综合评价: {quality_desc}")
        
        report.append("")
        report.append("-" * 90)
        report.append("指标计算公式")
        report.append("-" * 90)
        report.append("  相关性(保留率) = 筛选后保留数 ÷ 总采集数")
        report.append("  独特性(独家率) = 独家新闻数 ÷ 该渠道保留总数")
        report.append("  效率(保留率) = 同相关性指标")
        report.append("  时效性(近期占比) = 发布日期在抓取前1-2天内的新闻数 ÷ 该渠道总采集数")
        report.append("  稳定性(采集成功率) = 是否成功采集到新闻（1=成功，0=失败）")
        report.append("=" * 90)
        
        return "\n".join(report)
