# -*- coding: utf-8 -*-
"""主题管理器"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor, QIcon, QPixmap

from ..utils.constants import THEMES_DIR, DEFAULT_THEME, USER_DATA_DIR
from ..utils.helpers import load_json, save_json


class ThemeManager(QObject):
    """主题管理器 - 支持动态主题切换"""
    
    # 主题变更信号
    theme_changed = Signal(str)  # theme_name
    
    def __init__(self):
        super().__init__()
        self._current_theme = DEFAULT_THEME
        self._themes: Dict[str, Dict[str, Any]] = {}
        self._theme_config: Dict[str, Any] = {}
        
        self._scan_themes()
        self._load_user_preference()
    
    def _scan_themes(self):
        """扫描可用主题"""
        self._themes = {}
        
        if not THEMES_DIR.exists():
            THEMES_DIR.mkdir(parents=True, exist_ok=True)
            self._create_default_themes()
        
        for theme_dir in THEMES_DIR.iterdir():
            if theme_dir.is_dir():
                config_file = theme_dir / "theme.json"
                if config_file.exists():
                    config = load_json(config_file, {})
                    if config:
                        theme_name = theme_dir.name
                        self._themes[theme_name] = {
                            'path': theme_dir,
                            'config': config
                        }
    
    def _create_default_themes(self):
        """创建默认主题"""
        # 创建 Hello Kitty 主题
        self._create_hello_kitty_theme()
        # 创建鬼灭之刃主题
        self._create_demon_slayer_theme()
    
    def _create_hello_kitty_theme(self):
        """创建 Hello Kitty 主题"""
        theme_dir = THEMES_DIR / "hello_kitty"
        theme_dir.mkdir(parents=True, exist_ok=True)
        (theme_dir / "icons").mkdir(exist_ok=True)
        (theme_dir / "images").mkdir(exist_ok=True)
        
        # 主题配置
        config = {
            "name": "hello_kitty",
            "display_name": "Hello Kitty 主题",
            "version": "1.0.0",
            "author": "DrinkWater Team",
            "description": "可爱的 Hello Kitty 粉色主题",
            
            "colors": {
                "primary": "#FF69B4",
                "secondary": "#FFFFFF",
                "accent": "#FFD700",
                "background": "#FFF0F5",
                "card_background": "#FFFFFF",
                "text": "#FF1493",
                "text_secondary": "#666666",
                "border": "#FFB6D9",
                "success": "#90EE90",
                "warning": "#FFD700",
                "error": "#FF6B6B"
            },
            
            "fonts": {
                "main": "Microsoft YaHei",
                "size": {
                    "title": 18,
                    "normal": 12,
                    "small": 10
                }
            },
            
            "style": {
                "border_radius": 12,
                "button_height": 36,
                "card_shadow": True,
                "animation_enabled": True
            }
        }
        
        save_json(theme_dir / "theme.json", config)
        
        # QSS 样式表
        qss = """
/* Hello Kitty 主题样式表 */

QMainWindow, QDialog {
    background-color: #FFF0F5;
}

QWidget {
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
    font-size: 12px;
}

QLabel {
    color: #FF1493;
}

QLabel#titleLabel {
    font-size: 18px;
    font-weight: bold;
    color: #FF69B4;
}

QPushButton {
    background-color: #FF69B4;
    color: white;
    border: none;
    border-radius: 12px;
    padding: 8px 16px;
    font-weight: bold;
    min-height: 36px;
}

QPushButton:hover {
    background-color: #FF85C1;
}

QPushButton:pressed {
    background-color: #E6559F;
}

QPushButton:disabled {
    background-color: #FFB6D9;
    color: #FFFFFF;
}

QPushButton#secondaryButton {
    background-color: #FFFFFF;
    color: #FF69B4;
    border: 2px solid #FF69B4;
}

QPushButton#secondaryButton:hover {
    background-color: #FFF0F5;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #FFFFFF;
    border: 2px solid #FFB6D9;
    border-radius: 8px;
    padding: 8px;
    color: #333333;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #FF69B4;
}

QComboBox {
    background-color: #FFFFFF;
    border: 2px solid #FFB6D9;
    border-radius: 8px;
    padding: 8px;
    color: #333333;
    min-height: 36px;
}

QComboBox:hover {
    border-color: #FF69B4;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    width: 12px;
    height: 12px;
}

QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    border: 2px solid #FFB6D9;
    border-radius: 8px;
    selection-background-color: #FFB6D9;
}

QSpinBox, QDoubleSpinBox, QTimeEdit, QDateEdit {
    background-color: #FFFFFF;
    border: 2px solid #FFB6D9;
    border-radius: 8px;
    padding: 8px;
    color: #333333;
    min-height: 36px;
}

