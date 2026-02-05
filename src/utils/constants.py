# -*- coding: utf-8 -*-
"""常量定义"""

import os
from pathlib import Path

# 应用信息
APP_NAME = "DrinkWater"
APP_VERSION = "1.0.0"
APP_AUTHOR = "DrinkWater Team"

# 路径配置
PROJECT_ROOT = Path(__file__).parent.parent.parent
SRC_ROOT = PROJECT_ROOT / "src"
RESOURCES_ROOT = PROJECT_ROOT / "resources"

# 用户数据目录（Windows: %APPDATA%/DrinkWater, Mac: ~/Library/Application Support/DrinkWater）
if os.name == 'nt':  # Windows
    USER_DATA_DIR = Path(os.environ.get('APPDATA', '')) / APP_NAME
else:  # Mac/Linux
    USER_DATA_DIR = Path.home() / "Library" / "Application Support" / APP_NAME

# 确保用户数据目录存在
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

# 数据文件路径
CONFIG_FILE = USER_DATA_DIR / "config.json"
DATA_FILE = USER_DATA_DIR / "data.json"
CACHE_FILE = USER_DATA_DIR / "cache.json"
LLM_CONFIG_FILE = USER_DATA_DIR / "llm_config.json"
DIET_RECORDS_FILE = USER_DATA_DIR / "diet_records.json"

# 主题目录
THEMES_DIR = RESOURCES_ROOT / "themes"
DEFAULT_THEME = "hello_kitty"

# 默认配置
DEFAULT_CONFIG = {
    "autostart": False,
    "theme": DEFAULT_THEME,
    "language": "zh_CN",
    "water_reminder": {
        "enabled": True,
        "interval_minutes": 45,
        "start_time": "09:00",
        "end_time": "18:00",
        "daily_target": 1800
    },
    "pregnancy": {
        "enabled": False,
        "last_period_date": None,
        "daily_tip_time": "09:00"
    },
    "workplace_reminders": {
        "stand_up": {
            "enabled": True,
            "interval_minutes": 45,
            "work_hours": {"start": "09:00", "end": "18:00"},
            "exclude_lunch": True
        },
        "eye_rest": {
            "enabled": True,
            "interval_minutes": 20
        },
        "nutrition": {
            "enabled": True,
            "snacks": [
                {"time": "10:00", "name": "上午加餐"},
                {"time": "15:00", "name": "下午茶"}
            ]
        },
        "medication": {
            "items": []
        },
        "posture": {
            "enabled": True,
            "interval_minutes": 30
        },
        "relaxation": {
            "enabled": True,
            "times": ["10:30", "16:00"]
        },
        "fetal_movement": {
            "enabled": False,
            "enable_week": 18,
            "times": ["09:00", "14:00", "20:00"]
        },
        "nap": {
            "enabled": True,
            "time": "12:30",
            "duration_minutes": 30
        }
    },
    "ai_mode": "smart",  # smart, full, minimal, off
    "notifications": {
        "sound": True,
        "popup": True,
        "duration_seconds": 5
    }
}

# 提醒优先级
class ReminderPriority:
    URGENT = 0      # 紧急（药物、产检）
    IMPORTANT = 1   # 重要（胎动记录、营养补充）
    NORMAL = 2      # 常规（喝水、站立、眼睛休息）
    SUGGESTED = 3   # 建议（情绪放松、姿势调整）

# AI 模式配置
AI_MODE_OPTIONS = {
    'smart': {
        'name': '智能模式（推荐）',
        'desc': '重要提醒用 AI，其他用模板',
        'ai_types': ['daily_tips', 'nutrition', 'posture'],
        'max_calls': 5,
    },
    'full': {
        'name': '完全 AI',
        'desc': '所有提醒都用 AI 生成',
        'ai_types': ['daily_tips', 'nutrition', 'posture', 'stand_up', 'relaxation'],
        'max_calls': 10,
    },
    'minimal': {
        'name': '节约模式',
        'desc': '仅每日建议用 AI',
        'ai_types': ['daily_tips'],
        'max_calls': 1,
    },
    'off': {
        'name': '关闭 AI',
        'desc': '全部使用固定模板',
        'ai_types': [],
        'max_calls': 0,
    }
}

# 降级模板
FALLBACK_TEMPLATES = {
    'nutrition': "🍎 加餐时间到！建议：坚果 10 颗 / 水果 1 份 / 酸奶 1 杯",
    'relaxation': "🧘‍♀️ 深呼吸 5 次，闭目 1 分钟，放松身心～",
    'stand_up': "💃 起来活动 3-5 分钟，绕办公室走走，促进血液循环～",
    'posture': "🪑 检查坐姿：背挺直，脚平放，腰垫靠垫，别跷腿～",
    'daily_tips': "💝 今日提示：多喝水，适度活动，保持好心情，按时产检～",
    'water': "💧 该喝水啦！保持水分摄入，对你和宝宝都很重要～",
    'eye_rest': "👀 眼睛休息时间！看看远处，眨眨眼，做做眼保健操～",
    'medication': "💊 吃药时间到！记得按时服用哦～",
    'nap': "😴 午休时间到！休息 30 分钟，恢复精力～",
    'fetal_movement': "👶 记录胎动时间！安静下来感受宝宝的活动～"
}

# GitHub 更新配置
GITHUB_REPO = "your-username/drinkwater"  # 替换为实际的仓库地址
UPDATE_CHECK_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
