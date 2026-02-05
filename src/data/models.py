# -*- coding: utf-8 -*-
"""数据模型定义"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, date, time
from typing import Optional, List, Dict, Any
from enum import Enum
import json


class RepeatType(Enum):
    """重复类型"""
    ONCE = "once"           # 一次性
    DAILY = "daily"         # 每天
    WEEKLY = "weekly"       # 每周
    MONTHLY = "monthly"     # 每月
    WORKDAYS = "workdays"   # 工作日


class ReminderType(Enum):
    """提醒类型"""
    WATER = "water"                 # 喝水
    EVENT = "event"                 # 普通事件
    COUNTDOWN = "countdown"         # 倒计时
    PREGNANCY_TIP = "pregnancy_tip" # 孕期建议
    STAND_UP = "stand_up"           # 站立活动
    EYE_REST = "eye_rest"           # 眼睛休息
    NUTRITION = "nutrition"         # 营养补充
    MEDICATION = "medication"       # 药物提醒
    POSTURE = "posture"             # 姿势调整
    RELAXATION = "relaxation"       # 情绪放松
    FETAL_MOVEMENT = "fetal_movement"  # 胎动记录
    NAP = "nap"                     # 午休


@dataclass
class Event:
    """事件模型"""
    id: str
    title: str
    description: str = ""
    remind_time: Optional[datetime] = None
    repeat_type: RepeatType = RepeatType.ONCE
    is_countdown: bool = False
    target_date: Optional[date] = None
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['repeat_type'] = self.repeat_type.value
        data['remind_time'] = self.remind_time.isoformat() if self.remind_time else None
        data['target_date'] = self.target_date.isoformat() if self.target_date else None
        data['created_at'] = self.created_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """从字典创建"""
        data = data.copy()
        data['repeat_type'] = RepeatType(data.get('repeat_type', 'once'))
        if data.get('remind_time'):
            data['remind_time'] = datetime.fromisoformat(data['remind_time'])
        if data.get('target_date'):
            data['target_date'] = date.fromisoformat(data['target_date'])
        if data.get('created_at'):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


@dataclass
class Medication:
    """药物模型"""
    id: str
    name: str
    dosage: str = ""
    times: List[str] = field(default_factory=list)  # ["09:00", "21:00"]
    cycle: RepeatType = RepeatType.DAILY
    start_date: Optional[date] = None
    duration_days: Optional[int] = None
    notes: str = ""
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['cycle'] = self.cycle.value
        data['start_date'] = self.start_date.isoformat() if self.start_date else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Medication':
        """从字典创建"""
        data = data.copy()
        data['cycle'] = RepeatType(data.get('cycle', 'daily'))
        if data.get('start_date'):
            data['start_date'] = date.fromisoformat(data['start_date'])
        return cls(**data)


@dataclass
class PregnancyConfig:
    """孕期配置"""
    enabled: bool = False
    last_period_date: Optional[date] = None
    daily_tip_time: str = "09:00"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'enabled': self.enabled,
            'last_period_date': self.last_period_date.isoformat() if self.last_period_date else None,
            'daily_tip_time': self.daily_tip_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PregnancyConfig':
        """从字典创建"""
        data = data.copy()
        if data.get('last_period_date'):
            data['last_period_date'] = date.fromisoformat(data['last_period_date'])
        return cls(**data)
    
    @property
    def current_week(self) -> Optional[int]:
        """获取当前孕周"""
        if not self.last_period_date:
            return None
        days = (date.today() - self.last_period_date).days
        return days // 7
    
    @property
    def current_week_day(self) -> Optional[tuple]:
        """获取当前孕周和天数"""
        if not self.last_period_date:
            return None
        days = (date.today() - self.last_period_date).days
        return days // 7, days % 7
    
    @property
    def due_date(self) -> Optional[date]:
        """获取预产期"""
        if not self.last_period_date:
            return None
        from datetime import timedelta
        return self.last_period_date + timedelta(days=280)


@dataclass
class DailyTipCache:
    """每日建议缓存"""
    date: date
    week_number: int
    tips_content: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'date': self.date.isoformat(),
            'week_number': self.week_number,
            'tips_content': self.tips_content,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DailyTipCache':
        """从字典创建"""
        data = data.copy()
        data['date'] = date.fromisoformat(data['date'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


@dataclass
class MealRecord:
    """餐食记录"""
    type: str  # breakfast, lunch, dinner, snack
    time: str
    foods: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MealRecord':
        return cls(**data)


@dataclass
class DietRecord:
    """每日饮食记录"""
    date: date
    meals: List[MealRecord] = field(default_factory=list)
    analysis: Optional[Dict[str, Any]] = None
    analyzed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'date': self.date.isoformat(),
            'meals': [m.to_dict() for m in self.meals],
            'analysis': self.analysis,
            'analyzed_at': self.analyzed_at.isoformat() if self.analyzed_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DietRecord':
        data = data.copy()
        data['date'] = date.fromisoformat(data['date'])
        data['meals'] = [MealRecord.from_dict(m) for m in data.get('meals', [])]
        if data.get('analyzed_at'):
            data['analyzed_at'] = datetime.fromisoformat(data['analyzed_at'])
        return cls(**data)


@dataclass  
class FetalMovementRecord:
    """胎动记录"""
    id: str
    date: date
    start_time: datetime
    end_time: Optional[datetime] = None
    count: int = 0
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'count': self.count,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FetalMovementRecord':
        data = data.copy()
        data['date'] = date.fromisoformat(data['date'])
        data['start_time'] = datetime.fromisoformat(data['start_time'])
        if data.get('end_time'):
            data['end_time'] = datetime.fromisoformat(data['end_time'])
        return cls(**data)


@dataclass
class WaterIntakeRecord:
    """饮水记录"""
    id: str
    time: datetime
    amount: int  # 毫升
    note: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'time': self.time.isoformat(),
            'amount': self.amount,
            'note': self.note
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WaterIntakeRecord':
        """从字典创建"""
        data = data.copy()
        data['time'] = datetime.fromisoformat(data['time'])
        return cls(**data)
