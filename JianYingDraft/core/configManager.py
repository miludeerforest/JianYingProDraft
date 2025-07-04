"""
 * @file   : configManager.py
 * @time   : 16:30
 * @date   : 2024/12/19
 * @mail   : 9727005@qq.com
 * @creator: ShanDong Xiedali
 * @company: HiLand & RainyTop
"""
import os
import configparser
from typing import Any, Dict


class SimpleConfigHelper:
    """简单的配置文件助手类"""

    _config = None
    _config_file = "_projectConfig.ini"

    @classmethod
    def _load_config(cls):
        """加载配置文件"""
        if cls._config is None:
            cls._config = configparser.ConfigParser()
            if os.path.exists(cls._config_file):
                cls._config.read(cls._config_file, encoding='utf-8')

    @classmethod
    def get_item(cls, section: str, key: str, default_value: Any = None) -> Any:
        """获取配置项"""
        cls._load_config()
        try:
            if cls._config.has_section(section) and cls._config.has_option(section, key):
                value = cls._config.get(section, key)
                # 尝试转换为适当的类型
                if isinstance(default_value, bool):
                    return value.lower() in ('true', '1', 'yes', 'on')
                elif isinstance(default_value, int):
                    return int(value)
                elif isinstance(default_value, float):
                    return float(value)
                else:
                    return value
            return default_value
        except Exception:
            return default_value

    @classmethod
    def set_item(cls, section: str, key: str, value: Any) -> bool:
        """设置配置项"""
        cls._load_config()
        try:
            if not cls._config.has_section(section):
                cls._config.add_section(section)
            cls._config.set(section, key, str(value))
            with open(cls._config_file, 'w', encoding='utf-8') as f:
                cls._config.write(f)
            return True
        except Exception:
            return False


