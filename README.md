# 💧 DrinkWater - 孕期健康提醒助手

一款专为孕妈妈设计的 Windows 桌面提醒应用，帮助您在忙碌的工作中保持健康习惯。

## ✨ 主要功能

### 🔔 智能提醒系统
- **喝水提醒** - 可配置间隔，保持水分摄入
- **站立活动** - 久坐提醒，促进血液循环
- **眼睛休息** - 20-20-20 法则，保护视力
- **姿势调整** - 正确坐姿，减轻腰部负担
- **营养补充** - 定时加餐提醒
- **用药提醒** - 叶酸、维生素等定时服药
- **午休提醒** - 适当休息，恢复精力
- **情绪放松** - 深呼吸、冥想引导

### 👶 孕期助手
- 自动计算孕周和预产期
- 显示宝宝发育阶段
- 每日孕期建议（AI 生成）
- 胎动记录功能

### 🍽️ 饮食管理
- 记录每日饮食
- AI 营养分析
- 个性化食物推荐

### ⏰ 事件管理
- 普通事件提醒
- 重要事件倒计时
- 一次性/周期性提醒

### 🎨 个性化主题
- Hello Kitty 粉色主题
- 鬼灭之刃和风主题
- 支持自定义主题

### 🤖 AI 能力
- 支持 DeepSeek、GLM-4、通义千问、OpenAI 等多种模型
- 智能内容生成
- 自动降级保障

## 🚀 快速开始

### 环境要求
- Python 3.10+
- Windows 10/11（最终运行环境）

### 安装依赖

```bash
cd drinkwater
pip install -r requirements.txt
```

### 运行应用

```bash
python main.py
```

### 打包为 exe

```bash
pip install pyinstaller
pyinstaller setup.spec
```

打包后的文件在 `dist/DrinkWater.exe`

## 📁 项目结构

```
drinkwater/
├── main.py                 # 应用入口
├── requirements.txt        # 依赖清单
├── version.json           # 版本信息
├── setup.spec             # PyInstaller 配置
├── src/
│   ├── core/              # 核心业务逻辑
│   │   ├── llm/           # 多模型 LLM 客户端
│   │   ├── scheduler.py   # 任务调度器
│   │   ├── reminder_engine.py  # 提醒引擎
│   │   └── pregnancy.py   # 孕期计算
│   ├── data/              # 数据层
│   │   ├── models.py      # 数据模型
│   │   ├── storage.py     # JSON 存储
│   │   └── cache.py       # API 缓存
│   ├── ui/                # 界面层
│   │   ├── main_window.py # 主窗口
│   │   ├── tray_icon.py   # 系统托盘
│   │   ├── theme_manager.py # 主题管理
│   │   ├── dialogs/       # 对话框
│   │   └── widgets/       # 自定义组件
│   └── utils/             # 工具模块
│       ├── autostart.py   # 开机自启
│       ├── updater.py     # 自动更新
│       └── constants.py   # 常量定义
└── resources/             # 资源文件
    └── themes/            # 主题包
```

## 🎨 自定义主题

1. 在 `resources/themes/` 下创建新文件夹
2. 添加 `theme.json` 配置文件
3. 添加 `style.qss` 样式表
4. 添加 `icons/` 和 `images/` 资源
5. 重启应用，在设置中选择新主题

## 🔧 配置 AI 模型

1. 打开设置 → AI 模型
2. 输入 API Key
3. 选择使用模式：
   - **智能模式** - 平衡效果和成本（推荐）
   - **完全 AI** - 效果最佳
   - **节约模式** - 最低成本
   - **关闭 AI** - 使用固定模板

## 📝 版本历史

### v1.0.0 (2026-02-04)
- 🎉 首次发布
- 完整的提醒系统
- 孕期助手功能
- 双主题支持
- 多 AI 模型支持

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

💝 祝每一位准妈妈孕期顺利，宝宝健康！
