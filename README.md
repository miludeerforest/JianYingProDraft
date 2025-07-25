# 🎬 剪映自动混剪工具

> **智能视频混剪解决方案** - 基于pyJianYingDraft开发的专业级自动混剪工具

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![Version](https://img.shields.io/badge/Version-v2.1.1-brightgreen.svg)](https://github.com/miludeerforest/JianYingProDraft)

一键生成专业级短视频，支持智能特效、防审核覆盖、字幕处理等完整功能。专为内容创作者和视频工作室设计。

## 🆕 最新更新 - v2.1.1 (2025-07-26)

### 🎯 Web端统计显示优化
- **📊 混剪统计面板** - 新增详细的混剪统计显示，包含素材数、特效数、覆盖率等
- **🔄 实时计数更新** - 支持类似终端的计数变化显示（如"15 → 16"）
- **📈 批量统计支持** - 批量混剪完成后正确显示统计信息
- **✨ 动画效果** - 添加统计变化的动画提示效果

### 🐛 界面加载修复
- **⚡ 加载器优化** - 修复页面卡在加载界面的问题
- **🛡️ 备用机制** - 添加3秒强制隐藏的备用加载机制
- **🔧 错误处理** - 完善JavaScript错误处理和调试信息

### 🧪 测试功能增强
- **🔬 测试页面** - 新增`/test`测试页面用于功能验证
- **🎮 模拟API** - 添加模拟混剪完成状态的测试接口
- **🌐 端口优化** - 支持多端口自动切换，解决端口占用问题

## ✨ 核心功能

### 🎯 智能混剪
- **现代化Web界面** - 直观的操作界面，实时统计显示
- **一键混剪** - 自动扫描素材，智能生成30-40秒短视频
- **批量生成** - 支持一次性生成多个不同版本，完整统计反馈

### 🛡️ 防审核技术
- **Pexels覆盖层** - 5%不透明度风景视频覆盖，有效防止平台识别
- **智能时长匹配** - 自动调整覆盖层时长，完美适配目标视频

### 🎨 专业特效系统
- **1700+特效资源** - 912种视频特效、468种滤镜、362种转场
- **轻微参数优化** - 12种参数类型智能调节，避免过度强烈效果
- **智能排除管理** - 可排除不喜欢的效果，个性化定制

### 📝 多语言字幕支持
- **智能编码检测** - 支持UTF-8、GBK、泰语等多种编码
- **时间戳修复** - 自动修复SRT格式错误，保持内容完整
- **多语言兼容** - 支持中英文混合、泰语、特殊字符

## 🚀 快速开始

### 📋 系统要求
- **操作系统**: Windows 10/11
- **Python版本**: 3.8+
- **剪映版本**: 剪映专业版

### ⚡ 启动方式

#### 🌐 Web界面（推荐）
```bash
python web_interface.py
```
浏览器访问：`http://localhost:5001`

#### 🖥️ 命令行界面
```bash
python interactive_automix.py
```

## 🌐 Web界面功能

### 🎨 主要特性
- **📊 实时统计** - 混剪进度、特效数量、覆盖率等详细统计
- **🎬 智能混剪** - 可视化产品选择、批量生成、进度监控
- **🚫 特效管理** - 搜索排除特效、分类管理、实时统计
- **🛡️ 防审核设置** - Pexels覆盖层配置、参数调整

## 💡 使用说明

### 🔄 基本流程
1. **启动Web界面** → 2. **选择产品型号** → 3. **设置参数** → 4. **开始混剪**

### 🎯 核心功能
- **智能特效排除** - 一键排除183个夸张特效，保持专业风格
- **实时搜索** - 输入关键词快速查找特效
- **批量生成** - 支持一次生成多个版本

## 📁 素材库结构

### 🗂️ 目录组织
```
📁 素材库根目录/
├── 📂 A83/                     # 产品型号文件夹
│   ├── 📂 摆拍/                 # 产品摆拍素材
│   ├── 📂 使用场景/             # 实际使用场景
│   ├── 📂 配音/                 # 解说音频文件
│   └── 📂 字幕/                 # SRT字幕文件
├── 📂 A84/                     # 其他产品型号
└── 📂 音效/                    # 环境音效库
```

### 📋 支持格式
- **视频**: MP4, AVI, MOV, MKV
- **音频**: MP3, WAV, AAC
- **字幕**: SRT（多编码支持）

## 🎯 技术特性

### 🎬 智能混剪
- **自动素材扫描** - 识别产品型号和场景分类
- **智能时长控制** - 精确控制30-40秒总时长
- **双轨道音频** - 解说100% + 背景10%音量

### 🛡️ 防审核技术
- **Pexels覆盖层** - 5%不透明度风景视频覆盖
- **多重备用机制** - 网络失败时自动使用本地备用

### 🎨 特效系统
- **1700+特效资源** - 912种特效、468种滤镜、362种转场
- **轻微参数优化** - 12种参数类型智能调节
- **智能排除** - 可排除183个夸张特效

### 📝 字幕处理
- **多编码支持** - UTF-8、GBK、泰语等编码智能检测
- **时间戳修复** - 自动修复SRT格式错误
- **内容保护** - 绝不修改字幕文本内容

## ⚙️ 配置说明

### 📊 主要参数
- **视频时长**: 30-40秒
- **特效概率**: 特效80%、滤镜90%、转场100%
- **防审核**: 5%不透明度Pexels覆盖层
- **音频配比**: 解说100% + 背景10%

### 🔑 Pexels API配置
1. 访问 https://www.pexels.com/api/ 获取免费API密钥
2. 替换配置文件中的API密钥（工具内置默认密钥可直接使用）

## 🎉 快速开始

```bash
# 克隆项目
git clone https://github.com/miludeerforest/JianYingProDraft.git

# 进入目录
cd JianYingProDraft

# 启动Web界面（推荐）
python web_interface.py
# 浏览器访问 http://localhost:5001

# 或启动命令行界面
python interactive_automix.py
```

## 📞 技术支持

- **GitHub Issues**: [提交问题](https://github.com/miludeerforest/JianYingProDraft/issues)
- **功能建议**: 欢迎提交新功能建议和改进意见

---

## 📋 更新日志

### 🆕 v2.1.1 - Web端统计优化版 (2025-07-26)

#### 🎯 混剪统计显示优化
- **📊 详细统计面板** - 新增混剪统计显示，包含素材数、特效数、覆盖率等
- **🔄 实时计数更新** - 支持类似终端的计数变化显示（如"15 → 16"）
- **📈 批量统计支持** - 批量混剪完成后正确显示统计信息
- **✨ 动画效果** - 添加统计变化的动画提示效果

#### 🐛 界面加载修复
- **⚡ 加载器优化** - 修复页面卡在加载界面的问题
- **🛡️ 备用机制** - 添加3秒强制隐藏的备用加载机制
- **🔧 错误处理** - 完善JavaScript错误处理和调试信息

#### 🧪 测试功能增强
- **🔬 测试页面** - 新增`/test`测试页面用于功能验证
- **🎮 模拟API** - 添加模拟混剪完成状态的测试接口
- **🌐 端口优化** - 支持多端口自动切换，解决端口占用问题

### 🎯 v2.2.0 - 界面优化版 (2025-07-24)
- **🔄 统一混剪界面** - 解决单个混剪与批量混剪功能重复问题
- **🎯 智能模式切换** - 根据生成数量自动切换单个/批量模式
- **📊 动态界面提示** - 实时显示当前模式和预期结果

### 🎨 v2.1.0 - 现代化界面版 (2025-07-23)
- **🎨 现代化设计系统** - 全新色彩系统，支持渐变色和多层次颜色
- **🚀 性能优化架构** - DOM缓存、事件委托、懒加载机制
- **📊 批量生成进度** - 修复进度计数不更新问题
- **🎯 用户体验提升** - 现代化加载器、悬停效果、动画过渡

### 🎉 v2.1.0 - 轻微特效优化版 (2025-07-05)
- **轻微特效系统** - 全面优化特效参数，避免过度强烈效果
- **智能参数调节** - 12种参数类型智能识别和调节
- **泰语编码支持** - 完整支持UTF-8、CP874、ISO-8859-11、TIS-620

### 🎯 历史版本
- **v2.0.0** - 防审核技术集成，完整的防审核技术系统
- **v1.6.2** - 泰语字幕编码修复，增强多语言字幕文件兼容性
