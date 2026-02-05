# -*- coding: utf-8 -*-
"""系统托盘图标"""

from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor, QPainterPath, QBrush, QPen

from .theme_manager import ThemeManager
from ..utils.constants import APP_NAME


class TrayIcon(QSystemTrayIcon):
    """系统托盘图标"""
    
    def __init__(self, main_window, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        
        self._main_window = main_window
        self._theme_manager = theme_manager
        self._is_paused = False
        
        self._setup_icon()
        self._setup_menu()
        self._connect_signals()
    
    def _create_default_tray_icon(self) -> QIcon:
        """创建默认的水滴托盘图标"""
        # 创建一个 64x64 的透明画布
        size = 64
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        # 绘制水滴形状
        path = QPainterPath()
        
        # 水滴的顶点和曲线
        cx, cy = size / 2, size * 0.15  # 顶点位置
        bottom_y = size * 0.85  # 底部位置
        width = size * 0.4  # 水滴宽度的一半
        
        # 从顶点开始绘制水滴
        path.moveTo(cx, cy)
        # 左侧曲线
        path.cubicTo(
            cx - width * 0.3, cy + size * 0.2,  # 控制点1
            cx - width, bottom_y - size * 0.2,  # 控制点2
            cx - width * 0.8, bottom_y - size * 0.1  # 终点
        )
        # 底部圆弧（左半部分）
        path.cubicTo(
            cx - width * 0.6, bottom_y + size * 0.05,
            cx - width * 0.2, bottom_y + size * 0.08,
            cx, bottom_y
        )
        # 底部圆弧（右半部分）
        path.cubicTo(
            cx + width * 0.2, bottom_y + size * 0.08,
            cx + width * 0.6, bottom_y + size * 0.05,
            cx + width * 0.8, bottom_y - size * 0.1
        )
        # 右侧曲线回到顶点
        path.cubicTo(
            cx + width, bottom_y - size * 0.2,
            cx + width * 0.3, cy + size * 0.2,
            cx, cy
        )
        
        # 填充水滴（使用主题色或默认蓝色）
        try:
            primary_color = self._theme_manager.get_color('primary')
            if not primary_color.isValid():
                primary_color = QColor("#4A90D9")
        except:
            primary_color = QColor("#4A90D9")  # 默认蓝色
        
        painter.setBrush(QBrush(primary_color))
        painter.setPen(QPen(primary_color.darker(120), 2))
        painter.drawPath(path)
        
        # 添加高光效果
        highlight = QPainterPath()
        highlight.addEllipse(cx - width * 0.3, cy + size * 0.25, width * 0.35, width * 0.5)
        painter.setBrush(QBrush(QColor(255, 255, 255, 120)))
        painter.setPen(Qt.NoPen)
        painter.drawPath(highlight)
        
        painter.end()
        
        return QIcon(pixmap)
    
    def _setup_icon(self):
        """设置托盘图标"""
        icon = self._theme_manager.get_icon('tray')
        if icon and not icon.isNull():
            self.setIcon(icon)
        else:
            # 使用动态生成的默认图标
            self.setIcon(self._create_default_tray_icon())
        
        self.setToolTip(f"{APP_NAME} - 点击显示主窗口")
    
    def _setup_menu(self):
        """设置右键菜单"""
        menu = QMenu()
        
        # 显示主窗口
        show_action = QAction("📱 显示主窗口", self)
        show_action.triggered.connect(self._on_show)
        menu.addAction(show_action)
        
        menu.addSeparator()
        
        # 快速喝水记录
        water_action = QAction("💧 记录喝水", self)
        water_action.triggered.connect(self._on_record_water)
        menu.addAction(water_action)
        
        menu.addSeparator()
        
        # 暂停/恢复提醒
        self._pause_action = QAction("⏸️ 暂停提醒", self)
        self._pause_action.triggered.connect(self._on_toggle_pause)
        menu.addAction(self._pause_action)
        
        menu.addSeparator()
        
        # 设置
        settings_action = QAction("⚙️ 设置", self)
        settings_action.triggered.connect(self._on_settings)
        menu.addAction(settings_action)
        
        menu.addSeparator()
        
        # 退出
        quit_action = QAction("❌ 退出", self)
        quit_action.triggered.connect(self._on_quit)
        menu.addAction(quit_action)
        
        self.setContextMenu(menu)
    
    def _connect_signals(self):
        """连接信号"""
        self.activated.connect(self._on_activated)
        self._theme_manager.theme_changed.connect(self._on_theme_changed)
    
    @Slot(QSystemTrayIcon.ActivationReason)
    def _on_activated(self, reason):
        """托盘图标激活"""
        if reason == QSystemTrayIcon.Trigger:
            # 单击 - 显示/隐藏主窗口
            if self._main_window.isVisible():
                self._main_window.hide()
            else:
                self._main_window.show_from_tray()
        elif reason == QSystemTrayIcon.DoubleClick:
            # 双击 - 显示主窗口
            self._main_window.show_from_tray()
    
    @Slot()
    def _on_show(self):
        """显示主窗口"""
        self._main_window.show_from_tray()
    
    @Slot()
    def _on_record_water(self):
        """记录喝水"""
        # 显示简单通知
        self.showMessage(
            "💧 喝水打卡",
            "已记录一次喝水，继续保持！",
            QSystemTrayIcon.Information,
            3000
        )
        # TODO: 记录到数据
    
    @Slot()
    def _on_toggle_pause(self):
        """暂停/恢复提醒"""
        self._is_paused = not self._is_paused
        
        if self._is_paused:
            self._pause_action.setText("▶️ 恢复提醒")
            self.showMessage(
                "⏸️ 提醒已暂停",
                "所有提醒已暂停，点击恢复",
                QSystemTrayIcon.Information,
                2000
            )
            # TODO: 暂停调度器
        else:
            self._pause_action.setText("⏸️ 暂停提醒")
            self.showMessage(
                "▶️ 提醒已恢复",
                "所有提醒已恢复正常",
                QSystemTrayIcon.Information,
                2000
            )
            # TODO: 恢复调度器
    
    @Slot()
    def _on_settings(self):
        """打开设置"""
        self._main_window.show_from_tray()
        self._main_window._on_settings()
    
    @Slot()
    def _on_quit(self):
        """退出应用"""
        from PySide6.QtWidgets import QApplication
        QApplication.quit()
    
    @Slot(str)
    def _on_theme_changed(self, theme_name: str):
        """主题变更"""
        self._setup_icon()
    
    def show_notification(self, title: str, message: str, icon_type=None):
        """显示通知"""
        if icon_type is None:
            icon_type = QSystemTrayIcon.Information
        self.showMessage(title, message, icon_type, 5000)
