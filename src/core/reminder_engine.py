# -*- coding: utf-8 -*-
"""提醒引擎 - 统一管理所有提醒"""

from typing import Optional, Dict, Any, Callable
from datetime import datetime, date, time
from PySide6.QtCore import QObject, Signal

from .scheduler import SchedulerManager
from ..data.storage import StorageManager
from ..data.models import ReminderType, RepeatType
from ..utils.constants import FALLBACK_TEMPLATES, ReminderPriority
from ..utils.helpers import is_within_time_range


class ReminderEngine(QObject):
    """提醒引擎 - 管理所有类型的提醒"""
    
    # 信号：提醒触发时发出
    reminder_triggered = Signal(str, str, str, int)  # type, title, content, priority
    
    def __init__(self, storage: StorageManager, scheduler: SchedulerManager):
        super().__init__()
        self._storage = storage
        self._scheduler = scheduler
        self._notification_callback: Optional[Callable] = None
    
    def set_notification_callback(self, callback: Callable):
        """设置通知回调函数"""
        self._notification_callback = callback
    
    def load_reminders(self):
        """加载并启动所有已配置的提醒"""
        config = self._storage.config
        
        # 1. 喝水提醒
        water_config = config.get('water_reminder', {})
        if water_config.get('enabled', False):
            self._setup_water_reminder(water_config)
        
        # 2. 职场健康提醒
        workplace = config.get('workplace_reminders', {})
        
        # 站立提醒
        stand_up = workplace.get('stand_up', {})
        if stand_up.get('enabled', False):
            self._setup_stand_up_reminder(stand_up)
        
        # 眼睛休息
        eye_rest = workplace.get('eye_rest', {})
        if eye_rest.get('enabled', False):
            self._setup_eye_rest_reminder(eye_rest)
        
        # 营养补充
        nutrition = workplace.get('nutrition', {})
        if nutrition.get('enabled', False):
            self._setup_nutrition_reminder(nutrition)
        
        # 姿势调整
        posture = workplace.get('posture', {})
        if posture.get('enabled', False):
            self._setup_posture_reminder(posture)
        
        # 情绪放松
        relaxation = workplace.get('relaxation', {})
        if relaxation.get('enabled', False):
            self._setup_relaxation_reminder(relaxation)
        
        # 午休提醒
        nap = workplace.get('nap', {})
        if nap.get('enabled', False):
            self._setup_nap_reminder(nap)
        
        # 3. 药物提醒
        medication = workplace.get('medication', {})
        meds = self._storage.get_medications()
        for med in meds:
            if med.enabled:
                self._setup_medication_reminder(med)
        
        # 4. 孕期相关
        pregnancy = self._storage.get_pregnancy_config()
        if pregnancy.enabled and pregnancy.last_period_date:
            self._setup_pregnancy_reminders(pregnancy)
            
            # 胎动记录（孕 18 周后）
            if pregnancy.current_week and pregnancy.current_week >= 18:
                fetal = workplace.get('fetal_movement', {})
                if fetal.get('enabled', False):
                    self._setup_fetal_movement_reminder(fetal)
        
        # 5. 自定义事件
        for event in self._storage.get_events():
            if event.enabled and not event.is_countdown:
                self._setup_event_reminder(event)
    
    def _setup_water_reminder(self, config: Dict):
        """设置喝水提醒"""
        interval = config.get('interval_minutes', 45)
        start_time = config.get('start_time', '09:00')
        end_time = config.get('end_time', '18:00')
        
        def water_callback():
            if is_within_time_range(start_time, end_time):
                self._trigger_reminder(
                    ReminderType.WATER,
                    "💧 喝水时间到！",
                    FALLBACK_TEMPLATES['water'],
                    ReminderPriority.NORMAL
                )
        
        self._scheduler.add_interval_job(
            job_id='water_reminder',
            func=water_callback,
            minutes=interval
        )
    
    def _setup_stand_up_reminder(self, config: Dict):
        """设置站立活动提醒"""
        interval = config.get('interval_minutes', 45)
        work_hours = config.get('work_hours', {})
        start_time = work_hours.get('start', '09:00')
        end_time = work_hours.get('end', '18:00')
        
        def stand_up_callback():
            if is_within_time_range(start_time, end_time):
                # TODO: 后续可接入 AI 生成内容
                self._trigger_reminder(
                    ReminderType.STAND_UP,
                    "💃 该起来活动啦！",
                    FALLBACK_TEMPLATES['stand_up'],
                    ReminderPriority.NORMAL
                )
        
        self._scheduler.add_interval_job(
            job_id='stand_up_reminder',
            func=stand_up_callback,
            minutes=interval
        )
    
    def _setup_eye_rest_reminder(self, config: Dict):
        """设置眼睛休息提醒"""
        interval = config.get('interval_minutes', 20)
        
        def eye_rest_callback():
            self._trigger_reminder(
                ReminderType.EYE_REST,
                "👀 眼睛休息时间！",
                FALLBACK_TEMPLATES['eye_rest'],
                ReminderPriority.NORMAL
            )
        
        self._scheduler.add_interval_job(
            job_id='eye_rest_reminder',
            func=eye_rest_callback,
            minutes=interval
        )
    
    def _setup_nutrition_reminder(self, config: Dict):
        """设置营养补充提醒"""
        snacks = config.get('snacks', [])
        
        for i, snack in enumerate(snacks):
            snack_time = snack.get('time', '10:00')
            snack_name = snack.get('name', '加餐')
            
            def nutrition_callback(name=snack_name):
                self._trigger_reminder(
                    ReminderType.NUTRITION,
                    f"🍎 {name}时间到！",
                    FALLBACK_TEMPLATES['nutrition'],
                    ReminderPriority.IMPORTANT
                )
            
            self._scheduler.add_time_job(
                job_id=f'nutrition_reminder_{i}',
                func=nutrition_callback,
                time_str=snack_time,
                day_of_week='mon-fri'  # 工作日
            )
    
    def _setup_posture_reminder(self, config: Dict):
        """设置姿势调整提醒"""
        interval = config.get('interval_minutes', 30)
        
        def posture_callback():
            self._trigger_reminder(
                ReminderType.POSTURE,
                "🪑 检查一下坐姿吧！",
                FALLBACK_TEMPLATES['posture'],
                ReminderPriority.SUGGESTED
            )
        
        self._scheduler.add_interval_job(
            job_id='posture_reminder',
            func=posture_callback,
            minutes=interval
        )
    
    def _setup_relaxation_reminder(self, config: Dict):
        """设置情绪放松提醒"""
        times = config.get('times', ['10:30', '16:00'])
        
        for i, t in enumerate(times):
            def relaxation_callback():
                self._trigger_reminder(
                    ReminderType.RELAXATION,
                    "🧘‍♀️ 放松一下，深呼吸～",
                    FALLBACK_TEMPLATES['relaxation'],
                    ReminderPriority.SUGGESTED
                )
            
            self._scheduler.add_time_job(
                job_id=f'relaxation_reminder_{i}',
                func=relaxation_callback,
                time_str=t,
                day_of_week='mon-fri'
            )
    
    def _setup_nap_reminder(self, config: Dict):
        """设置午休提醒"""
        nap_time = config.get('time', '12:30')
        
        def nap_callback():
            self._trigger_reminder(
                ReminderType.NAP,
                "😴 该午休啦！",
                FALLBACK_TEMPLATES['nap'],
                ReminderPriority.IMPORTANT
            )
        
        self._scheduler.add_time_job(
            job_id='nap_reminder',
            func=nap_callback,
            time_str=nap_time,
            day_of_week='mon-fri'
        )
    
    def _setup_medication_reminder(self, medication):
        """设置药物提醒"""
        for i, med_time in enumerate(medication.times):
            def medication_callback(med=medication):
                content = f"💊 记得吃 {med.name}！\n剂量：{med.dosage}"
                if med.notes:
                    content += f"\n备注：{med.notes}"
                
                self._trigger_reminder(
                    ReminderType.MEDICATION,
                    f"💊 吃药时间到！",
                    content,
                    ReminderPriority.URGENT
                )
            
            self._scheduler.add_time_job(
                job_id=f'medication_{medication.id}_{i}',
                func=medication_callback,
                time_str=med_time
            )
    
    def _setup_pregnancy_reminders(self, pregnancy_config):
        """设置孕期相关提醒"""
        tip_time = pregnancy_config.daily_tip_time
        
        def daily_tip_callback():
            week = pregnancy_config.current_week
            if week:
                # TODO: 后续接入 AI 生成内容
                self._trigger_reminder(
                    ReminderType.PREGNANCY_TIP,
                    f"💝 孕 {week} 周每日建议",
                    FALLBACK_TEMPLATES['daily_tips'],
                    ReminderPriority.IMPORTANT
                )
        
        self._scheduler.add_time_job(
            job_id='pregnancy_daily_tip',
            func=daily_tip_callback,
            time_str=tip_time
        )
    
    def _setup_fetal_movement_reminder(self, config: Dict):
        """设置胎动记录提醒"""
        times = config.get('times', ['09:00', '14:00', '20:00'])
        
        for i, t in enumerate(times):
            def fetal_callback():
                self._trigger_reminder(
                    ReminderType.FETAL_MOVEMENT,
                    "👶 记录胎动时间到！",
                    FALLBACK_TEMPLATES['fetal_movement'],
                    ReminderPriority.IMPORTANT
                )
            
            self._scheduler.add_time_job(
                job_id=f'fetal_movement_reminder_{i}',
                func=fetal_callback,
                time_str=t
            )
    
    def _setup_event_reminder(self, event):
        """设置自定义事件提醒"""
        if not event.remind_time:
            return
        
        if event.repeat_type == RepeatType.ONCE:
            # 一次性提醒
            self._scheduler.add_once_job(
                job_id=f'event_{event.id}',
                func=lambda e=event: self._trigger_event_reminder(e),
                run_time=event.remind_time
            )
        else:
            # 周期性提醒
            hour = event.remind_time.hour
            minute = event.remind_time.minute
            
            day_of_week = None
            if event.repeat_type == RepeatType.WORKDAYS:
                day_of_week = 'mon-fri'
            elif event.repeat_type == RepeatType.WEEKLY:
                # 使用创建时的星期几
                day_of_week = str(event.remind_time.weekday())
            
            self._scheduler.add_cron_job(
                job_id=f'event_{event.id}',
                func=lambda e=event: self._trigger_event_reminder(e),
                hour=hour,
                minute=minute,
                day_of_week=day_of_week
            )
    
    def _trigger_event_reminder(self, event):
        """触发事件提醒"""
        self._trigger_reminder(
            ReminderType.EVENT,
            event.title,
            event.description or "事件提醒",
            ReminderPriority.IMPORTANT
        )
    
    def _trigger_reminder(
        self,
        reminder_type: ReminderType,
        title: str,
        content: str,
        priority: int
    ):
        """触发提醒"""
        # 发送信号
        self.reminder_triggered.emit(
            reminder_type.value,
            title,
            content,
            priority
        )
        
        # 调用回调（如果有）
        if self._notification_callback:
            self._notification_callback(title, content, priority)
    
    def update_reminder(self, reminder_type: str, enabled: bool, config: Dict = None):
        """更新提醒配置"""
        job_prefix = f'{reminder_type}_reminder'
        
        if not enabled:
            # 禁用：移除相关任务
            for job_id in list(self._scheduler._jobs.keys()):
                if job_id.startswith(job_prefix) or job_id == job_prefix:
                    self._scheduler.remove_job(job_id)
        else:
            # 启用：重新设置
            if config:
                setup_method = getattr(self, f'_setup_{reminder_type}_reminder', None)
                if setup_method:
                    setup_method(config)
    
    def reload_all(self):
        """重新加载所有提醒"""
        self._scheduler.clear_all_jobs()
        self.load_reminders()
