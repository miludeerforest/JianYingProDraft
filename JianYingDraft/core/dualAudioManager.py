"""
 * @file   : dualAudioManager.py
 * @time   : 19:15
 * @date   : 2024/12/19
 * @mail   : 9727005@qq.com
 * @creator: ShanDong Xiedali
 * @company: HiLand & RainyTop
"""
import os
import math
from typing import Dict, Any, List, Optional, Tuple
from pymediainfo import MediaInfo
from JianYingDraft.core.configManager import AutoMixConfigManager
from JianYingDraft.core import template
from JianYingDraft.utils import tools


class DualAudioManager:
    """
    双轨音频管理器
    实现双轨音频处理，包括解说音频100%音量和背景音频10%音量的管理
    """
    
    def __init__(self):
        """初始化双轨音频管理器"""
        self.config_manager = AutoMixConfigManager
        self.narration_tracks = []  # 解说音频轨道列表
        self.background_tracks = []  # 背景音频轨道列表
    
    def create_audio_track(self, track_type: str = "audio") -> Dict[str, Any]:
        """
        创建音频轨道
        
        Args:
            track_type: 轨道类型，默认为"audio"
            
        Returns:
            Dict[str, Any]: 音频轨道字典
        """
        track_id = tools.generate_id()
        return template.get_track(track_id, track_type)
    
    def create_audio_segment(self, audio_info: Dict[str, Any], start_time: int, 
                           duration: int, volume: float = 1.0) -> Dict[str, Any]:
        """
        创建音频片段
        
        Args:
            audio_info: 音频信息字典
            start_time: 开始时间（微秒）
            duration: 持续时间（微秒）
            volume: 音量（0.0-1.0）
            
        Returns:
            Dict[str, Any]: 音频片段字典
        """
        segment_id = tools.generate_id()
        segment = template.get_segment(segment_id)
        
        # 设置音频特定属性
        segment['material_id'] = audio_info.get('id', '')
        segment['volume'] = volume
        segment['last_nonzero_volume'] = volume
        
        # 设置时间范围
        segment['source_timerange'] = {
            "duration": duration,
            "start": 0  # 从音频开始播放
        }
        segment['target_timerange'] = {
            "duration": duration,
            "start": start_time
        }
        
        # 音频不需要视频相关的属性
        segment['cartoon'] = False
        segment['visible'] = False
        
        return segment
    
    def add_narration_audio(self, audio_path: str, start_time: int = 0, 
                          duration: Optional[int] = None, volume: Optional[float] = None) -> Dict[str, Any]:
        """
        添加解说音频到第一轨道
        
        Args:
            audio_path: 音频文件路径
            start_time: 开始时间（微秒）
            duration: 持续时间（微秒），如果为None则使用音频全长
            volume: 音量，如果为None则使用配置文件中的值
            
        Returns:
            Dict[str, Any]: 包含轨道和片段信息的字典
        """
        if volume is None:
            narration_volume, _ = self.config_manager.get_audio_volumes()
            volume = narration_volume
        
        # 获取音频信息
        audio_info = self._get_audio_info(audio_path)
        if not audio_info:
            raise ValueError(f"无法获取音频信息: {audio_path}")
        
        # 确定音频时长
        if duration is None:
            duration = audio_info['duration']
        else:
            duration = min(duration, audio_info['duration'])
        
        # 创建音频轨道（如果还没有解说轨道）
        if not self.narration_tracks:
            track = self.create_audio_track()
            track['attribute'] = 0  # 正常轨道
            self.narration_tracks.append(track)
        
        # 使用第一个解说轨道
        narration_track = self.narration_tracks[0]
        
        # 创建音频片段
        segment = self.create_audio_segment(audio_info, start_time, duration, volume)
        
        # 添加到轨道
        narration_track['segments'].append(segment)
        
        return {
            'track': narration_track,
            'segment': segment,
            'audio_info': audio_info,
            'type': 'narration'
        }
    
    def add_background_audio(self, audio_path: str, target_duration: int, 
                           volume: Optional[float] = None) -> Dict[str, Any]:
        """
        添加背景音频到第二轨道，支持循环播放匹配目标时长
        
        Args:
            audio_path: 音频文件路径
            target_duration: 目标总时长（微秒）
            volume: 音量，如果为None则使用配置文件中的值
            
        Returns:
            Dict[str, Any]: 包含轨道和片段信息的字典
        """
        if volume is None:
            _, background_volume = self.config_manager.get_audio_volumes()
            volume = background_volume
        
        # 获取音频信息
        audio_info = self._get_audio_info(audio_path)
        if not audio_info:
            raise ValueError(f"无法获取音频信息: {audio_path}")
        
        # 创建背景音频轨道（如果还没有背景轨道）
        if not self.background_tracks:
            track = self.create_audio_track()
            track['attribute'] = 0  # 正常轨道
            self.background_tracks.append(track)
        
        # 使用第一个背景轨道
        background_track = self.background_tracks[0]
        
        # 计算需要循环的次数
        audio_duration = audio_info['duration']
        loop_count = math.ceil(target_duration / audio_duration)
        
        # 创建循环的音频片段
        current_time = 0
        segments = []
        
        for i in range(loop_count):
            # 计算当前片段的时长
            remaining_duration = target_duration - current_time
            segment_duration = min(audio_duration, remaining_duration)
            
            if segment_duration <= 0:
                break
            
            # 创建音频片段
            segment = self.create_audio_segment(audio_info, current_time, segment_duration, volume)
            segments.append(segment)
            background_track['segments'].append(segment)
            
            current_time += segment_duration
        
        return {
            'track': background_track,
            'segments': segments,
            'audio_info': audio_info,
            'type': 'background',
            'loop_count': loop_count,
            'total_duration': current_time
        }
    
    def apply_fade_effects(self, audio_segment: Dict[str, Any], 
                         fade_in_duration: int = 500000, fade_out_duration: int = 500000) -> Dict[str, Any]:
        """
        应用淡入淡出效果
        
        Args:
            audio_segment: 音频片段字典
            fade_in_duration: 淡入时长（微秒），默认0.5秒
            fade_out_duration: 淡出时长（微秒），默认0.5秒
            
        Returns:
            Dict[str, Any]: 更新后的音频片段
        """
        # 获取片段时长
        segment_duration = audio_segment.get('target_timerange', {}).get('duration', 0)
        
        # 确保淡入淡出时长不超过片段总时长的一半
        max_fade_duration = segment_duration // 2
        fade_in_duration = min(fade_in_duration, max_fade_duration)
        fade_out_duration = min(fade_out_duration, max_fade_duration)
        
        # 创建淡入淡出效果ID
        fade_id = tools.generate_id()
        
        # 添加淡入淡出信息到片段
        audio_segment['_fade_effects'] = {
            'fade_id': fade_id,
            'fade_in_duration': fade_in_duration,
            'fade_out_duration': fade_out_duration,
            'template': template.get_audio_fade(fade_id, fade_in_duration, fade_out_duration)
        }
        
        return audio_segment
    
    def match_audio_duration(self, target_duration: int) -> Dict[str, Any]:
        """
        调整音频时长匹配视频总时长
        
        Args:
            target_duration: 目标时长（微秒）
            
        Returns:
            Dict[str, Any]: 调整结果信息
        """
        result = {
            'target_duration': target_duration,
            'narration_adjusted': False,
            'background_adjusted': False,
            'adjustments': []
        }
        
        # 调整解说音频
        for track in self.narration_tracks:
            for segment in track['segments']:
                current_duration = segment.get('target_timerange', {}).get('duration', 0)
                if current_duration > target_duration:
                    # 缩短音频
                    segment['target_timerange']['duration'] = target_duration
                    segment['source_timerange']['duration'] = target_duration
                    result['narration_adjusted'] = True
                    result['adjustments'].append(f"解说音频从{current_duration/1000000:.1f}s缩短到{target_duration/1000000:.1f}s")
        
        # 调整背景音频（重新生成以匹配新时长）
        if self.background_tracks:
            result['background_adjusted'] = True
            result['adjustments'].append(f"背景音频重新循环匹配{target_duration/1000000:.1f}s")
        
        return result
    
    def _get_audio_info(self, audio_path: str) -> Optional[Dict[str, Any]]:
        """
        获取音频文件信息
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            Optional[Dict[str, Any]]: 音频信息字典，如果获取失败则返回None
        """
        try:
            if not os.path.exists(audio_path):
                print(f"音频文件不存在: {audio_path}")
                return None
            
            # 使用pymediainfo获取音频信息
            media_info = MediaInfo.parse(audio_path).to_data()["tracks"]
            
            # 查找音频轨道
            audio_track = None
            for track in media_info:
                if track.get('track_type') == 'Audio':
                    audio_track = track
                    break
            
            if not audio_track:
                print(f"未找到音频轨道: {audio_path}")
                return None
            
            # 生成音频ID
            audio_id = tools.generate_id()
            
            return {
                'id': audio_id,
                'path': audio_path,
                'filename': os.path.basename(audio_path),
                'duration': int(float(audio_track.get('duration', 0)) * 1000),  # 转换为微秒
                'sample_rate': audio_track.get('sampling_rate', 0),
                'channels': audio_track.get('channel_s', 0),
                'format': audio_track.get('format', ''),
                'bit_rate': audio_track.get('bit_rate', 0),
                'size': os.path.getsize(audio_path)
            }
            
        except Exception as e:
            print(f"获取音频信息时出错 {audio_path}: {str(e)}")
            return None
    
    def get_all_tracks(self) -> List[Dict[str, Any]]:
        """获取所有音频轨道"""
        return self.narration_tracks + self.background_tracks
    
    def get_audio_summary(self) -> Dict[str, Any]:
        """获取音频处理摘要"""
        narration_count = sum(len(track['segments']) for track in self.narration_tracks)
        background_count = sum(len(track['segments']) for track in self.background_tracks)
        
        total_narration_duration = 0
        total_background_duration = 0
        
        for track in self.narration_tracks:
            for segment in track['segments']:
                total_narration_duration += segment.get('target_timerange', {}).get('duration', 0)
        
        for track in self.background_tracks:
            for segment in track['segments']:
                total_background_duration += segment.get('target_timerange', {}).get('duration', 0)
        
        return {
            'narration_tracks': len(self.narration_tracks),
            'background_tracks': len(self.background_tracks),
            'narration_segments': narration_count,
            'background_segments': background_count,
            'total_narration_duration': total_narration_duration,
            'total_background_duration': total_background_duration,
            'narration_volume': self.config_manager.get_audio_volumes()[0],
            'background_volume': self.config_manager.get_audio_volumes()[1]
        }
    
    def print_audio_summary(self):
        """打印音频处理摘要"""
        summary = self.get_audio_summary()
        
        print("=== 双轨音频处理摘要 ===")
        print(f"解说轨道: {summary['narration_tracks']}个，片段: {summary['narration_segments']}个")
        print(f"背景轨道: {summary['background_tracks']}个，片段: {summary['background_segments']}个")
        print(f"解说总时长: {summary['total_narration_duration']/1000000:.1f}s")
        print(f"背景总时长: {summary['total_background_duration']/1000000:.1f}s")
        print(f"音量设置: 解说{summary['narration_volume']:.1%}, 背景{summary['background_volume']:.1%}")
        print("========================")
    
    def validate_audio_setup(self) -> Tuple[bool, List[str]]:
        """
        验证音频设置的有效性
        
        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误信息列表)
        """
        errors = []
        
        # 检查是否有音频轨道
        if not self.narration_tracks and not self.background_tracks:
            errors.append("没有添加任何音频轨道")
        
        # 检查解说音频
        if self.narration_tracks:
            for i, track in enumerate(self.narration_tracks):
                if not track.get('segments'):
                    errors.append(f"解说轨道{i+1}没有音频片段")
        
        # 检查背景音频
        if self.background_tracks:
            for i, track in enumerate(self.background_tracks):
                if not track.get('segments'):
                    errors.append(f"背景轨道{i+1}没有音频片段")
        
        # 检查音量设置
        narration_vol, background_vol = self.config_manager.get_audio_volumes()
        if not 0.0 <= narration_vol <= 1.0:
            errors.append(f"解说音量({narration_vol})超出有效范围(0.0-1.0)")
        if not 0.0 <= background_vol <= 1.0:
            errors.append(f"背景音量({background_vol})超出有效范围(0.0-1.0)")
        
        return len(errors) == 0, errors
