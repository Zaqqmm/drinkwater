#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DrinkWater - Windows 桌面提醒应用
主入口文件
"""

import sys
import os

# 确保项目路径在 sys.path 中
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from src.ui.main_window import MainWindow
from src.ui.tray_icon import TrayIcon
from src.ui.theme_manager import ThemeManager
from src.core.scheduler import SchedulerManager
from src.core.reminder_engine import ReminderEngine
from src.data.storage import StorageManager
from src.utils.constants import APP_NAME


def main():
    """应用主入口"""
    # 启用高 DPI 支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # 创建应用实例
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setQuitOnLastWindowClosed(False)  # 关闭窗口不退出，最小化到托盘
    
    # 设置默认字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)
    
    # 初始化存储管理器
    storage = StorageManager()
    
    # 初始化主题管理器并应用主题
    theme_manager = ThemeManager()
    theme_manager.apply_theme(app)
    
    # 初始化调度器
    scheduler = SchedulerManager()
    
    # 初始化提醒引擎
    reminder_engine = ReminderEngine(storage, scheduler)
    
    # 创建主窗口
    main_window = MainWindow(storage, theme_manager, reminder_engine)
    
    # 创建系统托盘
    tray_icon = TrayIcon(main_window, theme_manager)
    tray_icon.show()
    
    # 启动调度器
    scheduler.start()
    
    # 加载已保存的提醒任务
    reminder_engine.load_reminders()
    
    # 显示主窗口
    main_window.show()
    
    # 运行应用
    exit_code = app.exec()
    
    # 清理
    scheduler.shutdown()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