class AutoMixConfigManager:
    """
    自动混剪配置管理器
    提供对自动混剪相关配置项的便捷访问和验证
    """
    
    # 配置节名称
    SECTION_NAME = "JianYingDraft.automix"
    
    # 默认配置值
    DEFAULT_CONFIG = {
        'material_path': r'F:\Windows_data\Videos\B日期分类\素材',
        'draft_output_path': r'C:\Users\JDL-XXX\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft',
        'video_duration_min': 30000000,  # 30秒
        'video_duration_max': 40000000,  # 40秒
        'effect_probability': 0.8,
        'filter_probability': 0.9,
        'transition_probability': 1.0,
        'narration_volume': 1.0,
        'background_volume': 0.1,
        'batch_count': 5,
        'use_vip_effects': False,
        'trim_start_duration': 3000000,  # 3秒
        'video_scale_factor': 1.05,
        'contrast_range_min': 0.9,
        'contrast_range_max': 1.1,
        'brightness_range_min': 0.95,
        'brightness_range_max': 1.05,
        'min_video_duration': 5000000,   # 5秒
        'max_video_duration': 300000000, # 300秒
        'filter_intensity_min': 10,      # 滤镜强度最小值 (10%) - 轻微效果
        'filter_intensity_max': 25,      # 滤镜强度最大值 (25%) - 轻微效果
        'pexels_api_key': 'rwDQTKgarldHRe2MUQGbtUB95E59p7csmYSSIis1qRxOqVpHjAOadPTD',  # Pexels API密钥 (内置默认)
        'pexels_overlay_opacity': 0.05,     # 防审核覆盖层不透明度 (5%)
        'enable_pexels_overlay': True,      # 是否启用Pexels防审核覆盖层

        # 新增防审核技术配置（强制执行模式）
        'flip_probability': 1.0,            # 镜像翻转概率 (100% - 强制执行)
        'enable_speed_variation': True,     # 启用变速处理
        'speed_variation_min': 0.9,         # 最小变速比例
        'speed_variation_max': 1.1,         # 最大变速比例
        'enable_canvas_adjustment': False,  # 启用画幅调整（暂时禁用）
        'canvas_ratio': '9:16',             # 默认画幅比例

        # 模糊背景防审核技术（强制执行模式）
        'enable_blur_background': True,     # 启用模糊背景
        'blur_background_probability': 1.0, # 模糊背景应用概率 (100% - 强制执行)
        'foreground_scale': 0.8,            # 前景视频缩放比例 (80%)
        'background_blur_intensity': 0.5,   # 背景模糊强度 (50%)
        'background_scale': 1.2,            # 背景放大比例 (120%)

        # 抽帧/补帧防审核技术（强制执行模式）
        'enable_frame_manipulation': True,  # 启用抽帧/补帧（强制执行）
        'frame_drop_probability': 1.0,     # 抽帧概率 (100% - 强制执行)
        'frame_drop_interval': 5.0,        # 抽帧间隔（秒）
        'max_frame_drops_per_segment': 3   # 每个片段最大抽帧次数
    }
    
    @classmethod
    def get_material_path(cls) -> str:
        """获取素材库路径"""
        return cls._get_config_value('material_path', cls.DEFAULT_CONFIG['material_path'])
    
    @classmethod
    def get_draft_output_path(cls) -> str:
        """获取草稿输出路径"""
        return cls._get_config_value('draft_output_path', cls.DEFAULT_CONFIG['draft_output_path'])
    
    @classmethod
    def get_video_duration_range(cls) -> tuple[int, int]:
        """获取视频时长范围（微秒）"""
        min_duration = cls._get_config_value('video_duration_min', cls.DEFAULT_CONFIG['video_duration_min'])
        max_duration = cls._get_config_value('video_duration_max', cls.DEFAULT_CONFIG['video_duration_max'])
        return int(min_duration), int(max_duration)

    @classmethod
    def get_video_duration_min(cls) -> int:
        """获取视频最小时长（微秒）"""
        return int(cls._get_config_value('video_duration_min', cls.DEFAULT_CONFIG['video_duration_min']))

    @classmethod
    def get_video_duration_max(cls) -> int:
        """获取视频最大时长（微秒）"""
        return int(cls._get_config_value('video_duration_max', cls.DEFAULT_CONFIG['video_duration_max']))
    
    @classmethod
    def get_effect_probability(cls) -> float:
        """获取特效应用概率"""
        return float(cls._get_config_value('effect_probability', cls.DEFAULT_CONFIG['effect_probability']))
    
    @classmethod
    def get_filter_probability(cls) -> float:
        """获取滤镜应用概率"""
        return float(cls._get_config_value('filter_probability', cls.DEFAULT_CONFIG['filter_probability']))
    
    @classmethod
    def get_transition_probability(cls) -> float:
        """获取转场应用概率"""
        return float(cls._get_config_value('transition_probability', cls.DEFAULT_CONFIG['transition_probability']))
    
    @classmethod
    def get_audio_volumes(cls) -> tuple[float, float]:
        """获取音频音量设置（解说音量，背景音量）"""
        narration_volume = float(cls._get_config_value('narration_volume', cls.DEFAULT_CONFIG['narration_volume']))
        background_volume = float(cls._get_config_value('background_volume', cls.DEFAULT_CONFIG['background_volume']))
        return narration_volume, background_volume

    @classmethod
    def get_narration_volume(cls) -> float:
        """获取解说音量"""
        return float(cls._get_config_value('narration_volume', cls.DEFAULT_CONFIG['narration_volume']))

    @classmethod
    def get_background_volume(cls) -> float:
        """获取背景音量"""
        return float(cls._get_config_value('background_volume', cls.DEFAULT_CONFIG['background_volume']))
    
    @classmethod
    def get_batch_count(cls) -> int:
        """获取批量生成数量"""
        return int(cls._get_config_value('batch_count', cls.DEFAULT_CONFIG['batch_count']))
    
    @classmethod
    def get_use_vip_effects(cls) -> bool:
        """获取是否使用VIP特效"""
        value = cls._get_config_value('use_vip_effects', 'false')  # 明确使用字符串默认值
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)
    
    @classmethod
    def get_trim_start_duration(cls) -> int:
        """获取视频片段去掉前几秒的时长（微秒）"""
        return int(cls._get_config_value('trim_start_duration', cls.DEFAULT_CONFIG['trim_start_duration']))
    
    @classmethod
    def get_video_scale_factor(cls) -> float:
        """获取视频画面缩放比例"""
        return float(cls._get_config_value('video_scale_factor', cls.DEFAULT_CONFIG['video_scale_factor']))
    
    @classmethod
    def get_color_adjustment_ranges(cls) -> tuple[tuple[float, float], tuple[float, float]]:
        """获取色彩调整范围（对比度范围，亮度范围）"""
        contrast_min = float(cls._get_config_value('contrast_range_min', cls.DEFAULT_CONFIG['contrast_range_min']))
        contrast_max = float(cls._get_config_value('contrast_range_max', cls.DEFAULT_CONFIG['contrast_range_max']))
        brightness_min = float(cls._get_config_value('brightness_range_min', cls.DEFAULT_CONFIG['brightness_range_min']))
        brightness_max = float(cls._get_config_value('brightness_range_max', cls.DEFAULT_CONFIG['brightness_range_max']))
        return (contrast_min, contrast_max), (brightness_min, brightness_max)
    
    @classmethod
    def get_video_duration_filter_range(cls) -> tuple[int, int]:
        """获取视频时长过滤范围（微秒）"""
        min_duration = int(cls._get_config_value('min_video_duration', cls.DEFAULT_CONFIG['min_video_duration']))
        max_duration = int(cls._get_config_value('max_video_duration', cls.DEFAULT_CONFIG['max_video_duration']))
        return min_duration, max_duration

    @classmethod
    def get_filter_intensity_range(cls) -> tuple[int, int]:
        """获取滤镜强度范围（百分比）"""
        min_intensity = int(cls._get_config_value('filter_intensity_min', cls.DEFAULT_CONFIG['filter_intensity_min']))
        max_intensity = int(cls._get_config_value('filter_intensity_max', cls.DEFAULT_CONFIG['filter_intensity_max']))
        return min_intensity, max_intensity
    
    @classmethod
    def get_all_config(cls) -> Dict[str, Any]:
        """获取所有自动混剪配置"""
        config = {}
        for key, default_value in cls.DEFAULT_CONFIG.items():
            config[key] = cls._get_config_value(key, default_value)
        return config
    
    @classmethod
    def validate_config(cls) -> tuple[bool, list[str]]:
        """
        验证配置的有效性
        
        Returns:
            tuple[bool, list[str]]: (是否有效, 错误信息列表)
        """
        errors = []
        
        # 验证路径
        material_path = cls.get_material_path()
        if not os.path.exists(material_path):
            errors.append(f"素材库路径不存在: {material_path}")
        
        draft_output_path = cls.get_draft_output_path()
        if not os.path.exists(os.path.dirname(draft_output_path)):
            errors.append(f"草稿输出路径的父目录不存在: {os.path.dirname(draft_output_path)}")
        
        # 验证时长范围
        min_duration, max_duration = cls.get_video_duration_range()
        if min_duration >= max_duration:
            errors.append(f"视频最小时长({min_duration})应小于最大时长({max_duration})")
        
        if min_duration < 1000000:  # 小于1秒
            errors.append(f"视频最小时长({min_duration})过短，建议至少1秒(1000000微秒)")
        
        # 验证概率值
        for prob_name, prob_value in [
            ('特效概率', cls.get_effect_probability()),
            ('滤镜概率', cls.get_filter_probability()),
            ('转场概率', cls.get_transition_probability())
        ]:
            if not 0.0 <= prob_value <= 1.0:
                errors.append(f"{prob_name}({prob_value})应在0.0-1.0范围内")
        
        # 验证音量值
        narration_volume, background_volume = cls.get_audio_volumes()
        if not 0.0 <= narration_volume <= 1.0:
            errors.append(f"解说音量({narration_volume})应在0.0-1.0范围内")
        if not 0.0 <= background_volume <= 1.0:
            errors.append(f"背景音量({background_volume})应在0.0-1.0范围内")
        
        # 验证批量数量
        batch_count = cls.get_batch_count()
        if batch_count < 1:
            errors.append(f"批量生成数量({batch_count})应大于0")
        if batch_count > 100:
            errors.append(f"批量生成数量({batch_count})过大，建议不超过100")
        
        # 验证缩放比例
        scale_factor = cls.get_video_scale_factor()
        if not 0.5 <= scale_factor <= 2.0:
            errors.append(f"视频缩放比例({scale_factor})应在0.5-2.0范围内")
        
        # 验证色彩调整范围
        (contrast_min, contrast_max), (brightness_min, brightness_max) = cls.get_color_adjustment_ranges()
        if contrast_min >= contrast_max:
            errors.append(f"对比度最小值({contrast_min})应小于最大值({contrast_max})")
        if brightness_min >= brightness_max:
            errors.append(f"亮度最小值({brightness_min})应小于最大值({brightness_max})")
        
        return len(errors) == 0, errors
    
    @classmethod
    def _get_config_value(cls, key: str, default_value: Any) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键名
            default_value: 默认值
            
        Returns:
            配置值
        """
        try:
            return SimpleConfigHelper.get_item(cls.SECTION_NAME, key, default_value)
        except Exception as e:
            print(f"读取配置项 {cls.SECTION_NAME}.{key} 失败: {str(e)}")
            return default_value

    @classmethod
    def _set_config_value(cls, key: str, value: Any) -> bool:
        """
        设置配置值

        Args:
            key: 配置键名
            value: 配置值

        Returns:
            bool: 设置是否成功
        """
        try:
            result = SimpleConfigHelper.set_item(cls.SECTION_NAME, key, value)
            if result:
                print(f"设置配置项 {cls.SECTION_NAME}.{key} = {value}")
            return result
        except Exception as e:
            print(f"设置配置项 {cls.SECTION_NAME}.{key} 失败: {str(e)}")
            return False

    @classmethod
    def print_config_summary(cls):
        """打印配置摘要"""
        print("=== 自动混剪配置摘要 ===")
        print(f"素材库路径: {cls.get_material_path()}")
        print(f"草稿输出路径: {cls.get_draft_output_path()}")
        
        min_duration, max_duration = cls.get_video_duration_range()
        print(f"视频时长范围: {min_duration/1000000:.1f}s - {max_duration/1000000:.1f}s")
        
        print(f"特效概率: {cls.get_effect_probability():.1%}")
        print(f"滤镜概率: {cls.get_filter_probability():.1%}")
        print(f"转场概率: {cls.get_transition_probability():.1%}")
        
        narration_vol, background_vol = cls.get_audio_volumes()
        print(f"音频音量: 解说{narration_vol:.1%}, 背景{background_vol:.1%}")

        min_intensity, max_intensity = cls.get_filter_intensity_range()
        print(f"滤镜强度: {min_intensity}% - {max_intensity}%")

        print(f"批量生成数量: {cls.get_batch_count()}")
        print(f"使用VIP特效: {'是' if cls.get_use_vip_effects() else '否'}")
        print(f"视频缩放比例: {cls.get_video_scale_factor():.2f}")
        print(f"Pexels防审核层: {'启用' if cls.is_pexels_overlay_enabled() else '禁用'}")
        print(f"覆盖层不透明度: {cls.get_pexels_overlay_opacity():.1%} (极轻微覆盖)")
        print("========================")

    @classmethod
    def get_pexels_api_key(cls) -> str:
        """获取Pexels API密钥"""
        return cls._get_config_value('pexels_api_key', cls.DEFAULT_CONFIG['pexels_api_key'])

    @classmethod
    def set_pexels_api_key(cls, api_key: str) -> bool:
        """设置Pexels API密钥"""
        return cls._set_config_value('pexels_api_key', api_key)

    @classmethod
    def get_pexels_overlay_opacity(cls) -> float:
        """获取Pexels防审核覆盖层不透明度"""
        return cls._get_config_value('pexels_overlay_opacity', cls.DEFAULT_CONFIG['pexels_overlay_opacity'])

    @classmethod
    def set_pexels_overlay_opacity(cls, opacity: float) -> bool:
        """设置Pexels防审核覆盖层不透明度"""
        return cls._set_config_value('pexels_overlay_opacity', opacity)

    @classmethod
    def is_pexels_overlay_enabled(cls) -> bool:
        """检查是否启用Pexels防审核覆盖层"""
        return cls._get_config_value('enable_pexels_overlay', cls.DEFAULT_CONFIG['enable_pexels_overlay'])

    @classmethod
    def set_pexels_overlay_enabled(cls, enabled: bool) -> bool:
        """设置是否启用Pexels防审核覆盖层"""
        return cls._set_config_value('enable_pexels_overlay', enabled)

    # 新增防审核技术配置方法
    @classmethod
    def get_flip_probability(cls) -> float:
        """获取镜像翻转概率"""
        return float(cls._get_config_value('flip_probability', cls.DEFAULT_CONFIG['flip_probability']))

    @classmethod
    def set_flip_probability(cls, probability: float) -> bool:
        """设置镜像翻转概率"""
        return cls._set_config_value('flip_probability', probability)

    @classmethod
    def is_speed_variation_enabled(cls) -> bool:
        """检查是否启用变速处理"""
        return cls._get_config_value('enable_speed_variation', cls.DEFAULT_CONFIG['enable_speed_variation'])

    @classmethod
    def set_speed_variation_enabled(cls, enabled: bool) -> bool:
        """设置是否启用变速处理"""
        return cls._set_config_value('enable_speed_variation', enabled)

    @classmethod
    def get_speed_variation_range(cls) -> tuple[float, float]:
        """获取变速范围"""
        min_speed = float(cls._get_config_value('speed_variation_min', cls.DEFAULT_CONFIG['speed_variation_min']))
        max_speed = float(cls._get_config_value('speed_variation_max', cls.DEFAULT_CONFIG['speed_variation_max']))
        return min_speed, max_speed

    @classmethod
    def set_speed_variation_range(cls, min_speed: float, max_speed: float) -> bool:
        """设置变速范围"""
        success1 = cls._set_config_value('speed_variation_min', min_speed)
        success2 = cls._set_config_value('speed_variation_max', max_speed)
        return success1 and success2

    @classmethod
    def is_canvas_adjustment_enabled(cls) -> bool:
        """检查是否启用画幅调整"""
        return cls._get_config_value('enable_canvas_adjustment', cls.DEFAULT_CONFIG['enable_canvas_adjustment'])

    @classmethod
    def set_canvas_adjustment_enabled(cls, enabled: bool) -> bool:
        """设置是否启用画幅调整"""
        return cls._set_config_value('enable_canvas_adjustment', enabled)

    @classmethod
    def get_canvas_ratio(cls) -> str:
        """获取画幅比例"""
        return cls._get_config_value('canvas_ratio', cls.DEFAULT_CONFIG['canvas_ratio'])

    @classmethod
    def set_canvas_ratio(cls, ratio: str) -> bool:
        """设置画幅比例"""
        return cls._set_config_value('canvas_ratio', ratio)

    # 模糊背景防审核技术配置方法
    @classmethod
    def is_blur_background_enabled(cls) -> bool:
        """检查是否启用模糊背景"""
        return cls._get_config_value('enable_blur_background', cls.DEFAULT_CONFIG['enable_blur_background'])

    @classmethod
    def set_blur_background_enabled(cls, enabled: bool) -> bool:
        """设置是否启用模糊背景"""
        return cls._set_config_value('enable_blur_background', enabled)

    @classmethod
    def get_blur_background_probability(cls) -> float:
        """获取模糊背景应用概率"""
        return float(cls._get_config_value('blur_background_probability', cls.DEFAULT_CONFIG['blur_background_probability']))

    @classmethod
    def set_blur_background_probability(cls, probability: float) -> bool:
        """设置模糊背景应用概率"""
        return cls._set_config_value('blur_background_probability', probability)

    @classmethod
    def get_foreground_scale(cls) -> float:
        """获取前景视频缩放比例"""
        return float(cls._get_config_value('foreground_scale', cls.DEFAULT_CONFIG['foreground_scale']))

    @classmethod
    def set_foreground_scale(cls, scale: float) -> bool:
        """设置前景视频缩放比例"""
        return cls._set_config_value('foreground_scale', scale)

    @classmethod
    def get_background_blur_intensity(cls) -> float:
        """获取背景模糊强度"""
        return float(cls._get_config_value('background_blur_intensity', cls.DEFAULT_CONFIG['background_blur_intensity']))

    @classmethod
    def set_background_blur_intensity(cls, intensity: float) -> bool:
        """设置背景模糊强度"""
        return cls._set_config_value('background_blur_intensity', intensity)

    @classmethod
    def get_background_scale(cls) -> float:
        """获取背景放大比例"""
        return float(cls._get_config_value('background_scale', cls.DEFAULT_CONFIG['background_scale']))

    @classmethod
    def set_background_scale(cls, scale: float) -> bool:
        """设置背景放大比例"""
        return cls._set_config_value('background_scale', scale)

    # 抽帧/补帧防审核技术配置方法
    @classmethod
    def is_frame_manipulation_enabled(cls) -> bool:
        """检查是否启用抽帧/补帧"""
        return cls._get_config_value('enable_frame_manipulation', cls.DEFAULT_CONFIG['enable_frame_manipulation'])

    @classmethod
    def set_frame_manipulation_enabled(cls, enabled: bool) -> bool:
        """设置是否启用抽帧/补帧"""
        return cls._set_config_value('enable_frame_manipulation', enabled)

    @classmethod
    def get_frame_drop_probability(cls) -> float:
        """获取抽帧概率"""
        return float(cls._get_config_value('frame_drop_probability', cls.DEFAULT_CONFIG['frame_drop_probability']))

    @classmethod
    def set_frame_drop_probability(cls, probability: float) -> bool:
        """设置抽帧概率"""
        return cls._set_config_value('frame_drop_probability', probability)

    @classmethod
    def get_frame_drop_interval(cls) -> float:
        """获取抽帧间隔（秒）"""
        return float(cls._get_config_value('frame_drop_interval', cls.DEFAULT_CONFIG['frame_drop_interval']))

    @classmethod
    def set_frame_drop_interval(cls, interval: float) -> bool:
        """设置抽帧间隔（秒）"""
        return cls._set_config_value('frame_drop_interval', interval)

    @classmethod
    def get_max_frame_drops_per_segment(cls) -> int:
        """获取每个片段最大抽帧次数"""
        return int(cls._get_config_value('max_frame_drops_per_segment', cls.DEFAULT_CONFIG['max_frame_drops_per_segment']))

    @classmethod
    def set_max_frame_drops_per_segment(cls, max_drops: int) -> bool:
        """设置每个片段最大抽帧次数"""
        return cls._set_config_value('max_frame_drops_per_segment', max_drops)


# 为了向后兼容，提供一个简化的别名
ConfigManager = AutoMixConfigManager
