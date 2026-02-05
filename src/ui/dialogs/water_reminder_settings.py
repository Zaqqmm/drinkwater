# -*- coding: utf-8 -*-
"""喝水提醒设置对话框"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QCheckBox, QSpinBox, QTimeEdit,
    QGroupBox
)
from PySide6.QtCore import Qt, QTime

from ...data.storage import StorageManager
from ...core.reminder_engine import ReminderEngine


class WaterReminderSettingsDialog(QDialog):
    """喝水提醒设置对话框"""
    
    def __init__(
        self,
        storage: StorageManager,
        reminder_engine: ReminderEngine,
        parent=None
    ):
        super().__init__(parent)
        self._storage = storage
        self._reminder_engine = reminder_engine
        
        self.setWindowTitle("喝水提醒设置")
        self.setMinimumWidth(400)
        
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # 提醒设置组
        reminder_group = QGroupBox("💧 喝水提醒")
        reminder_layout = QFormLayout(reminder_group)
        
        # 启用提醒
        self._enabled_check = QCheckBox("启用喝水提醒")
        reminder_layout.addRow(self._enabled_check)
        
        # 提醒间隔
        self._interval_spin = QSpinBox()
        self._interval_spin.setRange(15, 120)
        self._interval_spin.setSuffix(" 分钟")
        reminder_layout.addRow("提醒间隔：", self._interval_spin)
        
        # 提醒时段
        time_layout = QHBoxLayout()
        self._start_time = QTimeEdit()
        self._start_time.setDisplayFormat("HH:mm")
        time_layout.addWidget(self._start_time)
        time_layout.addWidget(QLabel("至"))
        self._end_time = QTimeEdit()
        self._end_time.setDisplayFormat("HH:mm")
        time_layout.addWidget(self._end_time)
        time_layout.addStretch()
        reminder_layout.addRow("提醒时段：", time_layout)
        
        layout.addWidget(reminder_group)
        
        # 目标设置组
        target_group = QGroupBox("🎯 每日目标")
        target_layout = QFormLayout(target_group)
        
        # 每日目标饮水量
        self._daily_target_spin = QSpinBox()
        self._daily_target_spin.setRange(500, 5000)
        self._daily_target_spin.setSingleStep(100)
        self._daily_target_spin.setSuffix(" ml")
        target_layout.addRow("每日目标：", self._daily_target_spin)
        
        # 提示信息
        tip_label = QLabel("💡 建议每天饮水 1500-2000ml，根据个人情况调整")
        tip_label.setStyleSheet("color: #666666; font-size: 11px;")
        tip_label.setWordWrap(True)
        target_layout.addRow(tip_label)
        
        layout.addWidget(target_group)
        
        layout.addStretch()
        
        # 底部按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def _load_settings(self):
        """加载当前设置"""
        config = self._storage.config
        
        # 喝水提醒设置
        water = config.get('water_reminder', {})
        self._enabled_check.setChecked(water.get('enabled', True))
        self._interval_spin.setValue(water.get('interval_minutes', 45))
        
        start_time = water.get('start_time', '09:00')
        end_time = water.get('end_time', '18:00')
        self._start_time.setTime(QTime.fromString(start_time, "HH:mm"))
        self._end_time.setTime(QTime.fromString(end_time, "HH:mm"))
        
        # 每日目标
        self._daily_target_spin.setValue(water.get('daily_target', 1800))
    
    def _on_save(self):
        """保存设置"""
        # 一次性更新所有喝水提醒设置
        water_config = {
            'enabled': self._enabled_check.isChecked(),
            'interval_minutes': self._interval_spin.value(),
            'start_time': self._start_time.time().toString("HH:mm"),
            'end_time': self._end_time.time().toString("HH:mm"),
            'daily_target': self._daily_target_spin.value()
        }
        
        # 更新配置（只保存一次）
        self._storage.config['water_reminder'] = water_config
        self._storage.save_config()
        
        # 重新加载提醒
        self._reminder_engine.reload_all()
        
        self.accept()
    
    def get_daily_target(self) -> int:
        """获取每日目标饮水量"""
        return self._daily_target_spin.value()