QCheckBox {
    color: #FF1493;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #FFB6D9;
    border-radius: 4px;
    background-color: #FFFFFF;
}

QCheckBox::indicator:checked {
    background-color: #FF69B4;
    border-color: #FF69B4;
}

QRadioButton {
    color: #FF1493;
    spacing: 8px;
}

QRadioButton::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #FFB6D9;
    border-radius: 10px;
    background-color: #FFFFFF;
}

QRadioButton::indicator:checked {
    background-color: #FF69B4;
    border-color: #FF69B4;
}

QGroupBox {
    border: 2px solid #FFB6D9;
    border-radius: 12px;
    margin-top: 12px;
    padding-top: 12px;
    background-color: #FFFFFF;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: #FF69B4;
    font-weight: bold;
}

QTabWidget::pane {
    border: 2px solid #FFB6D9;
    border-radius: 12px;
    background-color: #FFFFFF;
}

QTabBar::tab {
    background-color: #FFF0F5;
    color: #FF69B4;
    padding: 10px 20px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #FF69B4;
    color: #FFFFFF;
}

QTabBar::tab:hover:!selected {
    background-color: #FFB6D9;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    background-color: #FFF0F5;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #FFB6D9;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #FF69B4;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QProgressBar {
    background-color: #FFE4EC;
    border: none;
    border-radius: 8px;
    text-align: center;
    color: #FF1493;
}

QProgressBar::chunk {
    background-color: #FF69B4;
    border-radius: 8px;
}

QSlider::groove:horizontal {
    background-color: #FFB6D9;
    height: 8px;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background-color: #FF69B4;
    width: 20px;
    height: 20px;
    margin: -6px 0;
    border-radius: 10px;
}

QSlider::handle:horizontal:hover {
    background-color: #FF85C1;
}

QListWidget, QTreeWidget, QTableWidget {
    background-color: #FFFFFF;
    border: 2px solid #FFB6D9;
    border-radius: 8px;
    alternate-background-color: #FFF8FA;
}

QListWidget::item, QTreeWidget::item {
    padding: 8px;
    border-radius: 4px;
}

QListWidget::item:selected, QTreeWidget::item:selected {
    background-color: #FFB6D9;
    color: #FF1493;
}

QListWidget::item:hover, QTreeWidget::item:hover {
    background-color: #FFE4EC;
}

QMenu {
    background-color: #FFFFFF;
    border: 2px solid #FFB6D9;
    border-radius: 8px;
    padding: 4px;
}

QMenu::item {
    padding: 8px 24px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #FFB6D9;
    color: #FF1493;
}

QToolTip {
    background-color: #FF69B4;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 4px 8px;
}

/* 自定义卡片样式 */
QFrame#card {
    background-color: #FFFFFF;
    border: 2px solid #FFB6D9;
    border-radius: 12px;
}

QFrame#card:hover {
    border-color: #FF69B4;
}
"""
        
        with open(theme_dir / "style.qss", 'w', encoding='utf-8') as f:
            f.write(qss)
    
    def _create_demon_slayer_theme(self):
        """创建鬼灭之刃主题"""
        theme_dir = THEMES_DIR / "demon_slayer"
        theme_dir.mkdir(parents=True, exist_ok=True)
        (theme_dir / "icons").mkdir(exist_ok=True)
        (theme_dir / "images").mkdir(exist_ok=True)
        
        # 主题配置
        config = {
            "name": "demon_slayer",
            "display_name": "鬼灭之刃主题",
            "version": "1.0.0",
            "author": "DrinkWater Team",
            "description": "日式和风，鬼灭之刃风格主题",
            
            "colors": {
                "primary": "#2C1810",
                "secondary": "#DC143C",
                "accent": "#00CED1",
                "background": "#F5E6D3",
                "card_background": "#FFFFFF",
                "text": "#2C1810",
                "text_secondary": "#666666",
                "border": "#DC143C",
                "success": "#228B22",
                "warning": "#FF8C00",
                "error": "#DC143C"
            },
            
            "fonts": {
                "main": "Microsoft YaHei",
                "size": {
                    "title": 18,
                    "normal": 12,
                    "small": 10
                }
            },
            
            "style": {
                "border_radius": 8,
                "button_height": 36,
                "card_shadow": True,
                "animation_enabled": True
            }
        }
        
        save_json(theme_dir / "theme.json", config)
        
        # QSS 样式表
        qss = """
/* 鬼灭之刃主题样式表 */

QMainWindow, QDialog {
    background-color: #F5E6D3;
}

