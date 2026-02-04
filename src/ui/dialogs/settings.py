# -*- coding: utf-8 -*-
"""设置对话框"""

from datetime import date

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QPushButton, QCheckBox, QSpinBox, QTimeEdit,
    QComboBox, QGroupBox, QFormLayout, QLineEdit, QDateEdit,
    QScrollArea, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QTime, QDate

from ..theme_manager import ThemeManager
from ...data.storage import StorageManager
from ...data.models import PregnancyConfig
from ...core.reminder_engine import ReminderEngine
from ...utils.constants import AI_MODE_OPTIONS


class SettingsDialog(QDialog):
    """设置对话框"""
    
    def __init__(
        self,
        storage: StorageManager,
        theme_manager: ThemeManager,
        reminder_engine: ReminderEngine,
        parent=None
    ):
        super().__init__(parent)
        self._storage = storage
        self._theme_manager = theme_manager
        self._reminder_engine = reminder_engine
        
        self.setWindowTitle("设置")
        self.setMinimumSize(600, 500)
        self.resize(700, 600)
        
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        
        # 选项卡
        self._tab_widget = QTabWidget()
        layout.addWidget(self._tab_widget)
        
        # 通用设置
        general_tab = self._create_general_tab()
        self._tab_widget.addTab(general_tab, "⚙️ 通用")
        
        # 提醒设置
        reminder_tab = self._create_reminder_tab()
        self._tab_widget.addTab(reminder_tab, "🔔 提醒")
        
        # 职场健康
        workplace_tab = self._create_workplace_tab()
        self._tab_widget.addTab(workplace_tab, "🏢 职场健康")
        
        # 孕期设置
        pregnancy_tab = self._create_pregnancy_tab()
        self._tab_widget.addTab(pregnancy_tab, "👶 孕期")
        
        # AI 设置
        ai_tab = self._create_ai_tab()
        self._tab_widget.addTab(ai_tab, "🤖 AI 模型")
        
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
    
    def _create_general_tab(self) -> QWidget:
        """创建通用设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # 主题设置
        theme_group = QGroupBox("🎨 主题设置")
        theme_layout = QFormLayout(theme_group)
        
        self._theme_combo = QComboBox()
        for theme in self._theme_manager.get_available_themes():
            self._theme_combo.addItem(theme['name'], theme['id'])
        theme_layout.addRow("选择主题：", self._theme_combo)
        
        refresh_theme_btn = QPushButton("刷新主题")
        refresh_theme_btn.clicked.connect(self._theme_manager.refresh_theme)
        theme_layout.addRow("", refresh_theme_btn)
        
        layout.addWidget(theme_group)
        
        # 启动设置
        startup_group = QGroupBox("🚀 启动设置")
        startup_layout = QVBoxLayout(startup_group)
        
        self._autostart_check = QCheckBox("开机自动启动")
        startup_layout.addWidget(self._autostart_check)
        
        self._start_minimized_check = QCheckBox("启动时最小化到托盘")
        startup_layout.addWidget(self._start_minimized_check)
        
        layout.addWidget(startup_group)
        
        # 通知设置
        notification_group = QGroupBox("🔔 通知设置")
        notification_layout = QVBoxLayout(notification_group)
        
        self._sound_check = QCheckBox("启用提示音")
        notification_layout.addWidget(self._sound_check)
        
        self._popup_check = QCheckBox("显示桌面弹窗")
        notification_layout.addWidget(self._popup_check)
        
        layout.addWidget(notification_group)
        layout.addStretch()
        
        return widget
    
    def _create_reminder_tab(self) -> QWidget:
        """创建提醒设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # 喝水提醒
        water_group = QGroupBox("💧 喝水提醒")
        water_layout = QFormLayout(water_group)
        
        self._water_enabled_check = QCheckBox("启用喝水提醒")
        water_layout.addRow(self._water_enabled_check)
        
        self._water_interval_spin = QSpinBox()
        self._water_interval_spin.setRange(15, 120)
        self._water_interval_spin.setSuffix(" 分钟")
        water_layout.addRow("提醒间隔：", self._water_interval_spin)
        
        time_layout = QHBoxLayout()
        self._water_start_time = QTimeEdit()
        self._water_start_time.setDisplayFormat("HH:mm")
        time_layout.addWidget(self._water_start_time)
        time_layout.addWidget(QLabel("至"))
        self._water_end_time = QTimeEdit()
        self._water_end_time.setDisplayFormat("HH:mm")
        time_layout.addWidget(self._water_end_time)
        time_layout.addStretch()
        water_layout.addRow("提醒时段：", time_layout)
        
        layout.addWidget(water_group)
        layout.addStretch()
        
        return widget
    
    def _create_workplace_tab(self) -> QWidget:
        """创建职场健康标签页"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        
        # 站立活动
        stand_group = QGroupBox("🚶‍♀️ 站立活动提醒")
        stand_layout = QFormLayout(stand_group)
        
        self._stand_enabled_check = QCheckBox("启用")
        stand_layout.addRow(self._stand_enabled_check)
        
        self._stand_interval_spin = QSpinBox()
        self._stand_interval_spin.setRange(15, 120)
        self._stand_interval_spin.setSuffix(" 分钟")
        stand_layout.addRow("间隔：", self._stand_interval_spin)
        
        layout.addWidget(stand_group)
        
        # 眼睛休息
        eye_group = QGroupBox("👀 眼睛休息提醒")
        eye_layout = QFormLayout(eye_group)
        
        self._eye_enabled_check = QCheckBox("启用")
        eye_layout.addRow(self._eye_enabled_check)
        
        self._eye_interval_spin = QSpinBox()
        self._eye_interval_spin.setRange(10, 60)
        self._eye_interval_spin.setSuffix(" 分钟")
        eye_layout.addRow("间隔：", self._eye_interval_spin)
        
        layout.addWidget(eye_group)
        
        # 姿势调整
        posture_group = QGroupBox("🪑 姿势调整提醒")
        posture_layout = QFormLayout(posture_group)
        
        self._posture_enabled_check = QCheckBox("启用")
        posture_layout.addRow(self._posture_enabled_check)
        
        self._posture_interval_spin = QSpinBox()
        self._posture_interval_spin.setRange(15, 60)
        self._posture_interval_spin.setSuffix(" 分钟")
        posture_layout.addRow("间隔：", self._posture_interval_spin)
        
        layout.addWidget(posture_group)
        
        # 午休提醒
        nap_group = QGroupBox("😴 午休提醒")
        nap_layout = QFormLayout(nap_group)
        
        self._nap_enabled_check = QCheckBox("启用")
        nap_layout.addRow(self._nap_enabled_check)
        
        self._nap_time_edit = QTimeEdit()
        self._nap_time_edit.setDisplayFormat("HH:mm")
        nap_layout.addRow("提醒时间：", self._nap_time_edit)
        
        layout.addWidget(nap_group)
        
        layout.addStretch()
        scroll.setWidget(widget)
        
        return scroll
    
    def _create_pregnancy_tab(self) -> QWidget:
        """创建孕期设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # 孕期配置
        pregnancy_group = QGroupBox("👶 孕期配置")
        pregnancy_layout = QFormLayout(pregnancy_group)
        
        self._pregnancy_enabled_check = QCheckBox("启用孕期助手")
        pregnancy_layout.addRow(self._pregnancy_enabled_check)
        
        self._last_period_date = QDateEdit()
        self._last_period_date.setCalendarPopup(True)
        self._last_period_date.setDisplayFormat("yyyy-MM-dd")
        pregnancy_layout.addRow("末次月经日期：", self._last_period_date)
        
        self._daily_tip_time = QTimeEdit()
        self._daily_tip_time.setDisplayFormat("HH:mm")
        pregnancy_layout.addRow("每日建议推送时间：", self._daily_tip_time)
        
        layout.addWidget(pregnancy_group)
        
        # 胎动记录
        fetal_group = QGroupBox("👶 胎动记录提醒")
        fetal_layout = QFormLayout(fetal_group)
        
        self._fetal_enabled_check = QCheckBox("启用（孕18周后自动开启）")
        fetal_layout.addRow(self._fetal_enabled_check)
        
        fetal_info = QLabel("建议每天记录三次胎动：上午、下午、晚上")
        fetal_info.setStyleSheet("color: #666666; font-size: 11px;")
        fetal_layout.addRow(fetal_info)
        
        layout.addWidget(fetal_group)
        layout.addStretch()
        
        return widget
    
    def _create_ai_tab(self) -> QWidget:
        """创建 AI 模型设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # AI 模式选择
        mode_group = QGroupBox("🤖 AI 使用模式")
        mode_layout = QVBoxLayout(mode_group)
        
        self._ai_mode_combo = QComboBox()
        for mode_id, mode_config in AI_MODE_OPTIONS.items():
            self._ai_mode_combo.addItem(
                f"{mode_config['name']} - {mode_config['desc']}",
                mode_id
            )
        mode_layout.addWidget(self._ai_mode_combo)
        
        mode_info = QLabel(
            "💡 智能模式：重要提醒使用 AI 生成，平衡效果和成本\n"
            "💡 完全 AI：所有提醒都使用 AI 生成，效果最佳\n"
            "💡 节约模式：仅每日建议使用 AI，最节省\n"
            "💡 关闭 AI：全部使用固定模板"
        )
        mode_info.setStyleSheet("color: #666666; font-size: 11px;")
        mode_info.setWordWrap(True)
        mode_layout.addWidget(mode_info)
        
        layout.addWidget(mode_group)
        
        # API Key 配置
        key_group = QGroupBox("🔑 API Key 配置")
        key_layout = QFormLayout(key_group)
        
        self._deepseek_key = QLineEdit()
        self._deepseek_key.setPlaceholderText("sk-xxxxxxxx")
        self._deepseek_key.setEchoMode(QLineEdit.Password)
        key_layout.addRow("DeepSeek API Key：", self._deepseek_key)
        
        self._glm4_key = QLineEdit()
        self._glm4_key.setPlaceholderText("id.secret 格式")
        self._glm4_key.setEchoMode(QLineEdit.Password)
        key_layout.addRow("智谱 GLM-4 API Key：", self._glm4_key)
        
        check_btn = QPushButton("检查 Key 状态")
        check_btn.clicked.connect(self._on_check_keys)
        key_layout.addRow("", check_btn)
        
        self._key_status_label = QLabel("")
        self._key_status_label.setWordWrap(True)
        key_layout.addRow("状态：", self._key_status_label)
        
        layout.addWidget(key_group)
        layout.addStretch()
        
        return widget
    
    def _load_settings(self):
        """加载当前设置"""
        config = self._storage.config
        
        # 通用设置
        current_theme = self._theme_manager.get_current_theme()
        for i in range(self._theme_combo.count()):
            if self._theme_combo.itemData(i) == current_theme:
                self._theme_combo.setCurrentIndex(i)
                break
        
        self._autostart_check.setChecked(config.get('autostart', False))
        
        notifications = config.get('notifications', {})
        self._sound_check.setChecked(notifications.get('sound', True))
        self._popup_check.setChecked(notifications.get('popup', True))
        
        # 喝水提醒
        water = config.get('water_reminder', {})
        self._water_enabled_check.setChecked(water.get('enabled', True))
        self._water_interval_spin.setValue(water.get('interval_minutes', 45))
        
        start_time = water.get('start_time', '09:00')
        end_time = water.get('end_time', '18:00')
        self._water_start_time.setTime(QTime.fromString(start_time, "HH:mm"))
        self._water_end_time.setTime(QTime.fromString(end_time, "HH:mm"))
        
        # 职场健康
        workplace = config.get('workplace_reminders', {})
        
        stand = workplace.get('stand_up', {})
        self._stand_enabled_check.setChecked(stand.get('enabled', True))
        self._stand_interval_spin.setValue(stand.get('interval_minutes', 45))
        
        eye = workplace.get('eye_rest', {})
        self._eye_enabled_check.setChecked(eye.get('enabled', True))
        self._eye_interval_spin.setValue(eye.get('interval_minutes', 20))
        
        posture = workplace.get('posture', {})
        self._posture_enabled_check.setChecked(posture.get('enabled', True))
        self._posture_interval_spin.setValue(posture.get('interval_minutes', 30))
        
        nap = workplace.get('nap', {})
        self._nap_enabled_check.setChecked(nap.get('enabled', True))
        nap_time = nap.get('time', '12:30')
        self._nap_time_edit.setTime(QTime.fromString(nap_time, "HH:mm"))
        
        # 孕期设置
        pregnancy = self._storage.get_pregnancy_config()
        self._pregnancy_enabled_check.setChecked(pregnancy.enabled)
        if pregnancy.last_period_date:
            self._last_period_date.setDate(QDate(
                pregnancy.last_period_date.year,
                pregnancy.last_period_date.month,
                pregnancy.last_period_date.day
            ))
        tip_time = pregnancy.daily_tip_time or '09:00'
        self._daily_tip_time.setTime(QTime.fromString(tip_time, "HH:mm"))
        
        fetal = workplace.get('fetal_movement', {})
        self._fetal_enabled_check.setChecked(fetal.get('enabled', False))
        
        # AI 设置
        ai_mode = config.get('ai_mode', 'smart')
        for i in range(self._ai_mode_combo.count()):
            if self._ai_mode_combo.itemData(i) == ai_mode:
                self._ai_mode_combo.setCurrentIndex(i)
                break
    
    def _on_save(self):
        """保存设置"""
        # 通用设置
        theme_id = self._theme_combo.currentData()
        if theme_id != self._theme_manager.get_current_theme():
            from PySide6.QtWidgets import QApplication
            self._theme_manager.apply_theme(QApplication.instance(), theme_id)
        
        self._storage.set_config('autostart', self._autostart_check.isChecked())
        self._storage.set_config('notifications.sound', self._sound_check.isChecked())
        self._storage.set_config('notifications.popup', self._popup_check.isChecked())
        
        # 喝水提醒
        self._storage.set_config('water_reminder.enabled', self._water_enabled_check.isChecked())
        self._storage.set_config('water_reminder.interval_minutes', self._water_interval_spin.value())
        self._storage.set_config('water_reminder.start_time', self._water_start_time.time().toString("HH:mm"))
        self._storage.set_config('water_reminder.end_time', self._water_end_time.time().toString("HH:mm"))
        
        # 职场健康
        self._storage.set_config('workplace_reminders.stand_up.enabled', self._stand_enabled_check.isChecked())
        self._storage.set_config('workplace_reminders.stand_up.interval_minutes', self._stand_interval_spin.value())
        
        self._storage.set_config('workplace_reminders.eye_rest.enabled', self._eye_enabled_check.isChecked())
        self._storage.set_config('workplace_reminders.eye_rest.interval_minutes', self._eye_interval_spin.value())
        
        self._storage.set_config('workplace_reminders.posture.enabled', self._posture_enabled_check.isChecked())
        self._storage.set_config('workplace_reminders.posture.interval_minutes', self._posture_interval_spin.value())
        
        self._storage.set_config('workplace_reminders.nap.enabled', self._nap_enabled_check.isChecked())
        self._storage.set_config('workplace_reminders.nap.time', self._nap_time_edit.time().toString("HH:mm"))
        
        self._storage.set_config('workplace_reminders.fetal_movement.enabled', self._fetal_enabled_check.isChecked())
        
        # 孕期设置
        qdate = self._last_period_date.date()
        last_period = date(qdate.year(), qdate.month(), qdate.day())
        
        pregnancy_config = PregnancyConfig(
            enabled=self._pregnancy_enabled_check.isChecked(),
            last_period_date=last_period if self._pregnancy_enabled_check.isChecked() else None,
            daily_tip_time=self._daily_tip_time.time().toString("HH:mm")
        )
        self._storage.set_pregnancy_config(pregnancy_config)
        
        # AI 设置
        self._storage.set_config('ai_mode', self._ai_mode_combo.currentData())
        
        # 重新加载提醒
        self._reminder_engine.reload_all()
        
        self.accept()
    
    def _on_check_keys(self):
        """检查 API Key 状态"""
        # TODO: 实现 Key 检查
        self._key_status_label.setText("检查中...")
        QMessageBox.information(self, "提示", "API Key 检查功能即将上线")
    
    def setCurrentTab(self, index: int):
        """设置当前标签页"""
        if 0 <= index < self._tab_widget.count():
            self._tab_widget.setCurrentIndex(index)
