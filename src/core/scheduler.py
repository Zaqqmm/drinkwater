# -*- coding: utf-8 -*-
"""定时任务调度器封装"""

from typing import Callable, Optional, Dict, Any, List
from datetime import datetime, timedelta
from apscheduler.schedulers.qt import QtScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.memory import MemoryJobStore


class SchedulerManager:
    """调度器管理器 - 封装 APScheduler"""
    
    def __init__(self):
        self._scheduler = QtScheduler()
        self._scheduler.add_jobstore(MemoryJobStore(), 'default')
        self._jobs: Dict[str, str] = {}  # job_id -> apscheduler_job_id
    
    def start(self):
        """启动调度器"""
        if not self._scheduler.running:
            self._scheduler.start()
    
    def shutdown(self):
        """关闭调度器"""
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)
    
    def add_interval_job(
        self,
        job_id: str,
        func: Callable,
        minutes: int = 0,
        hours: int = 0,
        seconds: int = 0,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        **kwargs
    ) -> bool:
        """
        添加间隔触发任务
        
        Args:
            job_id: 任务唯一标识
            func: 要执行的函数
            minutes: 间隔分钟数
            hours: 间隔小时数
            seconds: 间隔秒数
            start_time: 开始时间 "HH:MM"
            end_time: 结束时间 "HH:MM"
            **kwargs: 传递给 func 的参数
        """
        # 如果已存在同 ID 的任务，先移除
        self.remove_job(job_id)
        
        # 计算间隔
        interval_seconds = seconds + minutes * 60 + hours * 3600
        if interval_seconds <= 0:
            return False
        
        try:
            trigger = IntervalTrigger(
                seconds=interval_seconds,
                start_date=datetime.now()
            )
            
            job = self._scheduler.add_job(
                func,
                trigger=trigger,
                id=job_id,
                kwargs=kwargs,
                replace_existing=True,
                misfire_grace_time=60
            )
            
            self._jobs[job_id] = job.id
            return True
            
        except Exception as e:
            print(f"添加间隔任务失败 {job_id}: {e}")
            return False
    
    def add_cron_job(
        self,
        job_id: str,
        func: Callable,
        hour: int = None,
        minute: int = None,
        second: int = 0,
        day_of_week: str = None,  # 'mon-fri', '0-4', 等
        **kwargs
    ) -> bool:
        """
        添加定时触发任务（Cron 风格）
        
        Args:
            job_id: 任务唯一标识
            func: 要执行的函数
            hour: 小时 (0-23)
            minute: 分钟 (0-59)
            second: 秒 (0-59)
            day_of_week: 星期几，如 'mon-fri' 表示工作日
            **kwargs: 传递给 func 的参数
        """
        self.remove_job(job_id)
        
        try:
            trigger = CronTrigger(
                hour=hour,
                minute=minute,
                second=second,
                day_of_week=day_of_week
            )
            
            job = self._scheduler.add_job(
                func,
                trigger=trigger,
                id=job_id,
                kwargs=kwargs,
                replace_existing=True,
                misfire_grace_time=60
            )
            
            self._jobs[job_id] = job.id
            return True
            
        except Exception as e:
            print(f"添加定时任务失败 {job_id}: {e}")
            return False
    
    def add_time_job(
        self,
        job_id: str,
        func: Callable,
        time_str: str,
        day_of_week: str = None,
        **kwargs
    ) -> bool:
        """
        添加每日定时任务（简化版）
        
        Args:
            job_id: 任务唯一标识
            func: 要执行的函数
            time_str: 时间字符串 "HH:MM"
            day_of_week: 星期几限制
            **kwargs: 传递给 func 的参数
        """
        try:
            hour, minute = map(int, time_str.split(':'))
            return self.add_cron_job(
                job_id=job_id,
                func=func,
                hour=hour,
                minute=minute,
                day_of_week=day_of_week,
                **kwargs
            )
        except ValueError:
            print(f"无效的时间格式: {time_str}")
            return False
    
    def add_once_job(
        self,
        job_id: str,
        func: Callable,
        run_time: datetime,
        **kwargs
    ) -> bool:
        """
        添加一次性任务
        
        Args:
            job_id: 任务唯一标识
            func: 要执行的函数
            run_time: 执行时间
            **kwargs: 传递给 func 的参数
        """
        self.remove_job(job_id)
        
        # 如果执行时间已过，跳过
        if run_time <= datetime.now():
            return False
        
        try:
            trigger = DateTrigger(run_date=run_time)
            
            job = self._scheduler.add_job(
                func,
                trigger=trigger,
                id=job_id,
                kwargs=kwargs,
                replace_existing=True
            )
            
            self._jobs[job_id] = job.id
            return True
            
        except Exception as e:
            print(f"添加一次性任务失败 {job_id}: {e}")
            return False
    
    def remove_job(self, job_id: str) -> bool:
        """移除任务"""
        if job_id in self._jobs:
            try:
                self._scheduler.remove_job(job_id)
            except Exception:
                pass
            del self._jobs[job_id]
            return True
        return False
    
    def pause_job(self, job_id: str) -> bool:
        """暂停任务"""
        if job_id in self._jobs:
            try:
                self._scheduler.pause_job(job_id)
                return True
            except Exception:
                pass
        return False
    
    def resume_job(self, job_id: str) -> bool:
        """恢复任务"""
        if job_id in self._jobs:
            try:
                self._scheduler.resume_job(job_id)
                return True
            except Exception:
                pass
        return False
    
    def get_jobs(self) -> List[Dict[str, Any]]:
        """获取所有任务信息"""
        jobs = []
        for job_id in self._jobs:
            try:
                job = self._scheduler.get_job(job_id)
                if job:
                    jobs.append({
                        'id': job_id,
                        'next_run': job.next_run_time,
                        'pending': job.pending
                    })
            except Exception:
                pass
        return jobs
    
    def job_exists(self, job_id: str) -> bool:
        """检查任务是否存在"""
        return job_id in self._jobs
    
    def clear_all_jobs(self):
        """清除所有任务"""
        for job_id in list(self._jobs.keys()):
            self.remove_job(job_id)