QWidget {
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
    font-size: 12px;
}

QLabel {
    color: #2C1810;
}

QLabel#titleLabel {
    font-size: 18px;
    font-weight: bold;
    color: #DC143C;
}

QPushButton {
    background-color: #2C1810;
    color: #F5E6D3;
    border: 2px solid #DC143C;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: bold;
    min-height: 36px;
}

QPushButton:hover {
    background-color: #DC143C;
    color: white;
}

QPushButton:pressed {
    background-color: #8B0000;
}

QPushButton:disabled {
    background-color: #A9A9A9;
    border-color: #808080;
    color: #D3D3D3;
}

QPushButton#accentButton {
    background-color: #00CED1;
    border-color: #00CED1;
    color: #2C1810;
}

QPushButton#accentButton:hover {
    background-color: #20B2AA;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #FFFFFF;
    border: 2px solid #2C1810;
    border-radius: 6px;
    padding: 8px;
    color: #2C1810;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #DC143C;
}

QComboBox {
    background-color: #FFFFFF;
    border: 2px solid #2C1810;
    border-radius: 6px;
    padding: 8px;
    color: #2C1810;
    min-height: 36px;
}

QComboBox:hover {
    border-color: #DC143C;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    border: 2px solid #2C1810;
    selection-background-color: #F5E6D3;
}

QSpinBox, QDoubleSpinBox, QTimeEdit, QDateEdit {
    background-color: #FFFFFF;
    border: 2px solid #2C1810;
    border-radius: 6px;
    padding: 8px;
    color: #2C1810;
    min-height: 36px;
}

QCheckBox {
    color: #2C1810;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #2C1810;
    border-radius: 4px;
    background-color: #FFFFFF;
}

QCheckBox::indicator:checked {
    background-color: #DC143C;
    border-color: #DC143C;
}

QRadioButton {
    color: #2C1810;
    spacing: 8px;
}

QRadioButton::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #2C1810;
    border-radius: 10px;
    background-color: #FFFFFF;
}

QRadioButton::indicator:checked {
    background-color: #DC143C;
    border-color: #DC143C;
}

QGroupBox {
    border: 2px solid #2C1810;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
    background-color: #FFFFFF;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: #DC143C;
    font-weight: bold;
}

QTabWidget::pane {
    border: 2px solid #2C1810;
    border-radius: 8px;
    background-color: #FFFFFF;
}

QTabBar::tab {
    background-color: #F5E6D3;
    color: #2C1810;
    padding: 10px 20px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
    border: 2px solid #2C1810;
    border-bottom: none;
}

QTabBar::tab:selected {
    background-color: #DC143C;
    color: #FFFFFF;
    border-color: #DC143C;
}

QTabBar::tab:hover:!selected {
    background-color: #EBD5C0;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    background-color: #F5E6D3;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #2C1810;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #DC143C;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QProgressBar {
    background-color: #EBD5C0;
    border: 2px solid #2C1810;
    border-radius: 6px;
    text-align: center;
    color: #2C1810;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #DC143C, stop:1 #FF8C00);
    border-radius: 4px;
}

QSlider::groove:horizontal {
    background-color: #2C1810;
    height: 8px;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background-color: #DC143C;
    width: 20px;
    height: 20px;
    margin: -6px 0;
    border-radius: 10px;
}

QSlider::handle:horizontal:hover {
    background-color: #FF4500;
}

QListWidget, QTreeWidget, QTableWidget {
    background-color: #FFFFFF;
    border: 2px solid #2C1810;
    border-radius: 6px;
    alternate-background-color: #FAF0E6;
}

QListWidget::item, QTreeWidget::item {
    padding: 8px;
    border-radius: 4px;
}

QListWidget::item:selected, QTreeWidget::item:selected {
    background-color: #DC143C;
    color: #FFFFFF;
}

QListWidget::item:hover, QTreeWidget::item:hover {
    background-color: #F5E6D3;
}

QMenu {
    background-color: #FFFFFF;
    border: 2px solid #2C1810;
    border-radius: 6px;
    padding: 4px;
}

QMenu::item {
    padding: 8px 24px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #DC143C;
    color: #FFFFFF;
}

QToolTip {
    background-color: #2C1810;
    color: #F5E6D3;
    border: 2px solid #DC143C;
    border-radius: 4px;
    padding: 4px 8px;
}

/* 自定义卡片样式 */
QFrame#card {
    background-color: #FFFFFF;
    border: 2px solid #2C1810;
    border-radius: 8px;
}

