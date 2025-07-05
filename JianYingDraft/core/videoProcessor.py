"""
 * @file   : videoProcessor.py
 * @time   : 18:45
 * @date   : 2024/12/19
 * @mail   : 9727005@qq.com
 * @creator: ShanDong Xiedali
 * @company: HiLand & RainyTop
"""
import random
from typing import Dict, Any, Optional, Tuple
from JianYingDraft.core.configManager import AutoMixConfigManager


class VideoProcessor:
    """
    视频预处理器
    实现视频的预处理功能，包括去掉前3秒、画面扩大5%、随机调整对比度和亮度
    """
    
    def __init__(self):
        """初始化视频预处理器"""
        self.config_manager = AutoMixConfigManager
    
    def trim_start(self, media_info: Dict[str, Any], duration: Optional[int] = None) -> Dict[str, Any]:
        """
        设置视频去掉前几秒的参数
        
        Args:
            media_info: 媒体信息字典
            duration: 去掉的时长（微秒），如果为None则使用配置文件中的值
            
        Returns:
            Dict[str, Any]: 更新后的媒体信息
        """
        if duration is None:
            duration = self.config_manager.get_trim_start_duration()
        
        # 确保去掉的时长不超过视频总时长
        video_duration = media_info.get('duration', 0)
        if duration >= video_duration:
            print(f"警告：去掉时长({duration/1000000:.1f}s)大于等于视频总时长({video_duration/1000000:.1f}s)，设置为0")
            duration = 0
        
        # 设置start_in_media参数
        media_info['start_in_media'] = duration
        
        # 更新实际可用时长
        if 'duration' in media_info:
            media_info['available_duration'] = video_duration - duration
        
        return media_info
    
    def scale_video(self, segment: Dict[str, Any], scale_factor: Optional[float] = None) -> Dict[str, Any]:
        """
        设置视频画面缩放比例
        
        Args:
            segment: 视频片段字典
            scale_factor: 缩放比例，如果为None则使用配置文件中的值
            
        Returns:
            Dict[str, Any]: 更新后的片段信息
        """
        if scale_factor is None:
            scale_factor = self.config_manager.get_video_scale_factor()
        
        # 确保缩放比例在合理范围内
        if not 0.1 <= scale_factor <= 5.0:
            print(f"警告：缩放比例({scale_factor})超出合理范围(0.1-5.0)，设置为1.05")
            scale_factor = 1.05
        
        # 设置clip.scale属性
        if 'clip' not in segment:
            segment['clip'] = {
                "alpha": 1.0,
                "flip": {"horizontal": False, "vertical": False},
                "rotation": 0.0,
                "scale": {"x": 1.0, "y": 1.0},
                "transform": {"x": 0.0, "y": 0.0}
            }
        
        segment['clip']['scale'] = {"x": scale_factor, "y": scale_factor}
        
        return segment

    def convert_to_vertical_format(self, segment: Dict[str, Any], media_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        将视频转换为9:16竖屏格式

        Args:
            segment: 视频片段字典
            media_info: 视频媒体信息

        Returns:
            Dict[str, Any]: 更新后的片段信息
        """
        # 获取原始视频尺寸
        original_width = media_info.get('width', 1920)
        original_height = media_info.get('height', 1080)

        # 目标竖屏尺寸 (9:16)
        target_width = 1080
        target_height = 1920

        # 修复缩放计算：目标是110%左右，而不是187%
        # 对于常见的1920x1080视频转9:16，我们使用更合理的缩放
        if original_width >= original_height:
            # 横屏视频：以高度为准，适当放大
            base_scale = target_height / original_height * 0.6  # 降低基础缩放
        else:
            # 竖屏视频：以宽度为准
            base_scale = target_width / original_width

        # 确保缩放在合理范围内（1.0-1.2之间）
        scale_factor = max(1.0, min(1.2, base_scale))

        # 确保clip结构存在
        if 'clip' not in segment:
            segment['clip'] = {
                "alpha": 1.0,
                "flip": {"horizontal": False, "vertical": False},
                "rotation": 0.0,
                "scale": {"x": 1.0, "y": 1.0},
                "transform": {"x": 0.0, "y": 0.0}
            }

        # 设置缩放
        segment['clip']['scale'] = {"x": scale_factor, "y": scale_factor}

        # 计算居中位置
        # 缩放后的尺寸
        scaled_width = original_width * scale_factor
        scaled_height = original_height * scale_factor

        # 计算偏移量使视频居中
        offset_x = (target_width - scaled_width) / 2
        offset_y = (target_height - scaled_height) / 2

        # 设置位置偏移
        segment['clip']['transform'] = {"x": offset_x, "y": offset_y}

        # 记录转换信息
        segment['_vertical_conversion'] = {
            'original_size': {'width': original_width, 'height': original_height},
            'target_size': {'width': target_width, 'height': target_height},
            'scale_factor': scale_factor,
            'offset': {'x': offset_x, 'y': offset_y}
        }

        return segment

    def apply_random_flip(self, segment: Dict[str, Any]) -> Dict[str, Any]:
        """
        随机应用镜像翻转（防审核技术）

        Args:
            segment: 视频片段字典

        Returns:
            Dict[str, Any]: 更新后的片段信息
        """
        import random

        # 获取翻转概率配置（如果是100%则强制执行）
        flip_probability = self.config_manager.get_flip_probability()

        if flip_probability >= 1.0 or random.random() < flip_probability:
            # 确保clip结构存在
            if 'clip' not in segment:
                segment['clip'] = {
                    "alpha": 1.0,
                    "flip": {"horizontal": False, "vertical": False},
                    "rotation": 0.0,
                    "scale": {"x": 1.0, "y": 1.0},
                    "transform": {"x": 0.0, "y": 0.0}
                }

            # 应用水平翻转（最有效的防审核手段）
            segment['clip']['flip']['horizontal'] = True
            print(f"  🔄 应用镜像翻转（防审核 - {'强制执行' if flip_probability >= 1.0 else f'{flip_probability:.1%}概率'}）")

        return segment

    def apply_random_speed(self, segment: Dict[str, Any]) -> Dict[str, Any]:
        """
        应用随机变速处理（防审核技术）

        Args:
            segment: 视频片段字典

        Returns:
            Dict[str, Any]: 更新后的片段信息
        """
        import random

        # 检查是否启用变速处理
        if not self.config_manager.is_speed_variation_enabled():
            return segment

        # 获取变速范围配置
        speed_range = self.config_manager.get_speed_variation_range()
        min_speed, max_speed = speed_range

        # 生成随机变速（避免1.0，确保有变化）
        speed_options = []
        current = min_speed
        while current <= max_speed:
            if abs(current - 1.0) > 0.05:  # 避免接近1.0的速度
                speed_options.append(current)
            current += 0.05

        if speed_options:
            speed = random.choice(speed_options)

            # 创建Speed对象
            from pyJianYingDraft.segment import Speed
            speed_obj = Speed(speed)

            # 添加到片段
            if 'speed' not in segment:
                segment['speed'] = speed_obj.export_json()
            else:
                segment['speed']['speed'] = speed

            print(f"  ⚡ 应用变速: {speed:.2f}x（防审核）")

        return segment

    def create_blur_background_effect(self, segment: Dict[str, Any], media_info: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """
        创建模糊背景效果（防审核技术）

        Args:
            segment: 原始视频片段字典
            media_info: 媒体信息字典

        Returns:
            tuple: (背景片段, 前景片段)
        """
        import random
        import copy

        # 检查是否启用模糊背景
        if not self.config_manager.is_blur_background_enabled():
            return None, segment

        # 检查概率（如果是100%则强制执行）
        blur_probability = self.config_manager.get_blur_background_probability()
        if blur_probability < 1.0 and random.random() > blur_probability:
            return None, segment

        print(f"  🌫️  创建模糊背景效果（防审核 - {'强制执行' if blur_probability >= 1.0 else f'{blur_probability:.1%}概率'}）")

        # 获取配置参数
        foreground_scale = self.config_manager.get_foreground_scale()
        background_scale = self.config_manager.get_background_scale()
        blur_intensity = self.config_manager.get_background_blur_intensity()

        # 创建背景片段（复制原片段）
        background_segment = copy.deepcopy(segment)
        background_media = copy.deepcopy(media_info)

        # 设置背景片段属性
        background_segment['id'] = f"{segment['id']}_background"

        # 背景：放大并模糊
        if 'clip' not in background_segment:
            background_segment['clip'] = {
                "alpha": 1.0,
                "flip": {"horizontal": False, "vertical": False},
                "rotation": 0.0,
                "scale": {"x": 1.0, "y": 1.0},
                "transform": {"x": 0.0, "y": 0.0}
            }

        # 设置背景缩放
        background_segment['clip']['scale']['x'] = background_scale
        background_segment['clip']['scale']['y'] = background_scale

        # 添加模糊滤镜到背景
        if 'filters' not in background_segment:
            background_segment['filters'] = []

        # 创建模糊滤镜
        blur_filter = {
            "id": f"blur_filter_{segment['id']}",
            "type": "blur",
            "intensity": blur_intensity,
            "platform": "mobile"
        }
        background_segment['filters'].append(blur_filter)

        # 创建前景片段（缩小的主视频）
        foreground_segment = copy.deepcopy(segment)
        foreground_media = copy.deepcopy(media_info)

        # 设置前景片段属性
        foreground_segment['id'] = f"{segment['id']}_foreground"

        # 前景：缩小并居中
        if 'clip' not in foreground_segment:
            foreground_segment['clip'] = {
                "alpha": 1.0,
                "flip": {"horizontal": False, "vertical": False},
                "rotation": 0.0,
                "scale": {"x": 1.0, "y": 1.0},
                "transform": {"x": 0.0, "y": 0.0}
            }

        # 设置前景缩放
        foreground_segment['clip']['scale']['x'] = foreground_scale
        foreground_segment['clip']['scale']['y'] = foreground_scale

        print(f"    📐 背景放大: {background_scale:.1f}x, 前景缩放: {foreground_scale:.1f}x")
        print(f"    🌫️  模糊强度: {blur_intensity:.1%}")

        return (background_segment, background_media), (foreground_segment, foreground_media)

    def apply_frame_manipulation(self, segment: Dict[str, Any], media_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        应用抽帧/补帧处理（实验性防审核技术）

        Args:
            segment: 视频片段字典
            media_info: 媒体信息字典

        Returns:
            Dict[str, Any]: 更新后的片段信息
        """
        import random

        # 检查是否启用抽帧/补帧
        if not self.config_manager.is_frame_manipulation_enabled():
            return segment

        # 检查概率（如果是100%则强制执行）
        frame_drop_prob = self.config_manager.get_frame_drop_probability()
        if frame_drop_prob < 1.0 and random.random() > frame_drop_prob:
            return segment

        print(f"  🎞️  应用抽帧处理（实验性防审核 - {'强制执行' if frame_drop_prob >= 1.0 else f'{frame_drop_prob:.1%}概率'}）")

        # 获取配置参数
        drop_interval = self.config_manager.get_frame_drop_interval()
        max_drops = self.config_manager.get_max_frame_drops_per_segment()

        # 获取视频时长（微秒）
        video_duration = media_info.get('duration', 0)
        duration_seconds = video_duration / 1000000

        if duration_seconds < drop_interval * 2:
            print(f"    ⚠️  视频时长过短，跳过抽帧处理")
            return segment

        # 计算可能的抽帧点
        possible_drops = int(duration_seconds / drop_interval)
        actual_drops = min(possible_drops, max_drops)

        if actual_drops <= 0:
            return segment

        # 生成随机抽帧点（避开开头和结尾）
        drop_points = []
        start_time = drop_interval
        end_time = duration_seconds - drop_interval

        for i in range(actual_drops):
            # 在可用时间范围内随机选择抽帧点
            if start_time < end_time:
                drop_time = random.uniform(start_time, end_time)
                drop_points.append(drop_time)
                # 更新下一个抽帧点的最小时间
                start_time = drop_time + drop_interval

        if drop_points:
            # 创建分割点信息（这里只是标记，实际分割需要在更高层实现）
            if 'frame_drops' not in segment:
                segment['frame_drops'] = []

            for drop_time in drop_points:
                drop_info = {
                    'time': drop_time,
                    'duration': 0.1,  # 抽掉0.1秒
                    'type': 'frame_drop'
                }
                segment['frame_drops'].append(drop_info)

            print(f"    🎞️  计划抽帧点: {len(drop_points)}个")
            for i, drop_time in enumerate(drop_points, 1):
                print(f"      {i}. {drop_time:.1f}s处抽帧0.1s")

        return segment

    def adjust_color_randomly(self, segment: Dict[str, Any]) -> Dict[str, Any]:
        """
        随机调整视频的对比度和亮度
        
        Args:
            segment: 视频片段字典
            
        Returns:
            Dict[str, Any]: 更新后的片段信息
        """
        # 获取色彩调整范围
        (contrast_min, contrast_max), (brightness_min, brightness_max) = self.config_manager.get_color_adjustment_ranges()
        
        # 随机生成对比度和亮度值
        contrast_value = random.uniform(contrast_min, contrast_max)
        brightness_value = random.uniform(brightness_min, brightness_max)
        
        # 启用色彩调整功能
        segment['enable_color_curves'] = True
        segment['enable_color_wheels'] = True
        segment['enable_adjust'] = True
        
        # 设置HDR设置（包含亮度调整）
        if 'hdr_settings' not in segment:
            segment['hdr_settings'] = {"intensity": 1.0, "mode": 1, "nits": 1000}
        
        # 调整亮度（通过HDR intensity）
        segment['hdr_settings']['intensity'] = brightness_value
        
        # 添加色彩调整信息到segment（用于后续处理）
        segment['_color_adjustments'] = {
            'contrast': contrast_value,
            'brightness': brightness_value,
            'contrast_range': (contrast_min, contrast_max),
            'brightness_range': (brightness_min, brightness_max)
        }
        
        return segment
    
    def process_video_segment(self, video_info: Dict[str, Any], segment_duration: int) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        综合处理单个视频片段
        
        Args:
            video_info: 视频信息字典
            segment_duration: 片段时长（微秒）
            
        Returns:
            Tuple[Dict[str, Any], Dict[str, Any]]: (处理后的媒体信息, 处理后的片段信息)
        """
        try:
            # 1. 处理视频裁剪（去掉前3秒）
            processed_media_info = self.trim_start(video_info.copy())
            
            # 2. 创建基础片段信息
            segment_info = {
                "cartoon": False,
                "clip": {
                    "alpha": 1.0,
                    "flip": {"horizontal": False, "vertical": False},
                    "rotation": 0.0,
                    "scale": {"x": 1.0, "y": 1.0},
                    "transform": {"x": 0.0, "y": 0.0}
                },
                "common_keyframes": [],
                "enable_adjust": True,
                "enable_color_curves": True,
                "enable_color_wheels": True,
                "enable_lut": True,
                "enable_smart_color_adjust": False,
                "extra_material_refs": [],
                "group_id": "",
                "hdr_settings": {"intensity": 1.0, "mode": 1, "nits": 1000},
                "intensifies_audio": False,
                "is_placeholder": False,
                "is_tone_modify": False,
                "keyframe_refs": [],
                "last_nonzero_volume": 1.0,
                "material_id": "",
                "render_index": 0,
                "reverse": False,
                "speed": 1.0,
                "template_id": "",
                "template_scene": "default",
                "track_attribute": 0,
                "track_render_index": 0,
                "uniform_scale": {"on": True, "value": 1.0},
                "visible": True,
                "volume": 1.0
            }
            
            # 3. 设置时间范围
            start_in_media = processed_media_info.get('start_in_media', 0)
            available_duration = processed_media_info.get('available_duration', segment_duration)
            
            # 确保片段时长不超过可用时长
            actual_duration = min(segment_duration, available_duration)
            
            segment_info['source_timerange'] = {
                "duration": actual_duration,
                "start": start_in_media
            }
            segment_info['target_timerange'] = {
                "duration": actual_duration,
                "start": 0
            }
            
            # 4. 转换为9:16竖屏格式
            segment_info = self.convert_to_vertical_format(segment_info, processed_media_info)

            # 5. 应用画面缩放（修复：目标110%左右）
            # 获取额外的缩放因子（默认5%放大），但要确保最终结果合理
            extra_scale = self.config_manager.get_video_scale_factor()
            if 'clip' in segment_info and 'scale' in segment_info['clip']:
                current_scale = segment_info['clip']['scale']['x']
                # 修复：确保最终缩放在105%-115%范围内
                final_scale = current_scale * extra_scale
                # 如果最终缩放过大，调整到合理范围
                if final_scale > 1.15:
                    final_scale = 1.1  # 目标110%
                elif final_scale < 1.05:
                    final_scale = 1.05  # 最小105%

                segment_info['clip']['scale'] = {
                    "x": final_scale,
                    "y": final_scale
                }

            # 6. 应用随机色彩调整
            segment_info = self.adjust_color_randomly(segment_info)

            # 7. 应用防审核技术
            segment_info = self.apply_random_flip(segment_info)
            segment_info = self.apply_random_speed(segment_info)
            segment_info = self.apply_frame_manipulation(segment_info, processed_media_info)

            return processed_media_info, segment_info
            
        except Exception as e:
            print(f"处理视频片段时出错: {str(e)}")
            # 返回原始信息作为备用
            return video_info, {}
    
    def batch_process_videos(self, video_list: list, segment_durations: list) -> list:
        """
        批量处理多个视频片段
        
        Args:
            video_list: 视频信息列表
            segment_durations: 对应的片段时长列表（微秒）
            
        Returns:
            list: 处理结果列表，每个元素包含(媒体信息, 片段信息)
        """
        if len(video_list) != len(segment_durations):
            raise ValueError("视频列表和时长列表长度不匹配")
        
        results = []
        for i, (video_info, duration) in enumerate(zip(video_list, segment_durations)):
            try:
                media_info, segment_info = self.process_video_segment(video_info, duration)
                results.append({
                    'index': i,
                    'media_info': media_info,
                    'segment_info': segment_info,
                    'success': True,
                    'error': None
                })
            except Exception as e:
                print(f"处理第{i+1}个视频时出错: {str(e)}")
                results.append({
                    'index': i,
                    'media_info': video_info,
                    'segment_info': {},
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def validate_video_info(self, video_info: Dict[str, Any]) -> Tuple[bool, list]:
        """
        验证视频信息的有效性
        
        Args:
            video_info: 视频信息字典
            
        Returns:
            Tuple[bool, list]: (是否有效, 错误信息列表)
        """
        errors = []
        
        # 检查必要字段
        required_fields = ['path', 'duration']
        for field in required_fields:
            if field not in video_info:
                errors.append(f"缺少必要字段: {field}")
        
        # 检查时长
        duration = video_info.get('duration', 0)
        if duration <= 0:
            errors.append(f"视频时长无效: {duration}")
        
        # 检查文件路径
        import os
        path = video_info.get('path', '')
        if not os.path.exists(path):
            errors.append(f"视频文件不存在: {path}")
        
        return len(errors) == 0, errors
    
    def get_processing_summary(self, processed_results: list) -> Dict[str, Any]:
        """
        获取批量处理的摘要信息
        
        Args:
            processed_results: 批量处理结果列表
            
        Returns:
            Dict[str, Any]: 摘要信息
        """
        total_count = len(processed_results)
        success_count = sum(1 for result in processed_results if result.get('success', False))
        error_count = total_count - success_count
        
        # 统计色彩调整信息
        color_adjustments = []
        for result in processed_results:
            if result.get('success', False):
                segment_info = result.get('segment_info', {})
                if '_color_adjustments' in segment_info:
                    color_adjustments.append(segment_info['_color_adjustments'])
        
        return {
            'total_videos': total_count,
            'success_count': success_count,
            'error_count': error_count,
            'success_rate': success_count / total_count if total_count > 0 else 0,
            'color_adjustments': color_adjustments,
            'average_contrast': sum(adj['contrast'] for adj in color_adjustments) / len(color_adjustments) if color_adjustments else 0,
            'average_brightness': sum(adj['brightness'] for adj in color_adjustments) / len(color_adjustments) if color_adjustments else 0
        }
    
    def print_processing_summary(self, processed_results: list):
        """打印处理摘要"""
        summary = self.get_processing_summary(processed_results)
        
        print("=== 视频预处理摘要 ===")
        print(f"总视频数: {summary['total_videos']}")
        print(f"成功处理: {summary['success_count']}")
        print(f"处理失败: {summary['error_count']}")
        print(f"成功率: {summary['success_rate']:.1%}")
        
        if summary['color_adjustments']:
            print(f"平均对比度调整: {summary['average_contrast']:.2f}")
            print(f"平均亮度调整: {summary['average_brightness']:.2f}")
        
        print("=====================")
