# -*- coding: utf-8 -*-
"""喝水记录组件"""

import uuid
from datetime import date, datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QFrame, QScrollArea, QDateEdit, QInputDialog,
    QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, Slot, QDate, Signal

from ...data.storage import StorageManager
from ...data.models import WaterIntakeRecord
from ...core.reminder_engine import ReminderEngine


class WaterRecordItem(QFrame):
    """单条饮水记录项"""
    
    delete_clicked = Signal(str)  # 删除信号，传递记录ID
    
    def __init__(self, record: WaterIntakeRecord, parent=None):
        super().__init__(parent)
        self._record = record
        self.setObjectName("waterRecordItem")
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(12)
        
        # 时间
        time_label = QLabel(self._record.time.strftime("%H:%M"))
        time_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        layout.addWidget(time_label)
        
        # 饮水量
        amount_label = QLabel(f"{self._record.amount} ml")
        layout.addWidget(amount_label)
        
        # 备注
        if self._record.note:
            note_label = QLabel(f"({self._record.note})")
            note_label.setStyleSheet("color: #888888;")
            layout.addWidget(note_label)
        
        layout.addStretch()
        
        # 删除按钮
        delete_btn = QPushButton("删除")
        delete_btn.setObjectName("secondaryButton")
        delete_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self._record.id))
        layout.addWidget(delete_btn)