QFrame#card:hover {
    border-color: #DC143C;
}
"""
        
        with open(theme_dir / "style.qss", 'w', encoding='utf-8') as f:
            f.write(qss)
    
    def _load_user_preference(self):
        """加载用户主题偏好"""
        pref_file = USER_DATA_DIR / "theme_preference.json"
        pref = load_json(pref_file, {})
        self._current_theme = pref.get('theme', DEFAULT_THEME)
        
        # 确保主题存在
        if self._current_theme not in self._themes:
            self._current_theme = DEFAULT_THEME
    
    def _save_user_preference(self):
        """保存用户主题偏好"""
        pref_file = USER_DATA_DIR / "theme_preference.json"
        save_json(pref_file, {'theme': self._current_theme})
    
    def get_available_themes(self) -> List[Dict[str, Any]]:
        """获取所有可用主题"""
        themes = []
        for name, theme in self._themes.items():
            config = theme['config']
            themes.append({
                'id': name,
                'name': config.get('display_name', name),
                'description': config.get('description', ''),
                'author': config.get('author', ''),
                'version': config.get('version', '1.0.0'),
                'is_current': name == self._current_theme
            })
        return themes
    
    def get_current_theme(self) -> str:
        """获取当前主题名称"""
        return self._current_theme
    
    def get_theme_config(self, theme_name: str = None) -> Dict[str, Any]:
        """获取主题配置"""
        name = theme_name or self._current_theme
        if name in self._themes:
            return self._themes[name]['config']
        return {}
    
    def get_theme_path(self, theme_name: str = None) -> Optional[Path]:
        """获取主题目录路径"""
        name = theme_name or self._current_theme
        if name in self._themes:
            return self._themes[name]['path']
        return None
    
    def load_theme(self, theme_name: str) -> bool:
        """加载主题"""
        if theme_name not in self._themes:
            return False
        
        self._current_theme = theme_name
        self._theme_config = self._themes[theme_name]['config']
        self._save_user_preference()
        
        return True
    
    def apply_theme(self, app: QApplication, theme_name: str = None) -> bool:
        """应用主题到应用程序"""
        name = theme_name or self._current_theme
        
        if not self.load_theme(name):
            # 回退到默认主题
            name = DEFAULT_THEME
            if not self.load_theme(name):
                return False
        
        # 加载 QSS
        theme_path = self.get_theme_path(name)
        if theme_path:
            qss_file = theme_path / "style.qss"
            if qss_file.exists():
                with open(qss_file, 'r', encoding='utf-8') as f:
                    qss = f.read()
                
                # 替换变量
                qss = self._process_qss_variables(qss)
                app.setStyleSheet(qss)
        
        # 发送主题变更信号
        self.theme_changed.emit(name)
        
        return True
    
    def _process_qss_variables(self, qss: str) -> str:
        """处理 QSS 中的变量"""
        config = self._theme_config
        colors = config.get('colors', {})
        fonts = config.get('fonts', {})
        style = config.get('style', {})
        
        # 替换颜色变量
        for key, value in colors.items():
            qss = qss.replace(f"{{{{{key}}}}}", value)
        
        # 替换字体变量
        if 'main' in fonts:
            qss = qss.replace("{{fonts.main}}", fonts['main'])
        if 'size' in fonts:
            for key, value in fonts['size'].items():
                qss = qss.replace(f"{{{{fonts.size.{key}}}}}", str(value))
        
        # 替换样式变量
        for key, value in style.items():
            qss = qss.replace(f"{{{{{key}}}}}", str(value))
        
        return qss
    
    def get_color(self, color_name: str) -> QColor:
        """获取主题颜色"""
        colors = self._theme_config.get('colors', {})
        color_str = colors.get(color_name, '#000000')
        return QColor(color_str)
    
    def get_icon(self, icon_name: str) -> Optional[QIcon]:
        """获取主题图标"""
        theme_path = self.get_theme_path()
        if theme_path:
            icon_path = theme_path / "icons" / f"{icon_name}.png"
            if icon_path.exists():
                return QIcon(str(icon_path))
            # 尝试 ICO 格式
            icon_path = theme_path / "icons" / f"{icon_name}.ico"
            if icon_path.exists():
                return QIcon(str(icon_path))
        return None
    
    def get_image(self, image_name: str) -> Optional[QPixmap]:
        """获取主题图片"""
        theme_path = self.get_theme_path()
        if theme_path:
            image_path = theme_path / "images" / f"{image_name}.png"
            if image_path.exists():
                return QPixmap(str(image_path))
        return None
    
    def refresh_theme(self):
        """刷新当前主题（重新加载）"""
        self._scan_themes()
        app = QApplication.instance()
        if app:
            self.apply_theme(app, self._current_theme)
