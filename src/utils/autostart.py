# -*- coding: utf-8 -*-
"""开机自启动管理（Windows）"""

import sys
import os
from pathlib import Path

from ..utils.constants import APP_NAME


class AutoStartManager:
    """开机自启动管理器"""
    
    # Windows 注册表路径
    REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    def __init__(self):
        self._is_windows = sys.platform == 'win32'
    
    def is_enabled(self) -> bool:
        """检查是否已启用开机自启动"""
        if not self._is_windows:
            return False
        
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REG_PATH,
                0,
                winreg.KEY_READ
            )
            try:
                winreg.QueryValueEx(key, APP_NAME)
                return True
            except FileNotFoundError:
                return False
            finally:
                winreg.CloseKey(key)
        except Exception:
            return False
    
    def enable(self) -> bool:
        """启用开机自启动"""
        if not self._is_windows:
            print("自启动仅支持 Windows 系统")
            return False
        
        try:
            import winreg
            
            # 获取可执行文件路径
            if getattr(sys, 'frozen', False):
                # 打包后的 exe
                exe_path = sys.executable
            else:
                # 开发环境
                exe_path = f'"{sys.executable}" "{Path(__file__).parent.parent.parent / "main.py"}"'
            
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REG_PATH,
                0,
                winreg.KEY_SET_VALUE
            )
            
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe_path)
            winreg.CloseKey(key)
            
            return True
            
        except Exception as e:
            print(f"启用自启动失败: {e}")
            return False
    
    def disable(self) -> bool:
        """禁用开机自启动"""
        if not self._is_windows:
            return False
        
        try:
            import winreg
            
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REG_PATH,
                0,
                winreg.KEY_SET_VALUE
            )
            
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass  # 本来就不存在
            finally:
                winreg.CloseKey(key)
            
            return True
            
        except Exception as e:
            print(f"禁用自启动失败: {e}")
            return False
    
    def set_enabled(self, enabled: bool) -> bool:
        """设置自启动状态"""
        if enabled:
            return self.enable()
        else:
            return self.disable()


# 全局单例
autostart_manager = AutoStartManager()
