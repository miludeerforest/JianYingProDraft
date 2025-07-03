# JianYingDraft.PY

## 项目简介

项目来源于 `https://github.com/xiaoyiv/JianYingProDraft`
因为原始库旷日持久没有更新，所以自己动手丰衣足食，基于此项目进行二次开发。
虽说是二次开发，但跟原始项目相比早就“肝胆楚越也”，因此也就没有对原始项目进行fork。

## 新增功能

### 1. 抖音媒体素材添加
   抖音媒体素材的添加 :例子可以看api.py 方便直接调用

### 2. 自动混剪系统 🎬
   基于AI的智能视频自动混剪系统，支持：
   - **智能素材扫描**：自动扫描素材库，识别视频、音频、字幕文件
   - **产品型号选择**：支持指定产品型号（如A83）或随机选择
   - **随机效果应用**：基于1742个元数据项智能选择滤镜、转场、特效
   - **双轨音频处理**：解说音频100%音量，背景音频10%音量
   - **SRT字幕集成**：自动解析和添加SRT字幕文件
   - **时长精确控制**：确保生成30-40秒的标准短视频
   - **视频预处理**：去掉前3秒、画面扩大5%、随机色彩调整
   - **命令行接口**：提供用户友好的CLI工具，支持批量生成

#### 自动混剪使用方法

**基础使用：**
```bash
# 生成5个混剪视频
python autoMixCLI.py --count 5

# 指定产品型号A83
python autoMixCLI.py --product A83 --count 3

# 预览模式（查看将要使用的素材）
python autoMixCLI.py --preview --product A83
```

**高级使用：**
```bash
# 使用VIP特效，自定义时长
python autoMixCLI.py --product A83 --duration-min 35 --duration-max 45 --vip-effects

# 使用配置文件
python autoMixCLI.py --config automix_config.json

# 创建示例配置文件
python autoMixCLI.py --create-config
```

**参数说明：**
- `--count`: 生成视频数量
- `--product`: 产品型号（如A83、A82等）
- `--duration-min/max`: 时长范围（秒）
- `--vip-effects`: 使用VIP特效
- `--preview`: 预览模式
- `--debug`: 调试模式
- `--quiet`: 静默模式

## 剪映的草稿原理说明

1. 实现原理 : 剪映的草稿文件是 `json` 的形式存储的。我们只需要创建`draft_content.json`和`draft_mate_info.json`
   （其他文件则会在打开剪映软件后会自动补全）。两个文件内都记录了素材信息，其中：`draft_mate_info.json`
   内的素材信息会出现在剪映左侧的素材库中；`draft_content.json`的素材信息会出现在剪映下侧的时间线上。
2. 添加一个媒体素材到剪映软件，剪映会将其数据记录进入“草稿元数据库” 和 “草稿内容库”（包括素材部分和轨道部分）

## 本软件的实现原理说明

1. `add_media` 会识别媒体类型，加入到对应轨道。
2. 当没有视频轨道时，创建音频轨道会先创建视频轨道。

## 使用步骤与说明

1. 使用前先修改配置文件`_projectConfig.ini`内，剪映草稿文件夹路径为你本地正确的路径。
   ```shell
   drafts_root=Z:/jianying/Data/JianyingPro Drafts
   ```
2. 根据自己的需求修改`main.py`内的代码。运行`main.py`。
