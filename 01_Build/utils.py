"""
工具函数模块
"""
import pandas as pd
import numpy as np


EXCHANGE_RATE = 7.24


def format_price(value, unit="RMB/t", currency="CNY"):
    """
    格式化价格显示
    """
    if pd.isna(value) or value is None:
        return ""
    
    if currency == "USD":
        value = value / EXCHANGE_RATE
    
    if unit == "RMB/Wh":
        if currency == "USD":
            unit = "USD/Wh"
        if value < 0.01:
            return f"{value:.4f}"
        elif value < 0.1:
            return f"{value:.3f}"
        else:
            return f"{value:.2f}"
    else:
        if currency == "USD":
            unit = "USD/t"
        if value < 1:
            return f"{value:.3f}"
        elif value < 100:
            return f"{value:.1f}"
        else:
            return f"{int(value)}"


def get_weekly_avg(series):
    """获取本周均价"""
    today = pd.Timestamp.now()
    week_start = today - pd.Timedelta(days=today.dayofweek)
    mask = (series.index >= week_start) & (series.index <= today)
    weekly_data = series[mask].dropna()
    if len(weekly_data) == 0:
        return None
    return weekly_data.mean()


def get_period_avg(series, period, date=None):
    """获取指定周期的均价"""
    if date is None:
        date = series.index[-1]
    
    if period == "week":
        week_start = date - pd.Timedelta(days=date.dayofweek)
        week_end = week_start + pd.Timedelta(days=6)
        mask = (series.index >= week_start) & (series.index <= week_end)
    elif period == "month":
        mask = (series.index.year == date.year) & (series.index.month == date.month)
    elif period == "year":
        mask = (series.index.year == date.year)
    else:
        return None
    
    period_data = series[mask].dropna()
    if len(period_data) == 0:
        return None
    return period_data.mean()


def calc_change(current, previous):
    """计算变化百分比"""
    if previous is None or previous == 0 or pd.isna(previous):
        return None
    if pd.isna(current):
        return None
    return (current - previous) / previous * 100


def get_latest_price(series):
    """获取最新价格"""
    return series.dropna().iloc[-1] if len(series.dropna()) > 0 else None


def get_price_on_date(series, date_str):
    """获取指定日期的价格"""
    date = pd.Timestamp(date_str)
    if date in series.index:
        return series[date]
    return None


def get_date_range_str(start_date, end_date):
    """格式化日期范围显示"""
    if start_date.year == end_date.year:
        return f"{start_date.month}/{start_date.day} ~ {end_date.month}/{end_date.day}"
    else:
        return f"{start_date.year}/{start_date.month}/{start_date.day} ~ {end_date.year}/{end_date.month}/{end_date.day}"