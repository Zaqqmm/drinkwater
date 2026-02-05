# -*- coding: utf-8 -*-
"""主窗口"""

from datetime import date, datetime
from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget, QFrame, QScrollArea,
    QMessageBox, QSystemTrayIcon, QDateEdit, QTextBrowser,
    QSplitter, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, Slot, QDate
from PySide6.QtGui import QCloseEvent, QIcon

from .theme_manager import ThemeManager
from .icon_manager import icon_manager
from .widgets.event_card import EventCard
from .widgets.countdown import CountdownWidget
from .widgets.pregnancy_tips import PregnancyTipsWidget
from .widgets.water_tracker import WaterTrackerWidget
from .dialogs.settings import SettingsDialog
from .dialogs.add_event import AddEventDialog
from ..data.storage import StorageManager
from ..core.reminder_engine import ReminderEngine
from ..core.llm.manager import LLMManager
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
        self._selected_diet_date = date.today()  # 当前选中的饮食日期
        
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
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 内容容器（用于半透明背景和圆角）
        content_container = QWidget()
        content_container.setObjectName("contentContainer")
        main_layout.addWidget(content_container)
        
        # 内容布局
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(16)
        
        # 顶部标题栏
        header = self._create_header()
        content_layout.addWidget(header)
        
        # 主内容区（选项卡）
        self._tab_widget = QTabWidget()
        content_layout.addWidget(self._tab_widget)
        
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
        
        # 喝水记录标签页
        self._water_tracker = WaterTrackerWidget(self._storage, self._reminder_engine)
        self._tab_widget.addTab(self._water_tracker, "💧 喝水记录")
    
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
        
        self._water_progress_label = QLabel("💧 饮水进度：0%")
        self._water_progress_label.setCursor(Qt.PointingHandCursor)
        self._water_progress_label.setToolTip("点击查看喝水记录")
        self._water_progress_label.mousePressEvent = lambda e: self._tab_widget.setCurrentIndex(4)
        stats_layout.addWidget(self._water_progress_label)
        
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
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 日期选择栏（固定在顶部）
        date_frame = QFrame()
        date_frame.setObjectName("card")
        date_layout = QHBoxLayout(date_frame)
        
        # 上一天按钮
        prev_btn = QPushButton("◀ 上一天")
        prev_btn.setObjectName("secondaryButton")
        prev_btn.clicked.connect(self._on_diet_prev_day)
        date_layout.addWidget(prev_btn)
        
        # 日期选择器
        self._diet_date_edit = QDateEdit()
        self._diet_date_edit.setDate(QDate.currentDate())
        self._diet_date_edit.setCalendarPopup(True)
        self._diet_date_edit.setDisplayFormat("yyyy年MM月dd日")
        self._diet_date_edit.setMaximumDate(QDate.currentDate())
        self._diet_date_edit.dateChanged.connect(self._on_diet_date_changed)
        date_layout.addWidget(self._diet_date_edit)
        
        # 下一天按钮
        next_btn = QPushButton("下一天 ▶")
        next_btn.setObjectName("secondaryButton")
        next_btn.clicked.connect(self._on_diet_next_day)
        date_layout.addWidget(next_btn)
        
        # 今天按钮
        today_btn = QPushButton("📅 今天")
        today_btn.clicked.connect(self._on_diet_today)
        date_layout.addWidget(today_btn)
        
        date_layout.addStretch()
        layout.addWidget(date_frame)
        
        # 使用 QSplitter 让用户可以拖动调整饮食记录和分析结果的大小
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(8)
        splitter.setChildrenCollapsible(False)
        
        # 饮食记录卡片
        diet_frame = QFrame()
        diet_frame.setObjectName("card")
        diet_layout = QVBoxLayout(diet_frame)
        
        self._diet_title_label = QLabel("📝 今日饮食记录")
        self._diet_title_label.setObjectName("sectionLabel")
        diet_layout.addWidget(self._diet_title_label)
        
        # 餐食列表
        self._meals_label = QLabel("早餐：未记录\n午餐：未记录\n晚餐：未记录")
        diet_layout.addWidget(self._meals_label)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        self._record_diet_btn = QPushButton("📝 记录饮食")
        self._record_diet_btn.clicked.connect(self._on_record_diet)
        btn_layout.addWidget(self._record_diet_btn)
        
        analyze_btn = QPushButton("🤖 AI 分析营养")
        analyze_btn.setObjectName("secondaryButton")
        analyze_btn.clicked.connect(self._on_analyze_diet)
        btn_layout.addWidget(analyze_btn)
        
        btn_layout.addStretch()
        diet_layout.addLayout(btn_layout)
        
        splitter.addWidget(diet_frame)
        
        # 营养分析结果（使用 QTextBrowser 渲染 Markdown）
        self._nutrition_frame = QFrame()
        self._nutrition_frame.setObjectName("card")
        self._nutrition_frame.setVisible(False)
        nutrition_layout = QVBoxLayout(self._nutrition_frame)
        nutrition_layout.setContentsMargins(12, 12, 12, 12)
        
        nutrition_title = QLabel("📊 营养分析")
        nutrition_title.setObjectName("sectionLabel")
        nutrition_layout.addWidget(nutrition_title)
        
        self._nutrition_browser = QTextBrowser()
        self._nutrition_browser.setOpenExternalLinks(True)
        self._nutrition_browser.setMinimumHeight(200)
        # 让 QTextBrowser 可以扩展填充可用空间
        self._nutrition_browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        nutrition_layout.addWidget(self._nutrition_browser)
        
        splitter.addWidget(self._nutrition_frame)
        
        # 设置初始分割比例（饮食记录较小，分析结果较大）
        splitter.setStretchFactor(0, 1)  # 饮食记录
        splitter.setStretchFactor(1, 3)  # 分析结果（占更大空间）
        
        layout.addWidget(splitter, 1)  # stretch factor 1，让 splitter 占据剩余空间
        
        return widget
    
    @Slot()
    def _on_diet_prev_day(self):
        """切换到前一天"""
        current = self._diet_date_edit.date()
        self._diet_date_edit.setDate(current.addDays(-1))
    
    @Slot()
    def _on_diet_next_day(self):
        """切换到后一天"""
        current = self._diet_date_edit.date()
        if current < QDate.currentDate():
            self._diet_date_edit.setDate(current.addDays(1))
    
    @Slot()
    def _on_diet_today(self):
        """切换到今天"""
        self._diet_date_edit.setDate(QDate.currentDate())
    
    @Slot(QDate)
    def _on_diet_date_changed(self, qdate: QDate):
        """日期变更处理"""
        self._selected_diet_date = date(qdate.year(), qdate.month(), qdate.day())
        self._refresh_diet()
        
        # 更新标题
        if self._selected_diet_date == date.today():
            self._diet_title_label.setText("📝 今日饮食记录")
            self._record_diet_btn.setEnabled(True)
        else:
            self._diet_title_label.setText(f"📝 {self._selected_diet_date.strftime('%Y年%m月%d日')} 饮食记录")
            self._record_diet_btn.setEnabled(False)  # 历史记录不能修改
    
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
        self._water_tracker.refresh()
    
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
        """刷新饮食记录（根据选中的日期）"""
        # 获取选中日期的记录
        if self._selected_diet_date == date.today():
            record = self._storage.get_today_diet_record()
        else:
            record = self._storage.get_diet_record(self._selected_diet_date)
        
        meals_text = []
        meal_types = {
            'breakfast': '🌅 早餐',
            'morning_snack': '🥤 上午加餐',
            'lunch': '☀️ 午餐',
            'afternoon_snack': '🍵 下午加餐',
            'dinner': '🌙 晚餐',
            'evening_snack': '🥛 晚上加餐',
        }
        
        if record:
            recorded = {m.type: m for m in record.meals}
        else:
            recorded = {}
        
        for meal_type, name in meal_types.items():
            if meal_type in recorded:
                foods = ", ".join(recorded[meal_type].foods)
                meals_text.append(f"{name}：{foods}")
            else:
                meals_text.append(f"{name}：未记录")
        
        self._meals_label.setText("\n".join(meals_text))
        
        # 显示分析结果（使用 Markdown 渲染）
        if record and record.analysis:
            self._nutrition_frame.setVisible(True)
            analysis = record.analysis
            
            # 如果是 markdown 格式的字符串，直接渲染
            if isinstance(analysis, str):
                self._render_markdown(analysis)
            else:
                # 兼容旧的 JSON 格式，转换为文本显示
                self._render_json_analysis(analysis)
        else:
            self._nutrition_frame.setVisible(False)
    
    def _render_markdown(self, markdown_text: str):
        """渲染 Markdown 内容到 QTextBrowser"""
        try:
            import markdown
            html = markdown.markdown(
                markdown_text, 
                extensions=['tables', 'fenced_code', 'nl2br']
            )
            # 添加基本样式
            styled_html = f"""
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; line-height: 1.6; }}
                h2 {{ color: #333; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
                h3 {{ color: #555; }}
                ul {{ padding-left: 20px; }}
                li {{ margin: 5px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f5f5f5; }}
            </style>
            {html}
            """
            self._nutrition_browser.setHtml(styled_html)
        except ImportError:
            # 如果没有 markdown 库，直接显示原文
            self._nutrition_browser.setPlainText(markdown_text)
    
    def _render_json_analysis(self, analysis: dict):
        """渲染旧的 JSON 格式分析结果"""
        # 营养状态
        nutrition_names = {
            'protein': '蛋白质',
            'carbohydrate': '碳水化合物',
            'fat': '脂肪',
            'vitamins': '维生素',
            'fiber': '膳食纤维'
        }
        status = analysis.get('nutrition_status', {})
        status_lines = []
        for key, name in nutrition_names.items():
            if key in status:
                item = status[key]
                if isinstance(item, dict):
                    level = item.get('level', '未知')
                    comment = item.get('comment', '')
                    status_lines.append(f"• {name}: {level} - {comment}")
                else:
                    status_lines.append(f"• {name}: {item}")
        status_text = "\n".join(status_lines) if status_lines else "暂无数据"
        
        # 热量估算
        calories = analysis.get('calories_estimate', {})
        total_cal = calories.get('total', 0)
        cal_assessment = calories.get('assessment', '')
        
        # 改进建议
        recommendations = analysis.get('recommendations', [])
        if isinstance(recommendations, list):
            rec_text = "\n".join([f"• {r}" for r in recommendations if isinstance(r, str)])
        else:
            rec_text = "暂无建议"
        
        # 体重控制建议
        weight_tips = analysis.get('weight_control_tips', '')
        
        # 总结
        tip = analysis.get('tip', '')
        
        text = f"""<h3>营养状态</h3>
<p>{status_text.replace(chr(10), '<br>')}</p>

<h3>热量估算</h3>
<p>总热量：约 {total_cal} 千卡<br>{cal_assessment}</p>

<h3>改进建议</h3>
<p>{rec_text.replace(chr(10), '<br>')}</p>

<h3>体重控制</h3>
<p>{weight_tips}</p>

<p><b>💡 {tip}</b></p>
"""
        self._nutrition_browser.setHtml(text)
    
    def _update_status(self):
        """更新状态信息"""
        today = date.today()
        self._status_label.setText(f"📅 {today.strftime('%Y年%m月%d日')}")
        
        # 更新今日提醒统计
        events_count = len([e for e in self._storage.get_events() if e.enabled])
        self._today_reminder_label.setText(f"今日事件：{events_count} 个")
        
        # 更新饮水进度
        water_total = self._storage.get_today_water_total()
        water_target = self._storage.get_config('water_reminder.daily_target', 1800)
        water_percent = int(water_total / water_target * 100) if water_target > 0 else 0
        
        if water_total >= water_target:
            self._water_progress_label.setText(f"💧 已达标 {water_total}ml ({water_percent}%)")
            self._water_progress_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        else:
            self._water_progress_label.setText(f"💧 {water_total}/{water_target}ml ({water_percent}%)")
            self._water_progress_label.setStyleSheet("")
    
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
        # 获取选中日期的记录
        if self._selected_diet_date == date.today():
            record = self._storage.get_today_diet_record()
        else:
            record = self._storage.get_diet_record(self._selected_diet_date)
        
        if not record or not record.meals:
            date_str = "今日" if self._selected_diet_date == date.today() else self._selected_diet_date.strftime('%Y年%m月%d日')
            QMessageBox.information(
                self,
                "提示",
                f"请先记录{date_str}饮食再进行分析"
            )
            return
        
        # 构建 prompt
        prompt = self._build_diet_analysis_prompt(record, self._selected_diet_date)
        
        # 调用 LLM
        try:
            llm_manager = LLMManager()
            response = llm_manager.call(prompt, max_tokens=1500)
            
            if response.success:
                content = response.content.strip() if response.content else ""
                
                # 打印原始内容用于调试
                print(f"[DEBUG] AI 原始返回内容 (长度={len(content)}):\n{content[:500] if content else '(空)'}")
                
                # 检查是否为空
                if not content:
                    QMessageBox.warning(
                        self,
                        "分析失败",
                        "AI 返回了空内容，请检查 LLM 配置后重试。"
                    )
                    return
                
                # 直接保存 Markdown 内容作为分析结果
                self._storage.update_diet_analysis(self._selected_diet_date, content)
                
                # 刷新显示
                self._refresh_diet()
                
                QMessageBox.information(
                    self,
                    "分析完成",
                    "营养分析已完成，请查看分析结果！"
                )
            else:
                QMessageBox.warning(
                    self,
                    "分析失败",
                    f"AI 分析失败：{response.error_message}\n\n"
                    "请检查 LLM 配置是否正确。"
                )
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "错误",
                f"分析过程出错：{str(e)}"
            )
    
    def _build_diet_analysis_prompt(self, record, analysis_date: date) -> str:
        """构建饮食分析 prompt（时间感知）"""
        
        # 餐食类型中文映射
        meal_type_names = {
            'breakfast': '早餐',
            'morning_snack': '上午加餐',
            'lunch': '午餐',
            'afternoon_snack': '下午加餐',
            'dinner': '晚餐',
            'evening_snack': '晚上加餐',
        }
        
        # 构建餐食记录文本
        meals_text = ""
        for meal in record.meals:
            type_name = meal_type_names.get(meal.type, meal.type)
            foods = "、".join(meal.foods)
            meals_text += f"- {type_name} ({meal.time}): {foods}\n"
        
        if not meals_text:
            meals_text = "（无记录）"
        
        # 获取当前时间信息
        now = datetime.now()
        current_hour = now.hour
        
        # 判断分析模式
        is_today = (analysis_date == date.today())
        
        if is_today:
            # 今日实时分析：根据当前时间判断应有的餐食
            if current_hour < 11:
                time_period = "上午"
                expected_meals = "早餐"
                time_note = f"现在是{time_period}，主要评估早餐营养是否充足"
            elif current_hour < 14:
                time_period = "中午"
                expected_meals = "早餐、午餐"
                time_note = f"现在是{time_period}，评估早餐和午餐的营养摄入"
            elif current_hour < 18:
                time_period = "下午"
                expected_meals = "早餐、午餐、下午加餐"
                time_note = f"现在是{time_period}，评估全天至今的营养摄入，并给出晚餐建议"
            else:
                time_period = "晚上"
                expected_meals = "全天饮食"
                time_note = f"现在是{time_period}，评估全天饮食营养摄入"
            
            analysis_mode = f"实时分析（{time_period}时段，应有{expected_meals}）"
        else:
            # 历史分析：按全天评估
            time_period = "全天"
            time_note = "这是历史记录，按全天饮食进行完整营养评估"
            analysis_mode = "历史全天分析"
        
        # 检查是否启用孕期模式
        pregnancy_config = self._storage.get_pregnancy_config()
        user_info = ""
        pregnancy_note = ""
        if pregnancy_config.enabled and pregnancy_config.current_week:
            week = pregnancy_config.current_week
            # 判断孕期阶段
            if week <= 12:
                trimester = "孕早期"
                key_nutrients = "叶酸、维生素B6、铁"
            elif week <= 27:
                trimester = "孕中期"
                key_nutrients = "钙、铁、蛋白质、DHA"
            else:
                trimester = "孕晚期"
                key_nutrients = "铁、钙、蛋白质、膳食纤维"
            
            user_info = f"""
- **用户身份**：孕妇
- **当前孕周**：孕{week}周（{trimester}）
- **重点营养素**：{key_nutrients}"""
            
            pregnancy_note = f"""

⚠️ **孕期营养特别提醒**：
当前用户是孕{week}周的孕妇（{trimester}），在进行营养分析时请特别注意：
1. 重点关注{key_nutrients}等孕期关键营养素的摄入
2. 根据{trimester}的特点给出针对性的饮食建议
3. 注意孕期禁忌食物的提醒（如生食、高汞鱼类、酒精、咖啡因等）
4. 关注体重管理，给出合理的热量建议"""
        
        prompt = f"""你是专业营养师，请分析以下饮食记录并用 Markdown 格式返回分析结果。

## 分析信息
- **当前时间**：{now.strftime('%Y-%m-%d %H:%M')}（{time_period}）
- **分析日期**：{analysis_date.strftime('%Y-%m-%d')}（{'今天' if is_today else '历史'}）
- **分析模式**：{analysis_mode}
- **时间说明**：{time_note}{user_info}
{pregnancy_note}

## 饮食记录
{meals_text}

## 请按以下 Markdown 格式返回分析结果：

## 📊 营养评估

| 营养素 | 状态 | 说明 |
|--------|------|------|
| 蛋白质 | 充足/适中/不足 | 简短说明 |
| 碳水化合物 | 充足/适中/偏多/不足 | 简短说明 |
| 脂肪 | 适中/偏多/不足 | 简短说明 |
| 维生素 | 充足/适中/不足 | 简短说明 |
| 膳食纤维 | 充足/适中/不足 | 简短说明 |

## 🔥 热量估算

- **已摄入热量**：约 XXX 千卡
- **评估**：（根据时段和记录给出评估）

## 💡 改进建议

1. 建议一
2. 建议二
3. 建议三

## ⚖️ 体重控制建议

（给出具体的饮食调整和运动建议）

## 📝 总结

（一句话总结今日饮食情况和下一步行动）

---
注意：根据当前时段合理评估，如果是上午只有早餐是正常的，不要因为没有午餐晚餐就判断热量不足。"""

        return prompt
    
    @Slot(str)
    def _on_theme_changed(self, theme_name: str):
        """主题变更处理"""
        # 刷新 UI
        self._refresh_ui()
    
    @Slot(str, str, str, int)
    def _on_reminder_triggered(self, reminder_type: str, title: str, content: str, priority: int):
        """提醒触发处理"""
        # 显示系统通知
        self._show_notification(title, content)
    
    def _show_notification(self, title: str, content: str):
        """显示系统通知（跨平台兼容）"""
        import platform
        
        # 方法1：尝试使用 Qt 托盘通知（最可靠的跨平台方案）
        if hasattr(self, '_tray_icon') and self._tray_icon:
            self._tray_icon.showMessage(title, content, QSystemTrayIcon.Information, 5000)
            return
        
        # 方法2：macOS 使用 osascript 发送通知
        if platform.system() == 'Darwin':
            try:
                import subprocess
                # 使用 AppleScript 发送通知
                script = f'display notification "{content}" with title "{title}"'
                subprocess.run(['osascript', '-e', script], check=True)
                return
            except Exception as e:
                print(f"macOS 通知失败: {e}")
        
        # 方法3：使用 plyer 作为备选
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
