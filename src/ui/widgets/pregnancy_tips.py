# -*- coding: utf-8 -*-
"""孕期建议组件"""

from datetime import date

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar
)
from PySide6.QtCore import Qt

from ...data.storage import StorageManager
from ...core.pregnancy import PregnancyCalculator
from ...utils.helpers import days_until


class PregnancyTipsWidget(QFrame):
    """孕期信息和建议卡片"""
    
    def __init__(self, storage: StorageManager, parent=None):
        super().__init__(parent)
        self._storage = storage
        self._setup_ui()
        self.refresh()
    
    def _setup_ui(self):
        """设置 UI"""
        self.setObjectName("card")
        self.setFrameStyle(QFrame.StyledPanel)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)
        
        # 标题
        header_layout = QHBoxLayout()
        
        title = QLabel("👶 孕期信息")
        title.setObjectName("sectionLabel")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self._config_btn = QPushButton("设置孕期信息")
        self._config_btn.setObjectName("secondaryButton")
        header_layout.addWidget(self._config_btn)
        
        layout.addLayout(header_layout)
        
        # 孕期信息显示区
        self._info_widget = QFrame()
        self._info_layout = QVBoxLayout(self._info_widget)
        self._info_layout.setContentsMargins(0, 0, 0, 0)
        self._info_layout.setSpacing(12)
        
        # 孕周显示
        week_layout = QHBoxLayout()
        
        self._week_label = QLabel("孕 0 周")
        self._week_label.setStyleSheet("font-size: 28px; font-weight: bold;")
        week_layout.addWidget(self._week_label)
        
        self._stage_label = QLabel("")
        self._stage_label.setStyleSheet(
            "background-color: rgba(255, 105, 180, 0.2); "
            "color: #FF69B4; padding: 4px 12px; "
            "border-radius: 12px; font-size: 12px;"
        )
        week_layout.addWidget(self._stage_label)
        
        week_layout.addStretch()
        self._info_layout.addLayout(week_layout)
        
        # 进度条
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(4)
        
        progress_label_layout = QHBoxLayout()
        self._progress_label = QLabel("孕期进度")
        progress_label_layout.addWidget(self._progress_label)
        progress_label_layout.addStretch()
        self._due_date_label = QLabel("预产期：--")
        progress_label_layout.addWidget(self._due_date_label)
        progress_layout.addLayout(progress_label_layout)
        
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 280)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setFixedHeight(12)
        progress_layout.addWidget(self._progress_bar)
        
        self._info_layout.addLayout(progress_layout)
        
        # 宝宝发育信息
        self._baby_label = QLabel("")
        self._baby_label.setStyleSheet("color: #666666; font-size: 13px;")
        self._baby_label.setWordWrap(True)
        self._info_layout.addWidget(self._baby_label)
        
        # 今日建议
        self._tips_frame = QFrame()
        self._tips_frame.setStyleSheet(
            "background-color: rgba(255, 105, 180, 0.1); "
            "border-radius: 8px; padding: 8px;"
        )
        tips_layout = QVBoxLayout(self._tips_frame)
        tips_layout.setContentsMargins(12, 8, 12, 8)
        
        tips_title = QLabel("💡 今日建议")
        tips_title.setStyleSheet("font-weight: bold; color: #FF69B4;")
        tips_layout.addWidget(tips_title)
        
        self._tips_label = QLabel("")
        self._tips_label.setStyleSheet("color: #666666; font-size: 12px;")
        self._tips_label.setWordWrap(True)
        tips_layout.addWidget(self._tips_label)
        
        self._info_layout.addWidget(self._tips_frame)
        
        layout.addWidget(self._info_widget)
        
        # 未配置提示
        self._not_configured_label = QLabel(
            "还未设置孕期信息\n点击上方按钮开始配置"
        )
        self._not_configured_label.setAlignment(Qt.AlignCenter)
        self._not_configured_label.setStyleSheet("color: #999999; padding: 40px;")
        layout.addWidget(self._not_configured_label)
    
    def refresh(self):
        """刷新显示"""
        pregnancy = self._storage.get_pregnancy_config()
        
        if not pregnancy.enabled or not pregnancy.last_period_date:
            self._info_widget.setVisible(False)
            self._not_configured_label.setVisible(True)
            self._config_btn.setText("设置孕期信息")
            return
        
        self._info_widget.setVisible(True)
        self._not_configured_label.setVisible(False)
        self._config_btn.setText("修改设置")
        
        # 计算孕期信息
        calc = PregnancyCalculator(pregnancy)
        
        # 孕周显示
        week_day = calc.current_week_day
        if week_day:
            weeks, days = week_day
            week_text = f"孕 {weeks} 周"
            if days > 0:
                week_text += f" + {days} 天"
            self._week_label.setText(week_text)
        
        # 阶段
        stage = calc.trimester_name
        if stage:
            self._stage_label.setText(stage)
            self._stage_label.setVisible(True)
        else:
            self._stage_label.setVisible(False)
        
        # 进度
        if pregnancy.last_period_date:
            days_pregnant = (date.today() - pregnancy.last_period_date).days
            self._progress_bar.setValue(min(days_pregnant, 280))
            self._progress_label.setText(f"孕期进度 {days_pregnant}/280 天")
        
        # 预产期
        due_date = calc.due_date
        if due_date:
            days_left = days_until(due_date)
            self._due_date_label.setText(
                f"预产期：{due_date.strftime('%Y-%m-%d')}（还有 {days_left} 天）"
            )
        
        # 宝宝发育信息
        baby_info = calc.get_baby_development_stage()
        if baby_info:
            self._baby_label.setText(f"🎀 {baby_info}")
            self._baby_label.setVisible(True)
        else:
            self._baby_label.setVisible(False)
        
        # 今日建议（简化版，后续接入 AI）
        week = calc.current_week or 0
        if week <= 13:
            tips = "孕早期注意休息，补充叶酸，避免剧烈运动"
        elif week <= 27:
            tips = "孕中期相对稳定，可以适当增加活动量，注意补钙"
        else:
            tips = "孕晚期注意胎动，准备待产包，保持充足休息"
        
        self._tips_label.setText(tips)
