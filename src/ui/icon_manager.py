# -*- coding: utf-8 -*-
"""图标管理器"""

from pathlib import Path
from typing import Optional, Dict

from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QSize

from ..utils.constants import RESOURCES_ROOT


class IconManager:
    """图标管理器 - 统一管理应用图标"""
    
    # 默认图标（使用 emoji 作为文字替代）
    DEFAULT_ICONS = {
        'app': '💧',
        'tray': '💧',
        'water': '💧',
        'baby': '👶',
        'event': '📅',
        'settings': '⚙️',
        'notification': '🔔',
        'stand_up': '🚶‍♀️',
        'eye_rest': '👀',
        'nutrition': '🍎',
        'medication': '💊',
        'posture': '🪑',
        'relaxation': '🧘‍♀️',
        'nap': '😴',
        'fetal_movement': '👶',
        'countdown': '⏰',
        'add': '➕',
        'edit': '✏️',
        'delete': '🗑️',
        'refresh': '🔄',
        'check': '✅',
        'close': '❌',
        'info': 'ℹ️',
        'warning': '⚠️',
        'error': '❌',
        'success': '✅',
    }
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._icons_cache: Dict[str, QIcon] = {}
        self._theme_path: Optional[Path] = None
        self._initialized = True
    
    def set_theme_path(self, theme_path: Path):
        """设置当前主题路径"""
        self._theme_path = theme_path
        self._icons_cache.clear()  # 清空缓存
    
    def get_icon(self, icon_name: str, size: QSize = None) -> QIcon:
        """
        获取图标
        
        Args:
            icon_name: 图标名称
            size: 图标大小（可选）
            
        Returns:
            QIcon 对象
        """
        # 检查缓存
        cache_key = f"{icon_name}_{size.width() if size else 0}"
        if cache_key in self._icons_cache:
            return self._icons_cache[cache_key]
        
        icon = QIcon()
        
        # 1. 尝试从主题目录加载
        if self._theme_path:
            for ext in ['.png', '.ico', '.svg']:
                icon_path = self._theme_path / "icons" / f"{icon_name}{ext}"
                if icon_path.exists():
                    icon = QIcon(str(icon_path))
                    break
        
        # 2. 尝试从默认资源目录加载
        if icon.isNull():
            default_icons_dir = RESOURCES_ROOT / "icons"
            for ext in ['.png', '.ico', '.svg']:
                icon_path = default_icons_dir / f"{icon_name}{ext}"
                if icon_path.exists():
                    icon = QIcon(str(icon_path))
                    break
        
        # 3. 创建一个空图标（后续可以用 emoji 在 UI 中显示）
        # QIcon 不支持直接显示 emoji，但我们可以缓存一个空图标
        # 实际显示时使用 DEFAULT_ICONS 中的 emoji
        
        self._icons_cache[cache_key] = icon
        return icon
    
    def get_emoji(self, icon_name: str) -> str:
        """获取对应的 emoji（用于没有图标文件时的替代）"""
        return self.DEFAULT_ICONS.get(icon_name, '📌')
    
    def get_pixmap(self, icon_name: str, size: QSize = None) -> QPixmap:
        """获取图标的 QPixmap"""
        icon = self.get_icon(icon_name, size)
        if size:
            return icon.pixmap(size)
        return icon.pixmap(32, 32)  # 默认大小
    
    def has_icon(self, icon_name: str) -> bool:
        """检查是否有对应的图标文件"""
        if self._theme_path:
            for ext in ['.png', '.ico', '.svg']:
                if (self._theme_path / "icons" / f"{icon_name}{ext}").exists():
                    return True
        
        default_icons_dir = RESOURCES_ROOT / "icons"
        for ext in ['.png', '.ico', '.svg']:
            if (default_icons_dir / f"{icon_name}{ext}").exists():
                return True
        
        return False
    
    def get_available_icons(self) -> list:
        """获取所有可用的图标名称"""
        icons = set()
        
        # 从主题目录
        if self._theme_path:
            icons_dir = self._theme_path / "icons"
            if icons_dir.exists():
                for f in icons_dir.iterdir():
                    if f.suffix in ['.png', '.ico', '.svg']:
                        icons.add(f.stem)
        
        # 从默认目录
        default_icons_dir = RESOURCES_ROOT / "icons"
        if default_icons_dir.exists():
            for f in default_icons_dir.iterdir():
                if f.suffix in ['.png', '.ico', '.svg']:
                    icons.add(f.stem)
        
        # 添加默认 emoji 图标名称
        icons.update(self.DEFAULT_ICONS.keys())
        
        return sorted(list(icons))


# 全局单例
icon_manager = IconManager()
