# -*- coding: utf-8 -*-
"""倒计时组件"""

from datetime import date

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Signal, Qt

from ...utils.helpers import days_until


class CountdownWidget(QFrame):
    """倒计时卡片"""
    
    edit_clicked = Signal()
    delete_clicked = Signal()
    
    def __init__(
        self,
        title: str,
        target_date: date,
        description: str = "",
        parent=None
    ):
        super().__init__(parent)
        self._title = title
        self._target_date = target_date
        self._description = description
        self._setup_ui()
    
    def _setup_ui(self):
        """设置 UI"""
        self.setObjectName("card")
        self.setFrameStyle(QFrame.StyledPanel)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        
        # 左侧：天数显示
        days = days_until(self._target_date)
        
        days_frame = QFrame()
        days_layout = QVBoxLayout(days_frame)
        days_layout.setAlignment(Qt.AlignCenter)
        days_layout.setSpacing(0)
        
        if days >= 0:
            days_text = str(days)
            days_label_text = "天"
        else:
            days_text = str(abs(days))
            days_label_text = "天前"
        
        days_number = QLabel(days_text)
        days_number.setStyleSheet(
            f"font-size: 36px; font-weight: bold; "
            f"color: {'#FF69B4' if days >= 0 else '#999999'};"
        )
        days_number.setAlignment(Qt.AlignCenter)
        days_layout.addWidget(days_number)
        
        days_unit = QLabel(days_label_text)
        days_unit.setStyleSheet("font-size: 12px; color: #666666;")
        days_unit.setAlignment(Qt.AlignCenter)
        days_layout.addWidget(days_unit)
        
        layout.addWidget(days_frame)
        
        # 中间：标题和描述
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)
        
        title_label = QLabel(self._title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        content_layout.addWidget(title_label)
        
        if self._description:
            desc_label = QLabel(self._description)
            desc_label.setStyleSheet("color: #666666; font-size: 12px;")
            desc_label.setWordWrap(True)
            content_layout.addWidget(desc_label)
        
        # 目标日期
        date_label = QLabel(f"📅 {self._target_date.strftime('%Y年%m月%d日')}")
        date_label.setStyleSheet("color: #888888; font-size: 11px;")
        content_layout.addWidget(date_label)
        
        content_layout.addStretch()
        layout.addLayout(content_layout, 1)
        
        # 右侧：状态指示
        if days <= 7 and days >= 0:
            # 临近提醒
            alert_label = QLabel("⚠️ 临近")
            alert_label.setStyleSheet(
                "background-color: #FFD700; color: #333; "
                "padding: 4px 12px; border-radius: 12px; font-size: 12px;"
            )
            layout.addWidget(alert_label, alignment=Qt.AlignTop)
        elif days < 0:
            # 已过期
            expired_label = QLabel("已过")
            expired_label.setStyleSheet(
                "background-color: #CCCCCC; color: #666; "
                "padding: 4px 12px; border-radius: 12px; font-size: 12px;"
            )
            layout.addWidget(expired_label, alignment=Qt.AlignTop)
