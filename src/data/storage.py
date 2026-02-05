# -*- coding: utf-8 -*-
"""JSON 存储管理器"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import date, datetime
import copy

from ..utils.constants import (
    CONFIG_FILE, DATA_FILE, DEFAULT_CONFIG,
    DIET_RECORDS_FILE
)
from ..utils.helpers import load_json, save_json
from .models import (
    Event, Medication, PregnancyConfig, 
    DietRecord, MealRecord, FetalMovementRecord,
    WaterIntakeRecord
)


class StorageManager:
    """存储管理器 - 统一管理所有数据的存取"""
    
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._data: Dict[str, Any] = {}
        self._diet_records: Dict[str, DietRecord] = {}
        
        self._load_all()
    
    def _load_all(self):
        """加载所有数据"""
        # 加载配置，合并默认值
        self._config = self._merge_config(
            copy.deepcopy(DEFAULT_CONFIG),
            load_json(CONFIG_FILE, {})
        )
        
        # 加载数据
        self._data = load_json(DATA_FILE, {
            'events': [],
            'medications': [],
            'fetal_movements': [],
            'daily_tip_cache': {}
        })
        
        # 加载饮食记录
        diet_data = load_json(DIET_RECORDS_FILE, {})
        for date_str, record in diet_data.items():
            self._diet_records[date_str] = DietRecord.from_dict(record)
    
    def _merge_config(self, default: Dict, loaded: Dict) -> Dict:
        """递归合并配置，确保所有默认键存在"""
        result = copy.deepcopy(default)
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self) -> bool:
        """保存配置"""
        return save_json(CONFIG_FILE, self._config)
    
    def save_data(self) -> bool:
        """保存数据"""
        return save_json(DATA_FILE, self._data)
    
    def save_diet_records(self) -> bool:
        """保存饮食记录"""
        data = {k: v.to_dict() for k, v in self._diet_records.items()}
        return save_json(DIET_RECORDS_FILE, data)
    
    # ==================== 配置相关 ====================
    
    @property
    def config(self) -> Dict[str, Any]:
        """获取配置"""
        return self._config
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def set_config(self, key: str, value: Any) -> bool:
        """设置配置项"""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        return self.save_config()
    
    # ==================== 事件相关 ====================
    
    def get_events(self) -> List[Event]:
        """获取所有事件"""
        events_data = self._data.get('events', [])
        return [Event.from_dict(e) for e in events_data]
    
    def get_event(self, event_id: str) -> Optional[Event]:
        """获取单个事件"""
        for event in self.get_events():
            if event.id == event_id:
                return event
        return None
    
    def add_event(self, event: Event) -> bool:
        """添加事件"""
        events = self._data.get('events', [])
        events.append(event.to_dict())
        self._data['events'] = events
        return self.save_data()
    
    def update_event(self, event: Event) -> bool:
        """更新事件"""
        events = self._data.get('events', [])
        for i, e in enumerate(events):
            if e['id'] == event.id:
                events[i] = event.to_dict()
                self._data['events'] = events
                return self.save_data()
        return False
    
    def delete_event(self, event_id: str) -> bool:
        """删除事件"""
        events = self._data.get('events', [])
        self._data['events'] = [e for e in events if e['id'] != event_id]
        return self.save_data()
    
    def get_countdown_events(self) -> List[Event]:
        """获取所有倒计时事件"""
        return [e for e in self.get_events() if e.is_countdown and e.enabled]
    
    # ==================== 药物相关 ====================
    
    def get_medications(self) -> List[Medication]:
        """获取所有药物"""
        meds_data = self._data.get('medications', [])
        return [Medication.from_dict(m) for m in meds_data]
    
    def add_medication(self, medication: Medication) -> bool:
        """添加药物"""
        meds = self._data.get('medications', [])
        meds.append(medication.to_dict())
        self._data['medications'] = meds
        return self.save_data()
    
    def update_medication(self, medication: Medication) -> bool:
        """更新药物"""
        meds = self._data.get('medications', [])
        for i, m in enumerate(meds):
            if m['id'] == medication.id:
                meds[i] = medication.to_dict()
                self._data['medications'] = meds
                return self.save_data()
        return False
    
    def delete_medication(self, med_id: str) -> bool:
        """删除药物"""
        meds = self._data.get('medications', [])
        self._data['medications'] = [m for m in meds if m['id'] != med_id]
        return self.save_data()
    
    # ==================== 孕期相关 ====================
    
    def get_pregnancy_config(self) -> PregnancyConfig:
        """获取孕期配置"""
        config_data = self._config.get('pregnancy', {})
        return PregnancyConfig.from_dict(config_data)
    
    def set_pregnancy_config(self, config: PregnancyConfig) -> bool:
        """设置孕期配置"""
        self._config['pregnancy'] = config.to_dict()
        return self.save_config()
    
    # ==================== 每日建议缓存 ====================
    
    def get_daily_tip_cache(self, cache_date: date) -> Optional[Dict]:
        """获取每日建议缓存"""
        cache = self._data.get('daily_tip_cache', {})
        return cache.get(cache_date.isoformat())
    
    def set_daily_tip_cache(self, cache_date: date, content: Dict) -> bool:
        """设置每日建议缓存"""
        if 'daily_tip_cache' not in self._data:
            self._data['daily_tip_cache'] = {}
        self._data['daily_tip_cache'][cache_date.isoformat()] = {
            'content': content,
            'created_at': datetime.now().isoformat()
        }
        return self.save_data()
    
    # ==================== 饮食记录 ====================
    
    def get_diet_record(self, record_date: date) -> Optional[DietRecord]:
        """获取指定日期的饮食记录"""
        return self._diet_records.get(record_date.isoformat())
    
    def get_today_diet_record(self) -> DietRecord:
        """获取今日饮食记录（如不存在则创建）"""
        today = date.today()
        if today.isoformat() not in self._diet_records:
            self._diet_records[today.isoformat()] = DietRecord(date=today)
        return self._diet_records[today.isoformat()]
    
    def add_meal(self, record_date: date, meal: MealRecord) -> bool:
        """添加餐食记录"""
        if record_date.isoformat() not in self._diet_records:
            self._diet_records[record_date.isoformat()] = DietRecord(date=record_date)
        self._diet_records[record_date.isoformat()].meals.append(meal)
        return self.save_diet_records()
    
    def update_diet_analysis(self, record_date: date, analysis: Dict) -> bool:
        """更新饮食分析结果"""
        if record_date.isoformat() in self._diet_records:
            record = self._diet_records[record_date.isoformat()]
            record.analysis = analysis
            record.analyzed_at = datetime.now()
            return self.save_diet_records()
        return False
    
    # ==================== 胎动记录 ====================
    
    def get_fetal_movements(self, record_date: Optional[date] = None) -> List[FetalMovementRecord]:
        """获取胎动记录"""
        records_data = self._data.get('fetal_movements', [])
        records = [FetalMovementRecord.from_dict(r) for r in records_data]
        if record_date:
            records = [r for r in records if r.date == record_date]
        return records
    
    def add_fetal_movement(self, record: FetalMovementRecord) -> bool:
        """添加胎动记录"""
        if 'fetal_movements' not in self._data:
            self._data['fetal_movements'] = []
        self._data['fetal_movements'].append(record.to_dict())
        return self.save_data()
    
    def update_fetal_movement(self, record: FetalMovementRecord) -> bool:
        """更新胎动记录"""
        records = self._data.get('fetal_movements', [])
        for i, r in enumerate(records):
            if r['id'] == record.id:
                records[i] = record.to_dict()
                self._data['fetal_movements'] = records
                return self.save_data()
        return False
    
    # ==================== 饮水记录 ====================
    
    def get_water_records(self, record_date: date) -> List[WaterIntakeRecord]:
        """获取指定日期的饮水记录"""
        records_data = self._data.get('water_records', [])
        records = [WaterIntakeRecord.from_dict(r) for r in records_data]
        # 按日期筛选
        return [r for r in records if r.time.date() == record_date]
    
    def get_today_water_records(self) -> List[WaterIntakeRecord]:
        """获取今日饮水记录"""
        return self.get_water_records(date.today())
    
    def get_today_water_total(self) -> int:
        """获取今日总饮水量（毫升）"""
        records = self.get_today_water_records()
        return sum(r.amount for r in records)
    
    def get_water_total(self, record_date: date) -> int:
        """获取指定日期总饮水量（毫升）"""
        records = self.get_water_records(record_date)
        return sum(r.amount for r in records)
    
    def add_water_record(self, record: WaterIntakeRecord) -> bool:
        """添加饮水记录"""
        if 'water_records' not in self._data:
            self._data['water_records'] = []
        self._data['water_records'].append(record.to_dict())
        return self.save_data()
    
    def delete_water_record(self, record_id: str) -> bool:
        """删除饮水记录"""
        records = self._data.get('water_records', [])
        self._data['water_records'] = [r for r in records if r['id'] != record_id]
        return self.save_data()
