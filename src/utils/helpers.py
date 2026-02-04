# -*- coding: utf-8 -*-
"""通用工具函数"""

import json
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Optional, Any, Dict


def load_json(file_path: Path, default: Any = None) -> Any:
    """安全加载 JSON 文件"""
    try:
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"加载 JSON 文件失败 {file_path}: {e}")
    return default if default is not None else {}


def save_json(file_path: Path, data: Any, indent: int = 2) -> bool:
    """安全保存 JSON 文件"""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent, default=str)
        return True
    except IOError as e:
        print(f"保存 JSON 文件失败 {file_path}: {e}")
        return False


def calculate_pregnancy_week(last_period_date: date) -> tuple[int, int]:
    """
    计算孕周
    
    Args:
        last_period_date: 末次月经日期
        
    Returns:
        (周数, 天数) 例如 (12, 3) 表示 12 周 + 3 天
    """
    today = date.today()
    days = (today - last_period_date).days
    weeks = days // 7
    remaining_days = days % 7
    return weeks, remaining_days


def calculate_due_date(last_period_date: date) -> date:
    """
    计算预产期（末次月经 + 280 天）
    
    Args:
        last_period_date: 末次月经日期
        
    Returns:
        预产期日期
    """
    return last_period_date + timedelta(days=280)


def days_until(target_date: date) -> int:
    """计算距离目标日期的天数"""
    return (target_date - date.today()).days


def format_time(time_str: str) -> str:
    """格式化时间字符串为标准格式 HH:MM"""
    try:
        t = datetime.strptime(time_str, "%H:%M")
        return t.strftime("%H:%M")
    except ValueError:
        return time_str


def is_within_time_range(start_time: str, end_time: str) -> bool:
    """检查当前时间是否在指定时间范围内"""
    now = datetime.now().time()
    start = datetime.strptime(start_time, "%H:%M").time()
    end = datetime.strptime(end_time, "%H:%M").time()
    
    if start <= end:
        return start <= now <= end
    else:
        # 跨午夜的情况
        return now >= start or now <= end


def get_current_season() -> str:
    """获取当前季节"""
    month = datetime.now().month
    if month in [3, 4, 5]:
        return "春季"
    elif month in [6, 7, 8]:
        return "夏季"
    elif month in [9, 10, 11]:
        return "秋季"
    else:
        return "冬季"


def get_time_period() -> str:
    """获取当前时段"""
    hour = datetime.now().hour
    if 5 <= hour < 9:
        return "早晨"
    elif 9 <= hour < 12:
        return "上午"
    elif 12 <= hour < 14:
        return "中午"
    elif 14 <= hour < 18:
        return "下午"
    elif 18 <= hour < 22:
        return "晚上"
    else:
        return "深夜"


def truncate_text(text: str, max_length: int = 50) -> str:
    """截断文本，超出部分用省略号代替"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def generate_unique_id() -> str:
    """生成唯一 ID"""
    import uuid
    return str(uuid.uuid4())[:8]


def parse_date(date_str: str) -> Optional[date]:
    """解析日期字符串"""
    formats = ["%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None


def format_date(d: date, include_weekday: bool = False) -> str:
    """格式化日期"""
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    result = d.strftime("%Y-%m-%d")
    if include_weekday:
        result += f" {weekdays[d.weekday()]}"
    return result
