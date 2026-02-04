# -*- coding: utf-8 -*-
"""主窗口"""

from datetime import date, datetime
from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget, QFrame, QScrollArea,
    QMessageBox, QSystemTrayIcon
)
from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QCloseEvent, QIcon

from .theme_manager import ThemeManager
from .icon_manager import icon_manager
from .widgets.event_card import EventCard
from .widgets.countdown import CountdownWidget
from .widgets.pregnancy_tips import PregnancyTipsWidget
from .dialogs.settings import SettingsDialog
from .dialogs.add_event import AddEventDialog
from ..data.storage import StorageManager
from ..core.reminder_engine import ReminderEngine
from ..utils.constants import APP_NAME, APP_VERSION


class MainWindow(QMainWindow):
    """应用主窗口"""
    
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
        
        self._setup_ui()
        self._connect_signals()
        self._load_data()
        
        # 更新计时器（每分钟刷新）
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh_ui)
        self._refresh_timer.start(60000)  # 60 秒
    
    def _setup_ui(self):
        """设置 UI"""
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(900, 700)
        self.resize(1000, 750)
        
        # 设置窗口图标
        icon = self._theme_manager.get_icon('app')
        if icon:
            self.setWindowIcon(icon)
        
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)
        
        # 顶部标题栏
        header = self._create_header()
        main_layout.addWidget(header)
        
        # 主内容区（选项卡）
        self._tab_widget = QTabWidget()
        main_layout.addWidget(self._tab_widget)
        
        # 今日概览标签页
        today_tab = self._create_today_tab()
        self._tab_widget.addTab(today_tab, "📅 今日概览")
        
        # 倒计时标签页
        countdown_tab = self._create_countdown_tab()
        self._tab_widget.addTab(countdown_tab, "⏰ 重要倒计时")
        
        # 孕期助手标签页
        pregnancy_tab = self._create_pregnancy_tab()
        self._tab_widget.addTab(pregnancy_tab, "👶 孕期助手")
        
        # 饮食记录标签页
        diet_tab = self._create_diet_tab()
        self._tab_widget.addTab(diet_tab, "🍽️ 饮食记录")
    
    def _create_header(self) -> QWidget:
        """创建顶部标题栏"""
        header = QFrame()
        header.setObjectName("header")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题
        title_label = QLabel(f"💧 {APP_NAME}")
        title_label.setObjectName("titleLabel")
        layout.addWidget(title_label)
        
        # 状态信息
        self._status_label = QLabel()
        self._status_label.setObjectName("statusLabel")
        layout.addWidget(self._status_label)
        
        layout.addStretch()
        
        # 操作按钮
        add_event_btn = QPushButton("➕ 添加事件")
        add_event_btn.clicked.connect(self._on_add_event)
        layout.addWidget(add_event_btn)
        
        settings_btn = QPushButton("⚙️ 设置")
        settings_btn.setObjectName("secondaryButton")
        settings_btn.clicked.connect(self._on_settings)
        layout.addWidget(settings_btn)
        
        return header
    
    def _create_today_tab(self) -> QWidget:
        """创建今日概览标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # 今日提醒统计
        stats_frame = QFrame()
        stats_frame.setObjectName("card")
        stats_layout = QHBoxLayout(stats_frame)
        
        self._today_reminder_label = QLabel("今日提醒：加载中...")
        stats_layout.addWidget(self._today_reminder_label)
        
        stats_layout.addStretch()
        
        self._water_count_label = QLabel("💧 已喝水：0 次")
        stats_layout.addWidget(self._water_count_label)
        
        layout.addWidget(stats_frame)
        
        # 事件列表
        events_label = QLabel("📋 今日事件")
        events_label.setObjectName("sectionLabel")
        layout.addWidget(events_label)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        self._events_container = QWidget()
        self._events_layout = QVBoxLayout(self._events_container)
        self._events_layout.setAlignment(Qt.AlignTop)
        self._events_layout.setSpacing(12)
        
        scroll_area.setWidget(self._events_container)
        layout.addWidget(scroll_area)
        
        return widget
    
    def _create_countdown_tab(self) -> QWidget:
        """创建倒计时标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # 说明
        info_label = QLabel("🎯 重要事件倒计时，不错过任何重要时刻")
        layout.addWidget(info_label)
        
        # 添加按钮
        add_btn = QPushButton("➕ 添加倒计时")
        add_btn.clicked.connect(self._on_add_countdown)
        layout.addWidget(add_btn, alignment=Qt.AlignLeft)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        self._countdown_container = QWidget()
        self._countdown_layout = QVBoxLayout(self._countdown_container)
        self._countdown_layout.setAlignment(Qt.AlignTop)
        self._countdown_layout.setSpacing(12)
        
        scroll_area.setWidget(self._countdown_container)
        layout.addWidget(scroll_area)
        
        return widget
    
    def _create_pregnancy_tab(self) -> QWidget:
        """创建孕期助手标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # 孕期信息卡片
        self._pregnancy_tips_widget = PregnancyTipsWidget(self._storage)
        layout.addWidget(self._pregnancy_tips_widget)
        
        # 职场健康提醒
        workplace_frame = QFrame()
        workplace_frame.setObjectName("card")
        workplace_layout = QVBoxLayout(workplace_frame)
        
        workplace_title = QLabel("🏢 职场健康提醒")
        workplace_title.setObjectName("sectionLabel")
        workplace_layout.addWidget(workplace_title)
        
        reminders_info = QLabel(
            "✓ 站立活动 · ✓ 眼睛休息 · ✓ 营养补充 · ✓ 用药提醒\n"
            "✓ 姿势调整 · ✓ 情绪放松 · ✓ 午休提醒 · ✓ 胎动记录"
        )
        reminders_info.setWordWrap(True)
        workplace_layout.addWidget(reminders_info)
        
        config_btn = QPushButton("配置提醒")
        config_btn.setObjectName("secondaryButton")
        config_btn.clicked.connect(lambda: self._on_settings(tab_index=2))
        workplace_layout.addWidget(config_btn, alignment=Qt.AlignLeft)
        
        layout.addWidget(workplace_frame)
        layout.addStretch()
        
        return widget
    
    def _create_diet_tab(self) -> QWidget:
        """创建饮食记录标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)
        
        # 说明
        info_label = QLabel("🍽️ 记录每日饮食，获取个性化营养建议")
        layout.addWidget(info_label)
        
        # 今日饮食卡片
        diet_frame = QFrame()
        diet_frame.setObjectName("card")
        diet_layout = QVBoxLayout(diet_frame)
        
        diet_title = QLabel("📝 今日饮食记录")
        diet_title.setObjectName("sectionLabel")
        diet_layout.addWidget(diet_title)
        
        # 餐食列表
        self._meals_label = QLabel("早餐：未记录\n午餐：未记录\n晚餐：未记录")
        diet_layout.addWidget(self._meals_label)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        record_btn = QPushButton("📝 记录饮食")
        record_btn.clicked.connect(self._on_record_diet)
        btn_layout.addWidget(record_btn)
        
        analyze_btn = QPushButton("🤖 AI 分析营养")
        analyze_btn.setObjectName("secondaryButton")
        analyze_btn.clicked.connect(self._on_analyze_diet)
        btn_layout.addWidget(analyze_btn)
        
        btn_layout.addStretch()
        diet_layout.addLayout(btn_layout)
        
        layout.addWidget(diet_frame)
        
        # 营养分析结果
        self._nutrition_frame = QFrame()
        self._nutrition_frame.setObjectName("card")
        self._nutrition_frame.setVisible(False)
        nutrition_layout = QVBoxLayout(self._nutrition_frame)
        
        nutrition_title = QLabel("📊 营养分析")
        nutrition_title.setObjectName("sectionLabel")
        nutrition_layout.addWidget(nutrition_title)
        
        self._nutrition_label = QLabel()
        self._nutrition_label.setWordWrap(True)
        nutrition_layout.addWidget(self._nutrition_label)
        
        layout.addWidget(self._nutrition_frame)
        layout.addStretch()
        
        return widget
    
    def _connect_signals(self):
        """连接信号"""
        # 主题变更
        self._theme_manager.theme_changed.connect(self._on_theme_changed)
        
        # 提醒触发
        self._reminder_engine.reminder_triggered.connect(self._on_reminder_triggered)
    
    def _load_data(self):
        """加载数据"""
        self._refresh_events()
        self._refresh_countdowns()
        self._refresh_diet()
        self._update_status()
    
    def _refresh_ui(self):
        """刷新 UI"""
        self._update_status()
        self._pregnancy_tips_widget.refresh()
    
    def _refresh_events(self):
        """刷新事件列表"""
        # 清空现有事件
        while self._events_layout.count():
            item = self._events_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 加载事件
        events = self._storage.get_events()
        today_events = [e for e in events if not e.is_countdown and e.enabled]
        
        if not today_events:
            no_events_label = QLabel("暂无事件，点击「添加事件」创建新事件")
            no_events_label.setAlignment(Qt.AlignCenter)
            self._events_layout.addWidget(no_events_label)
        else:
            for event in today_events:
                card = EventCard(event)
                card.edit_clicked.connect(lambda e=event: self._on_edit_event(e))
                card.delete_clicked.connect(lambda e=event: self._on_delete_event(e))
                self._events_layout.addWidget(card)
        
        self._events_layout.addStretch()
    
    def _refresh_countdowns(self):
        """刷新倒计时"""
        # 清空现有
        while self._countdown_layout.count():
            item = self._countdown_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 加载倒计时事件
        countdowns = self._storage.get_countdown_events()
        
        # 添加预产期倒计时（如果有）
        pregnancy = self._storage.get_pregnancy_config()
        if pregnancy.enabled and pregnancy.due_date:
            due_countdown = CountdownWidget(
                title="🎀 预产期",
                target_date=pregnancy.due_date,
                description="期待宝宝的到来"
            )
            self._countdown_layout.addWidget(due_countdown)
        
        if not countdowns and not (pregnancy.enabled and pregnancy.due_date):
            no_countdown_label = QLabel("暂无倒计时事件")
            no_countdown_label.setAlignment(Qt.AlignCenter)
            self._countdown_layout.addWidget(no_countdown_label)
        else:
            for event in countdowns:
                if event.target_date:
                    widget = CountdownWidget(
                        title=event.title,
                        target_date=event.target_date,
                        description=event.description
                    )
                    widget.edit_clicked.connect(lambda e=event: self._on_edit_event(e))
                    widget.delete_clicked.connect(lambda e=event: self._on_delete_event(e))
                    self._countdown_layout.addWidget(widget)
        
        self._countdown_layout.addStretch()
    
    def _refresh_diet(self):
        """刷新饮食记录"""
        record = self._storage.get_today_diet_record()
        
        meals_text = []
        meal_types = {
            'breakfast': '早餐',
            'lunch': '午餐',
            'dinner': '晚餐',
            'snack': '加餐'
        }
        
        recorded = {m.type: m for m in record.meals}
        
        for meal_type, name in meal_types.items():
            if meal_type in recorded:
                foods = ", ".join(recorded[meal_type].foods)
                meals_text.append(f"{name}：{foods}")
            else:
                meals_text.append(f"{name}：未记录")
        
        self._meals_label.setText("\n".join(meals_text))
        
        # 显示分析结果
        if record.analysis:
            self._nutrition_frame.setVisible(True)
            analysis = record.analysis
            
            status = analysis.get('nutrition_status', {})
            status_text = " · ".join([f"{k}: {v}" for k, v in status.items()])
            
            recommendations = analysis.get('recommendations', [])
            rec_text = "\n".join([
                f"• {r.get('food', '')} - {r.get('benefit', '')}"
                for r in recommendations
            ])
            
            tip = analysis.get('tip', '')
            
            self._nutrition_label.setText(
                f"【营养状态】\n{status_text}\n\n"
                f"【推荐食物】\n{rec_text}\n\n"
                f"💡 {tip}"
            )
        else:
            self._nutrition_frame.setVisible(False)
    
    def _update_status(self):
        """更新状态信息"""
        today = date.today()
        self._status_label.setText(f"📅 {today.strftime('%Y年%m月%d日')}")
        
        # 更新今日提醒统计
        events_count = len([e for e in self._storage.get_events() if e.enabled])
        self._today_reminder_label.setText(f"今日事件：{events_count} 个")
    
    @Slot()
    def _on_add_event(self):
        """添加事件"""
        dialog = AddEventDialog(self)
        if dialog.exec():
            event = dialog.get_event()
            self._storage.add_event(event)
            self._reminder_engine.reload_all()
            self._refresh_events()
    
    @Slot()
    def _on_add_countdown(self):
        """添加倒计时"""
        dialog = AddEventDialog(self, is_countdown=True)
        if dialog.exec():
            event = dialog.get_event()
            self._storage.add_event(event)
            self._refresh_countdowns()
    
    def _on_edit_event(self, event):
        """编辑事件"""
        dialog = AddEventDialog(self, event=event)
        if dialog.exec():
            updated_event = dialog.get_event()
            self._storage.update_event(updated_event)
            self._reminder_engine.reload_all()
            self._refresh_events()
            self._refresh_countdowns()
    
    def _on_delete_event(self, event):
        """删除事件"""
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除「{event.title}」吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._storage.delete_event(event.id)
            self._reminder_engine.reload_all()
            self._refresh_events()
            self._refresh_countdowns()
    
    @Slot()
    def _on_settings(self, tab_index: int = 0):
        """打开设置"""
        dialog = SettingsDialog(
            self._storage,
            self._theme_manager,
            self._reminder_engine,
            self
        )
        dialog.setCurrentTab(tab_index)
        if dialog.exec():
            self._refresh_ui()
            self._load_data()
    
    @Slot()
    def _on_record_diet(self):
        """记录饮食"""
        from .dialogs.diet_record import DietRecordDialog
        dialog = DietRecordDialog(self._storage, self)
        if dialog.exec():
            self._refresh_diet()
    
    @Slot()
    def _on_analyze_diet(self):
        """AI 分析饮食"""
        record = self._storage.get_today_diet_record()
        if not record.meals:
            QMessageBox.information(
                self,
                "提示",
                "请先记录今日饮食再进行分析"
            )
            return
        
        # TODO: 调用 LLM 进行分析
        QMessageBox.information(
            self,
            "提示",
            "营养分析功能即将上线，敬请期待！"
        )
    
    @Slot(str)
    def _on_theme_changed(self, theme_name: str):
        """主题变更处理"""
        # 刷新 UI
        self._refresh_ui()
    
    @Slot(str, str, str, int)
    def _on_reminder_triggered(self, reminder_type: str, title: str, content: str, priority: int):
        """提醒触发处理"""
        # 显示系统通知
        try:
            from plyer import notification
            notification.notify(
                title=title,
                message=content,
                app_name=APP_NAME,
                timeout=5
            )
        except Exception as e:
            print(f"发送通知失败: {e}")
    
    def closeEvent(self, event: QCloseEvent):
        """关闭事件 - 最小化到托盘"""
        event.ignore()
        self.hide()
    
    def show_from_tray(self):
        """从托盘恢复显示"""
        self.showNormal()
        self.activateWindow()
        self.raise_()