class WaterTrackerWidget(QWidget):
    """喝水记录组件"""
    
    def __init__(self, storage: StorageManager, reminder_engine: ReminderEngine, parent=None):
        super().__init__(parent)
        self._storage = storage
        self._reminder_engine = reminder_engine
        self._selected_date = date.today()
        
        self._setup_ui()
        self._refresh()
    
    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 日期选择栏
        date_frame = QFrame()
        date_frame.setObjectName("card")
        date_layout = QHBoxLayout(date_frame)
        date_layout.setContentsMargins(10, 8, 10, 8)
        date_layout.setSpacing(8)
        
        # 上一天按钮
        prev_btn = QPushButton("◀ 前一天")
        prev_btn.setObjectName("secondaryButton")
        prev_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        prev_btn.clicked.connect(self._on_prev_day)
        date_layout.addWidget(prev_btn)
        
        # 日期选择器
        self._date_edit = QDateEdit()
        self._date_edit.setDate(QDate.currentDate())
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDisplayFormat("yyyy-MM-dd")
        self._date_edit.setMaximumDate(QDate.currentDate())
        self._date_edit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._date_edit.dateChanged.connect(self._on_date_changed)
        date_layout.addWidget(self._date_edit)
        
        # 下一天按钮
        next_btn = QPushButton("后一天 ▶")
        next_btn.setObjectName("secondaryButton")
        next_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        next_btn.clicked.connect(self._on_next_day)
        date_layout.addWidget(next_btn)
        
        # 今天按钮
        today_btn = QPushButton("今天")
        today_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        today_btn.clicked.connect(self._on_today)
        date_layout.addWidget(today_btn)
        
        date_layout.addStretch()
        
        # 提醒设置按钮
        settings_btn = QPushButton("⚙️ 提醒设置")
        settings_btn.setObjectName("secondaryButton")
        settings_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        settings_btn.clicked.connect(self._on_settings)
        date_layout.addWidget(settings_btn)
        
        layout.addWidget(date_frame)
        
        # 进度卡片
        progress_frame = QFrame()
        progress_frame.setObjectName("card")
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(12, 10, 12, 10)
        progress_layout.setSpacing(8)
        
        # 进度标题行
        progress_header = QHBoxLayout()
        self._progress_title = QLabel("💧 今日饮水进度")
        self._progress_title.setObjectName("sectionLabel")
        progress_header.addWidget(self._progress_title)
        
        progress_header.addStretch()
        
        self._progress_label = QLabel("0 / 1800 ml (0%)")
        progress_header.addWidget(self._progress_label)
        
        progress_layout.addLayout(progress_header)
        
        # 进度条
        self._progress_bar = QProgressBar()
        self._progress_bar.setMinimum(0)
        self._progress_bar.setMaximum(1800)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setMinimumHeight(16)
        self._progress_bar.setMaximumHeight(24)
        self._progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                background-color: #F5F5F5;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #64B5F6, stop:1 #2196F3);
                border-radius: 7px;
            }
        """)
        progress_layout.addWidget(self._progress_bar)
        
        layout.addWidget(progress_frame)
        
        # 快捷记录卡片
        quick_frame = QFrame()
        quick_frame.setObjectName("card")
        quick_layout = QVBoxLayout(quick_frame)
        quick_layout.setContentsMargins(12, 10, 12, 10)
        quick_layout.setSpacing(8)
        
        quick_title = QLabel("⚡ 快捷记录（点击按钮记录饮水量）")
        quick_title.setObjectName("sectionLabel")
        quick_layout.addWidget(quick_title)
        
        # 快捷按钮行
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        
        quick_amounts = [150, 200, 250, 300, 500]
        for amount in quick_amounts:
            btn = QPushButton(f"{amount} ml")
            btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            btn.clicked.connect(lambda checked, a=amount: self._add_water(a))
            btn_row.addWidget(btn)
        
        # 自定义按钮
        custom_btn = QPushButton("自定义...")
        custom_btn.setObjectName("secondaryButton")
        custom_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        custom_btn.clicked.connect(self._on_custom_amount)
        btn_row.addWidget(custom_btn)
        
        quick_layout.addLayout(btn_row)
        
        layout.addWidget(quick_frame)
        
        # 记录列表卡片
        records_frame = QFrame()
        records_frame.setObjectName("card")
        records_layout = QVBoxLayout(records_frame)
        records_layout.setContentsMargins(12, 10, 12, 10)
        records_layout.setSpacing(8)
        
        self._records_title = QLabel("📋 今日记录")
        self._records_title.setObjectName("sectionLabel")
        records_layout.addWidget(self._records_title)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setMinimumHeight(100)
        
        self._records_container = QWidget()
        self._records_layout = QVBoxLayout(self._records_container)
        self._records_layout.setAlignment(Qt.AlignTop)
        self._records_layout.setSpacing(6)
        self._records_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area.setWidget(self._records_container)
        records_layout.addWidget(scroll_area)
        
        layout.addWidget(records_frame, 1)
    
    def _get_daily_target(self) -> int:
        """获取每日目标饮水量"""
        return self._storage.get_config('water_reminder.daily_target', 1800)
    
    def _refresh(self):
        """刷新显示"""
        is_today = self._selected_date == date.today()
        
        # 更新标题
        if is_today:
            self._progress_title.setText("💧 今日饮水进度")
            self._records_title.setText("📋 今日记录")
        else:
            date_str = self._selected_date.strftime('%Y-%m-%d')
            self._progress_title.setText(f"💧 {date_str} 饮水进度")
            self._records_title.setText(f"📋 {date_str} 记录")
        
        # 更新进度
        total = self._storage.get_water_total(self._selected_date)
        target = self._get_daily_target()
        
        self._progress_bar.setMaximum(target)
        self._progress_bar.setValue(min(total, target))
        
        percent = int(total / target * 100) if target > 0 else 0
        
        if total >= target:
            self._progress_label.setText(f"🎉 {total} / {target} ml ({percent}%) 目标达成!")
            self._progress_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        else:
            self._progress_label.setText(f"{total} / {target} ml ({percent}%)")
            self._progress_label.setStyleSheet("color: #666666;")
        
        # 刷新记录列表
        self._refresh_records()
    
    def _refresh_records(self):
        """刷新记录列表"""
        # 清空现有记录
        while self._records_layout.count():
            item = self._records_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 加载记录
        records = self._storage.get_water_records(self._selected_date)
        records.sort(key=lambda r: r.time, reverse=True)  # 按时间倒序
        
        if not records:
            no_records_label = QLabel("暂无饮水记录，点击上方按钮记录")
            no_records_label.setAlignment(Qt.AlignCenter)
            no_records_label.setStyleSheet("color: #999999; padding: 20px;")
            self._records_layout.addWidget(no_records_label)
        else:
            for record in records:
                item = WaterRecordItem(record)
                item.delete_clicked.connect(self._on_delete_record)
                self._records_layout.addWidget(item)
        
        self._records_layout.addStretch()
    
    def _add_water(self, amount: int, note: str = ""):
        """添加饮水记录"""
        # 只能记录今天的
        if self._selected_date != date.today():
            QMessageBox.information(self, "提示", "只能记录今天的饮水量")
            return
        
        record = WaterIntakeRecord(
            id=str(uuid.uuid4()),
            time=datetime.now(),
            amount=amount,
            note=note
        )
        
        self._storage.add_water_record(record)
        self._refresh()
    
    @Slot()
    def _on_custom_amount(self):
        """自定义饮水量"""
        if self._selected_date != date.today():
            QMessageBox.information(self, "提示", "只能记录今天的饮水量")
            return
        
        amount, ok = QInputDialog.getInt(
            self,
            "自定义饮水量",
            "请输入饮水量（ml）：",
            value=200,
            min=10,
            max=2000,
            step=10
        )
        
        if ok:
            note, ok2 = QInputDialog.getText(
                self,
                "添加备注",
                "备注（可选）："
            )
            self._add_water(amount, note if ok2 else "")
    
    @Slot(str)
    def _on_delete_record(self, record_id: str):
        """删除记录"""
        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除这条饮水记录吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._storage.delete_water_record(record_id)
            self._refresh()
    
    @Slot()
    def _on_prev_day(self):
        """切换到前一天"""
        current = self._date_edit.date()
        self._date_edit.setDate(current.addDays(-1))
    
    @Slot()
    def _on_next_day(self):
        """切换到后一天"""
        current = self._date_edit.date()
        if current < QDate.currentDate():
            self._date_edit.setDate(current.addDays(1))
    
    @Slot()
    def _on_today(self):
        """切换到今天"""
        self._date_edit.setDate(QDate.currentDate())
    
    @Slot(QDate)
    def _on_date_changed(self, qdate: QDate):
        """日期变更处理"""
        self._selected_date = date(qdate.year(), qdate.month(), qdate.day())
        self._refresh()
    
    @Slot()
    def _on_settings(self):
        """打开提醒设置"""
        from ..dialogs.water_reminder_settings import WaterReminderSettingsDialog
        
        dialog = WaterReminderSettingsDialog(
            self._storage,
            self._reminder_engine,
            self
        )
        
        if dialog.exec():
            # 刷新进度条最大值
            self._refresh()
    
    def refresh(self):
        """外部调用刷新"""
        self._refresh()
