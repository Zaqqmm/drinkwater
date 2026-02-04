# -*- coding: utf-8 -*-
"""饮食记录对话框"""

from datetime import datetime

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit,
    QComboBox, QGroupBox, QFrame
)
from PySide6.QtCore import Qt

from ...data.storage import StorageManager
from ...data.models import MealRecord


class DietRecordDialog(QDialog):
    """饮食记录对话框"""
    
    MEAL_TYPES = [
        ('breakfast', '🌅 早餐'),
        ('lunch', '☀️ 午餐'),
        ('dinner', '🌙 晚餐'),
        ('snack', '🍪 加餐'),
    ]
    
    def __init__(self, storage: StorageManager, parent=None):
        super().__init__(parent)
        
        self._storage = storage
        
        self.setWindowTitle("记录饮食")
        self.setMinimumWidth(500)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # 说明
        info_label = QLabel(
            "📝 记录今天吃了什么，AI 将分析营养并推荐食物"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # 餐食类型
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("餐食类型："))
        
        self._meal_type_combo = QComboBox()
        for meal_id, meal_name in self.MEAL_TYPES:
            self._meal_type_combo.addItem(meal_name, meal_id)
        type_layout.addWidget(self._meal_type_combo)
        type_layout.addStretch()
        
        layout.addLayout(type_layout)
        
        # 食物输入
        food_group = QGroupBox("食物内容")
        food_layout = QVBoxLayout(food_group)
        
        self._food_edit = QTextEdit()
        self._food_edit.setPlaceholderText(
            "输入吃的食物，用逗号或换行分隔\n"
            "例如：米饭、红烧肉、青菜、豆腐汤"
        )
        self._food_edit.setMaximumHeight(120)
        food_layout.addWidget(self._food_edit)
        
        # 快捷选择
        quick_label = QLabel("快捷选择：")
        quick_label.setStyleSheet("color: #666666; font-size: 11px;")
        food_layout.addWidget(quick_label)
        
        quick_layout = QHBoxLayout()
        quick_foods = ["米饭", "面条", "鸡蛋", "牛奶", "水果", "蔬菜", "肉类", "鱼类"]
        for food in quick_foods:
            btn = QPushButton(food)
            btn.setFixedWidth(60)
            btn.clicked.connect(lambda checked, f=food: self._add_quick_food(f))
            quick_layout.addWidget(btn)
        quick_layout.addStretch()
        food_layout.addLayout(quick_layout)
        
        layout.addWidget(food_group)
        
        # 今日已记录
        today_record = self._storage.get_today_diet_record()
        if today_record.meals:
            recorded_group = QGroupBox("今日已记录")
            recorded_layout = QVBoxLayout(recorded_group)
            
            for meal in today_record.meals:
                meal_name = dict(self.MEAL_TYPES).get(meal.type, meal.type)
                foods = ", ".join(meal.foods)
                label = QLabel(f"{meal_name}：{foods}")
                label.setStyleSheet("color: #666666;")
                recorded_layout.addWidget(label)
            
            layout.addWidget(recorded_group)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def _add_quick_food(self, food: str):
        """添加快捷食物"""
        current = self._food_edit.toPlainText()
        if current:
            if not current.endswith(('、', '，', ',', '\n')):
                current += "、"
        current += food
        self._food_edit.setPlainText(current)
    
    def _on_save(self):
        """保存记录"""
        food_text = self._food_edit.toPlainText().strip()
        if not food_text:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "提示", "请输入食物内容")
            return
        
        # 解析食物列表
        import re
        foods = re.split(r'[,，、\n]+', food_text)
        foods = [f.strip() for f in foods if f.strip()]
        
        if not foods:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "提示", "请输入食物内容")
            return
        
        # 创建记录
        meal = MealRecord(
            type=self._meal_type_combo.currentData(),
            time=datetime.now().strftime("%H:%M"),
            foods=foods
        )
        
        # 保存
        from datetime import date
        self._storage.add_meal(date.today(), meal)
        
        self.accept()
