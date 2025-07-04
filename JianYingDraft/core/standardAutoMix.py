"""
标准化自动混剪核心 - 基于pyJianYingDraft标准API重构
参考功能清单.md中的标准用法
"""
import os
import random
import time
from typing import List, Dict, Any, Optional, Callable

# 导入pyJianYingDraft标准API
import sys
sys.path.append('.')
from pyJianYingDraft import (
    Script_file, Track_type, Video_segment, Audio_segment, Text_segment,
    Video_material, Audio_material,
    trange, SEC,
    Filter_type, Video_scene_effect_type, Transition_type,
    Text_style, Clip_settings,
    Effect_segment, Filter_segment
)

from JianYingDraft.core.configManager import AutoMixConfigManager
from JianYingDraft.core.materialScanner import MaterialScanner
from JianYingDraft.core.srtProcessor import SRTProcessor
from JianYingDraft.core.metadataManager import MetadataManager
from JianYingDraft.core.effectExclusionManager import EffectExclusionManager
from JianYingDraft.core.pexelsManager import PexelsManager


class StandardAutoMix:
    """
    标准化自动混剪类 - 基于pyJianYingDraft标准API
    """
    
    def __init__(self, draft_name: str):
        """初始化标准化自动混剪"""
        self.draft_name = draft_name
        self.config_manager = AutoMixConfigManager
        self.material_scanner = MaterialScanner()
        self.srt_processor = SRTProcessor()
        self.metadata_manager = MetadataManager()  # 初始化元数据管理器
        self.exclusion_manager = EffectExclusionManager()  # 初始化特效排除管理器
        self.pexels_manager = PexelsManager()  # 初始化Pexels管理器
        
        # 创建标准Script_file实例 - 9:16竖屏格式
        self.script = Script_file(1080, 1920)  # 宽度1080, 高度1920 (9:16)
        
        # 进度回调
        self.progress_callback: Optional[Callable[[str, float], None]] = None
        
        # 统计信息
        self.statistics = {
            'total_materials': 0,
            'selected_materials': 0,
            'applied_filters': 0,
            'applied_effects': 0,
            'applied_transitions': 0,
            'audio_tracks': 0,
            'subtitle_count': 0,
            'product_model': ''
        }
        
    def set_progress_callback(self, callback: Callable[[str, float], None]):
        """设置进度回调函数"""
        self.progress_callback = callback

    def _clean_enum_name(self, name: str) -> str:
        """清理枚举名称，移除特殊字符和空格"""
        import re
        # 移除特殊字符，只保留中文、英文、数字和下划线
        cleaned = re.sub(r'[^\w\u4e00-\u9fff]', '', name)
        # 移除开头的数字（Python标识符不能以数字开头）
        cleaned = re.sub(r'^\d+', '', cleaned)
        return cleaned

    def _filter_transitions(self, transitions):
        """过滤转场，排除弹幕类和不适合的转场特效"""
        # 定义要排除的转场关键词
        excluded_keywords = [
            '弹幕', 'danmu', '弹', '幕',
            '评论', '留言', '文字飞入', '字幕',
            '社交', '互动', '点赞', '关注'
        ]

        filtered_transitions = []
        for transition in transitions:
            transition_name = transition.name.lower()

            # 检查是否包含排除的关键词
            should_exclude = False
            for keyword in excluded_keywords:
                if keyword in transition_name:
                    should_exclude = True
                    break

            if not should_exclude:
                filtered_transitions.append(transition)

        print(f"  📊 转场过滤: 从{len(transitions)}个转场过滤到{len(filtered_transitions)}个（排除弹幕类）")
        return filtered_transitions
        
    def _update_progress(self, message: str, progress: float):
        """更新进度"""
        if self.progress_callback:
            self.progress_callback(message, progress)
            
    def auto_mix(self, target_duration: int = 35000000, product_model: str = None) -> Dict[str, Any]:
        """
        执行标准化自动混剪
        
        Args:
            target_duration: 目标时长（微秒）
            product_model: 产品型号
            
        Returns:
            Dict: 混剪结果
        """
        try:
            self._update_progress("开始标准化自动混剪", 0.0)
            
            # 1. 扫描素材
            self._update_progress("扫描产品素材库", 0.1)
            materials = self._scan_materials(product_model)
            
            # 2. 选择素材
            self._update_progress("智能选择素材", 0.2)
            selected_materials = self._select_materials(materials, target_duration)
            
            # 3. 创建轨道
            self._update_progress("创建轨道结构", 0.3)
            self._create_tracks()
            
            # 4. 添加视频片段
            self._update_progress("添加视频片段", 0.4)
            video_segments = self._add_video_segments(selected_materials['videos'], target_duration)

            # 4.5. 添加防审核覆盖层
            self._update_progress("添加防审核覆盖层", 0.45)
            self._add_anti_detection_overlay(target_duration)

            # 5. 添加转场
            self._update_progress("添加转场效果", 0.5)
            self._add_transitions(video_segments)
            
            # 6. 添加特效和滤镜
            self._update_progress("添加特效滤镜", 0.6)
            self._add_effects_and_filters(video_segments)
            
            # 7. 添加音频
            self._update_progress("添加音频轨道", 0.7)
            self._add_audio_tracks(selected_materials, target_duration)
            
            # 8. 添加字幕
            self._update_progress("添加字幕", 0.8)
            self._add_subtitles(selected_materials.get('subtitle_file'), target_duration)
            
            # 9. 保存草稿
            self._update_progress("保存草稿文件", 0.9)
            draft_path = self._save_draft()
            
            self._update_progress("标准化自动混剪完成", 1.0)
            
            return {
                'success': True,
                'draft_path': draft_path,
                'duration': target_duration,
                'statistics': self.statistics
            }
            
        except Exception as e:
            self._update_progress(f"混剪失败: {str(e)}", -1)
            return {
                'success': False,
                'error': str(e),
                'statistics': self.statistics
            }
            
    def _scan_materials(self, product_model: str = None) -> Dict[str, Any]:
        """扫描素材库"""
        material_path = self.config_manager.get_material_path()

        # 修复：使用正确的参数调用scan_product_materials
        materials = self.material_scanner.scan_product_materials(material_path, product_model)

        if not materials or not materials.get('videos'):
            raise ValueError("未找到视频素材")

        self.statistics['product_model'] = materials.get('product_model', 'Unknown')
        self.statistics['total_materials'] = len(materials.get('videos', []))

        return materials
        
    def _select_materials(self, materials: Dict[str, Any], target_duration: int) -> Dict[str, Any]:
        """智能选择素材"""
        videos = materials.get('videos', [])
        if not videos:
            raise ValueError("未找到视频素材")
            
        # 计算需要的视频数量（基于目标时长）
        avg_segment_duration = 4 * SEC  # 平均4秒每段
        target_video_count = max(3, min(10, target_duration // avg_segment_duration))
        
        # 智能选择视频（确保子文件夹覆盖）
        selected_videos = self._smart_select_videos(videos, target_video_count)
        self.statistics['selected_materials'] = len(selected_videos)
        
        # 选择音频
        narration_audio = self._select_narration_audio(materials.get('audios', []))
        background_audio = self._select_background_audio(materials.get('background_audios', []))
        
        # 选择字幕
        subtitle_file = self._select_subtitle_file(materials.get('subtitles', []))
        
        print(f"素材选择完成:")
        print(f"  视频: {len(selected_videos)}个")
        print(f"  解说音频: {'有' if narration_audio else '无'}")
        print(f"  背景音效: {'有' if background_audio else '无'}")
        print(f"  字幕文件: {'有' if subtitle_file else '无'}")
        
        return {
            'videos': selected_videos,
            'narration_audio': narration_audio,
            'background_audio': background_audio,
            'subtitle_file': subtitle_file
        }
        
    def _smart_select_videos(self, videos: List[Dict], target_count: int) -> List[Dict]:
        """智能选择视频，确保每个文件夹最多选择1个视频"""
        # 按文件夹分组（修复：使用正确的属性名folder_name）
        videos_by_folder = {}
        for video in videos:
            folder = video.get('folder_name', 'root')  # 修复：使用folder_name而不是folder
            if folder not in videos_by_folder:
                videos_by_folder[folder] = []
            videos_by_folder[folder].append(video)

        folders = list(videos_by_folder.keys())
        selected_videos = []
        used_folders = set()  # 记录已使用的文件夹

        print(f"检测到 {target_count} 个视频需求，将从 {len(folders)} 个文件夹选择")
        print(f"发现 {len(folders)} 个子文件夹: {folders}")

        # 策略：每个文件夹最多选择1个视频，确保内容多样性
        available_folders = folders.copy()
        random.shuffle(available_folders)  # 随机打乱文件夹顺序

        for folder in available_folders:
            if len(selected_videos) >= target_count:
                break
            if folder not in used_folders and videos_by_folder[folder]:
                video = random.choice(videos_by_folder[folder])
                selected_videos.append(video)
                used_folders.add(folder)
                print(f"  从文件夹 '{folder}' 选择视频: {os.path.basename(video['path'])}")

        # 如果文件夹数量少于需求数量，调整目标数量
        if len(selected_videos) < target_count:
            actual_count = len(selected_videos)
            print(f"  ⚠️  文件夹数量({len(folders)})少于需求数量({target_count})，实际选择{actual_count}个视频")
            print(f"  📊 每个文件夹最多选择1个视频，确保内容多样性")

        return selected_videos
        
    def _select_narration_audio(self, audios: List[Dict]) -> Optional[str]:
        """选择解说音频"""
        if not audios:
            return None
        # 优先选择包含"解说"关键词的音频
        for audio in audios:
            if '解说' in os.path.basename(audio['path']):
                return audio['path']
        # 否则随机选择
        return random.choice(audios)['path']
        
    def _select_background_audio(self, environment_audios: List[Dict]) -> Optional[str]:
        """选择背景音频"""
        if not environment_audios:
            return None
        return random.choice(environment_audios)['path']
        
    def _select_subtitle_file(self, subtitles: List[Dict]) -> Optional[str]:
        """选择字幕文件"""
        if not subtitles:
            return None
        return random.choice(subtitles)['path']

    def _create_tracks(self):
        """创建标准轨道结构"""
        # 轨道层级结构（从下到上）:
        # 0. 主视频轨道 (素材视频)
        # 1. 防审核覆盖层轨道 (Pexels视频，15%不透明度)
        # 特效和滤镜使用专门的轨道类型

        # 创建视频轨道
        self.script.add_track(Track_type.video, "main_video")        # 轨道0: 主视频
        self.script.add_track(Track_type.video, "overlay_layer")     # 轨道1: 防审核覆盖层

        # 创建音频轨道
        self.script.add_track(Track_type.audio, "narration")         # 解说音频
        self.script.add_track(Track_type.audio, "background")        # 背景音频

        # 创建文本轨道（字幕）
        self.script.add_track(Track_type.text, "subtitle")           # 字幕轨道

    def _add_video_segments(self, videos: List[Dict], target_duration: int) -> List[Video_segment]:
        """添加视频片段"""
        if not videos:
            return []

        # 计算每个片段的时长
        segment_durations = self._calculate_segment_durations(len(videos), target_duration)
        video_segments = []
        current_time = 0

        for i, (video_info, duration) in enumerate(zip(videos, segment_durations)):
            # 创建视频素材
            video_material = Video_material(video_info['path'])

            # 计算源时间范围（去掉前3秒）
            trim_start = self.config_manager.get_trim_start_duration()
            source_start = min(trim_start, video_material.duration - duration)
            source_timerange = trange(source_start, duration)

            # 创建目标时间范围
            target_timerange = trange(current_time, duration)

            # 创建视频片段，应用110%缩放和色彩调整（每10秒变化）
            clip_settings, color_adjustments = self._create_video_clip_settings(current_time)

            video_segment = Video_segment(
                video_material,
                target_timerange,
                source_timerange=source_timerange,
                clip_settings=clip_settings,
                volume=0.0  # 关键修复：视频轨道静音
            )

            # 添加色彩调整关键帧（在片段开始时设置）
            self._add_color_keyframes(video_segment, color_adjustments)

            # 添加到主视频轨道
            self.script.add_segment(video_segment, "main_video")
            video_segments.append(video_segment)

            current_time += duration
            print(f"  ✅ 添加视频片段 {i+1}: {os.path.basename(video_info['path'])}, 时长{duration/SEC:.1f}s")

        return video_segments

    def _calculate_segment_durations(self, video_count: int, target_duration: int) -> List[int]:
        """计算片段时长分配"""
        if video_count == 0:
            return []

        # 基础时长分配
        base_duration = target_duration // video_count
        durations = [base_duration] * video_count

        # 分配剩余时间
        remaining = target_duration - sum(durations)
        for i in range(remaining // 100000):  # 以0.1秒为单位分配
            durations[i % video_count] += 100000

        # 添加随机变化（±20%）
        for i in range(len(durations)):
            variation = random.uniform(0.8, 1.2)
            durations[i] = int(durations[i] * variation)

        # 确保最小时长
        min_duration = 2 * SEC
        durations = [max(d, min_duration) for d in durations]

        return durations

    def _create_video_clip_settings(self, current_time: int) -> tuple:
        """创建视频片段设置（110%缩放）和色彩调整参数（每10秒变化）"""
        # 获取缩放因子（目标110%）
        scale_factor = 1.1  # 固定110%，符合用户要求

        # 随机调整亮度和对比度（10-15范围）
        import random
        contrast = random.uniform(0.10, 0.15)  # 10%-15%对比度调整
        brightness = random.uniform(0.10, 0.15)  # 10%-15%亮度调整

        # 随机决定正负方向
        if random.random() < 0.5:
            contrast = -contrast
        if random.random() < 0.5:
            brightness = -brightness

        print(f"    🎨 时间{current_time//SEC:.1f}s: 对比度{contrast:+.2f}, 亮度{brightness:+.2f}")

        # 返回Clip_settings（只包含缩放）和色彩调整参数
        clip_settings = Clip_settings(
            scale_x=scale_factor,
            scale_y=scale_factor
        )

        color_adjustments = {
            "contrast": contrast,
            "brightness": brightness
        }

        return clip_settings, color_adjustments

    def _add_color_keyframes(self, video_segment: Video_segment, color_adjustments: Dict[str, float]):
        """为视频片段添加色彩调整关键帧"""
        from pyJianYingDraft import Keyframe_property

        contrast = color_adjustments["contrast"]
        brightness = color_adjustments["brightness"]

        # 在片段开始时设置对比度关键帧
        if contrast != 0.0:
            video_segment.add_keyframe(Keyframe_property.contrast, 0, contrast)
            print(f"      🎨 添加对比度关键帧: {contrast:+.2f}")

        # 在片段开始时设置亮度关键帧
        if brightness != 0.0:
            video_segment.add_keyframe(Keyframe_property.brightness, 0, brightness)
            print(f"      🎨 添加亮度关键帧: {brightness:+.2f}")

    def _add_transitions(self, video_segments: List[Video_segment]):
        """为视频片段添加转场效果（使用VIP资源，改进兼容性）"""
        if len(video_segments) < 2:
            return

        # 从排除管理器获取过滤后的转场（包括弹幕过滤和用户排除）
        available_transitions = self.exclusion_manager.get_filtered_transitions()

        if not available_transitions:
            print("  ⚠️  没有可用的转场效果")
            return

        # 为每个片段（除最后一个）添加转场
        for i in range(len(video_segments) - 1):
            current_segment = video_segments[i]  # 前一个片段

            # 尝试多次选择，直到找到兼容的转场
            max_attempts = 10
            for attempt in range(max_attempts):
                transition_meta = random.choice(available_transitions)

                # 清理转场名称，移除特殊字符
                clean_name = self._clean_enum_name(transition_meta.name)
                transition_type = getattr(Transition_type, clean_name, None)

                if transition_type is not None:
                    break
            else:
                # 如果所有尝试都失败，使用备用转场
                fallback_transitions = ['闪白', '模糊', '上移', '下移']
                for fallback_name in fallback_transitions:
                    transition_type = getattr(Transition_type, fallback_name, None)
                    if transition_type is not None:
                        clean_name = fallback_name
                        break
                else:
                    print(f"  ⚠️  无法找到兼容的转场，跳过片段{i+1}")
                    continue

            try:
                # 转场添加在"前一个"视频片段上（参考你提供的示例）
                current_segment.add_transition(transition_type)  # 不指定duration，使用默认值

                # 确保转场素材添加到素材库
                if current_segment.transition and current_segment.transition not in self.script.materials.transitions:
                    self.script.materials.transitions.append(current_segment.transition)

                self.statistics['applied_transitions'] += 1
                print(f"  ✅ 添加转场: {transition_type.name} (片段{i+1}→片段{i+2})")

            except Exception as e:
                print(f"  ❌ 转场添加失败: {transition_type.name} - {str(e)}")

    def _add_effects_and_filters(self, video_segments: List[Video_segment]):
        """添加特效和滤镜到独立轨道（使用VIP资源，改进兼容性）"""
        # 从排除管理器获取过滤后的特效和滤镜（包括用户排除）
        available_effects = self.exclusion_manager.get_filtered_effects()
        available_filters = self.exclusion_manager.get_filtered_filters()

        if not available_effects:
            print("  ⚠️  没有可用的特效")
            return

        if not available_filters:
            print("  ⚠️  没有可用的滤镜")
            return

        # 创建一个特效轨道（使用正确的Track_type.effect）
        effect_track_name = "effect_track"
        self.script.add_track(Track_type.effect, effect_track_name)

        # 创建一个滤镜轨道（使用正确的Track_type.filter）
        filter_track_name = "filter_track"
        self.script.add_track(Track_type.filter, filter_track_name)

        for segment in video_segments:
            # 添加滤镜（100%概率 - 确保每个片段都有滤镜）
            # 尝试多次选择，直到找到兼容的滤镜
            filter_added = False
            max_attempts = 10
            for _ in range(max_attempts):
                filter_meta = random.choice(available_filters)
                # 清理滤镜名称，移除特殊字符
                clean_name = self._clean_enum_name(filter_meta.name)
                filter_type = getattr(Filter_type, clean_name, None)

                if filter_type is not None:
                    # 从配置管理器获取滤镜强度范围
                    min_intensity, max_intensity = self.config_manager.get_filter_intensity_range()
                    intensity = random.randint(min_intensity, max_intensity)
                    try:
                        # 使用script.add_filter()方法添加滤镜到滤镜轨道
                        self.script.add_filter(
                            filter_type,
                            segment.target_timerange,  # 与视频片段相同的时间范围
                            track_name=filter_track_name,
                            intensity=intensity  # 直接传入强度值，API会自动转换
                        )

                        self.statistics['applied_filters'] += 1
                        print(f"  ✅ 添加滤镜: {clean_name}, 强度{intensity}")
                        filter_added = True
                        break
                    except Exception as e:
                        print(f"  ❌ 滤镜添加失败: {clean_name} - {str(e)}")
                        continue

            # 如果所有尝试都失败，使用备用滤镜
            if not filter_added:
                fallback_filters = ['中性', '亮肤', '云暖', '乐游']
                for fallback_name in fallback_filters:
                    filter_type = getattr(Filter_type, fallback_name, None)
                    if filter_type is not None:
                        # 从配置管理器获取滤镜强度范围
                        min_intensity, max_intensity = self.config_manager.get_filter_intensity_range()
                        intensity = random.randint(min_intensity, max_intensity)
                        try:
                            self.script.add_filter(
                                filter_type,
                                segment.target_timerange,
                                track_name=filter_track_name,
                                intensity=intensity
                            )
                            self.statistics['applied_filters'] += 1
                            print(f"  ✅ 添加备用滤镜: {fallback_name}, 强度{intensity}")
                            break
                        except Exception as e:
                            continue

            # 添加特效（100%概率 - 确保每个片段都有特效）
            # 尝试多次选择，直到找到兼容的特效
            effect_added = False
            for _ in range(max_attempts):
                effect_meta = random.choice(available_effects)
                # 清理特效名称，移除特殊字符
                clean_name = self._clean_enum_name(effect_meta.name)
                effect_type = getattr(Video_scene_effect_type, clean_name, None)

                if effect_type is not None:
                    try:
                        # 使用script.add_effect()方法添加特效到特效轨道
                        self.script.add_effect(
                            effect_type,
                            segment.target_timerange,  # 与视频片段相同的时间范围
                            track_name=effect_track_name,
                            params=None  # 使用默认参数
                        )

                        self.statistics['applied_effects'] += 1
                        print(f"  ✅ 添加特效: {clean_name}")
                        effect_added = True
                        break
                    except Exception as e:
                        print(f"  ❌ 特效添加失败: {clean_name} - {str(e)}")
                        continue

            # 如果所有尝试都失败，使用备用特效
            if not effect_added:
                fallback_effects = ['X_Signal', 'VCR', 'DV录制框', 'RGB描边']
                for fallback_name in fallback_effects:
                    effect_type = getattr(Video_scene_effect_type, fallback_name, None)
                    if effect_type is not None:
                        try:
                            self.script.add_effect(
                                effect_type,
                                segment.target_timerange,
                                track_name=effect_track_name,
                                params=None
                            )
                            self.statistics['applied_effects'] += 1
                            print(f"  ✅ 添加备用特效: {fallback_name}")
                            break
                        except Exception as e:
                            continue

        print(f"  📊 特效轨道: {self.statistics['applied_effects']}个特效在同一轨道")
        print(f"  📊 滤镜轨道: {self.statistics['applied_filters']}个滤镜在同一轨道")

    def _add_audio_tracks(self, materials: Dict[str, Any], target_duration: int):
        """添加音频轨道"""
        # 添加解说音频
        if materials.get('narration_audio'):
            narration_volume = self.config_manager.get_audio_volumes()[0]  # 100%
            self._add_audio_segment(
                materials['narration_audio'],
                "narration",
                target_duration,
                narration_volume
            )
            self.statistics['audio_tracks'] += 1

        # 添加背景音频
        if materials.get('background_audio'):
            background_volume = self.config_manager.get_audio_volumes()[1]  # 10%
            self._add_audio_segment(
                materials['background_audio'],
                "background",
                target_duration,
                background_volume
            )
            self.statistics['audio_tracks'] += 1

    def _add_audio_segment(self, audio_path: str, track_name: str, duration: int, volume: float):
        """添加音频片段"""
        # 创建音频素材
        audio_material = Audio_material(audio_path)

        # 检查音频时长，如果不够则循环播放
        if audio_material.duration < duration:
            # 音频不够长，需要循环播放或截取部分
            actual_duration = min(duration, audio_material.duration)
            source_timerange = trange(0, actual_duration)
        else:
            # 音频足够长，截取需要的部分
            source_timerange = trange(0, duration)

        # 创建音频片段
        audio_segment = Audio_segment(
            audio_material,
            trange(0, duration),  # 目标时间范围
            source_timerange=source_timerange,  # 源时间范围
            volume=volume  # 直接设置音量，参考demo
        )

        # 添加到指定音频轨道
        self.script.add_segment(audio_segment, track_name)

        print(f"  ✅ 添加音频轨道 {track_name}: 时长{duration/SEC:.1f}s, 音量{volume:.1%}")

    def _add_subtitles(self, subtitle_file: str, target_duration: int):
        """添加字幕（包含格式自动修复）"""
        if not subtitle_file or not os.path.exists(subtitle_file):
            return

        try:
            # 先进行SRT格式自动修复
            print(f"  📝 准备导入字幕文件: {os.path.basename(subtitle_file)}")

            # 使用SRT处理器进行格式检查和修复
            fixed_subtitle_file = self._fix_and_prepare_srt(subtitle_file)

            # 使用pyJianYingDraft标准API导入修复后的SRT字幕
            self.script.import_srt(
                fixed_subtitle_file,
                track_name="subtitle",
                text_style=Text_style(
                    size=5.0,
                    color=(1.0, 1.0, 1.0),  # 白色
                    align=1  # 居中对齐
                ),
                clip_settings=Clip_settings(
                    transform_y=-0.8  # 底部位置
                )
            )

            # 统计字幕数量（简单估算）
            self.statistics['subtitle_count'] = target_duration // (3 * SEC)  # 假设每3秒一条字幕

            print(f"  ✅ 导入字幕文件: {os.path.basename(subtitle_file)}")

        except Exception as e:
            print(f"  ❌ 字幕导入失败: {str(e)}")

    def _fix_and_prepare_srt(self, subtitle_file: str) -> str:
        """修复并准备SRT字幕文件"""
        try:
            # 使用SRT处理器解析和修复字幕
            subtitles = self.srt_processor.parse_srt_file(subtitle_file)

            if not subtitles:
                print(f"  ⚠️  字幕文件为空或格式错误: {subtitle_file}")
                return subtitle_file

            # 检查是否需要创建修复后的文件
            original_file_size = os.path.getsize(subtitle_file)

            # 创建临时修复文件
            import tempfile
            temp_dir = tempfile.gettempdir()
            temp_filename = f"fixed_{os.path.basename(subtitle_file)}"
            fixed_file_path = os.path.join(temp_dir, temp_filename)

            # 重新生成标准格式的SRT内容
            fixed_content = self._generate_standard_srt(subtitles)

            # 写入修复后的文件
            with open(fixed_file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)

            # 比较文件大小，判断是否有修复
            fixed_file_size = os.path.getsize(fixed_file_path)
            if abs(fixed_file_size - original_file_size) > 10:  # 允许10字节的差异
                print(f"  🔧 字幕已修复并保存到临时文件")
                return fixed_file_path
            else:
                # 如果没有显著变化，删除临时文件，使用原文件
                os.remove(fixed_file_path)
                return subtitle_file

        except Exception as e:
            print(f"  ⚠️  字幕修复失败，使用原文件: {str(e)}")
            return subtitle_file

    def _generate_standard_srt(self, subtitles: List[Dict]) -> str:
        """生成标准格式的SRT内容"""
        srt_lines = []

        for i, subtitle in enumerate(subtitles, 1):
            # 序号
            srt_lines.append(str(i))

            # 时间戳
            start_time = self._microseconds_to_srt_time(subtitle['start_time'])
            end_time = self._microseconds_to_srt_time(subtitle['end_time'])
            srt_lines.append(f"{start_time} --> {end_time}")

            # 字幕文本
            srt_lines.append(subtitle['text'])

            # 空行分隔（除了最后一个）
            if i < len(subtitles):
                srt_lines.append('')

        return '\n'.join(srt_lines)

    def _microseconds_to_srt_time(self, microseconds: int) -> str:
        """将微秒转换为SRT时间格式"""
        total_seconds = microseconds // 1000000
        milliseconds = (microseconds % 1000000) // 1000

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    def _get_local_fallback_video(self) -> Optional[str]:
        """获取本地备用视频作为防审核覆盖层"""
        try:
            # 检查常见的本地视频目录
            fallback_dirs = [
                os.path.join(os.path.dirname(__file__), "..", "..", "fallback_videos"),
                os.path.join(self.config_manager.get_material_library_path(), "fallback_videos"),
                "fallback_videos"
            ]

            # 支持的视频格式
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv']

            for fallback_dir in fallback_dirs:
                if os.path.exists(fallback_dir):
                    for filename in os.listdir(fallback_dir):
                        if any(filename.lower().endswith(ext) for ext in video_extensions):
                            video_path = os.path.join(fallback_dir, filename)
                            print(f"  📁 使用本地备用视频: {filename}")
                            return video_path

            print("  ⚠️  未找到本地备用视频")
            return None

        except Exception as e:
            print(f"  ❌ 获取本地备用视频失败: {str(e)}")
            return None

    def _create_adaptive_overlay_segment(self, overlay_material: Video_material, target_duration: int) -> Video_segment:
        """
        创建自适应的防审核覆盖层片段，智能调整时长以匹配目标时长

        Args:
            overlay_material: 覆盖层视频素材
            target_duration: 目标时长（微秒）

        Returns:
            Video_segment: 调整后的视频片段
        """
        material_duration = overlay_material.duration

        # 获取不透明度设置
        opacity = self.config_manager.get_pexels_overlay_opacity()

        # 创建Clip_settings，设置不透明度
        from pyJianYingDraft import Clip_settings
        clip_settings = Clip_settings(alpha=opacity)

        if target_duration <= material_duration:
            # 目标时长不超过素材时长，直接截取
            print(f"  ✂️  截取覆盖层视频: 0s - {target_duration/1000000:.1f}s")
            overlay_segment = Video_segment(
                material=overlay_material,
                target_timerange=trange(0, target_duration),
                source_timerange=trange(0, target_duration),
                clip_settings=clip_settings,
                volume=0.0  # 静音处理
            )
        else:
            # 目标时长超过素材时长，使用慢速播放来拉伸时长
            print(f"  🐌 拉伸覆盖层视频: {material_duration/1000000:.1f}s → {target_duration/1000000:.1f}s")

            # 计算播放速度（慢速播放）
            speed_factor = material_duration / target_duration
            print(f"  ⚡ 播放速度: {speed_factor:.2f}x (慢速播放)")

            # 使用慢速播放来匹配目标时长
            overlay_segment = Video_segment(
                material=overlay_material,
                target_timerange=trange(0, target_duration),
                source_timerange=trange(0, material_duration),
                speed=speed_factor,
                clip_settings=clip_settings,
                volume=0.0  # 静音处理
            )

        print(f"  🌫️  设置不透明度: {opacity:.1%}")
        return overlay_segment

    def _add_anti_detection_overlay(self, target_duration: int):
        """添加防审核覆盖层"""
        # 检查是否启用防审核覆盖层
        if not self.config_manager.is_pexels_overlay_enabled():
            print("  ⏭️  防审核覆盖层已禁用，跳过")
            return

        try:
            print("  🛡️  准备添加防审核覆盖层...")

            # 获取防审核覆盖视频
            overlay_video_path = self.pexels_manager.get_anti_detection_overlay_video()

            if not overlay_video_path:
                print("  ⚠️  无法获取Pexels覆盖视频，尝试使用本地备用视频...")
                overlay_video_path = self._get_local_fallback_video()

                if not overlay_video_path:
                    print("  ⚠️  无法获取防审核覆盖视频，跳过此步骤")
                    return

            print(f"  📁 使用覆盖视频: {os.path.basename(overlay_video_path)}")

            # 创建视频素材
            overlay_material = Video_material(overlay_video_path)

            print(f"  🔇 覆盖层音频将在片段中静音处理")
            print(f"  📊 覆盖层视频时长: {overlay_material.duration/1000000:.1f}s, 目标时长: {target_duration/1000000:.1f}s")

            # 智能调整覆盖层时长以匹配目标时长（包含不透明度设置）
            overlay_segment = self._create_adaptive_overlay_segment(overlay_material, target_duration)

            # 添加到防审核覆盖轨道（在主视频轨道之上）
            self.script.add_segment(overlay_segment, "overlay_layer")

            # 获取不透明度用于日志显示
            opacity = self.config_manager.get_pexels_overlay_opacity()
            print(f"  ✅ 防审核覆盖层已添加 (不透明度: {opacity:.1%})")

            # 更新统计信息
            self.statistics['anti_detection_overlay'] = {
                'enabled': True,
                'opacity': opacity,
                'video_file': os.path.basename(overlay_video_path),
                'audio_muted': True  # 记录音频已静音
            }

        except Exception as e:
            print(f"  ❌ 添加防审核覆盖层失败: {str(e)}")
            # 防审核覆盖层失败不影响整体流程
            self.statistics['anti_detection_overlay'] = {
                'enabled': False,
                'error': str(e)
            }

    def _save_draft(self) -> str:
        """保存剪映草稿核心文件（简化版）"""
        import json

        # 获取草稿输出路径
        draft_output_path = self.config_manager.get_draft_output_path()

        # 创建草稿文件夹
        timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        draft_folder_name = f"{self.draft_name}_{timestamp}"
        draft_folder_path = os.path.join(draft_output_path, draft_folder_name)

        if not os.path.exists(draft_folder_path):
            os.makedirs(draft_folder_path)

        # 1. 保存draft_content.json（时间线素材信息）
        draft_content_path = os.path.join(draft_folder_path, "draft_content.json")
        self.script.dump(draft_content_path)

        # 2. 创建draft_meta_info.json（素材库信息）
        self._create_draft_meta_info(draft_folder_path)

        print(f"  ✅ 核心草稿文件已保存: {draft_folder_path}")
        print(f"  📄 draft_content.json - 时间线素材信息")
        print(f"  📄 draft_meta_info.json - 素材库信息")
        print(f"  🔄 其他文件将在剪映打开时自动补全")

        return draft_folder_path

    def _create_draft_meta_info(self, draft_folder_path: str):
        """创建draft_meta_info.json（素材库信息）"""
        import json

        # 根据实现原理，只需要创建draft_meta_info.json
        # 这个文件记录素材信息，会出现在剪映左侧的素材库中
        meta_info = {
            "draft_id": os.path.basename(draft_folder_path),
            "draft_name": self.draft_name,
            "create_time": int(time.time() * 1000000),  # 微秒时间戳
            "update_time": int(time.time() * 1000000),
            "duration": 35000000,  # 35秒
            "width": 1080,
            "height": 1920,
            "fps": 30,
            "version": "5.9.0",
            "materials": []  # 素材库中的素材信息
        }

        meta_file_path = os.path.join(draft_folder_path, "draft_meta_info.json")
        with open(meta_file_path, 'w', encoding='utf-8') as f:
            json.dump(meta_info, f, ensure_ascii=False, indent=2)

        print(f"  ✅ 素材库信息已创建: draft_meta_info.json")
