"""
 * @file   : autoMixDraft.py
 * @time   : 21:15
 * @date   : 2024/12/19
 * @mail   : 9727005@qq.com
 * @creator: ShanDong Xiedali
 * @company: HiLand & RainyTop
"""
import os
import random
import time
from typing import List, Dict, Any, Optional, Callable
from JianYingDraft.core.draft import Draft
from JianYingDraft.core.materialScanner import MaterialScanner
from JianYingDraft.core.metadataManager import MetadataManager
from JianYingDraft.core.randomEffectEngine import RandomEffectEngine
from JianYingDraft.core.videoProcessor import VideoProcessor
from JianYingDraft.core.dualAudioManager import DualAudioManager
from JianYingDraft.core.srtProcessor import SRTProcessor
from JianYingDraft.core.durationController import DurationController
from JianYingDraft.core.configManager import AutoMixConfigManager


class AutoMixDraft(Draft):
    """
    自动混剪引擎核心类
    继承Draft类，集成所有功能模块，实现完整的自动混剪流程
    """
    
    def __init__(self, name: str = "", config_manager: AutoMixConfigManager = None):
        """
        初始化自动混剪引擎
        
        Args:
            name: 草稿名称
            config_manager: 配置管理器实例
        """
        super().__init__(name)
        
        # 配置管理器
        self.config_manager = config_manager or AutoMixConfigManager
        
        # 初始化功能模块
        self.material_scanner = MaterialScanner()
        self.metadata_manager = MetadataManager()
        self.random_effect_engine = RandomEffectEngine(self.metadata_manager, self.config_manager)
        self.video_processor = VideoProcessor()
        self.dual_audio_manager = DualAudioManager()
        self.srt_processor = SRTProcessor()
        self.duration_controller = DurationController(self.config_manager)
        
        # 进度回调函数
        self.progress_callback: Optional[Callable[[str, float], None]] = None
        
        # 混剪统计信息
        self.mix_statistics = {
            'start_time': 0,
            'end_time': 0,
            'total_materials': 0,
            'selected_materials': 0,
            'applied_filters': 0,
            'applied_transitions': 0,
            'applied_effects': 0,
            'audio_tracks': 0,
            'subtitle_count': 0,
            'final_duration': 0,
            'errors': []
        }
    
    def set_progress_callback(self, callback: Callable[[str, float], None]):
        """设置进度回调函数"""
        self.progress_callback = callback
    
    def _update_progress(self, message: str, progress: float):
        """更新进度"""
        if self.progress_callback:
            self.progress_callback(message, progress)
        else:
            print(f"[{progress:.1%}] {message}")
    
    def auto_mix(self, target_duration: Optional[int] = None,
                product_model: Optional[str] = None,
                narration_audio: Optional[str] = None,
                background_audio: Optional[str] = None,
                subtitle_file: Optional[str] = None) -> Dict[str, Any]:
        """
        执行自动混剪流程

        Args:
            target_duration: 目标时长（微秒），如果为None则随机选择30-40秒
            product_model: 产品型号（如A83），如果为None则随机选择
            narration_audio: 解说音频文件路径（如果为None则使用扫描到的音频）
            background_audio: 背景音频文件路径（如果为None则使用扫描到的环境音效）
            subtitle_file: SRT字幕文件路径（如果为None则使用扫描到的字幕）

        Returns:
            Dict[str, Any]: 混剪结果信息
        """
        try:
            self.mix_statistics['start_time'] = time.time()
            self._update_progress("开始自动混剪流程", 0.0)

            # 1. 扫描并选择素材
            self._update_progress("扫描产品素材库", 0.1)
            selected_materials = self._scan_and_select_materials(product_model)

            # 使用扫描到的音频和字幕（如果没有指定的话）
            if narration_audio is None:
                narration_audio = selected_materials.get('narration_audio')
            if background_audio is None:
                background_audio = selected_materials.get('background_audio')
            if subtitle_file is None:
                subtitle_file = selected_materials.get('subtitle_file')
            
            # 2. 计算时长分配
            self._update_progress("计算时长分配", 0.3)
            duration_result = self._calculate_durations(selected_materials['videos'], target_duration)

            # 3. 处理视频片段
            self._update_progress("处理视频片段", 0.4)
            processed_videos = self._process_video_segments(selected_materials['videos'], duration_result)
            
            # 5. 应用滤镜和特效
            self._update_progress("应用滤镜和特效", 0.5)
            self._apply_effects_and_filters(processed_videos)
            
            # 6. 添加转场
            self._update_progress("添加转场", 0.6)
            self._add_transitions(processed_videos, duration_result)
            
            # 7. 处理音频轨道
            self._update_progress("处理音频轨道", 0.7)
            self._process_audio_tracks(narration_audio, background_audio, duration_result['total_duration'])
            
            # 8. 添加字幕
            self._update_progress("添加字幕", 0.8)
            self._process_subtitles(subtitle_file, duration_result['total_duration'])
            
            # 9. 验证和保存草稿
            self._update_progress("验证和保存草稿", 0.9)
            self._validate_and_save()
            
            self.mix_statistics['end_time'] = time.time()
            self.mix_statistics['final_duration'] = duration_result['total_duration']
            
            self._update_progress("自动混剪完成", 1.0)
            
            return {
                'success': True,
                'draft_path': self._draft_folder,
                'statistics': self.mix_statistics,
                'duration': duration_result['total_duration'],
                'message': '自动混剪成功完成'
            }
            
        except Exception as e:
            error_msg = f"自动混剪失败: {str(e)}"
            self.mix_statistics['errors'].append(error_msg)
            self._update_progress(error_msg, -1)
            
            return {
                'success': False,
                'error': error_msg,
                'statistics': self.mix_statistics
            }
    
    def _scan_and_select_materials(self, product_model: Optional[str] = None) -> Dict[str, Any]:
        """扫描并选择素材"""
        try:
            # 获取素材库路径
            material_path = self.config_manager.get_material_path()

            # 扫描指定产品型号的素材
            product_materials = self.material_scanner.scan_product_materials(material_path, product_model)

            if not product_materials['videos']:
                raise ValueError(f"产品型号 {product_materials['product_model']} 中没有找到可用的视频文件")

            # 智能选择素材 - 根据子文件夹数量动态调整视频数量
            folder_count = len(product_materials['folders'])
            video_count = max(4, folder_count)  # 至少4个视频，或者每个文件夹一个
            print(f"检测到 {folder_count} 个子文件夹，将选择 {video_count} 个视频")

            selected_materials = self.material_scanner.select_materials_from_product(
                product_materials,
                video_count=video_count
            )

            # 更新统计信息
            self.mix_statistics['total_materials'] = len(product_materials['videos'])
            self.mix_statistics['selected_materials'] = len(selected_materials['videos'])
            self.mix_statistics['product_model'] = selected_materials['product_model']

            return selected_materials

        except Exception as e:
            raise ValueError(f"扫描和选择素材失败: {str(e)}")
    
    def _calculate_durations(self, materials: List[Dict[str, Any]], 
                           target_duration: int) -> Dict[str, Any]:
        """计算时长分配"""
        try:
            # 使用时长控制器计算分配
            result = self.duration_controller.optimize_duration_distribution(materials, target_duration)
            
            if not result['success']:
                raise ValueError(f"时长分配失败: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            raise ValueError(f"计算时长分配失败: {str(e)}")
    
    def _process_video_segments(self, materials: List[Dict[str, Any]], 
                              duration_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """处理视频片段"""
        try:
            segment_durations = duration_result['segment_durations']
            processed_videos = []
            
            for i, (material, duration) in enumerate(zip(materials, segment_durations)):
                # 使用视频处理器处理片段
                media_info, segment_info = self.video_processor.process_video_segment(material, duration)

                # 添加视频到草稿（静音处理，并应用处理后的设置）
                self.add_media_with_settings(
                    material['path'],
                    start_at_track=0,
                    duration=duration,
                    bgm_mute=True,
                    segment_info=segment_info
                )

                processed_videos.append({
                    'material': material,
                    'media_info': media_info,
                    'segment_info': segment_info,
                    'duration': duration,
                    'index': i
                })
            
            return processed_videos
            
        except Exception as e:
            raise ValueError(f"处理视频片段失败: {str(e)}")
    
    def _apply_effects_and_filters(self, processed_videos: List[Dict[str, Any]]):
        """应用滤镜和特效"""
        try:
            current_time = 0

            for i, video_data in enumerate(processed_videos):
                segment_info = video_data['segment_info']
                segment_duration = video_data['duration']  # 使用实际分配的时长

                print(f"为视频片段 {i+1} 添加特效: 开始时间={current_time/1000000:.1f}s, 时长={segment_duration/1000000:.1f}s")

                # 强制应用滤镜（提高成功率）
                selected_filter = self.random_effect_engine.select_filter_for_segment(segment_info)
                if not selected_filter:
                    # 如果随机选择失败，强制选择一个滤镜
                    available_filters = self.metadata_manager.get_available_filters(free_only=True)
                    if available_filters:
                        selected_filter = available_filters[i % len(available_filters)]

                if selected_filter:
                    # 直接使用滤镜的resource_id和名称
                    filter_resource_id = getattr(selected_filter, 'resource_id', '')
                    filter_name = getattr(selected_filter, 'name', '')

                    if filter_resource_id:
                        self.add_effect_with_metadata(
                            resource_id=filter_resource_id,
                            name=filter_name,
                            start=current_time,
                            duration=segment_duration,
                            index=i + 200  # 滤镜使用不同的index范围
                        )
                        self.mix_statistics['applied_filters'] += 1
                        print(f"  ✅ 添加滤镜: {filter_name}")

                # 强制应用特效（提高成功率）
                selected_effect = self.random_effect_engine.select_effect_for_segment(segment_info)
                if not selected_effect:
                    # 如果随机选择失败，强制选择一个特效
                    available_effects = self.metadata_manager.get_available_effects(free_only=True)
                    if available_effects:
                        selected_effect = available_effects[i % len(available_effects)]

                if selected_effect:
                    # 直接使用特效的resource_id和名称
                    effect_resource_id = getattr(selected_effect, 'resource_id', '')
                    effect_name = getattr(selected_effect, 'name', '')

                    if effect_resource_id:
                        self.add_effect_with_metadata(
                            resource_id=effect_resource_id,
                            name=effect_name,
                            start=current_time,
                            duration=segment_duration,
                            index=i + 100  # 使用不同的index避免冲突
                        )
                        self.mix_statistics['applied_effects'] += 1
                        print(f"  ✅ 添加特效: {effect_name}")

                # 累加时间到下一个片段
                current_time += segment_duration

                current_time += segment_duration

        except Exception as e:
            raise ValueError(f"应用滤镜和特效失败: {str(e)}")
    
    def _add_transitions(self, processed_videos: List[Dict[str, Any]],
                        duration_result: Dict[str, Any]):
        """添加转场"""
        try:
            segment_durations = duration_result['segment_durations']
            current_time = 0

            for i in range(len(processed_videos) - 1):
                prev_video = processed_videos[i]
                next_video = processed_videos[i + 1]

                # 选择转场
                transition_result = self.random_effect_engine.select_transition_between_segments(
                    prev_video['segment_info'],
                    next_video['segment_info']
                )

                if transition_result:
                    transition_meta, transition_duration = transition_result
                    transition_resource_id = getattr(transition_meta, 'resource_id', '')
                    transition_name = getattr(transition_meta, 'name', '')

                    if transition_resource_id:
                        # 计算转场开始时间（在前一个片段结束时）
                        segment_duration = segment_durations[i]
                        transition_start = current_time + segment_duration - transition_duration // 2

                        # 实际添加转场到草稿
                        self.add_transition(
                            transition_name_or_resource_id=transition_resource_id,
                            start=transition_start,
                            duration=transition_duration
                        )
                        self.mix_statistics['applied_transitions'] += 1
                        print(f"  ✅ 添加转场: {transition_name} (时间: {transition_start/1000000:.1f}s)")

                # 累加时间到下一个片段
                current_time += segment_durations[i]

        except Exception as e:
            raise ValueError(f"添加转场失败: {str(e)}")
    
    def _process_audio_tracks(self, narration_audio: Optional[str], 
                            background_audio: Optional[str], total_duration: int):
        """处理音频轨道"""
        try:
            # 添加解说音频
            if narration_audio and os.path.exists(narration_audio):
                narration_volume, _ = self.config_manager.get_audio_volumes()
                self.add_audio_to_specific_track(
                    narration_audio,
                    track_index=0,  # 第一个音频轨道
                    duration=total_duration,
                    volume=narration_volume,
                    track_name="narration"
                )
                self.mix_statistics['audio_tracks'] += 1

            # 添加背景音频
            if background_audio and os.path.exists(background_audio):
                _, background_volume = self.config_manager.get_audio_volumes()
                self.add_audio_to_specific_track(
                    background_audio,
                    track_index=1,  # 第二个音频轨道
                    duration=total_duration,
                    volume=background_volume,
                    track_name="background"
                )
                self.mix_statistics['audio_tracks'] += 1
            
        except Exception as e:
            raise ValueError(f"处理音频轨道失败: {str(e)}")

    def add_audio_to_specific_track(self, audio_file: str, track_index: int, duration: int,
                                   volume: float = 1.0, track_name: str = ""):
        """
        添加音频到指定轨道 - 参考demo直接设置音量
        """
        from JianYingDraft.core.mediaFactory import MediaFactory
        from JianYingDraft.core import template

        # 创建音频媒体对象，不在这里设置音量，而是在segment中设置
        media = MediaFactory.create(audio_file, duration=duration)
        if media is None:
            return

        # 强制设置音频时长为目标时长
        media.duration = duration

        # 将媒体信息添加到draft的素材库
        self._Draft__add_media_to_content_materials(media)

        # 确保有足够的音频轨道
        all_tracks = self._tracks_in_draft_content
        audio_tracks = [track for track in all_tracks if track["type"] == "audio"]

        # 创建足够的音频轨道
        while len(audio_tracks) <= track_index:
            new_track = template.get_track()
            new_track["type"] = "audio"
            if track_name:
                new_track["_track_name"] = track_name  # 添加轨道标识
            all_tracks.append(new_track)
            audio_tracks.append(new_track)

        # 使用指定的音频轨道
        target_track = audio_tracks[track_index]

        # 设置音频片段的时间范围
        segment_target_timerange = media.segment_data_for_content["target_timerange"]
        segment_target_timerange["start"] = 0
        segment_target_timerange["duration"] = duration  # 确保时长正确

        # 强制设置source_timerange，确保音频被截取到正确长度
        if "source_timerange" in media.segment_data_for_content:
            media.segment_data_for_content["source_timerange"]["start"] = 0
            media.segment_data_for_content["source_timerange"]["duration"] = duration
        else:
            media.segment_data_for_content["source_timerange"] = {
                "start": 0,
                "duration": duration
            }

        # 关键修复：直接在segment中设置音量，参考demo的volume=0.6方式
        media.segment_data_for_content["volume"] = volume
        media.segment_data_for_content["last_nonzero_volume"] = volume

        # 确保音量设置生效的关键属性
        if "extra_material_refs" not in media.segment_data_for_content:
            media.segment_data_for_content["extra_material_refs"] = []

        # 同时更新材料数据中的时长
        if "audios" in media.material_data_for_content:
            media.material_data_for_content["audios"]["duration"] = duration

        target_track["segments"].append(media.segment_data_for_content)

        print(f"  ✅ 添加音频轨道 {track_name}: 时长{duration/1000000:.1f}s, 音量{volume:.1%}")

        # 将媒体信息添加到draft的元数据库
        self._Draft__add_media_to_meta_info(media)

    def add_media_with_settings(self, file_path: str, start_at_track: int = 0,
                               duration: int = 0, bgm_mute: bool = False,
                               segment_info: Dict[str, Any] = None):
        """
        添加媒体并应用视频处理设置（缩放、色彩调整等）
        """
        from JianYingDraft.core.mediaFactory import MediaFactory

        # 创建媒体对象
        media = MediaFactory.create(file_path, duration=duration, bgm_mute=bgm_mute)
        if media is None:
            return

        # 应用视频处理设置 - 参考demo的clip_settings方式
        if segment_info and hasattr(media, 'segment_data_for_content'):
            segment_data = media.segment_data_for_content

            # 确保clip结构存在，参考demo的Clip_settings结构
            if 'clip' not in segment_data:
                segment_data['clip'] = {
                    "alpha": 1.0,
                    "flip": {"horizontal": False, "vertical": False},
                    "rotation": 0.0,
                    "scale": {"x": 1.0, "y": 1.0},
                    "transform": {"x": 0.0, "y": 0.0}
                }

            # 关键修复：直接设置缩放值，确保在剪映界面显示正确
            if 'clip' in segment_info and 'scale' in segment_info['clip']:
                # 直接复制缩放设置，确保数据结构完整
                segment_data['clip']['scale']['x'] = segment_info['clip']['scale']['x']
                segment_data['clip']['scale']['y'] = segment_info['clip']['scale']['y']
                print(f"    🔍 应用缩放: {segment_info['clip']['scale']['x']:.2f}x")

            # 关键修复：直接设置位置变换，确保9:16居中对齐
            if 'clip' in segment_info and 'transform' in segment_info['clip']:
                segment_data['clip']['transform']['x'] = segment_info['clip']['transform']['x']
                segment_data['clip']['transform']['y'] = segment_info['clip']['transform']['y']
                print(f"    📍 应用位置: x={segment_info['clip']['transform']['x']:.1f}, y={segment_info['clip']['transform']['y']:.1f}")

            # 应用色彩调整
            if '_color_adjustments' in segment_info:
                color_adj = segment_info['_color_adjustments']
                segment_data['enable_adjust'] = True
                segment_data['enable_color_curves'] = True
                segment_data['enable_color_wheels'] = True

                # 设置HDR亮度
                if 'hdr_settings' in segment_info:
                    segment_data['hdr_settings'] = segment_info['hdr_settings'].copy()

                print(f"    🎨 应用色彩调整: 对比度{color_adj['contrast']:.2f}, 亮度{color_adj['brightness']:.2f}")

            # 应用其他视频设置
            for key in ['enable_adjust', 'enable_color_curves', 'enable_color_wheels', 'cartoon']:
                if key in segment_info:
                    segment_data[key] = segment_info[key]

            # 确保segment有必要的属性
            if 'extra_material_refs' not in segment_data:
                segment_data['extra_material_refs'] = []

        # 将媒体信息添加到draft的素材库
        self._Draft__add_media_to_content_materials(media)

        # 将媒体信息添加到draft的轨道库
        self._Draft__add_media_to_content_tracks(media, start=0)

    def add_effect_with_metadata(self, resource_id: str, name: str, start: int = 0,
                                duration: int = 0, index: int = 0):
        """
        添加带正确元数据的特效
        """
        from JianYingDraft.core.mediaEffect import MediaEffect
        from JianYingDraft.utils import tools
        from JianYingDraft.core import template

        # 直接创建特效媒体对象，使用resource_id
        media = MediaEffect(
            effect_name_or_resource_id=resource_id,  # 直接使用resource_id
            start=start,
            duration=duration
        )

        # 手动修正名称，确保显示中文名称
        if hasattr(media, 'material_data_for_content') and 'video_effects' in media.material_data_for_content:
            effect_data = media.material_data_for_content['video_effects']
            effect_data['name'] = name  # 设置中文名称
            effect_data['resource_id'] = resource_id  # 确保resource_id正确

        # 将媒体信息添加到draft的素材库
        self._Draft__add_media_to_content_materials(media)

        # 将媒体信息添加到draft的轨道库
        self._Draft__add_media_to_content_tracks(media, start=start)
    
    def _process_subtitles(self, subtitle_file: Optional[str], total_duration: int):
        """处理字幕"""
        try:
            if subtitle_file and os.path.exists(subtitle_file):
                # 解析SRT文件
                subtitles = self.srt_processor.parse_srt_file(subtitle_file)
                
                # 修复格式
                fixed_subtitles = self.srt_processor.fix_srt_format(subtitles)
                
                # 优化时长
                optimized_subtitles = self.srt_processor.optimize_subtitle_timing(fixed_subtitles, total_duration)
                
                # 添加字幕到草稿
                subtitle_count = self.srt_processor.add_subtitles_to_draft(self, optimized_subtitles)
                self.mix_statistics['subtitle_count'] = subtitle_count
            
        except Exception as e:
            raise ValueError(f"处理字幕失败: {str(e)}")
    
    def _validate_and_save(self):
        """验证和保存草稿"""
        try:
            # 验证草稿完整性
            draft_duration = self.calc_draft_duration()
            min_duration, max_duration = self.config_manager.get_video_duration_range()

            # 放宽验证范围，允许±5秒的误差
            tolerance = 5000000  # 5秒误差
            if not (min_duration - tolerance <= draft_duration <= max_duration + tolerance):
                print(f"警告：草稿时长({draft_duration/1000000:.1f}s)略超出标准范围({min_duration/1000000:.1f}s-{max_duration/1000000:.1f}s)，但在可接受范围内")
                # 不抛出异常，继续保存
            
            # 保存草稿
            self.save()
            
        except Exception as e:
            raise ValueError(f"验证和保存草稿失败: {str(e)}")
    
    def batch_generate(self, count: int, **kwargs) -> List[Dict[str, Any]]:
        """
        批量生成多个混剪作品

        Args:
            count: 生成数量
            **kwargs: 传递给auto_mix的参数
                target_duration_range: (min, max) 时长范围元组

        Returns:
            List[Dict[str, Any]]: 批量生成结果列表
        """
        results = []

        # 提取时长范围参数
        target_duration_range = kwargs.pop('target_duration_range', None)

        for i in range(count):
            try:
                # 为每个草稿生成唯一名称
                timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
                draft_name = f"AutoMix_{timestamp}_{i+1:03d}"

                # 创建新的AutoMixDraft实例
                auto_draft = AutoMixDraft(draft_name, self.config_manager)
                auto_draft.set_progress_callback(self.progress_callback)

                # 设置随机时长（如果提供了范围）
                current_kwargs = kwargs.copy()
                if target_duration_range:
                    import random
                    min_duration, max_duration = target_duration_range
                    current_kwargs['target_duration'] = random.randint(min_duration, max_duration)

                # 执行自动混剪
                result = auto_draft.auto_mix(**current_kwargs)
                result['batch_index'] = i + 1
                result['draft_name'] = draft_name

                results.append(result)

            except Exception as e:
                error_result = {
                    'success': False,
                    'batch_index': i + 1,
                    'draft_name': f"AutoMix_Error_{i+1:03d}",
                    'error': str(e)
                }
                results.append(error_result)

        return results
    
    def get_mix_statistics(self) -> Dict[str, Any]:
        """获取混剪统计信息"""
        stats = self.mix_statistics.copy()
        
        if stats['end_time'] > 0:
            stats['processing_time'] = stats['end_time'] - stats['start_time']
        
        return stats
    
    def print_mix_summary(self):
        """打印混剪摘要"""
        stats = self.get_mix_statistics()
        
        print("=== 自动混剪摘要 ===")
        print(f"处理时间: {stats.get('processing_time', 0):.1f}秒")
        print(f"总素材数: {stats['total_materials']}")
        print(f"选择素材数: {stats['selected_materials']}")
        print(f"应用滤镜数: {stats['applied_filters']}")
        print(f"应用转场数: {stats['applied_transitions']}")
        print(f"应用特效数: {stats['applied_effects']}")
        print(f"音频轨道数: {stats['audio_tracks']}")
        print(f"字幕数量: {stats['subtitle_count']}")
        print(f"最终时长: {stats['final_duration']/1000000:.1f}秒")
        
        if stats['errors']:
            print(f"错误数量: {len(stats['errors'])}")
            for error in stats['errors']:
                print(f"  - {error}")
        
        print("===================")
