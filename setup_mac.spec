# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Mac 打包配置文件

使用方法：
1. 安装 PyInstaller: uv add pyinstaller --dev
2. 运行: uv run pyinstaller setup_mac.spec
3. 打包后的 app 文件在 dist/ 目录下
"""

import os
from pathlib import Path

# 项目根目录
project_root = Path(SPECPATH)

# 数据文件（资源文件）
datas = [
    # 主题资源
    (str(project_root / 'resources' / 'themes'), 'resources/themes'),
    # 配置文件
    (str(project_root / 'resources' / 'config'), 'resources/config'),
    # 默认数据
    (str(project_root / 'resources' / 'data'), 'resources/data'),
    # 版本信息
    (str(project_root / 'version.json'), '.'),
]

# 隐藏导入（动态导入的模块）
hiddenimports = [
    'plyer.platforms.macosx.notification',
    'apscheduler.triggers.interval',
    'apscheduler.triggers.cron',
    'apscheduler.triggers.date',
    'apscheduler.jobstores.memory',
    'apscheduler.schedulers.qt',
]

# 排除的模块（减小体积）
excludes = [
    'tkinter',
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'PIL',
    'cv2',
]

a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DrinkWater',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DrinkWater',
)

app = BUNDLE(
    coll,
    name='DrinkWater.app',
    icon=None,  # 可以设置 .icns 图标文件
    bundle_identifier='com.drinkwater.app',
    info_plist={
        'CFBundleName': 'DrinkWater',
        'CFBundleDisplayName': 'DrinkWater',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.15',
        'NSRequiresAquaSystemAppearance': False,  # 支持 Dark Mode
    },
)
