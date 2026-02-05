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
            "version": "1.1.0",
            "author": "DrinkWater Team",
            "description": "可爱的 Hello Kitty 粉色主题，带背景图",
            
            "colors": {
                "primary": "#FF69B4",
                "primary_hover": "#FF85C1",
                "primary_pressed": "#E6559F",
                "secondary": "#FFFFFF",
                "accent": "#FFD700",
                "background": "#FFF0F5",
                "overlay_background": "rgba(255, 255, 255, 0.85)",
                "card_background": "rgba(255, 255, 255, 0.9)",
                "text": "#FF1493",
                "text_secondary": "#666666",
                "border": "#FFB6D9",
                "success": "#90EE90",
                "warning": "#FFD700",
                "error": "#FF6B6B"
            },
            
            "fonts": {
                "main": '"Microsoft YaHei", "PingFang SC", "Segoe UI", sans-serif',
                "size": {
                    "title": 18,
                    "subtitle": 16,
                    "normal": 13,
                    "small": 11
                }
            },
            
            "style": {
                "border_radius": 15,
                "button_height": 38,
                "card_shadow": True,
                "animation_enabled": True
            },
            
            "background_image": "images/background.jpg"
        }
        
        save_json(theme_dir / "theme.json", config)
        self._write_qss(theme_dir, config)
    
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
            "version": "1.1.0",
            "author": "DrinkWater Team",
            "description": "日式和风，鬼灭之刃风格主题，带背景图",
            
            "colors": {
                "primary": "#2C1810",
                "primary_hover": "#DC143C",
                "primary_pressed": "#8B0000",
                "secondary": "#DC143C",
                "accent": "#00CED1",
                "background": "#F5E6D3",
                "overlay_background": "rgba(255, 255, 255, 0.85)",
                "card_background": "rgba(255, 255, 255, 0.9)",
                "text": "#2C1810",
                "text_secondary": "#555555",
                "border": "#DC143C",
                "success": "#228B22",
                "warning": "#FF8C00",
                "error": "#DC143C"
            },
            
            "fonts": {
                "main": '"Microsoft YaHei", "PingFang SC", "Segoe UI", sans-serif',
                "size": {
                    "title": 18,
                    "subtitle": 16,
                    "normal": 13,
                    "small": 11
                }
            },
            
            "style": {
                "border_radius": 10,
                "button_height": 38,
                "card_shadow": True,
                "animation_enabled": True
            },
            
            "background_image": "images/background.jpg"
        }
        
        save_json(theme_dir / "theme.json", config)
        self._write_qss(theme_dir, config)

    def _write_qss(self, theme_dir: Path, config: Dict):
        """生成并写入 QSS 文件"""
        
        # 通用 QSS 模板
        qss_template = """
/* 全局样式 */
QMainWindow {
    background-color: {{colors.background}};
}

/* 具有背景图的容器（通常是 CentralWidget） */
#centralWidget {
    border-image: url("{{theme_path}}/{{background_image}}") 0 0 0 0 stretch stretch;
}

/* 内容覆盖层，提供透明背景以确保文字可读 */
#contentContainer {
    background-color: {{colors.overlay_background}};
    border-radius: {{style.border_radius}}px;
    margin: 10px;
}

QWidget {
    font-family: {{fonts.main}};
    font-size: {{fonts.size.normal}}px;
    color: {{colors.text}};
}

QDialog {
    background-color: {{colors.background}};
}

/* 标签 */
QLabel {
    color: {{colors.text}};
    background-color: transparent;
}

QLabel#titleLabel {
    font-size: {{fonts.size.title}}px;
    font-weight: bold;
    color: {{colors.primary}};
}

QLabel#sectionLabel {
    font-size: {{fonts.size.subtitle}}px;
    font-weight: bold;
    color: {{colors.primary}};
    margin-top: 10px;
    margin-bottom: 5px;
}

/* 按钮 */
QPushButton {
    background-color: {{colors.primary}};
    color: white;
    border: none;
    border-radius: {{style.border_radius}}px;
    padding: 8px 16px;
    font-weight: bold;
    min-height: {{style.button_height}}px;
}

QPushButton:hover {
    background-color: {{colors.primary_hover}};
}

QPushButton:pressed {
    background-color: {{colors.primary_pressed}};
    padding-top: 9px;
    padding-left: 17px;
}

QPushButton:disabled {
    background-color: #CCCCCC;
    color: #888888;
}

QPushButton#secondaryButton {
    background-color: transparent;
    color: {{colors.primary}};
    border: 2px solid {{colors.primary}};
}

QPushButton#secondaryButton:hover {
    background-color: {{colors.primary}};
    color: white;
}

/* 输入控件 */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QTimeEdit, QDateEdit, QComboBox {
    background-color: rgba(255, 255, 255, 0.9);
    border: 1px solid {{colors.border}};
    border-radius: {{style.border_radius}}px;
    padding: 8px;
    min-height: {{style.button_height}}px;
    selection-background-color: {{colors.primary}};
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 2px solid {{colors.primary}};
    background-color: #FFFFFF;
}

/* 组合框 */
QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    border: 1px solid {{colors.border}};
    border-radius: {{style.border_radius}}px;
    selection-background-color: {{colors.primary}};
    selection-color: white;
    padding: 5px;
}

/* 复选框与单选框 */
QCheckBox, QRadioButton {
    spacing: 8px;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 20px;
    height: 20px;
    border: 1px solid {{colors.border}};
    background-color: white;
    border-radius: 4px;
}

QRadioButton::indicator {
    border-radius: 10px;
}

QCheckBox::indicator:checked, QRadioButton::indicator:checked {
    background-color: {{colors.primary}};
    border-color: {{colors.primary}};
    image: url(":/icons/check.png"); /* 这里可能需要 SVG 或纯色绘制 */
}

/* 分组框 */
QGroupBox {
    border: 1px solid {{colors.border}};
    border-radius: {{style.border_radius}}px;
    margin-top: 1.5em;
    padding-top: 10px;
    background-color: rgba(255, 255, 255, 0.5);
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 10px;
    color: {{colors.primary}};
    font-weight: bold;
    background-color: transparent;
}

/* 选项卡 */
QTabWidget::pane {
    border: 1px solid {{colors.border}};
    border-radius: {{style.border_radius}}px;
    background-color: {{colors.card_background}};
    padding: 10px;
}

QTabBar::tab {
    background-color: rgba(255, 255, 255, 0.6);
    color: {{colors.text}};
    padding: 10px 20px;
    border-top-left-radius: {{style.border_radius}}px;
    border-top-right-radius: {{style.border_radius}}px;
    margin-right: 4px;
    min-width: 80px;
}

QTabBar::tab:selected {
    background-color: {{colors.primary}};
    color: white;
}

QTabBar::tab:hover:!selected {
    background-color: rgba(255, 255, 255, 0.9);
}

/* 滚动区域 */
QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    background-color: transparent;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: {{colors.border}};
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: {{colors.primary}};
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* 卡片样式 */
QFrame#card {
    background-color: {{colors.card_background}};
    border-radius: {{style.border_radius}}px;
    border: 1px solid rgba(0,0,0,0.05);
}

QFrame#card:hover {
    border: 1px solid {{colors.primary}};
    background-color: #FFFFFF;
}

/* 顶部标题栏 */
QFrame#header {
    background-color: transparent;
    border-bottom: 1px solid rgba(0,0,0,0.05);
    padding-bottom: 10px;
}

/* 列表与树 */
QListWidget, QTreeWidget, QTableWidget {
    background-color: {{colors.card_background}};
    border: 1px solid {{colors.border}};
    border-radius: {{style.border_radius}}px;
    alternate-background-color: rgba(0,0,0,0.02);
}

QListWidget::item, QTreeWidget::item {
    padding: 10px;
    border-radius: {{style.border_radius}}px;
}

QListWidget::item:selected, QTreeWidget::item:selected {
    background-color: {{colors.primary}};
    color: white;
}

QListWidget::item:hover:!selected {
    background-color: rgba(255, 255, 255, 0.8);
}
"""
        with open(theme_dir / "style.qss", 'w', encoding='utf-8') as f:
            f.write(qss_template)

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
                qss = self._process_qss_variables(qss, theme_path)
                app.setStyleSheet(qss)
        
        # 发送主题变更信号
        self.theme_changed.emit(name)
        
        return True
    
    def _process_qss_variables(self, qss: str, theme_path: Path) -> str:
        """处理 QSS 中的变量"""
        config = self._theme_config
        colors = config.get('colors', {})
        fonts = config.get('fonts', {})
        style = config.get('style', {})
        
        # 替换主题路径（用于图片）- 需要将反斜杠转换为斜杠
        theme_path_str = str(theme_path).replace('\\', '/')
        qss = qss.replace("{{theme_path}}", theme_path_str)
        
        # 替换背景图
        bg_image = config.get('background_image', '')
        qss = qss.replace("{{background_image}}", bg_image)
        
        # 替换颜色变量
        for key, value in colors.items():
            qss = qss.replace(f"{{{{colors.{key}}}}}", value)
        
        # 替换字体变量
        if 'main' in fonts:
            qss = qss.replace("{{fonts.main}}", fonts['main'])
        if 'size' in fonts:
            for key, value in fonts['size'].items():
                qss = qss.replace(f"{{{{fonts.size.{key}}}}}", str(value))
        
        # 替换样式变量
        for key, value in style.items():
            qss = qss.replace(f"{{{{style.{key}}}}}", str(value))
        
        return qss
    
    def get_color(self, color_name: str) -> QColor:
        """获取主题颜色"""
        colors = self._theme_config.get('colors', {})
        color_str = colors.get(color_name, '#000000')
        # 处理 rgba
        if color_str.startswith('rgba'):
            match = re.match(r'rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)', color_str)
            if match:
                r, g, b, a = match.groups()
                return QColor(int(r), int(g), int(b), int(float(a) * 255))
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
