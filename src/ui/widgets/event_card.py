# -*- coding: utf-8 -*-
"""事件卡片组件"""

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Signal

from ...data.models import Event, RepeatType


class EventCard(QFrame):
    """事件卡片"""
    
    edit_clicked = Signal(object)  # Event
    delete_clicked = Signal(object)  # Event
    
    def __init__(self, event: Event, parent=None):
        super().__init__(parent)
        self._event = event
        self._setup_ui()
    
    def _setup_ui(self):
        """设置 UI"""
        self.setObjectName("card")
        self.setFrameStyle(QFrame.StyledPanel)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        
        # 左侧内容
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)
        
        # 标题
        title_layout = QHBoxLayout()
        
        title_label = QLabel(self._event.title)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        title_layout.addWidget(title_label)
        
        # 重复类型标签
        if self._event.repeat_type != RepeatType.ONCE:
            repeat_text = self._get_repeat_text()
            repeat_label = QLabel(repeat_text)
            repeat_label.setStyleSheet(
                "background-color: rgba(0,0,0,0.1); "
                "padding: 2px 8px; border-radius: 4px; font-size: 11px;"
            )
            title_layout.addWidget(repeat_label)
        
        title_layout.addStretch()
        content_layout.addLayout(title_layout)
        
        # 描述
        if self._event.description:
            desc_label = QLabel(self._event.description)
            desc_label.setStyleSheet("color: #666666; font-size: 12px;")
            desc_label.setWordWrap(True)
            content_layout.addWidget(desc_label)
        
        # 时间
        if self._event.remind_time:
            time_text = self._event.remind_time.strftime("%H:%M")
            time_label = QLabel(f"⏰ {time_text}")
            time_label.setStyleSheet("color: #888888; font-size: 11px;")
            content_layout.addWidget(time_label)
        
        layout.addLayout(content_layout, 1)
        
        # 右侧按钮
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(8)
        
        edit_btn = QPushButton("编辑")
        edit_btn.setFixedWidth(60)
        edit_btn.setObjectName("secondaryButton")
        edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self._event))
        btn_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("删除")
        delete_btn.setFixedWidth(60)
        delete_btn.setStyleSheet(
            "QPushButton { background-color: #FF6B6B; color: white; }"
            "QPushButton:hover { background-color: #FF5252; }"
        )
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self._event))
        btn_layout.addWidget(delete_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
    
    def _get_repeat_text(self) -> str:
        """获取重复类型文本"""
        repeat_map = {
            RepeatType.DAILY: "每天",
            RepeatType.WEEKLY: "每周",
            RepeatType.MONTHLY: "每月",
            RepeatType.WORKDAYS: "工作日",
        }
        return repeat_map.get(self._event.repeat_type, "")
