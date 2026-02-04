# -*- coding: utf-8 -*-
"""添加/编辑事件对话框"""

from datetime import datetime, date

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit,
    QCheckBox, QComboBox, QDateEdit, QTimeEdit,
    QGroupBox
)
from PySide6.QtCore import QDate, QTime

from ...data.models import Event, RepeatType
from ...utils.helpers import generate_unique_id


class AddEventDialog(QDialog):
    """添加/编辑事件对话框"""
    
    def __init__(self, parent=None, event: Event = None, is_countdown: bool = False):
        super().__init__(parent)
        
        self._event = event
        self._is_countdown = is_countdown or (event and event.is_countdown)
        self._is_edit = event is not None
        
        title = "编辑事件" if self._is_edit else ("添加倒计时" if self._is_countdown else "添加事件")
        self.setWindowTitle(title)
        self.setMinimumWidth(450)
        
        self._setup_ui()
        
        if self._event:
            self._load_event()
    
    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # 基本信息
        basic_group = QGroupBox("基本信息")
        basic_layout = QFormLayout(basic_group)
        
        self._title_edit = QLineEdit()
        self._title_edit.setPlaceholderText("输入事件标题")
        basic_layout.addRow("标题：", self._title_edit)
        
        self._desc_edit = QTextEdit()
        self._desc_edit.setPlaceholderText("输入事件描述（可选）")
        self._desc_edit.setMaximumHeight(80)
        basic_layout.addRow("描述：", self._desc_edit)
        
        layout.addWidget(basic_group)
        
        if self._is_countdown:
            # 倒计时特有设置
            countdown_group = QGroupBox("倒计时设置")
            countdown_layout = QFormLayout(countdown_group)
            
            self._target_date_edit = QDateEdit()
            self._target_date_edit.setCalendarPopup(True)
            self._target_date_edit.setDate(QDate.currentDate().addDays(30))
            self._target_date_edit.setDisplayFormat("yyyy-MM-dd")
            countdown_layout.addRow("目标日期：", self._target_date_edit)
            
            layout.addWidget(countdown_group)
        else:
            # 普通事件提醒设置
            remind_group = QGroupBox("提醒设置")
            remind_layout = QFormLayout(remind_group)
            
            time_layout = QHBoxLayout()
            self._remind_time_edit = QTimeEdit()
            self._remind_time_edit.setDisplayFormat("HH:mm")
            self._remind_time_edit.setTime(QTime(9, 0))
            time_layout.addWidget(self._remind_time_edit)
            time_layout.addStretch()
            remind_layout.addRow("提醒时间：", time_layout)
            
            self._repeat_combo = QComboBox()
            self._repeat_combo.addItem("一次性", RepeatType.ONCE.value)
            self._repeat_combo.addItem("每天", RepeatType.DAILY.value)
            self._repeat_combo.addItem("工作日", RepeatType.WORKDAYS.value)
            self._repeat_combo.addItem("每周", RepeatType.WEEKLY.value)
            self._repeat_combo.addItem("每月", RepeatType.MONTHLY.value)
            remind_layout.addRow("重复：", self._repeat_combo)
            
            layout.addWidget(remind_group)
        
        # 启用状态
        self._enabled_check = QCheckBox("启用此事件")
        self._enabled_check.setChecked(True)
        layout.addWidget(self._enabled_check)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("保存" if self._is_edit else "添加")
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def _load_event(self):
        """加载事件数据"""
        if not self._event:
            return
        
        self._title_edit.setText(self._event.title)
        self._desc_edit.setPlainText(self._event.description)
        self._enabled_check.setChecked(self._event.enabled)
        
        if self._is_countdown:
            if self._event.target_date:
                self._target_date_edit.setDate(QDate(
                    self._event.target_date.year,
                    self._event.target_date.month,
                    self._event.target_date.day
                ))
        else:
            if self._event.remind_time:
                self._remind_time_edit.setTime(QTime(
                    self._event.remind_time.hour,
                    self._event.remind_time.minute
                ))
            
            for i in range(self._repeat_combo.count()):
                if self._repeat_combo.itemData(i) == self._event.repeat_type.value:
                    self._repeat_combo.setCurrentIndex(i)
                    break
    
    def _on_save(self):
        """保存事件"""
        title = self._title_edit.text().strip()
        if not title:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "提示", "请输入事件标题")
            return
        
        self.accept()
    
    def get_event(self) -> Event:
        """获取事件对象"""
        event_id = self._event.id if self._event else generate_unique_id()
        
        if self._is_countdown:
            qdate = self._target_date_edit.date()
            target_date = date(qdate.year(), qdate.month(), qdate.day())
            
            return Event(
                id=event_id,
                title=self._title_edit.text().strip(),
                description=self._desc_edit.toPlainText().strip(),
                is_countdown=True,
                target_date=target_date,
                enabled=self._enabled_check.isChecked()
            )
        else:
            qtime = self._remind_time_edit.time()
            now = datetime.now()
            remind_time = datetime(
                now.year, now.month, now.day,
                qtime.hour(), qtime.minute()
            )
            
            repeat_value = self._repeat_combo.currentData()
            repeat_type = RepeatType(repeat_value)
            
            return Event(
                id=event_id,
                title=self._title_edit.text().strip(),
                description=self._desc_edit.toPlainText().strip(),
                remind_time=remind_time,
                repeat_type=repeat_type,
                is_countdown=False,
                enabled=self._enabled_check.isChecked()
            )
