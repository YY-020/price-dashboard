# -*- coding: utf-8 -*-
"""
输出文件命名器
实现 PROJECT.md 中定义的命名规范
"""

import os


class OutputNamer:
    """输出文件命名器"""
    
    def __init__(self, date_str, channels=None):
        """
        Args:
            date_str: 日期字符串，如 '2026-06-25'
            channels: 渠道列表，如 ['electrive_battery', 'electrive_auto']
        """
        self.date_str = date_str.replace('-', '')
        self.channels = channels or []
    
    def get_suffix(self):
        """生成后缀：全渠道只加日期，demo场景加渠道后缀"""
        channel_tags = sorted(set(c.split('_')[0] for c in self.channels))
        
        if len(channel_tags) >= 6:
            return f"_{self.date_str}"
        elif len(channel_tags) == 1:
            return f"_{self.date_str}_{channel_tags[0]}"
        elif 1 < len(channel_tags) < 6:
            return f"_{self.date_str}_{'_'.join(channel_tags)}"
        else:
            return f"_{self.date_str}"
    
    def get_raw_news_path(self, output_dir):
        return os.path.join(output_dir, f"raw_news{self.get_suffix()}.xlsx")
    
    def get_organized_path(self, output_dir):
        return os.path.join(output_dir, f"organized_news{self.get_suffix()}.xlsx")
    
    def get_filtered_path(self, output_dir):
        return os.path.join(output_dir, f"filtered_news{self.get_suffix()}.xlsx")
    
    def get_report_path(self, output_dir):
        return os.path.join(output_dir, f"daily_report{self.get_suffix()}.txt")