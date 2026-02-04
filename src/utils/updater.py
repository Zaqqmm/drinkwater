# -*- coding: utf-8 -*-
"""自动升级管理器"""

import json
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

import httpx
from packaging import version

from .constants import APP_VERSION, UPDATE_CHECK_URL, PROJECT_ROOT


@dataclass
class UpdateInfo:
    """更新信息"""
    version: str
    download_url: str
    release_notes: str
    published_at: str
    is_newer: bool


class UpdateManager:
    """自动升级管理器"""
    
    def __init__(self):
        self._current_version = APP_VERSION
        self._latest_info: Optional[UpdateInfo] = None
    
    @property
    def current_version(self) -> str:
        """当前版本"""
        return self._current_version
    
    def check_update(self, timeout: int = 10) -> Optional[UpdateInfo]:
        """
        检查更新
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            如果有更新返回 UpdateInfo，否则返回 None
        """
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.get(UPDATE_CHECK_URL)
                
                if response.status_code != 200:
                    return None
                
                data = response.json()
                
                latest_version = data.get('tag_name', '').lstrip('v')
                if not latest_version:
                    return None
                
                # 比较版本
                is_newer = version.parse(latest_version) > version.parse(self._current_version)
                
                # 获取下载链接
                download_url = ""
                for asset in data.get('assets', []):
                    if asset.get('name', '').endswith('.exe'):
                        download_url = asset.get('browser_download_url', '')
                        break
                
                self._latest_info = UpdateInfo(
                    version=latest_version,
                    download_url=download_url,
                    release_notes=data.get('body', ''),
                    published_at=data.get('published_at', ''),
                    is_newer=is_newer
                )
                
                return self._latest_info if is_newer else None
                
        except Exception as e:
            print(f"检查更新失败: {e}")
            return None
    
    def download_update(
        self,
        update_info: UpdateInfo,
        progress_callback=None
    ) -> Optional[Path]:
        """
        下载更新
        
        Args:
            update_info: 更新信息
            progress_callback: 进度回调函数 (downloaded, total)
            
        Returns:
            下载的文件路径
        """
        if not update_info.download_url:
            return None
        
        try:
            # 创建临时文件
            temp_dir = Path(tempfile.gettempdir()) / "drinkwater_update"
            temp_dir.mkdir(exist_ok=True)
            
            filename = f"DrinkWater_{update_info.version}.exe"
            download_path = temp_dir / filename
            
            with httpx.Client(timeout=300) as client:
                with client.stream('GET', update_info.download_url) as response:
                    total = int(response.headers.get('content-length', 0))
                    downloaded = 0
                    
                    with open(download_path, 'wb') as f:
                        for chunk in response.iter_bytes(chunk_size=8192):
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            if progress_callback and total:
                                progress_callback(downloaded, total)
            
            return download_path
            
        except Exception as e:
            print(f"下载更新失败: {e}")
            return None
    
    def install_update(self, installer_path: Path) -> bool:
        """
        安装更新
        
        Args:
            installer_path: 安装程序路径
            
        Returns:
            是否成功启动安装
        """
        if not installer_path.exists():
            return False
        
        try:
            # 启动安装程序
            subprocess.Popen([str(installer_path)], shell=True)
            return True
        except Exception as e:
            print(f"启动安装程序失败: {e}")
            return False
    
    def get_changelog(self) -> str:
        """获取更新日志"""
        if self._latest_info:
            return self._latest_info.release_notes
        return ""


# 全局单例
update_manager = UpdateManager()
